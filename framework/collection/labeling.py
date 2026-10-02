"""
Gán nhãn tổng quát cho dữ liệu chuỗi thời gian theo thực thể.

Với mỗi điểm neo t của mỗi thực thể:
    label_raw = agg( target trên cửa sổ tương lai (t, t + H] )
    label     = label_raw (regression)  hoặc  [label_raw <operator> threshold] (binary)

Feature của dòng là quan sát tại t; cửa sổ nhãn bắt đầu SAU t nên không rò rỉ nhãn.
Dòng không đủ dữ liệu để xác định nhãn bị loại khỏi bảng training.
"""
from __future__ import annotations

import operator

import pandas as pd

from .config import CollectionConfig
from .window import Window

LABEL_COLUMNS = ["label", "label_raw", "label_coverage", "label_window_end"]

_COMPARATORS = {">": operator.gt, ">=": operator.ge, "<": operator.lt, "<=": operator.le}

# Tổng hợp trượt cộng/trừ dồn nên lệch cỡ 1e-16 (0.5 + 0.5 ra 0.9999999999999999); làm tròn để
# giá trị nằm đúng trên ngưỡng không bị lật nhãn
LABEL_DECIMALS = 9


def _future_aggregate(series: pd.Series, steps: int, agg: str):
    """Tổng hợp `series` trên (t, t + steps] cho từng mốc t → (giá trị, tỉ lệ số đo có mặt)."""
    if agg == "last":
        value = series.shift(-steps)
        return value, value.notna().astype("float64")
    rolling = series.rolling(window=steps, min_periods=1)
    value = getattr(rolling, agg)().shift(-steps).round(LABEL_DECIMALS)
    coverage = (rolling.count() / steps).shift(-steps)
    return value, coverage


def build_labels(observations: pd.DataFrame, window: Window, cfg: CollectionConfig):
    """Trả về (bảng training có nhãn, thống kê)."""
    spec = cfg.label
    obs = observations.copy()
    obs["event_time"] = pd.to_datetime(obs["event_time"], utc=True).dt.as_unit("ns")
    grid = pd.date_range(window.fetch_start, window.fetch_end, freq=cfg.frequency).as_unit("ns")

    parts = []
    for entity_id, group in obs.groupby("entity_id", sort=True):
        target = pd.to_numeric(group.set_index("event_time")[spec.target], errors="coerce")
        target = target[~target.index.duplicated(keep="last")].reindex(grid)
        if spec.valid_min is not None:
            target = target.where(target >= spec.valid_min)
        if spec.valid_max is not None:
            target = target.where(target <= spec.valid_max)
        value, coverage = _future_aggregate(target, cfg.horizon_steps, spec.agg)
        parts.append(pd.DataFrame({
            "entity_id": entity_id,
            "event_time": grid,
            "label_raw": value.to_numpy(),
            "label_coverage": coverage.to_numpy(),
        }))

    anchors = obs[(obs["event_time"] >= window.anchor_start) & (obs["event_time"] < window.anchor_end)]
    if not parts or anchors.empty:
        empty = anchors.assign(**{name: pd.Series(dtype="float64") for name in LABEL_COLUMNS})
        return empty, {"anchor_rows": 0, "labeled_rows": 0, "dropped_no_label": 0}

    merged = anchors.merge(pd.concat(parts, ignore_index=True), on=["entity_id", "event_time"], how="left")
    valid = merged["label_raw"].notna() & (merged["label_coverage"] >= spec.min_coverage - 1e-9)
    labeled = merged[valid].copy()

    if cfg.task_type == "binary":
        labeled["label"] = _COMPARATORS[spec.operator](labeled["label_raw"], spec.threshold).astype("int8")
    else:
        labeled["label"] = labeled["label_raw"].astype("float64")
    labeled["label_window_end"] = labeled["event_time"] + cfg.horizon

    feature_cols = [c for c in labeled.columns if c not in LABEL_COLUMNS]
    labeled = (labeled[feature_cols + LABEL_COLUMNS]
               .sort_values(["event_time", "entity_id"]).reset_index(drop=True))

    stats = {
        "anchor_rows": int(len(merged)),
        "labeled_rows": int(len(labeled)),
        "dropped_no_label": int(len(merged) - len(labeled)),
    }
    if len(labeled):
        stats["label_mean"] = round(float(labeled["label"].mean()), 6)   # binary: tỉ lệ lớp dương
        stats["label_raw_min"] = round(float(labeled["label_raw"].min()), 6)
        stats["label_raw_max"] = round(float(labeled["label_raw"].max()), 6)
    return labeled, stats

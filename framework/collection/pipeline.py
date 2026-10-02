"""
Các bước của data collection — dùng chung cho Airflow DAG và CLI.

    extract       gọi API → landing/ (JSON nguyên bản, nén gzip)
    flatten       landing/ → observations/ (bảng quan sát)
    build_labels  observations/ → labeled/ (bảng training có nhãn)
    report        ghi manifest + tóm tắt

Mỗi bước đọc đầu vào từ storage và chỉ trả về số đếm → XCom không chở DataFrame.
Mọi bước ghi theo kiểu "thay khoảng thời gian" nên chạy lại một cửa sổ cho kết quả y hệt.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from .config import CollectionConfig
from .connectors import get_connector
from .connectors.base import KEY_COLUMNS
from .labeling import build_labels
from .storage import Storage, default_base_uri
from .window import Window

logger = logging.getLogger(__name__)

LANDING, OBSERVATIONS, LABELED, MANIFESTS = "landing", "observations", "labeled", "_manifests"


class CollectionError(RuntimeError):
    """Lần thu thập không dùng được (nguồn không trả dữ liệu, cấu hình thiếu, ...)."""


def get_storage(cfg: CollectionConfig, base_uri: str | None = None, **storage_options) -> Storage:
    return Storage(f"{(base_uri or default_base_uri()).rstrip('/')}/{cfg.problem_id}", **storage_options)


def _landing_prefix(window: Window) -> str:
    return f"{LANDING}/window={window.key}"


def extract(cfg: CollectionConfig, window: Window, storage: Storage, connector=None) -> dict:
    if not cfg.entities:
        raise CollectionError(
            f"{cfg.problem_id}: danh sách entities rỗng. Với OpenAQ hãy chạy "
            "`python -m framework.collection discover-openaq` để chọn trạm trước.")
    connector = connector or get_connector(cfg)
    prefix = _landing_prefix(window)
    storage.delete(prefix)                         # rerun: thay toàn bộ landing của cửa sổ này

    count = 0
    for count, envelope in enumerate(connector.extract(window.fetch_start, window.fetch_end), start=1):
        storage.write_json_gz(f"{prefix}/part-{count - 1:05d}.json.gz", envelope)
    if count == 0:
        raise CollectionError(f"{cfg.problem_id}: không có request nào được thực hiện cho cửa sổ {window.key}")
    logger.info("[%s] extract: %d response → %s", cfg.problem_id, count, storage.uri(prefix))
    return {"responses": count, "landing": storage.uri(prefix)}


def _normalize(df: pd.DataFrame, cfg: CollectionConfig, window: Window) -> pd.DataFrame:
    """Chuẩn hoá cấu trúc (KHÔNG phải cleaning): đủ cột, đúng khoảng thời gian, một dòng / khoá."""
    df = df.copy()
    for variable in cfg.variables:                 # schema ổn định dù nguồn thiếu hẳn một biến
        if variable not in df.columns:
            df[variable] = np.nan
    df = df.dropna(subset=list(cfg.variables), how="all")      # mốc giờ nguồn chưa có dữ liệu
    df = df[(df["event_time"] >= window.fetch_start) & (df["event_time"] <= window.fetch_end)]
    return (df.drop_duplicates(KEY_COLUMNS, keep="last")
              .sort_values(["event_time", "entity_id"]).reset_index(drop=True))


def flatten(cfg: CollectionConfig, window: Window, storage: Storage, connector=None) -> dict:
    connector = connector or get_connector(cfg)
    files = storage.list_files(_landing_prefix(window))
    if not files:
        raise CollectionError(f"{cfg.problem_id}: không có file landing cho cửa sổ {window.key}")

    df = connector.flatten(storage.read_json_gz(rel) for rel in files)
    df = _normalize(df, cfg, window)
    if df.empty:
        raise CollectionError(
            f"{cfg.problem_id}: nguồn không trả quan sát nào trong "
            f"[{window.fetch_start.isoformat()}, {window.fetch_end.isoformat()}] — "
            "kiểm tra maturity_lag, danh sách entities và trạng thái nguồn")

    partitions = storage.replace_range(OBSERVATIONS, df, window.fetch_start,
                                       window.fetch_end + cfg.frequency)
    stats = {
        "rows": int(len(df)),
        "entities": int(df["entity_id"].nunique()),
        "columns": int(df.shape[1]),
        "target_nulls": int(df[cfg.label.target].isna().sum()),
        "partitions": len(partitions),
    }
    logger.info("[%s] flatten: %s", cfg.problem_id, stats)
    return stats


def label(cfg: CollectionConfig, window: Window, storage: Storage) -> dict:
    observations = storage.read_range(OBSERVATIONS, window.fetch_start, window.fetch_end)
    if observations.empty:
        raise CollectionError(f"{cfg.problem_id}: chưa có observations cho cửa sổ {window.key}")

    labeled, stats = build_labels(observations, window, cfg)
    labeled["source"] = cfg.source_type
    labeled["window_key"] = window.key            # truy ngược về landing/window=<key>/
    partitions = storage.replace_range(LABELED, labeled, window.anchor_start, window.anchor_end)
    stats["partitions"] = len(partitions)
    logger.info("[%s] build_labels: %s", cfg.problem_id, stats)
    return stats


def report(cfg: CollectionConfig, window: Window, storage: Storage, stages: dict) -> dict:
    """Ghi manifest của lần chạy; trả về tóm tắt kèm danh sách cảnh báo."""
    label_stats = stages.get("build_labels") or {}
    warnings = []
    if label_stats.get("labeled_rows", 0) == 0:
        warnings.append("Không có dòng nào được gán nhãn trong cửa sổ này")
    elif label_stats.get("dropped_no_label", 0) > label_stats.get("labeled_rows", 0):
        warnings.append("Hơn một nửa số điểm neo bị loại vì không đủ dữ liệu để xác định nhãn")

    summary = {
        "problem_id": cfg.problem_id,
        "task_type": cfg.task_type,
        "source": cfg.source_type,
        "window": window.to_dict(),
        "horizon": str(cfg.horizon),
        "maturity_lag": str(cfg.maturity_lag),
        "label": {"target": cfg.label.target, "agg": cfg.label.agg,
                  "threshold": cfg.label.threshold, "operator": cfg.label.operator},
        "stages": stages,
        "warnings": warnings,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    storage.write_json(f"{MANIFESTS}/window={window.key}.json", summary)
    logger.info("[%s] report: %s", cfg.problem_id, {**label_stats, "warnings": warnings})
    return summary


def run_window(cfg: CollectionConfig, window: Window, storage: Storage, connector=None) -> dict:
    """Chạy trọn pipeline cho một cửa sổ (CLI / backfill / test)."""
    connector = connector or get_connector(cfg)
    stages = {
        "extract": extract(cfg, window, storage, connector),
        "flatten": flatten(cfg, window, storage, connector),
        "build_labels": label(cfg, window, storage),
    }
    return report(cfg, window, storage, stages)


def split_range(start: datetime, end: datetime, chunk: timedelta):
    """Chia khoảng điểm neo [start, end) thành các đoạn dài tối đa `chunk` (backfill)."""
    cursor = start
    while cursor < end:
        yield cursor, min(cursor + chunk, end)
        cursor += chunk

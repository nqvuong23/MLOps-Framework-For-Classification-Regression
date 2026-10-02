"""Test cửa sổ thu thập và logic gán nhãn."""
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from framework.collection.labeling import build_labels
from framework.collection.window import Window, explicit_window, floor_time, parse_time, scheduled_window

UTC = timezone.utc


def obs_frame(values_by_entity: dict, start: datetime) -> pd.DataFrame:
    rows = []
    for entity_id, values in values_by_entity.items():
        for i, value in enumerate(values):
            rows.append({"entity_id": entity_id, "event_time": start + timedelta(hours=i), "x": value, "y": 1})
    df = pd.DataFrame(rows)
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    return df


# ── window ────────────────────────────────────────────────────────────────────

def test_scheduled_window_hourly(config_factory):
    cfg = config_factory(horizon_hours=24, maturity_lag=timedelta(hours=24))
    window = scheduled_window(cfg, datetime(2026, 10, 2, 13, 5, 30, tzinfo=UTC))
    # T làm tròn xuống 13:00; điểm neo = [T − 49h, T − 48h)
    assert window.anchor_start == datetime(2026, 9, 30, 12, tzinfo=UTC)
    assert window.anchor_end == datetime(2026, 9, 30, 13, tzinfo=UTC)
    assert window.fetch_start == window.anchor_start
    assert window.fetch_end == datetime(2026, 10, 1, 12, tzinfo=UTC)          # điểm neo cuối + 24h
    assert window.key == "20260930T1200Z_20260930T1300Z"


def test_scheduled_window_daily_label_is_mature(config_factory):
    cfg = config_factory(horizon_hours=24, interval=timedelta(days=1), maturity_lag=timedelta(days=7))
    run_time = datetime(2026, 10, 2, 6, 0, tzinfo=UTC)
    window = scheduled_window(cfg, run_time)
    assert window.anchor_start == datetime(2026, 9, 23, tzinfo=UTC)
    assert window.anchor_end == datetime(2026, 9, 24, tzinfo=UTC)
    assert window.fetch_end == datetime(2026, 9, 24, 23, tzinfo=UTC)
    # dữ liệu mới nhất cần gọi vẫn cũ hơn thời điểm run ít nhất maturity_lag
    assert floor_time(run_time, cfg.interval) - window.fetch_end >= cfg.maturity_lag


def test_same_interval_gives_same_window_and_consecutive_runs_tile(config_factory):
    cfg = config_factory(horizon_hours=24, maturity_lag=timedelta(hours=24))
    a = scheduled_window(cfg, datetime(2026, 10, 2, 13, 0, tzinfo=UTC))
    b = scheduled_window(cfg, datetime(2026, 10, 2, 13, 59, tzinfo=UTC))
    c = scheduled_window(cfg, datetime(2026, 10, 2, 14, 0, tzinfo=UTC))
    assert a == b                              # rerun trong cùng chu kỳ → cùng cửa sổ
    assert c.anchor_start == a.anchor_end      # run kế tiếp nối đúng vào, không hở không chồng


def test_window_roundtrip_and_parse_time(config_factory):
    cfg = config_factory()
    window = explicit_window(cfg, parse_time("2026-09-01"), parse_time("2026-09-02T00:00:00Z"))
    assert Window.from_dict(window.to_dict()) == window
    assert parse_time("2026-09-01T07:00:00+07:00") == datetime(2026, 9, 1, tzinfo=UTC)
    with pytest.raises(ValueError):
        explicit_window(cfg, parse_time("2026-09-02"), parse_time("2026-09-01"))


# ── labeling ──────────────────────────────────────────────────────────────────

START = datetime(2026, 9, 1, tzinfo=UTC)


def test_mean_label_uses_only_future_window(config_factory):
    cfg = config_factory(agg="mean", horizon_hours=3)
    window = explicit_window(cfg, START, START + timedelta(hours=2))          # điểm neo 00:00, 01:00
    obs = obs_frame({"a": [100, 1, 2, 3, 40]}, START)                         # 00:00 → 04:00
    labeled, stats = build_labels(obs, window, cfg)

    assert list(labeled["event_time"]) == [pd.Timestamp(START), pd.Timestamp(START + timedelta(hours=1))]
    # t=00:00 → mean(x tại 01,02,03) = 2, KHÔNG gồm giá trị 100 tại chính t
    assert labeled["label"].tolist() == pytest.approx([2.0, 15.0])
    assert labeled["x"].tolist() == [100, 1]                                  # feature là quan sát tại t
    assert labeled["label_window_end"].iloc[0] == pd.Timestamp(START + timedelta(hours=3))
    assert stats == {"anchor_rows": 2, "labeled_rows": 2, "dropped_no_label": 0,
                     "label_mean": 8.5, "label_raw_min": 2.0, "label_raw_max": 15.0}


def test_sum_threshold_binary_label(config_factory):
    cfg = config_factory(task_type="binary", agg="sum", threshold=1.0, operator=">=", horizon_hours=3)
    window = explicit_window(cfg, START, START + timedelta(hours=2))
    obs = obs_frame({"a": [9, 0.5, 0.25, 0.25, 0.125]}, START)
    labeled, _ = build_labels(obs, window, cfg)
    # t=00: 0.5+0.25+0.25 = 1.0 → 1 ; t=01: 0.25+0.25+0.125 = 0.625 → 0
    assert labeled["label"].tolist() == [1, 0]
    assert labeled["label_raw"].tolist() == pytest.approx([1.0, 0.625])
    assert str(labeled["label"].dtype) == "int8"


def test_last_label_is_point_value_at_horizon(config_factory):
    cfg = config_factory(agg="last", horizon_hours=3)
    window = explicit_window(cfg, START, START + timedelta(hours=2))
    labeled, _ = build_labels(obs_frame({"a": [10, 11, 12, 13, 14]}, START), window, cfg)
    assert labeled["label"].tolist() == [13.0, 14.0]


def test_min_coverage_drops_undetermined_labels(config_factory):
    cfg = config_factory(agg="mean", horizon_hours=4, min_coverage=0.75)
    window = explicit_window(cfg, START, START + timedelta(hours=2))
    # t=00 → cửa sổ 01..04 = [1, nan, 3, 5]: coverage 3/4 → giữ, mean = 3
    # t=01 → cửa sổ 02..05 = [nan, 3, 5, nan]: coverage 2/4 → loại
    obs = obs_frame({"a": [0, 1, np.nan, 3, 5, np.nan]}, START)
    labeled, stats = build_labels(obs, window, cfg)
    assert labeled["label"].tolist() == pytest.approx([3.0])
    assert labeled["label_coverage"].tolist() == pytest.approx([0.75])
    assert stats["dropped_no_label"] == 1


def test_missing_hours_count_against_coverage(config_factory):
    cfg = config_factory(agg="mean", horizon_hours=3, min_coverage=1.0)
    window = explicit_window(cfg, START, START + timedelta(hours=1))
    obs = obs_frame({"a": [0, 1, 2, 3]}, START)
    obs = obs[obs["event_time"] != pd.Timestamp(START + timedelta(hours=2))]   # mất hẳn dòng 02:00
    labeled, stats = build_labels(obs, window, cfg)
    assert labeled.empty and stats["dropped_no_label"] == 1


def test_valid_range_excludes_sentinels_from_label_only(config_factory):
    cfg = config_factory(agg="mean", horizon_hours=3, min_coverage=0.6, valid_min=0)
    window = explicit_window(cfg, START, START + timedelta(hours=1))
    labeled, _ = build_labels(obs_frame({"a": [-999, 10, -999, 20]}, START), window, cfg)
    assert labeled["label"].tolist() == pytest.approx([15.0])      # -999 không kéo lệch nhãn
    assert labeled["x"].tolist() == [-999]                         # feature giữ nguyên (cleaning là bước sau)


def test_entities_are_labeled_independently(config_factory):
    cfg = config_factory(agg="last", horizon_hours=2)
    window = explicit_window(cfg, START, START + timedelta(hours=1))
    labeled, _ = build_labels(obs_frame({"a": [1, 2, 3], "b": [10, 20, 30]}, START), window, cfg)
    assert dict(zip(labeled["entity_id"], labeled["label"])) == {"a": 3.0, "b": 30.0}

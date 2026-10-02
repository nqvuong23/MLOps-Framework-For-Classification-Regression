"""Test pipeline đầu-cuối trên thư mục local với nguồn giả: đúng dữ liệu, idempotent, không trùng dòng."""
import uuid
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from framework.collection import pipeline
from framework.collection.storage import Storage
from framework.collection.window import explicit_window, scheduled_window

UTC = timezone.utc
DAY = datetime(2026, 9, 1, tzinfo=UTC)


@pytest.fixture(params=["local", "object-store"])
def storage(tmp_path, request):
    """Chạy mọi test trên cả thư mục local lẫn object store (fsspec memory:// — cùng API với s3fs)."""
    if request.param == "local":
        return Storage(str(tmp_path / "demo"))
    return Storage(f"memory://collection-test-{uuid.uuid4().hex}/demo")


def read_layer(storage, layer):
    files = [f for f in storage.list_files(layer) if f.endswith(".parquet")]
    return pd.concat([storage.read_parquet(f) for f in files], ignore_index=True) if files else pd.DataFrame()


def test_run_window_writes_all_layers(config_factory, fake_connector, storage):
    cfg = config_factory(agg="mean", horizon_hours=3)
    window = explicit_window(cfg, DAY, DAY + timedelta(hours=4))
    summary = pipeline.run_window(cfg, window, storage, fake_connector(cfg))

    assert len(storage.list_files(f"landing/window={window.key}")) == 2          # 1 response / thực thể
    assert storage.exists(f"_manifests/window={window.key}.json")

    observations = read_layer(storage, "observations")
    assert len(observations) == 2 * 7                 # 4 điểm neo + 3 giờ horizon, 2 thực thể

    labeled = read_layer(storage, "labeled")
    assert len(labeled) == 2 * 4
    assert list(labeled.columns) == ["entity_id", "event_time", "x", "y", "label", "label_raw",
                                     "label_coverage", "label_window_end", "source", "window_key"]
    first = labeled[(labeled["entity_id"] == "a")].sort_values("event_time").iloc[0]
    # x tăng 1 mỗi giờ → mean(x tại t+1, t+2, t+3) = x(t) + 2
    assert first["event_time"] == pd.Timestamp(DAY) and first["label"] == pytest.approx(first["x"] + 2)
    assert summary["stages"]["build_labels"]["labeled_rows"] == 8 and summary["warnings"] == []


def test_rerun_is_idempotent(config_factory, fake_connector, storage):
    cfg = config_factory(horizon_hours=3)
    window = explicit_window(cfg, DAY, DAY + timedelta(hours=4))
    pipeline.run_window(cfg, window, storage, fake_connector(cfg))
    before = {layer: read_layer(storage, layer) for layer in ("observations", "labeled")}
    files_before = storage.list_files("")

    pipeline.run_window(cfg, window, storage, fake_connector(cfg))
    assert [f for f in storage.list_files("")] == files_before
    for layer, frame in before.items():
        pd.testing.assert_frame_equal(read_layer(storage, layer), frame)


def test_hourly_runs_accumulate_in_one_daily_partition_without_duplicates(config_factory, fake_connector, storage):
    cfg = config_factory(horizon_hours=3, maturity_lag=timedelta(hours=2))
    connector = fake_connector(cfg)
    first_run = datetime(2026, 9, 1, 10, tzinfo=UTC)
    for i in range(5):                                   # 5 run theo giờ liên tiếp
        pipeline.run_window(cfg, scheduled_window(cfg, first_run + timedelta(hours=i)), storage, connector)

    labeled = read_layer(storage, "labeled")
    assert len(labeled) == 2 * 5
    assert not labeled.duplicated(["entity_id", "event_time"]).any()
    assert [f for f in storage.list_files("labeled")] == ["labeled/event_date=2026-09-01/part-00000.parquet"]
    # điểm neo của 5 run nối nhau liên tục: 04:00 → 08:00
    assert sorted(labeled["event_time"].dt.hour.unique()) == [4, 5, 6, 7, 8]

    observations = read_layer(storage, "observations")
    assert not observations.duplicated(["entity_id", "event_time"]).any()


def test_window_spanning_midnight_splits_partitions(config_factory, fake_connector, storage):
    cfg = config_factory(horizon_hours=3)
    window = explicit_window(cfg, DAY + timedelta(hours=22), DAY + timedelta(hours=26))
    pipeline.run_window(cfg, window, storage, fake_connector(cfg))
    assert storage.list_files("labeled") == ["labeled/event_date=2026-09-01/part-00000.parquet",
                                             "labeled/event_date=2026-09-02/part-00000.parquet"]
    assert len(read_layer(storage, "labeled")) == 2 * 4


def test_backfill_then_scheduled_run_does_not_duplicate(config_factory, fake_connector, storage):
    cfg = config_factory(horizon_hours=3, maturity_lag=timedelta(hours=2))
    connector = fake_connector(cfg)
    pipeline.run_window(cfg, explicit_window(cfg, DAY, DAY + timedelta(hours=12)), storage, connector)
    pipeline.run_window(cfg, scheduled_window(cfg, datetime(2026, 9, 1, 10, tzinfo=UTC)), storage, connector)
    labeled = read_layer(storage, "labeled")
    assert len(labeled) == 2 * 12 and not labeled.duplicated(["entity_id", "event_time"]).any()


def test_anchor_without_observation_or_label_is_not_emitted(config_factory, fake_connector, storage):
    cfg = config_factory(agg="mean", horizon_hours=3, min_coverage=1.0)
    window = explicit_window(cfg, DAY, DAY + timedelta(hours=3))
    missing = {("a", DAY + timedelta(hours=1)),        # a: không có quan sát tại điểm neo 01:00
               ("b", DAY + timedelta(hours=5))}        # b: thiếu 1 giờ trong cửa sổ nhãn của 02:00
    summary = pipeline.run_window(cfg, window, storage, fake_connector(cfg, missing=missing))

    labeled = read_layer(storage, "labeled")
    got = set(zip(labeled["entity_id"], labeled["event_time"].dt.hour))
    # a@01 không có dòng; a@00 mất nhãn vì cửa sổ (01..03) thiếu 01:00; b@02 mất nhãn vì thiếu 05:00
    assert got == {("a", 2), ("b", 0), ("b", 1)}
    assert labeled["label"].notna().all()
    assert summary["stages"]["build_labels"]["dropped_no_label"] == 2


def test_empty_source_fails_loudly(config_factory, fake_connector, storage):
    cfg = config_factory(horizon_hours=3)
    window = explicit_window(cfg, DAY, DAY + timedelta(hours=2))
    everything = {(e.id, DAY + timedelta(hours=h)) for e in cfg.entities for h in range(10)}
    with pytest.raises(pipeline.CollectionError, match="không trả quan sát"):
        pipeline.run_window(cfg, window, storage, fake_connector(cfg, missing=everything))


def test_no_entities_fails_with_hint(config_factory, fake_connector, storage):
    cfg = config_factory(entities=())
    window = explicit_window(cfg, DAY, DAY + timedelta(hours=1))
    with pytest.raises(pipeline.CollectionError, match="discover-openaq"):
        pipeline.extract(cfg, window, storage, fake_connector(cfg))


def test_split_range():
    chunks = list(pipeline.split_range(DAY, DAY + timedelta(days=70), timedelta(days=30)))
    assert [(e - s).days for s, e in chunks] == [30, 30, 10]
    assert chunks[0][0] == DAY and chunks[-1][1] == DAY + timedelta(days=70)

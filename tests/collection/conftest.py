"""Fixture dùng chung cho test data collection (không gọi mạng, không cần S3)."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from framework.collection.config import CollectionConfig, Entity, LabelSpec  # noqa: E402
from framework.collection.connectors.base import Connector  # noqa: E402

UTC = timezone.utc


def make_config(task_type="regression", agg="mean", threshold=None, operator=">",
                min_coverage=1.0, horizon_hours=3, interval=timedelta(hours=1),
                maturity_lag=timedelta(hours=2), valid_min=None, valid_max=None,
                source_type="fake", variables=("x", "y"), entities=None) -> CollectionConfig:
    return CollectionConfig(
        problem_id="demo", task_type=task_type, description="", source_type=source_type,
        variables=tuple(variables), options={},
        entities=tuple(entities if entities is not None else
                       (Entity("a", "A", 1.0, 2.0), Entity("b", "B", 3.0, 4.0))),
        schedule="0 * * * *", start_date=datetime(2026, 1, 1, tzinfo=UTC),
        interval=interval, frequency=timedelta(hours=1),
        horizon=timedelta(hours=horizon_hours), maturity_lag=maturity_lag,
        label=LabelSpec(target="x", agg=agg, min_coverage=min_coverage, threshold=threshold,
                        operator=operator, valid_min=valid_min, valid_max=valid_max),
    )


class FakeConnector(Connector):
    """Nguồn giả: x = số giờ kể từ 2026-01-01 (cộng 1000 cho thực thể b), y = hằng số."""
    source_type = "fake"
    origin = datetime(2026, 1, 1, tzinfo=UTC)

    def __init__(self, cfg, missing=()):
        super().__init__(cfg)
        self.missing = set(missing)        # {(entity_id, datetime)} không có quan sát
        self.calls = 0

    def extract(self, start, end):
        self.calls += 1
        for entity in self.cfg.entities:
            hours, t = [], start
            while t <= end:
                if (entity.id, t) not in self.missing:
                    hours.append({"t": t.isoformat(), "x": (t - self.origin) / timedelta(hours=1)
                                  + (1000 if entity.id == "b" else 0), "y": 7})
                t += timedelta(hours=1)
            yield {"request": {"entity_id": entity.id}, "response": {"hours": hours}}

    def flatten(self, envelopes):
        rows = [{"entity_id": env["request"]["entity_id"], "event_time": h["t"], "x": h["x"], "y": h["y"]}
                for env in envelopes for h in env["response"]["hours"]]
        df = pd.DataFrame(rows, columns=["entity_id", "event_time", "x", "y"])
        df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
        return df


@pytest.fixture
def config_factory():
    return make_config


@pytest.fixture
def fake_connector():
    return FakeConnector

"""Test flatten của 2 connector (payload theo đúng schema API) và 4 file cấu hình bài toán."""
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from framework.collection.config import ConfigError, Entity, discover_problem_ids, load_config, parse_duration
from framework.collection.connectors import get_connector
from framework.collection.connectors.open_meteo import OpenMeteoConnector
from framework.collection.connectors.openaq import OpenAQConnector

UTC = timezone.utc


# ── Open-Meteo: JSON dạng cột, nhiều địa điểm trong một response ──────────────

def test_open_meteo_flatten(config_factory):
    cfg = config_factory(source_type="open_meteo", variables=("temperature_2m", "precipitation"),
                         entities=(Entity("hanoi", "Hà Nội", 21.03, 105.85, attrs={"country": "VN"}),
                                   Entity("tokyo", "Tokyo", 35.68, 139.65, attrs={"country": "JP"})))
    location = lambda elevation, temps: {                                        # noqa: E731
        "latitude": 0, "longitude": 0, "utc_offset_seconds": 0, "elevation": elevation,
        "hourly_units": {"time": "iso8601", "temperature_2m": "°C", "precipitation": "mm"},
        "hourly": {"time": ["2026-09-01T00:00", "2026-09-01T01:00"],
                   "temperature_2m": temps, "precipitation": [0.0, 1.5]}}
    envelope = {"request": {"entity_ids": ["hanoi", "tokyo"]},
                "response": [location(24.0, [28.1, 27.9]), location(40.0, [22.0, None])]}

    df = OpenMeteoConnector(cfg).flatten([envelope])
    assert list(df.columns) == ["entity_id", "event_time", "entity_name", "latitude", "longitude",
                                "country", "elevation", "temperature_2m", "precipitation"]
    assert len(df) == 4
    assert str(df["event_time"].dt.tz) == "UTC"
    tokyo = df[df["entity_id"] == "tokyo"].reset_index(drop=True)
    assert tokyo.loc[0, "temperature_2m"] == 22.0 and pd.isna(tokyo.loc[1, "temperature_2m"])
    assert tokyo.loc[0, "country"] == "JP" and tokyo.loc[0, "elevation"] == 40.0


def test_open_meteo_single_location_response_is_an_object(config_factory):
    cfg = config_factory(source_type="open_meteo", variables=("temperature_2m",),
                         entities=(Entity("hanoi", "Hà Nội", 21.03, 105.85),))
    envelope = {"request": {"entity_ids": ["hanoi"]},
                "response": {"utc_offset_seconds": 0, "elevation": 24.0,
                             "hourly": {"time": ["2026-09-01T00:00"], "temperature_2m": [28.1]}}}
    assert len(OpenMeteoConnector(cfg).flatten([envelope])) == 1


def test_open_meteo_rejects_non_utc_and_count_mismatch(config_factory):
    cfg = config_factory(source_type="open_meteo", variables=("temperature_2m",))
    hourly = {"time": ["2026-09-01T00:00"], "temperature_2m": [1.0]}
    with pytest.raises(ValueError, match="UTC"):
        OpenMeteoConnector(cfg).flatten([{"request": {"entity_ids": ["a"]},
                                          "response": {"utc_offset_seconds": 25200, "hourly": hourly}}])
    with pytest.raises(ValueError, match="địa điểm"):
        OpenMeteoConnector(cfg).flatten([{"request": {"entity_ids": ["a", "b"]},
                                          "response": {"utc_offset_seconds": 0, "hourly": hourly}}])


# ── OpenAQ: JSON dạng dòng, mỗi response là một sensor ────────────────────────

def openaq_result(hour_end: str, value, flagged=False, complete=100.0):
    end = datetime.fromisoformat(hour_end).replace(tzinfo=UTC)
    stamp = lambda t: {"utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "local": "ignored"}   # noqa: E731
    return {
        "value": value,
        "flagInfo": {"hasFlags": flagged},
        "parameter": {"id": 2, "name": "pm25", "units": "µg/m³", "displayName": None},
        "period": {"label": "1hour", "interval": "01:00:00",
                   "datetimeFrom": stamp(end - timedelta(hours=1)), "datetimeTo": stamp(end)},
        "coordinates": None,
        "summary": {"min": value, "q02": None, "q25": None, "median": value, "q75": None,
                    "q98": None, "max": value, "avg": value, "sd": None},
        "coverage": {"expectedCount": 1, "observedCount": 1, "percentComplete": complete,
                     "percentCoverage": complete},
    }


def test_openaq_flatten_pivots_sensors_into_one_row_per_station_hour(config_factory):
    cfg = config_factory(source_type="openaq", variables=("pm25", "pm10", "no2"),
                         entities=(Entity("8118", "Station A", 28.6, 77.2, attrs={"country": "IN"}),))
    envelopes = [
        {"request": {"entity_id": "8118", "sensor_id": 1, "parameter": "pm25"},
         "response": {"meta": {"found": 2}, "results": [openaq_result("2026-09-01T01:00", 40.0),
                                                        openaq_result("2026-09-01T02:00", 55.5, flagged=True)]}},
        {"request": {"entity_id": "8118", "sensor_id": 2, "parameter": "pm10"},
         "response": {"meta": {"found": 1}, "results": [openaq_result("2026-09-01T01:00", 90.0, complete=50.0)]}},
        {"request": {"entity_id": "8118", "sensor_id": 3, "parameter": "no2"},
         "response": {"meta": {"found": 0}, "results": []}},
    ]
    df = OpenAQConnector(cfg).flatten(envelopes)

    assert len(df) == 2                                              # 2 giờ, 1 trạm
    assert list(df.columns[:6]) == ["entity_id", "event_time", "entity_name", "latitude", "longitude", "country"]
    assert {"pm25", "pm10", "pm25_min", "pm25_max", "pm25_sd", "pm25_coverage", "pm25_flagged"} <= set(df.columns)
    assert "no2" not in df.columns                                   # pipeline sẽ bổ sung cột thiếu

    # event_time là mốc KẾT THÚC giờ đo
    assert list(df["event_time"]) == [pd.Timestamp("2026-09-01T01:00Z"), pd.Timestamp("2026-09-01T02:00Z")]
    first, second = df.iloc[0], df.iloc[1]
    assert first["pm25"] == 40.0 and first["pm10"] == 90.0 and first["pm10_coverage"] == 50.0
    assert second["pm25"] == 55.5 and pd.isna(second["pm10"])
    assert bool(second["pm25_flagged"]) is True and bool(first["pm25_flagged"]) is False


def test_openaq_flatten_empty(config_factory):
    cfg = config_factory(source_type="openaq", variables=("pm25",), entities=(Entity("1", "S"),))
    df = OpenAQConnector(cfg).flatten([{"request": {"entity_id": "1", "parameter": "pm25"},
                                        "response": {"results": []}}])
    assert df.empty and list(df.columns) == ["entity_id", "event_time"]


def test_openaq_extract_requires_api_key(config_factory, monkeypatch):
    monkeypatch.delenv("OPENAQ_API_KEY", raising=False)
    cfg = config_factory(source_type="openaq", variables=("pm25",),
                         entities=(Entity("1", "S", sensors=({"id": 9, "parameter": "pm25"},)),))
    with pytest.raises(RuntimeError, match="OPENAQ_API_KEY"):
        next(OpenAQConnector(cfg).extract(datetime(2026, 9, 1, tzinfo=UTC), datetime(2026, 9, 2, tzinfo=UTC)))


def test_openaq_extract_paginates_and_skips_missing_sensor(config_factory, monkeypatch):
    from framework.collection.connectors import openaq
    from framework.collection.http_client import HttpError

    cfg = config_factory(source_type="openaq", variables=("pm25", "pm10"),
                         entities=(Entity("1", "S", sensors=({"id": 9, "parameter": "pm25"},
                                                            {"id": 10, "parameter": "pm10"},
                                                            {"id": 11, "parameter": "bc"})),))   # bc không cần lấy
    calls = []

    class StubClient:
        def get_json(self, url, params):
            calls.append((url.rsplit("/", 2)[-2], params["page"]))
            if "/sensors/10/" in url:
                raise HttpError(404, url, "not found")
            return {"results": [openaq_result("2026-09-01T01:00", 1.0)] * (2 if params["page"] == 1 else 1)}

    monkeypatch.setattr(openaq, "make_client", lambda options=None: StubClient())
    connector = OpenAQConnector(cfg)
    connector.page_limit = 2
    envelopes = list(connector.extract(datetime(2026, 9, 1, tzinfo=UTC), datetime(2026, 9, 1, 5, tzinfo=UTC)))

    assert calls == [("9", 1), ("9", 2), ("10", 1)]                  # sensor 9 lật trang, 10 lỗi 404, 11 bỏ qua
    assert [e["request"]["sensor_id"] for e in envelopes] == [9, 9]
    params = envelopes[0]["request"]["params"]
    assert params["datetime_from"] == "2026-08-31T23:00:00Z" and params["datetime_to"] == "2026-09-01T06:00:00Z"


# ── cấu hình ──────────────────────────────────────────────────────────────────

def test_parse_duration():
    assert parse_duration("24h") == timedelta(hours=24)
    assert parse_duration("7d") == timedelta(days=7)
    with pytest.raises(ConfigError):
        parse_duration("một ngày")


def test_all_problem_configs_are_valid():
    problem_ids = discover_problem_ids()
    assert problem_ids == ["aq_pm25_clf", "aq_pm25_reg", "wx_rain_clf", "wx_temp_reg"]
    schedules = set()
    for problem_id in problem_ids:
        cfg = load_config(problem_id)
        assert cfg.horizon_steps == 24
        assert get_connector(cfg).source_type == cfg.source_type
        schedules.add(cfg.schedule)
    assert len(schedules) == 4                                       # không DAG nào gọi API cùng phút

    assert len(load_config("wx_rain_clf").entities) == 12
    assert load_config("wx_rain_clf").variables == load_config("wx_temp_reg").variables
    assert load_config("aq_pm25_clf").label.threshold == 35.4


def test_invalid_config_is_rejected(tmp_path):
    problem = tmp_path / "bad"
    problem.mkdir()
    (tmp_path / "entities.yaml").write_text("entities: []", encoding="utf-8")
    (problem / "collection.yaml").write_text(
        "problem_id: bad\ntask_type: binary\n"
        "source: {type: open_meteo, entities: ../entities.yaml, variables: [a]}\n"
        "collection: {schedule: '@daily', start_date: 2026-01-01, interval: 1d, frequency: 1h,"
        " horizon: 24h, maturity_lag: 7d}\n"
        "label: {target: a, agg: sum}\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="threshold"):
        load_config("bad", root=tmp_path)

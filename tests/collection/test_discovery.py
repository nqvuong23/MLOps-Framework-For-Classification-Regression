"""Test chọn trạm OpenAQ với client giả (payload theo schema của OpenAQ API v3)."""
from datetime import datetime, timedelta, timezone

from framework.collection.discovery import discover_stations

NOW = datetime.now(timezone.utc)
FRESH = {"utc": (NOW - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")}
STALE = {"utc": (NOW - timedelta(days=400)).strftime("%Y-%m-%dT%H:%M:%SZ")}
OLD = {"utc": (NOW - timedelta(days=900)).strftime("%Y-%m-%dT%H:%M:%SZ")}
RECENT_START = {"utc": (NOW - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")}


def sensor(sensor_id, name, units="µg/m³", last=FRESH):
    return {"id": sensor_id, "name": f"{name} {units}", "parameter": {"id": 0, "name": name, "units": units},
            "datetimeFirst": OLD, "datetimeLast": last}


def location(loc_id, sensors, first=OLD, last=FRESH, iso="IN"):
    return {"id": loc_id, "name": f"Station {loc_id}", "locality": "City", "timezone": "Asia/Kolkata",
            "country": {"id": 9, "code": iso, "name": iso}, "provider": {"id": 1, "name": "Gov"},
            "isMobile": False, "isMonitor": True, "coordinates": {"latitude": 1.0, "longitude": 2.0},
            "sensors": [{"id": s["id"], "name": s["name"], "parameter": s["parameter"]} for s in sensors],
            "datetimeFirst": first, "datetimeLast": last, "_details": sensors}


class StubClient:
    def __init__(self, locations):
        self.locations = {loc["id"]: loc for loc in locations}
        self.calls = []

    def get_json(self, url, params=None):
        self.calls.append(url)
        if url.endswith("/parameters"):
            return {"results": [{"id": 2, "name": "pm25", "units": "µg/m³"}, {"id": 1, "name": "pm10"}]}
        if url.endswith("/locations"):
            assert params["iso"] == "IN" and params["parameters_id"] == 2 and params["monitor"] == "true"
            return {"results": list(self.locations.values())}
        loc_id = int(url.split("/locations/")[1].split("/")[0])
        return {"results": self.locations[loc_id]["_details"]}


def test_discover_stations_filters_and_ranks():
    rich = [sensor(11, "pm25"), sensor(12, "pm10"), sensor(13, "no2"), sensor(14, "o3"), sensor(15, "so2")]
    client = StubClient([
        location(1, [sensor(21, "pm25"), sensor(22, "pm10"), sensor(23, "no2"), sensor(24, "o3")]),
        location(2, rich),                                                        # nhiều thông số nhất → đứng đầu
        location(3, rich, last=STALE),                                            # đã ngừng gửi dữ liệu
        location(4, rich, first=RECENT_START),                                    # lịch sử quá ngắn
        location(5, [sensor(51, "pm25"), sensor(52, "pm10")]),                    # quá ít thông số
        location(6, [sensor(61, "pm25", last=STALE), sensor(62, "pm10"), sensor(63, "no2"),
                     sensor(64, "o3"), sensor(65, "co")]),                        # sensor pm25 đã chết
        location(7, [sensor(71, "pm25"), sensor(72, "pm10"), sensor(73, "no2", units="ppm"),
                     sensor(74, "o3"), sensor(75, "so2")]),                       # no2 khác đơn vị đa số
    ])
    stations = discover_stations(["IN"], ["pm25", "pm10", "no2", "o3", "so2", "co"],
                                 max_stations=10, min_parameters=4, client=client)

    assert [s["id"] for s in stations] == ["2", "7", "1"]
    assert stations[0]["country"] == "IN" and stations[0]["timezone"] == "Asia/Kolkata"
    assert [s["parameter"] for s in stations[0]["sensors"]] == ["no2", "o3", "pm10", "pm25", "so2"]
    assert {"id": 11, "parameter": "pm25", "units": "µg/m³"} in stations[0]["sensors"]
    # trạm 7 giữ lại nhưng bỏ sensor no2 đo bằng ppm
    assert [s["parameter"] for s in stations[1]["sensors"]] == ["o3", "pm10", "pm25", "so2"]


def test_discover_stations_respects_max_stations():
    sensors = lambda base: [sensor(base + i, name) for i, name in enumerate(["pm25", "pm10", "no2", "o3"])]  # noqa: E731
    client = StubClient([location(i, sensors(i * 10)) for i in range(1, 6)])
    stations = discover_stations(["IN"], ["pm25", "pm10", "no2", "o3"], max_stations=2, client=client)
    assert len(stations) == 2
    assert sum("/sensors" in url for url in client.calls) == 2          # không gọi chi tiết thừa

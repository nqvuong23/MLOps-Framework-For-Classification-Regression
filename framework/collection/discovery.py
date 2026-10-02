"""
Chọn trạm OpenAQ để thu thập và ghi ra file entities (chạy một lần, cần OPENAQ_API_KEY).

Tiêu chí: trạm tham chiếu cố định, có sensor của thông số bắt buộc, còn gửi dữ liệu gần đây,
có lịch sử đủ dài; ưu tiên trạm đo được NHIỀU thông số (mỗi dòng có nhiều thuộc tính).
"""
from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime, timedelta, timezone

from .connectors.openaq import API_URL, make_client
from .window import parse_time

logger = logging.getLogger(__name__)


def _utc(node) -> datetime | None:
    value = (node or {}).get("utc")
    return parse_time(value) if value else None


def _paged(client, url: str, params: dict, limit: int = 1000):
    page = 1
    while True:
        body = client.get_json(url, {**params, "limit": limit, "page": page})
        results = body.get("results") or []
        yield from results
        if len(results) < limit:
            return
        page += 1


def discover_stations(iso_codes, parameters, required: str = "pm25", max_stations: int = 10,
                      per_country: int | None = None, min_parameters: int = 4,
                      max_age_hours: int = 48, min_history_days: int = 365,
                      url: str = API_URL, client=None) -> list:
    client = client or make_client()
    now = datetime.now(timezone.utc)
    newest_allowed = now - timedelta(hours=max_age_hours)
    oldest_required = now - timedelta(days=min_history_days)
    wanted = set(parameters)

    required_ids = [p["id"] for p in _paged(client, f"{url}/parameters", {}) if p.get("name") == required]
    if not required_ids:
        raise RuntimeError(f"OpenAQ không có thông số '{required}'")

    candidates = []
    for iso in iso_codes:
        seen = set()
        for parameter_id in required_ids:
            query = {"iso": iso, "parameters_id": parameter_id, "monitor": "true", "mobile": "false"}
            for location in _paged(client, f"{url}/locations", query):
                if location["id"] in seen:
                    continue
                seen.add(location["id"])
                first, last = _utc(location.get("datetimeFirst")), _utc(location.get("datetimeLast"))
                if not first or not last or last < newest_allowed or first > oldest_required:
                    continue
                names = {(s.get("parameter") or {}).get("name") for s in location.get("sensors") or []}
                if required not in names or len(names & wanted) < min_parameters:
                    continue
                candidates.append((len(names & wanted), (now - first).days, location))
        logger.info("%s: đã duyệt %d trạm, tổng ứng viên hiện có %d", iso, len(seen), len(candidates))

    # Nhiều thông số trước, lịch sử dài trước
    candidates.sort(key=lambda item: (-item[0], -item[1]))

    stations, per_iso = [], Counter()
    for _, _, location in candidates:
        if len(stations) >= max_stations:
            break
        iso = (location.get("country") or {}).get("code")
        if per_country and per_iso[iso] >= per_country:
            continue

        # Chi tiết từng sensor: chọn 1 sensor còn hoạt động cho mỗi thông số
        details = client.get_json(f"{url}/locations/{location['id']}/sensors").get("results") or []
        chosen = {}
        for sensor in details:
            name = (sensor.get("parameter") or {}).get("name")
            last = _utc(sensor.get("datetimeLast"))
            if name not in wanted or not last or last < newest_allowed:
                continue
            if name not in chosen or last > chosen[name][0]:
                chosen[name] = (last, sensor)
        if required not in chosen or len(chosen) < min_parameters:
            continue

        coordinates = location.get("coordinates") or {}
        stations.append({
            "id": str(location["id"]),
            "name": location.get("name") or str(location["id"]),
            "latitude": coordinates.get("latitude"),
            "longitude": coordinates.get("longitude"),
            "country": iso,
            "locality": location.get("locality"),
            "timezone": location.get("timezone"),
            "provider": (location.get("provider") or {}).get("name"),
            "sensors": [{"id": sensor["id"], "parameter": name,
                         "units": (sensor.get("parameter") or {}).get("units")}
                        for name, (_, sensor) in sorted(chosen.items())],
        })
        per_iso[iso] += 1

    return _drop_minority_units(stations, required)


def _drop_minority_units(stations: list, required: str) -> list:
    """Mỗi thông số chỉ giữ MỘT đơn vị (đa số) để một cột không trộn µg/m³ với ppm."""
    units = {}
    for station in stations:
        for sensor in station["sensors"]:
            units.setdefault(sensor["parameter"], Counter())[sensor["units"]] += 1
    majority = {name: counter.most_common(1)[0][0] for name, counter in units.items()}

    kept = []
    for station in stations:
        sensors = [s for s in station["sensors"] if s["units"] == majority[s["parameter"]]]
        dropped = len(station["sensors"]) - len(sensors)
        if dropped:
            logger.warning("Trạm %s: bỏ %d sensor khác đơn vị đa số", station["id"], dropped)
        if any(s["parameter"] == required for s in sensors):
            kept.append({**station, "sensors": sensors})
    return kept

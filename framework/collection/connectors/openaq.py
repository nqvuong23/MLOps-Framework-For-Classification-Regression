"""
Connector OpenAQ API v3 (cần API key trong biến môi trường OPENAQ_API_KEY).

JSON trả về ở DẠNG DÒNG: `results[]`, mỗi phần tử là số đo trung bình một giờ của MỘT sensor.
Phải gọi theo từng sensor (`/sensors/{id}/hours`) rồi gộp các sensor của cùng trạm thành một dòng.

event_time = `period.datetimeTo.utc` (mốc KẾT THÚC của giờ đo) → dòng tại t chỉ chứa số đo
đã có ở thời điểm t, không lẫn số đo của giờ kế tiếp.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Iterable, Iterator

import pandas as pd

from ..http_client import HttpClient, HttpError
from .base import KEY_COLUMNS, Connector

logger = logging.getLogger(__name__)

API_URL = "https://api.openaq.org/v3"
API_KEY_ENV = "OPENAQ_API_KEY"
# Mỗi số đo giờ được bung thành các cột: <param> (giá trị) + <param>_<field> dưới đây
SUMMARY_FIELDS = ("min", "max", "sd")
EXTRA_FIELDS = SUMMARY_FIELDS + ("coverage", "flagged")


def make_client(options: dict | None = None) -> HttpClient:
    options = options or {}
    api_key = os.environ.get(options.get("api_key_env", API_KEY_ENV), "")
    if not api_key:
        raise RuntimeError(f"Thiếu biến môi trường {options.get('api_key_env', API_KEY_ENV)} (API key OpenAQ)")
    # Giới hạn miễn phí 60 request/phút → giãn ~1.1s giữa 2 request
    return HttpClient(headers={"X-API-Key": api_key},
                      min_interval=float(options.get("min_interval_s", 1.1)))


class OpenAQConnector(Connector):
    source_type = "openaq"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.url = cfg.options.get("url", API_URL).rstrip("/")
        self.page_limit = int(cfg.options.get("page_limit", 1000))

    def extract(self, start: datetime, end: datetime) -> Iterator[dict]:
        client = make_client(self.cfg.options)
        # Nới 1 giờ mỗi đầu: không phụ thuộc việc API lọc theo đầu hay cuối của giờ đo
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        date_from = (start - timedelta(hours=1)).strftime(fmt)
        date_to = (end + timedelta(hours=1)).strftime(fmt)

        for entity in self.cfg.entities:
            for sensor in entity.sensors:
                if sensor["parameter"] not in self.cfg.variables:
                    continue
                url = f"{self.url}/sensors/{sensor['id']}/hours"
                page = 1
                while True:
                    params = {"datetime_from": date_from, "datetime_to": date_to,
                              "limit": self.page_limit, "page": page}
                    try:
                        response = client.get_json(url, params)
                    except HttpError as exc:
                        if exc.status == 404:      # sensor bị gỡ khỏi OpenAQ — bỏ qua, không làm hỏng cả run
                            logger.warning("Sensor %s (trạm %s) không tồn tại — bỏ qua", sensor["id"], entity.id)
                            break
                        raise
                    yield {
                        "request": {
                            "url": url, "params": params, "entity_id": entity.id,
                            "sensor_id": sensor["id"], "parameter": sensor["parameter"],
                            "fetched_at": datetime.now(timezone.utc).isoformat(),
                        },
                        "response": response,
                    }
                    if len(response.get("results") or []) < self.page_limit:
                        break
                    page += 1

    def flatten(self, envelopes: Iterable[dict]) -> pd.DataFrame:
        rows = []
        for envelope in envelopes:
            request = envelope["request"]
            for result in envelope["response"].get("results") or []:
                period_end = ((result.get("period") or {}).get("datetimeTo") or {}).get("utc")
                if not period_end:
                    continue
                summary = result.get("summary") or {}
                rows.append({
                    "entity_id": request["entity_id"],
                    "parameter": request["parameter"],
                    "event_time": period_end,
                    "value": result.get("value"),
                    **{name: summary.get(name) for name in SUMMARY_FIELDS},
                    "coverage": (result.get("coverage") or {}).get("percentComplete"),
                    "flagged": (result.get("flagInfo") or {}).get("hasFlags"),
                })
        if not rows:
            return pd.DataFrame(columns=KEY_COLUMNS)

        long = pd.DataFrame(rows)
        long["event_time"] = pd.to_datetime(long["event_time"], utc=True)
        long = long.drop_duplicates(KEY_COLUMNS + ["parameter"], keep="first")

        # Dạng dòng (1 dòng / sensor / giờ) → dạng rộng (1 dòng / trạm / giờ)
        parameters = [p for p in self.cfg.variables if p in set(long["parameter"])]
        pieces = []
        for field_name in ("value",) + EXTRA_FIELDS:
            piece = long.pivot(index=KEY_COLUMNS, columns="parameter", values=field_name)[parameters]
            if field_name == "flagged":
                piece = piece.astype("boolean")
            else:
                piece = piece.apply(pd.to_numeric, errors="coerce")
            if field_name != "value":
                piece = piece.add_suffix(f"_{field_name}")
            pieces.append(piece)
        wide = pd.concat(pieces, axis=1).reset_index()
        wide.columns.name = None
        return self.with_entity_attrs(wide)

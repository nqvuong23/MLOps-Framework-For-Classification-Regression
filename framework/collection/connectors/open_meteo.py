"""
Connector Open-Meteo Historical Weather API (không cần API key).

JSON trả về ở DẠNG CỘT: {"hourly": {"time": [...], "<biến>": [...], ...}}; gọi nhiều toạ độ
thì trả về MẢNG các object theo đúng thứ tự toạ độ đã gửi.

Mốc `time` của Open-Meteo: biến tức thời là giá trị tại mốc đó; biến tích luỹ (precipitation,
rain, ...) là tổng của GIỜ TRƯỚC ĐÓ → khớp sẵn quy ước event_time của framework.
"""
from __future__ import annotations

import logging
import time
from datetime import date, datetime, timedelta, timezone
from typing import Iterable, Iterator

import pandas as pd

from ..http_client import HttpClient
from .base import Connector

logger = logging.getLogger(__name__)

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
# Open-Meteo tính "trọng số" request: > 10 biến hoặc > 14 ngày / địa điểm được đếm thành nhiều call.
# Giới hạn miễn phí 600 call/phút → nghỉ 0.15s cho mỗi call quy đổi (~400 call/phút).
SECONDS_PER_WEIGHTED_CALL = 0.15


class OpenMeteoConnector(Connector):
    source_type = "open_meteo"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.url = cfg.options.get("url", ARCHIVE_URL)
        self.models = cfg.options.get("models")               # ví dụ "era5" để nhãn không bị sửa lại
        self.chunk_days = int(cfg.options.get("chunk_days", 31))
        self.client = HttpClient()

    def _weight(self, n_days: int) -> float:
        return len(self.cfg.entities) * max(1.0, len(self.cfg.variables) / 10) * max(1.0, n_days / 14)

    def extract(self, start: datetime, end: datetime) -> Iterator[dict]:
        # API nhận theo NGÀY (bao gồm cả 2 đầu) → lấy trọn ngày, bước sau sẽ cắt lại theo giờ
        first_day, last_day = start.date(), end.date()
        entities = self.cfg.entities
        day = first_day
        while day <= last_day:
            chunk_end = min(day + timedelta(days=self.chunk_days - 1), last_day)
            params = {
                "latitude": ",".join(str(e.latitude) for e in entities),
                "longitude": ",".join(str(e.longitude) for e in entities),
                "start_date": day.isoformat(),
                "end_date": chunk_end.isoformat(),
                "hourly": ",".join(self.cfg.variables),
                "timezone": "UTC",
            }
            if self.models:
                params["models"] = self.models
            logger.info("Open-Meteo: %s → %s | %d địa điểm", day, chunk_end, len(entities))
            envelope = {
                "request": {
                    "url": self.url,
                    "params": params,
                    "entity_ids": [e.id for e in entities],
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                },
                "response": self.client.get_json(self.url, params),
            }
            # Nghỉ SAU mỗi request theo trọng số của nó → backfill nhiều cửa sổ liên tiếp không vượt giới hạn
            time.sleep(self._weight((chunk_end - day).days + 1) * SECONDS_PER_WEIGHTED_CALL)
            yield envelope
            day = chunk_end + timedelta(days=1)

    def flatten(self, envelopes: Iterable[dict]) -> pd.DataFrame:
        frames = []
        for envelope in envelopes:
            response = envelope["response"]
            locations = response if isinstance(response, list) else [response]
            entity_ids = envelope["request"]["entity_ids"]
            if len(locations) != len(entity_ids):
                raise ValueError(f"Open-Meteo trả {len(locations)} địa điểm, đã gửi {len(entity_ids)}")

            for entity_id, location in zip(entity_ids, locations):
                if location.get("utc_offset_seconds", 0) != 0:
                    raise ValueError("Open-Meteo không trả giờ UTC — kiểm tra tham số timezone")
                hourly = pd.DataFrame(location["hourly"])          # "bung" các mảng song song thành dòng
                hourly.insert(0, "event_time", pd.to_datetime(hourly.pop("time"), utc=True))
                hourly.insert(0, "entity_id", entity_id)
                hourly.insert(2, "elevation", location.get("elevation"))
                frames.append(hourly)

        if not frames:
            return pd.DataFrame(columns=["entity_id", "event_time"])
        return self.with_entity_attrs(pd.concat(frames, ignore_index=True))

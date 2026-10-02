"""Giao diện chung của một connector nguồn dữ liệu."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, Iterator

import pandas as pd

from ..config import CollectionConfig

KEY_COLUMNS = ["entity_id", "event_time"]


class Connector(ABC):
    """
    Mỗi nguồn hiện thực 2 việc:
      extract(start, end) → sinh các "envelope" {"request": {...}, "response": <JSON nguyên bản>}
      flatten(envelopes)  → DataFrame: entity_id, event_time (UTC), mỗi biến một cột

    Quy ước event_time: giá trị tại dòng t mô tả trạng thái ĐÃ BIẾT ở thời điểm t
    (đại lượng tích luỹ/trung bình theo giờ gắn vào mốc KẾT THÚC của giờ đó).
    """
    source_type: str = ""

    def __init__(self, cfg: CollectionConfig):
        self.cfg = cfg

    @abstractmethod
    def extract(self, start: datetime, end: datetime) -> Iterator[dict]:
        """Gọi API lấy quan sát có event_time ∈ [start, end] (có thể trả rộng hơn)."""

    @abstractmethod
    def flatten(self, envelopes: Iterable[dict]) -> pd.DataFrame:
        """JSON nguyên bản → bảng quan sát dạng rộng."""

    def entity_frame(self) -> pd.DataFrame:
        """Thuộc tính tĩnh của thực thể (tên, toạ độ, ...) để gắn vào từng dòng."""
        rows = []
        for entity in self.cfg.entities:
            rows.append({"entity_id": entity.id, "entity_name": entity.name,
                         "latitude": entity.latitude, "longitude": entity.longitude, **entity.attrs})
        return pd.DataFrame(rows)

    def with_entity_attrs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Chèn các cột thuộc tính tĩnh ngay sau entity_id, event_time."""
        attrs = self.entity_frame()
        if df.empty or attrs.empty:
            return df
        attrs = attrs[["entity_id"] + [c for c in attrs.columns if c != "entity_id" and c not in df.columns]]
        merged = df.merge(attrs, on="entity_id", how="left")
        attr_cols = [c for c in attrs.columns if c != "entity_id"]
        value_cols = [c for c in merged.columns if c not in KEY_COLUMNS + attr_cols]
        return merged[KEY_COLUMNS + attr_cols + value_cols]

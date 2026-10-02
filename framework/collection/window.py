"""
Tính cửa sổ thời gian của một lần thu thập.

Chỉ lấy điểm neo có nhãn đã "chín". Với run tại thời điểm T (làm tròn xuống theo `interval`):

    điểm neo t ∈ [T − H − M − interval,  T − H − M)
    dữ liệu cần gọi: từ điểm neo đầu tiên đến (điểm neo cuối + H)

H = horizon của nhãn, M = maturity_lag (thời gian chờ nguồn chốt số liệu).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .config import CollectionConfig

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def to_utc(value: datetime) -> datetime:
    """Datetime bất kỳ → datetime UTC thuần (naive coi như UTC)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return datetime.fromtimestamp(value.timestamp(), tz=timezone.utc)


def parse_time(text: str) -> datetime:
    """'2026-09-20' / '2026-09-20T06:00' / '...Z' / '...+07:00' → datetime UTC."""
    return to_utc(datetime.fromisoformat(str(text).strip().replace("Z", "+00:00")))


def floor_time(value: datetime, step) -> datetime:
    return EPOCH + ((to_utc(value) - EPOCH) // step) * step


@dataclass(frozen=True)
class Window:
    anchor_start: datetime      # điểm neo đầu (bao gồm)
    anchor_end: datetime        # điểm neo cuối (không bao gồm)
    fetch_start: datetime       # quan sát cần có: từ đây (bao gồm) ...
    fetch_end: datetime         # ... đến đây (bao gồm) = điểm neo cuối + H

    @property
    def key(self) -> str:
        """Khoá xác định duy nhất cửa sổ — dùng làm tên thư mục landing / manifest."""
        fmt = "%Y%m%dT%H%MZ"
        return f"{self.anchor_start.strftime(fmt)}_{self.anchor_end.strftime(fmt)}"

    def to_dict(self) -> dict:
        return {name: getattr(self, name).isoformat()
                for name in ("anchor_start", "anchor_end", "fetch_start", "fetch_end")}

    @classmethod
    def from_dict(cls, data: dict) -> "Window":
        return cls(**{name: parse_time(value) for name, value in data.items()})


def explicit_window(cfg: CollectionConfig, start: datetime, end: datetime) -> Window:
    """Cửa sổ cho khoảng điểm neo [start, end) chỉ định tay (backfill)."""
    start, end = floor_time(start, cfg.frequency), floor_time(end, cfg.frequency)
    if end <= start:
        raise ValueError(f"Khoảng điểm neo rỗng: start={start.isoformat()} end={end.isoformat()}")
    return Window(anchor_start=start, anchor_end=end, fetch_start=start,
                  fetch_end=end - cfg.frequency + cfg.horizon)


def scheduled_window(cfg: CollectionConfig, reference_time: datetime) -> Window:
    """Cửa sổ của một run theo lịch tại `reference_time` (logical_date của DAG run)."""
    run_time = floor_time(reference_time, cfg.interval)
    newest_anchor_end = run_time - cfg.horizon - cfg.maturity_lag
    return explicit_window(cfg, newest_anchor_end - cfg.interval, newest_anchor_end)

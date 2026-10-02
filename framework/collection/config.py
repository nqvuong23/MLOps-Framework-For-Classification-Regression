"""Đọc và kiểm tra `problems/<problem_id>/collection.yaml`."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

TASK_TYPES = ("binary", "regression")
AGGREGATIONS = ("mean", "sum", "last", "max", "min")
OPERATORS = (">", ">=", "<", "<=")

_DURATION_RE = re.compile(r"^\s*(\d+)\s*([smhdw])\s*$")
_DURATION_UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}


class ConfigError(ValueError):
    """Cấu hình collection.yaml không hợp lệ."""


def parse_duration(text) -> timedelta:
    """'24h' / '7d' / '30m' → timedelta."""
    match = _DURATION_RE.match(str(text))
    if not match:
        raise ConfigError(f"Khoảng thời gian không hợp lệ: {text!r} (ví dụ đúng: 1h, 24h, 7d)")
    return timedelta(**{_DURATION_UNITS[match.group(2)]: int(match.group(1))})


def problems_dir() -> Path:
    """Thư mục chứa config các bài toán; override bằng biến môi trường PROBLEMS_DIR."""
    env = os.environ.get("PROBLEMS_DIR")
    return Path(env) if env else Path(__file__).resolve().parents[2] / "problems"


@dataclass(frozen=True)
class Entity:
    """Một thực thể cần thu thập: trạm quan trắc (OpenAQ) hoặc địa điểm (Open-Meteo)."""
    id: str
    name: str
    latitude: float | None = None
    longitude: float | None = None
    sensors: tuple = ()                           # chỉ OpenAQ: ({id, parameter, units}, ...)
    attrs: dict = field(default_factory=dict)     # thuộc tính tĩnh khác: country, timezone, ...


@dataclass(frozen=True)
class LabelSpec:
    target: str                    # cột dùng để tính nhãn
    agg: str                       # cách tổng hợp trên cửa sổ (t, t + horizon]
    min_coverage: float            # tỉ lệ số đo tối thiểu trong cửa sổ để nhãn hợp lệ
    threshold: float | None        # chỉ bài toán binary
    operator: str
    valid_min: float | None        # giá trị ngoài [valid_min, valid_max] coi như thiếu KHI TÍNH NHÃN
    valid_max: float | None


@dataclass(frozen=True)
class CollectionConfig:
    problem_id: str
    task_type: str
    description: str
    source_type: str
    variables: tuple
    options: dict
    entities: tuple
    schedule: str
    start_date: datetime
    interval: timedelta            # mỗi run phụ trách bao nhiêu thời gian điểm neo
    frequency: timedelta           # độ phân giải của dữ liệu nguồn
    horizon: timedelta             # H: độ dài cửa sổ nhãn
    maturity_lag: timedelta        # M: thời gian chờ nguồn chốt số liệu
    label: LabelSpec

    @property
    def horizon_steps(self) -> int:
        return int(self.horizon / self.frequency)


def _load_entities(path: Path) -> tuple:
    if not path.exists():
        raise ConfigError(f"Không tìm thấy file entities: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    reserved = {"id", "name", "latitude", "longitude", "sensors"}
    entities = []
    for item in raw.get("entities") or []:
        entities.append(Entity(
            id=str(item["id"]),
            name=str(item.get("name", item["id"])),
            latitude=item.get("latitude"),
            longitude=item.get("longitude"),
            sensors=tuple(item.get("sensors") or ()),
            attrs={k: v for k, v in item.items() if k not in reserved},
        ))
    ids = [e.id for e in entities]
    if len(ids) != len(set(ids)):
        raise ConfigError(f"Trùng entity id trong {path}")
    return tuple(entities)


def _to_utc_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(str(value))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def load_config(problem_id: str, root: Path | None = None) -> CollectionConfig:
    root = Path(root) if root else problems_dir()
    path = root / problem_id / "collection.yaml"
    if not path.exists():
        raise ConfigError(f"Không tìm thấy {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    try:
        source, coll, lab = raw["source"], raw["collection"], raw["label"]
        cfg = CollectionConfig(
            problem_id=str(raw["problem_id"]),
            task_type=str(raw["task_type"]),
            description=str(raw.get("description", "")),
            source_type=str(source["type"]),
            variables=tuple(source["variables"]),
            options=dict(source.get("options") or {}),
            entities=_load_entities((path.parent / source["entities"]).resolve()),
            schedule=str(coll["schedule"]),
            start_date=_to_utc_datetime(coll["start_date"]),
            interval=parse_duration(coll["interval"]),
            frequency=parse_duration(coll["frequency"]),
            horizon=parse_duration(coll["horizon"]),
            maturity_lag=parse_duration(coll["maturity_lag"]),
            label=LabelSpec(
                target=str(lab["target"]),
                agg=str(lab["agg"]),
                min_coverage=float(lab.get("min_coverage", 1.0)),
                threshold=None if lab.get("threshold") is None else float(lab["threshold"]),
                operator=str(lab.get("operator", ">")),
                valid_min=None if lab.get("valid_min") is None else float(lab["valid_min"]),
                valid_max=None if lab.get("valid_max") is None else float(lab["valid_max"]),
            ),
        )
    except KeyError as exc:
        raise ConfigError(f"{path}: thiếu khoá bắt buộc {exc}") from exc

    _validate(cfg, path)
    return cfg


def _validate(cfg: CollectionConfig, path: Path) -> None:
    def fail(message: str):
        raise ConfigError(f"{path}: {message}")

    if cfg.problem_id != path.parent.name:
        fail(f"problem_id '{cfg.problem_id}' phải trùng tên thư mục '{path.parent.name}'")
    if cfg.task_type not in TASK_TYPES:
        fail(f"task_type phải thuộc {TASK_TYPES}")
    if cfg.label.agg not in AGGREGATIONS:
        fail(f"label.agg phải thuộc {AGGREGATIONS}")
    if cfg.label.operator not in OPERATORS:
        fail(f"label.operator phải thuộc {OPERATORS}")
    if cfg.task_type == "binary" and cfg.label.threshold is None:
        fail("bài toán binary cần label.threshold")
    if cfg.label.target not in cfg.variables:
        fail(f"label.target '{cfg.label.target}' không nằm trong source.variables")
    if not 0 < cfg.label.min_coverage <= 1:
        fail("label.min_coverage phải trong (0, 1]")
    for name in ("interval", "horizon"):
        if getattr(cfg, name) % cfg.frequency:
            fail(f"collection.{name} phải là bội số của collection.frequency")
    if cfg.horizon_steps < 1:
        fail("collection.horizon phải >= collection.frequency")


def discover_problem_ids(root: Path | None = None) -> list:
    """Mọi thư mục con có collection.yaml (bỏ qua thư mục bắt đầu bằng '_')."""
    root = Path(root) if root else problems_dir()
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir()
                  if p.is_dir() and not p.name.startswith("_") and (p / "collection.yaml").exists())

"""Registry connector: thêm nguồn mới = thêm 1 class + 1 dòng ở đây."""
from __future__ import annotations

from ..config import CollectionConfig, ConfigError
from .base import Connector
from .open_meteo import OpenMeteoConnector
from .openaq import OpenAQConnector

CONNECTORS = {cls.source_type: cls for cls in (OpenMeteoConnector, OpenAQConnector)}


def get_connector(cfg: CollectionConfig) -> Connector:
    try:
        return CONNECTORS[cfg.source_type](cfg)
    except KeyError:
        raise ConfigError(f"source.type '{cfg.source_type}' chưa được hỗ trợ; có: {sorted(CONNECTORS)}") from None

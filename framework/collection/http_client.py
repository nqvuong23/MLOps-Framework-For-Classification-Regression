"""HTTP GET trả JSON, có giãn nhịp gọi và retry — dùng chung cho mọi connector."""
from __future__ import annotations

import logging
import time

import requests

logger = logging.getLogger(__name__)

RETRY_STATUS = {429, 500, 502, 503, 504}


class HttpError(RuntimeError):
    def __init__(self, status: int, url: str, body: str):
        super().__init__(f"HTTP {status} từ {url}: {body[:300]}")
        self.status = status


class HttpClient:
    def __init__(self, headers: dict | None = None, min_interval: float = 0.0,
                 timeout: float = 90.0, max_retries: int = 6):
        self.session = requests.Session()
        self.session.headers.update(headers or {})
        self.min_interval = min_interval      # giây tối thiểu giữa 2 request (tôn trọng rate limit)
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_call = 0.0

    def _throttle(self) -> None:
        wait = self.min_interval - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    @staticmethod
    def _retry_wait(response, fallback: float) -> float:
        """Ưu tiên thời gian chờ do server chỉ định (Retry-After / x-ratelimit-reset tính bằng giây)."""
        for header in ("Retry-After", "x-ratelimit-reset"):
            value = response.headers.get(header)
            try:
                seconds = float(value)
            except (TypeError, ValueError):
                continue
            if 0 < seconds <= 3600:
                return seconds + 1
        return fallback

    def get_json(self, url: str, params: dict | None = None):
        delay = 2.0
        for attempt in range(1, self.max_retries + 1):
            self._throttle()
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
            except (requests.ConnectionError, requests.Timeout) as exc:
                if attempt == self.max_retries:
                    raise
                logger.warning("Lỗi kết nối %s (lần %d/%d): %s", url, attempt, self.max_retries, exc)
                time.sleep(delay)
                delay = min(delay * 2, 120)
                continue

            if response.status_code == 200:
                return response.json()
            if response.status_code in RETRY_STATUS and attempt < self.max_retries:
                wait = self._retry_wait(response, delay)
                logger.warning("HTTP %d từ %s — thử lại sau %.0fs (lần %d/%d)",
                               response.status_code, url, wait, attempt, self.max_retries)
                time.sleep(wait)
                delay = min(delay * 2, 120)
                continue
            raise HttpError(response.status_code, url, response.text)
        raise RuntimeError(f"GET {url} thất bại sau {self.max_retries} lần")

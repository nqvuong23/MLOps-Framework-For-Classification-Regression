"""
Lưu trữ cho data collection — chạy trên S3 (production) hoặc thư mục local (test) qua fsspec.

Layout dưới base URI của một bài toán:
    landing/window=<key>/part-00000.json.gz            JSON nguyên bản từ API (bất biến)
    observations/event_date=YYYY-MM-DD/part-00000.parquet   bảng quan sát đã flatten
    labeled/event_date=YYYY-MM-DD/part-00000.parquet        bảng training có nhãn
    _manifests/window=<key>.json                       tóm tắt một lần chạy
"""
from __future__ import annotations

import gzip
import io
import json
import os
from datetime import datetime, timedelta

import fsspec
import pandas as pd

PART_FILE = "part-00000.parquet"


def default_base_uri() -> str:
    """s3://<S3_BUCKET_NAME>/<S3_PREFIX_COLLECTION>; override toàn bộ bằng COLLECTION_BASE_URI."""
    override = os.environ.get("COLLECTION_BASE_URI")
    if override:
        return override.rstrip("/")
    bucket = os.environ.get("S3_BUCKET_NAME", "")
    if not bucket:
        raise RuntimeError("Thiếu S3_BUCKET_NAME (hoặc COLLECTION_BASE_URI) để biết nơi lưu dữ liệu")
    prefix = os.environ.get("S3_PREFIX_COLLECTION", "data-collection").strip("/")
    return f"s3://{bucket}/{prefix}"


class Storage:
    """Đọc/ghi theo đường dẫn tương đối dưới một base URI (s3://... hoặc đường dẫn local)."""

    def __init__(self, base_uri: str, **storage_options):
        self.base_uri = base_uri.rstrip("/")
        self.fs, root = fsspec.core.url_to_fs(self.base_uri, **storage_options)
        self.root = root.rstrip("/")
        protocol = self.fs.protocol
        self._is_local = "file" in ((protocol,) if isinstance(protocol, str) else protocol)

    def uri(self, rel: str) -> str:
        return f"{self.base_uri}/{rel.strip('/')}"

    def _path(self, rel: str) -> str:
        return f"{self.root}/{rel.strip('/')}"

    # ── bytes ────────────────────────────────────────────────────────────────
    def write_bytes(self, rel: str, data: bytes) -> None:
        path = self._path(rel)
        if self._is_local:
            self.fs.makedirs(path.rsplit("/", 1)[0], exist_ok=True)
        self.fs.pipe_file(path, data)

    def read_bytes(self, rel: str) -> bytes:
        return self.fs.cat_file(self._path(rel))

    def exists(self, rel: str) -> bool:
        self.fs.invalidate_cache()          # s3fs cache listing — luôn hỏi lại trạng thái thật
        return self.fs.exists(self._path(rel))

    def list_files(self, rel_prefix: str) -> list:
        """Mọi file dưới prefix, trả về đường dẫn tương đối, đã sắp xếp."""
        self.fs.invalidate_cache()
        try:
            found = self.fs.find(self._path(rel_prefix))
        except FileNotFoundError:
            return []
        base = self.root + "/"
        return sorted(p.replace("\\", "/").split(base, 1)[-1] for p in found)

    def delete(self, rel: str) -> None:
        if self.exists(rel):
            self.fs.rm(self._path(rel), recursive=True)

    # ── JSON / Parquet ───────────────────────────────────────────────────────
    def write_json_gz(self, rel: str, obj) -> None:
        self.write_bytes(rel, gzip.compress(json.dumps(obj, ensure_ascii=False).encode("utf-8")))

    def read_json_gz(self, rel: str):
        return json.loads(gzip.decompress(self.read_bytes(rel)).decode("utf-8"))

    def write_json(self, rel: str, obj) -> None:
        self.write_bytes(rel, json.dumps(obj, ensure_ascii=False, indent=2, default=str).encode("utf-8"))

    def write_parquet(self, rel: str, df: pd.DataFrame) -> None:
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        self.write_bytes(rel, buffer.getvalue())

    def read_parquet(self, rel: str) -> pd.DataFrame:
        return pd.read_parquet(io.BytesIO(self.read_bytes(rel)))

    # ── bảng partition theo ngày của event_time ──────────────────────────────
    @staticmethod
    def partition_path(layer: str, day: str) -> str:
        return f"{layer}/event_date={day}/{PART_FILE}"

    def replace_range(self, layer: str, df: pd.DataFrame, start: datetime, end: datetime) -> list:
        """
        Thay toàn bộ dòng có event_time ∈ [start, end) của `layer` bằng `df`.

        Dòng ngoài khoảng trong cùng partition được giữ nguyên → run theo giờ, run theo ngày
        và backfill cùng ghi vào một file/ngày mà không trùng dòng; rerun cho kết quả y hệt.
        """
        if not df.empty and not ((df["event_time"] >= start) & (df["event_time"] < end)).all():
            raise ValueError("replace_range: df có dòng nằm ngoài khoảng [start, end)")

        new_days = df["event_time"].dt.strftime("%Y-%m-%d") if not df.empty else pd.Series(dtype="object")
        touched = []
        day = start.date()
        last_day = (end - timedelta(microseconds=1)).date()
        while day <= last_day:
            day_str = day.isoformat()
            rel = self.partition_path(layer, day_str)
            frames = []
            existed = self.exists(rel)
            if existed:
                old = self.read_parquet(rel)
                kept = old[(old["event_time"] < start) | (old["event_time"] >= end)]
                if not kept.empty:
                    frames.append(kept)
            if not df.empty:
                new_part = df[new_days == day_str]
                if not new_part.empty:
                    frames.append(new_part)

            if frames:
                merged = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]
                merged = merged.sort_values(["event_time", "entity_id"]).reset_index(drop=True)
                self.write_parquet(rel, merged)
                touched.append(rel)
            elif existed:
                self.delete(rel)
            day += timedelta(days=1)
        return touched

    def read_range(self, layer: str, start: datetime, end: datetime) -> pd.DataFrame:
        """Đọc các dòng có event_time ∈ [start, end] (bao gồm hai đầu)."""
        frames = []
        day = start.date()
        while day <= end.date():
            rel = self.partition_path(layer, day.isoformat())
            if self.exists(rel):
                frames.append(self.read_parquet(rel))
            day += timedelta(days=1)
        if not frames:
            return pd.DataFrame()
        df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]
        return df[(df["event_time"] >= start) & (df["event_time"] <= end)].reset_index(drop=True)

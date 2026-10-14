"""
BƯỚC 2 — LÀM PHẲNG (JSON → BẢNG)
=================================
Biến JSON dạng cột của Open-Meteo thành bảng "dài theo thời gian, rộng theo biến":

    JSON (1 file / tháng)                           Bảng (1 dòng / thành phố / giờ)
    ─────────────────────────────────────           ──────────────────────────────────────────────
    [ { "hourly": {                                 entity_id  event_time        temperature_2m  ...
          "time":           [t0, t1, ...],    →     hanoi      2023-10-01 00:00  27.7            ...
          "temperature_2m": [27.7, 28.0, ...],      hanoi      2023-10-01 01:00  28.0            ...
          ... } },                                  tokyo      2023-10-01 00:00  22.1            ...
      { ... thành phố thứ 2 ... } ]

    Đầu vào : 1_raw/*.json.gz
    Đầu ra  : 2_flat/observations.parquet

Bước này CHỈ đổi hình dạng — không sửa giá trị, không ép kiểu, không bỏ dòng. Giữ nguyên mọi
"bẩn" của nguồn để bước làm sạch xử lý có kiểm soát và đếm được.

Ba kiểm tra cấu trúc bắt buộc (sai là dừng ngay, vì sai ở đây thì mọi bước sau đều sai):
  1. Số object trong response == số entity_ids đã gửi (response chỉ ghép được theo THỨ TỰ).
  2. utc_offset_seconds == 0 (mọi mốc thời gian phải là UTC).
  3. Mọi mảng trong "hourly" dài bằng mảng "time".

Chạy:
    python test/flatten.py
"""
from __future__ import annotations

import gzip
import json

import pandas as pd

from config import (CITIES, FLAT_DIR, KEYS, RAW_DIR, VARIABLES, header, read_json, rel, setup_console,
                    write_parquet)


def flatten_envelope(envelope: dict, file_name: str) -> list[pd.DataFrame]:
    """Một envelope (1 request, nhiều thành phố) → danh sách DataFrame, mỗi thành phố một bảng."""
    response = envelope["response"]
    locations = response if isinstance(response, list) else [response]   # 1 toạ độ → object, nhiều → mảng
    entity_ids = envelope["request"]["entity_ids"]
    if len(locations) != len(entity_ids):
        raise ValueError(f"{file_name}: API trả {len(locations)} địa điểm nhưng đã gửi {len(entity_ids)}")

    frames = []
    for entity_id, loc in zip(entity_ids, locations):              # ghép theo THỨ TỰ
        if loc.get("utc_offset_seconds", 0) != 0:
            raise ValueError(f"{file_name}/{entity_id}: không phải giờ UTC — kiểm tra tham số timezone")
        hourly = loc["hourly"]
        lengths = {k: len(v) for k, v in hourly.items()}
        if len(set(lengths.values())) != 1:
            raise ValueError(f"{file_name}/{entity_id}: các mảng hourly lệch độ dài {lengths}")

        df = pd.DataFrame(hourly)                                  # mảng song song → cột
        df.insert(0, "event_time", pd.to_datetime(df.pop("time"), utc=True))
        df.insert(0, "entity_id", entity_id)
        meta = CITIES[entity_id]
        df.insert(2, "entity_name", meta["name"])
        df.insert(3, "country", meta["country"])
        df.insert(4, "latitude", meta["latitude"])                 # toạ độ KHAI BÁO của thành phố
        df.insert(5, "longitude", meta["longitude"])
        df.insert(6, "elevation", loc.get("elevation"))            # độ cao ô lưới (m)
        df.insert(7, "grid_latitude", loc.get("latitude"))         # tâm ô lưới ERA5 — chỉ để tham khảo
        df.insert(8, "grid_longitude", loc.get("longitude"))
        df["source_file"] = file_name                              # truy ngược về file JSON gốc
        frames.append(df)
    return frames


def main() -> None:
    setup_console()
    manifest = RAW_DIR / "_manifest.json"
    if not manifest.exists():
        raise SystemExit(f"Chưa có {rel(manifest)} — hãy chạy collection.py trước.")
    # Chỉ đọc đúng các file của lần thu thập gần nhất (thư mục có thể còn file cũ ngoài cửa sổ)
    files = [RAW_DIR / name for name in read_json(manifest)["files"]]

    header("BƯỚC 2 — LÀM PHẲNG JSON → BẢNG")
    frames = []
    for path in files:
        envelope = json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
        frames += flatten_envelope(envelope, path.name)
    obs = pd.concat(frames, ignore_index=True).sort_values(KEYS).reset_index(drop=True)
    write_parquet(obs, FLAT_DIR / "observations.parquet")

    # ── In ra để quan sát ────────────────────────────────────────────────────
    print(f"  Đọc            : {len(files)} file JSON")
    print(f"  Kết quả        : {len(obs):,} dòng × {obs.shape[1]} cột")
    print(f"  Thành phố      : {obs['entity_id'].nunique()}")
    print(f"  Thời gian      : {obs['event_time'].min()} → {obs['event_time'].max()}")

    print("\n  Kiểu dữ liệu GỐC (chưa ép kiểu — đó là việc của bước làm sạch):")
    for dtype, cols in obs[list(VARIABLES)].dtypes.groupby(obs[list(VARIABLES)].dtypes).groups.items():
        print(f"    {str(dtype):10} : {len(cols):>2} cột  ({', '.join(list(cols)[:4])}{', ...' if len(cols) > 4 else ''})")
    print("    → weather_code đang là SỐ NGUYÊN, nhưng thực chất là biến PHÂN LOẠI.")

    print("\n  Số dòng mỗi thành phố:")
    counts = obs.groupby("entity_id").size()
    for entity_id, n in counts.items():
        print(f"    {entity_id:12} {n:>7,}")

    print("\n  Toạ độ khai báo vs tâm ô lưới ERA5 (API trả về tâm ô, KHÔNG phải điểm đã gửi):")
    grid = obs.groupby("entity_id")[["latitude", "grid_latitude", "longitude", "grid_longitude"]].first()
    for entity_id, r in grid.head(4).iterrows():
        print(f"    {entity_id:12} ({r.latitude:.4f}, {r.longitude:.4f}) → ô lưới ({r.grid_latitude:.4f}, {r.grid_longitude:.4f})")

    print("\n  5 dòng đầu (một số cột):")
    cols = ["entity_id", "event_time", "temperature_2m", "precipitation", "cloud_cover", "weather_code"]
    print(obs[cols].head().to_string(index=False))
    print(f"\n  Lưu tại        : {rel(FLAT_DIR / 'observations.parquet')}")


if __name__ == "__main__":
    main()

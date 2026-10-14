"""
BƯỚC 1 — THU THẬP
=================
Gọi Open-Meteo Historical Weather API, lưu NGUYÊN VĂN JSON trả về (nén gzip) vào test/data/1_raw/.

    Đầu vào : khoảng ngày [--start, --end) + danh sách thành phố
    Đầu ra  : 1_raw/<YYYY-MM>.json.gz   — mỗi tháng một file, dạng {"request": ..., "response": ...}
              1_raw/_manifest.json      — tóm tắt: các file, số "call" API đã tiêu

Quan sát được gì ở bước này:
  • JSON của Open-Meteo ở DẠNG CỘT: các mảng song song đánh chỉ số theo "time".
  • Gửi nhiều toạ độ trong 1 request → nhận về MẢNG, đúng thứ tự đã gửi. Response KHÔNG có id
    địa điểm, nên ta tự lưu "entity_ids" vào request để bước flatten ghép lại cho đúng.
  • Một "API call" của Open-Meteo được tính theo TRỌNG SỐ (số biến × số ngày × số địa điểm),
    không phải số HTTP request — nên phải giãn nhịp gọi theo trọng số.

Chạy:
    python test/collection.py                                         # mặc định: 3 năm, 12 thành phố
    python test/collection.py --cities hanoi,tokyo                    # chạy thử nhanh 2 thành phố
    python test/collection.py --start 2016-10-01 --end 2026-10-01     # 10 năm (nên chạy làm nhiều đợt)

Chạy lại là AN TOÀN: tháng nào đã có file thì bỏ qua (trừ khi --force), nên nếu bị chặn vì hết
hạn mức API thì chỉ cần chạy lại sau, phần đã tải không bị gọi lại.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import time
from datetime import date, datetime, timedelta, timezone

import requests

from config import (API_URL, CITIES, ERA5_LAG_DAYS, MODEL, RAW_DIR, VARIABLES, header, rel,
                    setup_console, write_json)

# Hạn mức miễn phí: 600 call/phút, 5.000/giờ, 10.000/ngày → giãn 0,12 giây cho mỗi call quy đổi
SECONDS_PER_WEIGHTED_CALL = 0.12


def weighted_calls(n_locations: int, n_variables: int, n_days: int) -> float:
    """Công thức quy đổi của Open-Meteo: > 10 biến hoặc > 14 ngày bị tính thành nhiều call."""
    return n_locations * max(1.0, n_variables / 10) * max(1.0, n_days / 14)


def month_chunks(start: date, end: date):
    """Chia [start, end) thành các đoạn theo tháng dương lịch → mỗi đoạn một file."""
    cursor = start
    while cursor < end:
        nxt = (cursor.replace(day=1) + timedelta(days=32)).replace(day=1)
        yield cursor, min(nxt, end)
        cursor = nxt


def fetch_month(cities: list[str], first: date, last: date, session: requests.Session) -> dict:
    """Một HTTP request cho tất cả thành phố trong một tháng. Trả về envelope {request, response}."""
    params = {
        "latitude": ",".join(str(CITIES[c]["latitude"]) for c in cities),
        "longitude": ",".join(str(CITIES[c]["longitude"]) for c in cities),
        "start_date": first.isoformat(),
        "end_date": last.isoformat(),           # Open-Meteo: end_date là NGÀY CUỐI, có tính
        "hourly": ",".join(VARIABLES),
        "models": MODEL,
        "timezone": "UTC",
    }
    for attempt in range(1, 6):
        resp = session.get(API_URL, params=params, timeout=120)
        if resp.status_code == 200:
            return {
                "request": {"url": API_URL, "params": params, "entity_ids": cities,
                            "fetched_at": datetime.now(timezone.utc).isoformat()},
                "response": resp.json(),
            }
        reason = resp.json().get("reason", resp.text[:200]) if resp.headers.get(
            "content-type", "").startswith("application/json") else resp.text[:200]
        if resp.status_code == 429 and "inute" in reason:          # vượt hạn mức theo PHÚT → chờ
            print(f"      429 hạn mức theo phút — chờ 65 giây (lần {attempt})")
            time.sleep(65)
            continue
        if resp.status_code == 429:                                 # theo GIỜ / NGÀY → dừng hẳn
            raise SystemExit(f"\nHết hạn mức API: {reason}\n"
                             "Các tháng đã tải vẫn được giữ — chạy lại lệnh sau ít giờ để tải tiếp.")
        if resp.status_code >= 500:
            time.sleep(5 * attempt)
            continue
        raise SystemExit(f"HTTP {resp.status_code}: {reason}")
    raise SystemExit("Gọi API thất bại sau 5 lần thử")


def main() -> None:
    setup_console()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start", default="2023-10-01", help="ngày đầu (bao gồm), mặc định 2023-10-01")
    parser.add_argument("--end", default="2026-10-01", help="ngày cuối (KHÔNG bao gồm), mặc định 2026-10-01")
    parser.add_argument("--cities", default=",".join(CITIES), help="danh sách id, ngăn bằng dấu phẩy")
    parser.add_argument("--force", action="store_true", help="tải lại cả các tháng đã có file")
    args = parser.parse_args()

    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    cities = [c.strip() for c in args.cities.split(",") if c.strip()]
    unknown = [c for c in cities if c not in CITIES]
    if unknown:
        raise SystemExit(f"Không biết thành phố: {unknown}. Có: {list(CITIES)}")
    newest = date.today() - timedelta(days=ERA5_LAG_DAYS)
    if end > newest:
        raise SystemExit(f"--end={end} quá mới: ERA5 chỉ có dữ liệu tới khoảng {newest} (trễ {ERA5_LAG_DAYS} ngày).")

    chunks = list(month_chunks(start, end))
    total_days = (end - start).days
    est = sum(weighted_calls(len(cities), len(VARIABLES), (b - a).days) for a, b in chunks)
    header("BƯỚC 1 — THU THẬP (Open-Meteo Archive API, models=era5)")
    print(f"  Khoảng ngày   : [{start}, {end})  = {total_days} ngày, {len(chunks)} tháng")
    print(f"  Thành phố     : {len(cities)} — {', '.join(cities)}")
    print(f"  Biến          : {len(VARIABLES)} biến theo giờ")
    print(f"  Chi phí ước   : ~{est:,.0f} call quy đổi ({est / 10000:.0%} hạn mức 10.000 call/ngày)")
    if est > 4500:
        print("  ⚠ Vượt ~5.000 call/giờ: lần chạy này có thể bị chặn giữa chừng — chạy lại sau là tải tiếp.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    files, spent, skipped = [], 0.0, 0
    for i, (first, stop) in enumerate(chunks, start=1):
        path = RAW_DIR / f"{first:%Y-%m}.json.gz"
        files.append(path.name)
        if path.exists() and not args.force:
            cached = json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))["request"]["entity_ids"]
            if cached == cities:                      # cùng tháng VÀ cùng danh sách thành phố → dùng lại
                skipped += 1
                continue
            print(f"  [{i:>3}/{len(chunks)}] {path.name}: file cũ có {len(cached)} thành phố, cần {len(cities)} → tải lại")
        last = stop - timedelta(days=1)
        t0 = time.monotonic()
        envelope = fetch_month(cities, first, last, session)
        path.write_bytes(gzip.compress(json.dumps(envelope, ensure_ascii=False).encode("utf-8")))
        cost = weighted_calls(len(cities), len(VARIABLES), (stop - first).days)
        spent += cost
        n_hours = len((envelope["response"][0] if isinstance(envelope["response"], list)
                       else envelope["response"])["hourly"]["time"])
        print(f"  [{i:>3}/{len(chunks)}] {first} → {last}  {n_hours:>4} giờ × {len(cities)} tp  "
              f"{path.stat().st_size / 1024:>6.0f} KB  {cost:>5.0f} call  ({time.monotonic() - t0:.1f}s)")
        time.sleep(cost * SECONDS_PER_WEIGHTED_CALL)     # giãn nhịp theo trọng số của chính request

    write_json({
        "source": API_URL, "model": MODEL, "start": str(start), "end": str(end),
        "cities": cities, "variables": list(VARIABLES), "files": files,
        "weighted_calls_this_run": round(spent), "generated_at": datetime.now(timezone.utc).isoformat(),
    }, RAW_DIR / "_manifest.json")

    print(f"\n  Đã tải mới   : {len(chunks) - skipped} file   (bỏ qua {skipped} file đã có)")
    print(f"  Call đã tiêu : {spent:,.0f}")
    print(f"  Lưu tại      : {rel(RAW_DIR)}/")
    print("\n  Xem thử 1 file:  python -c \"import gzip,json; e=json.load(gzip.open('test/data/1_raw/"
          f"{files[0]}')); print(json.dumps(e, ensure_ascii=False)[:800])\"")


if __name__ == "__main__":
    main()

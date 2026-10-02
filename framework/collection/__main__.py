"""
CLI của data collection — chạy pipeline ngoài Airflow (thử nghiệm, backfill, chọn trạm).

    python -m framework.collection list
    python -m framework.collection window --problem wx_rain_clf
    python -m framework.collection run --problem wx_rain_clf                         # như 1 run theo lịch, lúc này
    python -m framework.collection run --problem wx_rain_clf --start 2025-01-01 --end 2026-09-01   # backfill
    python -m framework.collection run --problem wx_rain_clf --base-uri ./_collection_out          # ghi ra local
    python -m framework.collection discover-openaq --iso IN TH US --max-stations 10

--start/--end là khoảng ĐIỂM NEO [start, end) theo UTC; nhãn cần dữ liệu đến end + horizon.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from .config import discover_problem_ids, load_config, problems_dir
from .pipeline import get_storage, run_window, split_range
from .window import explicit_window, parse_time, scheduled_window

logger = logging.getLogger("framework.collection")


def _cmd_list(args) -> int:
    for problem_id in discover_problem_ids():
        cfg = load_config(problem_id)
        print(f"{cfg.problem_id:14s} {cfg.task_type:10s} {cfg.source_type:10s} "
              f"schedule='{cfg.schedule}' entities={len(cfg.entities)} "
              f"label={cfg.label.agg}({cfg.label.target}) H={cfg.horizon} M={cfg.maturity_lag}")
    return 0


def _cmd_window(args) -> int:
    cfg = load_config(args.problem)
    at = parse_time(args.at) if args.at else datetime.now(timezone.utc)
    print(json.dumps(scheduled_window(cfg, at).to_dict(), indent=2))
    return 0


def _cmd_run(args) -> int:
    cfg = load_config(args.problem)
    storage = get_storage(cfg, args.base_uri)

    if bool(args.start) != bool(args.end):
        raise SystemExit("--start và --end phải đi cùng nhau")
    if args.start:
        start, end = parse_time(args.start), parse_time(args.end)
        windows = [explicit_window(cfg, s, e)
                   for s, e in split_range(start, end, timedelta(days=args.chunk_days))]
    else:
        at = parse_time(args.at) if args.at else datetime.now(timezone.utc)
        windows = [scheduled_window(cfg, at)]

    logger.info("%s → %s | %d cửa sổ", cfg.problem_id, storage.base_uri, len(windows))
    total = 0
    for index, window in enumerate(windows, start=1):
        summary = run_window(cfg, window, storage)
        labels = summary["stages"]["build_labels"]
        total += labels["labeled_rows"]
        print(f"[{index}/{len(windows)}] {window.key}: quan sát={summary['stages']['flatten']['rows']} "
              f"có nhãn={labels['labeled_rows']} loại={labels['dropped_no_label']} "
              f"label_mean={labels.get('label_mean')}")
        for warning in summary["warnings"]:
            print(f"    ! {warning}")
    print(f"Tổng số dòng training: {total} → {storage.uri('labeled')}")
    return 0


def _cmd_discover_openaq(args) -> int:
    from .discovery import discover_stations

    stations = discover_stations(
        iso_codes=args.iso, parameters=args.parameters, required=args.required,
        max_stations=args.max_stations, per_country=args.per_country,
        min_parameters=args.min_parameters, max_age_hours=args.max_age_hours,
        min_history_days=args.min_history_days)
    if not stations:
        print("Không tìm thấy trạm nào thoả tiêu chí — nới --min-parameters / --max-age-hours hoặc đổi --iso")
        return 1

    out = Path(args.out)
    header = ("# Sinh bởi `python -m framework.collection discover-openaq` lúc "
              f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC — iso={args.iso}\n")
    out.write_text(header + yaml.safe_dump({"entities": stations}, allow_unicode=True, sort_keys=False),
                   encoding="utf-8")
    for station in stations:
        print(f"{station['id']:>8s}  {station['country']}  {station['name'][:40]:40s} "
              f"{[s['parameter'] for s in station['sensors']]}")
    print(f"Đã ghi {len(stations)} trạm → {out}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m framework.collection", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="liệt kê các bài toán có collection.yaml").set_defaults(func=_cmd_list)

    p_window = sub.add_parser("window", help="xem cửa sổ mà một run theo lịch sẽ thu thập")
    p_window.add_argument("--problem", required=True)
    p_window.add_argument("--at", help="thời điểm run (ISO, UTC); mặc định: bây giờ")
    p_window.set_defaults(func=_cmd_window)

    p_run = sub.add_parser("run", help="chạy extract → flatten → gán nhãn")
    p_run.add_argument("--problem", required=True)
    p_run.add_argument("--start", help="điểm neo đầu (bao gồm), ví dụ 2026-01-01")
    p_run.add_argument("--end", help="điểm neo cuối (không bao gồm)")
    p_run.add_argument("--at", help="giả lập một run theo lịch tại thời điểm này")
    p_run.add_argument("--chunk-days", type=int, default=30, help="backfill: số ngày điểm neo mỗi đoạn")
    p_run.add_argument("--base-uri", help="nơi ghi (mặc định s3://$S3_BUCKET_NAME/$S3_PREFIX_COLLECTION)")
    p_run.set_defaults(func=_cmd_run)

    p_disc = sub.add_parser("discover-openaq", help="chọn trạm OpenAQ và ghi file entities")
    p_disc.add_argument("--iso", nargs="+", required=True, help="mã quốc gia ISO-2, ví dụ IN TH US")
    p_disc.add_argument("--parameters", nargs="+",
                        default=["pm25", "pm10", "no2", "o3", "so2", "co", "temperature", "relativehumidity"])
    p_disc.add_argument("--required", default="pm25", help="thông số bắt buộc phải có (cột tính nhãn)")
    p_disc.add_argument("--max-stations", type=int, default=10)
    p_disc.add_argument("--per-country", type=int, help="giới hạn số trạm mỗi quốc gia")
    p_disc.add_argument("--min-parameters", type=int, default=4)
    p_disc.add_argument("--max-age-hours", type=int, default=48)
    p_disc.add_argument("--min-history-days", type=int, default=365)
    p_disc.add_argument("--out", default=str(problems_dir() / "_entities" / "openaq_stations.yaml"))
    p_disc.set_defaults(func=_cmd_discover_openaq)

    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):        # console Windows (cp1252) không in được tiếng Việt
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

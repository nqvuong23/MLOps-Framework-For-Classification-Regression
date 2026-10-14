"""
BƯỚC 5 — VALIDATION (cổng kiểm soát)
====================================
Trả lời hai câu hỏi trước khi cho dữ liệu đi tiếp:
  (1) Bước làm sạch đã CHẠY XONG chưa?  (2) Có bản ghi nào LỌT LƯỚI, chưa được làm sạch không?
và kiểm tra luôn chất lượng nhãn. Không sửa dữ liệu — chỉ kiểm tra và ra quyết định ĐẠT / CHẶN.

    Nhóm A — làm sạch đã xong, không sót dòng
      V1  Bảo toàn      : mỗi dòng đầu vào nằm ở ĐÚNG MỘT trong hai bảng (sạch / cách ly), không mất, không thêm
      V2  Luỹ đẳng      : chạy lại clean() lên bảng sạch → KHÔNG được sửa hay loại thêm dòng nào
      V3  Dấu vết       : mọi dòng sạch có rules_applied = 63 (đã đi qua đủ 6 quy tắc) và cùng một run_id
      V4  Lý do cách ly : mọi dòng cách ly có reject_reason hợp lệ
      V5  Tỉ lệ cách ly : ≤ 1% (ERA5 vốn sạch; cao hơn nghĩa là nguồn đã đổi)          [cảnh báo]
    Nhóm B — chất lượng bảng sạch
      V6  Nguồn nhãn    : weather_code suy lại được từ precipitation + snowfall + cloud_cover ≥ 99%
      V7  Schema        : đủ cột, đúng kiểu (số đo float32, weather_code category, thời gian UTC)
      V8  Không rỗng    : 0 ô rỗng ở các cột bắt buộc
      V9  Khoá duy nhất : 0 cặp (entity_id, event_time) trùng
      V10 Lưới giờ      : mọi mốc giờ bị thiếu trong bảng sạch đều có mặt trong bảng cách ly
      V11 Cân bằng      : các thành phố có số dòng chênh nhau ≤ 1%                     [cảnh báo]
    Nhóm C — nhãn
      V12 Đúng 24 giờ   : label_time − event_time = 24h ở mọi dòng
      V13 Không rò rỉ   : 1.000 dòng ngẫu nhiên — label_raw khớp weather_code của dòng t + 24h trong bảng sạch
      V14 Ánh xạ        : label = gộp_nhóm(label_raw) ở mọi dòng
      V15 Phân bố nhãn  : mỗi lớp lệch ≤ 10 điểm % so với phân bố 5 năm đã đo           [cảnh báo]

    Đầu vào : 2_flat/, 3_clean/, 4_labeled/
    Đầu ra  : 5_validation/report.json — mã thoát 1 nếu có kiểm tra CHẶN bị trượt

Chạy:
    python test/validation.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from cleaning import ALL_RULES, REASON_PREFIXES, clean
from config import (CLASSES, CLEAN_DIR, EXPECTED_CLASS_SHARE, FLAT_DIR, HORIZON_HOURS, KEYS, LABEL_DIR,
                    LABEL_SOURCE, MEASURES, VALID_DIR, VARIABLES, WMO_CATEGORIES, derive_weather_code,
                    header, read_json, read_parquet, rel, setup_console, to_class, wmo_to_int, write_json)

RESULTS: list[dict] = []


def check(code: str, name: str, passed: bool, detail: str, blocking: bool = True) -> None:
    status = "ĐẠT" if passed else ("CHẶN" if blocking else "CẢNH BÁO")
    RESULTS.append({"id": code, "kiem_tra": name, "ket_qua": status, "chi_tiet": detail})


def key_set(df: pd.DataFrame) -> pd.MultiIndex:
    return pd.MultiIndex.from_frame(df[KEYS].assign(event_time=pd.to_datetime(df["event_time"], utc=True)))


def group_a(source: pd.DataFrame, cleaned: pd.DataFrame, quarantine: pd.DataFrame, report: dict) -> None:
    # V1 — bảo toàn số dòng và khoá
    q_input = quarantine[quarantine["_origin"] == "input"]
    n_src, n_out = len(source), len(cleaned) + len(q_input)
    src_keys = key_set(source.dropna(subset=KEYS)).unique()
    out_keys = key_set(cleaned).append(key_set(q_input)).unique()
    lost, invented = src_keys.difference(out_keys), out_keys.difference(src_keys)
    q_not_dup = q_input[~q_input["reject_reason"].str.startswith("R2_trung_khoa")]
    both = key_set(cleaned).intersection(key_set(q_not_dup))
    check("V1", "Bảo toàn dòng", n_src == n_out and not len(lost) and not len(invented) and not len(both),
          f"đầu vào {n_src:,} = sạch {len(cleaned):,} + cách ly {len(q_input):,} ({'đúng' if n_src == n_out else 'SAI'}); "
          f"khoá bị mất {len(lost)}, khoá tự sinh {len(invented)}, khoá nằm ở cả 2 bảng {len(both)}")

    # V2 — luỹ đẳng: làm sạch lần hai không được thay đổi gì
    cleaned2, quarantine2, _ = clean(cleaned, run_id="v2-recheck")
    rejected_again = int((quarantine2["_origin"] == "input").sum())
    refixed = int((cleaned2["fixed_by"] > 0).sum())
    same_rows = len(cleaned2) == len(cleaned)
    values_same = same_rows and all(
        np.array_equal(cleaned2[c].to_numpy(), cleaned[c].to_numpy(), equal_nan=True) for c in MEASURES
    ) and cleaned2[LABEL_SOURCE].astype(str).equals(cleaned[LABEL_SOURCE].astype(str))
    check("V2", "Luỹ đẳng (chạy lại không đổi)", same_rows and rejected_again == 0 and refixed == 0 and values_same,
          f"lần 2: {refixed} dòng bị sửa thêm, {rejected_again} dòng bị loại thêm, "
          f"giá trị {'giữ nguyên' if values_same else 'BỊ THAY ĐỔI'}")

    # V3 — dấu vết xử lý
    bad_trace = int((cleaned["rules_applied"] != ALL_RULES).sum())
    run_ids = cleaned["cleaning_run_id"].dropna().unique()
    check("V3", "Dấu vết đủ 6 quy tắc", bad_trace == 0 and len(run_ids) == 1,
          f"{bad_trace} dòng thiếu quy tắc; run_id: {list(run_ids)[:2]}")

    # V4 — lý do cách ly hợp lệ
    prefix = quarantine["reject_reason"].fillna("").str.split(":").str[0]
    bad_reason = int((~prefix.isin(REASON_PREFIXES)).sum())
    check("V4", "Lý do cách ly hợp lệ", bad_reason == 0,
          f"{bad_reason} dòng không có lý do hợp lệ; phân bố: {prefix.value_counts().to_dict()}")

    # V5 — tỉ lệ cách ly
    rate = len(q_input) / max(1, n_src)
    check("V5", "Tỉ lệ cách ly ≤ 1%", rate <= 0.01, f"{rate:.4%} ({len(q_input):,} dòng)", blocking=False)


def group_b(cleaned: pd.DataFrame, quarantine: pd.DataFrame) -> None:
    # V6 — nguồn nhãn khớp công thức suy lại
    derived = derive_weather_code(cleaned["precipitation"], cleaned["snowfall"], cleaned["cloud_cover"])
    actual = wmo_to_int(cleaned[LABEL_SOURCE]).to_numpy()
    match = float(np.mean(derived == actual))
    check("V6", "weather_code suy lại được ≥ 99%", match >= 0.99,
          f"khớp {match:.4%} — nếu tụt thì nguồn đã đổi cách sinh mã")

    # V7 — schema và kiểu
    problems = [c for c in VARIABLES if c not in cleaned.columns]
    problems += [f"{c}:{cleaned[c].dtype}" for c in MEASURES if c in cleaned.columns and cleaned[c].dtype != "float32"]
    if not isinstance(cleaned[LABEL_SOURCE].dtype, pd.CategoricalDtype) or \
            list(cleaned[LABEL_SOURCE].cat.categories) != WMO_CATEGORIES:
        problems.append(f"{LABEL_SOURCE}:{cleaned[LABEL_SOURCE].dtype}")
    if str(getattr(cleaned["event_time"].dt, "tz", None)) != "UTC":
        problems.append("event_time không phải UTC")
    check("V7", "Schema & kiểu dữ liệu", not problems, "đủ cột, đúng kiểu" if not problems else f"sai: {problems}")

    # V8 — không rỗng
    nulls = cleaned[KEYS + MEASURES + [LABEL_SOURCE]].isna().sum()
    check("V8", "Không ô rỗng ở cột bắt buộc", int(nulls.sum()) == 0,
          f"{int(nulls.sum())} ô rỗng" + (f": {nulls[nulls > 0].to_dict()}" if nulls.sum() else ""))

    # V9 — khoá duy nhất
    dup = int(cleaned.duplicated(KEYS).sum())
    check("V9", "Khoá duy nhất", dup == 0, f"{dup} khoá trùng")

    # V10 — mọi mốc giờ thiếu trong bảng sạch đều được giải thích bởi bảng cách ly
    unexplained = 0
    q_keys = key_set(quarantine)
    for entity_id, g in cleaned.groupby("entity_id"):
        grid = pd.date_range(g["event_time"].min(), g["event_time"].max(), freq="h", tz="UTC")
        missing = grid.difference(pd.DatetimeIndex(g["event_time"]))
        if len(missing):
            miss_keys = pd.MultiIndex.from_arrays([[entity_id] * len(missing), missing], names=KEYS)
            unexplained += len(miss_keys.difference(q_keys))
    check("V10", "Lưới giờ liên tục (lỗ hổng có lý do)", unexplained == 0,
          f"{unexplained} mốc giờ biến mất mà không nằm trong bảng cách ly")

    # V11 — cân bằng giữa các thành phố
    counts = cleaned.groupby("entity_id").size()
    spread = (counts.max() - counts.min()) / counts.max()
    check("V11", "Số dòng các thành phố chênh ≤ 1%", spread <= 0.01,
          f"ít nhất {counts.idxmin()} {counts.min():,} — nhiều nhất {counts.idxmax()} {counts.max():,} "
          f"(chênh {spread:.2%})", blocking=False)


def group_c(cleaned: pd.DataFrame, labeled: pd.DataFrame) -> None:
    # V12 — nhãn đúng 24 giờ sau
    wrong = int(((labeled["label_time"] - labeled["event_time"]) != pd.Timedelta(hours=HORIZON_HOURS)).sum())
    check("V12", "label_time = event_time + 24h", wrong == 0, f"{wrong} dòng lệch")

    # V13 — tra ngược độc lập: nhãn có thật sự lấy từ dòng t + 24h không
    sample = labeled.sample(min(1000, len(labeled)), random_state=0)
    lookup = cleaned.set_index(KEYS)[LABEL_SOURCE]
    keys = pd.MultiIndex.from_arrays([sample["entity_id"], sample["event_time"] + pd.Timedelta(hours=HORIZON_HOURS)])
    truth = wmo_to_int(lookup.reindex(keys)).to_numpy()
    ok = int(np.sum(truth == sample["label_raw"].to_numpy()))
    check("V13", "Không rò rỉ / lệch mốc nhãn", ok == len(sample),
          f"{ok}/{len(sample)} dòng mẫu khớp weather_code thật tại t + 24h")

    # V14 — ánh xạ gộp nhóm đúng
    wrong = int((to_class(labeled["label_raw"]).astype(str).to_numpy() != labeled["label"].astype(str).to_numpy()).sum())
    check("V14", "label = gộp_nhóm(label_raw)", wrong == 0, f"{wrong} dòng sai ánh xạ")

    # V15 — phân bố nhãn
    share = labeled["label"].value_counts(normalize=True).reindex(CLASSES).fillna(0)
    worst = max(CLASSES, key=lambda c: abs(share[c] - EXPECTED_CLASS_SHARE[c]))
    gap = abs(share[worst] - EXPECTED_CLASS_SHARE[worst])
    check("V15", "Phân bố nhãn lệch ≤ 10 điểm %", gap <= 0.10,
          " · ".join(f"{c} {share[c]:.1%}" for c in CLASSES) + f"  (lệch nhiều nhất: {worst} {gap * 100:.1f} điểm)",
          blocking=False)


def main() -> None:
    setup_console()
    report = read_json(CLEAN_DIR / "report.json")
    injected = report.get("injected_errors")
    source = read_parquet(CLEAN_DIR / "injected_input.parquet" if injected else FLAT_DIR / "observations.parquet")
    cleaned = read_parquet(CLEAN_DIR / "cleaned.parquet")
    quarantine = read_parquet(CLEAN_DIR / "quarantine.parquet")
    labeled = read_parquet(LABEL_DIR / "labeled.parquet")

    header("BƯỚC 5 — VALIDATION")
    if injected:
        print("  ⚠ Bảng sạch được tạo ở CHẾ ĐỘ CẤY LỖI — đối chiếu với bản đầu vào đã cấy lỗi.\n")
    group_a(source, cleaned, quarantine, report)
    group_b(cleaned, quarantine)
    group_c(cleaned, labeled)

    groups = {"V1": "A. Làm sạch đã xong, không sót dòng", "V6": "B. Chất lượng bảng sạch", "V12": "C. Nhãn"}
    for r in RESULTS:
        if r["id"] in groups:
            print(f"\n  {groups[r['id']]}")
        icon = {"ĐẠT": "✓", "CHẶN": "✗", "CẢNH BÁO": "!"}[r["ket_qua"]]
        print(f"   {icon} {r['id']:4} {r['kiem_tra']:36} {r['ket_qua']:9} {r['chi_tiet']}")

    blocked = [r["id"] for r in RESULTS if r["ket_qua"] == "CHẶN"]
    warned = [r["id"] for r in RESULTS if r["ket_qua"] == "CẢNH BÁO"]
    verdict = "CHẶN — không được đi tiếp" if blocked else "ĐẠT — cho phép sang feature engineering"
    write_json({"verdict": verdict, "blocked": blocked, "warnings": warned, "checks": RESULTS,
                "injected_errors": injected, "generated_at": datetime.now(timezone.utc).isoformat()},
               VALID_DIR / "report.json")
    print(f"\n  KẾT LUẬN: {verdict}" + (f"   (trượt: {blocked})" if blocked else "")
          + (f"   (cảnh báo: {warned})" if warned else ""))
    print(f"  Lưu tại : {rel(VALID_DIR / 'report.json')}")
    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()

"""
BƯỚC 3 — LÀM SẠCH
=================
Áp 6 quy tắc theo thứ tự, mỗi quy tắc chọn theo "semantic_type" của cột (khai trong config.py),
không viết riêng cho từng tên cột:

    R1  Ép kiểu          số đo → float32; weather_code → category (mã WMO hợp lệ); thời gian → UTC
    R2  Khoá             (entity_id, event_time) không null, không trùng
    R3  Lưới giờ         mỗi thành phố phải đủ mọi mốc giờ liên tục; mốc thiếu → thêm dòng rỗng
    R4  Khoảng vật lý    giá trị ngoài khoảng của semantic_type → đặt rỗng
    R5  Điền khuyết      lỗ hổng ≤ 2 giờ liên tiếp → nội suy tuyến tính; lỗ dài hơn → để nguyên
    R6  Nhất quán        rain không được lớn hơn precipitation (rain là một phần của precipitation) → kẹp lại

    → dòng nào còn thiếu sau R5 thì đưa vào BẢNG CÁCH LY kèm lý do (fail-soft: không dừng pipeline)

THỨ TỰ QUAN TRỌNG: R6 phải chạy SAU R5. Bản đầu tiên của file này để kiểm tra nhất quán chạy TRƯỚC
nội suy — R5 nội suy rain và precipitation độc lập nên tạo ra vi phạm mới mà không ai kiểm tra lại.
validation.py bắt được lỗi đó nhờ kiểm tra luỹ đẳng (V2): chạy làm sạch lần hai vẫn còn sửa thêm dòng.

    Đầu vào : 2_flat/observations.parquet
    Đầu ra  : 3_clean/cleaned.parquet      dòng đạt, kèm cột dấu vết fixed_by / rules_applied
              3_clean/quarantine.parquet   dòng bị cách ly, kèm cột reject_reason
              3_clean/report.json          số đếm theo từng quy tắc

Ba nguyên tắc để bước sau CHỨNG MINH được việc làm sạch đã xong và không sót dòng nào:
  • Không dòng nào biến mất: mỗi dòng đầu vào kết thúc ở ĐÚNG MỘT trong hai bảng (kể cả bản trùng).
  • Mỗi dòng mang dấu vết: fixed_by = bitmask các quy tắc đã SỬA dòng đó; rules_applied = mọi quy tắc.
  • Luỹ đẳng: chạy clean() lần hai trên bảng sạch không được sửa thêm gì (validation.py kiểm tra).

Dữ liệu ERA5 rất sạch (đo 105.120 dòng: 0 thiếu, 0 ngoài khoảng), nên làm sạch dữ liệu thật thường
không sửa gì. Muốn thấy từng quy tắc hoạt động, dùng --inject-errors để CHỦ ĐỘNG cấy lỗi đã biết trước
vào một bản sao rồi xem quy tắc bắt được bao nhiêu (kỹ thuật "error injection", như bài JENGA).

Chạy:
    python test/cleaning.py                       # làm sạch dữ liệu thật
    python test/cleaning.py --inject-errors 200   # cấy lỗi để học — chạy lại không có cờ để có dữ liệu sạch
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from config import (CLEAN_DIR, FLAT_DIR, KEYS, LABEL_SOURCE, MEASURES, VALID_RANGES, VARIABLES,
                    header, read_parquet, rel, setup_console, wmo_category, write_json, write_parquet)

RULES = {"R1_ep_kieu": 1, "R2_khoa": 2, "R3_luoi_gio": 4,
         "R4_khoang_vat_ly": 8, "R5_dien_khuyet": 16, "R6_nhat_quan": 32}
ALL_RULES = sum(RULES.values())                     # = 63: dòng đã đi qua đủ 6 quy tắc
MAX_GAP_HOURS = 2                                   # chỉ nội suy lỗ hổng ngắn
RAIN_TOLERANCE_MM = 0.05
STATIC_COLS = ["entity_name", "country", "latitude", "longitude", "elevation", "grid_latitude", "grid_longitude"]
TRACE_COLS = ["_origin", "fixed_by", "rules_applied", "cleaning_run_id"]
REASON_PREFIXES = ["R2_khoa_null", "R2_trung_khoa", "R3_thieu_dong", "R5_con_thieu"]


def _fill_short_gaps(s: pd.Series, max_len: int):
    """Nội suy tuyến tính CHỈ các lỗ hổng dài ≤ max_len và có giá trị ở cả hai đầu."""
    isna = s.isna()
    if not isna.any():
        return s, pd.Series(False, index=s.index)
    run_id = (isna != isna.shift()).cumsum()                 # đánh số từng đoạn liên tiếp
    run_len = isna.groupby(run_id).transform("sum")          # độ dài đoạn rỗng chứa mỗi ô
    interp = s.interpolate(method="linear", limit_area="inside")
    fill = isna & (run_len <= max_len) & interp.notna()
    return s.where(~fill, interp), fill


def clean(obs: pd.DataFrame, run_id: str = "manual"):
    """Hàm thuần: nhận bảng quan sát → (bảng sạch, bảng cách ly, báo cáo). Không đọc/ghi file."""
    df = obs.drop(columns=[c for c in TRACE_COLS + ["reject_reason"] if c in obs.columns]).copy()
    report = {"n_input": len(df), "rules": {name: {} for name in RULES}}
    df["_origin"] = "input"                 # "input" = dòng có thật; "gap_fill" = dòng R3 thêm vào
    df["fixed_by"] = 0
    quarantined = []

    # ── R1: ép kiểu ──────────────────────────────────────────────────────────
    df["entity_id"] = df["entity_id"].astype("string")
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True, errors="coerce")
    for col in MEASURES:
        before = df[col].notna()
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")
        bad = before & df[col].isna()                        # có giá trị nhưng không phải số
        if bad.any():
            report["rules"]["R1_ep_kieu"][col] = int(bad.sum())
            df.loc[bad, "fixed_by"] |= RULES["R1_ep_kieu"]
    before = df[LABEL_SOURCE].notna()
    df[LABEL_SOURCE] = wmo_category(df[LABEL_SOURCE].to_numpy())
    bad = before & df[LABEL_SOURCE].isna()
    if bad.any():
        report["rules"]["R1_ep_kieu"][f"{LABEL_SOURCE} (mã WMO không hợp lệ)"] = int(bad.sum())
        df.loc[bad, "fixed_by"] |= RULES["R1_ep_kieu"]

    # ── R2: khoá ─────────────────────────────────────────────────────────────
    null_key = df["entity_id"].isna() | df["event_time"].isna()
    if null_key.any():
        quarantined.append(df[null_key].assign(reject_reason="R2_khoa_null"))
        report["rules"]["R2_khoa"]["khoá rỗng"] = int(null_key.sum())
    df = df[~null_key]
    dup = df.duplicated(KEYS, keep="last")                   # giữ bản cuối, bản trước vào cách ly
    if dup.any():
        quarantined.append(df[dup].assign(reject_reason="R2_trung_khoa"))
        report["rules"]["R2_khoa"]["dòng trùng khoá"] = int(dup.sum())
    df = df[~dup]

    # ── R3: lưới giờ liên tục cho từng thành phố ────────────────────────────
    parts, n_added = [], 0
    for entity_id, g in df.groupby("entity_id", sort=True):
        g = g.set_index("event_time").sort_index()
        grid = pd.date_range(g.index.min(), g.index.max(), freq="h", tz="UTC")
        missing = grid.difference(g.index)
        if len(missing):
            add = pd.DataFrame(index=missing)
            add["entity_id"] = entity_id
            for col in STATIC_COLS:
                add[col] = g[col].iloc[0]
            add["_origin"] = "gap_fill"
            add["fixed_by"] = RULES["R3_luoi_gio"]
            g = pd.concat([g, add]).sort_index()
            n_added += len(missing)
        parts.append(g.rename_axis("event_time").reset_index())
    df = pd.concat(parts, ignore_index=True)
    for col in MEASURES:                                     # concat có thể làm mất kiểu → ép lại
        df[col] = df[col].astype("float32")
    df[LABEL_SOURCE] = wmo_category(df[LABEL_SOURCE].to_numpy())
    df["fixed_by"] = df["fixed_by"].astype("int64")
    if n_added:
        report["rules"]["R3_luoi_gio"]["mốc giờ bị thiếu → thêm dòng rỗng"] = n_added

    # ── R4: khoảng vật lý theo semantic_type ────────────────────────────────
    for col in MEASURES:
        lo, hi = VALID_RANGES[VARIABLES[col]]
        out = df[col].notna() & ((df[col] < lo) | (df[col] > hi))
        if out.any():
            report["rules"]["R4_khoang_vat_ly"][f"{col} ∉ [{lo}, {hi}]"] = int(out.sum())
            df.loc[out, col] = np.nan
            df.loc[out, "fixed_by"] |= RULES["R4_khoang_vat_ly"]

    # ── R5: điền lỗ hổng ngắn (weather_code KHÔNG điền — là nguồn nhãn, không được bịa) ──
    df = df.sort_values(KEYS).reset_index(drop=True)
    for col in MEASURES:
        if not df[col].isna().any():
            continue
        filled_total = 0
        for _, idx in df.groupby("entity_id", sort=False).groups.items():
            new, mask = _fill_short_gaps(df.loc[idx, col], MAX_GAP_HOURS)
            if mask.any():
                df.loc[idx, col] = new.astype("float32")
                df.loc[mask[mask].index, "fixed_by"] |= RULES["R5_dien_khuyet"]
                # chỉ đếm ô của dòng THẬT: dòng rỗng do R3 thêm vẫn bị cách ly vì không có weather_code
                filled_total += int((mask & (df.loc[idx, "_origin"] == "input")).sum())
        if filled_total:
            report["rules"]["R5_dien_khuyet"][col] = filled_total

    # ── R6: nhất quán giữa các cột — chạy SAU điền khuyết, vì nội suy từng cột riêng rẽ có thể
    #        tạo vi phạm mới. Kẹp rain = precipitation (thay vì xoá) để phép sửa tự nó luỹ đẳng. ──
    bad = df["rain"].notna() & df["precipitation"].notna() & (df["rain"] > df["precipitation"] + RAIN_TOLERANCE_MM)
    if bad.any():
        report["rules"]["R6_nhat_quan"]["rain > precipitation → kẹp rain = precipitation"] = int(
            (bad & (df["_origin"] == "input")).sum())
        df.loc[bad, "rain"] = df.loc[bad, "precipitation"]
        df.loc[bad, "fixed_by"] |= RULES["R6_nhat_quan"]

    # ── Dòng còn thiếu → cách ly ────────────────────────────────────────────
    required = MEASURES + [LABEL_SOURCE]
    nulls = df[required].isna()
    bad_rows = nulls.any(axis=1)
    if bad_rows.any():
        sub = df[bad_rows].copy()
        sub["reject_reason"] = [
            "R3_thieu_dong" if origin == "gap_fill"
            else "R5_con_thieu:" + ",".join(np.array(required)[row].tolist()[:3])
            for origin, row in zip(sub["_origin"], nulls[bad_rows].to_numpy())
        ]
        quarantined.append(sub)

    cleaned = df[~bad_rows].copy()
    cleaned["rules_applied"] = ALL_RULES
    cleaned["cleaning_run_id"] = run_id
    quarantine = (pd.concat(quarantined, ignore_index=True) if quarantined
                  else df.head(0).assign(reject_reason=pd.Series(dtype="string")))
    quarantine[LABEL_SOURCE] = wmo_category(quarantine[LABEL_SOURCE].to_numpy())

    report.update({
        "n_cleaned": len(cleaned),
        "n_quarantine": len(quarantine),
        "n_quarantine_from_input": int((quarantine["_origin"] == "input").sum()),
        "n_quarantine_gap_rows": int((quarantine["_origin"] == "gap_fill").sum()),
        "n_cleaned_repaired": int((cleaned["fixed_by"] > 0).sum()),
        "quarantine_rate": round((quarantine["_origin"] == "input").sum() / max(1, report["n_input"]), 6),
        "quarantine_reasons": quarantine["reject_reason"].str.split(":").str[0].value_counts().to_dict(),
    })
    return cleaned.reset_index(drop=True), quarantine.reset_index(drop=True), report


def inject_errors(obs: pd.DataFrame, n: int, seed: int = 42):
    """
    Cấy lỗi ĐÃ BIẾT vào một bản sao để quan sát từng quy tắc. Mỗi loại lỗi rơi vào các dòng khác nhau
    để số đếm dễ đối chiếu. CHỈ dùng để học — không đưa dữ liệu này vào training thật.
    """
    rng = np.random.default_rng(seed)
    df = obs.copy()
    k = max(1, n // 5)
    pool = rng.permutation(np.arange(30, len(df) - 30))      # tránh mép để lỗ hổng nằm "bên trong"
    cursor = [0]

    def take(m: int) -> np.ndarray:
        """Lấy m vị trí dòng CHƯA dùng → mỗi loại lỗi rơi vào dòng riêng."""
        rows = pool[cursor[0]:cursor[0] + m]
        cursor[0] += m
        return rows

    injected = {}

    rows = take(n)                                            # 1. ô rỗng lẻ (sửa được bằng nội suy)
    cols = rng.choice(MEASURES, size=len(rows))
    for r, c in zip(rows, cols):
        df.iat[r, df.columns.get_loc(c)] = np.nan
    injected["o_rong_le (R5 nội suy được)"] = len(rows)

    rows = take(n)                                            # 2. giá trị ngoài khoảng vật lý
    bad_values = {"relative_humidity_2m": 250.0, "temperature_2m": 999.0, "precipitation": -3.0}
    for i, r in enumerate(rows):
        c = list(bad_values)[i % 3]
        df.iat[r, df.columns.get_loc(c)] = bad_values[c]
    injected["ngoai_khoang (R4)"] = len(rows)

    rows = take(n)                                            # 3. chữ lẫn trong cột số
    df["pressure_msl"] = df["pressure_msl"].astype(object)
    for r in rows:
        df.iat[r, df.columns.get_loc("pressure_msl")] = "N/A"
    injected["chu_trong_cot_so (R1)"] = len(rows)

    rows = take(k)                                            # 4. mã WMO không tồn tại
    df[LABEL_SOURCE] = df[LABEL_SOURCE].astype(object)
    for r in rows:
        df.iat[r, df.columns.get_loc(LABEL_SOURCE)] = 999
    injected["ma_WMO_sai (R1 → cách ly, không bịa nhãn)"] = len(rows)

    rows = take(k)                                            # 5. rain > precipitation
    for r in rows:
        df.iat[r, df.columns.get_loc("rain")] = float(df.iat[r, df.columns.get_loc("precipitation")] or 0) + 5
    injected["rain_lon_hon_precipitation (R6)"] = len(rows)

    runs = max(1, n // 50)                                    # 6. lỗ hổng dài 5 giờ (không nội suy được)
    starts = take(runs)
    for s in starts:
        df.loc[df.index[s:s + 5], "cloud_cover"] = np.nan
    injected["lo_hong_5_gio (R5 bỏ qua → cách ly)"] = int(runs * 5)

    dup_rows = take(k)                                        # 7. dòng trùng khoá
    drop_rows = take(k)                                       # 8. xoá dòng → mất mốc giờ
    df = pd.concat([df, df.iloc[dup_rows]], ignore_index=True)
    df = df.drop(index=drop_rows).reset_index(drop=True)
    injected["dong_trung (R2)"] = len(dup_rows)
    injected["dong_bi_xoa (R3)"] = len(drop_rows)
    return df, injected


def main() -> None:
    setup_console()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inject-errors", type=int, default=0, metavar="N",
                        help="cấy N lỗi mỗi loại vào bản sao để quan sát (chỉ để học)")
    args = parser.parse_args()

    obs = read_parquet(FLAT_DIR / "observations.parquet")
    header("BƯỚC 3 — LÀM SẠCH")
    injected = None
    if args.inject_errors:
        obs, injected = inject_errors(obs, args.inject_errors)
        print("  ⚠ CHẾ ĐỘ HỌC: đã cấy lỗi vào bản sao dữ liệu:")
        for name, count in injected.items():
            print(f"      {name:44} {count:>6}")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    cleaned, quarantine, report = clean(obs, run_id)
    report["run_id"] = run_id
    report["injected_errors"] = injected

    write_parquet(cleaned, CLEAN_DIR / "cleaned.parquet")
    write_parquet(quarantine, CLEAN_DIR / "quarantine.parquet")
    write_json(report, CLEAN_DIR / "report.json")
    injected_path = CLEAN_DIR / "injected_input.parquet"
    if injected:      # lưu đúng bản đầu vào đã cấy lỗi để validation đối chiếu bảo toàn số dòng
        obs.assign(pressure_msl=obs["pressure_msl"].astype(str),
                   weather_code=obs["weather_code"].astype(str)).pipe(write_parquet, injected_path)
    elif injected_path.exists():
        injected_path.unlink()

    print(f"\n  {'Quy tắc':20} {'Chi tiết':52} {'Số ô/dòng':>9}")
    print(f"  {'─' * 20} {'─' * 52} {'─' * 9}")
    for rule, details in report["rules"].items():
        if not details:
            print(f"  {rule:20} {'(không phát hiện gì)':52} {0:>9}")
        for i, (what, count) in enumerate(details.items()):
            print(f"  {rule if i == 0 else '':20} {what[:52]:52} {count:>9,}")

    print(f"\n  Đầu vào                     : {report['n_input']:>9,} dòng")
    print(f"  → Bảng sạch                 : {report['n_cleaned']:>9,} dòng  (trong đó {report['n_cleaned_repaired']:,} dòng đã được sửa)")
    print(f"  → Bảng cách ly (dòng thật)  : {report['n_quarantine_from_input']:>9,} dòng  ({report['quarantine_rate']:.4%})")
    print(f"  → Bảng cách ly (mốc thiếu)  : {report['n_quarantine_gap_rows']:>9,} dòng  (dòng rỗng do R3 thêm, không có thật)")
    print(f"  Đẳng thức bảo toàn          : {report['n_input']:,} = {report['n_cleaned']:,} + "
          f"{report['n_quarantine_from_input']:,}  → "
          f"{'ĐÚNG' if report['n_input'] == report['n_cleaned'] + report['n_quarantine_from_input'] else 'SAI'}")
    if report["quarantine_reasons"]:
        print(f"  Lý do cách ly               : {report['quarantine_reasons']}")

    print(f"\n  Kiểu dữ liệu sau làm sạch: weather_code = {cleaned[LABEL_SOURCE].dtype} "
          f"({len(cleaned[LABEL_SOURCE].cat.categories)} mã WMO hợp lệ), số đo = {cleaned['temperature_2m'].dtype}")
    repaired = cleaned[cleaned["fixed_by"] > 0]
    if len(repaired):
        print("\n  Vài dòng ĐÃ ĐƯỢC SỬA (fixed_by là bitmask: 1=R1 2=R2 4=R3 8=R4 16=R5 32=R6):")
        print(repaired[["entity_id", "event_time", "fixed_by", "relative_humidity_2m", "temperature_2m",
                        "pressure_msl", "rain"]].head(6).to_string(index=False))
    if len(quarantine):
        print("\n  Vài dòng BỊ CÁCH LY:")
        print(quarantine[["entity_id", "event_time", "_origin", "reject_reason"]].head(6).to_string(index=False))
    print(f"\n  Lưu tại: {rel(CLEAN_DIR)}/  (cleaned.parquet, quarantine.parquet, report.json)")


if __name__ == "__main__":
    main()

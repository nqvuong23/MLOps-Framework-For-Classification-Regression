"""
BƯỚC 4 — GÁN NHÃN
=================
Nhãn của WX-C1 ĐÃ CÓ SẴN trong dữ liệu (weather_code do API trả về) — không phải gán tay.
Việc của bước này chỉ là DỊCH THỜI GIAN và GỘP NHÓM:

    label_raw = weather_code tại (t + 24h)        ← lấy từ TƯƠNG LAI, đúng 24 giờ sau điểm neo t
    label     = gộp label_raw thành 4 lớp         ← bảng LABEL_MAPPING trong config.py

    Dòng tại t                                   Dòng tại t + 24h
    ┌──────────────────────────────┐             ┌──────────────────────┐
    │ feature: mọi quan sát tại t  │  ─────────► │ weather_code = 61    │ → label_raw = 61 → label = "3_mua"
    └──────────────────────────────┘             └──────────────────────┘

    Đầu vào : 3_clean/cleaned.parquet
    Đầu ra  : 4_labeled/labeled.parquet   — mọi cột của bảng sạch + label_time, label_raw, label

Ghép theo MỐC THỜI GIAN CHÍNH XÁC (merge trên event_time + 24h), KHÔNG dùng shift(-24) theo số dòng:
nếu giữa chừng có mốc bị cách ly thì shift theo dòng sẽ lấy nhầm giờ — một lỗi rò rỉ/lệch nhãn rất khó thấy.

Điểm neo không xác định được nhãn (mốc t + 24h nằm ngoài dữ liệu hoặc bị cách ly) bị LOẠI —
không bao giờ ghi nhãn tạm hay rỗng.

Chạy:
    python test/labeling.py
"""
from __future__ import annotations

import pandas as pd

from config import (CLASSES, CLEAN_DIR, CODES_SEEN_IN_ERA5, HORIZON_HOURS, KEYS, LABEL_DIR, LABEL_SOURCE,
                    header, read_parquet, rel, setup_console, to_class, wmo_to_int, write_parquet)


def build_labels(cleaned: pd.DataFrame):
    """Hàm thuần: bảng sạch → (bảng có nhãn, thống kê)."""
    df = cleaned.copy()
    df["label_time"] = df["event_time"] + pd.Timedelta(hours=HORIZON_HOURS)

    future = cleaned[KEYS + [LABEL_SOURCE]].rename(
        columns={"event_time": "label_time", LABEL_SOURCE: "label_raw"})
    df = df.merge(future, on=["entity_id", "label_time"], how="left")      # ghép đúng mốc t + 24h

    last_time = cleaned.groupby("entity_id")["event_time"].max().rename("last_time")
    df = df.merge(last_time, left_on="entity_id", right_index=True)
    no_label = df["label_raw"].isna()
    beyond = no_label & (df["label_time"] > df["last_time"])               # t+24h vượt quá dữ liệu đã thu
    stats = {
        "n_anchor": len(df),
        "dropped_beyond_window": int(beyond.sum()),
        "dropped_future_quarantined": int((no_label & ~beyond).sum()),     # t+24h có nhưng đã bị cách ly
    }

    df = df[~no_label].drop(columns="last_time")
    df["label_raw"] = wmo_to_int(df["label_raw"]).astype("int16")         # giữ mã gốc để kiểm tra
    df["label"] = to_class(df["label_raw"]).to_numpy()
    if df["label"].isna().any():                                          # mã chưa khai trong mapping
        raise ValueError(f"Có mã WMO chưa có trong LABEL_MAPPING: {sorted(df.loc[df['label'].isna(), 'label_raw'].unique())}")
    stats["n_labeled"] = len(df)
    stats["unexpected_codes"] = sorted(set(df["label_raw"].unique()) - set(CODES_SEEN_IN_ERA5))
    return df.reset_index(drop=True), stats


def baselines(df: pd.DataFrame) -> pd.DataFrame:
    """
    Hai mốc mà model PHẢI vượt (tính trên toàn bộ dữ liệu có nhãn, chỉ để tham khảo):
      • persistence : đoán nhóm của 24h tới = nhóm đang quan sát tại t
      • lớp đông nhất: luôn đoán lớp xuất hiện nhiều nhất của thành phố đó
    """
    now = to_class(df[LABEL_SOURCE])
    rows = []
    for entity_id, idx in df.groupby("entity_id").groups.items():
        label = df.loc[idx, "label"]
        rows.append({"entity_id": entity_id,
                     "persistence": (now.loc[idx].to_numpy() == label.to_numpy()).mean(),
                     "lop_dong_nhat": label.value_counts(normalize=True).iloc[0],
                     "lop": label.value_counts().index[0]})
    out = pd.DataFrame(rows)
    total = {"entity_id": "GỘP", "persistence": (now.to_numpy() == df["label"].to_numpy()).mean(),
             "lop_dong_nhat": df["label"].value_counts(normalize=True).iloc[0],
             "lop": df["label"].value_counts().index[0]}
    return pd.concat([out, pd.DataFrame([total])], ignore_index=True)


def main() -> None:
    setup_console()
    cleaned = read_parquet(CLEAN_DIR / "cleaned.parquet")
    header("BƯỚC 4 — GÁN NHÃN (weather_code tại t + 24h → 4 lớp)")
    labeled, stats = build_labels(cleaned)
    write_parquet(labeled, LABEL_DIR / "labeled.parquet")

    print(f"  Điểm neo (dòng sạch)                     : {stats['n_anchor']:>9,}")
    print(f"  − loại: t+24h vượt quá dữ liệu đã thu    : {stats['dropped_beyond_window']:>9,}"
          f"   (= 24 giờ cuối × số thành phố)")
    print(f"  − loại: mốc t+24h đã bị cách ly          : {stats['dropped_future_quarantined']:>9,}")
    print(f"  = Dòng có nhãn                           : {stats['n_labeled']:>9,}")
    if stats["unexpected_codes"]:
        print(f"  ⚠ Xuất hiện mã WMO chưa từng thấy ở ERA5: {stats['unexpected_codes']}")

    print("\n  Phân bố nhãn (gộp):")
    dist = labeled["label"].value_counts().reindex(CLASSES)
    for cls, n in dist.items():
        bar = "█" * int(round(n / len(labeled) * 60))
        print(f"    {cls:12} {n:>9,}  {n / len(labeled):6.2%}  {bar}")

    print("\n  Phân bố nhãn theo thành phố (%):")
    table = pd.crosstab(labeled["entity_id"], labeled["label"], normalize="index").reindex(columns=CLASSES) * 100
    print(table.round(1).to_string())

    print("\n  Baseline phải vượt (accuracy):")
    base = baselines(labeled)
    for _, r in base.iterrows():
        need = max(r.persistence, r.lop_dong_nhat)
        print(f"    {r.entity_id:12} persistence {r.persistence:6.2%}   lớp đông nhất ({r.lop:11}) "
              f"{r.lop_dong_nhat:6.2%}   → model phải > {need:6.2%}")

    print("\n  Ví dụ 3 dòng (feature tại t → nhãn tại t+24h):")
    cols = ["entity_id", "event_time", LABEL_SOURCE, "precipitation", "label_time", "label_raw", "label"]
    print(labeled[cols].sample(3, random_state=1).to_string(index=False))
    print(f"\n  Lưu tại: {rel(LABEL_DIR / 'labeled.parquet')}")


if __name__ == "__main__":
    main()

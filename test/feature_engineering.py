"""
BƯỚC 6 — FEATURE ENGINEERING
============================
Từ bảng có nhãn, sinh đặc trưng cho model rồi chia train / validation / test theo THỜI GIAN.

    Nguyên tắc bất di bất dịch: đặc trưng của dòng t CHỈ được dùng dữ liệu có event_time ≤ t.
    Mọi cửa sổ trượt đều NHÌN LÙI (trailing), không bao giờ nhìn hai phía.

    Nhóm đặc trưng                        Ví dụ                               Vì sao
    ───────────────────────────────────── ─────────────────────────────────── ─────────────────────────────────
    Gốc tại t                              temperature_2m, cloud_cover, ...    trạng thái hiện tại
    Trễ (lag) 1/3/6/12/24h                 cloud_cover_lag3h                   xu hướng, không chỉ một lát cắt
    Biến thiên                             pressure_msl_delta3h                áp suất giảm nhanh → sắp mưa
    Cửa sổ trượt 3/6/24h                   precipitation_sum24h                "đang trong đợt mưa hay không"
    Nhóm thời tiết tại t và t−24h          group_now_*, group_lag24h_*         persistence ~51% → đặc trưng mạnh
    Chu kỳ                                 hour_sin, doy_cos                   23h và 0h phải gần nhau
    Gió dạng vector                        wind_u_10m, wind_v_10m              359° và 1° phải gần nhau
    Vật lý dẫn xuất                        dew_point_depression, is_day        không khí sắp bão hoà → dễ mưa
    Thực thể                               latitude, elevation, city_*         một model chung cho 12 thành phố
    Prior khí hậu học (FIT TRÊN TRAIN)     prior_3_mua                         tỉ lệ mưa của thành phố theo tháng

    Đầu vào : 3_clean/cleaned.parquet (chuỗi đầy đủ để tính lag), 4_labeled/labeled.parquet (điểm neo + nhãn)
              5_validation/report.json (phải ĐẠT mới được chạy)
    Đầu ra  : 6_features/{train,val,test}.parquet
              6_features/artifacts/ — feature_spec.json, climatology_prior.json, split.json, label_mapping.json

Chia tập: test = 365 ngày cuối, validation = 365 ngày trước đó, train = phần còn lại (cả hai đều phủ trọn
một vòng mùa). Bỏ 24 giờ đầu của validation và test làm VÙNG ĐỆM: nhãn của điểm neo cuối tập trước nằm
ở t + 24h, lấn sang đầu tập sau.

Chạy:
    python test/feature_engineering.py
    python test/feature_engineering.py --val-days 180 --test-days 180   # khi dữ liệu ngắn
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from config import (CITIES, CLASSES, CLEAN_DIR, FEATURE_DIR, HORIZON_HOURS, KEYS, LABEL_DIR, LABEL_MAPPING,
                    LABEL_SOURCE, MEASURES, RAW_DIR, VALID_DIR, header, read_json, read_parquet, rel, setup_console,
                    to_class, write_json, write_parquet)

LAG_VARS = ["cloud_cover", "precipitation", "pressure_msl", "relative_humidity_2m", "temperature_2m"]
LAGS = [1, 3, 6, 12, 24]
DELTAS = [("pressure_msl", 3), ("pressure_msl", 24), ("temperature_2m", 24), ("relative_humidity_2m", 3)]
ROLLING = [("cloud_cover", "mean", 3), ("cloud_cover", "mean", 6), ("cloud_cover", "mean", 24),
           ("relative_humidity_2m", "mean", 3), ("relative_humidity_2m", "mean", 6),
           ("relative_humidity_2m", "mean", 24), ("precipitation", "sum", 6), ("precipitation", "sum", 24),
           ("pressure_msl", "std", 24), ("wind_gusts_10m", "max", 24)]
WIND = [("10m", "wind_speed_10m", "wind_direction_10m"), ("100m", "wind_speed_100m", "wind_direction_100m")]
PRIOR_SMOOTHING = 1.0          # làm trơn Laplace cho prior khí hậu học


def _one_hot(values: pd.Series, prefix: str, levels: list[str]) -> pd.DataFrame:
    """One-hot với DANH SÁCH MỨC CỐ ĐỊNH — train/val/test/serving luôn ra cùng một bộ cột."""
    cat = pd.Categorical(values.astype("string"), categories=levels)
    out = pd.get_dummies(cat, prefix=prefix, dtype="float32").set_axis(values.index)
    out[values.isna().to_numpy()] = np.nan      # thiếu giá trị → giữ RỖNG, đừng để thành hàng toàn số 0
    return out


def time_series_features(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Đặc trưng chỉ phụ thuộc chuỗi thời gian của CHÍNH thành phố đó, chỉ nhìn lùi."""
    parts = []
    for entity_id, g in cleaned.groupby("entity_id", sort=True):
        g = g.set_index("event_time").sort_index()
        # Dựng lưới giờ đầy đủ: mốc bị cách ly thành dòng rỗng → shift(k) đúng bằng "k giờ trước"
        grid = pd.date_range(g.index.min(), g.index.max(), freq="h", tz="UTC")
        g = g.reindex(grid)
        f = pd.DataFrame(index=grid)
        f["entity_id"] = entity_id

        for col in MEASURES:                                              # gốc tại t
            if not col.startswith("wind_direction"):
                f[col] = g[col]
        for name, speed, direction in WIND:                               # hướng gió → vector (u, v)
            rad = np.deg2rad(g[direction])
            f[f"wind_u_{name}"] = -g[speed] * np.sin(rad)
            f[f"wind_v_{name}"] = -g[speed] * np.cos(rad)
        for col in LAG_VARS:                                              # trễ
            for k in LAGS:
                f[f"{col}_lag{k}h"] = g[col].shift(k)
        for col, k in DELTAS:                                             # biến thiên
            f[f"{col}_delta{k}h"] = g[col] - g[col].shift(k)
        for col, how, w in ROLLING:                                       # cửa sổ trượt NHÌN LÙI, đòi đủ w giờ
            f[f"{col}_{how}{w}h"] = getattr(g[col].rolling(w, min_periods=w), how)()
        group_now = to_class(g[LABEL_SOURCE])                             # nhóm thời tiết tại t và t−24h
        f = f.join(_one_hot(group_now.set_axis(grid), "group_now", CLASSES))
        f = f.join(_one_hot(group_now.shift(24).set_axis(grid), "group_lag24h", CLASSES))
        hour = grid.hour.to_numpy()                                       # chu kỳ
        doy = grid.dayofyear.to_numpy()
        f["hour_sin"], f["hour_cos"] = np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)
        f["doy_sin"], f["doy_cos"] = np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)
        f["dew_point_depression"] = g["temperature_2m"] - g["dew_point_2m"]   # vật lý dẫn xuất
        f["is_day"] = (g["shortwave_radiation"] > 0).astype("float32")
        for col in ("latitude", "longitude", "elevation"):                # thực thể
            f[col] = g[col].ffill().bfill()
        parts.append(f.rename_axis("event_time").reset_index())
    out = pd.concat(parts, ignore_index=True)
    out = out.join(_one_hot(out["entity_id"], "city", list(CITIES)))
    return out


def split_by_time(anchors: pd.Series, val_days: int, test_days: int, end: pd.Timestamp | None = None) -> dict:
    """Biên chia tập theo thời gian: test = N ngày cuối, val = M ngày trước đó, train = phần còn lại."""
    end = end if end is not None else anchors.max().ceil("D")
    test_start = end - pd.Timedelta(days=test_days)
    val_start = test_start - pd.Timedelta(days=val_days)
    if val_start <= anchors.min() + pd.Timedelta(days=30):
        raise SystemExit(f"Dữ liệu quá ngắn ({(end - anchors.min()).days} ngày) cho val {val_days} + test {test_days} "
                         "ngày — giảm --val-days/--test-days hoặc thu thập thêm.")
    embargo = pd.Timedelta(hours=HORIZON_HOURS)
    return {"train": (anchors.min(), val_start), "val": (val_start + embargo, test_start),
            "test": (test_start + embargo, end), "embargo_hours": HORIZON_HOURS}


def fit_climatology_prior(train: pd.DataFrame) -> dict:
    """FIT CHỈ TRÊN TRAIN: tỉ lệ từng lớp theo (thành phố, tháng), làm trơn Laplace."""
    month = train["event_time"].dt.month
    counts = pd.crosstab([train["entity_id"], month], train["label"]).reindex(columns=CLASSES, fill_value=0)
    probs = (counts + PRIOR_SMOOTHING).div(counts.sum(axis=1) + PRIOR_SMOOTHING * len(CLASSES), axis=0)
    glob = train["label"].value_counts(normalize=True).reindex(CLASSES).fillna(0)
    return {"fitted_on": "train", "fitted_range": [str(train["event_time"].min()), str(train["event_time"].max())],
            "n_rows": len(train), "global": glob.round(6).to_dict(),
            "table": {f"{e}|{m}": probs.loc[(e, m)].round(6).to_dict() for e, m in probs.index}}


def apply_climatology_prior(df: pd.DataFrame, prior: dict) -> pd.DataFrame:
    """APPLY nguyên vẹn bảng đã fit — không bao giờ fit lại trên val/test/serving."""
    keys = df["entity_id"].astype(str) + "|" + df["event_time"].dt.month.astype(str)
    rows = [prior["table"].get(k, prior["global"]) for k in keys]
    for cls in CLASSES:
        df[f"prior_{cls}"] = np.array([r[cls] for r in rows], dtype="float32")
    return df


def leakage_self_check(feats: pd.DataFrame, cleaned: pd.DataFrame, n: int = 300) -> list[str]:
    """Tính lại độc lập vài đặc trưng từ bảng sạch để chắc chắn chúng chỉ dùng dữ liệu ≤ t."""
    lookup = cleaned.set_index(KEYS).sort_index()
    sample = feats.dropna().sample(min(n, len(feats)), random_state=0)
    errors = []
    for _, r in sample.iterrows():
        t = r["event_time"]
        lag = lookup["cloud_cover"].get((r["entity_id"], t - pd.Timedelta(hours=24)))
        if lag is not None and not np.isclose(lag, r["cloud_cover_lag24h"]):
            errors.append(f"cloud_cover_lag24h sai tại {r['entity_id']} {t}")
        window = [lookup["precipitation"].get((r["entity_id"], t - pd.Timedelta(hours=h))) for h in range(24)]
        if all(v is not None for v in window) and not np.isclose(sum(window), r["precipitation_sum24h"], atol=1e-3):
            errors.append(f"precipitation_sum24h sai tại {r['entity_id']} {t}")
    return errors


def main() -> None:
    setup_console()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--val-days", type=int, default=365)
    parser.add_argument("--test-days", type=int, default=365)
    parser.add_argument("--force", action="store_true", help="chạy dù validation chưa ĐẠT (không khuyến khích)")
    args = parser.parse_args()

    verdict = read_json(VALID_DIR / "report.json")
    if verdict["blocked"] and not args.force:
        raise SystemExit(f"Validation đang CHẶN ({verdict['blocked']}) — sửa lỗi trước, hoặc dùng --force.")

    cleaned = read_parquet(CLEAN_DIR / "cleaned.parquet")
    labeled = read_parquet(LABEL_DIR / "labeled.parquet")
    header("BƯỚC 6 — FEATURE ENGINEERING")

    feats = time_series_features(cleaned)
    anchors = labeled[KEYS + ["label_raw", "label"]]
    data = anchors.merge(feats, on=KEYS, how="left")                  # đặc trưng tại t + nhãn tại t + 24h

    manifest = RAW_DIR / "_manifest.json"            # mốc cuối = mốc cuối cửa sổ thu thập (ngày tròn)
    end = pd.Timestamp(read_json(manifest)["end"], tz="UTC") if manifest.exists() else None
    bounds = split_by_time(data["event_time"], args.val_days, args.test_days, end)
    splits = {name: data[(data["event_time"] >= a) & (data["event_time"] < b)].copy()
              for name, (a, b) in ((k, v) for k, v in bounds.items() if k != "embargo_hours")}
    n_embargo = len(data) - sum(len(s) for s in splits.values())

    prior = fit_climatology_prior(splits["train"])                     # FIT trên train
    feature_cols = None
    dropped = {}
    for name, df in splits.items():
        df = apply_climatology_prior(df, prior)                         # APPLY cho cả 3 tập
        if feature_cols is None:
            feature_cols = [c for c in df.columns if c not in KEYS + ["label_raw", "label"]]
        before = len(df)
        df = df.dropna(subset=feature_cols)                             # 24h đầu (lag) + quanh mốc bị cách ly
        dropped[name] = before - len(df)
        df[feature_cols] = df[feature_cols].astype("float32")
        splits[name] = df[KEYS + feature_cols + ["label_raw", "label"]].reset_index(drop=True)
        write_parquet(splits[name], FEATURE_DIR / f"{name}.parquet")

    errors = leakage_self_check(splits["train"], cleaned)
    assert pd.Timestamp(prior["fitted_range"][1]) < bounds["val"][0], "prior được fit lấn sang validation!"

    groups = {"gốc tại t": [c for c in feature_cols if c in MEASURES],
              "gió vector": [c for c in feature_cols if c.startswith("wind_u") or c.startswith("wind_v")],
              "trễ (lag)": [c for c in feature_cols if "_lag" in c and not c.startswith("group")],
              "biến thiên": [c for c in feature_cols if "_delta" in c],
              "cửa sổ trượt": [c for c in feature_cols if any(c.endswith(f"{h}{w}h") for _, h, w in ROLLING)],
              "nhóm thời tiết t, t−24h": [c for c in feature_cols if c.startswith("group_")],
              "chu kỳ": [c for c in feature_cols if c.endswith("_sin") or c.endswith("_cos")],
              "vật lý dẫn xuất": ["dew_point_depression", "is_day"],
              "thực thể": [c for c in feature_cols if c in ("latitude", "longitude", "elevation") or c.startswith("city_")],
              "prior khí hậu học (fit train)": [c for c in feature_cols if c.startswith("prior_")]}
    art = FEATURE_DIR / "artifacts"
    write_json({"features": feature_cols, "dtype": "float32", "groups": groups, "target": "label",
                "classes": CLASSES, "keys": KEYS, "generated_at": datetime.now(timezone.utc).isoformat()},
               art / "feature_spec.json")
    write_json(prior, art / "climatology_prior.json")
    write_json({k: [str(v[0]), str(v[1])] if isinstance(v, tuple) else v for k, v in bounds.items()},
               art / "split.json")
    write_json(LABEL_MAPPING, art / "label_mapping.json")

    print(f"  Đặc trưng: {len(feature_cols)} cột")
    for g, cols in groups.items():
        print(f"    {g:30} {len(cols):>3}   {', '.join(cols[:3])}{', ...' if len(cols) > 3 else ''}")

    print(f"\n  {'Tập':6} {'từ':>26} {'đến (không gồm)':>26} {'dòng':>9} {'bỏ do thiếu lag':>16}")
    for name in ("train", "val", "test"):
        a, b = bounds[name]
        print(f"  {name:6} {str(a):>26} {str(b):>26} {len(splits[name]):>9,} {dropped[name]:>16,}")
    print(f"  Vùng đệm {HORIZON_HOURS}h giữa các tập: bỏ {n_embargo:,} điểm neo")

    print("\n  Phân bố nhãn theo tập (%):")
    dist = pd.DataFrame({n: s["label"].value_counts(normalize=True).reindex(CLASSES) * 100 for n, s in splits.items()})
    print(dist.round(2).to_string())

    print(f"\n  Kiểm tra chống rò rỉ: prior fit trên {prior['fitted_range'][0][:10]} → {prior['fitted_range'][1][:10]} "
          f"(chỉ train) ✓;  tính lại lag/rolling độc lập trên 300 dòng: "
          f"{'✓ khớp' if not errors else f'✗ {len(errors)} lỗi: {errors[:2]}'}")
    print(f"\n  Lưu tại: {rel(FEATURE_DIR)}/  (train/val/test.parquet + artifacts/)")


if __name__ == "__main__":
    main()

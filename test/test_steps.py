"""
Test OFFLINE cho các bước tiền xử lý — không gọi API, không đọc test/data/.

Dùng một bảng quan sát nhỏ dựng tại chỗ (2 thành phố × vài chục giờ) có cùng cấu trúc với đầu ra
của flatten.py. Đây là fixture để kiểm thử LOGIC, không phải dữ liệu training.

Chạy:
    pytest test/test_steps.py -v
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cleaning import ALL_RULES, RAIN_TOLERANCE_MM, _fill_short_gaps, clean, inject_errors  # noqa: E402
from config import (CITIES, CLASSES, CODE_TO_CLASS, KEYS, LABEL_SOURCE, MEASURES, WMO_CODES,  # noqa: E402
                    derive_weather_code, wmo_to_int)
from feature_engineering import _one_hot, split_by_time, time_series_features  # noqa: E402
from labeling import build_labels  # noqa: E402

T0 = pd.Timestamp("2025-01-01", tz="UTC")


def make_obs(hours: int = 96, cities=("hanoi", "tokyo"), seed: int = 0) -> pd.DataFrame:
    """Bảng giống đầu ra flatten.py: đủ 27 biến, giá trị hợp lệ, weather_code nhất quán với mưa + mây."""
    rng = np.random.default_rng(seed)
    times = pd.date_range(T0, periods=hours, freq="h", tz="UTC")
    h = np.arange(hours)
    frames = []
    for city in cities:
        meta = CITIES[city]
        precip = np.round(np.clip(rng.normal(0.1, 0.8, hours), 0, None), 1)
        cloud = rng.integers(0, 101, hours)
        temp = 25 + 5 * np.sin(2 * np.pi * h / 24)
        df = pd.DataFrame({
            "entity_id": city, "event_time": times, "entity_name": meta["name"], "country": meta["country"],
            "latitude": meta["latitude"], "longitude": meta["longitude"], "elevation": 10.0,
            "grid_latitude": meta["latitude"], "grid_longitude": meta["longitude"],
            "temperature_2m": temp, "relative_humidity_2m": rng.integers(40, 100, hours),
            "dew_point_2m": temp - 5, "apparent_temperature": temp + 1,
            "pressure_msl": 1010 + np.sin(h / 10), "surface_pressure": 1005 + np.sin(h / 10),
            "precipitation": precip, "rain": precip, "snowfall": 0.0,
            "cloud_cover": cloud, "cloud_cover_low": cloud // 2, "cloud_cover_mid": cloud // 3,
            "cloud_cover_high": cloud // 4,
            "shortwave_radiation": np.clip(800 * np.sin(2 * np.pi * h / 24), 0, None),
            "direct_radiation": np.clip(500 * np.sin(2 * np.pi * h / 24), 0, None),
            "diffuse_radiation": np.clip(200 * np.sin(2 * np.pi * h / 24), 0, None),
            "sunshine_duration": np.clip(3600 * np.sin(2 * np.pi * h / 24), 0, None),
            "wind_speed_10m": rng.uniform(0, 20, hours), "wind_speed_100m": rng.uniform(0, 30, hours),
            "wind_direction_10m": rng.integers(0, 361, hours), "wind_direction_100m": rng.integers(0, 361, hours),
            "wind_gusts_10m": rng.uniform(5, 40, hours), "et0_fao_evapotranspiration": rng.uniform(0, 0.5, hours),
            "vapour_pressure_deficit": rng.uniform(0, 2, hours), "soil_temperature_0_to_7cm": temp,
            "soil_moisture_0_to_7cm": 0.3,
        })
        df["weather_code"] = derive_weather_code(precip, 0.0, cloud)
        df["source_file"] = "fixture"
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


# ── config ───────────────────────────────────────────────────────────────────

def test_label_mapping_covers_every_wmo_code_exactly_once():
    assert sorted(CODE_TO_CLASS) == sorted(WMO_CODES)
    assert set(CODE_TO_CLASS.values()) == set(CLASSES)


def test_derive_weather_code_is_robust_to_float32():
    # sau khi ép float32, 1,3 thành 1,2999999523 — ngưỡng đặt ở điểm giữa nên vẫn đúng
    precip = np.array([0.4, 0.5, 1.0, 1.3, 2.5, 7.6], dtype="float32")
    assert derive_weather_code(precip, 0.0, 100).tolist() == [51, 53, 55, 61, 63, 65]
    assert derive_weather_code(0.0, 0.0, np.array([19, 20, 50, 80])).tolist() == [0, 1, 2, 3]


# ── cleaning ─────────────────────────────────────────────────────────────────

def test_fill_short_gaps_only_fills_short_runs_inside_the_series():
    s = pd.Series([1, np.nan, np.nan, 4, np.nan, np.nan, np.nan, 8, np.nan], dtype="float32")
    filled, mask = _fill_short_gaps(s, max_len=2)
    assert mask.tolist() == [False, True, True, False, False, False, False, False, False]
    assert filled[1:3].tolist() == pytest.approx([2.0, 3.0])
    assert filled[4:7].isna().all() and pd.isna(filled.iloc[8])   # lỗ dài 3 và lỗ ở mép: để nguyên


def test_clean_leaves_clean_data_untouched():
    obs = make_obs()
    cleaned, quarantine, report = clean(obs)
    assert len(cleaned) == len(obs) and quarantine.empty
    assert (cleaned["fixed_by"] == 0).all() and (cleaned["rules_applied"] == ALL_RULES).all()
    assert cleaned["temperature_2m"].dtype == "float32"
    assert isinstance(cleaned[LABEL_SOURCE].dtype, pd.CategoricalDtype)


def test_clean_catches_injected_errors_and_conserves_rows():
    obs, injected = inject_errors(make_obs(hours=24 * 30), n=20)
    cleaned, quarantine, report = clean(obs)
    rules = report["rules"]
    assert rules["R1_ep_kieu"]["pressure_msl"] == 20                      # chữ trong cột số
    assert rules["R2_khoa"]["dòng trùng khoá"] == 4
    assert rules["R3_luoi_gio"]["mốc giờ bị thiếu → thêm dòng rỗng"] == 4
    assert sum(rules["R4_khoang_vat_ly"].values()) == 20                  # giá trị ngoài khoảng
    q_input = quarantine[quarantine["_origin"] == "input"]
    assert len(obs) == len(cleaned) + len(q_input)                        # không dòng nào biến mất
    assert cleaned[KEYS].duplicated().sum() == 0
    assert cleaned[MEASURES + [LABEL_SOURCE]].isna().sum().sum() == 0


def test_clean_is_idempotent():
    obs, _ = inject_errors(make_obs(hours=24 * 30), n=20)
    cleaned, _, _ = clean(obs)
    cleaned2, quarantine2, _ = clean(cleaned)
    assert len(cleaned2) == len(cleaned)
    assert (cleaned2["fixed_by"] == 0).all()                              # lần hai không sửa thêm gì
    assert (quarantine2["_origin"] != "input").all()                      # và không loại thêm dòng thật
    for col in MEASURES:
        assert np.array_equal(cleaned2[col].to_numpy(), cleaned[col].to_numpy(), equal_nan=True), col


def test_consistency_rule_runs_after_interpolation():
    # Hồi quy cho lỗi thứ tự quy tắc: precipitation hỏng (âm) được nội suy thành giá trị nhỏ,
    # trong khi rain thật lớn → phải bị kẹp lại, nếu không lần làm sạch thứ hai sẽ còn sửa.
    obs = make_obs()
    i = obs.index[(obs["entity_id"] == "hanoi") & (obs["event_time"] == T0 + pd.Timedelta(hours=10))][0]
    obs.loc[[i - 1, i + 1], "precipitation"] = 0.0
    obs.loc[i, ["precipitation", "rain"]] = [-5.0, 3.0]
    cleaned, _, _ = clean(obs)
    assert (cleaned["rain"] <= cleaned["precipitation"] + RAIN_TOLERANCE_MM).all()


# ── labeling ─────────────────────────────────────────────────────────────────

def test_labels_join_on_exact_timestamp_not_row_shift():
    cleaned, _, _ = clean(make_obs(hours=72))
    gap = T0 + pd.Timedelta(hours=30)
    cleaned = cleaned[~((cleaned["entity_id"] == "hanoi") & (cleaned["event_time"] == gap))]   # mốc bị cách ly
    labeled, stats = build_labels(cleaned)

    hanoi = labeled[labeled["entity_id"] == "hanoi"].set_index("event_time")
    assert (gap - pd.Timedelta(hours=24)) not in hanoi.index              # nhãn của t=6h rơi vào lỗ → bị loại
    truth = cleaned.set_index(KEYS)[LABEL_SOURCE]
    keys = pd.MultiIndex.from_arrays([labeled["entity_id"], labeled["event_time"] + pd.Timedelta(hours=24)])
    assert (wmo_to_int(truth.reindex(keys)).to_numpy() == labeled["label_raw"].to_numpy()).all()
    assert stats["dropped_future_quarantined"] == 1
    assert stats["dropped_beyond_window"] == 2 * 24                       # 24 giờ cuối × 2 thành phố


# ── feature engineering ─────────────────────────────────────────────────────

def test_features_only_use_the_past():
    cleaned, _, _ = clean(make_obs(hours=96))
    cut = T0 + pd.Timedelta(hours=60)
    before = time_series_features(cleaned)

    future_changed = cleaned.copy()                                       # sửa toàn bộ tương lai sau cut
    after_cut = future_changed["event_time"] > cut
    future_changed.loc[after_cut, MEASURES] = future_changed.loc[after_cut, MEASURES] * 3 + 7
    after = time_series_features(future_changed)

    past = before["event_time"] <= cut                                    # đặc trưng tại t ≤ cut không được đổi
    pd.testing.assert_frame_equal(before[past].reset_index(drop=True), after[past].reset_index(drop=True))

    row = before[(before["entity_id"] == "hanoi") & (before["event_time"] == cut)].iloc[0]
    expected = cleaned[(cleaned["entity_id"] == "hanoi") &
                       (cleaned["event_time"] == cut - pd.Timedelta(hours=24))]["cloud_cover"].iloc[0]
    assert row["cloud_cover_lag24h"] == pytest.approx(expected)


def test_one_hot_keeps_missing_values_missing():
    out = _one_hot(pd.Series(["0_quang", None, "3_mua"]), "g", CLASSES)
    assert out.iloc[0].tolist() == [1, 0, 0, 0] and out.iloc[1].isna().all()


def test_split_is_chronological_with_embargo():
    anchors = pd.Series(pd.date_range("2023-10-01", "2026-09-30 23:00", freq="h", tz="UTC"))
    b = split_by_time(anchors, 365, 365, end=pd.Timestamp("2026-10-01", tz="UTC"))
    assert b["train"][1] <= b["val"][0] - pd.Timedelta(hours=24)          # vùng đệm 24h
    assert b["val"][1] <= b["test"][0] - pd.Timedelta(hours=24)
    assert b["test"][1] == pd.Timestamp("2026-10-01", tz="UTC")
    assert (b["test"][1] - b["test"][0]) >= pd.Timedelta(days=364)        # test phủ trọn một vòng mùa

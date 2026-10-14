"""
Cấu hình và tiện ích dùng chung cho 6 bước tiền xử lý bài toán WX-C1 (wx_code_clf).

    Dự đoán NHÓM HIỆN TƯỢNG THỜI TIẾT tại t + 24h, từ trạng thái khí quyển tại t.

Mọi tri thức của bài toán (thành phố, biến, khoảng vật lý, ánh xạ nhãn) tập trung ở đây để
6 file còn lại chỉ chứa logic xử lý. Dữ liệu lưu local dưới test/data/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── Đường dẫn: mỗi bước một thư mục, đọc thư mục trước, ghi thư mục của mình ──────
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW_DIR = DATA / "1_raw"                  # collection.py          → JSON gốc từ API (gzip)
FLAT_DIR = DATA / "2_flat"                # flatten.py             → bảng quan sát
CLEAN_DIR = DATA / "3_clean"              # cleaning.py            → bảng sạch + bảng cách ly
LABEL_DIR = DATA / "4_labeled"            # labeling.py            → bảng có nhãn
VALID_DIR = DATA / "5_validation"         # validation.py          → báo cáo kiểm tra
FEATURE_DIR = DATA / "6_features"         # feature_engineering.py → train/val/test + artifact

# ── Nguồn dữ liệu ─────────────────────────────────────────────────────────────
API_URL = "https://archive-api.open-meteo.com/v1/archive"
MODEL = "era5"            # ghim ERA5: giá trị đã chốt, không bị sửa lại về sau
ERA5_LAG_DAYS = 6         # đo ngày 2026-10-14: ERA5 có dữ liệu tới T-6
HORIZON_HOURS = 24        # nhãn = nhóm thời tiết tại t + 24h

# 12 thành phố — khí hậu đa dạng để nhãn có đủ biến thiên
CITIES = {
    "hanoi":       {"name": "Hà Nội",          "country": "VN", "latitude": 21.0285,  "longitude": 105.8542},
    "ho_chi_minh": {"name": "TP. Hồ Chí Minh", "country": "VN", "latitude": 10.8231,  "longitude": 106.6297},
    "bangkok":     {"name": "Bangkok",         "country": "TH", "latitude": 13.7563,  "longitude": 100.5018},
    "singapore":   {"name": "Singapore",       "country": "SG", "latitude": 1.3521,   "longitude": 103.8198},
    "jakarta":     {"name": "Jakarta",         "country": "ID", "latitude": -6.2088,  "longitude": 106.8456},
    "mumbai":      {"name": "Mumbai",          "country": "IN", "latitude": 19.0760,  "longitude": 72.8777},
    "tokyo":       {"name": "Tokyo",           "country": "JP", "latitude": 35.6762,  "longitude": 139.6503},
    "sydney":      {"name": "Sydney",          "country": "AU", "latitude": -33.8688, "longitude": 151.2093},
    "london":      {"name": "London",          "country": "GB", "latitude": 51.5074,  "longitude": -0.1278},
    "new_york":    {"name": "New York",        "country": "US", "latitude": 40.7128,  "longitude": -74.0060},
    "sao_paulo":   {"name": "São Paulo",       "country": "BR", "latitude": -23.5505, "longitude": -46.6333},
    "nairobi":     {"name": "Nairobi",         "country": "KE", "latitude": -1.2921,  "longitude": 36.8219},
}

# 27 biến theo giờ, kèm "semantic_type" — bước làm sạch chọn quy tắc theo semantic_type, không theo tên cột
VARIABLES = {
    "temperature_2m":             "temperature_c",
    "relative_humidity_2m":       "percent",
    "dew_point_2m":               "temperature_c",
    "apparent_temperature":       "temperature_c",
    "pressure_msl":               "pressure_hpa",
    "surface_pressure":           "pressure_hpa",
    "precipitation":              "precip_mm",
    "rain":                       "precip_mm",
    "snowfall":                   "snow_cm",
    "cloud_cover":                "percent",
    "cloud_cover_low":            "percent",
    "cloud_cover_mid":            "percent",
    "cloud_cover_high":           "percent",
    "shortwave_radiation":        "radiation_wm2",
    "direct_radiation":           "radiation_wm2",
    "diffuse_radiation":          "radiation_wm2",
    "sunshine_duration":          "duration_s",
    "wind_speed_10m":             "speed_kmh",
    "wind_speed_100m":            "speed_kmh",
    "wind_direction_10m":         "angle_deg",
    "wind_direction_100m":        "angle_deg",
    "wind_gusts_10m":             "speed_kmh",
    "et0_fao_evapotranspiration": "et0_mm",
    "vapour_pressure_deficit":    "vpd_kpa",
    "weather_code":               "wmo_code",
    "soil_temperature_0_to_7cm":  "temperature_c",
    "soil_moisture_0_to_7cm":     "ratio",
}
LABEL_SOURCE = "weather_code"
MEASURES = [v for v, t in VARIABLES.items() if t != "wmo_code"]   # 26 biến số đo

# Khoảng vật lý hợp lệ theo semantic_type (nới rộng hơn khoảng đo thật để không loại nhầm)
VALID_RANGES = {
    "temperature_c": (-90, 60),
    "percent":       (0, 100),
    "pressure_hpa":  (800, 1100),
    "precip_mm":     (0, 400),
    "snow_cm":       (0, 100),
    "radiation_wm2": (0, 1500),
    "duration_s":    (0, 3600),
    "speed_kmh":     (0, 500),
    "angle_deg":     (0, 360),
    "et0_mm":        (0, 10),
    "vpd_kpa":       (0, 15),
    "ratio":         (0, 1),
}

# Toàn bộ mã WMO 4677 hợp lệ mà Open-Meteo có thể trả về
WMO_CODES = [0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57, 61, 63, 65, 66, 67,
             71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 99]

# Ánh xạ mã WMO → 4 lớp. Khai đủ mọi mã hợp lệ (kể cả mã ERA5 chưa từng sinh ra) để nếu nguồn
# đổi hành vi thì pipeline vẫn chạy, còn validation sẽ cảnh báo mã lạ.
CLASSES = ["0_quang", "1_nhieu_may", "2_mua_phun", "3_mua"]
LABEL_MAPPING = {
    "0_quang":     [0, 1],
    "1_nhieu_may": [2, 3, 45, 48],                       # 45, 48 = sương mù (ERA5 không sinh)
    "2_mua_phun":  [51, 53, 55, 56, 57],
    "3_mua":       [61, 63, 65, 66, 67, 71, 73, 75, 77,  # tuyết (0,15%) gộp vào mưa
                    80, 81, 82, 85, 86, 95, 96, 99],
}
CODE_TO_CLASS = {code: cls for cls, codes in LABEL_MAPPING.items() for code in codes}
CODES_SEEN_IN_ERA5 = [0, 1, 2, 3, 51, 53, 55, 61, 63, 65, 71, 73, 75]   # đo 5 năm × 12 thành phố

# Phân bố nhãn kỳ vọng (đo thật 5 năm × 12 thành phố) — dùng để phát hiện bất thường ở validation
EXPECTED_CLASS_SHARE = {"0_quang": 0.3186, "1_nhieu_may": 0.4167, "2_mua_phun": 0.2264, "3_mua": 0.0382}

KEYS = ["entity_id", "event_time"]


def derive_weather_code(precipitation, snowfall, cloud_cover) -> np.ndarray:
    """
    Suy lại weather_code từ 3 biến cùng dòng. Ngưỡng ĐO ĐƯỢC từ dữ liệu ERA5 (khớp 99,96%):
    weather_code không mang thông tin gì ngoài 3 biến này. Dùng để kiểm tra chất lượng nhãn.

    Ngưỡng mưa đặt ở ĐIỂM GIỮA hai mức đo (lượng mưa có độ phân giải 0,1 mm), không đặt đúng biên:
    sau khi ép float32, 1,3 thành 1,2999999523 và phép "p < 1,3" cho kết quả SAI.
    """
    p = np.asarray(precipitation, dtype="float64")
    s = np.asarray(snowfall, dtype="float64")
    c = np.asarray(cloud_cover, dtype="float64")
    cloud = np.select([c < 19.5, c < 49.5, c < 79.5], [0, 1, 2], default=3)
    rain = np.select([p < 0.45, p < 0.95, p < 1.25, p < 2.45, p < 7.55], [51, 53, 55, 61, 63], default=65)
    snow = np.select([s < 0.2, s < 0.8], [71, 73], default=75)
    return np.where(s > 0, snow, np.where(p > 0, rain, cloud))


WMO_CATEGORIES = [str(c) for c in WMO_CODES]


def wmo_category(values) -> pd.Categorical:
    """
    Mã WMO → kiểu category với nhãn là CHUỖI ("0", "51", ...). Mã lạ / không phải số → rỗng.

    Vì sao chuỗi: (1) weather_code là biến PHÂN LOẠI — mã 75 không "lớn hơn" mã 3 theo nghĩa nào;
    (2) category số nguyên bị Parquet (pyarrow 25) lưu thành int64 và đọc lại ra float64, mất kiểu;
    category chuỗi thì giữ nguyên, kể cả danh sách mã chưa từng xuất hiện.
    """
    s = pd.Series(values)
    if isinstance(s.dtype, pd.CategoricalDtype):
        s = s.astype("string")
    codes = pd.to_numeric(s, errors="coerce")
    valid = codes.isin(WMO_CODES)
    labels = np.where(valid, codes.fillna(-1).astype("int64").astype(str), None)
    return pd.Categorical(labels, categories=WMO_CATEGORIES)


def wmo_to_int(values) -> pd.Series:
    """Category chuỗi → số nguyên (nullable) để tra bảng ánh xạ hoặc so sánh."""
    s = pd.Series(values)
    return pd.to_numeric(s.astype("string"), errors="coerce").astype("Int64")


def to_class(codes) -> pd.Series:
    """Mã WMO → nhãn 4 lớp, kiểu category có thứ tự cố định."""
    ints = wmo_to_int(codes)
    mapped = ints.map(lambda c: CODE_TO_CLASS.get(int(c)) if pd.notna(c) else None)
    return pd.Series(pd.Categorical(mapped, categories=CLASSES), index=ints.index)


# ── Tiện ích đọc/ghi ──────────────────────────────────────────────────────────
def setup_console() -> None:
    """Console Windows (cp1252) không in được tiếng Việt → ép UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        sys.exit(f"Chưa có {rel(path)} — hãy chạy bước trước.")
    return pd.read_parquet(path)


def write_json(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def read_json(path: Path):
    if not path.exists():
        sys.exit(f"Chưa có {rel(path)} — hãy chạy bước trước.")
    return json.loads(path.read_text(encoding="utf-8"))


def header(title: str) -> None:
    print(f"\n{'═' * 78}\n  {title}\n{'═' * 78}")


def rel(path: Path) -> str:
    """Đường dẫn tương đối so với gốc repo, để in ra cho gọn."""
    try:
        return str(Path(path).resolve().relative_to(ROOT.parent)).replace("\\", "/")
    except ValueError:
        return str(path)

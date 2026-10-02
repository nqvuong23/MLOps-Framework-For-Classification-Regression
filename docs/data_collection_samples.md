# Data Collection: bảng kết quả mẫu

Dữ liệu thật, thu ngày 2026-10-02 bằng CLI `python -m framework.collection run`, ghi ra thư mục local `_collection_out/`. Mỗi bài toán chạy một run theo lịch và một backfill: Open-Meteo lấy điểm neo từ 2026-09-09 đến hết 2026-09-23, OpenAQ từ 2026-09-23 đến hết 2026-09-29 cộng một giờ của run theo lịch. Cách chạy lại: xem [data_collection_demo.md](data_collection_demo.md).

Mỗi bài toán đi qua ba bước: JSON gốc từ API, bảng quan sát sau khi flatten, bảng training có nhãn. Bảng mẫu chỉ hiển thị một số cột; danh sách đủ cột nằm ngay dưới mỗi bảng. Mọi mốc thời gian là UTC.

## Tổng hợp

| problem_id    | Nguồn      | Loại       |   Thực thể |   Dòng quan sát |   Số cột |   Dòng có nhãn |   Số cột có nhãn | Nhãn                                            |
|:--------------|:-----------|:-----------|-----------:|----------------:|---------:|---------------:|-----------------:|:------------------------------------------------|
| `wx_temp_reg` | open_meteo | regression |         12 |           4,608 |       34 |          4,320 |               40 | nhãn trong [4.8, 34.4], trung bình 23.44        |
| `wx_rain_clf` | open_meteo | binary     |         12 |           4,608 |       34 |          4,320 |               40 | tỉ lệ lớp dương 57.9% (2,503/4,320)             |
| `aq_pm25_reg` | openaq     | regression |         12 |           2,247 |       47 |          1,709 |               53 | nhãn trong [2.10208, 48.5625], trung bình 13.13 |
| `aq_pm25_clf` | openaq     | binary     |         12 |           2,247 |       47 |          1,709 |               53 | tỉ lệ lớp dương 3.9% (67/1,709)                 |

## wx_temp_reg (open_meteo, regression)

Dự báo nhiệt độ (°C) sau 24 giờ tại mỗi địa điểm — nguồn Open-Meteo (ERA5).

- Nhãn: `last(temperature_2m)` trên `(t, t + 24h]`; `min_coverage = 1`.
- Thực thể: 12; tần suất dữ liệu: 1 giờ; `maturity_lag`: 7 ngày; lịch DAG: `0 6 * * *`.

### Bước 1: JSON gốc từ API (`landing/`)

2 file response. File mẫu: `_collection_out/wx_temp_reg/landing/window=20260909T0000Z_20260923T0000Z/part-00000.json.gz`. Cấu trúc: mảng 12 object, mỗi địa điểm một object; dưới đây là object đầu tiên (đã rút gọn để dễ đọc).

```json
{
  "request": {
    "url": "https://archive-api.open-meteo.com/v1/archive",
    "params": {
      "latitude": "21.0285,10.8231,13.7563,1.3521,-6.2088,19.076,35.6762,-33…",
      "longitude": "105.8542,106.6297,100.5018,103.8198,106.8456,72.8777,139.…",
      "start_date": "2026-09-09",
      "end_date": "2026-09-23",
      "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,apparent…",
      "timezone": "UTC",
      "models": "era5"
    },
    "entity_ids": [
      "hanoi",
      "ho_chi_minh",
      "bangkok",
      "… (12 giá trị)"
    ],
    "fetched_at": "2026-10-02T13:53:15.885860+00:00"
  },
  "response": [
    {
      "latitude": 21.0,
      "longitude": 105.75,
      "generationtime_ms": 26.14903450012207,
      "utc_offset_seconds": 0,
      "timezone": "GMT",
      "timezone_abbreviation": "GMT",
      "elevation": 19.0,
      "hourly_units": {
        "time": "iso8601",
        "temperature_2m": "°C",
        "relative_humidity_2m": "%",
        "pressure_msl": "hPa",
        "…": "(28 khoá)"
      },
      "hourly": {
        "time": [
          "2026-09-09T00:00",
          "2026-09-09T01:00",
          "2026-09-09T02:00",
          "… (360 giá trị)"
        ],
        "temperature_2m": [
          27.7,
          28.0,
          30.8,
          "… (360 giá trị)"
        ],
        "relative_humidity_2m": [
          90,
          90,
          77,
          "… (360 giá trị)"
        ],
        "pressure_msl": [
          1008.7,
          1009.6,
          1010.3,
          "… (360 giá trị)"
        ],
        "…": "(28 mảng song song)"
      }
    },
    "… (12 địa điểm)"
  ]
}
```

### Bước 2: bảng quan sát sau khi flatten (`observations/`)

4,608 dòng × 34 cột; 12 thực thể; `event_time` từ 2026-09-09 00:00 đến 2026-09-24 23:00 UTC. Mỗi dòng là một cặp (thực thể, giờ).

| entity_id   | event_time       | entity_name   | country   |   temperature_2m |   relative_humidity_2m |   pressure_msl |   precipitation |   cloud_cover |   wind_speed_10m |
|:------------|:-----------------|:--------------|:----------|-----------------:|-----------------------:|---------------:|----------------:|--------------:|-----------------:|
| hanoi       | 2026-09-09 00:00 | Hà Nội        | VN        |             27.7 |                     90 |         1008.7 |             0   |             7 |              4.4 |
| hanoi       | 2026-09-09 01:00 | Hà Nội        | VN        |             28   |                     90 |         1009.6 |             0   |            10 |              5.2 |
| hanoi       | 2026-09-09 02:00 | Hà Nội        | VN        |             30.8 |                     77 |         1010.3 |             0   |            18 |              6.6 |
| tokyo       | 2026-09-09 00:00 | Tokyo         | JP        |             28.5 |                     81 |         1004.4 |             0   |            96 |             29.9 |
| tokyo       | 2026-09-09 01:00 | Tokyo         | JP        |             29.1 |                     79 |         1004.4 |             0.1 |           100 |             29.3 |
| tokyo       | 2026-09-09 02:00 | Tokyo         | JP        |             29.5 |                     78 |         1003.8 |             0.1 |           100 |             28.1 |

Đủ 34 cột: `entity_id`, `event_time`, `entity_name`, `latitude`, `longitude`, `country`, `elevation`, `temperature_2m`, `relative_humidity_2m`, `dew_point_2m`, `apparent_temperature`, `pressure_msl`, `surface_pressure`, `precipitation`, `rain`, `snowfall`, `cloud_cover`, `cloud_cover_low`, `cloud_cover_mid`, `cloud_cover_high`, `shortwave_radiation`, `direct_radiation`, `diffuse_radiation`, `sunshine_duration`, `wind_speed_10m`, `wind_speed_100m`, `wind_direction_10m`, `wind_direction_100m`, `wind_gusts_10m`, `et0_fao_evapotranspiration`, `vapour_pressure_deficit`, `weather_code`, `soil_temperature_0_to_7cm`, `soil_moisture_0_to_7cm`.

### Bước 3: bảng training có nhãn (`labeled/`)

4,320 dòng × 40 cột; điểm neo từ 2026-09-09 00:00 đến 2026-09-23 23:00 UTC; nhãn trong [4.8, 34.4], trung bình 23.44; số khoá `(entity_id, event_time)` bị trùng: 0; số điểm neo bị loại vì không đủ dữ liệu để xác định nhãn: 0.

| entity_id   | event_time       | country   |   temperature_2m |   relative_humidity_2m |   pressure_msl |   label |   label_raw |   label_coverage | label_window_end   | source     | window_key                    |
|:------------|:-----------------|:----------|-----------------:|-----------------------:|---------------:|--------:|------------:|-----------------:|:-------------------|:-----------|:------------------------------|
| hanoi       | 2026-09-09 00:00 | VN        |             27.7 |                     90 |         1008.7 |    25.1 |        25.1 |                1 | 2026-09-10 00:00   | open_meteo | 20260909T0000Z_20260923T0000Z |
| hanoi       | 2026-09-09 01:00 | VN        |             28   |                     90 |         1009.6 |    25.2 |        25.2 |                1 | 2026-09-10 01:00   | open_meteo | 20260909T0000Z_20260923T0000Z |
| hanoi       | 2026-09-09 02:00 | VN        |             30.8 |                     77 |         1010.3 |    27.8 |        27.8 |                1 | 2026-09-10 02:00   | open_meteo | 20260909T0000Z_20260923T0000Z |
| tokyo       | 2026-09-09 00:00 | JP        |             28.5 |                     81 |         1004.4 |    20.5 |        20.5 |                1 | 2026-09-10 00:00   | open_meteo | 20260909T0000Z_20260923T0000Z |
| tokyo       | 2026-09-09 01:00 | JP        |             29.1 |                     79 |         1004.4 |    20.9 |        20.9 |                1 | 2026-09-10 01:00   | open_meteo | 20260909T0000Z_20260923T0000Z |
| tokyo       | 2026-09-09 02:00 | JP        |             29.5 |                     78 |         1003.8 |    21.4 |        21.4 |                1 | 2026-09-10 02:00   | open_meteo | 20260909T0000Z_20260923T0000Z |

Mọi cột của bảng quan sát được giữ nguyên làm feature; thêm 6 cột: `label`, `label_raw`, `label_coverage`, `label_window_end`, `source`, `window_key`.

Đối chiếu dòng đầu của bảng mẫu (`hanoi`, 2026-09-09 00:00): cửa sổ nhãn có 24/24 giờ có số đo hợp lệ, `last` tính lại từ `observations/` = 25.1, `label_raw` trong bảng = 25.1.

## wx_rain_clf (open_meteo, binary)

Dự đoán 24 giờ tới có mưa (tổng lượng mưa >= 1 mm) — nguồn Open-Meteo (ERA5).

- Nhãn: `sum(precipitation)` trên `(t, t + 24h]`, `label = 1` nếu `label_raw >= 1`; `min_coverage = 1`.
- Thực thể: 12; tần suất dữ liệu: 1 giờ; `maturity_lag`: 7 ngày; lịch DAG: `30 6 * * *`.

### Bước 1 và 2: JSON gốc và bảng quan sát

Giống hệt [wx_temp_reg](#wx_temp_reg-open_meteo-regression): hai bài toán dùng chung nguồn, danh sách biến và thực thể, chỉ khác cách tính nhãn. Dữ liệu vẫn được thu và lưu riêng dưới `_collection_out/wx_rain_clf/`: 2 file response trong `landing/`, 4,608 dòng × 34 cột trong `observations/`.

### Bước 3: bảng training có nhãn (`labeled/`)

4,320 dòng × 40 cột; điểm neo từ 2026-09-09 00:00 đến 2026-09-23 23:00 UTC; tỉ lệ lớp dương 57.9% (2,503/4,320); số khoá `(entity_id, event_time)` bị trùng: 0; số điểm neo bị loại vì không đủ dữ liệu để xác định nhãn: 0.

| entity_id   | event_time       | country   |   precipitation |   temperature_2m |   relative_humidity_2m |   label |   label_raw |   label_coverage | label_window_end   | source     | window_key                    |
|:------------|:-----------------|:----------|----------------:|-----------------:|-----------------------:|--------:|------------:|-----------------:|:-------------------|:-----------|:------------------------------|
| hanoi       | 2026-09-09 00:00 | VN        |             0   |             27.7 |                     90 |       1 |        10.8 |                1 | 2026-09-10 00:00   | open_meteo | 20260909T0000Z_20260923T0000Z |
| tokyo       | 2026-09-09 00:00 | JP        |             0   |             28.5 |                     81 |       1 |        14   |                1 | 2026-09-10 00:00   | open_meteo | 20260909T0000Z_20260923T0000Z |
| hanoi       | 2026-09-09 01:00 | VN        |             0   |             28   |                     90 |       1 |        11.1 |                1 | 2026-09-10 01:00   | open_meteo | 20260909T0000Z_20260923T0000Z |
| hanoi       | 2026-09-10 21:00 | VN        |             1.1 |             24.9 |                     93 |       0 |         0.8 |                1 | 2026-09-11 21:00   | open_meteo | 20260909T0000Z_20260923T0000Z |
| hanoi       | 2026-09-10 22:00 | VN        |             0.2 |             24.2 |                     98 |       0 |         0.6 |                1 | 2026-09-11 22:00   | open_meteo | 20260909T0000Z_20260923T0000Z |
| hanoi       | 2026-09-10 23:00 | VN        |             0   |             24.5 |                     96 |       0 |         0.6 |                1 | 2026-09-11 23:00   | open_meteo | 20260909T0000Z_20260923T0000Z |

Mọi cột của bảng quan sát được giữ nguyên làm feature; thêm 6 cột: `label`, `label_raw`, `label_coverage`, `label_window_end`, `source`, `window_key`.

Đối chiếu dòng đầu của bảng mẫu (`hanoi`, 2026-09-09 00:00): cửa sổ nhãn có 24/24 giờ có số đo hợp lệ, `sum` tính lại từ `observations/` = 10.8, `label_raw` trong bảng = 10.8.

## aq_pm25_reg (openaq, regression)

Dự báo nồng độ PM2.5 trung bình 24 giờ tới (µg/m³) tại trạm — nguồn OpenAQ.

- Nhãn: `mean(pm25)` trên `(t, t + 24h]`; `min_coverage = 0.75`.
- Thực thể: 12; tần suất dữ liệu: 1 giờ; `maturity_lag`: 1 ngày; lịch DAG: `5 * * * *`.

### Bước 1: JSON gốc từ API (`landing/`)

110 file response. File mẫu: `_collection_out/aq_pm25_reg/landing/window=20260923T0000Z_20260930T0000Z/part-00052.json.gz`. Cấu trúc: `results[]` có 193 phần tử, mỗi phần tử là số đo một giờ của một sensor; dưới đây là phần tử đầu tiên (đã rút gọn để dễ đọc).

```json
{
  "request": {
    "url": "https://api.openaq.org/v3/sensors/13502151/hours",
    "params": {
      "datetime_from": "2026-09-22T23:00:00Z",
      "datetime_to": "2026-10-01T00:00:00Z",
      "limit": 1000,
      "page": 1
    },
    "entity_id": "4946812",
    "sensor_id": 13502151,
    "parameter": "pm25",
    "fetched_at": "2026-10-02T14:06:35.167245+00:00"
  },
  "response": {
    "meta": {
      "name": "openaq-api",
      "website": "/",
      "page": 1,
      "limit": 1000,
      "found": 193
    },
    "results": [
      {
        "value": 26.1,
        "flagInfo": {
          "hasFlags": false
        },
        "parameter": {
          "id": 2,
          "name": "pm25",
          "units": "µg/m³",
          "displayName": null
        },
        "period": {
          "label": "1hour",
          "interval": "01:00:00",
          "datetimeFrom": {
            "utc": "2026-09-22T23:00:00Z",
            "local": "2026-09-23T06:00:00+07:00"
          },
          "datetimeTo": {
            "utc": "2026-09-23T00:00:00Z",
            "local": "2026-09-23T07:00:00+07:00"
          }
        },
        "coordinates": null,
        "summary": {
          "min": 22.42,
          "q02": 22.7456,
          "q25": 24.3675,
          "median": 25.29,
          "q75": 27.2625,
          "q98": 31.415999999999997,
          "max": 32.01,
          "avg": 26.095,
          "sd": 2.862246869656275
        },
        "coverage": {
          "expectedCount": 1,
          "expectedInterval": "01:00:00",
          "observedCount": 12,
          "observedInterval": "12:00:00",
          "percentComplete": 1200.0,
          "percentCoverage": 1200.0,
          "datetimeFrom": {
            "utc": "2026-09-22T22:05:00Z",
            "local": "2026-09-23T05:05:00+07:00"
          },
          "datetimeTo": {
            "utc": "2026-09-23T00:00:00Z",
            "local": "2026-09-23T07:00:00+07:00"
          }
        }
      },
      "… (193 phần tử)"
    ]
  }
}
```

### Bước 2: bảng quan sát sau khi flatten (`observations/`)

2,247 dòng × 47 cột; 12 thực thể; `event_time` từ 2026-09-23 00:00 đến 2026-10-01 13:00 UTC. Mỗi dòng là một cặp (thực thể, giờ).

|   entity_id | event_time       | entity_name                           | country   |   pm25 |   pm10 |       no2 |        o3 |   pm25_min |   pm25_max |   pm25_coverage |
|------------:|:-----------------|:--------------------------------------|:----------|-------:|-------:|----------:|----------:|-----------:|-----------:|----------------:|
|     2622556 | 2026-09-23 00:00 | 경인항                                   | KR        |   27   |   67   |    0.0359 |    0.0135 |      27    |      27    |             100 |
|     2622556 | 2026-09-23 01:00 | 경인항                                   | KR        |   18   |   40   |    0.0234 |    0.0346 |      18    |      18    |             100 |
|     2622556 | 2026-09-23 02:00 | 경인항                                   | KR        |   10   |   29   |    0.0169 |    0.0464 |      10    |      10    |             100 |
|     4946812 | 2026-09-23 00:00 | Công viên Nhân Chính - Khuất Duy Tiến | VN        |   26.1 |   54.8 | null      | null      |      22.42 |      32.01 |            1200 |
|     4946812 | 2026-09-23 01:00 | Công viên Nhân Chính - Khuất Duy Tiến | VN        |   28.2 |   48.6 | null      | null      |      25.2  |      31.48 |            1200 |
|     4946812 | 2026-09-23 02:00 | Công viên Nhân Chính - Khuất Duy Tiến | VN        |   41   |   65.9 | null      | null      |      33.05 |      46.98 |            1200 |

Đủ 47 cột: `entity_id`, `event_time`, `entity_name`, `latitude`, `longitude`, `country`, `locality`, `timezone`, `provider`, `pm25`, `pm10`, `no2`, `o3`, `so2`, `co`, `pm25_min`, `pm10_min`, `no2_min`, `o3_min`, `so2_min`, `co_min`, `pm25_max`, `pm10_max`, `no2_max`, `o3_max`, `so2_max`, `co_max`, `pm25_sd`, `pm10_sd`, `no2_sd`, `o3_sd`, `so2_sd`, `co_sd`, `pm25_coverage`, `pm10_coverage`, `no2_coverage`, `o3_coverage`, `so2_coverage`, `co_coverage`, `pm25_flagged`, `pm10_flagged`, `no2_flagged`, `o3_flagged`, `so2_flagged`, `co_flagged`, `temperature`, `relativehumidity`.

Cột toàn `null` (không thực thể nào có số đo): `no2_sd`, `o3_sd`, `so2_sd`, `co_sd`, `temperature`, `relativehumidity`. Cột vẫn được giữ để schema ổn định.

### Bước 3: bảng training có nhãn (`labeled/`)

1,709 dòng × 53 cột; điểm neo từ 2026-09-23 00:00 đến 2026-09-30 13:00 UTC; nhãn trong [2.10208, 48.5625], trung bình 13.13; số khoá `(entity_id, event_time)` bị trùng: 0; số điểm neo bị loại vì không đủ dữ liệu để xác định nhãn: 121.

|   entity_id | event_time       | country   |   pm25 |   pm10 |       no2 |   label |   label_raw |   label_coverage | label_window_end   | source   | window_key                    |
|------------:|:-----------------|:----------|-------:|-------:|----------:|--------:|------------:|-----------------:|:-------------------|:---------|:------------------------------|
|     2622556 | 2026-09-23 00:00 | KR        |   27   |   67   |    0.0359 | 15      |     15      |                1 | 2026-09-24 00:00   | openaq   | 20260923T0000Z_20260930T0000Z |
|     2622556 | 2026-09-23 01:00 | KR        |   18   |   40   |    0.0234 | 14.8333 |     14.8333 |                1 | 2026-09-24 01:00   | openaq   | 20260923T0000Z_20260930T0000Z |
|     2622556 | 2026-09-23 02:00 | KR        |   10   |   29   |    0.0169 | 15.0833 |     15.0833 |                1 | 2026-09-24 02:00   | openaq   | 20260923T0000Z_20260930T0000Z |
|     4946812 | 2026-09-23 00:00 | VN        |   26.1 |   54.8 | null      | 43.3208 |     43.3208 |                1 | 2026-09-24 00:00   | openaq   | 20260923T0000Z_20260930T0000Z |
|     4946812 | 2026-09-23 01:00 | VN        |   28.2 |   48.6 | null      | 44.2625 |     44.2625 |                1 | 2026-09-24 01:00   | openaq   | 20260923T0000Z_20260930T0000Z |
|     4946812 | 2026-09-23 02:00 | VN        |   41   |   65.9 | null      | 44.6958 |     44.6958 |                1 | 2026-09-24 02:00   | openaq   | 20260923T0000Z_20260930T0000Z |

Mọi cột của bảng quan sát được giữ nguyên làm feature; thêm 6 cột: `label`, `label_raw`, `label_coverage`, `label_window_end`, `source`, `window_key`.

Đối chiếu dòng đầu của bảng mẫu (`2622556`, 2026-09-23 00:00): cửa sổ nhãn có 24/24 giờ có số đo hợp lệ, `mean` tính lại từ `observations/` = 15, `label_raw` trong bảng = 15.

## aq_pm25_clf (openaq, binary)

Dự đoán 24 giờ tới PM2.5 trung bình có vượt ngưỡng không lành mạnh — nguồn OpenAQ.

- Nhãn: `mean(pm25)` trên `(t, t + 24h]`, `label = 1` nếu `label_raw > 35.4`; `min_coverage = 0.75`.
- Thực thể: 12; tần suất dữ liệu: 1 giờ; `maturity_lag`: 1 ngày; lịch DAG: `35 * * * *`.

### Bước 1 và 2: JSON gốc và bảng quan sát

Giống hệt [aq_pm25_reg](#aq_pm25_reg-openaq-regression): hai bài toán dùng chung nguồn, danh sách biến và thực thể, chỉ khác cách tính nhãn. Dữ liệu vẫn được thu và lưu riêng dưới `_collection_out/aq_pm25_clf/`: 110 file response trong `landing/`, 2,247 dòng × 47 cột trong `observations/`.

### Bước 3: bảng training có nhãn (`labeled/`)

1,709 dòng × 53 cột; điểm neo từ 2026-09-23 00:00 đến 2026-09-30 13:00 UTC; tỉ lệ lớp dương 3.9% (67/1,709); số khoá `(entity_id, event_time)` bị trùng: 0; số điểm neo bị loại vì không đủ dữ liệu để xác định nhãn: 121.

|   entity_id | event_time       | country   |   pm25 |   pm10 |       no2 |   label |   label_raw |   label_coverage | label_window_end   | source   | window_key                    |
|------------:|:-----------------|:----------|-------:|-------:|----------:|--------:|------------:|-----------------:|:-------------------|:---------|:------------------------------|
|     4946812 | 2026-09-23 00:00 | VN        |   26.1 |   54.8 | null      |       1 |     43.3208 |                1 | 2026-09-24 00:00   | openaq   | 20260923T0000Z_20260930T0000Z |
|     4946812 | 2026-09-23 01:00 | VN        |   28.2 |   48.6 | null      |       1 |     44.2625 |                1 | 2026-09-24 01:00   | openaq   | 20260923T0000Z_20260930T0000Z |
|     4946812 | 2026-09-23 02:00 | VN        |   41   |   65.9 | null      |       1 |     44.6958 |                1 | 2026-09-24 02:00   | openaq   | 20260923T0000Z_20260930T0000Z |
|     2622556 | 2026-09-23 00:00 | KR        |   27   |   67   |    0.0359 |       0 |     15      |                1 | 2026-09-24 00:00   | openaq   | 20260923T0000Z_20260930T0000Z |
|     2622556 | 2026-09-23 01:00 | KR        |   18   |   40   |    0.0234 |       0 |     14.8333 |                1 | 2026-09-24 01:00   | openaq   | 20260923T0000Z_20260930T0000Z |
|     2622556 | 2026-09-23 02:00 | KR        |   10   |   29   |    0.0169 |       0 |     15.0833 |                1 | 2026-09-24 02:00   | openaq   | 20260923T0000Z_20260930T0000Z |

Mọi cột của bảng quan sát được giữ nguyên làm feature; thêm 6 cột: `label`, `label_raw`, `label_coverage`, `label_window_end`, `source`, `window_key`.

Đối chiếu dòng đầu của bảng mẫu (`4946812`, 2026-09-23 00:00): cửa sổ nhãn có 24/24 giờ có số đo hợp lệ, `mean` tính lại từ `observations/` = 43.3208, `label_raw` trong bảng = 43.3208.

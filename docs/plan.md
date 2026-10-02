# Plan — Bài toán từ OpenAQ / Open-Meteo & tính năng "Data Collection"

> **Trạng thái**: §3 đã được hiện thực (xem [§8](#8-hiện-thực-so-với-kế-hoạch)). Ngày khảo sát API: **2026-10-02**.
> **Thay thế** phần chọn nguồn trong [datasets.md](datasets.md) (EIA, NYC 311): hai nguồn chính thức là **OpenAQ** và **Open-Meteo**.
> Các con số về field, giới hạn, độ trễ bên dưới lấy từ OpenAPI spec của OpenAQ (`api.openaq.org/openapi.json`),
> tài liệu Open-Meteo, và các lệnh gọi thử trực tiếp.

---

## 0. Tóm tắt

| | OpenAQ | Open-Meteo |
|---|---|---|
| Bản chất dữ liệu | **Số đo thật** từ trạm quan trắc không khí | **Reanalysis / mô hình** thời tiết dạng lưới (ERA5, ECMWF IFS) |
| Hồi quy đề xuất | Nồng độ **PM2.5 trung bình 24h tới** tại trạm | **Nhiệt độ** `temperature_2m` tại `t + 24h` |
| Phân loại đề xuất | 24h tới có **vượt ngưỡng PM2.5 không lành mạnh** không | 24h tới **có mưa** không (tổng lượng mưa ≥ 1 mm) |
| Nhãn "chín" sau | ~48h (24h horizon + 24h chờ dữ liệu về muộn) | ~8 ngày (24h horizon + 7 ngày chờ ERA5 chốt) |
| Lịch DAG hợp lý | mỗi giờ | mỗi ngày |
| Độ khó thu thập | Cao hơn: cần API key, gọi theo từng sensor, có thiếu/lỗi số đo | Thấp: không key, 1 request cho nhiều địa điểm, không thiếu giá trị |

**Thứ tự làm demo**: Open-Meteo trước (đơn giản, chạy được ngay) → OpenAQ sau (kiểm chứng tính năng đủ tổng quát).

Cả 4 bài toán đều quy về **một phép biến đổi chung**: *nhãn = hàm tổng hợp của cột mục tiêu trên cửa sổ `(t, t + H]`*.
Vì vậy tính năng Data Collection chỉ cần viết một lần, khác nhau ở cấu hình.

---

## 1. Hai nguồn cung cấp những gì

### 1.1 OpenAQ (API v3)

| | |
|---|---|
| Base URL | `https://api.openaq.org/v3` |
| Xác thực | Header `X-API-Key` (đăng ký miễn phí tại explore.openaq.org). Không có key → HTTP 401 |
| Giới hạn | **60 request/phút, 2.000 request/giờ**; vượt → HTTP 429; theo dõi qua header `x-ratelimit-remaining`, `x-ratelimit-reset` |
| Phân trang | `limit` (mặc định 100) + `page`; tổng số bản ghi ở `meta.found` |

Endpoint cần dùng:

| Endpoint | Dùng để | Tham số chính |
|---|---|---|
| `GET /locations` | Tìm trạm | `iso`, `coordinates` + `radius`, `bbox`, `parameters_id`, `monitor` |
| `GET /locations/{id}/sensors` | Lấy danh sách sensor của trạm | — |
| `GET /sensors/{id}/hours` | **Số đo trung bình theo giờ** (nguồn chính) | `datetime_from`, `datetime_to`, `limit`, `page` |
| `GET /sensors/{id}/days` | Trung bình theo ngày | `date_from`, `date_to` |
| `GET /parameters` | Tra mã thông số (PM2.5, PM10, O₃, NO₂, SO₂, CO…) | — |

Field trả về của một bản ghi giờ (`results[]`):

| Field | Ý nghĩa | Vai trò |
|---|---|---|
| `value` | Giá trị trung bình giờ (có thể `null`) | **feature / nguồn tính nhãn** |
| `parameter.{id,name,units}` | Thông số và đơn vị | tên cột khi pivot |
| `period.datetimeFrom.utc`, `period.datetimeTo.utc` | Khoảng thời gian của số đo | **event time** |
| `summary.{min,q25,median,q75,max,avg,sd}` | Thống kê trong giờ | feature phụ |
| `coverage.{expectedCount,observedCount,percentComplete}` | Độ đầy đủ số đo | **lọc chất lượng** |
| `flagInfo.hasFlags` | Số đo bị gắn cờ nghi ngờ | **lọc chất lượng** |
| `coordinates.{latitude,longitude}` | Toạ độ | metadata |

Metadata trạm (`/locations`): `id`, `name`, `locality`, `timezone`, `country.code`, `provider.name`, `isMonitor`
(trạm tham chiếu), `isMobile`, `sensors[]`, `datetimeFirst`, `datetimeLast`.

Lưu ý thực tế:
- Mỗi trạm có bộ sensor khác nhau; phải gọi **theo từng sensor**.
- Nhiều trạm đã ngừng gửi dữ liệu → bắt buộc kiểm `datetimeLast` trước khi chọn.
- Lịch sử dài có sẵn dạng CSV tại `s3://openaq-data-archive` (không cần credential), cột:
  `location_id, sensors_id, location, datetime, lat, lon, parameter, units, value` → dùng cho backfill.

### 1.2 Open-Meteo (Historical Weather API)

| | |
|---|---|
| URL | `https://archive-api.open-meteo.com/v1/archive` |
| Xác thực | **Không cần key** |
| Giới hạn (miễn phí) | 600/phút, 5.000/giờ, 10.000/ngày, 300.000/tháng |
| Tham số | `latitude`, `longitude` (nhận **danh sách** nhiều điểm), `start_date`, `end_date`, `hourly`, `daily`, `timezone`, `models` |
| License | CC-BY 4.0 (ghi nguồn) |

Biến theo giờ (`hourly`):

| Nhóm | Biến |
|---|---|
| Nhiệt – ẩm | `temperature_2m`, `apparent_temperature`, `relative_humidity_2m`, `dew_point_2m`, `vapour_pressure_deficit` |
| Áp suất – mây | `pressure_msl`, `surface_pressure`, `cloud_cover`, `cloud_cover_low/mid/high` |
| Mưa – tuyết | `precipitation`, `rain`, `snowfall`, `snow_depth`, `weather_code` (mã WMO) |
| Gió | `wind_speed_10m`, `wind_speed_100m`, `wind_direction_10m`, `wind_gusts_10m` |
| Bức xạ | `shortwave_radiation`, `direct_radiation`, `diffuse_radiation`, `sunshine_duration` |
| Đất | `soil_temperature_*`, `soil_moisture_*`, `et0_fao_evapotranspiration` |

Biến theo ngày (`daily`): `temperature_2m_max/min`, `precipitation_sum`, `rain_sum`, `precipitation_hours`,
`weather_code`, `wind_speed_10m_max`, `shortwave_radiation_sum`, `sunrise`, `sunset`…

Hình dạng JSON: **dạng cột** — `hourly: {time: [...], temperature_2m: [...], ...}`; gọi nhiều toạ độ thì trả về
**mảng** các object, mỗi object một địa điểm.

**Độ trễ nhãn — đã kiểm bằng lệnh gọi thật ngày 2026-10-02:**

| Chế độ | Dữ liệu có đến | Hệ quả |
|---|---|---|
| Mặc định (`best_match`) | hôm nay | Vài ngày gần nhất lấy từ IFS, **sau đó bị thay bằng ERA5** → giá trị có thể đổi |
| `models=era5` | **2026-09-26** (trễ 6 ngày), sau đó là `null` | Giá trị đã chốt, không đổi nữa |

→ Để đúng yêu cầu "nhãn đã xác định xong", demo dùng **`models=era5` + lùi 7 ngày**.

Open-Meteo còn có Air Quality API (`air-quality-api.open-meteo.com`, biến `pm2_5`, `pm10`, `us_aqi`… từ mô hình CAMS) —
không dùng làm nhãn vì là output mô hình, nhưng có thể làm baseline so sánh cho bài toán OpenAQ về sau.

---

## 2. Đề xuất bài toán

Quy ước chung: mỗi dòng dữ liệu là một cặp **(thực thể, thời điểm neo `t`)**; feature là giá trị quan sát tại `t`;
nhãn tính trên cửa sổ tương lai `(t, t + 24h]`. Horizon `H = 24h` là tham số cấu hình.

### 2.1 OpenAQ

**Hồi quy — `aq_pm25_reg`: dự báo PM2.5 trung bình 24 giờ tới tại trạm.**
- Nhãn: trung bình `value` của sensor PM2.5 trên `(t, t+24h]`, đơn vị µg/m³.
- Điều kiện hợp lệ: có ≥ 18/24 giờ số đo hợp lệ (75%, đúng quy ước tính trung bình 24h của US EPA).
- Feature tại `t`: PM2.5, PM10, NO₂, O₃, SO₂, CO (tuỳ trạm), thống kê `summary`, giờ/thứ/tháng, toạ độ.
- Baseline có sẵn: persistence (PM2.5 tại `t`) → đo được "skill" của model.
- Vì sao chọn: PM2.5 là thông số phổ biến nhất trên OpenAQ, có ý nghĩa sức khoẻ rõ, biến động theo mùa mạnh (drift thật).

**Phân loại — `aq_pm25_clf`: 24 giờ tới có vượt ngưỡng không lành mạnh không.**
- Nhãn: `1` nếu PM2.5 trung bình `(t, t+24h]` **> 35,4 µg/m³** (mốc "Unhealthy for Sensitive Groups" của US EPA AQI), ngược lại `0`.
- Ngưỡng là tham số: với thành phố sạch dùng mốc WHO 2021 (**15 µg/m³**) để tỉ lệ lớp dương không quá thấp.
- Vì sao chọn: nhãn = **số đo thật × ngưỡng do cơ quan y tế công bố**, không phải rule tự đặt; đúng dạng cảnh báo mà các hệ thống AQI thực tế phát hành.
- Phương án đa lớp (6 mức AQI) để dành sau — nhị phân đủ cho demo và ít lệch lớp hơn.

Tiêu chí chọn trạm (5–10 trạm): `isMonitor = true`, `isMobile = false`, có sensor PM2.5, `datetimeLast` trong 48h gần nhất,
`datetimeFirst` ≥ 2 năm trước, tỉ lệ lớp dương kỳ vọng 10–40% (ưu tiên đô thị ô nhiễm theo mùa).

### 2.2 Open-Meteo

**Hồi quy — `wx_temp_reg`: dự báo nhiệt độ sau 24 giờ.**
- Nhãn: `temperature_2m` tại `t + 24h` (°C).
- Feature tại `t`: nhiệt độ, độ ẩm, điểm sương, áp suất, mây, gió, bức xạ, độ ẩm đất, giờ/ngày trong năm.
- Baseline: persistence (nhiệt độ tại `t`, cùng giờ hôm nay).
- Vì sao chọn: biến liên tục, không thiếu giá trị, phân phối "đẹp". Không chọn lượng mưa làm hồi quy vì phần lớn giá trị bằng 0 (zero-inflated).

**Phân loại — `wx_rain_clf`: 24 giờ tới có mưa không.**
- Nhãn: `1` nếu tổng `precipitation` trên `(t, t+24h]` **≥ 1,0 mm** (định nghĩa "ngày có mưa" thông dụng trong khí tượng).
- Vì sao chọn: bài toán kinh điển (kiểu "RainTomorrow"), dễ giải thích; tỉ lệ lớp thay đổi mạnh giữa mùa mưa và mùa khô → **prior shift theo mùa**, minh chứng tốt cho nhu cầu retrain.
- Không chọn `weather_code` đa lớp: ~28 mã WMO, lệch lớp nặng, khó đánh giá trong demo.

Chọn địa điểm (5–10 toạ độ): các thành phố có mùa mưa rõ (ví dụ Hà Nội, Đà Nẵng, TP.HCM) để nhãn mưa không quá lệch.

**Giới hạn cần nói rõ trong báo cáo**: nhãn Open-Meteo là reanalysis (ECMWF/Copernicus), không phải số đo tại trạm.
Đủ uy tín và ổn định cho mục đích MLOps, nhưng không nên tuyên bố là "dự báo thời tiết tốt hơn mô hình số trị".

### 2.3 Bảng chốt

| `problem_id` | Nguồn | Loại | Nhãn | Nhãn chín sau | Lệch lớp |
|---|---|---|---|---|---|
| `aq_pm25_reg` | OpenAQ | regression | mean PM2.5 `(t, t+24h]` | ~48h | — |
| `aq_pm25_clf` | OpenAQ | binary | mean PM2.5 > 35,4 µg/m³ | ~48h | tuỳ trạm, mục tiêu 10–40% |
| `wx_temp_reg` | Open-Meteo | regression | `temperature_2m` tại `t+24h` | ~8 ngày | — |
| `wx_rain_clf` | Open-Meteo | binary | Σ precipitation `(t, t+24h]` ≥ 1 mm | ~8 ngày | theo mùa, ước lượng 20–60% |

Trong cùng một nguồn, nhãn phân loại suy ra trực tiếp từ nhãn hồi quy / cùng cửa sổ → **một lần thu thập xuất được cả hai cột nhãn**;
chọn bài toán nào chỉ là chọn cột `target` ở bước train.

**Hướng mở rộng** (ngoài phạm vi demo): ghép thời tiết Open-Meteo theo toạ độ trạm làm feature cho bài toán PM2.5 —
gió, mưa, độ ẩm là yếu tố chi phối ô nhiễm; hai nguồn bạn chọn bổ sung cho nhau rất tự nhiên.

---

## 3. Tính năng "Data Collection"

### 3.1 Phạm vi

**Đầu vào**: cấu hình một bài toán (nguồn, danh sách thực thể, biến cần lấy, horizon, luật tính nhãn).
**Đầu ra**: bảng training dạng tabular, mỗi dòng có feature tại `t` + nhãn đã xác định, lưu Parquet theo partition ngày.
**Không thuộc phạm vi**: cleaning nâng cao, feature engineering (lag/rolling), train, serving — các khối này nối vào sau.

### 3.2 Nguyên tắc cốt lõi: chỉ thu thập điểm neo có nhãn đã "chín"

Một DAG run kết thúc tại `T` **không** lấy dữ liệu mới nhất, mà lấy các điểm neo đủ cũ:

```
              điểm neo t              hết cửa sổ nhãn        nguồn đã chốt số liệu      DAG run
────────────────┼──────── H ────────────┼──────── M ──────────────┼──────────────────────┤ T
           t = T − (H + M)           t + H                    t + H + M
```

- `H` — horizon của nhãn (24h).
- `M` — thời gian chờ nguồn chốt số liệu (*maturity lag*): OpenAQ 24h (số đo về muộn), Open-Meteo 7 ngày (ERA5).
- Mỗi run **tự chứa**: gọi API lấy đúng đoạn `[t_đầu, t_cuối + H]` cần cho các điểm neo của run đó, không phụ thuộc run trước.

| | OpenAQ | Open-Meteo |
|---|---|---|
| Schedule | mỗi giờ | mỗi ngày |
| Điểm neo của mỗi run `[T − H − M − interval, T − H − M)` | 1 giờ: `[T − 49h, T − 48h)` | 24 giờ của ngày `T − 9 ngày` |
| Đoạn dữ liệu cần gọi | 25 giờ / sensor | 2 ngày / địa điểm |
| Số request / run | số trạm × số sensor (~30–40) | **1** (nhiều toạ độ trong một request) |

### 3.3 Cấu hình (mỗi bài toán một file, DAG sinh ra từ file này)

Các khoá dự kiến của `problems/<problem_id>/collection.yaml`:

| Khoá | Ví dụ | Ý nghĩa |
|---|---|---|
| `source` | `openaq` / `open_meteo` | chọn connector |
| `schedule` | `@hourly` / `@daily` | chu kỳ DAG |
| `entities` | file danh sách trạm / toạ độ | thực thể cần thu thập |
| `variables` | `[pm25, pm10, no2, o3]` | biến cần lấy |
| `horizon` | `24h` | cửa sổ nhãn |
| `maturity_lag` | `24h` / `7d` | thời gian chờ nguồn chốt |
| `label.target` | `pm25` / `temperature_2m` / `precipitation` | cột dùng tính nhãn |
| `label.agg` | `mean` / `last` / `sum` | cách tổng hợp trên cửa sổ |
| `label.threshold` | `35.4` / `1.0` | ngưỡng sinh nhãn phân loại |
| `label.min_coverage` | `0.75` | tỉ lệ số đo tối thiểu để nhãn hợp lệ |

### 3.4 Các bước của DAG `<problem_id>_collect`

| # | Task | Việc làm | Kết quả |
|---|---|---|---|
| 1 | `resolve_window` | Từ `data_interval_end`, `H`, `M` tính khoảng điểm neo và đoạn dữ liệu cần gọi | khoảng thời gian (XCom) |
| 2 | `extract` | Gọi API theo từng thực thể; retry + backoff khi 429/5xx; **lưu nguyên JSON** (nén gzip) | `landing/…/run=<id>/*.json.gz` + manifest (tham số gọi, HTTP status, số bản ghi) |
| 3 | `flatten` | JSON → bảng quan sát: mỗi dòng = (thực thể, giờ UTC), mỗi biến một cột; chuẩn hoá kiểu, đơn vị, múi giờ | bảng `observations` |
| 4 | `validate` | Kiểm tra tối thiểu: không rỗng, không trùng khoá (thực thể, giờ), khoảng giá trị hợp lệ, loại số đo bị gắn cờ / coverage thấp | dòng lỗi → `quarantine/`, dòng sạch đi tiếp |
| 5 | `build_labels` | Với mỗi điểm neo `t`: tổng hợp cột mục tiêu trên `(t, t+H]` → nhãn hồi quy; áp ngưỡng → nhãn phân loại; bỏ dòng không đủ coverage | bảng training có nhãn |
| 6 | `load` | Ghi Parquet, **ghi đè partition** theo ngày của điểm neo | `labeled/event_date=YYYY-MM-DD/` |
| 7 | `report` | Log số dòng lấy về / hợp lệ / có nhãn, tỉ lệ lớp dương; cảnh báo khi 0 dòng | log + alert qua `send_alert` |

Quy tắc áp dụng cho mọi task:
- Khoảng thời gian chỉ lấy từ `data_interval_*` của Airflow, không dùng `now()` hay Airflow Variable → **rerun cho kết quả y hệt**.
- XCom chỉ chở đường dẫn và số đếm, không chở DataFrame.
- Feature chỉ dùng dữ liệu tại `≤ t`; cửa sổ nhãn bắt đầu **sau** `t` → không rò rỉ nhãn.
- API key đọc từ biến môi trường (`OPENAQ_API_KEY` trong `.env`, không commit); chuyển sang SSM là bước sau.

### 3.5 Khác biệt khi flatten giữa hai nguồn

| | OpenAQ | Open-Meteo |
|---|---|---|
| Dạng JSON | **dạng dòng**: `results[]`, mỗi phần tử một số đo của một sensor | **dạng cột**: các mảng song song theo `time` |
| Phép biến đổi | gộp các sensor của cùng trạm → pivot `parameter.name` thành cột | "bung" mảng thành dòng, gắn mã địa điểm |
| Khoá thời gian | `period.datetimeTo.utc` — mốc **kết thúc** giờ đo, để dòng tại `t` không chứa số đo sau `t` | `time` (yêu cầu `timezone=UTC`) |
| Giá trị thiếu | thường gặp (`null`, giá trị âm, giờ bị mất) | không có (trừ đoạn ERA5 chưa cập nhật) |
| Lưu ý riêng | đơn vị khác nhau giữa các trạm (µg/m³ / ppm) | `precipitation` là tổng của **giờ trước đó** → cửa sổ `(t, t+H]` lấy các mốc `t+1 … t+H` |

### 3.6 Schema bảng đầu ra

| Cột | Mô tả |
|---|---|
| `entity_id` | mã trạm (OpenAQ) hoặc mã địa điểm (Open-Meteo) |
| `event_time` | điểm neo `t`, UTC |
| `<biến>` … | giá trị các biến tại `t` (feature thô) |
| `label_reg` | nhãn hồi quy |
| `label_clf` | nhãn phân loại (0/1) |
| `label_window_end` | `t + H` |
| `label_coverage` | tỉ lệ số đo có trong cửa sổ nhãn |
| `source`, `run_id`, `collected_at` | truy vết nguồn gốc |

Nơi lưu (theo layout ở [datasets.md §4.2](datasets.md)): `s3://<bucket>/<problem_id>/{landing,observations,labeled,quarantine}/`.

### 3.7 Nạp lịch sử ban đầu (backfill)

Tái sử dụng đúng logic bước 2–6 với một khoảng ngày dài, chạy một lần ngoài lịch:
- Open-Meteo: một request trả được nhiều năm dữ liệu giờ cho mỗi địa điểm → chia theo năm.
- OpenAQ: API phù hợp cho vài tháng gần nhất (bị giới hạn request); lịch sử dài lấy từ S3 archive (dạng CSV, không giới hạn).

---

## 4. Trình tự thực hiện demo

| Bước | Việc | Kiểm chứng |
|---|---|---|
| 1 | Chốt bài toán demo đầu tiên (đề xuất: `wx_rain_clf` + `wx_temp_reg`) và danh sách 5 toạ độ | file `entities` |
| 2 | Viết `collection.yaml` cho Open-Meteo | review cấu hình |
| 3 | Làm connector Open-Meteo: `extract` + `flatten`, thử trên 1 ngày | bảng `observations` đúng số dòng = 24 × số địa điểm |
| 4 | Làm `build_labels` + `load`; kiểm tay vài dòng nhãn so với dữ liệu gốc | nhãn khớp khi tính lại bằng tay |
| 5 | Ghép thành DAG `@daily`, chạy 3–5 run liên tiếp và **rerun 1 run** | partition không trùng dòng, rerun ra kết quả y hệt |
| 6 | Backfill 1–2 năm | bảng training đủ lớn, xem tỉ lệ lớp theo tháng |
| 7 | Đăng ký API key OpenAQ, chọn trạm theo tiêu chí §2.1 | danh sách trạm còn hoạt động |
| 8 | Làm connector OpenAQ (chỉ thay `extract` + `flatten`), dùng lại bước 4–5 | DAG `@hourly` chạy xanh, **không sửa** `build_labels` / `load` |
| 9 | Chuẩn bị kịch bản demo: trigger DAG → xem JSON thô → xem bảng có nhãn | chạy trọn trong vài phút |

Bước 1–6 là demo tối thiểu trình bày được. Bước 7–8 chứng minh tính năng dùng chung cho nguồn thứ hai.

## 5. Tiêu chí hoàn thành demo

- [ ] DAG chạy theo interval, mỗi run sinh thêm đúng một lô dữ liệu training mới.
- [ ] Xem được cả ba tầng: JSON nguyên bản → bảng quan sát → bảng có nhãn.
- [ ] Mọi dòng trong bảng training đều có nhãn đã xác định (không có nhãn tạm / `null`).
- [ ] Rerun một run cũ không tạo dòng trùng và cho kết quả giống hệt.
- [ ] Hai nguồn chạy trên cùng logic gán nhãn, chỉ khác connector và file cấu hình.

## 6. Rủi ro & điểm cần bạn chốt

| Vấn đề | Ảnh hưởng | Hướng xử lý |
|---|---|---|
| Trạm OpenAQ ngừng gửi dữ liệu hoặc thiếu nhiều giờ | Run không sinh được dòng | Lọc theo `datetimeLast`; chọn dư trạm; `min_coverage` |
| Giới hạn 60 request/phút của OpenAQ | 429 khi nhiều trạm | Giãn nhịp gọi, đọc header `x-ratelimit-remaining` |
| ERA5 trễ 6 ngày | Dữ liệu training luôn chậm ~8 ngày | Chấp nhận (retrain tuần vẫn đủ); hoặc dùng `best_match` và ghi đè lại sau khi ERA5 chốt |
| Ngưỡng PM2.5 không phù hợp với trạm đã chọn | Lệch lớp nặng | Xem phân phối sau backfill rồi mới chốt ngưỡng |

Cần bạn quyết định trước khi code:
1. Bài toán demo đầu tiên: Open-Meteo (đề xuất) hay OpenAQ?
2. Địa điểm / trạm: Việt Nam hay các thành phố quốc tế có dữ liệu dày hơn?
3. Nơi lưu cho demo: S3 ngay, hay thư mục local trong container Airflow rồi chuyển S3 sau?

## 7. Tài liệu đã dùng

- OpenAQ: [API docs](https://docs.openaq.org/) · [measurements](https://docs.openaq.org/resources/measurements) · [locations](https://docs.openaq.org/resources/locations) · [rate limits](https://docs.openaq.org/using-the-api/rate-limits) · [OpenAPI spec](https://api.openaq.org/openapi.json) · [S3 archive](https://docs.openaq.org/aws/about)
- Open-Meteo: [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) · [Air Quality API](https://open-meteo.com/en/docs/air-quality-api) · [điều khoản & giới hạn](https://open-meteo.com/en/terms)

## 8. Hiện thực so với kế hoạch

Code: [framework/collection/](../framework/collection/) · config: [problems/](../problems/) ·
DAG: [data_collection_dag.py](../airflow/dags/data_collection_dag.py) · test: [tests/collection/](../tests/collection/).

| Kế hoạch | Hiện thực |
|---|---|
| 7 task (§3.4) | **5 task**: `resolve_window → extract → flatten → build_labels → report`. `load` gộp vào từng bước (mỗi bước tự ghi layer của mình); `validate` chỉ còn kiểm tra cấu trúc (không rỗng, một dòng / khoá) — cleaning và quarantine để cho khối sau |
| 2 lần thu thập, mỗi lần 2 cột nhãn (§2.3) | **4 DAG độc lập**, mỗi bài toán một thư mục config và một cột `label` |
| Ghi đè partition (§3.4) | Thay đúng khoảng thời gian của run trong file ngày → run theo giờ, run theo ngày và backfill không tạo dòng trùng |
| Cột đầu ra (§3.6) | `label`, `label_raw` (giá trị trước khi áp ngưỡng), `label_coverage`, `label_window_end`, `source`, `window_key` |
| Chọn trạm OpenAQ (§2.1) | Lệnh `python -m framework.collection discover-openaq` sinh `problems/_entities/openaq_stations.yaml` |

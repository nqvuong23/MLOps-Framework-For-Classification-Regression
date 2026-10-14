# Phân tích hai nguồn dữ liệu & lựa chọn bài toán

> **Mục đích**: tổng hợp lại toàn bộ hiểu biết về hai nguồn API đang dùng cho khối Data Collection,
> đủ chi tiết để quay lại làm việc sau thời gian dài không chạm vào code.
>
> **Cách lập tài liệu**: mọi số liệu trong file này được **đo thật bằng cách gọi API ngày 2026-10-14**
> (OpenAPI spec của OpenAQ, trang tài liệu của Open-Meteo, và hàng trăm request thăm dò biên thời gian).
> Chỗ nào chưa kiểm chứng được đều ghi rõ. Mọi mốc thời gian là **UTC**.
> Ký hiệu `T` = ngày chạy (hôm nay), `T-6` = 6 ngày trước.

**Mục lục**

1. [Hai nguồn dữ liệu](#1-hai-nguồn-dữ-liệu)
2. [Open-Meteo — chi tiết API](#2-open-meteo--chi-tiết-api)
3. [OpenAQ — chi tiết API](#3-openaq--chi-tiết-api)
4. [So sánh hai nguồn dưới góc nhìn MLOps](#4-so-sánh-hai-nguồn-dưới-góc-nhìn-mlops)
5. [Đề xuất bài toán cho mỗi nguồn](#5-đề-xuất-bài-toán-cho-mỗi-nguồn)
6. [Chiến lược dataset: train / validation / test / inference](#6-chiến-lược-dataset-train--validation--test--inference)

---

## 1. Hai nguồn dữ liệu

| | **Open-Meteo** | **OpenAQ** |
|---|---|---|
| Lĩnh vực | Thời tiết + khí hậu (và cả chất lượng không khí dạng mô hình) | Chất lượng không khí |
| Bản chất số liệu | **Đầu ra mô hình số**: reanalysis (ERA5) và dự báo (IFS, GFS, ICON...) trên lưới toàn cầu | **Số đo vật lý thật** từ trạm quan trắc mặt đất |
| Tổ chức | Open-Meteo (Thụy Sĩ), tổng hợp dữ liệu mở của ECMWF, DWD, NOAA, JMA, Météo-France... | OpenAQ (phi lợi nhuận, Mỹ), tổng hợp từ 173 nhà cung cấp |
| Đơn vị không gian | **Ô lưới** — điểm nào trên Trái Đất cũng có dữ liệu | **Trạm quan trắc** — chỉ nơi có trạm |
| Độ phân giải / quy mô | 9–11 km toàn cầu, 1–2 km khu vực | >1.000 trạm truy vấn được; 21.337 sensor PM2.5 đang hoạt động |
| Xác thực | Không cần key (bậc miễn phí) | Bắt buộc header `X-API-Key` |
| Giới hạn miễn phí | 600 request/phút, 5.000/giờ, 10.000/ngày | 60 request/phút, 2.000/giờ |
| Giấy phép | CC BY 4.0; **bậc miễn phí chỉ cho mục đích phi thương mại** | Theo từng nhà cung cấp — 12 loại giấy phép (§3.6) |
| Mốc dữ liệu sớm nhất | **1940-01-01** (ERA5) | **2016-01-01** qua API; **2006-11-13** qua S3 archive |
| Độ trễ số liệu | ERA5 trễ 6 ngày; mô hình dự báo gần như tức thời | Thường 1–3 giờ, một số nhà cung cấp trễ hơn |
| Số "API" gọi được | **11 API dữ liệu + 2 API phụ trợ** (§2.1) | **1 REST API gồm 39 endpoint + 1 kho S3 công khai** (§3.1) |
| Vai trò trong đồ án | 2 bài toán `wx_*` | 2 bài toán `aq_*` |

**Điểm mấu chốt cần nhớ**: Open-Meteo cho **dữ liệu dày và đầy đủ** (một request lấy được 12 địa điểm × 27 biến
× 1 tháng, không bao giờ thiếu ô lưới), còn OpenAQ cho **số đo thật nhưng thưa và lỗ chỗ** (mất sensor, mất giờ,
đơn vị khác nhau giữa các trạm, có giá trị âm và giá trị vô lý tới 1.680 µg/m³). Hai nguồn đại diện cho hai kiểu
dữ liệu tabular rất khác nhau — đó chính là lý do tốt để framework phải chạy được cả hai mà không sửa code.

---

## 2. Open-Meteo — chi tiết API

### 2.1 Có bao nhiêu API? — 11 API dữ liệu + 2 phụ trợ

Trả lời trực tiếp câu hỏi "mỗi nguồn có phải chỉ có 1 API để lấy?": **không**. Open-Meteo chia theo **host riêng
cho từng loại dữ liệu**, nhưng cú pháp tham số giống nhau hoàn toàn giữa các host. Dự án hiện **chỉ dùng 1
trong 11 API**.

| # | API | Host + đường dẫn | Nội dung | Dự án dùng? |
|---|---|---|---|---|
| 1 | **Historical Weather (Archive)** | `archive-api.open-meteo.com/v1/archive` | Reanalysis quá khứ (ERA5 và cộng sự) | ✅ **đang dùng** |
| 2 | Forecast | `api.open-meteo.com/v1/forecast` | Dự báo 16 ngày + quá khứ 93 ngày | ❌ |
| 3 | Historical Forecast | `historical-forecast-api.open-meteo.com/v1/forecast` | **Lưu trữ các bản dự báo đã phát** từ 2016 | ❌ (nên dùng — §6.4) |
| 4 | Previous Runs | `previous-runs-api.open-meteo.com/v1/forecast` | So sánh các lần chạy mô hình trước đó | ❌ |
| 5 | Ensemble | `ensemble-api.open-meteo.com/v1/ensemble` | Dự báo tổ hợp, tới 39 thành viên mỗi biến | ❌ |
| 6 | **Air Quality** | `air-quality-api.open-meteo.com/v1/air-quality` | PM2.5, PM10, AQI... từ mô hình CAMS | ❌ (dùng cho bài toán AQI) |
| 7 | Marine | `marine-api.open-meteo.com/v1/marine` | Sóng: chiều cao, chu kỳ, hướng | ❌ |
| 8 | Flood | `flood-api.open-meteo.com/v1/flood` | Lưu lượng sông (GloFAS) | ❌ |
| 9 | Climate (CMIP6) | `climate-api.open-meteo.com/v1/climate` | Kịch bản khí hậu tới 2050 | ❌ |
| 10 | Satellite Radiation | `satellite-api.open-meteo.com/v1/archive` | Bức xạ mặt trời từ ảnh vệ tinh, từ 1983 | ❌ |
| 11 | Seasonal Forecast | `seasonal-api.open-meteo.com/v1/seasonal` | Dự báo mùa, tới 217 ngày | ❌ |
| – | Geocoding (phụ trợ) | `geocoding-api.open-meteo.com/v1/search` | Tên địa danh → toạ độ | ❌ |
| – | Elevation (phụ trợ) | `api.open-meteo.com/v1/elevation` | Toạ độ → độ cao | ❌ |

Bản thương mại dùng host `customer-api.open-meteo.com` kèm `&apikey=...`, cú pháp y hệt.

### 2.2 Định dạng request và response

**Request**: luôn là `HTTP GET` với query parameter — không body, không header, không SDK.

```
GET https://archive-api.open-meteo.com/v1/archive
      ?latitude=21.0285,10.8231             ← nhiều địa điểm: ngăn bằng dấu phẩy
      &longitude=105.8542,106.6297
      &start_date=2026-09-01&end_date=2026-09-30
      &hourly=temperature_2m,precipitation  ← nhóm biến: hourly | daily | current | minutely_15
      &models=era5                          ← ghim mô hình (quan trọng, xem §2.5)
      &timezone=UTC
```

**Định dạng trả về** (tham số `format`, đã thử từng giá trị):

| `format` | Content-Type | Ghi chú |
|---|---|---|
| (không truyền) hoặc `json` | `application/json` | Mặc định |
| `csv` | `text/csv` | Có khối metadata ở đầu file rồi mới tới bảng |
| `xlsx` | `application/vnd.openxmlformats-...sheet` | File Excel nhị phân |
| `flatbuffers` | `application/octet-stream` | Nhỏ và nhanh nhất, cần thư viện giải mã |
| `protobuf` | – | **HTTP 400** — không hỗ trợ |

**Tham số đáng chú ý khác** (đã kiểm chứng): `timezone` (`UTC` hoặc tên IANA như `Asia/Bangkok`),
`timeformat=unixtime`, `temperature_unit=fahrenheit`, `wind_speed_unit`, `precipitation_unit`,
`cell_selection`, `past_days`, `forecast_days`, `tilt`/`azimuth` (bức xạ trên mặt phẳng nghiêng).

### 2.3 Phân tích cấu trúc JSON trả về

JSON của Open-Meteo ở **dạng cột (columnar)**: không phải mảng các bản ghi, mà là **các mảng song song cùng độ
dài, đánh chỉ số theo `time`**.

```jsonc
{
  "latitude": 21.05448,            // ⚠️ TÂM Ô LƯỚI, không phải toạ độ đã gửi (21.0285)
  "longitude": 105.807106,
  "generationtime_ms": 0.055,
  "utc_offset_seconds": 0,
  "timezone": "GMT",
  "timezone_abbreviation": "GMT",
  "elevation": 24.0,               // độ cao ô lưới (m)

  "hourly_units": {                // đơn vị của từng biến — nên lưu cùng dữ liệu
    "time": "iso8601",
    "temperature_2m": "°C",
    "precipitation": "mm"
  },
  "hourly": {                      // CÁC MẢNG SONG SONG, cùng độ dài
    "time":           ["2026-09-01T00:00", "2026-09-01T01:00", "..."],
    "temperature_2m": [27.7, 28.0, "..."],
    "precipitation":  [0.0, 0.0, "..."]
  }
}
```

**Năm đặc tính của cấu trúc này và hệ quả khi xử lý:**

1. **Mỗi nhóm thời gian là một cặp khoá** `<nhóm>` + `<nhóm>_units`. Các nhóm: `current` (một giá trị, kèm
   `interval` giây), `minutely_15`, `hourly`, `daily`, và `six_hourly`/`monthly` (riêng API Seasonal). Một request
   lấy được nhiều nhóm cùng lúc → response chứa nhiều cặp khoá.
2. **Nhiều địa điểm → JSON là một MẢNG** object theo đúng thứ tự toạ độ đã gửi (đã kiểm chứng: gửi 3 toạ độ →
   mảng 3 phần tử); một địa điểm → một object. Code phải xử lý cả hai dạng —
   [open_meteo.py:79](../framework/collection/connectors/open_meteo.py#L79) đang làm đúng. Response
   **không có `location_id`**, nên chỉ ghép lại được bằng **thứ tự**; gửi sai thứ tự thì dữ liệu gán sai địa điểm
   mà không có cách nào phát hiện.
3. **Nhiều mô hình → đổi TÊN CỘT** bằng hậu tố: `models=era5,era5_land` cho ra `temperature_2m_era5` và
   `temperature_2m_era5_land` (đã kiểm chứng). Lấy một mô hình thì tên cột không có hậu tố.
4. **Giá trị thiếu là `null`**, không phải mã lỗi. Biến không tồn tại trong mô hình đã chọn (ví dụ `albedo` chỉ có
   ở CERRA) trả về toàn `null`.
5. **Toạ độ trả về khác toạ độ đã gửi** (tâm ô lưới). Muốn gắn nhãn theo địa điểm thì phải tự giữ `entity_id`,
   không dựa vào `latitude`/`longitude` trong response.

**Quy ước mốc thời gian** (quan trọng khi gán nhãn): biến tức thời (`temperature_2m`) là giá trị **tại** mốc đó;
biến tích luỹ (`precipitation`, `rain`, `sunshine_duration`) là tổng của **giờ trước** mốc đó — dòng `01:00` chứa
lượng mưa khoảng `00:00–01:00`. Khớp đúng quy ước `event_time` của framework.

### 2.4 Danh mục biến theo từng API

Đếm từ trang tài liệu chính thức của từng API:

| API | `hourly` | `daily` | `current` | `minutely_15` | Khác | Số mô hình chọn được |
|---|---|---|---|---|---|---|
| Forecast | 65 | 63 | 15 | 32 | 27 mức áp suất | ~50 |
| **Historical Weather** | **72** | **54** | – | – | – | **7** |
| Historical Forecast | 70 | 73 | – | 32 | | ~50 |
| Ensemble | 69 | 41 | – | – | | 21 |
| **Air Quality** | **43** | – | 19 | – | | 2 (`cams_global`, `cams_europe`) |
| Marine | 23 | 11 | 22 | 3 | | nhiều |
| Flood | – | 7 | – | – | | 6 (GloFAS v3/v4) |
| Climate (CMIP6) | – | 19 | – | – | | 7 |
| Satellite Radiation | 16 | 5 | – | – | | 7 vệ tinh |
| Seasonal | 84 | 63 | – | – | 69 `monthly` | |

Dự án đang khai báo **27 biến `hourly`** của Historical Weather API
([wx_temp_reg/collection.yaml](../problems/wx_temp_reg/collection.yaml)) — khoảng **38% trong 72 biến có sẵn**.
Trong 72 biến đó, 23 biến là `*_spread` (độ phân tán, chỉ có khi `models=era5_ensemble`).

Nhóm biến đáng chú ý **chưa dùng** của Historical Weather API: `snow_depth`, **`boundary_layer_height`**
(chiều cao lớp xáo trộn khí quyển — liên quan trực tiếp tới nồng độ bụi), `wet_bulb_temperature_2m`,
`total_column_integrated_water_vapour`, `is_day`, `direct_normal_irradiance`, `global_tilted_irradiance`.

Air Quality API có 43 biến `hourly`, trong đó có **nhãn tính sẵn**: `us_aqi`, `european_aqi` và AQI theo từng
chất (`us_aqi_pm2_5`, `european_aqi_ozone`...), cùng `uv_index`, `dust`, `pm10_wildfires` và 6 loại phấn hoa
(chỉ châu Âu).

### 2.5 Phạm vi thời gian từng API — đo thật, không theo tài liệu

Cách đo: tìm kiếm nhị phân ngày sớm nhất **có giá trị không null**, và quét lùi để tìm ngày mới nhất **có giá trị
không null** (chứ không chỉ là ngày API chấp nhận). Đo tại Hà Nội (21.03, 105.85); các mô hình chỉ phủ châu Âu
thì đo tại Paris.

| API / mô hình | Ngày sớm nhất **có dữ liệu** | Ngày mới nhất **có dữ liệu** | Độ trễ | Phủ không gian |
|---|---|---|---|---|
| Archive — **ERA5-Seamless** (mặc định) | **1940-01-01** | `T-0` (2026-10-14) | 0 ngày | Toàn cầu |
| Archive — **ERA5** | **1940-01-01** | `T-6` (2026-10-08) | **6 ngày** | Toàn cầu |
| Archive — ERA5-Land | 1950-01-01 | `T-6` | 6 ngày | Đất liền |
| Archive — ERA5-Ensemble | 1940-01-01 | `T-6` | 6 ngày | Toàn cầu |
| Archive — CERRA | 1985-01-01 | **giữa 2021** (có 2021-06-01, hết trước 2021-12-01) | đã ngừng | **Chỉ châu Âu** |
| Archive — ECMWF IFS | 2016-12-31 | `T-0` | 0 ngày | Toàn cầu |
| Historical Forecast | 2016-12-31 | `T+2` | – | Toàn cầu |
| Satellite Radiation (seamless) | **1983-01-01** | `T-0` | 0 ngày | Theo vệ tinh |
| Satellite — EUMETSAT Sarah3 | 1983-01-01 | `T-3` | 3 ngày | Châu Âu, châu Phi |
| Air Quality (CAMS) | **2022-08-04** | `T+4` | – | Toàn cầu |
| Flood (GloFAS v4) | **1997-01-01** | ≥ `T+180` | – | Lưu vực sông |
| Marine | 2021-10-01 | `T+8` | – | Biển |
| Climate (CMIP6) | 1950-01-01 | **2050-12-31** (2051 → HTTP 400) | – | Toàn cầu |

**Giới hạn `forecast_days` / `past_days`** (đọc từ chính thông báo lỗi của API):

| API | `forecast_days` tối đa | `past_days` tối đa |
|---|---|---|
| Forecast | **16** | **93** |
| Air Quality | **7** | (dùng `start_date` để lấy xa hơn) |
| Marine | 16 | – |
| Flood | **366** | – |
| Ensemble | **36** | 93 |
| Seasonal | **217** | **408** |

> **Hệ quả quan trọng nhất của bảng trên**: `models=era5` (dự án đang ghim) chỉ có dữ liệu đến `T-6` — đó chính
> là lý do `maturity_lag: 7d` trong config. Nếu bỏ `models=era5`, ERA5-Seamless sẽ lấp khoảng trống bằng IFS:
> có dữ liệu đến hôm nay, nhưng **giá trị bị sửa lại** khi ERA5 chính thức về, làm nhãn đã gán trước đó không
> còn khớp. Giữ `models=era5` là quyết định đúng.

### 2.6 Giới hạn, chi phí quy đổi và giấy phép

- **Hạn mức miễn phí** (trang điều khoản): **< 10.000 call/ngày, 5.000/giờ, 600/phút**; hạn mức 300.000/tháng
  *hiện chưa được áp dụng* ("monthly limits are not enforced").
- **Một "API call" không bằng một HTTP request.** Request lấy **hơn 10 biến** hoặc **dài hơn 14 ngày** cho một
  địa điểm bị tính thành **nhiều call, theo phân số**:

  ```
  số call ≈ số_địa_điểm × max(1, số_biến / 10) × max(1, số_ngày / 14)
  ```

  Ví dụ của chính Open-Meteo: 2 tuần × 15 biến = 1,5 call; 4 tuần × 15 biến = 3,0 call.
  Áp vào dự án: **12 địa điểm × 27 biến × 31 ngày = 72 call cho 1 HTTP request**.
  Hàm `_weight` trong [open_meteo.py:40](../framework/collection/connectors/open_meteo.py#L40) đang tính đúng
  công thức này để giãn nhịp gọi.
- **Giấy phép**: dữ liệu theo **CC BY 4.0**, phải ghi nguồn. Bậc miễn phí **chỉ dùng cho mục đích phi thương
  mại** — phù hợp đồ án học tập, nhưng cần lưu ý nếu triển khai thật.

---

## 3. OpenAQ — chi tiết API

### 3.1 Có bao nhiêu cách lấy dữ liệu? — 1 REST API (39 endpoint) + 1 kho S3

| Kênh | Địa chỉ | Xác thực | Định dạng | Dùng khi nào |
|---|---|---|---|---|
| **REST API v3** | `https://api.openaq.org/v3` | `X-API-Key` **bắt buộc** | JSON | Thu thập theo chu kỳ, dữ liệu mới nhất |
| **S3 Open Data Archive** | `s3://openaq-data-archive` (HTTP công khai) | **không cần** | CSV.gz | Backfill khối lớn, lấy dữ liệu cũ |

Spec OpenAPI đầy đủ tại `https://api.openaq.org/openapi.json` (OpenAPI 3.1.0, 39 path, phiên bản 3.0.0).
Dự án hiện **chỉ dùng 1 trong 39 endpoint** để lấy dữ liệu (`/sensors/{id}/hours`), cộng 3 endpoint cho việc
chọn trạm.

### 3.2 Toàn bộ 39 endpoint, chia theo nhóm

**(a) Danh mục tra cứu — 15 endpoint** (hỏi một lần rồi cache):

| Endpoint | Số bản ghi thật | Nội dung |
|---|---|---|
| `/parameters`, `/parameters/{id}` | **43** | Danh mục thông số đo (§3.3) |
| `/countries`, `/countries/{id}` | **159** | Quốc gia + khoảng thời gian có dữ liệu |
| `/providers`, `/providers/{id}` | **173** | Nhà cung cấp dữ liệu |
| `/instruments`, `/manufacturers` (+ `/{id}`) | 30 / 13 | Thiết bị đo, nhà sản xuất |
| `/licenses`, `/licenses/{id}` | **12** | Giấy phép (§3.6) |
| `/owners`, `/owners/{id}` | >1.000 | Đơn vị sở hữu trạm |

**(b) Trạm (location) — 5 endpoint:**

- `GET /locations` — tìm trạm. Lọc theo `iso`, `countries_id`, `providers_id`, `parameters_id`, `instruments_id`,
  `manufacturers_id`, `licenses_id`, `monitor` (trạm tham chiếu hay cảm biến rẻ), `mobile`, và **theo không
  gian**: `coordinates` + `radius` (**tối đa 25 km**) hoặc `bbox`.
- `GET /locations/{id}` — chi tiết một trạm.
- `GET /locations/{id}/sensors` — **quan trọng**: `/locations` chỉ khai báo trạm *có* sensor nào; muốn biết sensor
  nào **còn sống** thì phải gọi vào đây (§3.5).
- `GET /locations/{id}/latest` — số đo mới nhất của mọi sensor trong trạm.
- `GET /locations/{id}/flags` — cờ chất lượng dữ liệu của trạm.

**(c) Chuỗi thời gian theo sensor — 17 endpoint.** Nhóm quan trọng nhất; đã gọi thử **toàn bộ** trên cùng một
sensor (PM2.5 của trạm Hawthorne, Mỹ) để so sánh:

| Endpoint | `period.label` | Kết quả đo thật | Ý nghĩa |
|---|---|---|---|
| `/sensors/{id}/measurements` | `raw` | 24 dòng/ngày | **Số đo thô** theo tần suất gốc của trạm |
| `/sensors/{id}/measurements/hourly` | `1 hour` | 24 dòng/ngày | Gộp thô → giờ |
| `/sensors/{id}/measurements/daily` | `1 day` | 31 dòng/tháng | Gộp thô → ngày |
| **`/sensors/{id}/hours`** | `1hour` | 24 dòng/ngày | **Giờ tính sẵn — dự án đang dùng** |
| `/sensors/{id}/hours/daily` | `1 day` | 31 dòng/tháng | Giờ → ngày |
| `/sensors/{id}/hours/monthly` | `1 month` | 10 dòng/10 tháng | Giờ → tháng |
| `/sensors/{id}/hours/yearly` | – | **HTTP 408 timeout** | Giờ → năm (quá nặng) |
| `/sensors/{id}/days` | `1day` | 31 dòng/tháng | Ngày tính sẵn |
| `/sensors/{id}/days/monthly`, `/days/yearly` | `1 month`, `1 year` | 10, 11 dòng | Rollup từ ngày |
| `/sensors/{id}/years` | `1year` | 10 dòng/10 năm | Năm tính sẵn |
| `/sensors/{id}/hours/hourofday` | `00`..`23` | **24 dòng** | **Nhịp theo giờ trong ngày** |
| `/sensors/{id}/hours/dayofweek`, `/days/dayofweek` | `1`..`7` | 7 dòng | Nhịp theo thứ |
| `/sensors/{id}/hours/monthofyear` | – | HTTP 408 | Nhịp theo tháng (quá nặng) |
| `/sensors/{id}/days/monthofyear` | `01`..`12` | 12 dòng | Nhịp theo tháng (bản nhẹ) |
| `/sensors/{id}` | – | 1 bản ghi | Metadata + `coverage` + `latest` + `summary` của sensor |
| `/sensors/{id}/flags` | – | 459 cờ | Cờ chất lượng của sensor |

Ba nhóm `hourofday` / `dayofweek` / `monthofyear` cho **đặc trưng khí hậu học sẵn dùng**, rất tiện làm feature mà
không phải tự tính. Ví dụ đo được: trạm Hà Nội 4946812 gần như phẳng theo giờ (30–37 µg/m³), còn trạm Mỹ 288
có đỉnh lúc 09h (9 µg/m³ so với 6 µg/m³ ban đêm).

**(d) Mới nhất & cờ — 2 endpoint**: `/parameters/{id}/latest` (ví dụ `/parameters/2/latest` → **21.337 sensor**
PM2.5 đang có số đo), `/sensors/{id}/flags`.

**Phân trang**: `limit` mặc định 100, **tối đa 1000** (vượt → HTTP 422, thông báo
`Input should be less than or equal to 1000`), `page` để lật trang. Khoảng thời gian: `datetime_from`/`datetime_to`
(endpoint theo giờ) hoặc `date_from`/`date_to` (theo ngày); nhận cả `2026-10-01` và `2026-10-01T11:19:38-06:00`.

### 3.3 Danh mục 43 thông số đo

Điểm cần cảnh giác nhất: **cùng một chất có nhiều `parameter_id` với đơn vị khác nhau.**

| Chất | Các id (đơn vị) |
|---|---|
| PM | `1` pm10, `2` pm25, `19` pm1, `19844` pm4 (đều µg/m³) |
| NO₂ | **`5` (µg/m³), `7` (ppm), `15` (ppb)** |
| CO | **`4` (µg/m³), `8` (ppm), `102` (ppb)** |
| SO₂ | **`6` (µg/m³), `9` (ppm), `101` (ppb)** |
| O₃ | **`3` (µg/m³), `10` (ppm), `32` (ppb)** |
| NO / NOx | `24`, `35`, `19843` / `23`, `27`, `19840` |
| Black carbon | `11` bc, cùng 6 bước sóng `19861`–`19866` (ng/m³) |
| Khí nhà kính | `21` co2 (ppm), `28` ch4 (ppm) |
| Đếm hạt | `33` ufp, `125` um003, `126` um010, `130` um025, `135` um100 (particles/cm³) |
| Khí tượng | `22` wind_direction, `34` wind_speed, `95` pressure, **`100` temperature (°C), `128` temperature (°F)**, `98` relativehumidity, `134` humidity |

`/parameters` còn phân loại `parameter_type` = `pollutant` \| `meteorological`.

Hàm `_drop_minority_units` trong [discovery.py](../framework/collection/discovery.py) xử lý đúng vấn đề này: mỗi
thông số chỉ giữ **một đơn vị chiếm đa số**, để một cột không trộn µg/m³ với ppm.

### 3.4 Phân tích cấu trúc JSON trả về

Mọi endpoint trả về **cùng một khung**: `meta` + `results[]` — dạng **dòng**, trái ngược hoàn toàn với dạng cột
của Open-Meteo.

```jsonc
{
  "meta": {
    "name": "openaq-api", "website": "/",
    "page": 1, "limit": 1000,
    "found": 192          // ⚠️ số nguyên khi nhỏ, nhưng là CHUỖI ">1000" khi lớn
  },
  "results": [ /* ... */ ]
}
```

**Một phần tử `results[]` của endpoint chuỗi thời gian** — đúng cho cả `measurements`, `hours`, `days`, `years`
(bốn schema `Measurement` / `HourlyData` / `DailyData` / `AnnualData` có **trường giống nhau hoàn toàn**):

```jsonc
{
  "value": 0.1,                                  // giá trị đã gộp trong kỳ
  "flagInfo": { "hasFlags": false },             // có bị gắn cờ chất lượng?
  "parameter": { "id": 8, "name": "co",
                 "units": "ppm", "displayName": null },
  "period": {
    "label": "1hour", "interval": "01:00:00",
    "datetimeFrom": { "utc": "2026-09-22T23:00:00Z",
                      "local": "2026-09-22T17:00:00-06:00" },
    "datetimeTo":   { "utc": "2026-09-23T00:00:00Z",   // ← framework dùng mốc NÀY làm event_time
                      "local": "2026-09-22T18:00:00-06:00" }
  },
  "coordinates": null,                           // thường null ở trạm cố định
  "summary": {                                   // phân phối trong kỳ
    "min": 0.1, "q02": 0.1, "q25": 0.1, "median": 0.1,
    "q75": 0.1, "q98": 0.1, "max": 0.1, "avg": 0.1, "sd": null
  },
  "coverage": {                                  // độ đầy đủ của kỳ
    "expectedCount": 1, "expectedInterval": "01:00:00",
    "observedCount": 1, "observedInterval": "01:00:00",
    "percentComplete": 100.0, "percentCoverage": 100.0,
    "datetimeFrom": { }, "datetimeTo": { }
  }
}
```

**Sáu điều cần nhớ về cấu trúc này:**

1. **Một phần tử = một sensor × một kỳ.** Muốn có bảng "một dòng = một trạm × một giờ" thì phải gọi riêng từng
   sensor rồi **pivot** — chính là việc `flatten` trong
   [openaq.py](../framework/collection/connectors/openaq.py) đang làm. Đây là khác biệt lớn nhất so với
   Open-Meteo: **12 trạm × 6 sensor = 72 request**, trong khi Open-Meteo lấy 12 địa điểm bằng **1 request**.
2. **`summary` và `coverage` là feature miễn phí.** Mỗi giá trị giờ kèm sẵn min/max/median/sd và tỉ lệ đầy đủ —
   dự án đang lấy `min`, `max`, `sd`, `coverage`, `flagged` thành các cột `<param>_<field>`.
3. **`period.datetimeTo` là mốc kết thúc kỳ** → dùng làm `event_time` thì dòng tại `t` chỉ chứa thông tin đã biết
   ở `t`, không rò rỉ tương lai.
4. **`meta.found` không đáng tin khi lớn**: trả về chuỗi `">1000"` thay vì số. Không dùng nó để tính số trang;
   phải lật trang tới khi trả về ít hơn `limit`.
5. **`percentComplete` có thể vượt 100.** Trạm Hà Nội 4946812 đo **5 phút/lần** nhưng khai báo
   `expectedInterval = 01:00:00`, nên một giờ có 12 số đo → `percentComplete = 1200`. Đã kiểm chứng: gọi
   `measurements` trong 3 giờ trả **36 dòng** ở trạm này, nhưng chỉ **3 dòng** ở 4 trạm khác. Mọi logic kiểm tra
   độ phủ **không được giả định giá trị này ≤ 100**.
6. **`value` có thể âm hoặc vô lý.** Metadata sensor 3724 cho `summary.min = -4.9` µg/m³; hai trạm Hàn Quốc có
   giá trị trung bình ngày tới **1.270** và **1.680** µg/m³. Đây là lý do cần `valid_min`/`valid_max` trong config nhãn.

**Cờ chất lượng** (`/sensors/{id}/flags`) là nguồn **nhãn do nhà cung cấp cấp sẵn**:

```jsonc
{
  "locationId": 288,
  "flagType": { "id": 4, "label": "Limits exceeded", "level": "ERROR" },
  "datetimeFrom": { "utc": "2016-03-11T16:00:00Z" },
  "datetimeTo":   { "utc": "2016-03-11T17:00:00Z" },
  "sensorIds": [], "note": "1 measurement..."
}
```

### 3.5 Phạm vi thời gian và độ phủ

| | REST API v3 | S3 Archive |
|---|---|---|
| Mốc sớm nhất toàn hệ thống | **2016-01-01T01:00Z** (Trung Quốc, Israel) | **2006-11-13** (trạm id 1) |
| Mốc mới nhất | gần thời gian thực (`T-0`, trễ 1–3 giờ) | **trễ ~5 ngày** (trạm 288: tới 2026-10-09) |
| Trạm đã ngừng hoạt động | **HTTP 404** — trạm id 1 đã bị gỡ khỏi API | **vẫn còn** dữ liệu |
| Việt Nam | 2016-01-30T01:00Z → `T-0`, 10 thông số | – |

Cấu trúc kho S3 và schema (đã tải file thật về kiểm tra):

```
s3://openaq-data-archive/records/csv.gz/locationid=<ID>/year=<YYYY>/month=<MM>/location-<ID>-<YYYYMMDD>.csv.gz

location_id,sensors_id,location,datetime,lat,lon,parameter,units,value
288,3724,Hawthorne-288,2016-03-06T13:00:00-07:00,40.733501,-111.871696,pm25,µg/m³,1.2
```

→ **Dạng dòng (long format)**, một file một ngày một trạm, `datetime` là **giờ địa phương kèm offset** (khác API
dùng UTC). Rất phù hợp để backfill vì không bị giới hạn 60 request/phút.

**Độ phủ thật của 12 trạm đang dùng** (đo bằng `/sensors/{id}/days`, cửa sổ 2024-10-01 → 2026-10-01, tối đa 731 ngày):

| Trạm | QG | Số ngày có dữ liệu | Lịch sử bắt đầu |
|---|---|---|---|
| 288, 807 | US | 731, 731 | 2016-03 |
| 3844, 3847 | TW | 625, 625 | 2016-12 |
| 2622556, 2622558 | KR | 716, 719 | 2024-03 |
| 2302, 2351 | PE | 617, 710 | – |
| 4946812, 4946813 | VN | **452, 445** | **2025-07-03** |
| 225457, 225394 | ZA | **46, 52** | 2021-04 (gần như mất dữ liệu trong cửa sổ này) |

> Đây là ràng buộc quyết định độ dài cửa sổ training ở §6: **hai trạm Việt Nam chỉ có dữ liệu từ 2025-07-03**, và
> hai trạm Nam Phi gần như rỗng trong 2 năm qua.

**Một cạm bẫy khi chọn trạm**: `/locations` khai báo một trạm có 6 thông số, nhưng kiểm tra chi tiết sensor thì
nhiều sensor đã chết từ lâu. Ví dụ trạm 701 (Thái Lan) khai 6 sensor, nhưng chỉ `pm25` và `pm10` còn số đo năm
2026; `no2`/`co` dừng từ 2020, `so2` từ 2019, `o3` từ 2022. **Phải gọi `/locations/{id}/sensors` và kiểm tra
`datetimeLast` của từng sensor.**

### 3.6 Giới hạn và giấy phép

- **Rate limit**: 60 request/phút (xác nhận qua header `X-Ratelimit-Limit: 60`, kèm `X-Ratelimit-Used`,
  `X-Ratelimit-Remaining`, `X-Ratelimit-Reset`), 2.000/giờ theo tài liệu.
- **Lỗi hay gặp**: `HTTP 408` khi rollup khoảng quá dài; `HTTP 500` **cố định** ở một số trạm (đã gặp ở
  `/locations/225567/sensors`, `225573`, `225576` — retry 6 lần vẫn lỗi, buộc phải bỏ qua trạm đó);
  `HTTP 404` khi sensor/trạm đã bị gỡ.
- **Giấy phép theo từng nhà cung cấp** — 12 loại và **không đồng nhất**:

| Giấy phép | Dùng thương mại | Phải ghi nguồn | Share-alike |
|---|---|---|---|
| US Public Domain, CC0 1.0 | ✅ | ❌ | ❌ |
| ODC-BY, CC BY 2.5/4.0, UK OGL, Taiwan OGDL, Poland GIOS, Mexico SINAICA, Japan Gov Standard | ✅ | ✅ | ❌ |
| CC BY-SA 4.0 | ✅ | ✅ | **✅** |
| **Australian Capital Territory (ACT) Government** | **❌ KHÔNG** | ✅ | ❌ |

→ Nếu mở rộng sang Úc (ACT) thì dữ liệu đó **không được dùng cho mục đích thương mại**. Trường `licenses` trong
`/locations/{id}` cho biết giấy phép của từng trạm — nên lưu vào metadata khi thu thập.

---

## 4. So sánh hai nguồn dưới góc nhìn MLOps

| Tiêu chí | Open-Meteo | OpenAQ |
|---|---|---|
| Hình dạng JSON | **Dạng cột** (mảng song song) | **Dạng dòng** (`results[]`) |
| Số request cho 12 thực thể × 1 tháng | **1** | **72** (12 trạm × 6 sensor) |
| Thiếu dữ liệu | Gần như không — mô hình luôn có giá trị | **Thường xuyên**: mất sensor, mất giờ, trạm chết |
| Giá trị bất thường | Hiếm | **Nhiều**: âm, tới 1.680 µg/m³, cờ "Limits exceeded" |
| Đơn vị | Thống nhất, khai báo trong `*_units` | **Không thống nhất giữa trạm** (ppm/ppb/µg/m³) |
| Số liệu bị sửa lại về sau | **Có** (ERA5-Seamless) — tránh bằng `models=era5` | Có (số liệu về muộn) |
| Metadata chất lượng kèm theo | Không | **Có sẵn**: `coverage`, `summary`, `flagInfo` |
| Backfill khối lớn | Dễ (1 request = 31 ngày × 12 địa điểm) | Chậm qua API; **nên dùng S3 archive** |
| Độ dài lịch sử dùng được | **86 năm** (từ 1940) | **~10 năm** qua API, bị chặn bởi tuổi từng trạm |

Với framework, hai nguồn này buộc phải hỗ trợ: (a) cả JSON dạng cột và dạng dòng, (b) cả dữ liệu đầy đủ và dữ
liệu lỗ chỗ phải loại dòng, (c) kiểm tra đơn vị theo từng thực thể, (d) chiến lược backfill khác nhau theo rate
limit của nguồn.

---

## 5. Đề xuất bài toán cho mỗi nguồn

### 5.1 Ba mức "nhãn có sẵn hay phải tự tạo"

Phân loại rõ ba mức, vì đây là câu hỏi quan trọng nhất khi chọn bài toán:

| Mức | Định nghĩa | Công sức | Ví dụ |
|---|---|---|---|
| **A. Nhãn sẵn trong API** | API trả về đúng cột nhãn đó; chỉ cần dịch chuyển về tương lai | Không | `weather_code`, `us_aqi`, `flagInfo.hasFlags` |
| **B. Nhãn suy ra bằng quy tắc công bố** | Áp công thức/ngưỡng của tổ chức uy tín (US EPA, WHO, WMO) lên giá trị đo | Thấp, hoàn toàn tự động, **có thể tái lập** | Nhóm AQI theo breakpoint EPA; "ngày có mưa" ≥ 1 mm của WMO |
| **C. Nhãn phải gán tay** | Cần người xem từng dòng rồi quyết định | Cao | *không dùng trong đồ án này* |

> **Toàn bộ 12 bài toán dưới đây chỉ dùng mức A và B.** Đây là điểm mạnh của việc chọn hai nguồn này: nhãn do
> bên uy tín cung cấp hoặc suy ra bằng ngưỡng công bố, **không có bước gán tay nào**, nên pipeline retrain tự
> động hoàn toàn. Đúng với yêu cầu trong [CLAUDE.md](../CLAUDE.md) §1: "không tự giả lập dữ liệu hay tự sinh
> nhãn bằng rule" — ở đây "rule" là tiêu chuẩn công bố của EPA/WHO/WMO, không phải quy tắc tự nghĩ ra.

**Quy ước chung cho mọi bài toán** (đã hiện thực trong framework):

- Mỗi dòng là một cặp (thực thể, điểm neo `t`); feature là quan sát **tại `t`**, nhãn tính trên cửa sổ tương lai
  **`(t, t + H]`** → không rò rỉ nhãn.
- Chỉ thu thập điểm neo đã "chín": `t ≤ T − H − maturity_lag`.
- Dòng không đủ dữ liệu xác định nhãn bị **loại**, không ghi nhãn tạm hay `null`.

### 5.2 Open-Meteo — 3 bài toán phân loại

| | **WX-C1 · `wx_code_clf`** | **WX-C2 · `wx_rain_clf`** ✅ đã có | **WX-C3 · `wx_aqi_clf`** |
|---|---|---|---|
| Loại | Multiclass (5 lớp) | Binary | Multiclass (4 lớp) |
| Câu hỏi | 24 giờ tới thuộc loại hiện tượng thời tiết nào? | 24 giờ tới có mưa đáng kể không? | 24 giờ tới mức AQI (Mỹ) thuộc nhóm nào? |
| Nhãn | `weather_code` tại `t+24h`, gộp nhóm | `sum(precipitation)` trên `(t, t+24h]` ≥ 1 mm | `us_aqi` tại `t+24h`, chia nhóm EPA |
| **Mức nhãn** | **A — nhãn sẵn** (mã WMO do API trả) | **B — ngưỡng WMO** 1 mm/ngày | **A — nhãn sẵn** (`us_aqi` do Open-Meteo tính) |
| API dùng | Historical Weather | Historical Weather | **Air Quality API** (API khác của cùng nguồn) |
| Phân bố thật đo được | quang 34,1% · nhiều mây 40,5% · mưa phùn 21,8% · mưa 3,5% · tuyết 0,2% | **43,9% dương** (12 địa điểm × 365 ngày) | Hà Nội: Unhealthy+ 42,9% · USG 31,7% · Moderate 25,5%; London: Good 87,5% · Moderate 12,5% |
| Lưu ý | Lớp tuyết rất ít (0,2%) → nên gộp vào "mưa" hoặc bỏ địa điểm ôn đới | Cân bằng tốt nhất trong 3 bài; ngưỡng 5 mm → 22,0%, 10 mm → 11,7% | **Chỉ có dữ liệu từ 2022-08-04** → cửa sổ training ngắn hơn hai bài kia |

**Phương án thay thế cho WX-C3** nếu muốn giữ nguyên một API: `wx_gust_clf` — gió giật cực đại 24 giờ tới
≥ 60 km/h (mức cảnh báo). Đo thật: **2,3% dương** (≥ 50 km/h: 6,0%; ≥ 40 km/h: 20,5%) → mất cân bằng nặng,
phù hợp để thử các kỹ thuật xử lý imbalance nhưng khó hơn.
Hoặc `wx_frost_clf` — sương giá (`temperature_2m_min` ≤ 0 °C): **2,9% dương** trên 12 địa điểm, nhưng tỉ lệ này
phụ thuộc hoàn toàn vào việc chọn địa điểm ôn đới.

### 5.3 Open-Meteo — 3 bài toán hồi quy

| | **WX-R1 · `wx_temp_reg`** ✅ đã có | **WX-R2 · `wx_rain_sum_reg`** | **WX-R3 · `wx_solar_reg`** |
|---|---|---|---|
| Câu hỏi | Nhiệt độ sau đúng 24 giờ là bao nhiêu? | Tổng lượng mưa 24 giờ tới là bao nhiêu? | Tổng bức xạ mặt trời 24 giờ tới là bao nhiêu? |
| Nhãn | `last(temperature_2m)` trên `(t, t+24h]` | `sum(precipitation)` trên `(t, t+24h]` | `sum(shortwave_radiation)` trên `(t, t+24h]` |
| Đơn vị | °C | mm | MJ/m² (hoặc Wh/m²) |
| **Mức nhãn** | **A** — giá trị đo, chỉ dịch thời gian | **B** — cộng dồn giá trị đo | **B** — cộng dồn giá trị đo |
| Phân bố thật đo được | nhãn trong **[4,8 ; 34,4] °C**, trung bình 23,5 (12 địa điểm, backfill 14 ngày); Tmax cả năm: [-8,3 ; 41,7] | **35,0% đúng bằng 0**, 21,1% trong (0;1) mm, 43,9% ≥ 1 mm, 11,7% ≥ 10 mm; trung bình 4,06 mm, max **361,5 mm** → lệch phải rất mạnh | trung bình **16,7**, p10 7,0, p90 24,4, max 32,8 MJ/m² |
| Metric đề xuất | MAE / RMSE | MAE trên log1p, hoặc tách 2 tầng (có mưa? → lượng mưa) | MAE / R² |
| Ứng dụng | Bài toán cơ sở, dễ kiểm chứng | Khó nhất — nhiều số 0, đuôi dài | Dự báo sản lượng điện mặt trời |

**Phương án thay thế**: `wx_et0_reg` — nhu cầu nước cây trồng (`et0_fao_evapotranspiration`): đo thật trung bình
**3,63 mm/ngày**, tối đa 9,80 → phân phối gọn, dễ học, có ý nghĩa nông nghiệp.

### 5.4 OpenAQ — 3 bài toán phân loại

| | **AQ-C1 · `aq_pm25_clf`** ✅ đã có | **AQ-C2 · `aq_aqi_cat_clf`** | **AQ-C3 · `aq_flag_clf`** |
|---|---|---|---|
| Loại | Binary | Multiclass (6 lớp, thực tế gộp 4) | Binary |
| Câu hỏi | PM2.5 trung bình 24 giờ tới có vượt ngưỡng không lành mạnh? | 24 giờ tới thuộc nhóm AQI nào? | Số đo giờ tới có bị nhà cung cấp gắn cờ lỗi? |
| Nhãn | `mean(pm25)` trên `(t, t+24h]` > 35,4 µg/m³ | `mean(pm25)` → nhóm theo breakpoint EPA | `flagInfo.hasFlags` tại `t+1h` |
| **Mức nhãn** | **B — ngưỡng US EPA** | **B — bảng breakpoint US EPA** | **A — nhãn sẵn**, do nhà cung cấp gắn |
| Phân bố thật đo được (12 trạm, 2 năm, 6.469 ngày-trạm) | **7,9% dương** ở 35,4 — quá lệch | Moderate 53,5% · Good 38,6% · USG 4,8% · Unhealthy 2,1% · Hazardous 0,9% · Very Unhealthy 0,2% | Chỉ 5/12 trạm có cờ: 459, 165, 25, 497, 628 cờ; 7 trạm còn lại **0 cờ** |
| **Khuyến nghị** | **Đổi ngưỡng sang 25 µg/m³ → 18,1% dương**, hoặc 15 (mốc WHO) → **40,6%** | Gộp còn 3–4 lớp: Good / Moderate / Unhealthy+ (38,6% / 53,5% / 8,0%) | Chỉ dùng với 5 trạm có cờ; nếu không thì chọn phương án thay thế dưới |

**Vì sao nên đổi ngưỡng AQ-C1**: ngưỡng 35,4 µg/m³ cho tỉ lệ lớp dương chỉ 7,9% trên toàn bộ 12 trạm, và riêng
hai trạm Mỹ/Đài Loan là **0,0%** — mô hình chỉ cần đoán "không vượt" là đã đúng >92%. Đo thật từng ngưỡng:

| Ngưỡng | Tỉ lệ ngày vượt | Nguồn ngưỡng |
|---|---|---|
| 15 µg/m³ | **40,6%** | WHO 2021, trung bình 24h |
| 25 µg/m³ | **18,1%** | WHO 2005 |
| 35,4 µg/m³ | 7,9% | US EPA — ranh giới "Unhealthy for Sensitive Groups" |
| 55,5 µg/m³ | 3,1% | US EPA — ranh giới "Unhealthy" |

**Phương án thay thế cho AQ-C3** (phổ quát hơn, áp dụng cho mọi trạm): `aq_spike_clf` — PM2.5 trung bình 24 giờ
tới **tăng ≥ 50%** so với 24 giờ vừa qua. Nhãn mức B, tính được ở mọi trạm, và là bài toán "phát hiện đợt ô
nhiễm" có giá trị thực tế hơn là dự đoán mức tuyệt đối.

### 5.5 OpenAQ — 3 bài toán hồi quy

| | **AQ-R1 · `aq_pm25_reg`** ✅ đã có | **AQ-R2 · `aq_pm25_peak_reg`** | **AQ-R3 · `aq_hours_exceed_reg`** |
|---|---|---|---|
| Câu hỏi | PM2.5 trung bình 24 giờ tới? | **Đỉnh** PM2.5 theo giờ trong 24 giờ tới? | 24 giờ tới có **bao nhiêu giờ** vượt ngưỡng WHO? |
| Nhãn | `mean(pm25)` trên `(t, t+24h]` | `max(pm25)` trên `(t, t+24h]` | `count(pm25 > 15)` trên `(t, t+24h]`, giá trị 0–24 |
| Đơn vị | µg/m³ | µg/m³ | số giờ (đếm) |
| **Mức nhãn** | **B** | **B** | **B — ngưỡng WHO** |
| Phân bố thật đo được | nhãn [2,1 ; 48,6], trung bình 13,1 (cửa sổ 1 tuần); 2 năm: trung bình 23,3, p50 12,0, p99 135,0 | **đỉnh ≈ 1,6–2,0× trung bình**: VN 45,3 (max 109), KR 20,8 (max 53), US 13,6 (max 61,2), PE 36,5 (max 101) | trung bình **18,8/24 giờ** (VN), 6,1 (KR), **1,4** (US), 18,5 (PE) |
| Metric đề xuất | MAE / RMSE | MAE; cân nhắc quantile loss (đỉnh quan trọng ở đuôi trên) | MAE; hoặc Poisson/Tweedie vì là biến đếm |
| Vì sao đáng làm | Bài toán cơ sở | Cảnh báo đỉnh quan trọng hơn trung bình với sức khoẻ | Biến đếm — kiểu nhãn thứ ba, buộc framework hỗ trợ objective khác |

AQ-R3 dùng được `summary.max` có sẵn trong mỗi bản ghi giờ (§3.4) nên **không tốn thêm request nào**.

### 5.6 Tổng hợp 12 bài toán

| Mã | `problem_id` | Nguồn | Loại | Mức nhãn | Trạng thái |
|---|---|---|---|---|---|
| WX-C1 | `wx_code_clf` | Open-Meteo | multiclass (5) | **A** | đề xuất mới |
| WX-C2 | `wx_rain_clf` | Open-Meteo | binary | B | ✅ đã hiện thực |
| WX-C3 | `wx_aqi_clf` | Open-Meteo (Air Quality API) | multiclass (4) | **A** | đề xuất mới |
| WX-R1 | `wx_temp_reg` | Open-Meteo | regression | A | ✅ đã hiện thực |
| WX-R2 | `wx_rain_sum_reg` | Open-Meteo | regression | B | đề xuất mới |
| WX-R3 | `wx_solar_reg` | Open-Meteo | regression | B | đề xuất mới |
| AQ-C1 | `aq_pm25_clf` | OpenAQ | binary | B | ✅ đã hiện thực (nên đổi ngưỡng) |
| AQ-C2 | `aq_aqi_cat_clf` | OpenAQ | multiclass (4) | B | đề xuất mới |
| AQ-C3 | `aq_flag_clf` | OpenAQ | binary | **A** | đề xuất mới (hạn chế: 5/12 trạm) |
| AQ-R1 | `aq_pm25_reg` | OpenAQ | regression | B | ✅ đã hiện thực |
| AQ-R2 | `aq_pm25_peak_reg` | OpenAQ | regression | B | đề xuất mới |
| AQ-R3 | `aq_hours_exceed_reg` | OpenAQ | regression (đếm) | B | đề xuất mới |

**Giá trị với framework**: 12 bài toán này phủ **binary, multiclass, regression liên tục và regression đếm** trên
**hai hình dạng JSON khác nhau** và **ba API khác nhau** — đủ rộng để chứng minh "thêm bài toán = thêm một thư
mục cấu hình". Riêng WX-C1 và AQ-C2 là **multiclass**, mà `config.py` hiện chỉ cho `TASK_TYPES = ("binary",
"regression")` → cần mở rộng, đúng như định hướng "task-type registry" ở [CLAUDE.md](../CLAUDE.md) §8.

---

## 6. Chiến lược dataset: train / validation / test / inference

### 6.1 Nguyên tắc chia tập

1. **Chia theo thời gian, không chia ngẫu nhiên.** Dữ liệu chuỗi thời gian có tự tương quan rất mạnh (PM2.5 giờ
   này gần như bằng giờ trước); chia ngẫu nhiên khiến điểm liền kề rơi vào cả train và test → **điểm test cao
   giả tạo**, mô hình sụp khi deploy.
2. **Ba tập liền khối, nối tiếp**: train (cũ nhất) → validation → test (mới nhất). Test là giai đoạn gần hiện tại
   nhất vì đó là phân phối mà model sẽ gặp khi deploy.
3. **Chừa khoảng đệm bằng `horizon` giữa các tập.** Nhãn của điểm neo cuối tập train được tính trên cửa sổ
   `(t, t+24h]`, lấn sang 24 giờ đầu tập validation → phải bỏ 24 giờ đầu mỗi tập sau, nếu không là rò rỉ.
4. **Biên chia dùng mốc ngày tròn và cố định** cho mọi thực thể, để mọi trạm/địa điểm chia cùng một mốc.
5. **Điểm neo mới nhất dùng được** = `T − horizon − maturity_lag`:
   - Open-Meteo (`H=24h`, `M=7d`) → `T-8` = **2026-10-06**
   - OpenAQ (`H=24h`, `M=24h`) → `T-2` = **2026-10-12**

### 6.2 Mốc cụ thể — Open-Meteo

Tính 70/15/15 theo ngày, cửa sổ kết thúc ở 2026-10-01 (mốc tròn tháng, nằm trong giới hạn `T-8`):

| Phương án | Cửa sổ | Train (70%) | Validation (15%) | Test (15%) | Test phủ đủ 1 vòng mùa? |
|---|---|---|---|---|---|
| 3 năm (tối thiểu) | 2023-10-01 → 2026-10-01 (1.096 ngày) | 2023-10-01 → 2025-11-06 (767 ng) | 2025-11-06 → 2026-04-19 (164 ng) | 2026-04-19 → 2026-10-01 (165 ng) | ❌ chỉ 0,45 năm |
| 6 năm | 2020-10-01 → 2026-10-01 (2.191 ngày) | 2020-10-01 → 2024-12-12 (1.533 ng) | 2024-12-12 → 2025-11-05 (328 ng) | 2025-11-05 → 2026-10-01 (330 ng) | ❌ 0,90 năm (gần đủ) |
| **10 năm (khuyến nghị)** | **2016-10-01 → 2026-10-01 (3.652 ngày)** | **2016-10-01 → 2023-10-01 (2.556 ng)** | **2023-10-01 → 2025-03-31 (547 ng)** | **2025-03-31 → 2026-10-01 (549 ng)** | **✅ 1,50 năm** |

> **Vì sao khuyến nghị 10 năm**: dữ liệu thời tiết có **chu kỳ mùa rất mạnh**. Với cửa sổ 3 năm, tập test chỉ trải
> 165 ngày (tháng 4 → tháng 10) — model được đánh giá **chỉ trên nửa năm nóng**, không biết nó hoạt động thế nào
> vào mùa đông. Chỉ cửa sổ 10 năm mới cho mỗi tập val/test phủ trên một vòng mùa đầy đủ. ERA5 có dữ liệu từ
> 1940 nên độ dài cửa sổ **không bị nguồn giới hạn**, chỉ bị giới hạn bởi hạn mức API (xem §6.5).
>
> Nếu buộc phải dùng cửa sổ ngắn, hãy báo cáo metric **tách theo mùa** thay vì một con số tổng, để không che mất
> việc model yếu ở một mùa cụ thể.

Với bài toán **WX-C3** (`wx_aqi_clf`, dùng Air Quality API): nguồn chỉ có từ **2022-08-04** → cửa sổ tối đa
2022-09-01 → 2026-10-01 (1.491 ngày): train 1.043 ngày (→ 2025-07-11), val 223 ngày (→ 2026-02-19),
test 225 ngày (→ 2026-10-01).

### 6.3 Mốc cụ thể — OpenAQ

Cửa sổ bị chặn bởi tuổi của trạm mới nhất (§3.5), nên có hai lựa chọn với đánh đổi rõ ràng:

| Phương án | Cửa sổ | Train (70%) | Validation (15%) | Test (15%) | Đánh đổi |
|---|---|---|---|---|---|
| **2 năm (khuyến nghị)** | **2024-10-01 → 2026-10-01 (730 ngày)** | **2024-10-01 → 2026-02-23 (510 ng)** | **2026-02-23 → 2026-06-12 (109 ng)** | **2026-06-12 → 2026-10-01 (111 ng)** | 2 trạm VN chỉ góp dữ liệu từ 2025-07; 2 trạm ZA gần như rỗng |
| 15 tháng (mọi trạm đều có dữ liệu) | 2025-07-03 → 2026-10-01 (455 ngày) | 2025-07-03 → 2026-05-17 (318 ng) | 2026-05-17 → 2026-07-24 (68 ng) | 2026-07-24 → 2026-10-01 (69 ng) | Tập val/test chỉ ~2 tháng — quá ngắn, nhiễu lớn |
| 5 năm (bỏ trạm mới) | 2021-10-01 → 2026-10-01 (1.826 ngày) | 2021-10-01 → 2025-04-01 (1.278 ng) | 2025-04-01 → 2025-12-30 (273 ng) | 2025-12-30 → 2026-10-01 (275 ng) | Chỉ 8/12 trạm đủ lịch sử, **mất cả 2 trạm Việt Nam** |

**Khuyến nghị**: dùng cửa sổ **2 năm** và chấp nhận số dòng không đều giữa các trạm (framework đã loại đúng
những dòng không đủ dữ liệu). Nếu cần cửa sổ dài hơn mà vẫn giữ trạm Việt Nam, hãy **chạy `discover-openaq` lại
với tiêu chí `--min-history-days` cao hơn** để thay hai trạm VN mới bằng trạm VN có lịch sử dài hơn — hiện mạng
OpenAQ ở Việt Nam có dữ liệu từ 2016-01-30, nên khả năng tìm được là có.

Lưu ý thêm: **hai trạm Nam Phi (225457, 225394) chỉ còn 46 và 52 ngày dữ liệu** trong 2 năm qua → nên loại khỏi
danh sách, vì chúng gần như không góp gì cho training mà vẫn tốn 12 request mỗi lần chạy.

### 6.4 Tập inference — và một vấn đề train/serve skew cần xử lý

Cần **phân biệt rõ hai thứ** mà cùng gọi là "inference":

**(a) Inference phục vụ dự đoán thật (serving)** — mô hình chạy trên dữ liệu **mới nhất** để dự đoán tương lai,
lúc này **chưa có nhãn**:

| Nguồn | Lịch chạy | Lấy gì | Số request/lần | Vấn đề |
|---|---|---|---|---|
| Open-Meteo | mỗi ngày 1 lần | Quan sát tại `t = T` (hôm nay) | 1 HTTP (≈32 call) | ⚠️ **ERA5 không có dữ liệu cho hôm nay** (trễ 6 ngày) |
| OpenAQ | mỗi ngày 1 lần (hoặc mỗi giờ) | Số đo giờ mới nhất của 12 trạm | 72 request ≈ 1,2 phút | Không có vấn đề — API gần thời gian thực |

> ### ⚠️ Vấn đề quan trọng nhất phát hiện được khi khảo sát
>
> Dự án **train trên ERA5** (`models=era5`), nhưng ERA5 **chỉ có dữ liệu đến `T-6`**. Khi model đã deploy và cần
> dự đoán cho **hôm nay**, không thể lấy feature từ ERA5 — buộc phải lấy từ một nguồn khác (ERA5-Seamless hoặc
> Forecast API), mà đó là **đầu ra của mô hình khác** (IFS thay vì ERA5), có phân phối khác với dữ liệu đã train.
> Đây chính là **train/serve skew**, và nó sẽ không lộ ra ở tập test (vì test cũng dùng ERA5) — chỉ lộ ra sau khi
> deploy, dưới dạng độ chính xác tụt không rõ nguyên nhân.
>
> **Ba cách xử lý, theo thứ tự nên ưu tiên:**
>
> 1. **Train trên Historical Forecast API** (`historical-forecast-api.open-meteo.com`, có dữ liệu từ 2016-12-31).
>    API này lưu lại **chính các bản dự báo đã phát trong quá khứ** — tức là feature lúc train giống hệt feature
>    mà Forecast API sẽ cho lúc serving. Đây là cách đúng về bản chất, và là lý do API này tồn tại.
> 2. **Giữ ERA5 để train, nhưng đo độ lệch**: thu thập song song cả hai nguồn cho cùng khoảng thời gian, tính
>    chênh lệch phân phối từng biến, và đưa phép hiệu chỉnh vào bước serving.
> 3. **Chấp nhận và chỉ dự đoán cho quá khứ** (`t = T-8`): hợp lệ về mặt học thuật, pipeline sạch, nhưng model
>    không còn giá trị dự báo thực tế.
>
> Khuyến nghị: với mục tiêu "dự báo 24 giờ tới" thì chọn (1). Nếu muốn giữ nguyên thiết kế hiện tại thì ghi rõ
> trong tài liệu rằng bài toán là "dự đoán hậu nghiệm trên dữ liệu reanalysis", và vẫn nên làm (2) để có số đo
> cụ thể về độ lệch.

**(b) Inference có nhãn — dùng để monitor và trigger retrain**: chính là luồng mà pipeline Data Collection hiện
tại đang chạy. Mỗi ngày lấy các điểm neo **vừa chín** (nhãn đã xác định), so dự đoán với nhãn thật để tính độ
chính xác thực tế và phát hiện drift:

| Nguồn | Lịch | Điểm neo lấy | Số dòng/lần | Chi phí |
|---|---|---|---|---|
| Open-Meteo | mỗi ngày 06:00 UTC | 24 điểm neo của ngày `T-8` | 12 địa điểm × 24 = **288 dòng** | 1 HTTP ≈ **32 call** (0,3% hạn mức ngày) |
| OpenAQ | mỗi ngày | 24 điểm neo của ngày `T-2` | ≈ 12 trạm × 24 × 85% ≈ **245 dòng** | **72 request** ≈ 1,2 phút |

→ Chi phí inference hằng ngày là **không đáng kể** với cả hai nguồn. Có thể chạy mỗi giờ nếu muốn
(OpenAQ: 72 request/giờ = 1,2 phút/giờ, vẫn dưới hạn mức 2.000/giờ).

### 6.5 Chi phí API cho mỗi lần training

**Open-Meteo** (quy đổi theo công thức §2.6; hạn mức 10.000 call/ngày):

| Kịch bản | Số HTTP request | Số "call" quy đổi | % hạn mức ngày |
|---|---|---|---|
| 12 địa điểm × 27 biến × **2 năm** | 24 | 1.722 | 17,2% |
| 12 địa điểm × 27 biến × **5 năm** | 59 | 4.233 | 42,3% |
| 12 địa điểm × 27 biến × **10 năm** (khuyến nghị) | 118 | **8.466** | **84,7%** |
| 12 địa điểm × 8 biến × 2 năm (bộ biến gọn) | 24 | 638 | 6,4% |
| 50 địa điểm × 27 biến × 5 năm | 59 | 17.637 | **176% — vượt hạn mức** |

> Phương án 10 năm dùng tới **84,7% hạn mức một ngày** → phải thu thập **một lần duy nhất rồi lưu vào S3**, và
> chia ra nhiều ngày nếu cần chạy lại. Đây đúng là lý do kiến trúc tách `landing/` (JSON gốc, bất biến) khỏi
> `observations/`: **thu thập một lần, gán nhãn lại bao nhiêu lần cũng được** mà không gọi lại API. Nếu muốn
> giảm chi phí, cắt bộ biến từ 27 xuống ~10 biến quan trọng nhất sẽ giảm gần 2,7 lần số call.

**OpenAQ** (60 request/phút, `limit` tối đa 1000 dòng/request):

| Kịch bản | Số request | Thời gian |
|---|---|---|
| 12 trạm × 6 sensor × **2 năm**, `/hours` | 1.296 | **≈ 22 phút** |
| 12 trạm × 6 sensor × 5 năm, `/hours` | 3.168 | ≈ 53 phút |
| 12 trạm × 1 sensor (chỉ pm25) × 2 năm | 216 | ≈ 3,6 phút |
| 12 trạm × 6 sensor × 2 năm, `/days` (nhãn theo ngày) | 72 | ≈ 1,2 phút |

→ Nếu cần cửa sổ dài hơn 5 năm hoặc nhiều trạm hơn, **dùng S3 archive thay cho API**: 12 trạm × 2 năm = 8.760
file CSV.gz, không bị rate limit (nhưng trễ ~5 ngày và phải tự gộp giờ).

### 6.6 Số dòng dataset thu được

| Cấu hình | Dòng/ngày | 2 năm | 5 năm | 10 năm |
|---|---|---|---|---|
| Open-Meteo 12 địa điểm, điểm neo **mỗi giờ** | 288 | 210.240 | 525.888 | ~1.051.000 |
| Open-Meteo 12 địa điểm, điểm neo **mỗi ngày** | 12 | 8.760 | 21.912 | 43.824 |
| OpenAQ 12 trạm, điểm neo **mỗi giờ** (độ phủ ~85%) | ~245 | 178.120 | 445.544 | – |
| OpenAQ 12 trạm, điểm neo **mỗi ngày** | 12 | 8.760 | 21.912 | – |

**Chọn tần suất điểm neo thế nào**: với horizon 24 giờ, các điểm neo cách nhau 1 giờ có cửa sổ nhãn **trùng nhau
23/24** → nhãn tự tương quan cực mạnh, số dòng lớn nhưng **lượng thông tin độc lập chỉ bằng bản theo ngày**.
Hai hệ quả:

- Đừng đọc con số 210.240 dòng như "210 nghìn mẫu độc lập"; số mẫu độc lập thực tế gần với 8.760.
- Nếu muốn tăng tốc training mà gần như không mất thông tin, có thể lấy điểm neo **mỗi 6 giờ** (giảm 4 lần số
  dòng). Giữ điểm neo mỗi giờ vẫn có ích khi muốn model học nhịp theo giờ trong ngày.

### 6.7 Checklist khi tạo một bài toán mới

1. Chọn API và biến → kiểm tra **phạm vi thời gian** của chính API/mô hình đó (§2.5, §3.5).
2. Chọn nhãn → xác định **mức A hay B** (§5.1); nếu mức B thì ghi rõ ngưỡng lấy từ tổ chức nào.
3. Đo **phân bố nhãn thật** trên ít nhất 1 năm trước khi chốt ngưỡng — đừng chốt theo cảm giác. Bài học từ
   AQ-C1: ngưỡng 35,4 µg/m³ "đúng tiêu chuẩn EPA" nhưng cho lớp dương chỉ 7,9%.
4. Đặt `maturity_lag` ≥ độ trễ thật của nguồn (Open-Meteo ERA5: 7 ngày; OpenAQ: 24 giờ).
5. Xác định cửa sổ train/val/test sao cho **val và test mỗi tập phủ ít nhất một vòng mùa** nếu dữ liệu có chu kỳ năm.
6. Kiểm tra **chi phí API** của cửa sổ đã chọn (§6.5) trước khi chạy backfill.
7. Kiểm tra **feature lúc serving có lấy được không** — bước hay bị bỏ qua nhất (§6.4).

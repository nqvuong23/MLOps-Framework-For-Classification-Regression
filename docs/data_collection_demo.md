# Data Collection: hướng dẫn chạy demo

Có hai cách chạy. Cả hai dùng chung code trong `framework/collection/` và cấu hình trong `problems/`.

| | Cách 1: CLI trên máy local | Cách 2: Airflow (Docker Compose) |
|---|---|---|
| Cần gì | Python (đã thử với 3.14) | Docker, file `.env` |
| Ghi dữ liệu ra | thư mục `_collection_out/` | S3, hoặc thư mục local nếu đặt `COLLECTION_BASE_URI` |
| Trạng thái | đã chạy thật cả 4 bài toán ngày 2026-10-02 (Windows, Python 3.14) | chưa chạy thật; file DAG mới được kiểm tra bằng stub của Airflow |

Kết quả mẫu của lần chạy ngày 2026-10-02: [data_collection_samples.md](data_collection_samples.md).

Các lệnh dưới đây viết cho PowerShell, chạy từ thư mục gốc của repo. Trên Linux/macOS: kích hoạt venv bằng `source .venv/bin/activate` và đặt biến môi trường bằng `export TEN=gia_tri`.

## Chuẩn bị

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r airflow.requirements.txt pytest

pytest tests/collection          # 42 passed, không cần mạng
```

Nếu PowerShell chặn `Activate.ps1`, chạy `Set-ExecutionPolicy -Scope Process RemoteSigned` rồi kích hoạt lại.

Hai bài toán `aq_*` cần API key của OpenAQ (đăng ký miễn phí tại https://explore.openaq.org/register):

```powershell
$env:OPENAQ_API_KEY = "<key của bạn>"
```

Hai bài toán `wx_*` (Open-Meteo) không cần key.

## Cách 1: chạy bằng CLI

### Bước 1. Xem các bài toán và cửa sổ thu thập

```powershell
python -m framework.collection list
python -m framework.collection window --problem wx_temp_reg
```

`list` in ra 4 bài toán. `window` cho biết một run theo lịch lúc này sẽ lấy điểm neo nào. Ví dụ chạy ngày 2026-10-02 với `wx_temp_reg` (horizon 24 giờ, `maturity_lag` 7 ngày):

```json
{
  "anchor_start": "2026-09-23T00:00:00+00:00",
  "anchor_end": "2026-09-24T00:00:00+00:00",
  "fetch_start": "2026-09-23T00:00:00+00:00",
  "fetch_end": "2026-09-24T23:00:00+00:00"
}
```

Run lấy 24 điểm neo của ngày 2026-09-23 và gọi API đến hết 2026-09-24 để đủ dữ liệu tính nhãn.

### Bước 2. Chạy hai bài toán Open-Meteo

```powershell
python -m framework.collection run --problem wx_temp_reg --base-uri ./_collection_out
python -m framework.collection run --problem wx_rain_clf --base-uri ./_collection_out
```

Mỗi lệnh mất khoảng 10 giây và kết thúc bằng một dòng tóm tắt:

```
[1/1] 20260923T0000Z_20260924T0000Z: quan sát=576 có nhãn=288 loại=0 label_mean=22.993056
Tổng số dòng training: 288 → ./_collection_out/wx_temp_reg/labeled
```

576 dòng quan sát = 12 thành phố × 48 giờ; 288 dòng có nhãn = 12 thành phố × 24 điểm neo.

### Bước 3. Chạy hai bài toán OpenAQ

```powershell
python -m framework.collection run --problem aq_pm25_reg --base-uri ./_collection_out
python -m framework.collection run --problem aq_pm25_clf --base-uri ./_collection_out
```

Mỗi lệnh mất khoảng 1 phút: OpenAQ phải gọi riêng từng sensor (55 sensor của 12 trạm) và giới hạn 60 request/phút. Một run theo lịch chỉ phụ trách 1 giờ điểm neo nên cho khoảng 10 đến 12 dòng có nhãn.

Danh sách trạm nằm trong `problems/_entities/openaq_stations.yaml` (12 trạm ở VN, KR, TW, PE, ZA, US). Muốn chọn lại trạm:

```powershell
python -m framework.collection discover-openaq --iso VN KR TW PE ZA US --max-stations 12 --per-country 2
```

### Bước 4. Backfill để có nhiều dữ liệu hơn

`--start` và `--end` là khoảng điểm neo `[start, end)` theo UTC.

```powershell
python -m framework.collection run --problem wx_temp_reg --start 2026-09-09 --end 2026-09-23 --base-uri ./_collection_out
python -m framework.collection run --problem wx_rain_clf --start 2026-09-09 --end 2026-09-23 --base-uri ./_collection_out
python -m framework.collection run --problem aq_pm25_reg --start 2026-09-23 --end 2026-09-30 --base-uri ./_collection_out
python -m framework.collection run --problem aq_pm25_clf --start 2026-09-23 --end 2026-09-30 --base-uri ./_collection_out
```

`end` phải đủ cũ để nhãn đã chốt: Open-Meteo cần `end` cách hiện tại ít nhất 8 ngày, OpenAQ ít nhất 2 ngày.

### Bước 5. Chạy lại để thấy tính idempotent

Chạy lại bất kỳ lệnh nào ở bước 2 đến 4: số dòng trong `labeled/` không đổi, không có dòng trùng.

## Đọc kết quả

Mỗi bài toán có một thư mục dưới `_collection_out/`:

```
_collection_out/wx_temp_reg/
  landing/window=20260923T0000Z_20260924T0000Z/part-00000.json.gz    JSON gốc từ API
  observations/event_date=2026-09-23/part-00000.parquet              bảng quan sát đã flatten
  labeled/event_date=2026-09-23/part-00000.parquet                   bảng training có nhãn
  _manifests/window=20260923T0000Z_20260924T0000Z.json               tóm tắt lần chạy
```

Xem bảng training:

```powershell
python -c "import pandas as pd; df = pd.read_parquet('_collection_out/wx_rain_clf/labeled'); print(df.shape); print(df[['entity_id','event_time','precipitation','label','label_raw','label_window_end']].head(10)); print(df['label'].value_counts())"
```

Đổi `labeled` thành `observations` để xem bảng quan sát. Khi đọc cả thư mục, pandas thêm cột `event_date` lấy từ tên partition.

Xem JSON gốc và manifest:

```powershell
python -c "import glob, gzip, json; f = sorted(glob.glob('_collection_out/wx_temp_reg/landing/*/*.json.gz'))[0]; print(f); print(json.dumps(json.load(gzip.open(f)))[:1500])"
Get-Content _collection_out/wx_temp_reg/_manifests/*.json -Encoding UTF8
```

## Cách 2: chạy bằng Airflow

Phần này chưa được chạy thật. Nếu gặp lỗi, xem log của `airflow-dag-processor` trước.

### Bước 1. Tạo file `.env`

```powershell
Copy-Item .env.example .env
```

Mở `.env` và kiểm tra:

| Biến | Giá trị |
|---|---|
| `AIRFLOW_PROJ_DIR` | `./airflow`. Thiếu biến này thì Compose mount `./dags` thay vì `./airflow/dags` và Airflow không thấy DAG nào. |
| `OPENAQ_API_KEY` | key OpenAQ |
| `S3_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | để ghi lên S3. Không để khoảng trắng sau giá trị. |
| `COLLECTION_BASE_URI` | tuỳ chọn, dùng khi chưa có AWS: đặt `/opt/airflow/logs/_collection_out` để dữ liệu ghi ra `airflow/logs/_collection_out/` trên máy host. |
| `AIRFLOW_UID` | chỉ cần trên Linux: kết quả của lệnh `id -u` |

`.env` đã nằm trong `.gitignore`. Key thật chỉ đặt ở `.env`; `.env.example` chỉ chứa placeholder.

### Bước 2. Dựng và khởi động

```powershell
docker compose up -d --build
docker compose ps
```

Lần đầu mất vài phút để build image và khởi tạo database. Giao diện ở http://localhost:8080, đăng nhập bằng `_AIRFLOW_WWW_USER_USERNAME` / `_AIRFLOW_WWW_USER_PASSWORD` trong `.env`.

### Bước 3. Kiểm tra DAG đã được nạp

```powershell
docker compose exec airflow-scheduler airflow dags list
docker compose exec airflow-scheduler airflow dags list-import-errors
```

Phải thấy 4 DAG: `wx_temp_reg_collect`, `wx_rain_clf_collect`, `aq_pm25_reg_collect`, `aq_pm25_clf_collect`.

### Bước 4. Bật và chạy một DAG

DAG mới tạo ở trạng thái tạm dừng.

```powershell
docker compose exec airflow-scheduler airflow dags unpause wx_temp_reg_collect
docker compose exec airflow-scheduler airflow dags trigger wx_temp_reg_collect
```

Trên giao diện, mở DAG và xem 5 task chạy lần lượt: `resolve_window`, `extract`, `flatten`, `build_labels`, `report`. Log của `report` in số dòng có nhãn; nếu lần chạy không gán được nhãn nào, log có một dòng `WARNING`.

Để chạy một khoảng điểm neo tuỳ chọn (tối đa 31 ngày), dùng "Trigger DAG" kèm cấu hình:

```json
{"start": "2026-09-22", "end": "2026-09-23"}
```

### Bước 5. Xem dữ liệu

Trên S3: `s3://<S3_BUCKET_NAME>/data-collection/<problem_id>/`, cùng cấu trúc thư mục như ở phần "Đọc kết quả".

## Lỗi thường gặp

| Thông báo | Nguyên nhân | Cách xử lý |
|---|---|---|
| `Thiếu S3_BUCKET_NAME (hoặc COLLECTION_BASE_URI)` | chạy CLI mà không chỉ nơi ghi | thêm `--base-uri ./_collection_out` |
| `Thiếu biến môi trường OPENAQ_API_KEY` | chưa đặt key | `$env:OPENAQ_API_KEY = "..."` |
| `danh sách entities rỗng` | `openaq_stations.yaml` không có trạm | chạy `discover-openaq` |
| `nguồn không trả quan sát nào` | khoảng thời gian quá mới, nguồn chưa có số liệu | lùi `--end`, hoặc kiểm tra trạm còn hoạt động |
| `discover-openaq` chạy rất lâu, log lặp `HTTP 500 ... thử lại` | OpenAQ trả lỗi cố định cho một số trạm; mỗi trạm tốn khoảng 1 phút retry rồi bị bỏ qua | chờ, hoặc đổi `--iso` sang nước khác |
| `discover-openaq --iso IN` không ra trạm nào | số liệu Ấn Độ trên OpenAQ đang về trễ hơn 48 giờ | tăng `--max-age-hours`, đồng thời tăng `maturity_lag` của bài toán cho tương ứng |
| Airflow không hiện DAG | `AIRFLOW_PROJ_DIR` sai, hoặc DAG lỗi import | xem bước 1 và bước 3 của cách 2 |

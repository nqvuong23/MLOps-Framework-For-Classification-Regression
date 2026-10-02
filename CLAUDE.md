# MLOps Framework cho dữ liệu dạng bảng

## 1. Bối cảnh & Mục tiêu

- **Đồ án**: xây dựng một **MLOps framework cho dữ liệu dạng bảng (tabular)**, tự động hoá toàn bộ vòng đời Machine Learning: data collection --> validation --> transform & cleaning --> labeling --> feature engineering --> trainning --> register --> deploy --> monitor --> retrain.
- **Phạm vi bài toán**: hai loại — **classification** và **regression**. Cùng một code pipeline phải chạy được cả hai.
- **Định nghĩa "framework"**: thêm một bài toán mới = thêm **một thư mục cấu hình** trong `problems/`,
  **không sửa code pipeline**. Tri thức của bài toán (tên cột, ngưỡng, nhãn, lịch chạy) nằm trong file khai báo;
  code trong `framework/` không được chứa tên cột hay hằng số của bài toán cụ thể nào.
- **Nguồn gốc**: phát triển tiếp từ một đồ án MLOps trước đó (pipeline end-to-end viết cứng cho một bài toán duy nhất).
  Giai đoạn đầu **giữ nguyên kiến trúc tổng thể** của đồ án đó (mục 2, 3) và tổng quát hoá dần từng khối.
- **Dữ liệu**: lấy từ **nguồn mở, cập nhật liên tục, có nhãn do bên uy tín cung cấp** — không tự giả lập dữ liệu
  hay tự sinh nhãn bằng rule. Hiện dùng hai nguồn: **Open-Meteo** và **OpenAQ** (mục 4).
- **Trạng thái (2026-10-02)**: mới hiện thực xong khối đầu tiên là **Data Collection**. Các khối còn lại
  (cleaning, feature engineering, training, deployment, monitoring) chưa có trong framework — làm tiếp theo thứ tự đó.

---

## 2. Kiến trúc tổng thể

```
   Nguồn dữ liệu mở (REST API, JSON)            Open-Meteo · OpenAQ
                    │
                    │  DAG <problem_id>_collect — lịch theo từng nguồn            [ĐÃ CÓ]
                    ▼
      Data Collection:  extract --> flatten --> build_labels
                    │
   ┌────────────────▼──────────────────────────────────────────────┐
   │  AWS S3 (data lake + artifact store)                          │
   │  data-collection/<problem_id>/{landing, observations, labeled}│
   │  + prefix của các khối sau, mlflow-artifacts                  │
   └────────────────┬──────────────────────────────────────────────┘
                    │  Data Processing: validate --> clean --> feature engineering   [KẾ THỪA]
                    │  Model Training: HPO + train --> MLflow Registry --> promotion gate
                    ▼
      API Gateway + Lambda ──► CodePipeline ──► CodeBuild
                      (pull model --> BentoML build --> Trivy scan --> push ECR)
                    │
      CodeDeploy ──► ECS Fargate (BentoML service)
                    │
      Prometheus ──► Grafana   |   Drift detection (Evidently AI)
                                        └──► vượt ngưỡng --> trigger retrain
```

- **[ĐÃ CÓ]**: đã viết theo hướng framework, điều khiển bằng cấu hình.
- **[KẾ THỪA]**: thiết kế lấy từ đồ án trước; code gốc viết cứng cho một bài toán nên phải viết lại
  theo hướng cấu hình trước khi dùng (hạn chế cụ thể ở mục 9).

---

## 3. Các thành phần kế thừa từ kiến trúc cũ

Mô tả ở mức thiết kế. Đây là điểm xuất phát, chưa phải code của framework.

### 3.1 Data Processing
- Airflow DAG tuyến tính: extract --> validate --> clean --> validate --> feature engineering --> validate --> lưu S3.
- **Validate nhiều tầng** bằng Great Expectations (raw / processed / features).
- **Fail-soft**: dòng không đạt được tách sang prefix riêng và gửi cảnh báo, pipeline tiếp tục với dòng sạch.
- **Spark** chạy `local[*]` ngay trong Airflow worker, đọc/ghi S3 qua `s3a://`.
- Với framework: đầu vào của khối này là lớp `observations/` / `labeled/` do Data Collection sinh ra.

### 3.2 Model Training
- Airflow DAG chạy định kỳ **hoặc** bị trigger khi phát hiện drift.
- Gộp dữ liệu training theo tuần để không phải quét quá nhiều prefix S3 mỗi lần train.
- Time-based split --> **Optuna** tune siêu tham số --> **XGBoost** --> log **MLflow** (nested runs).
- **Promotion gate**: model mới chỉ được register khi metric tốt hơn model hiện tại một khoảng `PROMOTION_DELTA`.
- MLflow: backend store = RDS PostgreSQL, artifact store = S3.
- Sau khi promote: tạo **reference snapshot** (mẫu dữ liệu training) cho bước drift detection.
- Với framework: objective, metric và tiêu chí promote phải chọn theo `task_type`
  (classification / regression), không viết cứng.

### 3.3 Model Deployment
- Airflow POST tới **API Gateway --> Lambda --> CodePipeline**.
- **CodeBuild**: lấy model từ MLflow Registry --> `bentoml build` --> `bentoml containerize` --> **Trivy scan** --> push **ECR**.
- **CodeDeploy --> ECS Fargate**: BentoML service, endpoint `POST /predict`.

### 3.4 Model Observation
- **Performance**: Prometheus scrape `/metrics` của BentoML --> Grafana.
- **Data drift**: Airflow DAG dùng **Evidently AI** so sánh reference snapshot với dữ liệu gần đây,
  sinh HTML report lên S3; vượt ngưỡng --> cảnh báo và trigger DAG training qua Airflow REST API v2.

---

## 4. Feature: Data Collection

**Mục đích**: theo chu kỳ, gọi API của nguồn dữ liệu, lấy JSON, biến thành **bảng training có nhãn đã xác định**.
Khối này **không** làm cleaning hay feature engineering — đó là các feature kế tiếp.

### 4.1 Hai nguồn dữ liệu

| | Open-Meteo | OpenAQ |
|---|---|---|
| Dữ liệu | Thời tiết theo giờ dạng lưới toàn cầu (reanalysis ERA5) | Chất lượng không khí theo giờ, **số đo thật** từ trạm quan trắc |
| API | `archive-api.open-meteo.com/v1/archive` | `api.openaq.org/v3`, gọi theo từng sensor: `/sensors/{id}/hours` |
| Xác thực | Không cần key | Header `X-API-Key`, đọc từ biến môi trường `OPENAQ_API_KEY` |
| Giới hạn | 600/phút, 5.000/giờ, 10.000/ngày (tính theo trọng số request) | 60 request/phút, 2.000/giờ |
| Dạng JSON | Dạng cột: các mảng song song theo `time`; nhiều toạ độ trong một request | Dạng dòng: `results[]`, mỗi phần tử là một số đo của một sensor |
| Thực thể | 12 thành phố ([open_meteo_locations.yaml](problems/_entities/open_meteo_locations.yaml)) | Trạm quan trắc ([openaq_stations.yaml](problems/_entities/openaq_stations.yaml)) |
| Độ trễ số liệu | ERA5 trễ ~6 ngày (đo ngày 2026-10-02); ghim `models=era5` để giá trị không bị sửa lại | Số đo có thể về muộn từ nhà cung cấp |

### 4.2 Bốn bài toán (2 nguồn × 2 loại)

| `problem_id` | Nguồn | Loại | Nhãn — tính trên cửa sổ `(t, t + 24h]` | Lịch DAG |
|---|---|---|---|---|
| `wx_temp_reg` | Open-Meteo | regression | `temperature_2m` tại `t + 24h` | mỗi ngày 06:00 UTC |
| `wx_rain_clf` | Open-Meteo | binary | tổng `precipitation` ≥ 1 mm | mỗi ngày 06:30 UTC |
| `aq_pm25_reg` | OpenAQ | regression | trung bình PM2.5 (cần ≥ 75% số giờ có số đo) | mỗi giờ, phút 5 |
| `aq_pm25_clf` | OpenAQ | binary | trung bình PM2.5 > 35,4 µg/m³ | mỗi giờ, phút 35 |

### 4.3 Cách hoạt động

- **Chỉ thu thập điểm neo có nhãn đã "chín"**. Mỗi dòng là một cặp (thực thể, thời điểm neo `t`): feature là
  quan sát tại `t`, nhãn tính trên cửa sổ tương lai `(t, t + H]`. Một run tại `T` lấy các điểm neo
  `t ∈ [T − H − M − interval, T − H − M)`, với `H` = horizon của nhãn, `M` = `maturity_lag`
  (thời gian chờ nguồn chốt số liệu: Open-Meteo 7 ngày, OpenAQ 24 giờ).
- **DAG** `<problem_id>_collect`, 5 task: `resolve_window` --> `extract` --> `flatten` --> `build_labels` --> `report`.
  [data_collection_dag.py](airflow/dags/data_collection_dag.py) là DAG factory: quét `problems/*/collection.yaml`
  và sinh mỗi bài toán một DAG.
- **Ba lớp dữ liệu** trên S3, dưới `s3://$S3_BUCKET_NAME/$S3_PREFIX_COLLECTION/<problem_id>/`:
  - `landing/window=<key>/` — JSON nguyên bản từ API (gzip), không sửa.
  - `observations/event_date=YYYY-MM-DD/` — bảng đã flatten: `entity_id`, `event_time` (UTC), thuộc tính thực thể, mỗi biến một cột.
  - `labeled/event_date=YYYY-MM-DD/` — bảng training: các cột trên + `label`, `label_raw`, `label_coverage`,
    `label_window_end`, `source`, `window_key`.
  - `_manifests/window=<key>.json` — tóm tắt từng lần chạy.
- **Idempotent**: mỗi bước thay đúng khoảng thời gian của run trong file ngày, nên run theo giờ, run theo ngày,
  backfill và rerun không tạo dòng trùng.
- **Quy ước `event_time`**: dòng tại `t` chỉ chứa thông tin đã biết ở thời điểm `t`. Đại lượng trung bình/tích luỹ
  theo giờ gắn vào mốc **kết thúc** của giờ đó (OpenAQ dùng `period.datetimeTo.utc`).
- Dòng không đủ dữ liệu để xác định nhãn bị loại khỏi `labeled/`; không bao giờ ghi nhãn tạm hay `null`.

### 4.4 Code & cấu hình

- [framework/collection/](framework/collection/) — `config.py` (đọc + kiểm tra cấu hình), `window.py` (tính cửa sổ),
  `connectors/` (mỗi nguồn một class `extract` + `flatten`), `labeling.py` (gán nhãn tổng quát),
  `storage.py` (S3 hoặc thư mục local qua fsspec), `pipeline.py` (các bước, dùng chung cho DAG và CLI),
  `discovery.py` (chọn trạm OpenAQ).
- [problems/](problems/)`<problem_id>/collection.yaml` — khai báo `source` (type, entities, variables),
  `collection` (schedule, interval, frequency, horizon, maturity_lag) và `label` (target, agg, threshold, min_coverage).
- Thêm nguồn mới: viết một connector và đăng ký trong `connectors/__init__.py`.
- CLI: `python -m framework.collection {list | window | run | discover-openaq}`; `run --start --end` để backfill,
  `--base-uri <thư mục>` để ghi ra local thay vì S3.
- Test: `pytest tests/collection` — không cần mạng, không cần S3.
- Phụ thuộc: DAG import `send_alert` và `airflow_failure_callback` từ `airflow/plugins/alert_utils.py`;
  `docker-compose.yaml` phải mount `./framework` và `./problems` vào `/opt/airflow/`.

### 4.5 Trạng thái kiểm chứng (2026-10-02)

- Đã chạy thật end-to-end với **Open-Meteo** (run theo lịch và backfill 40 ngày), ghi ra thư mục local; nhãn khớp khi tính tay.
- **Chưa kiểm chứng**: gọi OpenAQ thật (connector mới test bằng payload dựng theo OpenAPI spec), ghi lên S3 thật,
  và parse/chạy DAG trong Airflow thật.
- `openaq_stations.yaml` **đang rỗng** --> hai DAG `aq_*` sẽ lỗi cho tới khi chạy `discover-openaq` (cần API key).
- Ngưỡng 35,4 µg/m³ phụ thuộc trạm được chọn; xem tỉ lệ lớp dương sau backfill, nếu quá thấp thì đổi sang 15 (mốc WHO).

---

## 5. Tech Stack

| Lớp | Công nghệ |
|---|---|
| Orchestration | Apache Airflow **3.2.2** (CeleryExecutor + Redis + Postgres metadata DB) |
| Data collection | requests, pandas, pyarrow, fsspec / s3fs, PyYAML |
| Data quality | Great Expectations **1.18.1** |
| Processing | PySpark (local mode), pandas |
| ML | XGBoost, Optuna, scikit-learn |
| Experiment / Registry | MLflow (backend RDS PostgreSQL + artifact S3) |
| Serving | BentoML |
| CI/CD | AWS CodePipeline + CodeBuild + CodeDeploy, Trivy, ECR |
| Runtime | AWS ECS Fargate, API Gateway, Lambda |
| Storage | AWS S3 (data lake), AWS RDS PostgreSQL (MLflow backend) |
| Monitoring | Prometheus, Grafana, Evidently AI **0.4.36** |
| Alerting | Slack webhook (`slack-sdk`) + SMTP email |
| Test | pytest |
| Local dev | Docker Compose |

---

## 6. Cấu trúc repository

- [framework/](framework/) — code dùng chung của framework; hiện có `collection/`.
- [problems/](problems/) — mỗi bài toán một thư mục cấu hình; `_entities/` chứa danh sách thực thể dùng chung.
- [airflow/dags/](airflow/dags/) — `data_collection_dag.py` (DAG factory); DAG của các khối sau đặt ở đây.
- [airflow/plugins/](airflow/plugins/) — `alert_utils.py` (Slack/email + `airflow_failure_callback`).
- [tests/](tests/) — `collection/`.
- [docs/](docs/) — `plan.md` (khảo sát hai nguồn + thiết kế Data Collection),
  `improvement.md` (thiết kế framework: contract, operator tổng quát, label store, DAG factory).
- [docker-compose.yaml](docker-compose.yaml), `airflow.Dockerfile`, `airflow.requirements.txt` — Airflow stack.
- [.env.example](.env.example) — danh sách biến môi trường (chỉ placeholder, không chứa giá trị thật).

Tài liệu cũ cần lưu ý nếu được mang sang: phần chọn bài toán trong `improvement.md` §1 và toàn bộ `datasets.md`
(đề xuất EIA, NYC 311) **đã bị thay thế** bởi `plan.md` — không làm theo.

---

## 7. Cấu hình & quy ước code

- Mọi cấu hình hạ tầng qua **environment variable** (`.env`, không commit): `S3_BUCKET_NAME`, `S3_PREFIX_COLLECTION`,
  `OPENAQ_API_KEY`, AWS credentials, Slack/SMTP. Cấu hình của bài toán nằm trong `problems/<problem_id>/`.
- Airflow 3.x: dùng `logical_date` (không `execution_date`), `airflow.providers.standard.operators.python`,
  REST API **v2**, `on_failure_callback` thay cho `email_on_failure`. Run trigger tay có thể không có
  `logical_date` --> dùng `dag_run.run_after`.
- Khoảng thời gian một run xử lý chỉ được suy ra từ `logical_date`, không dùng `now()` hay Airflow Variable.
- **XCom chỉ chở đường dẫn và số đếm**, không chở DataFrame; dữ liệu đi qua S3.
- S3 scheme: `s3a://` cho Spark/Hadoop, `s3://` cho boto3/pandas/fsspec.
- Comment & docstring viết **tiếng Việt**.
- Alert: `send_alert(subject, message, level, context)` với level `info | warning | error | success`.
- Code mới trong `framework/` phải có test trong `tests/`.

---

## 8. Định hướng thiết kế framework

Chi tiết và tài liệu tham khảo ở `docs/improvement.md`. Các ý chính, chưa hiện thực:

- **Dataset Contract (YAML)**: khai báo cột, `semantic_type`, ràng buộc, mức xử lý lỗi; từ contract sinh ra
  expectation suite, cleaning operator và schema của serving API.
- **Operator tổng quát** chọn theo `semantic_type`, không theo tên cột.
- **Transformer artifact fit-once / apply-many**: thống kê (scaler, bounds, vocab) fit lúc training, log cùng model;
  pipeline batch và serving chỉ transform.
- **Feature engineering khai báo**, tính theo event time, chỉ dùng dữ liệu `≤ t`.
- **Task-type registry**: `binary | multiclass | regression` --> objective, metric, tiêu chí promote.
- **DAG factory** cho mọi khối, theo mẫu của Data Collection.

---

## 9. Hạn chế của kiến trúc kế thừa (phải xử lý khi tổng quát hoá)

- **Viết cứng cho một bài toán**: schema, expectation suite, cleaning rule và danh sách feature nằm trong code;
  danh sách feature còn bị lặp ở training, drift detection và serving.
- **XCom chở DataFrame** giữa các task: không scale, phình metadata DB.
- **Con trỏ incremental lưu trong Airflow Variable**: không idempotent, không backfill được.
- **Spark local mode** trong Airflow worker: không phân tán thật, tạo/stop session lặp lại mỗi task.
- **Rò rỉ thống kê**: scaler fit trên từng batch thay vì dùng scaler của lần training.
- **HPO đánh giá trên tập test** và promote bằng **một metric duy nhất**; chưa có integration test trước khi deploy.
- **Trivy `--exit-code 0`**: scan chỉ để audit, không chặn image có lỗ hổng CRITICAL.
- **Secrets**: `.env.example` của đồ án cũ chứa credential thật — không mang sang; dùng placeholder
  và chuyển dần sang Secrets Manager / SSM.
- Chưa có CI cho code, chưa có IaC.

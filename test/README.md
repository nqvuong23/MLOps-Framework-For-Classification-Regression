# Thực hành tiền xử lý — bài toán WX-C1

> Dự đoán **nhóm hiện tượng thời tiết sau 24 giờ** (quang / nhiều mây / mưa phùn / mưa) từ trạng thái khí quyển
> hiện tại. Nguồn: Open-Meteo, mô hình ERA5. Kế hoạch chi tiết: [docs/wx_code_clf_preprocessing_plan.md](../docs/wx_code_clf_preprocessing_plan.md).

Mỗi bước là **một file chạy độc lập**: đọc thư mục của bước trước, ghi thư mục của mình, in ra những gì cần quan
sát. Không có Airflow, không có S3 — mọi thứ nằm trong `test/data/`.

```
collection.py ──► 1_raw/        JSON gốc, mỗi tháng 1 file (.json.gz)
flatten.py    ──► 2_flat/       observations.parquet — 1 dòng = (thành phố, giờ)
cleaning.py   ──► 3_clean/      cleaned.parquet + quarantine.parquet + report.json
labeling.py   ──► 4_labeled/    labeled.parquet — thêm label = nhóm thời tiết tại t + 24h
validation.py ──► 5_validation/ report.json — ĐẠT thì mới cho đi tiếp
feature_engineering.py ──► 6_features/  train / val / test.parquet + artifacts/
```

`config.py` chứa toàn bộ tri thức của bài toán (12 thành phố, 27 biến, khoảng vật lý, ánh xạ nhãn) để 6 file kia
chỉ chứa logic. Quy tắc làm sạch trong code đánh số R1–R6 theo **thứ tự chạy**, khác cách đánh số C1–C6 trong kế
hoạch: kiểm tra nhất quán được chuyển xuống cuối, sau bước nội suy (lý do ở mục 7).

Kết quả lần chạy mặc định (12 thành phố, 2023-10 → 2026-10): 315.648 dòng quan sát → 8 dòng bị cách ly →
315.344 dòng có nhãn (32,2% / 41,2% / 22,7% / 3,8%) → train 105.120 / val 104.792 / test 104.544 dòng × 100 đặc trưng.

## 1. Cài đặt

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r test/requirements.txt
```

## 2. Chạy demo — 6 lệnh theo thứ tự

```powershell
python test/collection.py              # ~6 phút: 12 thành phố × 3 năm (2023-10 → 2026-10)
python test/flatten.py
python test/cleaning.py
python test/labeling.py
python test/validation.py
python test/feature_engineering.py
```

Chạy thử nhanh (~1 phút) với 2 thành phố: `python test/collection.py --cities hanoi,tokyo`, rồi 5 lệnh còn lại
như trên. Chạy lại `collection.py` là an toàn: tháng nào đã tải (cùng danh sách thành phố) thì bỏ qua.

## 3. Mỗi bước — nên quan sát gì

| Bước | Quan sát |
|---|---|
| **collection** | Chi phí API tính theo **trọng số** (12 thành phố × 27 biến × 31 ngày ≈ 72 "call" cho 1 HTTP request). Mở một file JSON để thấy **dạng cột**: các mảng song song theo `time`. |
| **flatten** | `weather_code` đang là **số nguyên** dù bản chất là biến phân loại. Toạ độ API trả về là **tâm ô lưới ERA5**, không phải toạ độ đã gửi. |
| **cleaning** | Bảng 6 quy tắc và số ô mỗi quy tắc bắt được; **đẳng thức bảo toàn** `đầu vào = sạch + cách ly`. Dữ liệu ERA5 rất sạch nên gần như không có gì để sửa — xem mục 4 để thấy các quy tắc hoạt động. |
| **labeling** | Dòng bị loại vì không xác định được nhãn (24 giờ cuối, mốc tương lai bị cách ly). Phân bố nhãn theo thành phố và **baseline phải vượt** (persistence, lớp đông nhất). |
| **validation** | 15 kiểm tra, chia 3 nhóm. Quan trọng nhất là **V2 luỹ đẳng**: chạy làm sạch lần hai trên bảng sạch không được sửa thêm dòng nào — đó là bằng chứng không bản ghi nào lọt lưới. |
| **feature_engineering** | 100 đặc trưng chia 10 nhóm; biên train/val/test và **vùng đệm 24h**; prior khí hậu học **chỉ fit trên train**; tự kiểm tra rò rỉ bằng cách tính lại đặc trưng độc lập. |

## 4. Thử chế độ cấy lỗi

Dữ liệu ERA5 sạch nên khó thấy các quy tắc làm sạch làm việc. Cờ `--inject-errors N` cấy lỗi **đã biết trước**
vào một bản sao — chữ trong cột số, giá trị ngoài khoảng, mã WMO sai, dòng trùng, dòng bị xoá, lỗ hổng dài... —
rồi so số lỗi cấy vào với số lỗi bị bắt:

```powershell
python test/cleaning.py --inject-errors 200
python test/labeling.py
python test/validation.py
```

Học xong thì **chạy lại `python test/cleaning.py` không có cờ** để các bước sau dùng dữ liệu thật.

## 5. Chạy test

```powershell
pytest test/test_steps.py -v
```

11 test, không cần mạng: ánh xạ nhãn đủ mọi mã WMO, ngưỡng không vỡ với float32, chỉ nội suy lỗ hổng ngắn,
làm sạch bảo toàn dòng và luỹ đẳng, nhãn ghép đúng mốc t + 24h, đặc trưng không nhìn tương lai, chia tập có vùng đệm.

## 6. Xem dữ liệu

```powershell
python -c "import pandas as pd; df = pd.read_parquet('test/data/6_features/train.parquet'); print(df.shape); print(df.iloc[:3, :8])"
python -c "import pandas as pd; q = pd.read_parquet('test/data/3_clean/quarantine.parquet'); print(q[['entity_id','event_time','reject_reason']])"
```

## 7. Những lỗi thật đã gặp khi viết các bước này

Đây là phần đáng đọc nhất — mỗi lỗi đều **không làm chương trình báo lỗi**, chỉ âm thầm làm sai dữ liệu:

1. **Thứ tự quy tắc làm sạch.** Bản đầu kiểm tra `rain ≤ precipitation` *trước* khi nội suy. Nội suy hai cột độc
   lập lại sinh ra vi phạm mới mà không ai kiểm tra. Kiểm tra **V2 luỹ đẳng** bắt được: lần chạy thứ hai vẫn sửa
   thêm 9 dòng. Sửa: đưa kiểm tra nhất quán xuống sau nội suy.
2. **Ngưỡng và float32.** Sau khi ép kiểu, 1,3 mm thành 1,2999999523 nên phép `< 1,3` cho kết quả sai — 160 dòng
   (trên dữ liệu 2 thành phố) bị suy sai mã thời tiết, V6 tụt còn 99,70%. Sửa: đặt ngưỡng ở **điểm giữa** hai mức
   đo (1,25) → V6 lên 100%.
3. **Category số nguyên mất kiểu khi ghi Parquet.** `weather_code` dạng category số được ghi thành `int64`, đọc lại
   ra `float64`. Sửa: dùng category **chuỗi** (`"0"`, `"51"`, ...).
4. **One-hot che mất giá trị thiếu.** `get_dummies` biến ô rỗng thành hàng toàn số 0 — trông như dữ liệu hợp lệ.
   Sửa: giữ nguyên rỗng để dòng đó bị loại đúng cách.
5. **Dữ liệu thật cũng có lỗi.** ERA5 trả `soil_moisture_0_to_7cm = −0,004` (âm, phi vật lý) suốt 8 giờ ở Tokyo
   (2025-08-17). Quy tắc khoảng vật lý bắt được và 8 dòng đó bị cách ly.

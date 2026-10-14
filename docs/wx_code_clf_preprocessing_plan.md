# WX-C1 `wx_code_clf` — Kế hoạch tiền xử lý

> **Bài toán**: phân loại hiện tượng thời tiết trong 24 giờ tới, nguồn Open-Meteo.
> **Phạm vi tài liệu**: chỉ bàn **quy trình tiền xử lý** — từ thu thập tới khi có bảng feature sẵn sàng đưa vào
> training. Không bàn chọn thuật toán, HPO, serving.
>
> **Căn cứ số liệu**: mọi con số trong file này được đo thật bằng cách gọi Open-Meteo Archive API ngày
> 2026-10-14 — 5 năm × 12 thành phố cho phân bố nhãn (525.888 mốc giờ) và 1 năm × 12 thành phố cho
> 27 biến feature (105.120 dòng). Mốc thời gian là UTC.
>
> Nguồn gốc bài toán: [data_sources_api_analysis.md](data_sources_api_analysis.md) §5.2 (WX-C1).

**Mục lục**

1. [Phân tích bài toán](#1-phân-tích-bài-toán)
2. [Chu kỳ training và dataset tích luỹ](#2-chu-kỳ-training-và-dataset-tích-luỹ)
3. [Phân tích dataset](#3-phân-tích-dataset)
4. [Quy trình tiền xử lý](#4-quy-trình-tiền-xử-lý)
5. [Artifact và quy tắc chống rò rỉ](#5-artifact-và-quy-tắc-chống-rò-rỉ)
6. [Checklist nghiệm thu](#6-checklist-nghiệm-thu)

---

## 1. Phân tích bài toán

### 1.1 Nhiệm vụ của model

> Cho biết trạng thái khí quyển **tại thời điểm `t`** ở một địa điểm, hãy dự đoán **loại hiện tượng thời tiết
> tại thời điểm `t + 24 giờ`** ở chính địa điểm đó.

Đây là bài toán **phân loại đa lớp (multiclass), một nhãn**, trên dữ liệu bảng có cấu trúc chuỗi thời gian theo
từng thực thể.

### 1.2 Nhãn — và một phát hiện quyết định cách tiếp cận

Nhãn gốc là `weather_code`: mã WMO do Open-Meteo trả về sẵn. Theo cách phân loại ở
[data_sources_api_analysis.md](data_sources_api_analysis.md) §5.1 thì đây là **nhãn mức A — có sẵn trong API,
không cần gán tay**.

**Đo thật 5 năm × 12 thành phố (525.888 mốc giờ): ERA5 chỉ sinh ra 13 mã**, và **không bao giờ** sinh mã sương mù
(45–48), mưa rào (80–82) hay dông (95–99):

| Mã | Ý nghĩa | Tỉ lệ | Mã | Ý nghĩa | Tỉ lệ |
|---|---|---|---|---|---|
| 0 | Trời quang | 19,36% | 61 | Mưa nhẹ | 2,23% |
| 1 | Phần lớn quang | 12,50% | 63 | Mưa vừa | 1,33% |
| 2 | Có mây rải rác | 10,63% | 65 | Mưa to | 0,11% |
| 3 | Nhiều mây | 31,04% | 71 | Tuyết nhẹ | 0,07% |
| 51 | Mưa phùn nhẹ | 17,49% | 73 | Tuyết vừa | 0,06% |
| 53 | Mưa phùn vừa | 3,97% | 75 | Tuyết dày | 0,02% |
| 55 | Mưa phùn dày | 1,18% | | | |

> ### ⚠️ Phát hiện quan trọng nhất: `weather_code` là **hàm xác định** của 3 biến khác trong cùng dòng
>
> Suy ngược lại `weather_code` chỉ từ `precipitation`, `snowfall`, `cloud_cover` cho kết quả **khớp
> 105.081/105.120 = 99,96%** (39 dòng lệch duy nhất nằm ở ranh giới tuyết nhẹ/tuyết vừa). Ngưỡng đo được chính xác:
>
> | Điều kiện | Mã |
> |---|---|
> | `snowfall > 0` | 71 (0,07–0,14 cm) · 73 (0,21–0,77) · 75 (0,84–2,17) |
> | `precipitation = 0`, `cloud_cover` ∈ [0,19] / [20,49] / [50,79] / [80,100] | 0 / 1 / 2 / 3 |
> | `precipitation` ∈ [0,1; 0,4] / [0,5; 0,9] / [1,0; 1,2] mm/h | 51 / 53 / 55 |
> | `precipitation` ∈ [1,3; 2,4] / [2,5; 7,5] / ≥ 7,6 mm/h | 61 / 63 / 65 |
>
> **Bốn hệ quả bắt buộc phải xử lý:**
>
> 1. **Nhãn không mang thêm thông tin ngoài 3 biến đó.** Bài toán thực chất là "dự báo lượng mưa và lượng mây
>    sau 24 giờ, rồi áp bảng ngưỡng". Phải ghi rõ điều này trong báo cáo, nếu không sẽ bị hiểu nhầm là model
>    học được một khái niệm phức tạp hơn thực tế.
> 2. **Có một baseline mạnh và rất đáng làm**: huấn luyện 2 model hồi quy (`precipitation`, `cloud_cover` tại
>    `t+24h`) rồi áp bảng ngưỡng để suy ra mã. Nếu model phân loại không thắng được baseline này thì nên dùng
>    baseline.
> 3. **Ranh giới lớp là ngưỡng cứng** → các dòng sát ngưỡng (ví dụ mưa 0,4 so với 0,5 mm/h) về bản chất là
>    *không phân biệt được*. Đừng kỳ vọng accuracy cao ở vùng biên; nên báo cáo thêm ma trận nhầm lẫn để thấy
>    lỗi chủ yếu rơi vào lớp **liền kề** (vốn ít nghiêm trọng).
> 4. **Dùng chính công thức này làm kiểm tra chất lượng nhãn** ở bước validation (§4.5, kiểm tra V6) — nếu tỉ lệ
>    khớp tụt xuống dưới ~99% thì nguồn đã đổi cách sinh mã, phải dừng pipeline.

**Gộp nhóm nhãn.** Giữ 13 lớp là không nên: 3 lớp tuyết cộng lại chỉ 0,15%. Gộp theo nhóm hiện tượng WMO:

| Nhãn dùng để train | Mã gốc | Tỉ lệ đo thật (12 thành phố, 5 năm) |
|---|---|---|
| `0_quang` — trời quang tới ít mây | 0, 1 | **31,86%** |
| `1_nhieu_may` — nhiều mây, không mưa | 2, 3 | **41,67%** |
| `2_mua_phun` — mưa phùn | 51, 53, 55 | **22,64%** |
| `3_mua` — mưa | 61, 63, 65 | **3,67%** |
| `4_tuyet` — tuyết | 71, 73, 75 | **0,15%** |

**Khuyến nghị về lớp tuyết**: 0,15% là quá hiếm để học. Hai lựa chọn, chọn một và ghi vào config:

- **(a) Gộp `4_tuyet` vào `3_mua`** → bài toán 4 lớp (31,86% / 41,67% / 22,64% / 3,82%). Đơn giản, khuyến nghị
  cho lần đầu.
- **(b) Giữ 5 lớp** nhưng chỉ khi tập thực thể có thành phố ôn đới; đo thật thì chỉ 3/12 thành phố từng có tuyết
  (Tokyo 0,31%, New York 1,30%, London 0,20%), 9 thành phố còn lại **không có dòng tuyết nào**.

### 1.3 Input và output của model

**Output**: một trong 4 (hoặc 5) nhãn ở trên. Nên trả thêm **vector xác suất** của từng lớp — vì ranh giới là
ngưỡng cứng nên xác suất hữu ích hơn nhãn cứng khi cảnh báo.

**Input**: một dòng = một cặp (thực thể, điểm neo `t`), gồm 4 khối:

| Khối | Nguồn | Ví dụ cột | Ghi chú |
|---|---|---|---|
| Khoá | pipeline | `entity_id`, `event_time` | Không đưa vào model, chỉ để tra cứu |
| Thuộc tính thực thể | file entities | `latitude`, `longitude`, `elevation`, `country` | Tĩnh theo thực thể |
| Quan sát tại `t` | API, 27 biến | `temperature_2m`, `cloud_cover`, `precipitation`, ... | Giá trị tại đúng `t` |
| Đặc trưng dẫn xuất | bước feature engineering (§4.6) | lag, trung bình trượt, biến thiên áp suất, mã hoá chu kỳ | Chỉ dùng dữ liệu `≤ t` |

**Ràng buộc tuyệt đối**: mọi cột input chỉ được chứa thông tin **đã biết tại thời điểm `t`**. Nhãn lấy ở `t+24h`.
Không có ngoại lệ.

### 1.4 Phạm vi: một thành phố hay nhiều thành phố?

Đây là câu hỏi thiết kế quan trọng nhất. Số liệu đo thật cho thấy **12 thành phố có phân bố nhãn rất khác nhau**:

| Thành phố | `0_quang` | `1_nhieu_may` | `2_mua_phun` | `3_mua` | `4_tuyet` | Persistence | Đoán lớp đông nhất |
|---|---|---|---|---|---|---|---|
| hanoi | 26,28% | 44,92% | 23,94% | 4,86% | 0% | 51,38% | 44,92% |
| ho_chi_minh | 20,64% | 47,96% | 26,22% | 5,18% | 0% | 52,05% | 47,96% |
| bangkok | 29,63% | 46,73% | 20,52% | 3,11% | 0% | 54,16% | 46,73% |
| **singapore** | **8,70%** | 45,89% | **38,38%** | 7,04% | 0% | 50,20% | 45,89% |
| jakarta | 18,63% | 42,10% | 34,76% | 4,50% | 0% | 47,94% | 42,10% |
| **mumbai** | **52,84%** | **14,82%** | 26,83% | 5,51% | 0% | **73,37%** | 52,84% |
| tokyo | 41,42% | 38,03% | 16,64% | 3,60% | 0,31% | 43,48% | 41,42% |
| sydney | 47,57% | 31,45% | 18,96% | 2,01% | 0% | 46,68% | **47,57%** |
| london | 30,46% | 51,43% | 16,54% | 1,37% | 0,20% | 46,77% | **51,43%** |
| new_york | 43,79% | 40,44% | 11,60% | 2,87% | 1,30% | 42,58% | **43,79%** |
| sao_paulo | 34,10% | 43,41% | 19,51% | 2,99% | 0% | 49,20% | 43,41% |
| nairobi | 28,31% | 52,91% | 17,78% | 1,00% | 0% | 55,69% | 52,91% |
| **Gộp 12** | **31,86%** | **41,67%** | **22,64%** | **3,67%** | **0,15%** | **51,12%** | **41,67%** |

**Khuyến nghị: dùng cả 12 thành phố, một model chung**, với lý do dựa trên chính số liệu trên:

1. **Khác biệt giữa thành phố là tín hiệu học được, không phải nhiễu.** Singapore 8,7% trời quang so với Mumbai
   52,8% — chênh lệch này gắn với vĩ độ, mùa, khí hậu, tức là **học được từ đặc trưng thực thể**
   (`latitude`, `elevation`, prior khí hậu học). Đây đúng là bài kiểm tra mà framework cần: cùng một pipeline
   chạy cho nhiều thực thể không đồng nhất.
2. **Gấp 12 lần dữ liệu**: 1.051.776 dòng cho 10 năm thay vì 87.648 dòng.
3. **Pipeline đã thu thập sẵn 12 thành phố** — không tốn thêm chi phí API.
4. **Lớp hiếm cần gộp nhiều thành phố mới đủ mẫu**: lớp `3_mua` ở Nairobi chỉ 1,00%; gộp 12 thành phố cho 3,67%.

**Hai điều bắt buộc đi kèm khi làm đa thành phố:**

- **Đánh giá phải tách theo từng thành phố**, không chỉ một con số tổng. Model có thể đạt accuracy cao nhờ học
  tốt Mumbai (dễ, persistence 73,4%) mà rất kém ở Tokyo (khó, persistence 43,5%).
- **Dùng macro-F1 làm metric chính**, không dùng accuracy. Lý do ở §1.5.

**Nếu muốn chạy thử nhanh lần đầu**, hãy chọn **Hà Nội**: phân bố cân đối nhất (26/45/24/5), có đủ 4 nhóm,
persistence 51,4% sát mức trung bình, và nhịp mùa rõ để kiểm chứng feature (xem §3.2).
**Tránh lấy Mumbai làm thành phố thử nghiệm** — persistence 73,4% khiến mọi model trông có vẻ tốt.

### 1.5 Baseline bắt buộc phải vượt

Đây là phần hay bị bỏ qua nhất, và với bài toán này thì **rất dễ tự lừa mình**:

| Baseline | Cách làm | Kết quả đo thật (12 thành phố, 5 năm) |
|---|---|---|
| **Đoán lớp đông nhất** | Luôn trả `1_nhieu_may` | **accuracy 41,67%** |
| **Persistence** | Trả đúng nhóm đang quan sát tại `t` | **accuracy 51,12%** |
| Persistence theo từng thành phố | | từ 42,58% (New York) tới 73,37% (Mumbai) |
| **Hồi quy rồi áp ngưỡng** | 2 model dự báo `precipitation` + `cloud_cover` tại `t+24h`, áp bảng §1.2 | *chưa đo — nên làm* |

> **Ngưỡng chấp nhận**: model phân loại phải vượt **51,12% accuracy** (persistence gộp) **và** vượt persistence
> **ở từng thành phố riêng lẻ**. Lưu ý ở Sydney, London, New York thì "đoán lớp đông nhất" còn **tốt hơn**
> persistence — nên ngưỡng của mỗi thành phố là `max(persistence, lớp đông nhất)` của chính thành phố đó.
>
> Vì accuracy bị chi phối bởi 2 lớp lớn (73,5% tổng), **metric chính phải là macro-F1** để lớp `3_mua` (3,67%)
> có trọng số ngang các lớp khác. Accuracy chỉ dùng để so với baseline.

---

## 2. Chu kỳ training và dataset tích luỹ

### 2.1 Nguyên tắc

- **Lần 1 (khởi tạo)**: lấy một khối lịch sử dài. Khuyến nghị **10 năm**.
- **Lần N (N ≥ 2)**: **không lấy lại từ đầu**. Dataset lần N = dataset lần N−1 **+ phần dữ liệu mới** phát sinh
  từ lần training trước tới lần này.

Điều này khả thi vì kiến trúc đã tách `landing/` (JSON gốc, bất biến) khỏi các lớp sau: **thu thập một lần, gán
nhãn và sinh feature lại bao nhiêu lần cũng được** mà không gọi lại API.

### 2.2 Ví dụ cụ thể — chu kỳ 1 tháng, lần 1 vào 2026-10-01

| Lần | Ngày training | Cửa sổ dữ liệu | Số ngày | Số dòng (điểm neo giờ, 12 thành phố) | Call API **mới** |
|---|---|---|---|---|---|
| 1 | 2026-10-01 | 2016-10-01 → 2026-10-01 | 3.652 | 1.051.776 | **8.466** |
| 2 | 2026-11-01 | 2016-10-01 → 2026-11-01 | 3.683 | 1.060.704 | **72** |
| 3 | 2026-12-01 | 2016-10-01 → 2026-12-01 | 3.713 | 1.069.344 | **72** |
| 4 | 2027-01-01 | 2016-10-01 → 2027-01-01 | 3.744 | 1.078.272 | 72 |
| 5 | 2027-02-01 | 2016-10-01 → 2027-02-01 | 3.775 | 1.087.200 | 72 |
| 6 | 2027-03-01 | 2016-10-01 → 2027-03-01 | 3.803 | 1.095.264 | 72 |

Đúng như mô tả: dataset lần 3 = dataset lần 1 (10 năm) + dữ liệu hai tháng 2026-10 và 2026-11.

**Chi phí** (hạn mức Open-Meteo: 10.000 call/ngày, công thức quy đổi ở
[data_sources_api_analysis.md](data_sources_api_analysis.md) §2.6):

| Kịch bản | HTTP request | Call quy đổi | % hạn mức ngày |
|---|---|---|---|
| Lần 1 — 10 năm × 27 biến × 12 địa điểm | 118 | **8.466** | **84,7%** |
| Lần 1 — 10 năm × 15 biến | 118 | 4.703 | 47,0% |
| Lần 1 — 5 năm × 27 biến | 59 | 4.233 | 42,3% |
| Lần N — thêm 1 tháng × 27 biến | 1 | **72** | 0,7% |

> **Cảnh báo về lần 1**: 8.466 call = **84,7% hạn mức của cả ngày**. Chỉ còn ~1.500 call dự phòng, nên nếu có
> lỗi phải chạy lại thì sẽ vượt hạn mức. Ba cách xử lý:
> - **Chia lần 1 thành 2–3 ngày** (ví dụ mỗi ngày 4 năm) — an toàn nhất, pipeline đã hỗ trợ qua
>   `run --start --end`.
> - Hoặc **giảm bộ biến xuống ~15 biến** (còn 47% hạn mức).
> - Hoặc bắt đầu với **5 năm** (42,3%) rồi mở rộng dần về quá khứ ở các lần sau.
>
> Từ lần 2 trở đi chi phí **không đáng kể (0,7%)** — nên chu kỳ 1 tháng, thậm chí 1 tuần, đều thoải mái.

### 2.3 Vấn đề: cửa sổ lớn dần làm biên chia tập dịch chuyển

Nếu chia 70/15/15 theo **tỉ lệ** trên cửa sổ đang lớn dần, biên sẽ trượt theo mỗi lần training:

| Lần | Cửa sổ | Train đến | Validation | Test |
|---|---|---|---|---|
| 1 | 2016-10-01 → 2026-10-01 | 2023-10-01 | 2023-10-01 → 2025-03-31 | 2025-03-31 → 2026-10-01 |
| 3 | 2016-10-01 → 2026-12-01 | 2023-11-13 | 2023-11-13 → 2025-05-22 | 2025-05-22 → 2026-12-01 |
| 6 | 2016-10-01 → 2027-03-01 | 2024-01-15 | 2024-01-15 → 2025-08-07 | 2025-08-07 → 2027-03-01 |

**Hệ quả nghiêm trọng**: mỗi lần training lại đánh giá trên **một tập test khác nhau** → không thể so sánh model
lần 6 với model lần 1, mà **promotion gate của dự án lại so sánh metric để quyết định có promote hay không**
(xem [CLAUDE.md](../CLAUDE.md) §3.2). So sánh như vậy là so táo với cam.

**Giải pháp: dùng hai tập test song song.**

| Tập | Định nghĩa | Dùng để | Có bị đưa vào train không? |
|---|---|---|---|
| **Test trượt** | **365 ngày gần nhất** của cửa sổ, độ dài **cố định** | **Promotion gate** — ước lượng hiệu năng khi deploy | Ở các lần sau thì có (khi đã lùi vào quá khứ) |
| **Test đóng băng** | Một khoảng **cố định vĩnh viễn**, ví dụ `2025-10-01 → 2026-10-01` | Theo dõi xu hướng chất lượng giữa các phiên bản | **Không bao giờ** — luôn bị cắt khỏi train/val |

Với cách này: `test trượt` luôn là 365 ngày cuối (phủ đủ một vòng mùa, xem §3.2), còn `test đóng băng` cho một
thước đo bất biến qua mọi lần retrain. Ghi cả hai metric vào MLflow; **promotion gate chỉ dùng test trượt**,
vì nó mới phản ánh phân phối hiện tại.

Phần còn lại (cửa sổ trừ đi test trượt và test đóng băng) chia theo thời gian: **85% train / 15% validation**,
validation là phần **gần hiện tại nhất** trong phần còn lại đó.

---

## 3. Phân tích dataset

### 3.1 API và mô hình

| Hạng mục | Lựa chọn | Lý do |
|---|---|---|
| API | **Historical Weather (Archive)**: `archive-api.open-meteo.com/v1/archive` | Duy nhất cho dữ liệu quá khứ dài; có đủ `weather_code` |
| Mô hình | **`models=era5`** | Xem phân tích dưới |
| Múi giờ | `timezone=UTC` | Tránh lệch giờ mùa hè; framework yêu cầu UTC |
| Nhóm biến | `hourly` (27 biến) | Nhãn cần độ phân giải giờ |
| Độ phân giải điểm neo | 1 giờ | Nhãn là giá trị tại đúng `t+24h`, không phải tổng hợp cửa sổ |

**Vì sao `models=era5` chứ không phải mô hình khác** — đã kiểm tra khả năng hỗ trợ `weather_code` của từng mô hình:

| Mô hình | Có `weather_code`? | Phạm vi | Độ trễ | Kết luận |
|---|---|---|---|---|
| **`era5`** | ✅ | 1940 → `T-6` | 6 ngày | ✅ **Chọn** — giá trị đã chốt, không bị sửa lại |
| `era5_seamless` (mặc định) | ✅ | 1940 → `T-0` | 0 ngày | ❌ Lấp khoảng trống bằng IFS → **giá trị bị sửa lại**, nhãn đã gán sẽ lệch |
| **`era5_land`** | ❌ **KHÔNG hỗ trợ** | 1950 → `T-6` | 6 ngày | ❌ Trả toàn `null` cho `weather_code` |
| `era5_ensemble` | ✅ | 1940 → `T-6` | 6 ngày | Dùng được, nhưng độ phân giải thô hơn |
| `ecmwf_ifs` | ✅ | 2016-12-31 → `T-0` | 0 ngày | Lịch sử ngắn hơn |
| `cerra` | ✅ | 1985 → giữa 2021 | đã ngừng | ❌ Chỉ châu Âu, đã ngừng cập nhật |

→ Giữ `models: era5` như config hiện tại, và vì ERA5 trễ 6 ngày nên **`maturity_lag: 7d`** là đúng.
Điểm neo mới nhất dùng được = `T − 24h − 7d` = **`T-8`**.

**Lưu ý về train/serve skew**: ERA5 không có dữ liệu cho hôm nay, nên khi deploy sẽ không lấy được feature từ
chính nguồn đã train. Vấn đề này và ba hướng xử lý đã phân tích ở
[data_sources_api_analysis.md](data_sources_api_analysis.md) §6.4 — **phải chốt trước khi làm bước serving**,
nhưng không ảnh hưởng tới quy trình tiền xử lý mô tả dưới đây.

### 3.2 Cửa sổ dữ liệu và chia tập

Đo thật cho thấy **nhịp mùa rất mạnh** — ví dụ Hà Nội, tỉ lệ từng nhóm theo tháng (5 năm):

| Tháng | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `0_quang` | 31,96% | 16,78% | 27,42% | 39,83% | 23,52% | **6,25%** | 11,10% | 11,24% | 24,72% | 37,23% | **46,97%** | 37,93% |
| `3_mua` | 0,24% | 1,03% | 1,32% | 2,08% | 7,45% | 7,94% | 7,47% | 11,99% | **12,72%** | 5,19% | 0,50% | **0,19%** |

Tỉ lệ `3_mua` chênh nhau **67 lần** giữa tháng 12 (0,19%) và tháng 9 (12,72%).

> **Hệ quả bắt buộc**: tập validation và test **mỗi tập phải phủ trọn ít nhất 12 tháng liên tục**. Nếu test chỉ
> trải 4 tháng mùa khô thì metric hoàn toàn vô nghĩa với mùa mưa. Đây chính là lý do chọn **test trượt = 365
> ngày** ở §2.3.

Ngược lại, **trôi phân phối giữa các năm là nhẹ** (gộp 12 thành phố, các năm đầy đủ):

| Năm | `0_quang` | `1_nhieu_may` | `2_mua_phun` | `3_mua` | `4_tuyet` |
|---|---|---|---|---|---|
| 2022 | 29,77% | 41,80% | 24,35% | 3,92% | 0,16% |
| 2023 | 34,02% | 40,66% | 21,84% | 3,38% | 0,10% |
| 2024 | 31,66% | 41,08% | 23,27% | 3,87% | 0,13% |
| 2025 | 30,51% | 42,35% | 23,39% | 3,58% | 0,17% |

→ Biến động giữa năm chỉ 3–4 điểm phần trăm. **Retrain hằng tháng không phải vì phân phối trôi nhanh**, mà để
bổ sung dữ liệu mới và giữ model luôn gần với giai đoạn hiện tại. Có thể giãn chu kỳ lên 1 quý nếu muốn tiết
kiệm, miễn là có giám sát drift.

**Cấu hình cửa sổ khuyến nghị cho lần 1 (training ngày 2026-10-01):**

| Tập | Khoảng | Số ngày | Số dòng (12 thành phố) |
|---|---|---|---|
| Train | 2016-10-01 → 2024-10-01 | 2.922 | ~841.500 |
| Validation | 2024-10-01 → 2025-10-01 | 365 | ~105.100 |
| **Test trượt** | 2025-10-01 → 2026-10-01 | 365 | ~105.100 |
| *Test đóng băng* | *trùng test trượt ở lần 1; từ lần 2 giữ nguyên khoảng này* | 365 | ~105.100 |

Mỗi lần retrain, train và validation tiến lên, còn test trượt luôn là 365 ngày cuối.

### 3.3 Lưu ý về số dòng "ảo"

1.051.776 dòng **không phải** 1 triệu mẫu độc lập: điểm neo cách nhau 1 giờ, trong khi nhãn ở `t+24h` — hai dòng
liền kề có trạng thái khí quyển gần như giống nhau. Số mẫu thực sự độc lập gần với **43.824** (số ngày × thành phố).

Hai lựa chọn, ghi rõ vào config:

- **Giữ điểm neo mỗi giờ** (khuyến nghị): model học được nhịp theo giờ trong ngày; đổi lại phải cẩn thận khi chia
  tập (chia theo khối thời gian, **tuyệt đối không chia ngẫu nhiên**).
- **Lấy điểm neo mỗi 6 giờ**: giảm 4 lần số dòng, train nhanh hơn, gần như không mất thông tin.

---

## 4. Quy trình tiền xử lý

Sáu bước, mỗi bước là một task riêng, ghi kết quả ra một lớp dữ liệu riêng trên S3. Nguyên tắc chung:
**mỗi bước chỉ đọc lớp trước và ghi lớp của mình; XCom chỉ chở đường dẫn và số đếm.**

```
   Open-Meteo Archive API
            │
   ┌────────▼─────────┐
   │ B1. Thu thập     │ → landing/      JSON gốc (gzip), bất biến
   ├──────────────────┤
   │ B2. Định dạng    │ → observations/ bảng rộng: 1 dòng = (thành phố, giờ)
   ├──────────────────┤
   │ B3. Làm sạch     │ → cleaned/      + quarantine/ (dòng bị loại, kèm lý do)
   ├──────────────────┤
   │ B4. Gán nhãn     │ → labeled/      + cột label
   ├──────────────────┤
   │ B5. Validation   │ → (cổng chặn)   báo cáo + chặn pipeline nếu không đạt
   ├──────────────────┤
   │ B6. Feature eng. │ → features/     bảng sẵn sàng training
   └──────────────────┘
```

### 4.1 B1 — Thu thập

| | |
|---|---|
| **Vào** | Cấu hình `problems/wx_code_clf/collection.yaml` + khoảng thời gian của run |
| **Ra** | `landing/window=<key>/part-NNNNN.json.gz` — JSON nguyên bản, **không sửa một ký tự nào** |
| **Trạng thái** | ✅ Đã có — tái dùng [pipeline.extract](../framework/collection/pipeline.py) |

Việc cần làm:

1. Tạo thư mục `problems/wx_code_clf/` với `collection.yaml`: `source.type: open_meteo`, `models: era5`,
   27 biến, `horizon: 24h`, `maturity_lag: 7d`, `frequency: 1h`, `interval: 1d`.
2. **Chia nhỏ lần backfill đầu tiên** thành các đoạn ≤ 4 năm để không vượt hạn mức API (§2.2).
3. Giữ nguyên nguyên tắc **landing bất biến**: nếu sau này đổi cách gán nhãn hay đổi feature, chạy lại từ B2
   chứ không gọi lại API.

**Kiểm tra ngay tại B1**: số response nhận được đúng bằng số đoạn đã gửi; mỗi response có đủ 12 phần tử
(12 thành phố) theo đúng thứ tự `entity_ids` đã gửi.

### 4.2 B2 — Định dạng bảng

| | |
|---|---|
| **Vào** | `landing/` |
| **Ra** | `observations/event_date=YYYY-MM-DD/part-00000.parquet` |
| **Trạng thái** | ✅ Đã có — [OpenMeteoConnector.flatten](../framework/collection/connectors/open_meteo.py) |

Chuyển JSON **dạng cột** (mảng song song) thành bảng rộng: mỗi dòng là một cặp (`entity_id`, `event_time`),
mỗi biến một cột, kèm thuộc tính tĩnh của thực thể.

Ba điểm phải cẩn thận (đã phân tích ở [data_sources_api_analysis.md](data_sources_api_analysis.md) §2.3):

1. **Ghép theo thứ tự**: response không có `location_id`; phải ghép mảng kết quả với `entity_ids` đã gửi theo
   đúng thứ tự. Kiểm tra `len(locations) == len(entity_ids)` và **dừng ngay nếu lệch**.
2. **Không lấy `latitude`/`longitude` từ response** làm toạ độ thực thể — đó là tâm ô lưới. Giữ toạ độ khai báo
   trong file entities.
3. **Kiểm tra `utc_offset_seconds == 0`** — nếu khác 0 nghĩa là tham số `timezone` bị sai, toàn bộ mốc thời gian
   sẽ lệch.

### 4.3 B3 — Làm sạch

| | |
|---|---|
| **Vào** | `observations/` |
| **Ra** | `cleaned/` (dòng đạt) + `quarantine/` (dòng bị loại, kèm cột `reject_reason`) |
| **Trạng thái** | ❌ Chưa có — **cần viết mới** |

**Tin tốt từ việc khảo sát**: dữ liệu ERA5 **rất sạch**. Đo trên 105.120 dòng × 27 biến (1 năm × 12 thành phố):

- **0 giá trị thiếu** trên toàn bộ 27 biến.
- **0 vi phạm khoảng vật lý** (độ ẩm 7–100%, mây 0–100%, mưa ≥ 0, hướng gió 0–360...).
- **0 mốc thời gian trùng, 0 lỗ hổng** — 5 năm cho đúng 43.824 mốc giờ liên tục (1.826 ngày × 24).

→ Bước làm sạch ở đây **không phải để sửa dữ liệu bẩn, mà là một cổng kiểm soát** phát hiện khi nguồn đổi hành
vi. Vẫn phải viết đầy đủ, vì framework cần nó cho các nguồn khác (OpenAQ thì bẩn thật).

**Các quy tắc cần hiện thực**, theo `semantic_type` chứ không theo tên cột cụ thể:

| # | Quy tắc | Áp dụng cho | Xử lý khi vi phạm |
|---|---|---|---|
| C1 | **Ép kiểu**: mã hoá → `category`; đo lường → `float32`; thời gian → `datetime64[ns, UTC]` | tất cả | Ép được thì ép; không ép được → cách ly |
| C2 | **Khoá không null, không trùng** `(entity_id, event_time)` | khoá | Giữ bản ghi cuối, log số trùng |
| C3 | **Khoảng vật lý** theo từng `semantic_type` (xem bảng dưới) | biến đo | Ngoài khoảng → **đặt `null`**, ghi lý do |
| C4 | **Giá trị thiếu** | biến đo | Nội suy tuyến tính nếu lỗ ≤ 2 giờ; lỗ > 2 giờ → cách ly dòng |
| C5 | **Tính nhất quán giữa cột**: `rain ≤ precipitation`; `cloud_cover_low/mid/high ≤ 100` | nhóm cột | Vi phạm → cách ly |
| C6 | **Liên tục thời gian**: mỗi thực thể phải có đủ mốc giờ liên tục | khoá | Thiếu mốc → sinh dòng rỗng rồi áp C4 |

**Khoảng vật lý** dùng cho C3 (lấy từ chính khoảng đo được, nới biên an toàn):

| `semantic_type` | Cột | Khoảng hợp lệ |
|---|---|---|
| `percent` | `relative_humidity_2m`, `cloud_cover*` | [0, 100] |
| `temperature_c` | `temperature_2m`, `dew_point_2m`, `apparent_temperature`, `soil_temperature_*` | [−90, 60] |
| `precip_mm` | `precipitation`, `rain` | [0, 400] |
| `snow_cm` | `snowfall` | [0, 100] |
| `pressure_hpa` | `pressure_msl`, `surface_pressure` | [800, 1100] |
| `radiation_wm2` | `shortwave_radiation`, `direct_radiation`, `diffuse_radiation` | [0, 1500] |
| `speed_kmh` | `wind_speed_10m`, `wind_speed_100m`, `wind_gusts_10m` | [0, 500] |
| `angle_deg` | `wind_direction_10m`, `wind_direction_100m` | [0, 360] |
| `duration_s` | `sunshine_duration` | [0, 3600] |
| `ratio` | `soil_moisture_0_to_7cm` | [0, 1] |
| `wmo_code` | `weather_code` | tập hợp mã WMO hợp lệ |

> **Bẫy kiểu dữ liệu quan trọng nhất**: `weather_code` có kiểu `int` trong JSON nhưng **là biến phân loại**, không
> phải số. Nếu để nguyên `int` thì mọi phép chuẩn hoá/so sánh sau này đều sai (mã 75 không "lớn hơn" mã 3 theo
> nghĩa nào cả). **Bắt buộc ép sang `category` ngay tại C1.** Tương tự, `wind_direction_*` là **biến vòng**:
> 359° và 1° chỉ cách nhau 2°, nhưng về số thì cách 358 — xử lý ở bước feature engineering (§4.6).

**Nguyên tắc fail-soft**: dòng vi phạm được đẩy sang `quarantine/` kèm `reject_reason`, pipeline **tiếp tục** với
phần sạch — đúng thiết kế kế thừa ở [CLAUDE.md](../CLAUDE.md) §3.1. Nhưng phải có ngưỡng: nếu
**> 1% số dòng bị cách ly trong một run** thì dừng pipeline và cảnh báo, vì dữ liệu ERA5 vốn sạch nên tỉ lệ đó
nghĩa là nguồn đã đổi.

### 4.4 B4 — Gán nhãn

| | |
|---|---|
| **Vào** | `cleaned/` |
| **Ra** | `labeled/` — thêm `label`, `label_raw`, `label_window_end` |
| **Trạng thái** | ⚠️ Một phần — [labeling.py](../framework/collection/labeling.py) có sẵn `agg: last`, nhưng **chưa hỗ trợ multiclass** |

Nhãn **đã có sẵn** trong dữ liệu (mức A), nên bước này chỉ gồm **dịch thời gian + gộp nhóm**:

```
label_raw = weather_code tại (t + 24h)        ← agg: last, horizon: 24h
label     = gop_nhom(label_raw)               ← ánh xạ 13 mã → 4 lớp
```

Ánh xạ gộp nhóm phải **khai báo trong YAML**, không viết cứng trong code:

```yaml
label:
  target: weather_code
  agg: last                 # giá trị tại đúng t + 24h
  horizon: 24h
  min_coverage: 1.0         # phải có quan sát tại t+24h, không chấp nhận thiếu
  mapping:                  # mục mới cần bổ sung vào config.py
    "0_quang":      [0, 1]
    "1_nhieu_may":  [2, 3]
    "2_mua_phun":   [51, 53, 55]
    "3_mua":        [61, 63, 65, 71, 73, 75]   # đã gộp tuyết vào mưa
```

**Việc cần làm trong framework** (đây là phần sửa code duy nhất đáng kể):

1. Mở rộng `TASK_TYPES` trong [config.py](../framework/collection/config.py) để nhận `multiclass`
   (hiện chỉ có `binary`, `regression`).
2. Thêm khoá `label.mapping` và kiểm tra khi nạp cấu hình: mọi mã trong `mapping` phải hợp lệ, không mã nào bị
   khai hai lần, và **không mã nào bị bỏ sót** — nếu nguồn trả mã lạ thì phải báo lỗi chứ không âm thầm bỏ qua.
3. Giữ nguyên nguyên tắc: **dòng không xác định được nhãn thì loại**, không ghi `null`.

**Kiểm tra ngay tại B4**: mỗi dòng có `label` thuộc đúng tập lớp đã khai; `label_window_end == event_time + 24h`;
số dòng bị loại vì thiếu quan sát ở `t+24h` phải bằng đúng số điểm neo nằm ở rìa cuối cửa sổ.

### 4.5 B5 — Validation

| | |
|---|---|
| **Vào** | `labeled/` (và cả `cleaned/`, `quarantine/` để đối chiếu) |
| **Ra** | Báo cáo + **quyết định cho đi tiếp hay chặn** |
| **Trạng thái** | ❌ Chưa có — cần viết mới (dùng Great Expectations như định hướng ở [CLAUDE.md](../CLAUDE.md) §3.1) |

Đây là bước trả lời đúng hai câu hỏi đã đặt ra: *"làm sạch xong chưa?"* và *"có bản ghi nào lọt lưới chưa được
làm sạch không?"*.

**Nhóm 1 — Chứng minh bước làm sạch đã chạy hết, không sót dòng nào:**

| # | Kiểm tra | Cách làm | Chặn pipeline? |
|---|---|---|---|
| **V1** | **Bảo toàn số dòng** | `n(observations) == n(cleaned) + n(quarantine)` — đẳng thức phải đúng tuyệt đối | ✅ Có |
| **V2** | **Điểm bất động (quan trọng nhất)** | **Chạy lại toàn bộ bộ quy tắc làm sạch lên `cleaned/`. Nếu còn bất kỳ dòng nào bị sửa hoặc bị loại → có dòng đã lọt lưới ở lần đầu.** Kết quả đúng phải là: 0 dòng thay đổi | ✅ Có |
| **V3** | **Dấu vết xử lý** | Mỗi dòng ở `cleaned/` mang cột `cleaning_run_id` và `rules_applied` (bitmask các quy tắc đã chạy). Không dòng nào được thiếu bit nào | ✅ Có |
| **V4** | **Lý do cách ly hợp lệ** | Mọi dòng trong `quarantine/` có `reject_reason` khác rỗng và thuộc tập lý do đã khai báo | ✅ Có |
| **V5** | **Tỉ lệ cách ly** | `n(quarantine) / n(observations) ≤ 1%` (ERA5 vốn sạch) | ⚠️ Cảnh báo |

> V2 là cách chứng minh chặt chẽ nhất: **bước làm sạch phải là phép toán luỹ đẳng** — chạy một lần hay hai lần
> cho kết quả như nhau. Nếu lần chạy thứ hai còn sửa được gì, nghĩa là lần đầu chưa xong.

**Nhóm 2 — Kiểm tra chất lượng dữ liệu đầu ra:**

| # | Kiểm tra | Ngưỡng đạt |
|---|---|---|
| V6 | **Nhãn suy lại được từ `precipitation` + `snowfall` + `cloud_cover`** (công thức §1.2) | ≥ 99% khớp — dưới ngưỡng nghĩa là nguồn đã đổi cách sinh mã |
| V7 | Schema: đủ cột, đúng kiểu, `weather_code` là `category` | 100% |
| V8 | Không null ở cột bắt buộc (khoá, nhãn, 27 biến) | 100% |
| V9 | Khoá `(entity_id, event_time)` duy nhất | 100% |
| V10 | Chuỗi thời gian liên tục theo từng thực thể, bước đúng 1 giờ | 100% |
| V11 | **Phân bố nhãn nằm trong khoảng kỳ vọng** so với 5 năm lịch sử (±10 điểm % cho mỗi lớp) | Lệch hơn → cảnh báo drift |
| V12 | Đủ 12 thực thể, mỗi thực thể có số dòng xấp xỉ nhau (chênh ≤ 1%) | Lệch hơn → cảnh báo |
| V13 | **Không rò rỉ**: với mẫu ngẫu nhiên 1.000 dòng, `label_raw` phải khớp đúng `weather_code` của dòng có `event_time = t + 24h` | 100% |

V13 là kiểm tra chống rò rỉ nhãn quan trọng nhất — nó xác nhận nhãn thực sự lấy từ tương lai và lấy đúng mốc.

### 4.6 B6 — Feature engineering

| | |
|---|---|
| **Vào** | `labeled/` |
| **Ra** | `features/` — bảng sẵn sàng đưa vào training |
| **Trạng thái** | ❌ Chưa có — cần viết mới |

**Nguyên tắc bất di bất dịch**: mọi đặc trưng chỉ được tính từ dữ liệu có `event_time ≤ t`. Cửa sổ trượt phải là
**trailing** (nhìn lùi), không bao giờ **centered**.

| Nhóm | Đặc trưng | Vì sao cần |
|---|---|---|
| **Gốc** | 27 biến tại `t` | Trạng thái hiện tại |
| **Trễ (lag)** | Giá trị tại `t−1h`, `t−3h`, `t−6h`, `t−12h`, `t−24h` cho các biến chủ chốt: `cloud_cover`, `precipitation`, `pressure_msl`, `relative_humidity_2m`, `temperature_2m` | Cho model thấy xu hướng, không chỉ một lát cắt |
| **Biến thiên** | `pressure_msl(t) − pressure_msl(t−3h)` và `(t−24h)`; tương tự cho nhiệt độ, độ ẩm | **Biến thiên áp suất 3 giờ là chỉ báo thời tiết kinh điển** — áp giảm nhanh báo hiệu mưa |
| **Trung bình trượt** | Trung bình/max/độ lệch chuẩn trên 3h, 6h, 24h lùi; **tổng mưa** 6h, 24h lùi | Làm mượt nhiễu, nắm bắt "đang trong đợt mưa hay không" |
| **Nhãn quá khứ** | Nhóm thời tiết tại `t`, `t−24h` (dạng category) | Persistence đạt 51,12% → đây là đặc trưng mạnh nhất, **bắt buộc có** |
| **Chu kỳ** | `sin`/`cos` của giờ trong ngày và ngày trong năm | Mã hoá tính tuần hoàn; nhịp mùa rất mạnh (§3.2) |
| **Biến vòng** | `sin`/`cos` của `wind_direction_10m`, `wind_direction_100m`; hoặc tách thành `u = v·cos θ`, `v = v·sin θ` | Hướng gió 359° và 1° phải gần nhau |
| **Vật lý dẫn xuất** | Chênh lệch nhiệt độ điểm sương `temperature_2m − dew_point_2m`; `is_day = shortwave_radiation > 0` | Chênh lệch điểm sương nhỏ ⇒ không khí bão hoà ⇒ dễ mưa/sương |
| **Thực thể** | `latitude`, `longitude`, `elevation`; **prior khí hậu học**: tỉ lệ từng lớp của chính thành phố đó theo tháng | Giúp một model chung phục vụ 12 thành phố khác nhau (§1.4) |

> ### ⚠️ Prior khí hậu học — cái bẫy rò rỉ dễ mắc nhất
>
> Đặc trưng "tỉ lệ lớp `3_mua` của Hà Nội trong tháng 9" rất mạnh, nhưng **phải tính chỉ từ dữ liệu trong tập
> train**. Nếu tính trên toàn bộ dataset thì thông tin của tập test rò rỉ ngược vào feature, và metric sẽ đẹp
> giả tạo.
>
> Cách làm đúng: coi nó là **transformer artifact fit-once/apply-many** (đúng định hướng ở
> [CLAUDE.md](../CLAUDE.md) §8): **fit** bảng prior trên tập train → lưu cùng model → **apply** nguyên vẹn
> cho validation, test và serving. Tuyệt đối không fit lại trên từng tập.

**Xử lý giá trị thiếu do lag/rolling sinh ra**: 24 giờ đầu của mỗi thực thể sẽ thiếu các đặc trưng lag-24h. Hai
cách: (a) loại bỏ các dòng đó — đơn giản, mất ~0,03% dữ liệu với 10 năm; (b) giữ và để model xử lý `null`
(XGBoost làm được). Khuyến nghị **(a)** vì sạch hơn và chi phí không đáng kể.

**Mã hoá biến phân loại**: `weather_code` quá khứ và `entity_id` nên dùng **one-hot** (ít lớp) hoặc để XGBoost xử
lý native categorical. **Không dùng target encoding** cho bài này — rủi ro rò rỉ cao mà lợi ích thấp khi số lớp nhỏ.

**Chuẩn hoá**: XGBoost không cần. Nếu sau này thử mô hình tuyến tính/mạng nơ-ron thì scaler cũng phải theo cơ chế
fit-once trên train, lưu cùng model — tránh đúng lỗi "rò rỉ thống kê" đã ghi ở [CLAUDE.md](../CLAUDE.md) §9.

---

## 5. Artifact và quy tắc chống rò rỉ

**Artifact phải lưu cùng model** (để batch và serving dùng lại y hệt):

| Artifact | Nội dung | Fit trên |
|---|---|---|
| `label_mapping.json` | Ánh xạ 13 mã WMO → 4 lớp | Cấu hình (tĩnh) |
| `feature_spec.json` | Danh sách cột, thứ tự, kiểu, `semantic_type` | Cấu hình (tĩnh) |
| `climatology_prior.parquet` | Prior từng lớp theo (thành phố, tháng) | **Chỉ tập train** |
| `cleaning_rules.json` | Khoảng hợp lệ, ngưỡng, phiên bản quy tắc | Cấu hình (tĩnh) |
| `category_levels.json` | Tập giá trị của các cột category | **Chỉ tập train** |

**Năm quy tắc chống rò rỉ, kiểm tra tự động ở B5:**

1. Mọi feature chỉ dùng dữ liệu `event_time ≤ t`; nhãn lấy tại `t + 24h` (kiểm tra V13).
2. Chia tập **theo thời gian, theo khối**, không bao giờ ngẫu nhiên.
3. Mọi thống kê (prior, scaler, mức category) **fit trên train, apply cho val/test**.
4. **Chừa khoảng đệm 24 giờ** giữa các tập: nhãn của điểm neo cuối tập train nằm ở `t+24h`, lấn sang đầu tập
   validation → bỏ 24 giờ đầu của mỗi tập đứng sau.
5. `test đóng băng` **không bao giờ** xuất hiện trong train hay validation, ở bất kỳ lần retrain nào.

---

## 6. Checklist nghiệm thu

**Cấu hình**

- [ ] `problems/wx_code_clf/collection.yaml` với `models: era5`, `horizon: 24h`, `maturity_lag: 7d`, `frequency: 1h`
- [ ] `label.mapping` khai đủ 13 mã WMO, không trùng, không sót
- [ ] `config.py` chấp nhận `task_type: multiclass`

**Dữ liệu**

- [ ] Backfill 10 năm chia thành ≥ 3 đợt để không vượt hạn mức API
- [ ] Cả 12 thực thể đều có số dòng xấp xỉ nhau
- [ ] Cửa sổ train/val/test có biên cố định, `test trượt` phủ đúng 365 ngày
- [ ] `test đóng băng` được khai báo và cắt khỏi train/val

**Tiền xử lý**

- [ ] B3 luỹ đẳng — chạy lần hai trên `cleaned/` không sửa dòng nào (V2)
- [ ] Đẳng thức bảo toàn số dòng đúng tuyệt đối (V1)
- [ ] `weather_code` có kiểu `category`, không phải `int`
- [ ] Hướng gió đã mã hoá vòng (`sin`/`cos`)
- [ ] Prior khí hậu học fit **chỉ trên train**, lưu thành artifact

**Nhãn và đánh giá**

- [ ] Nhãn suy lại từ `precipitation`+`snowfall`+`cloud_cover` khớp ≥ 99% (V6)
- [ ] Phân bố nhãn khớp mức kỳ vọng: ~32% / 42% / 23% / 4%
- [ ] Đã tính baseline **persistence (51,12%)** và **lớp đông nhất (41,67%)** trên đúng tập test
- [ ] Đã tính baseline "hồi quy mưa + mây rồi áp ngưỡng"
- [ ] Metric chính là **macro-F1**; accuracy chỉ để so baseline
- [ ] Có bảng metric **tách theo từng thành phố**, so với baseline của riêng thành phố đó

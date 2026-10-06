# Ý tưởng từ các bài báo — Data Processing

> Tóm tắt nội dung 16 bài báo trong thư mục [`paper/`](../paper/). Mỗi mục là **một bài báo độc lập**, chỉ trình bày những gì bài báo đó cung cấp,
> tập trung vào **phương pháp**. Thuật ngữ kỹ thuật giữ nguyên tiếng Anh khi cần.
>
> Cấu trúc chung của mỗi mục: **thông tin bài** → **tóm tắt** → **mục tiêu / câu hỏi nghiên cứu** → **phương pháp** (phần dài nhất)
> → **thiết kế thực nghiệm** → **kết quả** → **hạn chế / hướng mở do tác giả nêu**.

## Danh sách bài báo

| # | Bài báo | Năm | Loại | Trọng tâm phương pháp |
|---|---|---|---|---|
| 1 | [Data pipeline quality](#1-data-pipeline-quality-influencing-factors-root-causes-of-data-related-issues-and-processing-problem-areas-for-developers) — Foidl et al. | 2024 | Thực nghiệm | Taxonomy 41 yếu tố ảnh hưởng chất lượng pipeline; khai phá GitHub / Stack Overflow tìm nguyên nhân gốc lỗi dữ liệu |
| 2 | [Automated data processing and feature engineering — survey](#2-automated-data-processing-and-feature-engineering-for-deep-learning-and-big-data-applications-a-survey) — Mumuni & Mumuni | 2025 | Survey | Tự động hoá imputation, encoding, cleaning, labeling, augmentation, feature engineering; AutoML |
| 3 | [Data preprocessing impact on ML algorithm performance](#3-data-preprocessing-impact-on-machine-learning-algorithm-performance) — Amato & Di Lecce | 2023 | Thực nghiệm | Chọn đặc trưng bằng SPQR (semi-pivoted QR) so với PCA; ảnh hưởng của chuẩn hoá |
| 4 | [Auto-Validate](#4-auto-validate-unsupervised-data-validation-using-data-domain-patterns-inferred-from-data-lakes) — Song & He | 2021 | Phương pháp | Tự suy luật validation (pattern) cho cột chuỗi, tối thiểu false-positive bằng bằng chứng từ data lake |
| 5 | [Towards Observability for Production ML Pipelines](#5-towards-observability-for-production-machine-learning-pipelines-vision-paper) — Shankar & Parameswaran | 2022 | Vision | Detect → diagnose → react; ước lượng accuracy khi thiếu nhãn; ràng buộc tự tinh chỉnh; mltrace |
| 6 | [Data Smells in Public Datasets](#6-data-smells-in-public-datasets) — Shome et al. | 2022 | Thực nghiệm | Catalogue 14 data smell từ 25 dataset |
| 7 | [Leakage and the Reproducibility Crisis](#7-leakage-and-the-reproducibility-crisis-in-ml-based-science) — Kapoor & Narayanan | 2022 | Khảo sát + tái lập | Taxonomy 8 loại leakage; model info sheet; tái lập nghiên cứu dự đoán nội chiến |
| 8 | [DiffPrep](#8-diffprep-differentiable-data-preprocessing-pipeline-search-for-learning-over-tabular-data) — Li et al. | 2023 | Phương pháp | Tìm pipeline tiền xử lý theo từng đặc trưng bằng tối ưu hai cấp khả vi |
| 9 | [Data Cleaning and ML — SLR](#9-data-cleaning-and-machine-learning-a-systematic-literature-review) — Côté et al. | 2024 | SLR | 101 bài, 6 hoạt động làm sạch: feature, label, entity matching, outlier, imputation, holistic |
| 10 | [Data-Centric Evaluation for Tabular Data](#10-a-data-centric-perspective-on-evaluating-machine-learning-models-for-tabular-data) — Tschalzev et al. | 2024 | Benchmark | 3 pipeline tiền xử lý (chuẩn / feature engineering chuyên gia / test-time adaptation) trên 10 cuộc thi Kaggle |
| 11 | [Imputation for Prediction](#11-imputation-for-prediction-beware-of-diminishing-returns) — Le Morvan & Varoquaux | 2025 | Thực nghiệm | Định lượng impute tốt hơn giúp dự đoán bao nhiêu; vai trò missingness indicator |
| 12 | [A Novel ML Data Preprocessing Method](#12-a-novel-machine-learning-data-preprocessing-method-for-enhancing-classification-algorithms-performance) — Iliou et al. | 2015 | Phương pháp | 6 bước biến đổi đại số tuyến tính sinh 4·m đặc trưng |
| 13 | [mlinspect](#13-mlinspect-a-data-distribution-debugger-for-machine-learning-pipelines) — Grafberger et al. | 2021 | Demo | Trích DAG từ pipeline pandas/scikit-learn, inspection dựa trên lineage, phát hiện data distribution bug |
| 14 | [JENGA](#14-jenga--a-framework-to-study-the-impact-of-data-errors-on-the-predictions-of-machine-learning-models) — Schelter et al. | 2021 | Công nghiệp | Tiêm lỗi dữ liệu tổng hợp để đo độ bền mô hình; stress-test schema TFDV |
| 15 | [Auto-Prep](#15-auto-prep-efficient-and-automated-data-preprocessing-pipeline) — Bilal et al. | 2022 | Hệ thống | Tự phát hiện kiểu, xử lý thiếu, encoding, chọn đặc trưng, scaling — có khuyến nghị tương tác |
| 16 | [Data Preprocessing for Supervised Learning](#16-data-preprocessing-for-supervised-learning) — Kotsiantis et al. | 2006 | Tổng quan | Thuật toán cho 6 bước: chọn mẫu/outlier, thiếu, rời rạc hoá, chuẩn hoá, chọn đặc trưng, xây dựng đặc trưng |

---

## 1. Data pipeline quality: Influencing factors, root causes of data-related issues, and processing problem areas for developers

| | |
|---|---|
| **Tác giả** | Harald Foidl, Valentina Golendukhina, Rudolf Ramler, Michael Felderer |
| **Nguồn** | *The Journal of Systems and Software* 207 (2024) 111855 — open access CC BY |
| **Loại bài** | Nghiên cứu thực nghiệm: tổng quan tài liệu đa nguồn + phỏng vấn chuyên gia + khai phá GitHub/Stack Overflow |
| **File** | `paper/1-s2.0-S0164121223002509-main.pdf` |

### 1.1 Tóm tắt

Data pipeline là thành phần cốt lõi của hệ thống hướng dữ liệu nhưng thường kém tin cậy và trả ra dữ liệu chất lượng thấp.
Bài báo làm hai việc:

1. Xây dựng **taxonomy gồm 41 yếu tố ảnh hưởng (influencing factors — IF)** tới khả năng pipeline cung cấp dữ liệu chất lượng,
   gom thành 14 nhóm và 5 chủ đề, rồi kiểm chứng bằng phỏng vấn 8 chuyên gia.
2. Nghiên cứu thực nghiệm: tìm **nguyên nhân gốc (root cause)** của lỗi liên quan đến dữ liệu và **giai đoạn pipeline** nơi lỗi xuất hiện
   (khai phá GitHub), và các **chủ đề xử lý dữ liệu mà lập trình viên hỏi nhiều nhất** (khai phá Stack Overflow).

Kết quả nổi bật: lỗi dữ liệu chủ yếu do **sai kiểu dữ liệu (33%)**, xảy ra nhiều nhất ở **giai đoạn cleaning (35%)**;
**tích hợp và nạp dữ liệu (integration + ingestion) chiếm 47%** câu hỏi của lập trình viên; **tương thích (compatibility)** là một vùng vấn đề riêng.

### 1.2 Mục tiêu nghiên cứu

| # | Mục tiêu |
|---|---|
| O1 | Xác định và đánh giá các yếu tố ảnh hưởng tới khả năng pipeline cung cấp dữ liệu chất lượng cao |
| O2 | Phân tích các lỗi liên quan đến dữ liệu: nguyên nhân gốc và vị trí (giai đoạn) trong pipeline |
| O3 | Xác định các chủ đề xử lý dữ liệu mà lập trình viên gặp khó, và xem chúng có trùng với các giai đoạn xử lý điển hình không |

**Định nghĩa IF**: mọi khía cạnh con người, kỹ thuật hoặc tổ chức có thể ảnh hưởng tới khả năng pipeline cung cấp dữ liệu chất lượng.

### 1.3 Khái niệm nền: kiến trúc data pipeline mà bài báo sử dụng

Bài báo nhìn pipeline theo góc **thực tiễn** (một phần mềm tự động thao tác và di chuyển dữ liệu từ nguồn tới đích),
thay vì góc lý thuyết (DAG gồm các node xử lý).

```
 Data sources ──► ┌──────────────── Data processing ────────────────┐ ──► Data sinks
 (DB, sensor,     │ Ingestion ─► Preprocessing ─────────► Loading   │     (pipeline khác,
  file; dữ liệu   │              ├ integration (schema mapping,     │      ứng dụng, DWH,
  cấu trúc / bán  │              │   loại trùng)                    │      data lake)
  cấu trúc / phi  │              ├ cleaning (missing value, nhiễu)  │
  cấu trúc)       │              └ transformation (binarize, chuẩn  │
                  │                hoá, rời rạc hoá, giảm chiều,    │
                  │                oversampling, sinh mẫu)          │
                  └──────────────────────┬──────────────────────────┘
                                   Data storage (tạm / lâu dài)
     Tác vụ hỗ trợ:  Monitoring (chất lượng dữ liệu, hiệu năng, log, alert)
                     Management (workflow/orchestration, metadata/catalog/versioning, cấu hình & nâng cấp tool)
```

Phân loại pipeline theo 3 tiêu chí: **cách ingest** (batch / streaming / lambda), **thứ tự xử lý** (ETL / ELT),
**mục đích** (data collection pipeline / data preprocessing pipeline cho ML).

### 1.4 Phương pháp

Toàn bộ quy trình nghiên cứu gồm 3 phương pháp, mỗi phương pháp phục vụ một mục tiêu:

```
 O1 ──► Multivocal Literature Review ──► Thematic synthesis ──► Taxonomy IF ──► Phỏng vấn 8 chuyên gia (kiểm chứng)
 O2 ──► Khai phá issue GitHub (11 dự án) ──► gán nhãn root cause + stage
 O3 ──► Khai phá câu hỏi Stack Overflow (30 tag) ──► gán nhãn chủ đề
```

#### a) Multivocal Literature Review (MLR) — dùng cả tài liệu khoa học lẫn tài liệu "xám"

- **Hai bộ từ khoá khác nhau** cho Google Scholar (biến thể học thuật: *data processing pipeline*, *ML pipeline*...) và
  Google Search (thực tiễn: *data pipeline* AND *pitfall / anti pattern / issues / challenges*...).
  Lý do: giới học thuật ít dùng đúng cụm "data pipeline", còn thực tiễn thì dùng nhiều.
- **Giới hạn không gian tìm kiếm**: chỉ xét 3 trang đầu (30 kết quả) mỗi chuỗi tìm kiếm, chỉ xem tiếp nếu trang cuối còn bài liên quan.
- **Tiêu chí**: có toàn văn, công bố 2000–2021, nói về đặc tính chất lượng / best practice / bài học / yêu cầu / vấn đề của pipeline;
  loại bài không phải tiếng Anh và bài chỉ nói về khía cạnh ML.
- **Phễu lọc**:

| Bước | Số nguồn |
|---|---|
| Quét ban đầu | 1.203 |
| Sau lọc theo tiêu đề/tóm tắt | 144 (111 khoa học + 33 tài liệu xám) |
| + snowballing tiến/lùi | 149 |
| Sau đánh giá chi tiết (2 người bỏ phiếu độc lập) | **109** (83 khoa học + 26 xám) |

- **Trích xuất**: rút 612 đoạn văn mô tả khía cạnh *chất lượng* (best practice, đặc tính) hoặc *vấn đề* (issue, challenge).
  Loại 175 đoạn quá trừu tượng / quá chung / không ảnh hưởng chất lượng dữ liệu. Tiêu chí "có ảnh hưởng" dựa trên
  5 đặc tính chất lượng dữ liệu nội tại của **ISO/IEC 25012**: accuracy, completeness, consistency, credibility, currentness.
- **Thematic synthesis** (tổng hợp theo chủ đề) trên 437 đoạn còn lại:

```
 437 đoạn văn ──(gán mã quy nạp)──► 164 code ──(gom theo độ tương đồng)──► 41 IF
                                                                           │
                       5 chủ đề (theme) ◄──(gom nhóm cấp cao)── 14 nhóm IF ◄┘
 Ví dụ:  "glue code", "dead code", "duplicated code"  ─►  IF "Code quality"  ─►  nhóm "Software code"  ─►  chủ đề "Processing"
```

  Hai nhà nghiên cứu làm lặp, đổi tên/gộp code liên tục; mỗi người gán nhóm vào chủ đề độc lập, bất đồng thì người thứ ba phân xử;
  cuối cùng chuẩn hoá thuật ngữ.

#### b) Kiểm chứng bằng chuyên gia

- 8 chuyên gia, mỗi người ≥ 3 năm kinh nghiệm data engineering (một nửa 3–5 năm, một nửa > 5 năm, 2 người > 10 năm).
- Phỏng vấn có cấu trúc; để không quá tải, chỉ hỏi đánh giá **14 nhóm IF** (IF con được đưa làm ví dụ).
- Thang Likert 4 mức: high / medium / low / no influence (cho phép không trả lời).

#### c) Khai phá GitHub — nguyên nhân gốc và vị trí lỗi

1. Chọn 11 dự án mã nguồn mở có data pipeline là thành phần chính (ckan, covid-19-data, DataGristle, dataprep, doit, flyte,
   networkx, opendata.cern.ch, pandas-profiling, pybossa, rubrix) → **12.345 issue**.
2. Lấy mẫu ngẫu nhiên 400 issue (độ tin cậy 95%, cỡ mẫu tối thiểu 373) → gán nhãn *data-related / not / ambiguous* → chỉ **42** issue liên quan dữ liệu (~10%).
3. **Chiến lược tăng mật độ**: rút từ khoá đặc trưng cho issue *không* liên quan dữ liệu (UI, API, version, tutorial, license, typo, logo,
   documentation, readme...), kiểm tra chúng không xuất hiện trong issue liên quan dữ liệu, rồi lọc bỏ 6.172 issue (52%).
   Lấy thêm 200 mẫu từ 5.773 issue còn lại (giữ phân bố theo dự án) → thêm 58 issue.
4. Tổng **100 issue liên quan dữ liệu**. Gán nhãn **root cause** theo hướng quy nạp và **stage** theo hướng suy diễn
   (dùng các stage định nghĩa sẵn); nếu mô tả không đủ thì đọc thêm mã nguồn/bản sửa. Hai người khác kiểm tra lại đến khi đồng thuận.

#### d) Khai phá Stack Overflow — chủ đề lập trình viên gặp khó

1. Tag khởi đầu: *data pipeline, data cleaning, data integration, data ingestion, data transformation, data loading* + *pandas, scikit-learn*.
2. **Snowball tag** qua Stack Overflow API (mỗi lần API gợi ý tối đa 8 tag liên quan) đến khi không còn tag mới → **30 tag**.
3. Thu **15.035 bài** (sau loại trùng) → lấy mẫu 400 (95% tin cậy) → loại 301 bài hỏi chung về thư viện/phân tích → **99 bài**.
4. Gán nhãn suy diễn theo các stage điển hình, rồi lặp lại: gom, tinh chỉnh, tạo nhãn mới đến khi ra các chủ đề chính.

### 1.5 Kết quả

#### a) Taxonomy 41 IF — 5 chủ đề, 14 nhóm

| Chủ đề | Nhóm IF | Các IF |
|---|---|---|
| **Data** | Data characteristics | Data dependencies (độ bất ổn của dữ liệu theo thời gian), Data representation, Data variety, Data volume |
| | Data management | Data governance, Data security, Metadata (catalog, data dictionary, schema) |
| | Data sources | Complexity (số nguồn, độ khó join), Reliability (độ sẵn sàng, chất lượng nguồn) |
| **Development & deployment** | Communication & information sharing | Awareness (nhìn pipeline như một tổng thể), Requirements specifications (luật biến đổi, yêu cầu xử lý) |
| | Personnel | Domain knowledge, Expertise |
| | Quality assurance | Best practices (review, refactor, canary), Testing scope |
| | Training-serving skew | Code equality (code dev ≠ prod), Data drift (dữ liệu dev ≠ prod) |
| **Infrastructure** | Serving environment | Hardware, Performance, Scalability |
| | Tools & technology | Appropriateness, Compatibility, Debugging capabilities, Functionality, Heterogeneity, Reliability, Usability |
| **Life cycle management** | Application management | Configuration management, CI/CD, Workflow & orchestration management |
| | Monitoring | Application performance monitoring, Data lineage (quan sát dữ liệu qua mọi bước, gồm versioning) |
| **Processing** | Data flow architecture | Complexity, Dependencies, Modularization, Processing mode, **Reproducibility** (gồm caching, **idempotency**), **Sequence of data operations** |
| | Functionality | Automation (tự động validate, xử lý), Configuration (tham số xử lý), Data cleaning |
| | Software code | Code quality (dead/duplicated code), **Data type handling** (ép kiểu, delimiter, encoding) |

#### b) Đánh giá của chuyên gia

- 13/14 nhóm được đa số chuyên gia đánh giá ảnh hưởng **trung bình đến cao** (tổng: 51 high, 49 medium, 8 low, 1 no).
- **5 nhóm ảnh hưởng mạnh nhất**: Functionality, Personnel, Quality assurance, Data flow architecture, Software code
  (thuộc chủ đề *Development & deployment* và *Processing*). Nhóm Processing vừa được đánh giá cao vừa có độ đồng thuận cao.
- Bất đồng lớn nhất: data management, data sources, personnel, serving environment, tools & technology.
  *Serving environment* có điểm thấp nhất và cũng ít đồng thuận nhất.

#### c) GitHub — nguyên nhân gốc của 100 lỗi liên quan dữ liệu

| Nguyên nhân gốc | Tỉ lệ | Mô tả |
|---|---|---|
| **Data type** | **33%** | Kiểu dữ liệu sai/không xác định → không xử lý được, hoặc mất thông tin mà không báo lỗi; gồm cả cách xử lý kiểu trong data frame. ~90% xảy ra ở cleaning hoặc integration |
| Symbols & characters | 17% | Ký tự đặc biệt, dấu, chữ cái hệ khác, ký hiệu không được encoding hỗ trợ |
| Raw data | 17% | Dữ liệu thô bị trùng, thiếu, hỏng; chủ yếu ở ingestion và integration |
| Functionality | 13% | Hàm chạy sai hoặc thiếu hàm; ~một nửa ở cleaning (dữ liệu đúng bị coi là sai sau khi clean) |
| Data frame | 11% | Tạo, merge, purge, thay đổi data frame; quyền truy cập của nhóm người dùng |
| Large data sets | 7% | Không đọc/tải/nạp được dữ liệu lớn |
| Logical errors | 2% | Gọi thuộc tính/phương thức không tồn tại |

**Vị trí lỗi theo stage**: cleaning **35%**, ingestion **34%**, integration **21%**; loading và transformation ít nhất.

#### d) Stack Overflow — 6 chủ đề từ 99 bài

```
 Integration    ███████████  (lớn nhất: biến đổi DB, thao tác bảng/data frame, câu hỏi đặc thù nền tảng/ngôn ngữ)
 Ingestion      ████████     (upload kiểu dữ liệu, kết nối DB với nền tảng xử lý)        ┐ integration + ingestion = 47%
 Loading        ██████       (hiệu năng, quy trình kết nối dịch vụ, tính đúng của output)
 Cleaning   ┐   ███          (phần lớn là xử lý missing value)                           ┐ cleaning + transformation = 13%
 Transform. ┘   ███          (thay ký tự, xử lý kiểu dữ liệu...)                          ┘
 Compatibility  ██           8% — KHÔNG thuộc stage nào: code chạy khác nhau giữa OS, khác ngôn ngữ, cài đặt môi trường
```

#### e) Quan hệ giữa các kết quả (Fig. 10 của bài)

- IF góp phần gây ra root cause: ví dụ IF *data type handling* và *data representation* giải thích root cause phổ biến nhất *data type*.
- Các stage nơi lỗi xảy ra phần lớn trùng với chủ đề lập trình viên hỏi; riêng *compatibility* là nhóm câu hỏi tách biệt,
  có thể phản ánh chính root cause *data type*.
- Quan sát của tác giả: lỗi hiếm xuất hiện ở *transformation* — có thể vì biến đổi sai **không gây lỗi ngay** nên không bị phát hiện.

### 1.6 Hạn chế (do tác giả nêu)

- Chỉ góc nhìn kỹ thuật phần mềm/dữ liệu, không xét yếu tố quản lý/kinh doanh.
- Bằng chứng nghiêng về **dữ liệu dạng bảng** hơn các loại dữ liệu khác.
- Chưa xét quan hệ phụ thuộc giữa các IF; xếp hạng mức ảnh hưởng chỉ mang tính tham khảo (mẫu chuyên gia nhỏ).
- Chỉ dùng GitHub và Stack Overflow, phụ thuộc vào tag đã chọn, và dựa trên lấy mẫu.

---

## 2. Automated data processing and feature engineering for deep learning and big data applications: A survey

| | |
|---|---|
| **Tác giả** | Alhassan Mumuni, Fuseini Mumuni |
| **Nguồn** | *Journal of Information and Intelligence* 3 (2025) 113–153 — open access CC BY-NC-ND |
| **Loại bài** | Survey (tổng quan) |
| **File** | `paper/1-s2.0-S2949715924000027-main.pdf` |

### 2.1 Tóm tắt

Deep learning tự động hoá được việc học đặc trưng, nhưng nhiều bước xử lý dữ liệu trong pipeline vẫn làm thủ công:
thu thập, tiền xử lý, tăng cường dữ liệu. Bài survey tổng hợp các kỹ thuật **tự động hoá xử lý dữ liệu** trong pipeline deep learning
và big data, chia làm 3 nhóm tác vụ:

```
                         ┌─ Preprocessing ── imputation · categorical encoding · cleaning · labeling
 Data processing ────────┼─ Data augmentation ── biến đổi dữ liệu có sẵn · sinh dữ liệu bằng generative AI · dataset distillation
 (định nghĩa của bài)    └─ Feature engineering ── feature extraction · feature synthesis (construction) · feature selection
```

Ngoài từng tác vụ riêng lẻ, bài còn trình bày cách **AutoML tối ưu đồng thời mọi giai đoạn** của pipeline, liệt kê các công cụ AutoML
phổ biến, ứng dụng trong công nghiệp và các thách thức còn mở.

### 2.2 Mục tiêu

- Bù khoảng trống: các survey AutoML trước tập trung vào toàn bộ pipeline hoặc công cụ end-to-end, ít đi sâu vào
  **tiền xử lý và feature engineering mức thấp**, và thường chỉ nói về kỹ thuật truyền thống.
- Phân loại các cách tiếp cận tự động hoá theo **mức độ tự động** và theo **tác vụ**.

### 2.3 Khung khái niệm

#### a) Xử lý dữ liệu trong pipeline truyền thống vs. deep learning

| | ML truyền thống | Deep learning |
|---|---|---|
| Cách làm | Mọi bước làm thủ công, **tách rời** (feature extractor viết tay, cố định) | Xử lý dữ liệu được tích hợp vào mô hình và **huấn luyện end-to-end** |
| Khi điều kiện đổi | Phải thiết kế và triển khai lại extractor | Tham số tự điều chỉnh theo phản hồi hiệu năng |
| Lưu trữ | Lưu dữ liệu đã xử lý offline | Xử lý online, không cần lưu thêm mẫu |

Dù vậy, DL vẫn cần xử lý thêm vì: hiệu năng phụ thuộc mạnh vào chất lượng dữ liệu (→ preprocessing), dữ liệu thiếu hoặc không đại diện
(→ augmentation), và bài toán phức tạp/ít dữ liệu hoặc cần giải thích (→ feature engineering).

#### b) Bốn mức độ tự động hoá (Table 2 của bài)

| Mức | Đặc điểm |
|---|---|
| **Basic** | Tiền xử lý độc lập, chủ yếu thủ công hoặc dùng thư viện xử lý chung |
| **Analytical** | Tự động trong pipeline DL nhưng dùng **công thức giải tích** được định nghĩa tường minh |
| **DL (deep-learned)** | Module xử lý **được học** bên trong pipeline ML |
| **AutoML** | Xử lý end-to-end + chọn mô hình + tinh chỉnh siêu tham số |

#### c) Phát biểu hình thức bài toán tiền xử lý tự động

> Cho tập dữ liệu **D** và tập phép tiền xử lý cơ bản **Pᵢ ∈ S** (i = 1..n), tìm cách **chọn và áp dụng** các phép này lên D
> để **tối đa hiệu năng dự đoán** trên tác vụ đích.

Độ khó: phải quyết định phép nào phù hợp, **biến đổi đến mức nào**, và **thứ tự áp dụng**. Phương pháp tiên tiến nhận vào dataset + tập phép
nguyên thuỷ + siêu tham số của chúng (độ mạnh, thứ tự), rồi dùng một thuật toán tối ưu để tìm tổ hợp tốt nhất:

```
 Dataset + {phép tiền xử lý nguyên thuỷ, siêu tham số}
        │
        ▼
 Bộ tìm kiếm: Reinforcement Learning | Gradient Descent | Bayesian Optimization | Evolutionary Algorithm
        │
        ▼
 Pipeline tiền xử lý tốt nhất (phép nào · mức độ · thứ tự)  ──► đánh giá bằng hiệu năng mô hình ──┐
        ▲                                                                                        │
        └────────────────────────────── phản hồi ────────────────────────────────────────────────┘
```

Khó khăn thêm: cùng một phép tiền xử lý cho kết quả rất khác nhau tuỳ **loại dữ liệu và loại mô hình** → nhiều phương pháp
nhận diện kiểu dữ liệu/mô hình trước rồi mới áp dụng phép phù hợp ngữ cảnh. AutoGluon-Tabular dùng **sơ đồ 2 tầng**:
tầng 1 tiền xử lý **không phụ thuộc mô hình**, tầng 2 tiền xử lý **riêng cho từng mô hình**.

### 2.4 Phương pháp — Tự động hoá tiền xử lý (Mục 3)

Các vấn đề mà từng tác vụ tiền xử lý giải quyết (Fig. 8):

| Imputation | Categorical encoding | Cleaning | Labeling / re-labeling |
|---|---|---|---|
| Thiếu điểm dữ liệu, thiếu thuộc tính, thiếu key/metadata, dữ liệu không đủ, mất cân bằng | Chuyển ordinal/nominal sang số, gán trọng số, tương thích giữa hệ thống | Dữ liệu sai, lỗi thứ tự, nhiễu/hỏng, dư thừa, không liên quan, **sai kiểu/hạng mục**, **định dạng không nhất quán** | Chưa có nhãn, lỗi gán nhãn crowdsource, nhãn sai, sai danh pháp, lỗi chính tả trong nhãn, domain shift |

#### a) Imputation (điền giá trị thiếu)

| Hướng | Cách làm | Ví dụ |
|---|---|---|
| Thống kê truyền thống | Dùng tính chất thống kê của dữ liệu quan sát được để phát hiện và tính giá trị thiếu | — |
| **Generative modeling** | Học phân phối của dữ liệu "bình thường", rồi dùng nó để phát hiện và điền giá trị thiếu end-to-end | **GAIN** (GAN), denoising autoencoder, VAE (MIWAE, GP-VAE), scIGANs |
| **AutoML** | Tối ưu **nhiều** mô hình ứng viên bằng **nhiều** thuật toán tìm kiếm để tìm pipeline imputation tốt nhất | **HyperImpute**, Automunge; Auto-Sklearn, Azure Databricks AutoML |
| **Human-in-the-loop** | Tự động phát hiện thiếu → đề xuất giá trị → người dùng chấp nhận/từ chối qua giao diện trực quan | Auto-Prep (Bilal et al.) |

Bài lưu ý: imputation hoàn toàn tự động **có thể làm giảm hiệu năng**, vì xác định giá trị đúng đôi khi cần hiểu ngữ cảnh mà mô hình không có.

#### b) Categorical encoding

- Kỹ thuật truyền thống: binary, ordinal, label, one-hot, target encoding.
- **Khó tự động hoá hoàn toàn** vì khó định nghĩa phép nguyên thuỷ để mô hình tự chuyển hạng mục → số. TPOT, Auto-Keras vẫn encode thủ công;
  Auto-Sklearn có label encoder nhưng cần người dùng khai báo hạng mục; H2O dùng one-hot.
- Một số cách: nhúng encoding truyền thống vào AutoML và dùng **ensemble cây** để đánh giá/chọn phần tử đã encode;
  hoặc dùng **embedding học được** — ví dụ **BERT-Sort** dùng mô hình ngôn ngữ huấn luyện sẵn để hiểu ngữ nghĩa và sắp thứ tự giá trị ordinal.

#### c) Data cleaning

- Lỗi điển hình: sai thứ tự/chỉ mục, gán sai lớp, đặt tên không nhất quán, lỗi chính tả, nhiễu ngẫu nhiên/bất thường (time series),
  bản ghi trùng/không liên quan, thiếu thuộc tính, sai kiểu. Chuẩn hoá, zero-centering, scaling cũng được xếp vào đây.
- Ba cách tự động hoá:

| Cách | Ví dụ |
|---|---|
| **Wrapper mức cao** quanh các hàm làm sạch mức thấp | **CleanTS** — trừu tượng hoá mức ngữ nghĩa cho làm sạch time series (outlier, trùng, kiểu/định dạng không nhất quán) |
| **Học** phép làm sạch dựa trên hiệu năng tác vụ đích | **Learn2Clean** (Q-learning chọn chuỗi phép làm sạch), **BoostClean** (gradient boosting), AlphaClean |
| **Meta-learning** để dùng chung cho nhiều dataset | Rotom và các công trình tương tự |

#### d) Data labeling

- Đa số vẫn thủ công hoặc **bán tự động** (thuật toán đề xuất nhãn, người kiểm duyệt). Tự động hoàn toàn chỉ có ở một số bài thị giác máy tính và ảnh y tế.
- Kỹ thuật: dùng mô hình phân loại/phát hiện/phân đoạn để nhận diện rồi sinh nhãn; **metric learning** so khớp ảnh chưa nhãn với hạng mục đã biết rồi
  chuyển nhãn theo độ tương đồng; khai thác **văn bản đi kèm** (ví dụ báo cáo bệnh học + NLP + ontology).
- Khó khăn: cần nhận biết ngữ cảnh, độ phức tạp từ vựng, mơ hồ ngữ nghĩa, nhãn mang tính chủ quan.

#### e) Tiền xử lý end-to-end

- **Auto-Prep**: tự động điền thiếu, nhận diện kiểu dữ liệu, xoá trùng, encode hạng mục, scale đặc trưng.
- **AutoDC**: phát hiện/xoá outlier, sửa nhãn, chọn edge case, augmentation.
- **Plug-in chuyên tiền xử lý** gắn vào AutoML để tận dụng khả năng tối ưu pipeline: AutoData, DataAssist, BioAutoMATED, Atlantic, **DiffPrep**.
  Ví dụ **AutoData**: người dùng khai báo loại dữ liệu, tác vụ, mục tiêu hiệu năng → RL tìm dữ liệu từ kho bên ngoài → AutoML (Auto-WEKA/Auto-Keras)
  dựng và đánh giá mô hình → phản hồi để tinh chỉnh tìm kiếm.
- AutoML tổng quát chỉ tự xử lý được các bước cơ bản (TPOT, Auto-Keras chỉ phát hiện thiếu dữ liệu); bước phức tạp vẫn cần con người.

#### f) Vì sao khó so sánh hiệu năng các phương pháp tiền xử lý (Mục 3.9)

1. Không có thuật toán chuẩn cho cleaning, labeling, imputation; mục tiêu và cách cài đặt rất khác nhau.
2. Tiền xử lý hiếm khi là **một** phép — thường là chuỗi phép tuần tự/song song; so sánh đòi hỏi pipeline nhất quán, tổ hợp rất lớn.
3. Nhiều quyết định **mang tính chủ quan** (outlier là gì, giữ phần tử nào).

### 2.5 Phương pháp — Tự động hoá data augmentation (Mục 4)

Sơ đồ chung (Fig. 13):

```
 Training set ──► Data sampler (chọn mẫu để augment) ──► Augmenter (chuỗi phép biến đổi) ──► gộp vào batch i ──► Train
                        ▲                                       ▲                                              │
                        └─────────────── training loss phản hồi cho cả sampler và augmenter ───────────────────┘
```

**Bước 1 — sinh phép biến đổi** (tạo không gian tìm kiếm = phép × độ lớn):

| Cách | Mô tả |
|---|---|
| Analytical | Công thức/heuristic tường minh (xoay, cắt, lật, đổi màu) với khoảng độ lớn khai báo trước |
| Deep-learned transformation | Module biến đổi có tham số học được trong mạng, ví dụ **Spatial Transformer Network** |
| Generative | Huấn luyện cặp generator–discriminator để học phân phối thật rồi sinh biến thể; tối ưu song cấp (bi-level) cùng CNN |

**Bước 2 — tối ưu chiến lược augmentation** (chọn phép và mức độ):
- Tối ưu hộp đen: **RL, Bayesian optimization, evolutionary** — tốt nhưng chậm với dữ liệu lớn.
- **Gradient xấp xỉ** cho không gian rời rạc — hiệu quả hơn.
- **Thu gọn không gian tìm kiếm** (ví dụ chuyển về không gian tuyến tính với xác suất đều, duyệt bằng grid search) — nhanh, cạnh tranh, nhưng ít dư địa cải thiện thêm.

**Sinh dữ liệu bằng LLM và diffusion model**: sinh trực tiếp dữ liệu (ảnh, video, văn bản, âm thanh, time series, **dữ liệu bảng**) từ prompt,
dùng để bổ sung hoặc thay thế dữ liệu thật. Diffusion: chuỗi Markov thêm nhiễu dần rồi học quá trình khử nhiễu ngược.

**Dataset distillation**: chọn một tập con nhỏ giữ được khả năng khái quát của tập gốc (cũng dùng để chưng cất nhãn, kể cả nhãn nhiễu). Mức tự động hoá còn hạn chế.

**Kết quả so sánh** (Table 3, backbone WRN-28-10, ~300 epoch): baseline CIFAR-10 96,1% / CIFAR-100 81,2% / ImageNet top-1 76,3%;
tốt nhất trong nhóm tự động đạt 98,7% (KeepAA) / 85,2% (A2-Aug) / 79,9% (AdvAA). Trung bình 10 phương pháp tự động cao hơn 10 phương pháp truyền thống.
Rủi ro được nêu: chi phí tính toán lớn, và biến đổi quá mạnh có thể **làm đổi ngữ nghĩa/nhãn** của mẫu mà không phát hiện lúc huấn luyện.

### 2.6 Phương pháp — Tự động hoá feature engineering (Mục 5)

#### a) Phát biểu hình thức

> Với tác vụ **Tsk** và dataset **D** có tập đặc trưng **F = {f₁..fₙ}**: định nghĩa tập phép biến đổi **T = {t₁..tₙ}**, áp lên F để sinh
> tập đặc trưng mới **Φ**, rồi dùng cơ chế tìm kiếm chọn tập con tốt nhất trong không gian **Ω = F + Φ** để tối đa hiệu năng trên Tsk.

Vì không gian rất lớn, nhiều phương pháp **chia nhỏ không gian tìm kiếm**: ví dụ **VolcanoML** biểu diễn không gian thành cây các
không gian con nguyên tử, ghép theo nhiều cách tuỳ ngân sách tính toán.

#### b) Ba tác vụ con (định nghĩa bài dùng)

| Tác vụ | Định nghĩa | Kỹ thuật tiêu biểu |
|---|---|---|
| **Feature extraction** | Biến đổi dữ liệu thô/đặc trưng trung gian thành đặc trưng gọn, bền, đại diện hơn (thường là tổ hợp tuyến tính) | PCA, ICA, LDA, LLE; trong AutoML: các phép giải tích đơn giản tối ưu song cấp, thường gộp với chọn lọc (ví dụ sinh bằng phép toán rồi chọn bằng **Boruta**); NAS (MetaBu dùng optimal transport trên 135 meta-feature; Tr-AutoML chuyển giao kiến trúc đã học) |
| **Feature synthesis / construction** | Tạo đặc trưng mới từ đặc trưng sẵn có (biến đổi, nội suy, trung bình, trộn) | Xem mục c |
| **Feature selection** | Chọn tập đặc trưng **tối thiểu** cho hiệu năng tốt nhất | ExploreKit (classifier xếp hạng đặc trưng), **AutoDropout** (học mẫu dropout mức đặc trưng bằng tối ưu siêu tham số) |

Lợi ích của feature selection (theo bài): giảm kích thước mô hình, tăng hiệu năng (bỏ đặc trưng có hại), đơn giản cấu trúc, khám phá tri thức, dễ giải thích.
Khó khăn: bài toán **tổ hợp** — một đặc trưng vô ích khi đứng riêng có thể tối ưu khi kết hợp; có thể tồn tại nhiều tập tối ưu.

#### c) Hai chiến lược tổng hợp đặc trưng

| Chiến lược | Cách làm | Nhược điểm |
|---|---|---|
| **Expansion–reduction** (mở rộng rồi thu gọn) | Áp **tất cả** phép biến đổi cùng lúc để mở rộng tập đặc trưng, rồi chọn tập con tốt nhất | Tốn bộ nhớ vì phải lưu lượng đặc trưng lớn |
| **Lặp theo lô nhỏ** | Mỗi vòng áp ít phép → mở rộng → kiểm tra → chọn | Tốn tính toán do đánh giá mỗi vòng; có thể **loại mất** đặc trưng "trung gian" hữu ích cho bước sinh sau |
| **Meta-learning** | Dự đoán trước phép biến đổi nào hiệu quả để ưu tiên sinh và đánh giá | — |

#### d) Feature engineering end-to-end

- **SAFE**: dùng XGBoost tìm tổ hợp đặc trưng tốt theo **information gain**, rút gọn rồi mở rộng và lọc (Fig. 21).
- **EAAFE**, **RTHS**: thuật toán tiến hoá. **NFS**: RNN controller huấn luyện bằng RL sinh chính sách biến đổi.
- **DIFER** (Fig. 22): đưa bài toán về **liên tục, khả vi**:

```
 Khởi tạo quần thể (lấy mẫu ngẫu nhiên đặc trưng)
   └─► Tiến hoá đặc trưng, mỗi vòng:
         · chọn top-d đặc trưng
         · d/2 đặc trưng sinh bởi feature optimizer (encoder–predictor–decoder, leo gradient trong không gian vector)
         · d/2 đặc trưng sinh ngẫu nhiên không trùng (khám phá)
         · đánh giá, thêm vào tập ứng viên
   └─► Chọn lọc: thêm đặc trưng tốt nhất vào dataset, đánh giá mô hình
         · hiệu năng còn tăng và chưa chạm giới hạn → lặp
         · ngược lại → dừng sớm, trả về tập đặc trưng xây dựng F*
```

#### e) Kết quả so sánh

- **Table 5** (Random Forest, 10-fold CV, 23 dataset UCI/OpenML; so Raw, Random, ME, Brute-force/Expansion-Reduction, LFE, NFS, autofeat, DIFER):
  các phương pháp tự động vượt các cách cơ bản, nhưng **không nhất quán** — spambase, autos, convex gần như không cải thiện.
- **Table 6** (LightGBM, 10 lần chạy; Raw, DCN-V2, FCTree, SAFE, Autofeat, AutoCross, OpenFE, FETCH): phương pháp truyền thống đa số **không vượt baseline**;
  phương pháp tự động đôi khi cũng **tụt dưới baseline**; OpenFE thường tốt nhất (ví dụ Diabetes AUC 0,731 → 0,888; Medical RMSE 1128 → 982).
  Kết luận của bài: feature engineering **rất nhạy với dataset**.

### 2.7 Pipeline AutoML end-to-end và công cụ (Mục 6–7)

```
 Dữ liệu ngoài thực tế ─► Xác định dữ liệu liên quan ─► Thu thập ─► Tiền xử lý ─► Feature extraction ─► Feature synthesis
     ─► Feature selection ─► Chọn mô hình ─► Xây dựng mô hình ─► Huấn luyện ─► Kiểm định ─► Mô hình cuối
```

- Pipeline biểu diễn dưới dạng **đồ thị tính toán**; cấu trúc được chọn bằng hàm đánh giá. Có hệ **pipeline cố định** (ATM, ML-Plan, Hyperopt-Sklearn)
  và **pipeline độ dài thay đổi** (AutoDES, FLAML, RECIPE, H2O AutoML — thường dùng tiến hoá: đột biến, lai ghép).
- **AutoSmart**: tiền xử lý, tích hợp (gộp bảng), tổng hợp và chọn đặc trưng, ensemble, tinh chỉnh siêu tham số, kèm **bộ điều khiển thời gian và bộ nhớ**.
- Công cụ: mã nguồn mở (Auto-WEKA, Auto-Keras, PyCaret, TPOT, FEDOT, Auto-Sklearn...) linh hoạt nhưng cần kỹ năng lập trình;
  thương mại (SageMaker Autopilot, Vertex AI, Azure AutoML, DataRobot, H2O Driverless AI...) có GUI, hướng người dùng nghiệp vụ.
  Table 7 của bài liệt kê 23 công cụ theo loại dữ liệu hỗ trợ và tác vụ.

### 2.8 Thách thức do bài nêu (Mục 9.1)

| Thách thức | Nội dung |
|---|---|
| Khối lượng & độ phức tạp dữ liệu | Dữ liệu rất phức tạp vẫn cần con người can thiệp |
| Độ phức tạp bài toán | Labeling, categorical encoding đặc biệt khó tự động |
| Thiếu nhận biết ngữ cảnh | Sinh đặc trưng "mù" → đặc trưng không liên quan hoặc dư thừa |
| Kết quả quá bảo thủ | Mô hình sinh tránh outlier, thiếu biến thiên của dữ liệu thật; hallucination |
| Khả năng thích nghi/chuyển giao | Dữ liệu sinh ra tối ưu cho một tác vụ hẹp; dữ liệu thay đổi theo thời gian |
| Cân bằng nhiều yêu cầu | Kích thước dữ liệu vs thông tin, chính xác vs giải thích được, bền vững, công bằng |
| Độ tin cậy | Phương pháp hộp đen, khó đảm bảo chạy đúng khi triển khai |
| **Thiếu thước đo chuẩn** cho tác vụ tiền xử lý | Mỗi nghiên cứu dùng thiết lập riêng → khó so sánh |
| Khả năng mở rộng | Hoạt động kém trên **dữ liệu nhỏ** (khi đó kỹ thuật truyền thống thường tốt hơn); tốn tính toán |
| Phạm vi hẹp | Đa số tốt nhất với **dữ liệu bảng**, bài toán classification/regression |

Triển vọng: chức năng mức cao (kiểm soát chất lượng, quản lý ngân sách), mở rộng loại dữ liệu, **human-in-the-loop** nâng cao,
hạ tầng chuyên dụng, dữ liệu tổng hợp tự tinh chỉnh dần, sinh dữ liệu có giải thích.

---

## 3. Data preprocessing impact on machine learning algorithm performance

| | |
|---|---|
| **Tác giả** | Alberto Amato, Vincenzo Di Lecce (Politecnico di Bari) |
| **Nguồn** | *Open Computer Science* 2023; 13: 20220278 — open access CC BY 4.0 |
| **Loại bài** | Nghiên cứu thực nghiệm (research article) |
| **File** | `paper/10.1515_comp-2022-0278.pdf` |

### 3.1 Tóm tắt

Bài đánh giá một kỹ thuật tiền xử lý **chưa từng được dùng** cho ML: **SPQR (semi-pivoted QR) approximation** — một thuật toán xấp xỉ
ma trận thưa, hoạt động như **thuật toán chọn đặc trưng (feature selection)**. SPQR được so sánh với **PCA** về tác động lên hiệu năng
của thuật toán phân cụm không giám sát **Fuzzy C-Means (FCM)**, đo bằng **silhouette**, trên 4 dataset công khai của UCI.
Kết luận: SPQR cho kết quả **tương đương PCA** nhưng **không làm thay đổi dữ liệu gốc**.

### 3.2 Mục tiêu

- Kiểm tra giả thuyết: nếu đưa dữ liệu gốc và dữ liệu đã giảm chiều vào cùng một mô hình thì kết quả phải gần như giống nhau.
- Đánh giá SPQR như một bước tiền xử lý cho ML, so với PCA.
- Cho thấy phương pháp tiền xử lý (chuẩn hoá, giảm chiều) có thể ảnh hưởng đáng kể tới hiệu năng thuật toán.

### 3.3 Bối cảnh: ba họ phương pháp giảm chiều mà bài tổng kết

| Họ | Ý tưởng | Ví dụ |
|---|---|---|
| Thống kê / lý thuyết thông tin | Giảm theo tiêu chí thống kê/thông tin; bản lý thuyết thông tin bắt được quan hệ phi tuyến, xử lý cả biến hạng mục | PCA, Isomap, LLE, Hessian LLE, Laplacian eigenmaps, kernel PCA |
| Dựa trên từ điển (dictionary) | Phân rã ma trận dữ liệu, biểu diễn qua "từ điển" gồm các atom | SVD, K-means (trường hợp cực đoan: mỗi vector chỉ dùng một atom), NDR |
| Dựa trên phép chiếu | Chiếu lên không gian con có hướng "thú vị" (thường là phi Gauss) | Projection Pursuit (tối đa kurtosis), **SPQR** |

Lưu ý của tác giả: PCA **chiếu dữ liệu sang hệ trục mới**, nên làm việc trong không gian khác dữ liệu gốc → không nên áp dụng một cách máy móc.

### 3.4 Phương pháp

#### a) Thiết kế thí nghiệm — 6 cấu hình cho mỗi dataset (Fig. 1)

```
                         ┌──► FCM ───────────────► Silhouette      (1) Dữ liệu thô
 Dữ liệu gốc ────────────┼──► PCA ──► FCM ───────► Silhouette      (2) PCA trên dữ liệu thô
 (chỉ cột số)            └──► SPQR ─► FCM ───────► Silhouette      (3) SPQR trên dữ liệu thô
      │
      └─► Chuẩn hoá [0,1] ─┬──► FCM ───────────► Silhouette      (4) Dữ liệu chuẩn hoá
                           ├──► PCA ──► FCM ───► Silhouette      (5) PCA trên dữ liệu chuẩn hoá
                           └──► SPQR ─► FCM ───► Silhouette      (6) SPQR trên dữ liệu chuẩn hoá

 PCA: giữ lại ≥ 98% tổng phương sai (mất < 2%).   Số cụm c chạy từ 10 đến 50.
```

#### b) Thuật toán SPQR (semi-pivoted QR) — trọng tâm của bài

Bài toán gốc là **column subset selection**: từ ma trận A (m thực thể × n thuộc tính), chọn **k < n cột gốc** chứa phần lớn thông tin của A
(theo chuẩn phổ hoặc Frobenius). Có hai họ: *ngẫu nhiên* (chọn cột theo phân phối xác suất) và *tất định* — SPQR thuộc họ tất định (Stewart).

Các bước:

1. **QR có xoay cột (pivoted QR)**: trực chuẩn hoá các cột của A lần lượt bằng Gram–Schmidt; ở **đầu mỗi bước, đổi chỗ để lấy cột lớn nhất còn lại**.
   Kết quả là ma trận hoán vị P sao cho:

   ```
   A · P = Q · R          (Q trực giao, R tam giác trên, đường chéo của R không tăng)
   ```

2. **Phân khối** theo hạng k:

   ```
   [B₁  B₂] = [Q₁  Q₂] · ⎡ R₁₁  R₁₂ ⎤        B₁ = k cột đầu của A·P  (m × k)
                         ⎣  0   R₂₂ ⎦
   Tính chất:   (1) B₁ = Q₁ · R₁₁                     → k cột đầu được tái tạo CHÍNH XÁC
                (2) ‖B₂ − Q₁ · R₁₂‖ = ‖R₂₂‖           → sai số của phần còn lại ĐO ĐƯỢC
   ```

3. **Xấp xỉ**: `A · P ≈ Q₁ · [R₁₁  R₁₂]`. Không cần tính tường minh ma trận trực giao dày Q₁.

4. **Đầu ra**: k cột của A có span xấp xỉ không gian cột của A. Với người dùng, dữ liệu **không bị chiếu sang không gian mới** —
   chỉ là các cột gốc được **sắp lại theo mức quan trọng giảm dần**, rồi giữ k cột đầu.

#### c) PCA — 5 bước (để đối chiếu)

```
 Chuẩn hoá biến ─► Ma trận hiệp phương sai ─► Trị riêng / vector riêng ─► Sắp xếp, chọn thành phần chính ─► Chiếu dữ liệu lên trục mới
```

#### d) Thuật toán phân cụm Fuzzy C-Means

Tối thiểu hàm mục tiêu bình phương tối thiểu tổng quát:

```
 Q = Σᵢ₌₁..c Σₖ₌₁..N  uᵢₖᵐ · ‖xₖ − vᵢ‖²
   c: số cụm · N: số điểm · vᵢ: tâm (prototype) · U = [uᵢₖ]: ma trận thành viên mờ · m > 1: hệ số "mờ"
```

Lặp cập nhật U và các tâm cho tới khi `‖U − U′‖ = maxᵢ,ₖ |uᵢₖ − u′ᵢₖ| < ε`. Sau khi phân cụm, có thể dùng làm bộ phân loại:
mỗi cụm là một lớp, điểm mới x thuộc lớp `j = argminᵢ ‖x − vᵢ‖²`.

#### e) Đánh giá bằng Silhouette (vì dataset không có ground truth)

Với điểm y thuộc cụm A: `t(y)` = khoảng cách trung bình tới các điểm cùng cụm; `v(y) = min_{B≠A} d(y, B)` = khoảng cách trung bình nhỏ nhất tới cụm khác.

```
          ⎧ 1 − t(y)/v(y)    nếu t(y) < v(y)
 s(y) =   ⎨ 0                nếu t(y) = v(y)          −1 < s(y) < +1  (càng gần 1 càng tốt)
          ⎩ v(y)/t(y) − 1    nếu t(y) > v(y)
```

**Thước đo báo cáo**: phần trăm số điểm có silhouette **> 0,7**, **> 0,8**, **> 0,9**, vẽ theo số cụm c = 10..50.

### 3.5 Dữ liệu

| Dataset (UCI) | Kích thước | Ghi chú | Số chiều sau PCA (dữ liệu thô / chuẩn hoá) |
|---|---|---|---|
| Gender Gap in Spanish Wikipedia | 4.746 × 21 | Ước lượng số biên tập viên nữ | 1 / 6 |
| Room Occupancy Estimation | 10.129 × 16 | 7 nút cảm biến (nhiệt độ, ánh sáng, âm thanh, CO₂, PIR), gửi mỗi 30 s | 2 / 5 |
| Myocardial Infarction Complications | 1.700 × 124 | Ma trận thưa, nhiều NaN → chỉ giữ 13 cột không NaN | 6 / 10 |
| TUANDROMD (Android malware) | 4.465 × 241 | Ma trận thưa, nhiều số 0, không NaN | 7 / 7 |

Chỉ dùng các cột số.

### 3.6 Kết quả

- **Chuẩn hoá ảnh hưởng mạnh tới phân cụm**: trên 3/4 dataset, kết quả với dữ liệu chuẩn hoá **kém hơn** dữ liệu thô
  (Gender Gap, Myocardial: kém hơn; Room Occupancy: kém hơn một chút; TUANDROMD: tương đương).
  Giải thích của tác giả: chuẩn hoá có **"hiệu ứng cân bằng"** — mọi chiều có độ dài 1, mang trọng số bằng nhau trong hàm khoảng cách,
  điều này có thể sai về mặt ngữ nghĩa khi các đặc trưng có tầm quan trọng khác nhau.
- **Giảm chiều cải thiện** cả hiệu năng phân cụm lẫn hiệu năng tính toán.
- **SPQR ≈ PCA** về tỉ lệ điểm có silhouette cao (Fig. 26–28, trung bình trên 4 dataset), trong khi SPQR **giữ nguyên dữ liệu gốc**.

So sánh định tính do tác giả rút ra:

| | PCA | SPQR |
|---|---|---|
| Bản chất | Feature **extraction** — chiếu sang trục vector riêng | Feature **selection** — giữ cột gốc, chỉ đổi vị trí |
| Diễn giải đóng góp từng đặc trưng gốc | Khó | Giữ nguyên ý nghĩa cột |
| Điểm dữ liệu mới | Phải biến đổi sang không gian mới mới phân loại được | Dùng trực tiếp |
| Hiệu năng phân cụm trong thí nghiệm | Tham chiếu | Tương đương |

---

## 4. Auto-Validate: Unsupervised Data Validation Using Data-Domain Patterns Inferred from Data Lakes

| | |
|---|---|
| **Tác giả** | Jie Song (University of Michigan), Yeye He (Microsoft Research) |
| **Nguồn** | SIGMOD 2021 — arXiv:2104.04659v2 |
| **Loại bài** | Phương pháp mới + thực nghiệm trên dữ liệu production (một phần đã đưa vào tính năng Auto-Tag của Microsoft Azure Purview) |
| **File** | `paper/2104.04659v2.pdf` |

### 4.1 Tóm tắt

Pipeline dữ liệu chạy định kỳ (BI, ETL, retrain ML) thường hỏng **âm thầm** khi dữ liệu thượng nguồn thay đổi: thêm/bớt cột (**schema drift**),
đổi chuẩn định dạng như `en-us` → `en-US` hoặc lọt giá trị sai như `en-99` (**data drift**). Các công cụ validation khai báo (Google TFDV, Amazon Deequ)
cho phép viết ràng buộc nhưng phải viết **tay từng cột**; phần tự gợi ý ràng buộc của chúng rất yếu với cột **chuỗi**:
TFDV báo động giả trên **> 90%** cột chuỗi, Deequ trên **> 20%**.

Auto-Validate tự suy ra **pattern dạng regex** mô tả "miền giá trị" (data domain) của một cột chuỗi, bằng cách **dùng một kho bảng lớn (data lake)
làm bằng chứng**, với mục tiêu **tối thiểu tỉ lệ báo động giả (FPR)** mà vẫn bắt được nhiều lỗi. Biến thể tốt nhất đạt **precision 0,96 / recall 0,88**.

### 4.2 Mục tiêu và bài toán

- Cho một cột chuỗi **C** quan sát được hôm nay, suy ra luật validation áp dụng cho **dữ liệu tương lai chưa thấy** của cột đó
  (giống train/test trong ML).
- Phạm vi: cột chuỗi có giá trị **đồng nhất, do máy sinh** (khảo sát 1.000 cột thật: 67% thuộc loại này, 33% là ngôn ngữ tự nhiên; chuỗi chiếm 75% số cột).

**Validation khác profiling**:

| | Data profiling (Potter's Wheel, PADS...) | Data validation (bài này) |
|---|---|---|
| Mục tiêu | **Tóm tắt** giá trị đang có trong C | Mô tả **mọi giá trị hợp lệ** của miền, kể cả giá trị chưa xuất hiện |
| Ví dụ cột ngày tháng 3/2019 | `Mar <digit>{2} 2019` (tốt cho tóm tắt) | `<letter>{3} <digit>{2} <digit>{4}` |
| Nếu dùng sai | Pattern quá hẹp → báo động giả khi `Apr 01 2019` đến | Pattern quá rộng như `.*` → không bắt được lỗi nào |

Không gian pattern rất lớn: một cột ngày giờ đơn giản đã có ~**3,3 tỉ** cách tổng quát hoá (riêng ký tự "9" có 7 cách: `9`, `<digit>{1}`, `<digit>+`, `<num>`,
`<alphanum>`, `<alphanum>+`, `<all>`).

### 4.3 Phương pháp

#### a) Ngôn ngữ pattern và không gian giả thuyết

- **Cây tổng quát hoá**: lá là ký tự cụ thể, nút trong là token như `<digit>`, `<letter>`, `<num>`, `<alphanum>`, gốc `<all>`.
- **P(v)**: tập mọi pattern khớp với giá trị v. **Không gian giả thuyết** của cột C:

  ```
  H(C) = ⋂_{v ∈ C} P(v)  \  ".*"          (pattern khớp TẤT CẢ giá trị của C, loại pattern tầm thường)
  ```

- Sinh pattern 2 bước (Algorithm 1): (1) quét mỗi giá trị, sinh token **thô** (`<num>`, `<letter>+`), giữ pattern đủ độ phủ;
  (2) **drill-down** từng pattern thô thành pattern mịn (`<digit>{2}`...) khi vẫn đủ độ phủ. Khung phương pháp **không phụ thuộc** ngôn ngữ pattern cụ thể.

#### b) Ý tưởng cốt lõi: dùng kho bảng T để chấm điểm pattern

Gọi C là **query column** (cột cần sinh luật), D ∈ T là **data column** (cột bằng chứng trong data lake).
Giả định: đa số cột do máy sinh là **đồng nhất** (khảo sát: 87,9% cột đồng nhất). Một pattern h là **xấu** nếu:

1. h **không bao hết** giá trị hợp lệ của miền → gây báo động giả;
2. h **không có đủ cột khớp** trong T → chưa đủ bằng chứng để coi là một miền phổ biến.

Kiểm tra (1): nếu h đúng là miền thì các cột D khớp h phải "thuần". Nhiều cột **"lẫn"** (một phần giá trị khớp h, phần khác không) → h quá hẹp.

```
 Định nghĩa 1 — Impurity của cột D đối với h:      Imp_D(h) = |{v ∈ D : h ∉ P(v)}| / |D|
 Định nghĩa 2 — Nếu D cùng miền với C:             FPR_D(h) = FP/(TN+FP) = Imp_D(h)
 Định nghĩa 3 — FPR ước lượng trên toàn kho:       FPR_T(h) = avg { FPR_D(h) : D ∈ T, ∃v ∈ D khớp h }
 Coverage:                                         Cov_T(h) = số cột trong T có giá trị khớp h
```

Ví dụ trong bài: h₁ quá hẹp (không khớp "PM") → Imp = 2/12; h₂ chỉ cho 1 chữ số giờ → Imp = 8/12; h₅ đúng → Imp = 0.
Nếu 4.800/5.000 cột có FPR 0 và 200 cột có FPR 1% thì FPR_T(h₅) = 0,04%.

#### c) Bài toán tối ưu FMDV (FPR-Minimizing Data Validation)

```
   min      FPR_T(h)
 h ∈ H(C)
   s.t.     FPR_T(h) ≤ r          (r: ngưỡng FPR mục tiêu, ví dụ 0,1%)
            Cov_T(h) ≥ m          (m: số cột bằng chứng tối thiểu, ví dụ 100)
```

Đây là cách tiếp cận **thận trọng**: tìm pattern "an toàn" có FPR nhỏ nhất. **Lemma 1**: trong kịch bản đơn giản (mỗi cột lấy từ đúng một miền,
mỗi miền một pattern thật), với N cột cùng miền trong T và r = 0, nghiệm FMDV hội tụ về pattern thật với xác suất ≥ 1 − (1/2)ᴺ
(pattern "dưới-tổng-quát" bị loại vì vi phạm FPR). Tác giả cũng thử biến thể tối thiểu coverage (CMDV) nhưng FMDV tốt hơn.

#### d) Kiến trúc hệ thống: chỉ mục offline + truy vấn online

```
 OFFLINE (1 lần, quét toàn bộ T)                                  ONLINE (mỗi query column C)
 ┌──────────────────────────────────────────────────────┐         ┌───────────────────────────────────────────┐
 │ Với mỗi cột D ∈ T: liệt kê mọi pattern p ∈ P(D)        │         │ Liệt kê h ∈ H(C)                           │
 │   (chỉ giá trị có ≤ τ token, τ = 8 hoặc 13)            │         │ Tra chỉ mục lấy FPR_T(h), Cov_T(h)          │
 │   tính Imp_D(p)                                       │ ──────► │ Giải FMDV → pattern validation             │
 │ Gộp lại: p ↦ (FPR_T(p), Cov_T(p))                     │  index  │ Độ trễ: hàng chục ms (thay vì hàng giờ)     │
 │ 1 TB dữ liệu → chỉ mục < 1 GB                          │         └───────────────────────────────────────────┘
 └──────────────────────────────────────────────────────┘
```

#### e) Biến thể **Vertical cuts** (FMDV-V) — cột có cấu trúc ghép

Nhiều cột máy sinh là **ghép của nhiều miền con** (ví dụ: số thực + 2 timestamp + chuỗi trạng thái, có cột > 10 miền con). Hai vấn đề: pattern ghép hiếm khi
khớp chính xác trong T (không đạt coverage), và số pattern tăng **theo hàm mũ** theo số token. Giải pháp — **chia dọc** cột thành các cột con:

1. **Lexer** tách mỗi giá trị thành token thô `<symbol>`, `<num>`, `<letter>` (mở rộng token đến khi gặp ký tự khác lớp).
2. **Multi-sequence alignment (MSA)** các chuỗi token (NP-hard → căn chỉnh tham lam từng chuỗi; với dữ liệu máy sinh đồng nhất thường tối ưu).
3. Tìm **k-segmentation** (chia n token thành k đoạn liên tiếp) và pattern cho từng đoạn, mỗi đoạn dài tối đa τ token:

   ```
   (FMDV-V)   min  Σᵢ FPR_T(hᵢ)        s.t.  Σᵢ FPR_T(hᵢ) ≤ r ,   Cov_T(hᵢ) ≥ m  ∀i
   ```

   Dùng **tổng** (giả định bi quan: các dòng vi phạm ở từng đoạn không trùng nhau); dùng `max` (lạc quan) kém hiệu quả hơn.
4. Bài toán có **cấu trúc con tối ưu** → **quy hoạch động** từ dưới lên:

   ```
   minFPR(C[s,e]) = min {  min_{h ∈ P(C[s,e])} FPR_T(h)                      ← không cắt (giải bằng FMDV)
                           min_{t ∈ [s,e−1]} minFPR(C[s,t]) + minFPR(C[t+1,e])  ← cắt đôi tại t }
   ```

   Ví dụ: đoạn token [4,14] là "02/18/2015 00:00:00": không cắt cho FPR 0,004%, cắt thành ngày + giờ cho 0,01% → giữ nguyên.

Lợi ích: có thể **bỏ qua cột rộng hơn τ khi đánh chỉ mục** mà không mất chất lượng, vì lúc truy vấn cột rộng sẽ được ghép từ các miền con.

#### f) Biến thể **Horizontal cuts** (FMDV-H) — cột có giá trị đặc biệt

Ngay cả dữ liệu máy sinh cũng có giá trị **không tuân thủ** (ví dụ `-` cho null, do nhánh xử lý ngoại lệ trong code) → H(C) rỗng.
Cho phép "cắt ngang" bỏ một phần nhỏ giá trị, điều khiển bởi **tham số dung sai θ** (1%, 5%...):

```
 (FMDV-H)  min FPR_T(h)
   s.t.    h ∈ ⋃_{v∈C} P(v) \ ".*"                (lấy từ HỢP, không phải giao)
           FPR_T(h) ≤ r ,  Cov_T(h) ≥ m
           |{v ∈ C : h ∈ P(v)}| ≥ (1 − θ)·|C|      (h phải khớp ít nhất (1−θ) giá trị)
```

- **Định lý 2**: bài toán quyết định của FMDV-H là **NP-hard** (quy về independent set).
- Thực tế: pattern của giá trị bất thường thường **không giao** với pattern giá trị bình thường → giải **tham lam**: bỏ giá trị có pattern không giao với đa số,
  rồi chạy FMDV trên phần còn lại.
- **Kiểm định phân phối giá trị không tuân thủ** khi dữ liệu mới C′ đến: tỉ lệ không khớp lúc huấn luyện `θ_C(h)` và lúc kiểm tra `θ_C′(h)`
  được mô hình hoá là hai phân phối nhị thức; dùng **two-sample homogeneity test** — **Fisher's exact test** hoặc **Pearson Chi-squared có hiệu chỉnh Yates**.
  Chỉ báo lỗi khi bác bỏ giả thuyết H₀ "hai phân phối như nhau" (ví dụ 0,1% → 5% thì báo; 0,1% → 0,11% thì không).

Biến thể đầy đủ **FMDV-VH** kết hợp cả cắt dọc và cắt ngang.

**Độ phức tạp**: offline O(|T|·|P(C)|); online (FMDV-VH) O(|P(C)|·|C|·u(C)²), u(C) là số token tối đa — thực tế < 100 ms/cột.

### 4.4 Thiết kế thực nghiệm

| Hạng mục | Chi tiết |
|---|---|
| Kho dữ liệu | **Enterprise** (data lake Microsoft: 507K file, 7,2M cột) và **Government** (dữ liệu y tế từ NationalArchives.gov.uk: 29K file, 628K cột) |
| Benchmark | Lấy ngẫu nhiên 1.000 cột mỗi kho (B_E, B_G) |
| Chia train/test | 10% giá trị đầu của mỗi cột làm "train" để suy luật; 90% còn lại làm "test" |
| **Precision** | Luật suy từ C_train áp lên C_test của **chính cột đó**: báo lỗi bất kỳ = báo động giả → precision cột = 0 |
| **Recall** | Luật của cột i áp lên **các cột khác** j ≠ i (mô phỏng schema drift / lệch cột): tỉ lệ cột bị báo lỗi đúng. Nếu cột có báo động giả thì recall bị ép về 0 |
| Kiểm chứng | Gán nhãn tay pattern chuẩn cho 1.000 cột của B_E để xác nhận cách đánh giá tự động |
| Đối thủ | Deequ (Cat/Fra — từ điển cố định/một phần), TFDV, Potter's Wheel, SSIS, XSystem, FlashProfile, Grok (60+ regex thủ công), 4 biến thể schema-matching, cận trên FD, cận trên Auto-Detect |

### 4.5 Kết quả

- **Chất lượng** (571 cột trong B_E có pattern cú pháp): **FMDV-VH tốt nhất — precision 0,96, recall 0,88**; thứ tự FMDV-VH > FMDV-H > FMDV-V > FMDV.
  Đối thủ mạnh nhất: Potter's Wheel và SM-I-1. TFDV, Deequ kém trên dữ liệu chuỗi do dùng luật **từ điển** đơn giản. p-value so sánh F-score: 0,001–0,007.
- Đánh giá tự động vs. nhãn tay: (0,961; 0,880) vs. (0,963; 0,915) → cách đánh giá tự động hợp lệ (hơi đánh giá thấp).
- Cận trên của phương pháp dựa trên functional dependency chỉ phủ ~25% số trường hợp Auto-Validate xử lý → hai hướng **bổ trợ** nhau.
- Lỗi còn lại chủ yếu do URL định dạng linh hoạt và hợp của nhiều pattern khác nhau.
- **Độ nhạy**: r điều khiển trực tiếp đánh đổi precision/recall (FMDV-VH ổn định khi r ≥ 0,02); không nhạy với m (khuyên m ≥ 100);
  biến thể có cắt dọc không nhạy với τ nhỏ → khuyên dùng **FMDV-VH với τ = 8** (rẻ, nhanh); không nhạy với θ nếu θ không quá nhỏ.
- **Tốc độ**: FMDV-VH **0,082 s/cột**, nhanh hơn ~2 bậc so với các công cụ profiling (6–7 s/cột). Đánh chỉ mục offline: ~1 giờ (τ = 8) đến ~3 giờ (τ = 13) trên 10 node.
- **User study** (5 lập trình viên ≥ 5 năm kinh nghiệm, 20 cột): 2 người thất bại hoàn toàn; 3 người còn lại mất trung bình **117 s/cột**, precision trung bình **0,47**;
  thuật toán: 0,08 s, precision **1,0**, recall 0,978.
- **Case study Kaggle** (11 tác vụ, XGBoost mặc định): mô phỏng schema drift bằng cách **hoán đổi vị trí cột hạng mục** trong tập test → chất lượng tụt tới **78%**
  (WalmartTrips); Auto-Validate phát hiện drift ở **8/11** tác vụ, **không có báo động giả**.

### 4.6 Hạn chế / hướng mở (do tác giả nêu)

Chỉ áp dụng cho cột chuỗi do máy sinh; chưa xử lý dữ liệu dạng ngôn ngữ tự nhiên (nên dùng validation theo từ điển/set expansion hoặc semantic type)
và **dữ liệu số**. Chỉ xét ràng buộc đơn cột (bổ trợ cho phương pháp đa cột như FD, denial constraints).

---

## 5. Towards Observability for Production Machine Learning Pipelines [Vision Paper]

| | |
|---|---|
| **Tác giả** | Shreya Shankar, Aditya G. Parameswaran (UC Berkeley) |
| **Nguồn** | arXiv:2108.13557v3 (7/2022) |
| **Loại bài** | Vision paper: nêu thách thức nghiên cứu + ý tưởng giải pháp sơ bộ + kiến trúc hệ thống + prototype `mltrace` |
| **File** | `paper/2108.13557v3.pdf` |

### 5.1 Tóm tắt

Duy trì pipeline ML sau khi triển khai rất khó vì (1) **thiếu phản hồi thời gian thực** — nhãn đến muộn hoặc không đến, và (2) **lỗi âm thầm**
có thể xảy ra ở bất kỳ thành phần nào (dịch chuyển phân phối, đặc trưng bất thường). Bài đề xuất một loại hệ thống quản lý dữ liệu mới cung cấp
**observability end-to-end** cho pipeline ML, hỗ trợ 3 việc: **phát hiện (detect) → chẩn đoán (diagnose) → phản ứng (react)** với lỗi.
Hệ thống được thiết kế theo kiểu **"bolt-on"** — bọc quanh công cụ có sẵn, không bắt người dùng viết lại pipeline.

**Observability** (khác monitoring): không chỉ theo dõi các chỉ số định sẵn (*known-unknowns*) mà còn cho phép **đặt câu hỏi mới về hành vi
lịch sử của hệ thống mà không cần thu thập dữ liệu mới** (*unknown-unknowns*, truy vấn "mò kim đáy bể").

### 5.2 Vấn đề và động cơ

| Khía cạnh | Vì sao khó với ML |
|---|---|
| Phát hiện | Nhãn đến **trễ** và chỉ một phần → không đo được accuracy theo thời gian thực. Proxy như khoảng cách phân phối đặc trưng (TFX, SageMaker) cho **quá nhiều báo động giả** |
| Chẩn đoán | Các thành phần đan xen chặt — "changing anything changes everything (CACE)"; lỗi âm thầm như một tập con đặc trưng bị hỏng hoặc **cũ (stale)** |
| Sửa lỗi | Không có đáp án hiển nhiên; sửa thành phần khác nhau cải thiện khác nhau, người dùng không biết nên sửa gì trước |

Hạn chế của công cụ hiện có theo bài: thư viện assertion (Deequ...) **không hướng dẫn nên đặt assertion nào**, khó tái sử dụng, kết quả phải log riêng;
hiệu năng có thể tụt mà **không vi phạm assertion nào**. Kiểm định K-S/Chi-squared trên hàng nghìn đặc trưng gây **"alert fatigue"**,
và với dữ liệu lớn **p-value tiến về 0** dù dịch chuyển không đáng kể. TFX/SageMaker buộc viết lại pipeline bằng DSL riêng.

### 5.3 Khái niệm nền

- **Tuple**: một vector đặc trưng dùng để dự đoán. **Live prediction**: dự đoán sau triển khai. **Feedback** → suy ra **label**.
- **Bucket**: nhóm tuple xác định bởi hội các vị từ trên đặc trưng; **bucketing strategy**: cách gán tuple vào bucket.
- **Pipeline ví dụ** (dữ liệu taxi NYC, dự đoán khách có tip > 20% không; random forest):

```
 Raw data ─► Data cleaning ─► Feature generation ─┬─► Training ─► Models
                                                  └─► Inference ─► Predictions (t=1,2,5…)
                                                                         │ join theo ID
                                     Feedback (nhãn đến muộn: t=3,4,6…) ─┘─► Accuracy (None → Partial → Full)
```

- **Hình thức hoá dịch chuyển phân phối** (X: không gian đặc trưng, Y: không gian nhãn) — mọi định nghĩa quy về ít nhất một trong hai:

| Loại | Điều kiện | Ví dụ |
|---|---|---|
| **Concept shift** | P(Y\|X) đổi; P(Y) đổi nhưng P(X) không | Suy thoái kinh tế → khách tip ít hơn |
| **Covariate shift** | P(X) và P(Y) đổi nhưng P(Y\|X) không | Đêm giao thừa → nhiều chuyến quanh Times Square |

### 5.4 Phương pháp — lộ trình nghiên cứu 3 mũi (Fig. 2)

| | **Detect** | **Diagnose** | **React** |
|---|---|---|---|
| Câu hỏi | Pipeline đang chạy thế nào theo thời gian thực? | Thành phần nào lỗi tại một thời điểm? | Sửa thành phần nào sẽ giải quyết lỗi? |
| Mục tiêu | Theo dõi chỉ số ML tổng thể (accuracy) | Phát hiện lỗi theo **thành phần**, tại **một thời điểm** | Hỗ trợ sửa lỗi **xuyên thành phần, xuyên thời gian** |
| Thách thức | Thiếu nhãn; nhãn trễ | Logging & provenance; ràng buộc tự tinh chỉnh; dịch chuyển tự nhiên | Trễ feedback bất thường; lỗi lan toàn pipeline |

#### a) DETECT — ước lượng accuracy khi thiếu hoặc trễ nhãn

Ba biến thể accuracy cần theo dõi: tích luỹ từ đầu (hoặc reset mỗi ngày), trong cửa sổ thời gian w gần nhất, trên n dự đoán gần nhất.

**Thiếu nhãn → Importance weighting theo bucket**: chia tuple theo bucket, lấy accuracy lúc huấn luyện của từng bucket, trọng số theo số tuple live trong bucket.

```
 Ví dụ (bucket theo khu phố):  train acc  FiDi = 80%, Midtown = 50%
                               live       FiDi = 100 dự đoán, Midtown = 500 dự đoán
 Accuracy ước lượng = (0,8 × 100 + 0,5 × 500) / 600 = 55%
```

Chọn chiến lược bucket là bài toán đa mục tiêu trên O(d!) cách (d = số đặc trưng): **(i) không gian lưu trữ**, **(ii) độ thưa** (bucket mịn có thể rỗng →
không có ước lượng), **(iii) phương sai** accuracy giữa các bucket phải cao, **(iv) khả năng dự báo** (acc train của bucket phải dự báo được acc live).
Gợi ý: stratified sampling trong approximate query processing, ensemble, streaming clustering bền với dịch chuyển (đưa cả tập train vào).

**Nhãn trễ → join hai luồng prediction và feedback** (không giữ được cả hai trong bộ nhớ):
- Mỗi prediction join đúng **một** feedback → lấy mẫu đều trước khi join không bị vấn đề "ít đi bình phương".
- **Reservoir sampling** cả hai luồng với **hàm băm chung** trên ID. Cải tiến đề xuất: giữ reservoir cho prediction **chưa có** feedback +
  **tổng hợp cục bộ (partial aggregates)** cho prediction **đã có** feedback; tuple đã join nhường chỗ — nhưng phải giữ bảo đảm xác suất lấy mẫu đều (khó).
- Cửa sổ trượt: loại tuple hết hạn, hoặc **trọng số suy giảm mũ** ưu tiên tuple mới.
- Trường hợp partial feedback: trộn ước lượng full-feedback và no-feedback, trọng số theo số tuple.
- Ngoài ra theo dõi **business metric** (CTR, doanh thu) và tương quan với ML metric.

#### b) DIAGNOSE — phổ lỗi **hard → soft → drift** (từ gấp nhất tới ít gấp nhất)

| Loại | Ví dụ | Xử lý |
|---|---|---|
| Hard error | Nguồn dữ liệu không ingest được → đặc trưng thiếu | Cần xử lý ngay |
| Soft error | Đặc trưng có trung bình bất thường | Điều tra thủ công, nhiều báo động giả |
| Drift | Dữ liệu tự nhiên tiến hoá, mô hình không còn đúng | Retrain |

**(1) Logging & provenance (bolt-on)**: người dùng gắn **decorator** (Python) vào thành phần, chỉ ra input/output (biến dataframe) → tự log vào
observability store; khi cần truy vết, **DFS trên log** để dựng provenance. Giảm chi phí log: reservoir sample cho tuple dự đoán, mẫu đều cho tuple huấn luyện,
**log histogram** thay vì toàn bộ dữ liệu (histogram thích nghi khi dữ liệu đổi), học từ mẫu truy vấn của người dùng để quyết định log gì.

**(2) Ràng buộc toàn vẹn dữ liệu tự sinh và tự tinh chỉnh**: duy trì ràng buộc thủ công rất tốn công (người dùng mất hàng tháng chuyển hard ↔ soft, chỉnh ngưỡng).
Ý tưởng:

```
 Mô hình tự hồi quy (autoregressive) dự đoán LIKELIHOOD giá trị của một cột cho một tuple, cho trước các cột khác
   · Dùng masking để huấn luyện MỘT mô hình cho mọi cột (thay vì mỗi cột một mô hình)
   · Rời rạc hoá giá trị thành bucket để mô hình học phân phối (theo quantile — nhưng hỏng khi phân phối đổi;
     hoặc tách số thành chữ số như trong language modeling)
   · Gộp likelihood mỗi cột trên cửa sổ trượt
   · Ràng buộc = ngưỡng chung, ví dụ "likelihood gộp của cột > 80%"; chỉnh ngưỡng theo số cột/số tuple để cân bằng precision–recall
```

**(3) Dịch chuyển tự nhiên — adversarial validation**: K-S/KL giữa cửa sổ live và tập train cần giữ cả hai trong bộ nhớ, và p-value → 0 khi dữ liệu lớn
(Fig. 4: mọi đặc trưng đều "có ý nghĩa" < 0,05 suốt cả năm).
- Bộ nhớ: reservoir cho dữ liệu live + **mẫu có trọng số theo loss** của tập train (để không bỏ sót lớp thiểu số).
- Thay kiểm định: huấn luyện **bộ phân loại nhị phân c** phân biệt tuple đến từ **mẫu train** hay **reservoir live**. AUC ≈ 50% → hai tập giống nhau.
- Phiên bản streaming: thay vì tính AUC (nhiều lượt dữ liệu), **log loss của c** (một lượt); mỗi khi reservoir có tuple mới, lấy mẫu 50/50 từ reservoir và train,
  **fine-tune c bằng SGD**. Loss giảm ⇔ AUC tăng ⇔ dữ liệu live tách khỏi train.
- Trên dữ liệu taxi (Fig. 5), thời điểm loss của c báo dịch chuyển **trùng với lúc accuracy mô hình bắt đầu tụt** (cuối 3/2020); các đặc trưng có trọng số cao
  trong c chính là đặc trưng gây dịch chuyển → hỗ trợ chẩn đoán.

#### c) REACT — chỉ ra lỗi nào nên sửa trước

**(1) Phản ứng với trễ feedback**: tìm các nhóm tuple (mô tả bằng ít vị từ, dễ giải thích) có độ trễ nhãn nghiêm trọng — tương tự **frequent itemsets**
nhưng trên luồng, phải hỗ trợ cả **thêm và bớt** tuple (feedback đến muộn), và cửa sổ trượt (time-weighting suy giảm tần suất).

**(2) Hỗ trợ sửa thành phần hỏng** — hai loại lỗi pipeline:

| Loại | Định nghĩa | Ví dụ |
|---|---|---|
| **Staleness** | Dữ liệu **không đổi** khi lẽ ra phải đổi | Pipeline sinh đặc trưng người dùng hỏng → đọc giá trị cũ |
| **Corruption** | Dữ liệu **đổi bất ngờ** | Đổi sang API bản đồ mới trả km thay vì dặm |

Nhận xét chính: hai lỗi này xảy ra theo **cột** (cột là output của logic pipeline), trong khi kỹ thuật làm sạch truyền thống xét theo tập dòng.
Câu hỏi nghiên cứu: **cặp (thành phần, tập cột) nào giải thích tốt nhất việc tụt hiệu năng?** Ba bước:

```
 Bước 1 — Điểm lỗi theo cột (z-score theo thời gian, cửa sổ mùa vụ w, ví dụ 1 tuần):
          x_t  = một phép gộp của Pr[C] tại thời điểm t (ví dụ trung bình của cột, hoặc Pr[C = null])
          ε_t  = | x_t − mean(x_{t−1..t−w}) | / std(x_{t−1..t−w})
          → không cần cột phân phối chuẩn, vì z-score tính trên chuỗi thống kê theo thời gian, không trên giá trị cột.
          Staleness: x_t = độ lệch chuẩn của các trung bình gần đây (cột stale → phương sai thống kê không đổi);
          coi staleness là bài toán phát hiện bất thường để không báo nhầm cột vốn tĩnh.

 Bước 2 — Gom các cột lỗi cùng nhau theo tương quan (ví dụ ma trận hiệp phương sai lấy mẫu + spectral clustering).

 Bước 3 — Xếp hạng trên đồ thị dataflow (Algorithm 1 — ComponentRanking):
          nút = (nhóm cột, thành phần), cạnh theo cạnh của pipeline, trọng số = điểm lỗi.
          Bắt đầu từ nút cuối (predictions), lan truyền điểm ngược lên thượng nguồn bằng TÍCH điểm dọc đường đi, giữ giá trị lớn nhất;
          nút trung gian lỗi nhỏ sẽ làm giảm ưu tiên lỗi phía trước nó → trả về danh sách (nhóm cột, thành phần) sắp theo điểm.
```

**Case study** (hệ gợi ý của một ứng dụng di động, ~20 pipeline ML, mỗi mô hình ~10.000 đặc trưng):
- *Staleness*: pipeline `user_id_features` không chạy nhiều tuần; công cụ thấy điểm corruption cao với x_t = Pr[C = null] (cột ngày càng null),
  và khi cắt theo vùng phổ biến (USA) thấy điểm staleness cao → tìm ra pipeline đã dừng.
- *Corruption*: bản phát hành app mất âm thanh; không ràng buộc hard nào vi phạm, K-S báo động **mọi** cột (vô dụng); công cụ xếp các đặc trưng âm thanh
  (`audio_on`, `num_sound_button_toggles`) điểm cao nhất → tìm ra PR gây lỗi.

### 5.5 Kiến trúc hệ thống bolt-on (Fig. 6)

```
 ┌ Interface layer ─ decorator instrument pipeline · thư viện component tái sử dụng · UI cảnh báo ML metric · dashboard truy vấn log, trực quan hoá
 ├ Execution layer ─ trigger tính metric thô (accuracy xấp xỉ), thông tin mịn, phụ thuộc giữa component · kiểm tra ràng buộc toàn vẹn
 │                   (importance weighting, tinh chỉnh ràng buộc, drift detector, phát hiện bất thường theo thời gian, theo dõi provenance)
 └ Storage layer ─── reservoir sample trong bộ nhớ · dataset tham chiếu (train, live gần đây) ·
                     log mỗi lần chạy component (metric thô, khoảng cách phân phối, vi phạm ràng buộc, tóm tắt input/output, phụ thuộc)
```

**mltrace** (prototype mã nguồn mở) — ba abstraction:

| Abstraction | Nội dung |
|---|---|
| **Component** | Một stage của pipeline: tên (khoá chính), mô tả, owner, tag; hai hook **`beforeRun` / `afterRun`** để chạy kiểm tra/giám sát (ví dụ `TrainingComponent` kiểm tra rò rỉ train-test trước khi chạy và overfitting sau khi chạy) |
| **ComponentRun** | Metadata động của một lần chạy: thời điểm bắt đầu/kết thúc, input, output, snapshot mã nguồn/git hash, cờ staleness, các run phụ thuộc. **Phụ thuộc tự suy ra lúc chạy** theo input/output (run sinh `features.csv` là phụ thuộc của run dùng `features.csv`) |
| **IOPointer** | Định danh chuỗi của input/output (ví dụ `features.csv`, `model.joblib`) + dữ liệu tuần tự hoá |

Người dùng chỉ cần khai báo Component; ComponentRun và IOPointer được tạo tự động qua decorator.

---

## 6. Data Smells in Public Datasets

| | |
|---|---|
| **Tác giả** | Arumoy Shome, Luís Cruz, Arie van Deursen (Delft University of Technology) |
| **Nguồn** | CAIN 2022 (1st Conf. on AI Engineering – Software Engineering for AI) — arXiv:2203.08007v3 |
| **Loại bài** | Nghiên cứu thực nghiệm định tính: phân tích 25 dataset công khai, xây catalogue |
| **File** | `paper/2203.08007v3.pdf` |

### 6.1 Tóm tắt

Tương tự **code smell** trong kỹ nghệ phần mềm, bài đưa ra khái niệm **data smell**: *anti-pattern trong dataset báo hiệu sớm vấn đề hoặc nợ kỹ thuật*
trong hệ thống ML. Phân tích **25 dataset công khai phổ biến** trên Kaggle, tác giả xây dựng **catalogue 14 data smell** chia 5 nhóm, kèm ví dụ thật,
tác hại, ngữ cảnh ngoại lệ và gợi ý khắc phục. Smell phổ biến nhất là **đặc trưng tương quan (19/25 dataset)**.

Lý do bắt lỗi sớm ở dữ liệu: hệ ML thay đổi qua cả **dữ liệu, mô hình, code**, các stage gắn chặt nhau (đổi một chỗ lan ra cả pipeline),
và kiểm thử cần cả chu trình train–test tốn kém → sửa ở thượng nguồn nhanh, dễ, rẻ hơn.

### 6.2 Câu hỏi nghiên cứu

| RQ | Nội dung |
|---|---|
| RQ1 | Các vấn đề chất lượng dữ liệu nào lặp lại trong dataset công khai? |
| RQ2 | Mức độ phổ biến của chúng ra sao? |

### 6.3 Phương pháp — quy trình 3 pha (Fig. 1)

```
 1. Chọn dữ liệu                 2. Phát hiện smell (2 lượt)                     3. Lập catalogue
 Kaggle, sort "Most Votes"  ──►  Lượt 1: phân tích sơ bộ, ghi smell     ──►     Lọc theo tiêu chí loại trừ
 + 4 tiêu chí chọn               Lượt 2: kiểm chứng lại smell cũ                  + tác giả thứ 2 kiểm duyệt
 → 25 dataset                    và tìm smell bị bỏ sót ở dataset trước           → 14 smell, 5 nhóm
```

**Tiêu chí chọn dataset**: IC1 định dạng CSV · IC2 < 1 GB (phân tích được trên laptop) · IC3 dữ liệu có cấu trúc · IC4 chủ yếu đặc trưng số và hạng mục.
25 dataset gồm: abalone, adult, airbnb, avocado, bitcoin, breast-cancer, comic-dc, comic-marvel, covid-vaccine (×2), earthquake, fraud, happiness, heart,
insurance, iris, netflix, permit, playstore, student, suicide, telco, vgsales, wine, youtube (từ 4,5 KB đến 303 MB; 150 đến 4,8 triệu dòng).

**Các bước phân tích lượt 1** (bộ kiểm tra chuẩn ở pha *data understanding* của CRISP-DM), làm thủ công bằng Python + Pandas:

1. Đọc tài liệu đi kèm (nếu có).
2. Xem head và tail — toàn bảng và từng đặc trưng.
3. Xem tên cột và kiểu dữ liệu (schema kỳ vọng).
4. Thống kê mô tả.
5. Kiểm tra giá trị thiếu và dòng trùng.
6. Kiểm tra tương quan giữa các đặc trưng.

Cố ý **không** phân tích phân phối và quan hệ giữa đặc trưng (ngoài tương quan) vì kết quả không khái quát được sang dataset/lĩnh vực khác.

**Tiêu chí loại smell**: EC1 không khái quát được cho dữ liệu có cấu trúc · EC2 chỉ đúng với một ngôn ngữ/công cụ cụ thể (Python/Pandas mà không đúng với R, Matlab, Julia).

### 6.4 Kết quả — Catalogue 14 data smell

| Nhóm | Key | Smell | Số dataset |
|---|---|---|---|
| **Redundant value** (33) | `red-corr` | Đặc trưng tương quan | **19** |
| | `red-uid` | Cột định danh duy nhất | 11 |
| | `red-dup` | Dòng trùng | 3 |
| **Categorical value** (17) | `cat-hierarchy` | Thứ bậc giả do label encoding | 12 |
| | `cat-bin` | Đặc trưng hạng mục cần gộp nhóm (cardinality cao) | 5 |
| **Miscellaneous** (14) | `misc-unit` | Không rõ đơn vị đo | 9 |
| | `misc-balance` | Mất cân bằng lớp | 3 |
| | `misc-sensitive` | Có đặc trưng nhạy cảm | 2 |
| **Missing value** (13) | `miss-null` | Giá trị null | 11 |
| | `miss-sp-val` | Ký hiệu thiếu đặc biệt | 1 |
| | `miss-bin` | Giá trị thiếu mang nghĩa nhị phân | 1 |
| **String value** (12) | `str-num` | Số lưu dưới dạng chuỗi | 5 |
| | `str-sanitise` | Chuỗi có ký tự đặc biệt / khoảng trắng | 5 |
| | `str-human` | Chuỗi định dạng "cho người đọc" | 2 |

Chi tiết từng smell (dấu hiệu → tác hại → cách xử lý theo bài):

| Smell | Dấu hiệu / ví dụ | Tác hại | Gợi ý xử lý |
|---|---|---|---|
| `red-corr` | Hai đặc trưng số có tương quan tuyến tính | Thông tin dư thừa; dataset to, chậm, tốn lưu trữ qua mọi phiên bản thí nghiệm | Feature selection, bỏ đặc trưng dư thừa |
| `red-uid` | Cột id trong youtube, earthquake, netflix, telco, avocado | Mô hình học quan hệ giả giữa id và nhãn → không khái quát; che giấu dòng trùng | Không đưa vào huấn luyện; nhưng có thể khai thác khi phân tích (airbnb: `host_id` lặp → chủ nhà sở hữu nhiều phòng → đặc trưng mới; kết hợp id phát hiện trùng thật và outlier) |
| `red-dup` | Dòng trùng trong heart, insurance, iris (bỏ qua time series vì một sự kiện có thể lặp) | Dataset phình; dễ **overfit** vì học một mẫu nhiều lần | Xoá |
| `cat-hierarchy` | `education` có thứ bậc tự nhiên → label encoding hợp lý; nhưng áp cùng cách cho `sex`, `race` | Tạo **thứ bậc giả** → mô hình coi giá trị số lớn là "hơn" → thiên lệch | One-hot encoding cho đặc trưng không có thứ bậc |
| `cat-bin` | `neighbourhood` (airbnb) > 200 giá trị, nhiều giá trị hiếm; `native-country` 42 giá trị | One-hot tạo không gian đặc trưng rất lớn → tốn bộ nhớ, tính toán | Gộp nhóm: quốc gia → 7 châu lục; dùng `neighbourhood_group` (5 khu) |
| `misc-sensitive` | `sex`, `race` trong adult tương quan với thu nhập | Mô hình chính xác trên dữ liệu lịch sử nhưng **bất công** khi dùng ra quyết định | Bỏ đặc trưng nhạy cảm khi huấn luyện; regularization chống thiên lệch |
| `misc-balance` | fraud: rất ít giao dịch gian lận | Mô hình kém với lớp thiểu số | Metric bền (precision/recall), thêm dữ liệu, cân bằng số mẫu mỗi lớp |
| `misc-unit` | breast-cancer: bán kính, chu vi, diện tích không ghi đơn vị | Lẫn đơn vị → phát hiện outlier sai, lan sang đặc trưng phái sinh; chuẩn hoá (mean removal, scaling) vô nghĩa | Thống nhất đơn vị, ghi tài liệu |
| `miss-null` | permit: 50% thiếu ở cột ngày giờ; bitcoin 25%; covid-vaccine 50% cột số | Thống kê mô tả bỏ qua null → kết luận lệch; bỏ dòng làm **tăng mất cân bằng** ở miền ít dữ liệu | Imputation (mean, median, hồi quy tuyến tính, mô hình dự đoán) |
| `miss-sp-val` | adult dùng `?`; nói chung `nil`, `null`, `-9999`, `-6666` | Công cụ không nhận ra là thiếu; **mã giả số còn tệ hơn** vì công cụ vẫn tính tiếp mà không báo lỗi | Dùng kiểu null khi thu thập; nếu dùng ký hiệu đặc biệt phải ghi tài liệu |
| `miss-bin` | permit: hai cột thiếu 90%, phần còn lại toàn `Y` | Giá trị thiếu thực chất mang nghĩa **"N"**; xoá hoặc impute làm sai thông tin | Dấu hiệu: thiếu tập trung trong **một cột** + giá trị còn lại là phản hồi dương (`true`, `yes`) → điền giá trị âm |
| `str-sanitise` | `?` kèm khoảng trắng (adult); `' M'`, `'F '`, `' I '` (abalone) | Công cụ coi là giá trị khác nhau; càng nhiều hạng mục càng khó làm sạch | **Luôn** cắt khoảng trắng đầu/cuối cột chuỗi; ký tự đặc biệt xử lý theo từng trường hợp |
| `str-num` | `current_ver`, `android_ver` dạng `1.1.9` (playstore) | Mất thông tin số | Tách thành 3 đặc trưng số major/minor/patch |
| `str-human` | `duration` netflix: phim `"90 min"`, series `"2 Seasons"` | Không đồng nhất đơn vị; quy đổi season → phút cần tri thức miền | Chuẩn hoá về một đơn vị số (con của `str-num`) |

**Phân bố**: nhóm Redundant (33 lần) và Categorical (17) phổ biến nhất; Missing (13) và String (12) ít nhất.
Top smell xuất hiện > 10 dataset: `red-corr`, `cat-hierarchy`, `miss-null`, `red-uid`, `misc-unit`. Fig. 2 của bài là histogram 2 chiều smell × dataset.

### 6.5 Các quan sát (Mục Discussion của bài)

- **Thiếu tài liệu**: tên cột khó hiểu (`cp`, `trestbps`, `fbs` trong heart), cột `sex` đã label-encode mà không ghi giá trị nào là nam/nữ.
  Tài liệu dữ liệu tốt nên có: nguồn và quy trình thu thập, các thay đổi đã làm và lý do, **schema kỳ vọng**, tên cột có nghĩa, tình trạng thiếu/trùng,
  tương quan, thống kê mô tả.
- **Nợ kỹ thuật** tích luỹ do thiếu chuẩn hoá ở các bước thượng nguồn; data smell giúp phát hiện khi độ phức tạp còn thấp.
- **Data validation**: công cụ validation/linting kiểm được tính đúng, nhất quán, đầy đủ, thống kê — nhưng **không kiểm được công bằng và độ bền**;
  và viết luật vẫn đòi hỏi hiểu dữ liệu trước. Catalogue smell được xem là **khung để mở rộng hoặc xây mới** công cụ linting/validation.
- **Hiệu quả dữ liệu**: smell nhỏ có thể gây lãng phí chu kỳ huấn luyện lớn.

### 6.6 Hạn chế (do tác giả nêu)

Phân tích **nông** có chủ đích (không phát hiện outlier, không huấn luyện mô hình) để dễ nhân rộng; smell gắn với **phiên bản** dataset;
**chưa định lượng tác động** của từng smell lên hiệu năng mô hình; smell mang tính chủ quan (giảm bằng kiểm duyệt của tác giả thứ hai).

---

## 7. Leakage and the Reproducibility Crisis in ML-based Science

| | |
|---|---|
| **Tác giả** | Sayash Kapoor, Arvind Narayanan (Princeton University) |
| **Nguồn** | arXiv:2207.07048v1 (7/2022) — Princeton University |
| **Loại bài** | Khảo sát liên ngành + taxonomy + đề xuất tiêu chuẩn báo cáo + nghiên cứu tái lập (reproducibility study) |
| **File** | `paper/2207.07048v1.pdf` |

### 7.1 Tóm tắt

ML được dùng rộng rãi để dự đoán trong các ngành khoa học định lượng, nhưng có nhiều cạm bẫy phương pháp, nổi bật là **rò rỉ dữ liệu (data leakage)**.
Qua khảo sát tài liệu, tác giả tìm được **20 bài báo ở 17 lĩnh vực** chỉ ra lỗi, ảnh hưởng tổng cộng **329 bài**; **lĩnh vực nào cũng có leakage**.
Đóng góp:

1. **Taxonomy 8 loại leakage**, từ lỗi giáo khoa đến vấn đề nghiên cứu còn mở.
2. **Model info sheet** — mẫu báo cáo buộc tác giả lập luận rằng mô hình không bị leakage, bao phủ mọi loại trong taxonomy.
3. **Nghiên cứu tái lập** về dự đoán nội chiến (civil war prediction): **mọi** bài tuyên bố mô hình ML phức tạp vượt trội Logistic Regression đều **không tái lập được**
   do leakage; sau khi sửa, ML phức tạp **không tốt hơn đáng kể** LR.

### 7.2 Định nghĩa

> **Data leakage**: mối quan hệ **giả** giữa biến độc lập và biến mục tiêu, phát sinh như **sản phẩm phụ của cách thu thập, lấy mẫu hoặc tiền xử lý dữ liệu**.
> Vì quan hệ giả này không tồn tại trong phân phối mà kết luận khoa học hướng tới, leakage thường **thổi phồng** hiệu năng ước lượng.

- **Phạm vi**: *ML-based science* — dùng hiệu năng mô hình làm bằng chứng cho một kết luận khoa học (khác nghiên cứu phương pháp ML, ứng dụng kỹ thuật, cuộc thi).
- **Reproducible** (định nghĩa rộng hơn *computational reproducibility*): code và dữ liệu có sẵn **và** dữ liệu được phân tích đúng.
  Lỗi trong code làm thay đổi kết luận cũng tính là không tái lập được.

**Vì sao cách chống leakage của cuộc thi / ứng dụng kỹ thuật không áp dụng được cho khoa học**:

| Bối cảnh | Đặc điểm |
|---|---|
| Cuộc thi | Bên thứ ba độc lập tạo dữ liệu và giữ **tập đánh giá ẩn** |
| Ứng dụng kỹ thuật | Có thể thử triển khai quy mô nhỏ; chỉ cần ước lượng thô; dữ liệu lớn, chênh lệch nhỏ ít quan trọng |
| Khoa học dựa trên ML | Người nghiên cứu **có toàn bộ dữ liệu** khi xây mô hình; kết luận **nhạy với chênh lệch nhỏ** |

### 7.3 Phương pháp 1 — Taxonomy 8 loại leakage

```
 [L1] Không tách sạch train / test
       ├─ L1.1  Không có test set (train và test trên cùng dữ liệu)
       ├─ L1.2  Tiền xử lý trên cả train + test (imputation, over/under-sampling trước khi chia...)
       ├─ L1.3  Feature selection trên cả train + test
       └─ L1.4  Dòng trùng → cùng dữ liệu nằm ở cả train và test
 [L2] Mô hình dùng đặc trưng KHÔNG hợp lệ (ví dụ proxy của biến mục tiêu)
 [L3] Test set KHÔNG lấy từ phân phối mà kết luận hướng tới
       ├─ L3.1  Temporal leakage — dự đoán tương lai nhưng test chứa dữ liệu sớm hơn train
       ├─ L3.2  Không độc lập giữa mẫu train và test (cùng người/đơn vị ở cả hai)
       └─ L3.3  Sampling bias trong phân phối test (thiên lệch không gian, thiên lệch chọn mẫu)
```

| Loại | Ví dụ trong bài | Ghi chú/giải pháp bài nêu |
|---|---|---|
| L1.2 | Oversampling trước khi chia → mẫu sinh từ train xuất hiện trong test; imputation dùng chung train + test | Mọi bước tiền xử lý chỉ được "học" trên train |
| L1.3 | Chọn đặc trưng dựa trên thông tin đặc trưng nào tốt trên test | — |
| L2 | Dùng **thuốc hạ huyết áp** làm đặc trưng dự đoán **cao huyết áp**: lúc dự đoán cho bệnh nhân mới sẽ không có thông tin này, và nếu có thì bài toán trở nên tầm thường | Tính hợp lệ cần **tri thức miền**, không chia nhỏ được → người nghiên cứu phải biện minh |
| L3.1 | k-fold CV **xáo trộn** dữ liệu theo thời gian → train chứa dữ liệu muộn hơn test | Test phải luôn có timestamp **muộn hơn** train |
| L3.2 | Histopathology: nhiều quan sát của **cùng bệnh nhân** ở cả train và test, nhưng kết luận nói về bệnh nhân mới | **Block cross-validation** chia theo cấu trúc phụ thuộc; bài toán tổng quát còn khó vì không biết cấu trúc phụ thuộc |
| L3.3 | Loại các ca tự kỷ "ranh giới" (khó nhất) khỏi test; mô hình viêm phổi train ở một bệnh viện không khái quát sang bệnh viện khác | Kiểm thử trên dữ liệu từ đúng phân phối cần kết luận |

Các vấn đề khác trong khảo sát (Table 1): thiếu computational reproducibility (5 bài), **chất lượng dữ liệu** (10 bài — thiếu xử lý giá trị thiếu, dataset nhỏ so với số biến,
biến mục tiêu là proxy kém), **chọn metric sai** (4 bài — accuracy với dữ liệu mất cân bằng), lỗi dù dùng **dataset chuẩn** (7 bài — do không cố định train-test split và metric).

### 7.4 Phương pháp 2 — Model info sheet

Lấy cảm hứng từ *model cards* (Mitchell et al.) và checklist báo cáo, nhưng tập trung vào leakage. Người nghiên cứu phải trình bày **3 lập luận**:

| Lập luận | Nội dung phải chứng minh |
|---|---|
| **[L1] Tách sạch train–test** | Tập test **không tương tác** với dữ liệu train ở bất kỳ bước tiền xử lý, mô hình hoá hay đánh giá nào |
| **[L2] Mọi đặc trưng đều hợp lệ** | Biện minh vì sao từng đặc trưng (hoặc từng nhóm đặc trưng) được phép dùng; một đặc trưng sai là đủ gây leakage |
| **[L3] Test lấy từ phân phối cần kết luận** | Không có sampling/selection bias; làm rõ phân phối mà kết luận hướng tới; phát hiện temporal leakage |

Ánh xạ câu hỏi trong mẫu (Appendix C):

| Leakage | Câu hỏi | Yêu cầu |
|---|---|---|
| L1.1 | Q9–17 | Giải thích cách chia train/test ở **mọi bước** |
| L1.2 | Q12–13 | Cách tách train/test khi **chọn và áp dụng tiền xử lý** |
| L1.3 | Q14–15 | Cách tách train/test khi **chọn đặc trưng** |
| L1.4 | Q10 | Có dòng trùng không, xử lý thế nào |
| L3.2 | Q11 | Các phụ thuộc trong dữ liệu và cách xử lý khi chia |
| L3.3 | Q18–19 | Cách chọn dòng đưa vào phân tích; test khớp phân phối mục tiêu ra sao |
| L3.1 | Q20 | Vì sao cửa sổ thời gian train/test tách biệt và test **luôn muộn hơn** |
| L2 | Q21 | Lập luận tính hợp lệ của từng đặc trưng |

Hạn chế của model info sheet (tác giả nêu): không kiểm chứng được nếu thiếu computational reproducibility; khai báo sai có thể tạo cảm giác an toàn giả;
cần chuyên môn ML để điền và đánh giá; hiểu biết về leakage còn thay đổi → mẫu được **đánh phiên bản**.

### 7.5 Phương pháp 3 — Nghiên cứu tái lập: dự đoán nội chiến

**Quy trình**:

```
 Tìm kiếm có hệ thống (Dimensions DB: "civil" AND "war" AND (prediction|predicting|forecast), 1/2016 – 5/2021) + bài review của lĩnh vực
   → 124 bài → 15 bài tập trung dự đoán nội chiến và đánh giá bằng train-test split → 12 bài chia sẻ đủ code + dữ liệu
   → đọc bài + rà soát code để tìm lỗi → sửa lỗi, giữ mọi lựa chọn khác gần bản gốc nhất → chạy lại
```

**Phát hiện 1 — leakage làm kết quả không tái lập được**: lỗi ở **4/12 bài** — đúng 4 bài tuyên bố ML phức tạp vượt LR; cả 4 đăng ở top-10 tạp chí ngành.

| Bài | Tuyên bố | Lỗi | Sau khi sửa |
|---|---|---|---|
| Muchlinski et al. (2016) | Random Forest vượt xa LR | **L1.2** — impute train và test **cùng nhau** bằng `rfImpute` | RF không hơn LR (AUC RF: 0,94 báo cáo → 0,64) |
| Colaresi & Mahmood (2017) | RF vượt xa LR | **L1.2** — dùng lại dataset đã impute sai của Muchlinski | RF không hơn LR (0,91 → 0,75; LR Fearon–Laitin 0,77 → 0,79) |
| Wang (2019) | AdaBoost, GBT vượt xa các mô hình khác | **L1.2** (dùng lại dataset impute sai) + **L3.1** (k-fold với dữ liệu thời gian) | Chênh AUC AdaBoost – LR giảm từ **0,14 → 0,01** |
| Kaufman et al. (2019) | AdaBoost vượt các mô hình khác | **L2** — dùng các **proxy của biến mục tiêu** (`colwars`, `cowwars`, `sdwars`...) + **L3.1** | AdaBoost không còn vượt LR; **không mô hình nào** thắng baseline "dự đoán bằng kết quả năm trước" |

**Cơ chế leakage do imputation (phân tích Muchlinski et al.)**:
- Tập test out-of-sample **thiếu > 95% giá trị**, 70/90 biến thiếu hoàn toàn (không được nêu trong bài gốc).
- Mô hình impute được cho xem toàn bộ train **và nhãn của tập test** (nhãn được đưa vào làm biến độc lập khi impute) → điền giá trị thiếu ở test dựa trên tương quan
  nhãn–đặc trưng học từ train → test mang **cùng tương quan** như train.
- Trực quan hoá biến `agexp` (Fig. A1): giá trị được impute cho lớp *war* và *peace* **tách rời hoàn toàn** (dữ liệu gốc thì chồng lấn), dồn vào một khoảng hẹp →
  RF học được "khoảng hẹp" này, còn LR (hàm đơn điệu, một tham số/đặc trưng) thì không → giải thích vì sao RF "thắng".
- **Mô phỏng** (Fig. A2): `gdp = N(0,1) + onset`, 1.000 mẫu mỗi lớp, chia 50/50, xoá ngẫu nhiên 0–95% giá trị `gdp` rồi impute train + test chung,
  lặp 100 lần → accuracy "out-of-sample" **tăng dần theo tỉ lệ thiếu** — ước lượng bị thổi phồng giả tạo.
- **Cách sửa**: dùng `mice` (multiple imputation) cho phép chỉ định dòng nào thuộc test để **không dùng chúng khi xây mô hình impute**; hoặc impute train và test **riêng**
  (trong từng fold khi cross-validation).
- Lưu ý của tác giả: trong mô hình hoá **dự đoán**, imputation là **một phần của bước mô hình hoá** (không phải tiền xử lý độc lập như mô hình hoá giải thích);
  và cách impute nên **mô phỏng kịch bản triển khai** — nếu lúc triển khai mẫu đến từng cái một thì impute cả lô test cũng có thể lạc quan quá mức.

**Các lỗi khác ở Kaufman et al.**: chọn tham số Lasso sai (mô hình luôn dự đoán *peace*) → sửa bằng `cv.glmnet`; **thay giá trị thiếu bằng 0**
(mô hình không phân biệt được 0 thật và 0 do thiếu); chọn cutoff từ phân phối điểm thay vì từ train; **baseline yếu** (luôn đoán *peace*: accuracy 86,1%)
so với baseline mạnh hơn "lặp lại kết quả năm trước" (97,5%, kiểm định McNemar χ² = 633,7); nhầm lẫn biến mục tiêu (*onset* vs *ongoing* civil war).
Biến bị loại/thay bằng bản trễ (lagged): `pop`, `lpop`, `polity2`, `gdpen` (bị biến mục tiêu ảnh hưởng → dùng bản trễ); `onset`, `ethonset`, `durest`, `aim`, `ended`,
`ethwar`, `emponset`, `sdwars`, `sdonset`, `colwars`, `colonset`, `cowwars`, `cowonset` (proxy trực tiếp hoặc NA khi không có nội chiến → loại).

**Phát hiện 2 — thiếu kiểm định ý nghĩa và định lượng bất định**: 9/12 bài không có kiểm định thống kê hay khoảng tin cậy. Ví dụ Blair & Sambanis (2020):
test chỉ có **11** ca khởi phát nội chiến; AUC làm mượt 0,85 nhưng **khoảng tin cậy 95% (bootstrap) là [0,66 – 0,95]**; so sánh với các baseline không có ý nghĩa
(p = 0,14–0,34); kết quả còn nhạy với việc tính AUC trên ROC **làm mượt** thay vì ROC thực nghiệm.

### 7.6 Năm chẩn đoán và khuyến nghị (ngoài leakage)

| Chẩn đoán | Khuyến nghị |
|---|---|
| D1 Không hiểu **giới hạn của dự đoán** (nhầm thành công ở nhận dạng ảnh với dự đoán kết quả xã hội) | R1 Nghiên cứu và truyền thông giới hạn dự đoán; xác định cận trên độ chính xác (cận dưới Bayes error) |
| D2 Thổi phồng, lạc quan quá mức, thiên lệch xuất bản | R2 Coi kết quả ML-based science là **tạm thời** |
| D3 Thiếu chuyên môn (chuyên gia miền thiếu kiến thức ML và ngược lại) | R3 Hợp tác liên ngành, phổ biến best practice |
| D4 Thiếu **chuẩn hoá** (train-test split, metric) | R4 Dùng **common task framework**: dữ liệu train và metric thống nhất, holdout bí mật, leaderboard công khai |
| D5 Thiếu computational reproducibility | R5 Đảm bảo tái lập tính toán (ví dụ CodeOcean tái tạo đúng môi trường) |

---

## 8. DiffPrep: Differentiable Data Preprocessing Pipeline Search for Learning over Tabular Data

| | |
|---|---|
| **Tác giả** | Peng Li, Zhiyi Chen, Xu Chu, Kexin Rong (Georgia Institute of Technology) |
| **Nguồn** | SIGMOD 2023 (Proc. ACM Manag. Data, Article 183) — arXiv:2308.10915v1 |
| **Loại bài** | Phương pháp mới (AutoML cho tiền xử lý) + thực nghiệm |
| **File** | `paper/2308.10915v1.pdf` — mã nguồn: `github.com/chu-data-lab/DiffPrep` |

### 8.1 Tóm tắt

Thiết kế pipeline tiền xử lý dữ liệu bảng tốn nhiều công thử-sai (ước tính chiếm tới 80% thời gian data scientist). Các hệ AutoML hiện có
có **không gian tìm kiếm hẹp** và **tối ưu chậm** (phải huấn luyện mô hình nhiều lần). **DiffPrep** tự động tìm pipeline tiền xử lý **cho từng đặc trưng**
(chọn loại biến đổi, thứ tự, toán tử) sao cho hiệu năng của một mô hình **khả vi** là tốt nhất, bằng cách:

1. phát biểu bài toán là **tối ưu hai cấp (bi-level)**;
2. **nới lỏng** không gian rời rạc thành liên tục, khả vi (softmax + Sinkhorn);
3. giải bằng **gradient descent**, **chỉ huấn luyện mô hình một lần**.

Kết quả: tốt nhất trên **15/18** dataset thật, tăng test accuracy tới **6,6 điểm phần trăm**.

### 8.2 Mục tiêu — hai hạn chế của AutoML hiện có

| Hệ thống | Chọn toán tử | Chọn loại | Chọn thứ tự | Theo từng đặc trưng | Cách tối ưu |
|---|---|---|---|---|---|
| H2O | ✗ | ✗ | ✗ | ✗ | (pipeline mặc định cố định) |
| Azure AutoML | ✓ (chỉ chuẩn hoá) | ✗ | ✗ | ✗ | Random search |
| Auto-Sklearn | ✓ | ✓ | ✗ | ✗ | Bayesian optimization |
| Learn2Clean | ✓ | ✓ | ✓ | ✗ | Q-learning |
| **DiffPrep-Fix** | ✓ | ✓ | ✗ (người dùng cho) | **✓** | **Bi-level + gradient descent** |
| **DiffPrep-Flex** | ✓ | ✓ | **✓** | **✓** | **Bi-level + gradient descent** |

Không gian theo từng đặc trưng tăng **theo hàm mũ**: nếu mỗi đặc trưng có p pipeline thì d đặc trưng có pᵈ tổ hợp → random search/BO không mở rộng được.

### 8.3 Khái niệm hình thức

| Khái niệm | Định nghĩa |
|---|---|
| **TF operator** (toán tử biến đổi) | Hàm `o: X₁ → X₂` biến đổi **một đặc trưng vô hướng** (feature-wise). Không xét toán tử vector→vector như PCA. 14/18 toán tử trong `sklearn.preprocessing` thuộc loại này. Toán tử có tham số được rời rạc hoá thành nhiều toán tử: Z-score(2), Z-score(3), Z-score(4) |
| **TF type** (loại biến đổi) | Tập toán tử cùng mục đích: `τ = {o₁, o₂, ...}` |
| **Prototype** | Dãy có thứ tự các TF type, **không lặp** (muốn lặp thì khai báo 2 type khác tên): `T = {τ₁, τ₂, ...}` |
| **Pipeline** | Chọn một toán tử cho mỗi type trong prototype: `G_T = {o₁, o₂, ...}`, `oᵢ ∈ τᵢ`; xᵢ = oᵢ(xᵢ₋₁), x₀ = x, G_T(x) = x_L |

Không gian tìm kiếm dùng trong bài (Table 1):

| TF type | Đặc trưng số | Đặc trưng hạng mục |
|---|---|---|
| Missing value imputation | Mean, Median, Mode | Most frequent value, Dummy variable |
| Normalization | Standardization, Min-Max, Robust scaling, Max-Abs scaling | — |
| Outlier removal | Z-score(k), MAD(k), IQR(k) | — |
| Discretization | Uniform(k), Quantile(k) | — |

Lý do giới hạn tập toán tử: không gian tuỳ biến tuỳ ý quá lớn và **tăng nguy cơ overfit** khi đồng tối ưu với mô hình; các toán tử chọn đều "có tri thức trước":
outlier removal/imputation chỉ tác động tập con nhỏ, chuẩn hoá/rời rạc hoá chỉ co giãn/dịch phân phối chứ không bóp méo.

**Quy trình thủ công mà DiffPrep tự động hoá** (Fig. 3): (1) khám phá dữ liệu → (2) **chọn prototype** (loại nào, thứ tự nào — ví dụ outlier removal trước hay sau
normalization cho kết quả khác hẳn vì thống kê min/max thay đổi) → (3) **chọn toán tử** (KNN hợp min-max, LR hợp standardization — nhưng heuristic không luôn đúng)
→ (4) đánh giá pipeline bằng train/test mô hình → lặp lại.

### 8.4 Phát biểu bài toán (DPPS — Data Preprocessing Pipeline Search)

Mỗi mẫu có d đặc trưng x = [x¹..xᵈ]; đặc trưng thứ j có prototype Tʲ và pipeline G_Tʲ; mô hình h_θ.

```
   min           L_val( G_T¹, ..., G_Tᵈ, θ* )                         ← cấp ngoài: chọn pipeline để tối thiểu loss VALIDATION
 G_T¹..G_Tᵈ
   s.t.   θ* = argmin_θ  L_train( G_T¹, ..., G_Tᵈ, θ )                ← cấp trong: huấn luyện mô hình trên dữ liệu đã biến đổi
```

Dùng **hai cấp** thay vì tối ưu một cấp (cả pipeline lẫn mô hình trên loss train) vì một cấp **dễ overfit** (kinh nghiệm từ DARTS).
Cách ngây thơ (thử mọi pipeline) có `mᴸᵈ` tổ hợp cho một prototype (L type, m toán tử/type, d đặc trưng) → không khả thi.

### 8.5 Phương pháp — DiffPrep-Fix (thứ tự cố định)

**Bước 1 — Tham số hoá**: với mỗi đặc trưng, ma trận nhị phân **β (L × m)**: `βᵢⱼ = 1` nếu chọn toán tử oᵢⱼ cho type τᵢ; mỗi hàng đúng một số 1.

```
 Ví dụ: T = {τ₁, τ₂, τ₃}, mỗi type 4 toán tử, pipeline {o₁₂, o₂₁, o₃₄}:
        β = ⎡0 1 0 0⎤        Đầu ra từng bước:   xᵢ = Σⱼ βᵢⱼ · oᵢⱼ(xᵢ₋₁)          (2)
            ⎢1 0 0 0⎥
            ⎣0 0 0 1⎦
```

**Bước 2 — Nới lỏng khả vi**: cho βᵢⱼ ∈ [0,1] và giữ ràng buộc tổng hàng = 1 bằng **softmax** trên tham số nền α:

```
 βᵢⱼ = exp(αᵢⱼ) / Σₖ exp(αᵢₖ)       → βᵢⱼ = XÁC SUẤT chọn oᵢⱼ;  công thức (2) cho GIÁ TRỊ KỲ VỌNG của dữ liệu biến đổi
```

**Bước 3 — Giải bi-level bằng gradient descent** (Algorithm 1, theo DARTS):

```
 lặp đến hội tụ:
   α ← α − η₁ · ∇_α L_val( β(α), θ − η₂ ∇_θ L_train(β(α), θ) )     ← xấp xỉ θ* bằng MỘT bước gradient: θ′ = θ − η₂∇_θ L_train
   θ ← θ − η₂ · ∇_θ L_train( β(α), θ )
 (thực tế đặt η₁ = η₂ để khỏi tinh chỉnh hai learning rate)
```

Gradient theo α (quy tắc chuỗi) gồm 3 phần: g₁ = ∇_α β (từ softmax), g₂ = ∇_β L_val(β, θ′), và g₃ chứa **đạo hàm bậc hai** — xấp xỉ bằng **sai phân hữu hạn**:

```
 g₃ ≈ [ ∇_β L_train(β, θ⁺) − ∇_β L_train(β, θ⁻) ] / 2ε ,     θ± = θ ± ε · ∇_θ′ L_val(β, θ′)
```

**Toán tử là hộp đen**: không biết thuật toán bên trong (để người dùng thêm toán tử tuỳ biến) → đạo hàm của toán tử theo input xấp xỉ số:
`∂oᵢⱼ/∂xᵢ₋₁ ≈ [oᵢⱼ(xᵢ₋₁ + ε) − oᵢⱼ(xᵢ₋₁ − ε)] / 2ε`.

**Mẹo để dùng autodiff (PyTorch/TensorFlow) với toán tử hộp đen** — viết lại lan truyền xuôi:

```
 xᵢ = Σⱼ βᵢⱼ·õᵢⱼ  +  xᵢ₋₁ · Σⱼ β̃ᵢⱼ·g̃ᵢⱼ  −  x̃ᵢ₋₁ · Σⱼ β̃ᵢⱼ·g̃ᵢⱼ
   õᵢⱼ = oᵢⱼ(xᵢ₋₁) (output hộp đen) · g̃ᵢⱼ = đạo hàm số · dấu ~ = hằng số không mang gradient (.detach() / stop_gradient)
 → lan truyền xuôi cho ĐÚNG giá trị như (2); lan truyền ngược cho ĐÚNG gradient với đạo hàm toán tử thay bằng đạo hàm số.
```

**Algorithm 2 — DiffPrep-Fix**:

```
 Khởi tạo α, θ
 lặp đến hội tụ:
   1. FIT lại mọi TF operator trên dữ liệu train ĐÃ BIẾN ĐỔI tới bước trước nó
      (ví dụ standardization tính mean/std trên xᵢ₋₁; vì xᵢ₋₁ phụ thuộc β nên phải fit lại mỗi vòng)
   2. Lan truyền xuôi: tính L_train(β, θ⁺), L_train(β, θ⁻), L_val(β, θ′)
   3. Lan truyền ngược: các gradient tương ứng theo β
   4. Tính ∇_α L_val ; cập nhật α (Adam) ; cập nhật θ (SGD)
 trả về β(α), θ
```

**Độ phức tạp**: số tham số L × m × d. Mỗi vòng thêm 3 lượt xuôi + 3 lượt ngược so với huấn luyện thường; dùng **mini-batch** để fit toán tử và cập nhật α.

### 8.6 Phương pháp — DiffPrep-Flex (thứ tự tự học)

- Thêm **toán tử identity** `I(x) = x` vào mỗi type → chọn identity = **bỏ** type đó. Khi đó prototype chỉ còn là **một hoán vị** của mọi type
  (n type → n! hoán vị, d đặc trưng → (n!)ᵈ).
- Tham số hoá thứ tự bằng **ma trận hoán vị P (n × n)**: `Pᵢⱼ = 1` nếu type ở vị trí i là τⱼ (mỗi hàng và mỗi cột đúng một số 1).

```
 Ví dụ: S = {τ₁, τ₂, τ₃}, prototype {τ₂, τ₃, τ₁}:  P = ⎡0 1 0⎤      Đầu ra: xᵢ = Σⱼ Σₖ Pᵢⱼ · βⱼₖ · oⱼₖ(xᵢ₋₁)
                                                       ⎢0 0 1⎥
                                                       ⎣1 0 0⎦
```

- **Nới lỏng P** thành **ma trận ngẫu nhiên kép** (doubly stochastic — tổng mỗi hàng và mỗi cột = 1) bằng **chuẩn hoá Sinkhorn**: lặp xen kẽ chuẩn hoá hàng `R` và cột `C`
  trên ma trận không âm, `S(X) = lim_{l→∞} Sˡ(X)`, với `P = S(γ)` (γ là tham số nền không âm). Quá trình khả vi → Pᵢⱼ = xác suất τⱼ đứng ở vị trí i.
- **Algorithm 3 — DiffPrep-Flex**: như Algorithm 2 nhưng mỗi vòng tính gradient theo **cả γ (thứ tự) và α (toán tử)**, cập nhật cả hai rồi cập nhật θ.

Kiến trúc tổng thể:

```
 Đặc trưng xʲ ─► [ Pipeline có tham số (γʲ: thứ tự, αʲ: toán tử) — mỗi đặc trưng một bộ tham số riêng ] ─► đặc trưng đã xử lý ─► Mô hình h_θ ─► loss
                                    ▲                                                                                              │
                                    └─────────────── gradient của L_val (theo γ, α) ; gradient của L_train (theo θ) ──────────────┘
```

### 8.7 Thiết kế thực nghiệm

| Hạng mục | Chi tiết |
|---|---|
| Dữ liệu | 18 dataset OpenML (1.460 – 88.588 dòng, 6 – 81 đặc trưng, 2 – 28 lớp; một số có nhiều giá trị thiếu/outlier — outlier đếm theo Z-score > 3) |
| Chia | train / val / test = **60 / 20 / 20** ngẫu nhiên |
| Mô hình | **Logistic Regression** (khả vi); kiểm tra thêm mạng 2 lớp 100 nơ-ron ReLU |
| Ràng buộc không gian | Imputation **luôn đứng đầu** và không có identity (vì đa số toán tử sklearn không nhận giá trị thiếu); sau imputation, one-hot cho hạng mục |
| DP-Fix | Thứ tự {imputation, normalization, outlier removal, discretization} |
| Đối thủ | **Default** (mean/most-frequent + standardization, như H2O), **RandomSearch** (20 lần, cùng pipeline cho mọi đặc trưng), **Auto-Sklearn** (chỉ bộ tiền xử lý, giới hạn 1 giờ), **Learn2Clean** (Q-learning), **BoostClean** (boosting trên 50 pipeline ngẫu nhiên, ensemble 5) |
| Huấn luyện | SGD cho θ, Adam cho tham số pipeline; batch 512; 1.000 epoch; lấy epoch có val loss nhỏ nhất |
| Thước đo | Test accuracy và thời gian chạy end-to-end |

### 8.8 Kết quả

**Độ chính xác** (Table 2, Logistic Regression):
- Pipeline khác nhau → hiệu năng chênh rất lớn (wall-robot-nav: > 20%).
- DiffPrep (Fix + Flex) tốt nhất **15/18** dataset, hơn baseline tốt nhất > 1% trên 9 dataset; run_or_walk **+6,6%**, obesity **+5,5%**, connect-4 **+4,2%**.
  Trên connect-4 (rất nhiều outlier), DP-Fix chọn Z-score cho một số đặc trưng và **bỏ qua** (identity) cho đặc trưng khác — lợi ích của pipeline theo đặc trưng.
- DP-Fix và DP-Flex lần lượt vượt baseline tốt nhất trên 11 và 13 dataset; hai bản chênh < 2% trên 17/18 dataset (thứ tự mặc định thường đã tối ưu).
- RandomSearch hơn Default trên 15/18 (wall-robot-nav +17,5%, run_or_walk +11%) → **một pipeline mặc định cho mọi dataset không phải chiến lược tốt**.
- BoostClean thua DiffPrep 17/18; yếu ở đa lớp do one-vs-all gây mất cân bằng. Auto-Sklearn ≈ RandomSearch (cùng không gian). Learn2Clean kém nhất (Q-learning tìm không hiệu quả).

**Thời gian**: Default nhanh nhất; RandomSearch ~20× Default; Auto-Sklearn ~1 giờ cố định; BoostClean ~50× (còn chậm hơn với đa lớp); **DP-Fix ≈ ½ RandomSearch (~10× Default)**,
DP-Flex ≈ RandomSearch; tăng **tuyến tính** theo kích thước dữ liệu. Với mạng 2 lớp, DP-Fix chỉ chậm 2–3× và DP-Flex 6–7× so với Default
(chi phí thêm chủ yếu do phải gọi lại toán tử mỗi vòng vì pipeline "động").

**Phân tích độ nhạy**:
- Mô hình phi tuyến (mạng 2 lớp): vẫn tốt nhất 10/18 dataset.
- **Kích thước tập validation**: val 1% → overfit tập val (test kém); 1% → 25% cải thiện rõ; 25% → 50% ít khác biệt; quá lớn (99%) → mô hình overfit tập train nhỏ.
  Kết luận: **chia train:val = 60:20 là đủ tốt**.

**Ablation**:
- Tắt pipeline theo đặc trưng (mọi đặc trưng dùng chung α): accuracy giảm trên **14/18** dataset (run_or_walk −4,5%, connect-4 −4,4%). Dù vậy vẫn tốt nhất 7/18,
  vì tham số liên tục tương đương **tổ hợp nhiều toán tử** cho mỗi type.
- DP-Fix với **thứ tự tệ nhất**: giảm mạnh (mozilla4 −6,9%); DP-Flex tốt hơn bản này trên 13/18 → Flex an toàn cho người ít kinh nghiệm, và cần thiết khi thêm type tuỳ biến.
- Tối ưu **một cấp** trên loss train: thua bi-level trên 12/18 (hoà 2), nhưng chênh < 1% trên 17/18 nhờ tinh chỉnh learning rate trên val và early stopping.

**Case study dữ liệu tổng hợp** (tiêm 10% giá trị thiếu, biết ground truth): DiffPrep có accuracy mô hình tốt nhất trên cả 3 dataset, nhưng phép impute nó chọn **không
phải** phép có RMSE tốt nhất (wall-robot-nav: RMSE của DP-Flex tệ nhất nhưng accuracy cao nhất) → **chọn toán tử thuần theo chất lượng dữ liệu không đảm bảo
hiệu năng mô hình tốt nhất**; phải xét cùng các toán tử khác và mô hình.

**Kết hợp feature extraction**: dùng random forest làm bộ trích đặc trưng (embedding nút lá + xác suất dự đoán), nối vào dữ liệu gốc (số đặc trưng tăng lên ~330–470) rồi đưa vào DiffPrep:
accuracy tăng đáng kể trên **16/18** dataset (Auto-Sklearn bật feature processor: 11/18, và giảm trên một số dataset).

### 8.9 Hạn chế (do tác giả nêu)

Chỉ áp dụng khi mô hình cuối **khả vi**; chưa hỗ trợ mô hình không khả vi như random forest. Chỉ xét toán tử từng đặc trưng (không xét PCA, entity resolution).

---

## 9. Data Cleaning and Machine Learning: A Systematic Literature Review

| | |
|---|---|
| **Tác giả** | Pierre-Olivier Côté, Amin Nikanjam, Nafisa Ahmed, Dmytro Humeniuk, Foutse Khomh (Polytechnique Montréal) |
| **Nguồn** | *Automated Software Engineering* (2024) — arXiv:2310.01765v2 |
| **Loại bài** | Tổng quan tài liệu có hệ thống (SLR) theo hướng dẫn Kitchenham |
| **File** | `paper/2310.01765v2.pdf` |

### 9.1 Tóm tắt

Hiệu năng mô hình ML phụ thuộc mạnh vào chất lượng dữ liệu huấn luyện, và ngược lại ML cũng được dùng để làm sạch dữ liệu — một **quan hệ hai chiều**:
**DC4ML** (Data Cleaning for ML) và **ML4DC** (ML for Data Cleaning), gọi chung **DC&ML**. Bài tổng hợp **101 bài báo (2016–2022)**, phân loại thành
**6 hoạt động làm sạch**: feature cleaning, label cleaning, entity matching, outlier detection, imputation, holistic data cleaning; và đưa ra **24 hướng nghiên cứu**.

**Data cleaning** (định nghĩa bài dùng): phát hiện hoặc sửa các bản ghi hỏng, trùng, thiếu, sai hoặc nhiễu để nâng chất lượng dataset.

### 9.2 Câu hỏi nghiên cứu

| RQ | Nội dung |
|---|---|
| RQ1 | Các kỹ thuật làm sạch dữ liệu mới nhất trong DC&ML là gì? (chia thành RQ1.1–1.6 theo 6 hoạt động) |
| RQ2 | Cơ hội nghiên cứu tương lai? |

### 9.3 Phương pháp SLR

**Phạm vi**: dữ liệu **bảng, ảnh, văn bản** (loại phổ biến nhất trong ứng dụng ML). Bài 1/2016 – 17/10/2022.

**Chuỗi tìm kiếm**: `(ML terms: machine learning | deep learning | neural network(s) | reinforcement learning | supervised | unsupervised) AND
(data cleaning | cleansing | scrubbing | data repair(ing) | error repair(ing) | confident learning | label cleaning | ("error detection" AND (tab* | cell* | row* | image* | text*)))`
— giới hạn "error detection" theo loại dữ liệu vì cụm này quá rộng. Google Scholar có giới hạn riêng (truy vấn ≤ 256 ký tự, ngoặc không có tác dụng, OR ưu tiên hơn AND)
→ tách truy vấn làm hai, dùng **Publish or Perish** lấy 1.000 kết quả/năm/truy vấn.

**Phễu lọc**:

```
 14.254 bài (GS 12.000, Engineering Village 1.224, WoS 511, ScienceDirect 135, ACM 89, IEEE 295)
   → loại trùng bằng Zotero
   → lọc GS bằng script: chỉ giữ bài có từ khoá khớp ở TIÊU ĐỀ / TÓM TẮT / KEYWORD → gộp, loại trùng: 2.968
   → tiêu chí chọn/loại thủ công (2 người): 124
   → kiểm soát chất lượng: 80
   → snowballing (bài được ≥ 2 bài trong tập trích dẫn): +21
   = 101 bài
```

- **Tiêu chí chọn**: đề xuất cách phát hiện/sửa lỗi trong dataset ML, hoặc dùng ML để phát hiện/sửa lỗi dữ liệu.
  **Loại**: cách làm đặc thù bài toán (không khái quát), loại dữ liệu khác (âm thanh), tấn công dữ liệu (poisoning, adversarial), không truy cập miễn phí, bài thứ cấp, không tiếng Anh.
- **Kiểm soát chất lượng**: 7 câu hỏi chất lượng Q1.1–Q1.7 (mục tiêu, bối cảnh, giá trị, kết quả có bằng chứng, hạn chế, phương pháp, thí nghiệm) chấm 0–2;
  tổng < 7 → loại. 2 câu hỏi liên quan Q2.1–Q2.2 — cả hai bằng 0 → loại. Dưới ngưỡng thì người thứ hai chấm lại; bất đồng → người thứ ba quyết định.
- **Trích xuất**: lỗi được sửa, dataset, mô hình ML, cách đo chất lượng, so với gì, hiệu năng ML, hiệu năng kỹ thuật (tài nguyên, thời gian), hạn chế.

**Thống kê**: Feature cleaning 34%, Label cleaning 32%, Entity matching 18%, Outlier 8%, Holistic 4%, Imputation 3%, nhiều loại 2%.
Dữ liệu bảng chiếm ưu thế (feature cleaning: bảng 72%; entity matching: bảng 95%; label cleaning đa dạng nhất: ảnh 56%). 74% tác giả từ học thuật, 21% hỗn hợp, 5% công nghiệp.
Chỉ **20/101** bài có gói tái lập.

### 9.4 Taxonomy (Fig. 4)

```
 DC&ML (101)
 ├─ Feature cleaning (36)      — lỗi: GIÁ TRỊ ĐẶC TRƯNG sai
 │    ├─ Model-based (19) ── Ensemble-based (7) · Transformer-based (4) · Autoencoder-based (3)
 │    ├─ Error prioritization (3)
 │    └─ Data cleaning rule generation (2)
 ├─ Label cleaning (32)        — lỗi: NHÃN sai
 │    ├─ Uncertainty-based (10) · Loss-based (5) · Counterfactual (9) · Outlier-based (3)
 ├─ Entity matching (20)       — lỗi: BẢN GHI TRÙNG (cùng thực thể thật)
 │    ├─ Token comparison (2) · Latent space comparison (11: token / attribute / record level) · Learned comparison (4)
 ├─ Outlier detection (8)      — lỗi: bản ghi NGOÀI PHÂN PHỐI
 │    ├─ Statistic-based (1) · Distance-based (2) · Model-based (2)
 ├─ Imputation (3)             — lỗi: GIÁ TRỊ THIẾU
 └─ Holistic data cleaning (4) — NHIỀU loại lỗi cùng lúc
```

### 9.5 Phương pháp — Feature cleaning (dữ liệu bảng)

**Model-based**: coi làm sạch là bài toán dự đoán. *Phát hiện*: mô hình m dự đoán ô `r[Aᵢ]` có bẩn không (y ∈ [0,1]) khi biết cả bản ghi r.
*Sửa*: dự đoán giá trị sạch của ô bẩn. Khác biệt chính giữa các cách là **đặc trưng được thiết kế**:

| Loại đặc trưng | Ví dụ |
|---|---|
| **Tần suất** | TF-IDF của n-gram trong ô (giá trị càng hiếm càng dễ là lỗi); đồng xuất hiện giá trị giữa các cột |
| **Định dạng** | Thay chữ số bằng `n`, ký hiệu bằng `s`: `"400$"` → `"nnns"` — chỉ giữ "hình dạng" giá trị |
| **Metadata** | Kiểu dữ liệu, độ dài chuỗi của ô |

**Ensemble-based** (base tools + meta-model): không công cụ đơn lẻ nào tốt nhất/bắt được mọi lỗi → kết hợp:

```
 Base tools (thường không dùng ML): integrity constraints · matching dependencies · outlier detection · pattern violation
        │  dự đoán bẩn/sạch hoặc đề xuất giá trị sửa
        ▼
 Meta-model ─► PHÁT HIỆN: mỗi cột một mô hình nhận vector nhị phân output của base tools (Mahdavi et al., 2019);
                          hoặc chuyển base tools thành luật suy diễn của mô hình đồ thị xác suất (HoloClean — Rekatsinas et al., 2017)
             ─► SỬA: chọn giá trị sửa có khả năng đúng nhất trong tập đề xuất (Mahdavi & Abedjan, 2020: NN nhận vector độ tin cậy của các base repairer)
 Base repairer 3 loại: value-based ("a dg" → "a dog") · vicinity-based (city = Tokyo ⇒ country = Japan) · domain-based (thay bằng mode của cột)
```

Vấn đề: output base tools **tương quan** làm lệch meta-model (giải: k-means trên output, chọn tool tốt nhất mỗi cụm theo tập validation);
quá nhiều tool → chậm (giải: loại tool kém trên dataset tương tự) và tốn công cấu hình (giải: tự sinh mọi cấu hình trong tập định sẵn).

**Transformer-based** — hai trở ngại và cách giải:
1. *Bài toán phân loại vs sinh văn bản*: (a) hỏi mô hình nền bằng prompt "Có lỗi ở thuộc tính X không?" → yes/no (few/zero-shot, chỉ cần ~10 mẫu);
   (b) huấn luyện **masked data model** — che một ô, dự đoán lại, khác giá trị gốc ⇒ bẩn; (c) thêm lớp linear + softmax, fine-tune phân loại;
   (d) dùng transformer sinh embedding (học tương phản SimCLR) cho mô hình khác chấm điểm các đề xuất sửa.
2. *Dữ liệu bảng vs ngôn ngữ*: **tuần tự hoá** bản ghi thành chuỗi có tên cột — `"City: Montreal"` hoặc token đặc biệt `"[A]City [V]Montreal"`.

**Autoencoder-based**: dùng khả năng **khử nhiễu** của nén chiều — chuyển bản ghi thành bản ghi xác suất → qua autoencoder → chọn giá trị xác suất cao nhất;
VAE cải tiến tránh posterior collapse (lấy nhiều vector ẩn, sinh và lấy trung bình); hoặc dùng **loss tái tạo** — bản ghi có loss cao ở các epoch đầu là bẩn (Picket).

**Error prioritization**: không tự sửa mà **chọn bản ghi cho chuyên gia xem**: đối chiếu với Wikipedia qua hệ hỏi-đáp; chọn bản ghi mà nếu sửa sẽ **ảnh hưởng nhiều nhất**
tới mô hình (Krishnan et al., 2016: ưu tiên mẫu gây cập nhật trọng số lớn nhất).

**Sinh luật làm sạch**: MLNClean dùng Markov Logic Network sinh luật xác suất → ứng viên sửa → chọn ứng viên khả dĩ nhất và **khác ít nhất** so với giá trị gốc;
AutoFD học cấu trúc đồ thị xác suất ⇔ phát hiện functional dependency.

**Khác**: Krishnan et al. (2017) (áp từng tool, mỗi bản dữ liệu một mô hình, kết hợp bằng boosting); PClean (ngôn ngữ lập trình xác suất cho làm sạch);
cải tiến HoloClean cho **dữ liệu đến liên tục** — không huấn luyện lại mô hình làm sạch nếu phân phối dữ liệu mới không đổi.

**Kỹ thuật bổ trợ**:
- *Data augmentation*: dữ liệu làm sạch mất cân bằng (sạch ≫ bẩn) → **biến dữ liệu sạch thành bẩn** bằng phép làm hỏng "hợp lý", học từ cặp sạch/bẩn
  (Gestalt pattern matching, so khớp pattern phân cấp); chọn phép theo **phân phối thực nghiệm** của chúng.
- *Semi-supervised*: Naive Bayes dự đoán giá trị sạch, giữ dự đoán tin cậy > 90%; **label propagation** gán nhãn cho bản ghi tương tự (ngưỡng khác biệt thuộc tính, hoặc phân cụm phân cấp).
- *Active learning*: chọn **cột** mô hình kém tự tin nhất rồi chọn ô bằng query-by-committee; ưu tiên bộ có nhiều lỗi phổ biến để phủ nhiều loại lỗi.

**Time series**: mô hình tự hồi quy đề xuất giá trị sửa, theo **nguyên tắc sửa tối thiểu** chỉ áp **một** sửa (khác ít nhất), huấn luyện lại, lặp đến khi chênh lệch
dưới ngưỡng; hoặc ARX + NN dự đoán, kiểm định giả thuyết trên phần dư để phát hiện outlier, thay giá trị bất thường nhất rồi lặp.

**So sánh**: transformer-based thường tốt nhất, cần ít mẫu, dễ chuyển dataset (cùng định dạng prompt); ensemble-based cần cấu hình luật/công cụ theo từng dataset
nhưng có thể gộp transformer làm base tool; vẫn có cách không dùng transformer vượt transformer trên vài dataset.

### 9.6 Phương pháp — Label cleaning

| Họ | Ý tưởng | Kỹ thuật tiêu biểu |
|---|---|---|
| **Uncertainty-based** | Mô hình đã học đặc trưng mỗi lớp → dự đoán khác nhãn (xác suất lớp được gán thấp) = tín hiệu yếu của nhãn sai | Gửi người xem theo entropy cao nhất (có xét độ khó gán nhãn với người); tự động: bỏ mọi mẫu bị đánh dấu, hoặc bỏ dần mẫu kém tin cậy nhất rồi train lại; **Northcutt et al. (2019)**: ma trận nhiễu theo lớp, **ngưỡng riêng mỗi lớp** = độ tin cậy trung bình của mô hình trên các mẫu gán nhãn lớp đó |
| **Loss-based** | Mẫu nhãn sai có loss cao | Đánh dấu loss cao → gán lại bằng dự đoán → train lại, lặp; mạng **overfit mẫu nhiễu muộn hơn** → lấy loss trung bình qua nhiều lần, định kỳ tăng learning rate để "quên"; autoencoder cho **mỗi lớp**, gán lớp có lỗi tái tạo nhỏ nhất |
| **Counterfactual** | Sửa/bỏ mẫu làm mô hình tốt hơn ⇒ mẫu đó lỗi | So mô hình có/không có mẫu (song song hoá; mô hình dự đoán thay đổi val loss; **influence functions** — chỉ đúng lý thuyết với loss lồi; bộ ước lượng cho SGD); hoặc tối ưu sửa nhãn để tối đa accuracy trên tập sạch; dùng **"complaint"** của người dùng (về bản ghi hoặc giá trị tổng hợp) để bắt nhiễu hệ thống |
| **Outlier-based** | Mẫu nhãn sai khác xa các mẫu cùng lớp | Khoảng cách cosine tới các mẫu sạch cùng lớp; tới **prototype lớp** (self-attention); kết hợp góc nhìn cục bộ (kNN) và toàn cục (mật độ lớp) bằng tổng hợp Bayes |

Hai điều kiện để uncertainty-based thành công: (1) mô hình **không được overfit** (nếu không, nhãn sai được dự đoán "đúng" với độ tin cậy cao) — dùng học bền nhiễu
(Co-Teaching, BYOL) hoặc **dừng sớm** (mẫu nhãn sai được học muộn hơn; ví dụ k-means 2 cụm trên độ tin cậy mỗi epoch, dừng khi < 1% mẫu đổi cụm);
(2) **độ tin cậy chính xác** — softmax không phải độ tin cậy; dùng Bayesian NN hoặc xấp xỉ bằng **Monte Carlo Dropout**, Deep Ensemble.

Khác: rà support vector của SVM (mẫu gần biên dễ bị gán sai); GAN sinh dữ liệu sạch nhờ mode collapse; mạng ánh xạ nhãn vào nhãn đúng với skip-connection.
**Nhiễu hệ thống** (systematic noise) là điểm yếu chung: bỏ một mẫu không thay đổi mô hình vì nhiều mẫu khác cùng nhiễu.

Phân biệt: **label cleaning** sửa dữ liệu; **label-noise robust learning** sửa *thuật toán học* (lớp nhiễu, giảm trọng số mẫu nghi ngờ, teacher–student, cho phép từ chối dự đoán)
— không phải data cleaning, nhưng hai hướng bổ trợ nhau.

### 9.7 Phương pháp — Entity matching

Bài toán nhị phân: cho cặp (t₁, t₂), dự đoán có cùng thực thể không. **Blocking** trước để loại cặp chắc chắn không khớp:
luật thủ công (cùng mã bưu chính, top-20 láng giềng TF-IDF); **LSH trên embedding** bản ghi (GloVe + bi-LSTM; fastText + attention, nhiều embedding/bản ghi);
FAISS kNN với k điều chỉnh theo từng bản ghi để giữ recall.

| Cách so sánh | Mô tả |
|---|---|
| Token comparison | Tập từ **chung** và **khác** giữa hai bản ghi ("Montreal, Canada" vs "Quebec, Canada" → chung {Canada}, khác {Quebec, Montreal}) → embedding → mô hình. Tránh việc embedding "làm mờ" khác biệt quan trọng ("6-foot" vs "12-foot sandwich") nhưng nhạy với lỗi gõ |
| Latent space comparison | So embedding ở mức token / thuộc tính / bản ghi (cosine, hiệu từng phần tử), gộp kết quả rồi phân loại |
| Learned comparison | Mô hình tự học cách so: attention; dự đoán semantic type từng cột rồi dùng mô hình riêng cho type đó; **fine-tune transformer** trên chuỗi tuần tự hoá `[ATTRIBUTE NAME] city [ATTRIBUTE VALUE] Montreal ...`; prompt LLM |

Kỹ thuật bổ trợ: tạo cặp âm từ bản ghi **giống nhưng không khớp** (khó hơn ngẫu nhiên); cặp dương bằng biến đổi giữ danh tính + **MixDA** (nội suy embedding);
self-training; active learning gửi **cân bằng** cặp quanh ngưỡng 0,5; transfer learning với embedding **bất biến dataset** (adversarial, giảm KL divergence).
Transformer vượt DL "cổ điển" trung bình **27,5% F1** trên dataset khó và cần rất ít mẫu (prompt với 10 mẫu).

### 9.8 Phương pháp — Outlier detection, Imputation, Holistic

**Outlier detection** (không nhằm tìm nhãn sai):
- *Thống kê*: mô hình sinh, bản ghi xác suất thấp là outlier (làm giàu bằng metadata như độ dài chuỗi).
- *Khoảng cách*: so với láng giềng; trung bình có trọng số nhãn láng giềng, **ưu tiên lớp thiểu số** để không coi nhầm mẫu hợp lệ của lớp hiếm là outlier.
- *Mô hình*: GAN với k generator (mỗi cái học một nhóm dữ liệu) + discriminator; autoencoder kết hợp khoảng cách Mahalanobis/Euclid tới phân phối lớp gần nhất.
- *So sánh thực nghiệm*: **Isolation Forest** hiệu quả về average precision, thời gian, khả năng mở rộng; với time series, **KNN** tối ưu về hiệu năng, độ đơn giản, thời gian.
  Ensemble bỏ phiếu nhiều phương pháp dựa trên thước đo khác nhau, lọc phương pháp kém bằng spectral feature selection. Thước đo thường dùng: **AUROC** (bỏ qua chọn ngưỡng).

**Imputation**: Bayesian network chính xác nhất nhưng tốn huấn luyện (so với cây quyết định, kNN); **kEMI** — kNN tìm K bản ghi tương tự rồi
Expectation-Maximization dùng tương quan đặc trưng trong K bản ghi đó; **kEMI+** chạy EMI nhiều lần và hợp nhất bằng Dempster–Shafer (chính xác hơn, kém mở rộng);
ART + CANFIS (mạng nơ-ron mờ).

**Holistic — sinh pipeline làm sạch** (cleaning optimizer): tìm **thứ tự và cấu hình** công cụ làm sạch tối ưu một thước đo:
- Thước đo: thường dùng **hiệu năng mô hình** train trên dữ liệu đã làm sạch làm proxy chất lượng (vì không phải tool nào cũng giúp mô hình); hoặc số outlier, số vi phạm ràng buộc.
- Bộ tối ưu siêu tham số (Hyperopt) không tận dụng tính **tăng dần** của làm sạch → **beam search** (Krishnan & Wu, 2019) tỉa pipeline kém theo hiệu năng hiện tại;
  **RL** (Berti-Equille, 2019): trạng thái = tool vừa áp, phần thưởng = thay đổi hiệu năng mô hình, có thể chọn cả chuẩn hoá;
  tái dùng pipeline hiệu quả trên **dataset tương tự** (vector 22 meta-feature, khoảng cách L1).
- Benchmark (Li et al., 2019): cải thiện do làm sạch **khái quát sang mô hình khác**; **không tool nào tốt nhất mọi dataset**; làm sạch mọi loại lỗi không nhất thiết tốt hơn làm sạch một loại.

**Thước đo đánh giá chung**: accuracy, F1, precision, recall (như phân loại); PSNR (ảnh); MSE (time series); hiệu năng mô hình hạ nguồn; thời gian chạy
(HoloClean > 6 giờ cho 2 triệu bản ghi); hiệu năng theo số mẫu gán nhãn (20–300).

### 9.9 Thách thức và hướng nghiên cứu

| Thách thức | Nội dung |
|---|---|
| Khan hiếm dataset làm sạch có nhãn | Không có kho tập trung (Hospital, Flights, Beers được dùng nhiều); nhiều nghiên cứu phải **tiêm lỗi nhân tạo** |
| Mất cân bằng | Mẫu sạch ≫ mẫu bẩn; cặp không khớp ≫ cặp khớp |
| Thiếu công cụ | Chỉ một thư viện mở (OpenClean) và không được duy trì |
| Làm sạch "đơn lẻ" | Dữ liệu thật có nhiều loại lỗi, nhưng hầu hết phương pháp chỉ xử lý một loại; tương tác giữa các bước làm sạch chưa được hiểu rõ |

Sáu nhóm hướng nghiên cứu (24 khuyến nghị): (1) tham số hoá và **lọc mẫu augmentation không hợp lệ**; (2) kho dataset làm sạch, **taxonomy lỗi dữ liệu**, dataset có nhãn lỗi thật;
(3) cài đặt phương pháp vào thư viện công khai; (4) LLM cho làm sạch — cách **tuần tự hoá bảng** và cách prompt; (5) holistic: sinh pipeline mới, làm sạch nhiều loại lỗi cùng lúc,
**kết hợp làm sạch với các bước tiền xử lý khác**, phân tích ảnh hưởng qua lại giữa các bước; (6) **làm sạch tương tác** có chuyên gia (92/101 bài là tự động hoàn toàn).
Riêng feature cleaning: dùng **nhãn** của bản ghi khi làm sạch đặc trưng; chuyển kỹ thuật outlier detection sang error detection.

---

## 10. A Data-Centric Perspective on Evaluating Machine Learning Models for Tabular Data

| | |
|---|---|
| **Tác giả** | Andrej Tschalzev, Sascha Marton, Stefan Lüdtke, Christian Bartelt, Heiner Stuckenschmidt (University of Mannheim, University of Rostock) |
| **Nguồn** | NeurIPS 2024 — Track on Datasets and Benchmarks — arXiv:2407.02112v3 |
| **Loại bài** | Khung đánh giá (benchmark framework) + thực nghiệm quy mô lớn (> 200.000 mô hình được huấn luyện) |
| **File** | `paper/2407.02112v3.pdf` — mã nguồn: `github.com/atschalz/dc_tabeval` |

### 10.1 Tóm tắt

Các nghiên cứu so sánh mô hình cho dữ liệu bảng thường **lấy mô hình làm trung tâm**: chia cross-validation cố định và **một tiền xử lý chuẩn hoá chung
cho mọi dataset**. Bài chỉ ra cách đánh giá đó **bị thiên lệch**, vì pipeline thực tế cần tiền xử lý **riêng cho từng dataset**, đặc biệt là **feature engineering**.
Tác giả đề xuất **khung đánh giá lấy dữ liệu làm trung tâm**: 10 dataset từ cuộc thi Kaggle, mỗi dataset có pipeline tiền xử lý **cấp chuyên gia**,
và dùng **leaderboard Kaggle** làm thước đo bên ngoài.

Ba phát hiện chính:
1. Sau feature engineering riêng cho dataset, **thứ hạng mô hình thay đổi đáng kể**, khoảng cách giữa mô hình thu hẹp, tầm quan trọng của chọn mô hình giảm.
2. Mô hình mới dù có tiến bộ vẫn **hưởng lợi lớn từ feature engineering thủ công** — đúng cho cả mô hình cây lẫn mạng nơ-ron.
3. Dữ liệu bảng thường được coi là tĩnh nhưng mẫu thường **được thu thập theo thời gian**; thích nghi với dịch chuyển phân phối quan trọng kể cả với dữ liệu "tĩnh".

### 10.2 Mục tiêu — hai hạn chế của đánh giá hiện nay

| Hạn chế | Hệ quả |
|---|---|
| Thiết lập **chuẩn hoá quá mức**, không phản ánh quy trình thực tế (có feature engineering theo dataset) | Mô hình bị đánh giá như **hệ AutoML**, trong khi thực tế chúng là một thành phần của pipeline riêng |
| **Không có tham chiếu bên ngoài** cho hiệu năng cao nhất có thể đạt | Không đo được "state of the art" thật; khó so sánh giữa các nghiên cứu |

Ngoài ra nhiều benchmark giới hạn số mẫu, **bỏ cột hạng mục cardinality cao**, và **loại dữ liệu không i.i.d.** (có thời gian) → không đại diện thực tế.

### 10.3 Phương pháp — Khung đánh giá data-centric (Fig. 1)

```
 Data loading                 Preprocessing pipelines                     Unified CV pipeline                Evaluation
 ┌─────────────────────┐      ┌─────────────────────────────────────┐    ┌───────────────────────┐        ┌───────────────────────────┐
 │ gộp bảng            │      │ (a) Standardized — đơn giản,         │    │ k fold: train k model  │        │ nộp lên Kaggle qua API    │
 │ loại vấn đề: leakage,│ ──► │     không phụ thuộc dataset          │──► │ trên mỗi fold          │──────► │ → điểm trên test ẨN       │
 │ bản ghi lỗi          │      │ (b) Expert feature engineering —     │    │ dự đoán test mỗi model │        │ → vị trí trên private     │
 │ xử lý đặc trưng miền │      │     riêng cho dataset                │    │ → LẤY TRUNG BÌNH       │        │   leaderboard (percentile)│
 │ (ví dụ datetime)     │      │ (c) Test-time adaptation — như (b)   │    └───────────────────────┘        │ 0,9 = hơn 90% người thi  │
 └─────────────────────┘      │     nhưng dùng thêm test KHÔNG nhãn  │                                     └───────────────────────────┘
                              └─────────────────────────────────────┘
```

#### a) Chọn dataset (Fig. 2)

```
 Cuộc thi Kaggle: dữ liệu bảng, có thưởng, > 1.000 người tham gia      77
   − 15 lỗi kỹ thuật (code competition, không còn dữ liệu, chỉ 137 mẫu, thắng nhờ leak, lỗi nộp bài)   62
   − 10 dùng modality khác (ảnh, văn bản, tín hiệu, gen...) đáng kể     52
   −  6 miền đặc biệt (tương quan không gian; gợi ý/CTR có mô hình riêng)   46
   − 29 có tính thời gian KHÔNG bỏ qua được (cần feature engineering theo thời gian)   17
   −  7 không có lời giải chuyên gia tái lập được                       10 dataset
```

Lợi ích dùng Kaggle: bài toán có ý nghĩa thực tế (doanh nghiệp bỏ tiền tổ chức), metric được chọn theo nhu cầu thực tế, **tập test ẩn lớn** (giảm adaptive overfitting —
9/10 dataset có test ≥ 50.000 mẫu, ngưỡng tối thiểu khuyến nghị là 10.000), leaderboard là tham chiếu bên ngoài. Phát hiện quan trọng khi sàng lọc:
**46 cuộc thi có đặc trưng thời gian** — đa số dataset bảng có tính thời gian.

| Dataset | Năm | N train / test | D thô / sau FE | Tác vụ | Metric | Mô hình chuyên gia | TTA |
|---|---|---|---|---|---|---|---|
| MBGM | 2017 | 4.209 / 4.209 | 377 / 59 | Hồi quy | R² | XGBoost | Không |
| SVPC | 2018 | 12.296 / 49.342 | 4.992 / 1.420 | Hồi quy | RMSLE | LightGBM | Không |
| AEAC | 2013 | 32.769 / 58.921 | 9 / 315 | Nhị phân | AUC | Ensemble | Có |
| OGPCC | 2015 | 61.878 / 144.368 | 93 / 104 | Đa lớp | logloss | Ensemble | Có |
| SCS | 2016 | 76.020 / 75.818 | 370 / 224 | Nhị phân | AUC | Ensemble | Có |
| BPCCM | 2016 | 114.321 / 114.393 | 132 / 313 | Nhị phân | logloss | XGBoost | Không |
| SCTP | 2019 | 200.000 / 200.000 | 200 / 600 | Nhị phân | AUC | NN | Có |
| HQC | 2015 | 260.753 / 173.836 | 299 / 300 | Nhị phân | AUC | XGBoost | Không |
| IFD | 2019 | 590.540 / 506.691 | 432 / 263 | Nhị phân | AUC | CatBoost | Có |
| PSSDP | 2017 | 595.212 / 892.816 | 57 / 53 | Nhị phân | Gini | NN | Có |

#### b) Ba pipeline tiền xử lý (đều không phụ thuộc mô hình; bước riêng cho mô hình được coi là một phần của mô hình)

Định nghĩa: **preprocessing** = tập kỹ thuật áp trước mô hình; **feature engineering** = xây đặc trưng mới để cải thiện dự đoán (là tập con của preprocessing).

| Pipeline | Nội dung |
|---|---|
| **Standardized** | Cột số thiếu → **mean**; cột hạng mục thiếu → **một hạng mục mới**; bỏ cột hằng; log-transform target đuôi nặng (hồi quy). Đại diện thiết lập học thuật hiện nay |
| **Expert feature engineering** | Lấy phần chuẩn bị dữ liệu từ **một lời giải top** của mỗi cuộc thi (chọn theo hạng và độ đầy đủ mô tả). Đảm bảo mọi phép FE chỉ dùng **dữ liệu train** |
| **Test-time adaptation (TTA)** | Giống expert FE nhưng **dùng thêm đặc trưng của tập test (không nhãn)** khi tính đặc trưng — đúng như chuyên gia đã làm ở 6/10 dataset |

**Các kỹ thuật FE chuyên gia dùng lặp lại nhiều nhất** (số dataset): groupby interaction giữa cột hạng mục và cột số (4), tương tác hạng mục bậc 2 (3), chọn đặc trưng (3),
**frequency encoding** hạng mục (3), giảm chiều (2), tương tác hạng mục bậc 3 (2), tương tác số học bậc 2 (2), **tổng số giá trị thiếu trong một dòng** (2),
**tổng số giá trị 0 trong một dòng** (2). Nhận xét: kỹ thuật phổ biến nhất xoay quanh **đặc trưng hạng mục**; **tương tác** giữa đặc trưng thường được làm thủ công,
còn biến đổi một đặc trưng đơn lẻ thì hiếm.

Ví dụ chi tiết từ phụ lục (A.2):

| Dataset | Feature engineering của chuyên gia |
|---|---|
| MBGM | Cộng, AND logic, tổng nhiều đặc trưng nhị phân; chọn đặc trưng |
| SVPC | {max, mean, min, median, giá trị khác 0 đầu/cuối, số NaN, số giá trị duy nhất} trên các **nhóm cột** (40, 99... cột) |
| AEAC | Groupby (chuẩn hoá), tương tác hạng mục bậc 2–3, frequency encoding (của cả tương tác), log của tần suất, bỏ cột hằng |
| OGPCC | Đặc trưng tSNE, PCA, tâm KMeans |
| SCS | Bỏ cột tương quan cao/hằng, đếm giá trị 0/3/6/9 trong dòng, percentile rank của A trong nhóm B, tỉ lệ, đặc trưng KMeans 2–11 cụm |
| BPCCM | Tương tác hạng mục bậc 2, 3, 11; làm tròn số thành hạng mục; tổ hợp số học bậc 2; **target encoding out-of-fold** |
| SCTP | Thay giá trị chỉ xuất hiện một lần bằng mean; tạo đặc trưng hạng mục từ việc giá trị có lặp lại với target 1/0 hay là duy nhất |
| HQC | Tổng NA trong dòng, tổng số 0 trong dòng, tương tác hạng mục bậc 2 |
| IFD | Chọn đặc trưng; chuẩn hoá "time delta" về ngày; frequency encoding (train + test); groupby (mean, std, count); tương tác hạng mục bậc 2 |
| PSSDP | Chọn đặc trưng; tổng giá trị thiếu; frequency encoding tương tác bậc cao; one-hot (chỉ cho mô hình cây); với NN: train XGBoost dự đoán một đặc trưng từ nhóm khác, dùng **dự đoán out-of-fold** làm đặc trưng |

Kỹ thuật dùng cho **test-time feature engineering**: đếm tần suất hạng mục (AEAC, IFD, PSSDP), giảm chiều (OGPCC, SCS), groupby (SCS, IFD),
sự xuất hiện của giá trị số train trong test (SCTP), khử nhiễu bằng mô hình với dự đoán out-of-fold (PSSDP).

#### c) Mô hình, tối ưu siêu tham số, đánh giá

- **Mô hình**: XGBoost, LightGBM, CatBoost (mỗi cái đều được dùng trong ít nhất một lời giải chuyên gia); ResNet (baseline ~MLP có skip connection),
  FTTransformer, MLP-PLR (học hàm tần số cao), GRANDE (lai cây–nơ-ron); **AutoGluon** (`best_quality`, 10 giờ) đại diện AutoML không tiền xử lý.
- **CV ensembling**: dùng cùng kiểu chia fold như lời giải chuyên gia, thống nhất **10 fold** (stratified cho phân loại; IFD chia theo **tháng thu thập** → 6 fold);
  tập validation dùng cho early stopping và chọn siêu tham số; dự đoán test = **trung bình** dự đoán của các mô hình theo fold.
- **3 chế độ HPO** (tối ưu riêng mỗi fold để ensemble đa dạng): Default · Light (20 vòng random search) · Extensive (20 random + 80 vòng TPE, thư viện Optuna).
- **Tiền xử lý riêng cho mô hình**: cây — chỉ khai báo đúng kiểu hạng mục; NN — chuẩn hoá target (hồi quy), cột số thiếu → mean + `QuantileTransformer`,
  hạng mục → ordinal encoding (dùng embedding); GRANDE dùng leave-one-out encoding.
- **Thước đo**: vị trí trên **private leaderboard** dạng percentile → so sánh được giữa các dataset dù metric khác nhau (phụ lục F lặp lại bằng metric gốc, kết luận giữ nguyên).
- **Kiểm định thống kê** (D.4): hồi quy **mixed-effects** — biến phụ thuộc là vị trí leaderboard, dataset là random effect, fixed effects gồm FE, TTA, chọn mô hình, Light HPO, Extensive HPO.

### 10.4 Kết quả

**(1) So sánh mô hình thay đổi khi xét tiền xử lý riêng cho dataset** (Fig. 4):

| Mô hình | Standardized | Expert FE | FE + TTA |
|---|---|---|---|
| CatBoost | 0,79 | 0,89 | 0,97 |
| XGBoost | 0,68 | 0,90 | 0,97 |
| LightGBM | 0,62 | 0,85 | 0,90 |
| MLP-PLR | 0,60 | 0,82 | 0,91 |
| FTTransformer | 0,59 | 0,81 | 0,91 |
| GRANDE | 0,52 | 0,81 | 0,83 |
| ResNet | 0,44 | 0,62 | 0,64 |

(vị trí leaderboard trung bình, Table 17). Thứ hạng thay đổi (Spearman giữa pipeline thấp), khoảng cách thu hẹp, nhiều mô hình cùng đạt đỉnh;
**ưu thế của CatBoost biến mất** — vì CatBoost đã **tự làm feature engineering bên trong** (đếm, thống kê theo target cho hạng mục, encoding tổ hợp cho tương tác hạng mục);
khi áp cùng FE cho mô hình khác, XGBoost trung bình ngang CatBoost.

**(2) Tiến bộ đo được của mô hình mới** (Fig. 5): với tiền xử lý chuẩn, CatBoost lên top ở 3 cuộc thi trước đây cần nhiều FE thủ công; AutoGluon top ở 3 cuộc thi;
kiến trúc NN mới hơn ResNet trên 9 dataset; MLP-PLR và FTTransformer đạt top ở hai cuộc thi mà NN tuỳ biến từng là mô hình tốt nhất (sau FE và TTA).
Nhưng **6 dataset vẫn không thể đạt đỉnh nếu không có công sức con người**.

**(3) Feature engineering là yếu tố quan trọng nhất** (Fig. 6, Table 18): FE là thành phần đóng góp lớn nhất **cho mọi mô hình** — NN **không tự động hoá** được FE
với dữ liệu bảng. Chọn mô hình ít quan trọng hơn HPO trên một baseline cây mạnh. Kết quả hồi quy mixed-effects (546 quan sát, 10 nhóm):

| Hệ số | Coef. | p |
|---|---|---|
| Feature Engineering | **+0,201** | < 0,001 |
| Extensive HPO | +0,125 | < 0,001 |
| Light HPO | +0,085 | < 0,001 |
| Test-Time Adaptation | +0,080 | 0,001 |
| Model Selection (so với CatBoost) | +0,004 | **0,810** (không ý nghĩa) |

Góc nhìn "người thắng lấy tất" với CatBoost làm mặc định (Fig. 10): **không có FE** thì vị trí trung bình tốt nhất chỉ là percentile **14,5%**;
**không chọn mô hình** vẫn đạt **3%**. Không TTA: 3,2%; có TTA: 1,6%; phần còn thiếu để vào top 1% là ensembling.

**Xử lý hạng mục tối ưu phụ thuộc dataset** (Table 2): PSSDP cần **one-hot** (XGBoost 0,69 → 0,99), BPCCM cần **target encoding** (XGBoost 0,40 → 0,99) —
mỗi dataset một cách khác nhau, khác cách mặc định của mô hình. Với AEAC (toàn cột hạng mục), mọi NN đều tăng mạnh nhờ tương tác hạng mục
→ kiến trúc hiện tại **chưa nắm tốt mẫu phức tạp trong dữ liệu hạng mục**.

**(4) Test-time adaptation và tính thời gian** (Table 3): test-time FE cải thiện mô hình đơn trên **mọi** dataset có TTA (ví dụ SCTP 0,518 → 0,962 → 0,992);
với AEAC và OGPCC, FE chỉ có lợi **khi dùng như TTA**; 3 dataset không vào top 1% nếu không có TTA → so trực tiếp với leaderboard Kaggle là **không công bằng**
nếu không kiểm soát TTA. TTA chỉ hiệu quả khi dữ liệu **vi phạm i.i.d.** → dữ liệu được xem là tĩnh thực ra có dịch chuyển (ví dụ dataset *electricity* hay dùng
trong benchmark tĩnh lại cần chia theo thời gian).

**Khi nào test-time feature engineering khả thi trong thực tế** (A.3) — cần đủ 4 điều kiện: (1) dữ liệu cần dự đoán đến **theo lô**; (2) không cần dự đoán thời gian thực;
(3) dữ liệu train vẫn còn lúc test; (4) **huấn luyện lại** mô hình lúc test khả thi. Không áp dụng cho online learning, khi ít mẫu test, hoặc mô hình không huấn luyện lại được.
Ví dụ phù hợp: dự đoán hoàn trả sản phẩm — gom mẫu trong ngày, huấn luyện lại mô hình nhẹ hằng ngày.

**Thời gian chạy** (D.1): sau FE và TTA, **XGBoost là điểm Pareto duy nhất** (nhanh nhất và tốt nhất); với tiền xử lý chuẩn, các mô hình cây tạo biên Pareto.

### 10.5 Hạn chế (do tác giả nêu)

Phân phối leaderboard khác nhau giữa cuộc thi; không phải mọi người nộp là chuyên gia (nên nói "top 1% người tham gia", không nói "hơn 99% chuyên gia");
không lặp thí nghiệm để có error bar; đa số dataset thuộc tài chính, Bắc Mỹ/châu Âu; FE được trích từ pipeline vốn tối ưu cho mô hình cây.

### 10.6 Hướng đi tác giả đề xuất

Chọn tiền xử lý cẩn thận khi đánh giá (chuẩn hoá phù hợp cho AutoML, FE phù hợp khi muốn so sánh *ceteris paribus* hoặc thực tế); cần **tham chiếu hiệu năng bên ngoài**;
nghiên cứu vì sao mô hình không tự học được một số phép FE; phát triển phương pháp cho **dữ liệu bảng có tính thời gian** và TTA cho dữ liệu bảng;
đưa dataset có tính thời gian vào benchmark thay vì loại bỏ.

---

## 11. Imputation for Prediction: Beware of Diminishing Returns

| | |
|---|---|
| **Tác giả** | Marine Le Morvan, Gaël Varoquaux (Soda, Inria Saclay) |
| **Nguồn** | ICLR 2025 — arXiv:2407.19804v2 |
| **Loại bài** | Nghiên cứu thực nghiệm có kiểm soát (benchmark ~1.000.000 lần chạy, 325 ngày CPU) |
| **File** | `paper/2407.19804v2.pdf` — mã nguồn: `github.com/marineLM/Imputation_for_prediction_benchmark` |

### 11.1 Tóm tắt

Thực hành phổ biến: điền giá trị thiếu (imputation) trước khi huấn luyện, với kỳ vọng **impute càng chính xác thì dự đoán càng tốt**. Tuy nhiên lý thuyết và
thực nghiệm gần đây cho thấy impute hằng số đơn giản có thể **nhất quán và cạnh tranh**. Bài làm rõ **khi nào** đầu tư vào impute tinh vi thực sự giúp dự đoán tốt hơn,
bằng cách liên hệ **độ chính xác impute** với **độ chính xác dự đoán** trên mọi tổ hợp phương pháp impute × mô hình dự đoán, trên 19 dataset.

Kết luận: độ chính xác impute **ít quan trọng hơn** khi (i) dùng **mô hình biểu đạt mạnh**, (ii) thêm **missingness indicator** làm đầu vào bổ sung,
(iii) với **kết quả thật** (so với kết quả tuyến tính mô phỏng). Indicator **có lợi ngay cả khi thiếu hoàn toàn ngẫu nhiên (MCAR)**.
Tổng thể: trên dữ liệu thật với mô hình mạnh, cải thiện impute chỉ có tác động **nhỏ** lên dự đoán.

### 11.2 Bối cảnh và mục tiêu

**Ba cơ chế thiếu dữ liệu**:

| Cơ chế | Định nghĩa | Ghi chú |
|---|---|---|
| **MCAR** | Thiếu với xác suất cố định, độc lập mọi dữ liệu | Dễ impute nhất |
| **MAR** | Thiếu chỉ phụ thuộc biến **quan sát được** | — |
| **MNAR** | Thiếu phụ thuộc chính **giá trị không quan sát** (mang thông tin) | Dữ liệu thiếu tự nhiên thường được giả định là MNAR; đa số thuật toán impute **không hợp lệ** ở đây |

**Lý thuyết đã biết** (bài tóm lược): với mọi cơ chế thiếu và gần như mọi hàm impute tất định, thuật toán **nhất quán phổ quát** học trên dữ liệu đã impute
tiệm cận dự đoán tối ưu — kể cả impute bằng mean (mô hình coi mean là "giá trị đặc biệt" mã hoá việc thiếu). Với kết quả sinh tuyến tính, dự đoán tối ưu là mô hình tuyến tính
trên dữ liệu impute tối ưu → impute tốt hơn giúp mô hình tuyến tính. Ở MCAR, predictor tuyến tính tốt nhất gán trọng số 0 cho indicator.

**Vấn đề của các benchmark trước** (bài chỉ ra): huấn luyện impute trên **cả train + test** → *leakage*; huấn luyện impute **riêng** trên train và test → *"imputation shift"*
(mẫu impute khác nhau giữa train và test); chỉ impute một cột cố định; ít dataset; không tinh chỉnh siêu tham số hoặc tinh chỉnh trên dữ liệu đầy đủ; chỉ một loại mô hình.

**Mục tiêu**: không tìm pipeline "tốt nhất", mà **định lượng thay đổi hiệu năng dự đoán khi độ chính xác impute tăng**, có điều kiện theo mô hình, indicator, tỉ lệ thiếu.
Thiết kế chọn **MCAR** là kịch bản *tốt nhất* cho impute → nếu lợi ích nhỏ ở đây thì ở thực tế còn nhỏ hơn (**cận trên** của lợi ích). Chỉ xét **đặc trưng số**
(với đặc trưng hạng mục, cách hiệu quả thường là coi thiếu là **một hạng mục riêng**).

### 11.3 Phương pháp

#### a) Bốn phương pháp impute (chọn để phủ dải chất lượng rộng)

| Phương pháp | Cách làm |
|---|---|
| **mean** | Điền bằng trung bình các giá trị quan sát của cột — baseline |
| **iterativeBR** | Impute từng đặc trưng từ các đặc trưng khác theo vòng (round-robin) bằng **Bayesian ridge** (gần với MICE; `IterativeImputer` của scikit-learn) |
| **missforest** | Như trên nhưng dùng **random forest** (30 cây, độ sâu 15), lặp nhiều lượt qua từng đặc trưng |
| **condexp** | **Kỳ vọng có điều kiện** của phân phối chuẩn đa biến cho phần thiếu khi biết phần quan sát; mean và hiệp phương sai ước lượng **pairwise available-case** (ô (i,j) chỉ dùng mẫu quan sát cả i và j) — rẻ hơn EM |

#### b) Ba mô hình dự đoán + xử lý thiếu "tự nhiên"

- **MLP** (ReLU) — baseline đơn giản; **SAINT** — transformer chú ý cả hàng và cột (state-of-the-art DL cho bảng); **XGBoost** — boosting mạnh nhất cho hồi quy với đặc trưng số.
- Tinh chỉnh siêu tham số MLP và XGBoost bằng **Optuna 50 lần thử** trên tập validation; SAINT dùng mặc định của tác giả.
- **Xử lý thiếu tự nhiên (native)**: XGBoost dùng **MIA** (Missing Incorporated in Attribute) — khi tách nút, mẫu thiếu có thể đi trái, phải, hoặc thành lá riêng, chọn cách giảm lỗi nhiều nhất;
  SAINT dùng **embedding học được** riêng cho NaN của từng đặc trưng.

#### c) Dữ liệu và cơ chế thiếu

- Benchmark của Grinsztajn et al. (2022): **19 dataset hồi quy** (đặc trưng liên tục và thứ bậc; 3–79 đặc trưng; ~3.300 – 50.000 mẫu train).
- Tạo thiếu **MCAR** với tỉ lệ **20%** hoặc **50%** (mỗi giá trị độc lập có xác suất bị xoá).
- Chuẩn hoá: đặc trưng liên tục → `QuantileTransformer` (Gauss hoá); thứ bậc → chuẩn hoá z; y chuẩn hoá. **Tham số chuẩn hoá học trên tập train có giá trị thiếu**
  (trừ XGBoost native không chuẩn hoá).
- **Dữ liệu bán mô phỏng**: thay y bằng **hàm tuyến tính** của X (hệ số bằng nhau, chuẩn hoá cho var(βᵀX) = 1, nhiễu với SNR = 10) → so sánh kết quả thật vs tuyến tính.
- **MNAR** (phụ lục L): **probit self-masking** `P(Mⱼ = 1 | Xⱼ) = Φ(λⱼXⱼ − cⱼ)`, λⱼ = 1/(2σⱼ) để xác suất thiếu tăng **mượt** trên miền giá trị; cⱼ chọn theo công thức để đạt tỉ lệ thiếu mong muốn.

#### d) Quy trình đánh giá (chống leakage và imputation shift)

```
 Mỗi dataset: chia ngẫu nhiên train 80% / val 10% / test 10% (mỗi phần tối đa 50.000 mẫu); lặp 10 lần chia khác nhau
   1. Học mô hình impute trên TRAIN → áp CÙNG mô hình đó cho train, val, test
   2. (tuỳ chọn) nối MISSINGNESS INDICATOR (mask nhị phân) làm đặc trưng bổ sung — KHÔNG dùng cho bước impute
   3. Train mô hình dự đoán trên train đã impute; chọn siêu tham số trên val; đo R² trên test
 Tổ hợp: 4 impute × 3 mô hình × {có, không indicator} = 24, + XGBoost native + SAINT native = 26 pipeline
```

#### e) Cách định lượng "impute tốt hơn → dự đoán tốt hơn bao nhiêu"

- **Độ chính xác impute** = R² giữa giá trị impute và giá trị thật; **độ chính xác dự đoán** = R² trên test (đều lấy **tương đối** so với trung bình các phương pháp trên dataset đó).
- Với mỗi (mô hình, dataset): 4 phương pháp impute × 10 lần lặp = **40 cặp (R² impute, R² dự đoán)** → **hồi quy tuyến tính** R² dự đoán theo R² impute
  (thêm mã lần lặp làm covariate để khử ảnh hưởng của cách chia).
  - **Độ dốc (slope)** = hiệu ứng: tăng 1 đơn vị R² impute thì R² dự đoán tăng bao nhiêu.
  - **Tương quan riêng phần** (partial correlation, khử ảnh hưởng cách chia) = độ **tin cậy** của quan hệ. Phụ lục C: `cor = 1 / √(1 + σ²/(β²·var(X₁)))`
    — tương quan phụ thuộc cả độ dốc β lẫn độ nhiễu σ².
- Kiểm định: slope > 0 bằng one-sided t-test có **hiệu chỉnh Bonferroni**; median slope > 0 bằng **Wilcoxon signed-rank**; so sánh pipeline bằng **Critical Difference diagram** (kiểm định Nemenyi).

**Thí nghiệm phụ**: (1) **xáo trộn indicator** theo từng mẫu (giữ số giá trị thiếu mỗi dòng nhưng mất thông tin *cột nào* thiếu); (2) **permutation importance**
của 2 đặc trưng quan trọng nhất, tính riêng trên các mẫu mà đặc trưng đó bị thiếu vs được quan sát.

### 11.4 Kết quả

**(1) Bức tranh chung (Fig. 1)**: impute tinh vi hơn có xu hướng dự đoán tốt hơn (missforest > condexp ≈ iterativeBR > mean), nhưng **indicator làm giảm hiệu ứng này**;
MLP hưởng lợi rõ, **XGBoost gần như không**. Phương sai giữa dataset **lớn hơn** chênh lệch giữa phương pháp — missforest + XGBoost + indicator chỉ thắng 4/19 dataset;
mean không phải lúc nào cũng kém nhất.

**(2) So sánh các phương pháp impute (Fig. 2)**: ở 20% thiếu, missforest tốt nhất, condexp ≈ iterativeBR, mean kém hẳn. Ở 50%, mọi phương pháp (trừ mean) giảm chính xác
nhưng **condexp ít bị ảnh hưởng nhất** và **nhanh hơn missforest ~2 bậc độ lớn**. Chênh lệch R² impute giữa tốt nhất và kém nhất trung bình 0,5 (20%) và 0,3 (50%).

**(3) Liên hệ impute – dự đoán (Fig. 4, 5)**:

| Phát hiện | Bằng chứng |
|---|---|
| **Lợi ích dự đoán ≤ 10% lợi ích impute** | Độ dốc hiếm khi > 0,1; với XGBoost trung bình ≈ 0,025 hoặc nhỏ hơn (bằng 0 khi không indicator ở 20% thiếu). Ví dụ: tăng 0,3 R² impute (mean → condexp) chỉ tăng **0,0075** R² dự đoán |
| **Mô hình càng mạnh, impute càng ít quan trọng** | Độ dốc giảm MLP → SAINT → XGBoost; hiệu ứng dương có ý nghĩa với MLP nhưng **không** với SAINT, XGBoost (khi không indicator) |
| **Thêm indicator, impute ít quan trọng hơn** | Độ dốc giảm rõ khi có indicator (ví dụ Bike_Sharing, 50%: MLP slope 0,23 → MLP + indicator −0,01) |
| **Kết quả phi tuyến (thật), impute ít đáng tin hơn** | Tương quan trung bình với kết quả thật **thấp hơn 0,1–0,3** so với kết quả tuyến tính, nhiều dataset tương quan ≈ 0 |
| **Tỉ lệ thiếu cao hơn** (Fig. 12) | Hiệu ứng (slope) lớn hơn nhưng quan hệ **nhiễu hơn** (tương quan thấp hơn); với dữ liệu thật và mô hình mạnh, hiệu ứng vẫn rất nhỏ |
| **MNAR** (Fig. 34) | Hiệu ứng **thấp hơn** MCAR một cách nhất quán; không indicator thì impute tốt hơn còn **làm giảm** trung bình accuracy của XGBoost và SAINT — vì mean giữ được thông tin "giá trị này đã bị impute" |

**(4) Vì sao indicator có lợi ngay cả ở MCAR** (khi nó không chứa thông tin về y):
- Giả thuyết của tác giả: predictor tối ưu khi có giá trị thiếu = **hợp của hàm impute và hàm dự đoán**, nhưng hàm dự đoán tối ưu trên dữ liệu impute thường **gián đoạn
  tại các điểm được impute**; indicator hoạt động như **công tắc** giúp mô hình biểu diễn các gián đoạn đó.
- **Indicator xáo trộn** làm **giảm** hiệu năng (trừ XGBoost không đổi) và không làm thay đổi quan hệ impute–dự đoán → lợi ích của indicator **không** đến từ regularization hay
  từ việc đếm số giá trị thiếu, mà từ thông tin **cột nào** thiếu.
- Một đặc trưng khi bị impute trung bình chỉ **quan trọng bằng ~½** so với khi được quan sát (nhiều đặc trưng kém 10 lần) → giá trị impute đóng góp kém hơn giá trị thật.
- **XGBoost ở 50% thiếu không có indicator**: không phương pháp impute nào giúp, tốt nhất là **xử lý native** — XGBoost cần biết giá trị nào bị thiếu; impute tinh vi làm khó phân biệt
  giá trị impute với giá trị quan sát; **thêm indicator** khôi phục thông tin này và giúp XGBoost tận dụng được impute tốt (đặc biệt missforest).

### 11.5 Kết luận của tác giả

- Impute **có** vai trò với dự đoán, nhưng **nhỏ**; mức độ bị điều tiết bởi: mô hình linh hoạt, indicator, kết quả phi tuyến.
- Kết quả rút ra từ MCAR (thuận lợi nhất) → với dữ liệu thiếu tự nhiên (thường MNAR), lợi ích còn nhỏ hơn; phương pháp impute mới thường chỉ cải thiện ít so với SOTA
  → lợi ích dự đoán còn nhỏ hơn nữa.
- Lý do impute tốt không luôn đi kèm dự đoán tốt: đặc trưng được khôi phục tốt có thể **không có tính dự báo**; khó học predictor tốt cho **mọi mẫu hình thiếu**;
  R² impute là thước đo không hoàn hảo (missforest ≈ iterativeBR về R² impute nhưng dự đoán tốt hơn).
- **Hạn chế / hướng mở**: impute ngẫu nhiên vs tất định, multiple imputation; indicator **nhân đôi số đặc trưng** — nên xem xét encoding nhận biết thiếu,
  embedding thiếu học được, lớp mạng nhận biết thiếu. Định hướng: phát triển mô hình **tự xử lý giá trị thiếu** và tận dụng indicator, thay vì chỉ cải thiện impute.

---

## 12. A Novel Machine Learning Data Preprocessing Method for Enhancing Classification Algorithms Performance

| | |
|---|---|
| **Tác giả** | Theodoros Iliou, Christos-Nikolaos Anagnostopoulos (University of the Aegean), Marina Nerantzaki, George Anastassopoulos (Democritus University of Thrace) |
| **Nguồn** | 16th EANN Workshops, 2015 (ACM) — DOI 10.1145/2797143.2797155 |
| **Loại bài** | Đề xuất phương pháp + thực nghiệm (workshop paper) |
| **File** | `paper/2797143.2797155.pdf` |

### 12.1 Tóm tắt

Bài đề xuất một phương pháp tiền xử lý mới dựa trên **các phép biến đổi đại số tuyến tính đơn giản**, nhằm **giảm chiều và loại dư thừa**, sinh ra một tập đặc trưng mới
chứa thông tin hữu ích của dữ liệu gốc để tăng hiệu năng phân loại. Phương pháp được so với **PCA** trên 3 dataset UCI "khó" (các bộ phân loại thường đạt < 75%):
Mammographic Masses, Indian Liver, Contraceptive Method Choice; đánh giá bằng 5 bộ phân loại với repeated 10-fold cross-validation.
Kết luận của tác giả: đặc trưng sinh bởi phương pháp **cải thiện rõ rệt** hiệu năng phân loại, trong khi PCA chỉ cải thiện ở Mammographic Masses.

### 12.2 Mục tiêu

Biến đổi dữ liệu đầu vào thành dạng **phù hợp và hiệu quả hơn** cho thuật toán phân loại: giảm số biến ban đầu, loại dư thừa, tạo đặc trưng mới mang thông tin của dataset gốc.
Tác giả nêu rõ các bước của phương pháp được xác định bằng **thử–sai (trial-and-error)**.

### 12.3 Phương pháp — 6 bước

Ký hiệu: `dataset1` có **n** dòng, **k** biến, **m** lớp.

```
 dataset1 (k biến)
   │ Bước 1: thêm k−1 hiệu giữa các phần tử KỀ NHAU trong mỗi dòng
   ▼
 dataset2 (k + (k−1) biến)
   │ Bước 2: coi mỗi dòng là HỆ SỐ của một đa thức (bậc giảm dần) → thêm hệ số của ĐẠO HÀM
   ▼
 dataset3
   │ Bước 3: chia ngẫu nhiên 10% → Basic-Set (d dòng), 90% → Rest-Set (r dòng)
   │         trong Basic-Set: "chia phải ma trận" từng dòng với các dòng CÙNG LỚP → mean / median → Total_Mean_m, Total_Median_m
   │ Bước 4: với mỗi dòng Rest-Set: chia phải với từng dòng Basic-Set → mean / median theo lớp → RS_Mean, RS_Median
   │         Final = Total (bước 3) − RS
   │ Bước 5–6: gom các biến, chuyển vị
   ▼
 Dataset cuối: 4 × m biến cho mỗi dòng của Rest-Set
```

**Bước 1 — hiệu kề nhau**: với mỗi dòng, thêm `k−1` biến mới:

```
 [ X(2)−X(1),  X(3)−X(2),  …,  X(k)−X(k−1) ]          (1)
 Ví dụ k = 3:  [X1, X2, X3]  →  [X1, X2, X3, X2−X1, X3−X2]
```

**Bước 2 — đạo hàm đa thức**: coi vector thuộc tính của mỗi dòng là hệ số đa thức theo **bậc giảm dần**; tính đạo hàm → vector hệ số mới **ngắn hơn một phần tử**, thêm vào → `dataset3`.
Ví dụ với dòng 5 giá trị (Table 3 của bài): sinh thêm 4 biến `f′(X1·x⁴), f′(X2·x³), f′(X3·x²), f′((X2−X1)·x¹)`.

**Bước 3 — Basic-Set**: chọn ngẫu nhiên **10%** của `dataset3` làm Basic-Set (d dòng, m lớp), **90%** còn lại là Rest-Set.
- Với mỗi dòng x của Basic-Set: tính **matrix right division** (phép chia phải, `B/A ≈ B·inv(A)`, chính xác hơn `B/A = (A′\B′)′`) giữa dòng x và các dòng **cùng lớp** m.
- Lấy trung bình và trung vị:

```
 Mean_class_m_row_x   = Mean_i  ( row_x / row_mᵢ )          (2)       mᵢ: các dòng thuộc lớp m trong Basic-Set
 Median_class_m_row_x = Median_i( row_x / row_mᵢ )          (3)
 Total_Mean_m   = (1/d) Σ_{i=1..d} Mean_class_m_row_i       (4)       → m giá trị Total_Mean
 Total_Median_m = (1/d) Σ_{i=1..d} Median_class_m_row_i     (5)       → m giá trị Total_Median
```

**Bước 4 — Rest-Set**: với mỗi dòng j của Rest-Set (r dòng), chia phải với **từng dòng của Basic-Set**, lấy mean/median **theo lớp** m:

```
 RS_Mean_class_m_row_j   = Mean_i  ( row_j / row_mᵢ )                       (6)
 RS_Median_class_m_row_j = Median_i( row_j / row_mᵢ )                       (7)
 Final_Mean_m_row_j   = Total_Mean_m (bước 3)   − RS_Mean_class_m_row_j      (8)
 Final_Median_m_row_j = Total_Median_m (bước 3) − RS_Median_class_m_row_j    (9)
```

**Bước 5**: lấy 4 nhóm giá trị `RS_Mean`, `RS_Median`, `Final_Mean`, `Final_Median` cho mọi lớp, xếp vào một bảng (Table 5).
**Bước 6**: **chuyển vị** bảng → dataset cuối, mỗi dòng Rest-Set có **4·m biến** (với m lớp), sẵn sàng đưa vào bất kỳ bộ phân loại nào.

### 12.4 Thiết kế thực nghiệm

| Hạng mục | Chi tiết |
|---|---|
| Dataset | UCI: **Mammographic Masses**, **Indian Liver Patient**, **Contraceptive Method Choice** |
| So sánh | Dữ liệu gốc · PCA · phương pháp đề xuất |
| Bộ phân loại (WEKA 3.6, tham số mặc định) | IB1 (láng giềng gần nhất), J48 (C4.5), Random Forest, Multilayer Perceptron, Rotation Forest |
| Đánh giá | **Repeated 10-fold cross-validation** |
| Thước đo | Precision, Recall, **Cohen's kappa** (đồng thuận đã hiệu chỉnh theo may rủi; > 0 là tốt hơn ngẫu nhiên), **Weighted Avg ROC area** (0,5 ≈ đoán ngẫu nhiên, → 1 là tối ưu) |

### 12.5 Kết quả (Table 6–8)

**Kappa** theo từng bộ phân loại (Gốc / PCA / Đề xuất):

| Dataset | IB1 | J48 | Random Forest | MLP | Rotation Forest |
|---|---|---|---|---|---|
| Mammographic Masses | 0,48 / 0,46 / **1** | 0,67 / 0,63 / **0,98** | 0,58 / 0,59 / **0,99** | 0,61 / 0,62 / **0,99** | 0,67 / 0,66 / **1** |
| Indian Liver | 0,17 / 0,242 / **0,87** | 0,16 / 0,001 / **0,638** | 0,20 / 0,20 / **0,734** | 0,18 / 0,137 / 0,007 | 0,005 / 0,006 / **0,923** |
| Contraceptive Method | 0,126 / 0,13 / **0,99** | 0,27 / 0,22 / **0,93** | 0,248 / 0,23 / **0,98** | 0,30 / 0,32 / **0,97** | 0,29 / 0,25 / **1** |

**Precision** (Gốc → Đề xuất), ví dụ: Mammographic IB1 0,743 → 1; Indian Liver Rotation Forest 0,65 → 0,97; Contraceptive IB1 0,436 → 0,999.

Nhận xét của tác giả:
- **Mammographic Masses**: cả PCA và phương pháp đề xuất đều tốt hơn dữ liệu gốc với mọi bộ phân loại; phương pháp đề xuất nhỉnh hơn PCA.
- **Indian Liver**: PCA **không** cải thiện; phương pháp đề xuất cải thiện đáng kể với mọi bộ phân loại **trừ MLP**.
- **Contraceptive Method Choice**: phương pháp đề xuất đạt tỉ lệ phân loại đúng **gần gấp đôi** so với PCA và dữ liệu gốc.

### 12.6 Hướng tiếp theo (do tác giả nêu)

Thử trên nhiều dataset và bộ phân loại hơn; sửa đổi/mở rộng phương pháp để trở thành **một thuật toán phân loại**.

---

## 13. mlinspect: A Data Distribution Debugger for Machine Learning Pipelines

| | |
|---|---|
| **Tác giả** | Stefan Grafberger, Shubha Guha, Sebastian Schelter (AIRLab, University of Amsterdam), Julia Stoyanovich (New York University) |
| **Nguồn** | SIGMOD 2021 — Demo Track — DOI 10.1145/3448016.3452759 |
| **Loại bài** | Demo paper (trình diễn công cụ) |
| **File** | `paper/3448016.3452759.pdf` — mã nguồn: `github.com/stefan-grafberger/mlinspect` |

### 13.1 Tóm tắt

Ứng dụng ML rất **nhạy với dữ liệu đầu vào**. **mlinspect** là thư viện kiểm tra pipeline tiền xử lý ML dựa trên **lineage (dòng dõi dữ liệu)**, gọn nhẹ,
giúp phát hiện **data distribution bug**. Khác các công cụ trước, mlinspect:
- làm việc trên **các trừu tượng khai báo** của thư viện phổ biến (pipeline estimator/transformer của scikit-learn, pandas);
- xử lý được cả **dữ liệu quan hệ (bảng)** và **dữ liệu ma trận**;
- **không cần chèn code thủ công** (instrument) vào pipeline.

Bài demo trình diễn cách dùng mlinspect phát hiện và sửa lỗi phân phối dữ liệu trong một pipeline y tế mẫu.

### 13.2 Bài toán: data distribution bug

**Data distribution bug** = tên gọi chung cho:
- **thiên lệch có sẵn** (pre-existing bias): nhóm bị thiếu/thừa đại diện trong dữ liệu huấn luyện;
- **thiên lệch kỹ thuật** (technical bias): lệch phân phối **do chính các bước chuẩn bị dữ liệu** gây ra.

Vì sao khó bắt:
- Các bước pipeline dùng **thư viện và trừu tượng khác nhau**; biểu diễn dữ liệu đổi từ **quan hệ sang ma trận** trong quá trình chuẩn bị.
- Tiền xử lý kết hợp phép toán quan hệ trên bảng với pipeline estimator/transformer (có thể lồng nhau; cũng có trong SparkML, TensorFlow Transform).
- Truy ngược từ một dòng đã thành vector đặc trưng về **dữ liệu đầu vào dễ đọc** rất tốn công.
- Data scientist ít khi chịu **instrument code thủ công** như các hệ quản lý mô hình yêu cầu.

### 13.3 Phương pháp — kiến trúc mlinspect

```
 Code pipeline Python gốc (pandas + scikit-learn) — KHÔNG sửa
        │ chạy MỘT lần
        ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │ 1. Trích xuất DAG (logical query plan)                                                   │
 │    · module `inspect` của Python nhận diện các lời gọi hàm liên quan                      │
 │    · kết hợp với cây cú pháp (AST) → biểu diễn trung gian (IR) → dựng DAG                 │
 │ 2. Instrument các toán tử (tự động, chuẩn bị TRƯỚC khi chạy)                              │
 │ 3. Backend theo thư viện: chuyển lời gọi tới backend của pandas / scikit-learn theo module │
 │ 4. Inspections: lan truyền annotation (ví dụ lineage của tuple) qua các toán tử           │
 │ 5. Checks: luật kiểm tra ràng buộc trên DAG đã gắn annotation                             │
 └─────────────────────────────────────────────────────────────────────────────────────────┘
        ▼
 DAG được gắn kết quả (histogram, mẫu output...) + cảnh báo khi vượt ngưỡng
```

**Biểu diễn dataflow** — các phần tử của DAG:

| Thành phần | Nội dung |
|---|---|
| Nguồn dữ liệu | Thường là dữ liệu quan hệ |
| Dữ liệu chảy qua | Tập tuple quan hệ **hoặc** tensor |
| Toán tử quan hệ | join, selection, projection (bảng → bảng) |
| Bộ mã hoá đặc trưng | one-hot encoder... (bảng → vector) |
| Toán tử tiền xử lý ML | chuẩn hoá, nối (vector → vector) |

Các trừu tượng khai báo như cắt dữ liệu của pandas, `ColumnTransformer` của scikit-learn, pipeline của SparkML **tự nhiên có dạng DAG**.

**Inspection** — giao diện **không phụ thuộc thư viện** để lan truyền annotation:
- Giữ một **trạng thái kích thước cố định**, được gọi **một lần cho mỗi toán tử** trong DAG và reset sau mỗi toán tử.
- Có quyền truy cập **tuple output** của toán tử và **input tương ứng đã được annotate**.
- Gắn annotation cho tuple output, và có thể gắn kết quả (ví dụ **histogram** của output) vào toán tử trong DAG.
- Chi phí chỉ là **hằng số trên mỗi tuple** chảy qua DAG.

**Check** — cách tiếp cận dựa trên luật, kiểm tra ràng buộc trên DAG đã annotate, ví dụ **so sánh thay đổi histogram với một ngưỡng**.

**Ví dụ (Fig. 1)** — một phép selection làm lệch phân phối tuổi:

```
 data = data[data.zip == 123]

   age  zip                         σ zip=123                    age  zip
   60   123                       ───────────►                   60   123
   60   123                                                      60   123
   20   456                                                      20   123
   20   123
 phân phối tuổi 60/20: 50% / 50%                         phân phối tuổi 60/20: 66% / 33%   → vượt ngưỡng → CẢNH BÁO
```

**Các nhóm kiểm tra mà annotation dựa trên lineage cho phép**:
- **Công bằng**: phát hiện toán tử **gây ra hoặc khuếch đại** tình trạng thiếu đại diện của một nhóm.
- **Ràng buộc pháp lý**: kiểm tra việc dùng đặc trưng nhân khẩu học bị cấm.
- **Hiệu năng theo nhóm**: hỗ trợ tìm nhóm mà mô hình hoạt động kém, kể cả khi thuộc tính xác định nhóm đã bị **projection loại bỏ sớm** hoặc chỉ còn là một chiều của ma trận đặc trưng
  (lineage vẫn nối được dòng đặc trưng về bản ghi gốc).

Các inspection/check có sẵn được nêu trong bài:

| Tên | Chức năng |
|---|---|
| **Materialize First Output Rows** | Lưu mẫu các dòng output đầu tiên của mỗi toán tử |
| Histogram theo nhóm | Tính histogram các nhóm (nhạy cảm) ở kết quả trung gian |
| Record-level lineage | Truy vết lineage ở mức bản ghi |
| **No Bias Introduced For** (check) | So histogram input/output của toán tử; cảnh báo nếu **tỉ lệ nhóm thiểu số giảm** vượt ngưỡng chấp nhận |
| **No Illegal Features** (check) | Kiểm tra mô hình có dùng thuộc tính có thể bị cấm (ví dụ giới tính) không |

### 13.4 Kịch bản demo

**Pipeline y tế mẫu** (pandas + scikit-learn) — mục tiêu phân loại bệnh nhân có nguy cơ biến chứng; ràng buộc **công bằng giao thoa**: tỉ lệ false negative bằng nhau giữa các nhóm
kết hợp `age_group` × `race`:

```
 patients.csv ─┐
               ├─► JOIN ─► tính số biến chứng trung bình theo nhóm tuổi, gán nhãn nhị phân (cao hơn trung bình nhóm tuổi)
 histories.csv ┘        ─► PROJECTION (chọn thuộc tính)
                        ─► SELECTION (chỉ giữ một số county)          ← nguy cơ lỗi phân phối nếu county tương quan với tuổi/chủng tộc
                        ─► ColumnTransformer:
                              smoker, county, race : impute MODE → one-hot
                              last_name            : vector word embedding huấn luyện sẵn
                              num_children, income : chuẩn hoá
                        ─► mạng nơ-ron
```

**Các bước người dùng thực hiện** trên giao diện web (code bên trái, DAG bên phải):

1. Chọn inspection/check cần chạy, chạy pipeline như trong notebook; DAG cập nhật theo code.
2. **Materialize First Output Rows**: bấm vào nút DAG để xem mẫu output của toán tử, code tương ứng được tô sáng — ví dụ toán tử one-hot nhận dữ liệu bảng và sinh ma trận.
3. **No Bias Introduced For**: mlinspect **tô sáng toán tử có vấn đề** trong DAG; bấm vào để xem **histogram trước/sau**.
4. Trong dataset mẫu, `county` **tương quan** với thuộc tính nhạy cảm `race` → phép lọc county gây lỗi phân phối. Sửa bằng cách **thêm một giá trị county** vào danh sách lọc,
   chạy lại check và xem lại histogram để xác nhận.

---

## 14. JENGA — A Framework to Study the Impact of Data Errors on the Predictions of Machine Learning Models

| | |
|---|---|
| **Tác giả** | Sebastian Schelter (University of Amsterdam), Tammo Rukat (Amazon Research), Felix Biessmann (Einstein Center Digital Future) |
| **Nguồn** | EDBT 2021 — Industrial Paper — DOI 10.5441/002/edbt.2021.63 (CC BY-NC-ND 4.0) |
| **Loại bài** | Bài công nghiệp: thư viện mã nguồn mở + hai use case |
| **File** | `paper/9-.pdf` — mã nguồn: `github.com/schelterlabs/jenga` |

### 14.1 Tóm tắt

Hầu hết mô hình ML **dễ tổn thương trước lỗi trong dữ liệu serving** (dữ liệu mô hình dự đoán khi chạy thật). Lỗi này thường do **bug trong code tiền xử lý** hoặc **thay đổi schema
không lường trước** ở nguồn dữ liệu bên ngoài; chúng gây hậu quả nặng mà lại khó lường và khó bắt. **Jenga** là thư viện thử nghiệm nhẹ giúp kiểm tra **độ bền của mô hình**
trước các lỗi dữ liệu phổ biến, gồm: trừu tượng **task** (dataset + mô hình), tập **data corruption** tổng hợp dễ mở rộng (giá trị thiếu, outlier, lỗi gõ, nhiễu đo...)
và **evaluator**. Hai use case: (1) đo độ bền của mô hình với dữ liệu thiếu; (2) **stress-test** tự động các ràng buộc toàn vẹn viết bằng **TensorFlow Data Validation (TFDV)**.

### 14.2 Bối cảnh — lỗi dữ liệu trong ML production

Lỗi trong production thường **không** đến từ thay đổi của quá trình sinh dữ liệu thật, mà từ **lỗi lập trình trong pipeline tạo dữ liệu serving** hoặc **lỗi tích hợp
dữ liệu nhiều nguồn**; thường chỉ lộ ra khi mô hình đã triển khai. Các phương pháp ML về thay đổi dữ liệu đều cần **giả định phân phối** → khó liên hệ với lỗi thực tế.

Hai ví dụ thật tác giả gặp:
- Mô hình tuyến tính dùng tuổi; một kỹ sư (không hiểu mô hình) viết code **thay tuổi thiếu bằng 0** (giá trị khởi tạo mặc định của số nguyên) → mô hình coi những người này là **"trẻ tập đi"**.
- Pipeline dữ liệu train và serving chạy ở **hai môi trường cloud khác nhau** → code chuẩn bị dữ liệu hai bên **dần khác nhau** → lỗi dữ liệu khó phát hiện.

### 14.3 Phương pháp — thiết kế Jenga: 3 trừu tượng cốt lõi

```
 ┌──────────────┐     ┌────────────────────────┐     ┌──────────────────────────────────────────────────────────┐
 │ TASK          │     │ DATA CORRUPTION         │     │ EVALUATOR                                                  │
 │ raw dataset   │ ──► │ nhận dataframe → trả   │ ──► │ lặp nhiều lần: làm hỏng BẢN SAO tập test → đo hiệu năng     │
 │ + mô hình ML  │     │ dataframe đã làm hỏng  │     │ mô hình trên dữ liệu hỏng → so với điểm trên dữ liệu sạch  │
 │ = 1 bài toán  │     │ (cột c, tỉ lệ dòng r)  │     │ (+ tuỳ chọn: kiểm tra schema validation có bắt được không) │
 └──────────────┘     └────────────────────────┘     └──────────────────────────────────────────────────────────┘
```

#### a) Task mẫu (phân loại nhị phân, nhỏ, chạy vài phút trên CPU)

Phân loại review game có hữu ích không · ước lượng thu nhập > 50.000 USD/năm từ dữ liệu nhân khẩu · phân biệt ảnh giày sneaker và ankle boot.

#### b) Cách lấy mẫu giá trị bị làm hỏng (áp cho MỌI loại lỗi, không chỉ giá trị thiếu)

Mỗi lỗi cần chỉ định **cột c** và **tỉ lệ dòng r ∈ [0,1]**. Giá trị x_c bị làm hỏng theo một trong ba cách (mượn từ lý thuyết giá trị thiếu):

| Cách | Ý nghĩa |
|---|---|
| Độc lập với mọi giá trị khác | Hoàn toàn ngẫu nhiên (MCAR) |
| Phụ thuộc giá trị ở **cột khác** c | Ngẫu nhiên có điều kiện (MAR) |
| Phụ thuộc giá trị **chính cột** c | Không ngẫu nhiên (MNAR) |

#### c) Các loại data corruption

| Corruption | Cách làm | Mô phỏng lỗi thực tế |
|---|---|---|
| **Missing values** | Xoá giá trị theo MCAR / MAR / MNAR; hoặc theo **"độ khó dự đoán"** — dựa trên **entropy** dự đoán của mô hình (giống uncertainty sampling trong active learning) | Lỗi lập trình, tích hợp dữ liệu, đổi schema |
| **Swapped values** | Thay một tỉ lệ giá trị của cột này bằng giá trị cột khác | Người dùng nhập nhầm ô trong form; lập trình viên ghi nhầm cột đích |
| **Scaling** | Nhân ngẫu nhiên một tập con giá trị với 10, 100 hoặc 1000 | Đổi đơn vị trong code (ghi **mili giây** thay vì giây) |
| **Noise** | Cộng nhiễu Gauss quanh giá trị, độ lệch chuẩn ngẫu nhiên trong [2, 5] | Lỗi đo |
| **Encoding errors** | Thay ký tự trong chuỗi (ví dụ `a` → `á`) | Dữ liệu web khai báo sai encoding |
| **Image corruptions** | Tích hợp từ thư viện Augmentor | — |

#### d) Hai evaluator

| Evaluator | Chức năng |
|---|---|
| **CorruptionImpactEvaluator** | Nhận task, mô hình đã huấn luyện, danh sách corruption; áp từng corruption lên tập test giữ lại; tính hiệu năng trên dữ liệu hỏng |
| **SchemaStresstestEvaluator** | Như trên, **thêm một schema validation** (TFDV): ghi nhận schema có **bắt đúng** những corruption gây tác hại không |

#### e) Mở rộng (API)

- **Task tuỳ biến**: kế thừa `ClassificationTask`, cài đặt: constructor (nạp dữ liệu), `fit_model` (huấn luyện từ pandas dataframe, mô hình theo API predictor của scikit-learn),
  `score_on_test_data` (tính metric, ví dụ ROC AUC từ xác suất dự đoán).
- **Corruption tuỳ biến**: kế thừa `DataCorruption`, chỉ cần cài đặt `transform(data)`. Ví dụ `MillisInsteadOfSeconds`: sao chép sâu dữ liệu → chọn ngẫu nhiên một tỉ lệ dòng →
  nhân giá trị cột với 1000.
- Ví dụ dùng: tạo `IncomeEstimationTask` → huấn luyện mô hình → khai báo `MissingValues(column='age', missingness='mcar', fraction=0.05)` →
  `CorruptionImpactEvaluator(task).evaluate(model, num_repetitions=10, corruption)` → so `baseline_score` với `corrupted_scores`.
- Công nghệ: pandas, numpy, pipeline của scikit-learn, keras/tensorflow.

### 14.4 Use case 1 — Độ bền của mô hình với dữ liệu thiếu

**Thiết lập**: Logistic regression cho task ước lượng thu nhập; huấn luyện trên dữ liệu **sạch**, đánh giá ROC AUC trên test có giá trị thiếu tiêm vào 4 cột hạng mục
`education`, `marital_status`, `workclass`, `occupation`, với tỉ lệ 1%, 10%, 50%, 99%, theo cả MCAR/MAR/MNAR; mỗi cấu hình lặp 10 lần. Ba cách xử lý thiếu:

1. Thay bằng **ký hiệu placeholder** cố định.
2. Thay bằng **mode** (`SimpleImputer` của scikit-learn).
3. **Impute bằng mô hình ML** riêng (thư viện **datawig**: tự featurise dữ liệu bảng, huấn luyện mạng nơ-ron dự đoán giá trị thiếu).

**Kết quả (Fig. 1)**:
- Tác động **phụ thuộc mạnh vào cột**: gần như không với `workclass`; rất nhỏ với `occupation` khi < 50% thiếu; mạnh hơn với `education`; **mạnh nhất** với `marital_status`.
- Tác động đôi khi khác nhau theo cơ chế thiếu (ví dụ MNAR ở `marital_status` dễ xử lý hơn).
- **Không có chiến lược xử lý nào vượt trội**: placeholder đơn giản và tốt trong nhiều trường hợp; datawig giúp ở một số thiết lập (tỉ lệ thiếu cao ở `education`, hoặc `occupation`).
- Kết luận của tác giả: bản thân mô hình (kể cả kèm impute) **không xử lý tin cậy được mọi trường hợp** → cần **đặt kiểm tra (checks)** để bảo vệ dữ liệu serving.

### 14.5 Use case 2 — Stress-test ràng buộc toàn vẹn (TFDV)

**Thiết lập**:

```
 1. Task phân loại review game (dự đoán review có hữu ích)
 2. Schema bán tự động: tfdv.generate_statistics_from_df(train) → tfdv.infer_schema(...)
    · schema suy ra nhận đúng kiểu và miền hạng mục của đa số cột, nhưng QUÁ CHẶT với review_date
      (giá trị ngày tương lai luôn mới) → chỉnh tay: distribution_constraints.min_domain_mass = 0.0 cho phép giá trị mới
    · ví dụ ràng buộc: star_rating kiểu INT, presence.min_fraction = 1.0; verified_purchase kiểu BYTES, miền {"N", "Y"}
 3. Huấn luyện mô hình
 4. SchemaStresstest().run(task, model, schema, num_corruptions=250, performance_threshold=0.03)
    → sinh NGẪU NHIÊN 250 corruption cho dữ liệu serving, đo tác động lên AUC và xem schema có báo vi phạm không
```

**Phân loại kết quả** (AUC trên dữ liệu sạch 0,78828; "thất bại" = giảm > 3%):

| | Hiệu năng giảm > 3% | Hiệu năng giữ trong ngưỡng |
|---|---|---|
| **TFDV báo vi phạm** | **True positive** | **False positive** (vẫn đáng điều tra — có thể là dấu hiệu lỗi code hoặc nguồn dữ liệu) |
| **TFDV không báo** | **False negative** — quan trọng nhất: lỗi mô hình dễ tổn thương trong production → **phải bổ sung schema** | **True negative** |

**Kết quả trên 250 corruption** (Table 1):

| Nhóm | Số lượng | Ví dụ |
|---|---|---|
| True positive | 88 | Thiếu giá trị ở `star_rating` (25%) → **mô hình crash**; swap `review_body`↔`vine`, `verified_purchase`↔`title` → giá trị chưa thấy; nhiễu Gauss ở `star_rating` → sai kiểu int → float |
| True negative | 75 | Corruption ở cột văn bản mà TFDV bỏ qua **và** mô hình cũng không dùng (`review_id`, `product_id`...) |
| False positive | 39 | 93% thiếu ở `vine` nhưng ít ảnh hưởng; lỗi encoding ở `marketplace` (cột mô hình không dùng) |
| **False negative** | 48 (phần còn lại: 250 − 88 − 75 − 39) | **Scaling** `star_rating` (92%) → thiếu **range check**; encoding/thiếu/swap ở cột văn bản `title_and_review` → TFDV **không tự sinh ràng buộc cho cột văn bản** → cần kiểm tra **độ dài** và **encoding** |

Quy trình đề xuất: data scientist **lặp lại cải thiện ràng buộc cho đến khi vượt qua stress-test**; tác giả cho rằng nên trở thành **best practice** chạy stress-test lỗi dữ liệu
trước khi đưa mô hình vào production và tích hợp vào pipeline triển khai ML.

### 14.6 Bài học từ thực tế (Mục 6)

- Giá trị thiếu có thể **lan qua nhiều pipeline nối nhau** đến khi mô hình hướng khách hàng crash; truy ngược về nguồn rất tốn công.
- Ứng dụng đa ngôn ngữ thường gặp **lỗi encoding** do kho trung gian cấu hình sai.
- Dữ liệu **lịch/ngày tháng** thường sai (ví dụ ngày lễ di động).
- Mô hình do nhóm chuyên ML huấn luyện rồi bàn giao cho nhóm nghiệp vụ: dữ liệu nhóm nghiệp vụ cung cấp **không được lấy mẫu đại diện** → dataset shift.
- Mục tiêu dài hạn: thư viện lớn các corruption gặp trong thực tế để **tự động kiểm thử mô hình** (tương tự unit test, integration test), tích hợp vào **CI cho ML**;
  mở rộng sang hồi quy và xếp hạng.

---

## 15. Auto-Prep: Efficient and Automated Data Preprocessing Pipeline

| | |
|---|---|
| **Tác giả** | Mehwish Bilal, Ghulam Ali, Muhammad Waseem Iqbal, Muhammad Anwar, Muhammad Sheraz Arshad Malik, Rabiah Abdul Kadir |
| **Nguồn** | *IEEE Access* vol. 10, 2022 — DOI 10.1109/ACCESS.2022.3198662 (CC BY 4.0) |
| **Loại bài** | Đề xuất hệ thống (công cụ Python) + đánh giá trên 11 dataset |
| **File** | `paper/Auto-Prep_Efficient_and_Automated_Data_Preprocessing_Pipeline.pdf` |

### 15.1 Tóm tắt

Mỗi tác vụ tiền xử lý có rất nhiều lựa chọn khiến người ít kinh nghiệm bối rối. **Auto-Prep** là kiến trúc tiền xử lý tự động viết bằng Python cho AutoML, cung cấp
hỗ trợ **tự động, tương tác và dựa trên dữ liệu**: (1) **phát hiện vấn đề dữ liệu** và trình bày cho người dùng bằng trực quan hoá; (2) **đánh giá các kỹ thuật ứng viên**
và **khuyến nghị** kỹ thuật làm sạch/chuẩn bị hiệu quả nhất. Đầu vào chỉ gồm **đường dẫn file dataset** và **tên cột mục tiêu**.
Đánh giá trên 11 dataset (6 phân loại, 5 hồi quy): mô hình huấn luyện trên dữ liệu Auto-Prep xử lý **bằng hoặc tốt hơn** dữ liệu tiền xử lý thủ công.

### 15.2 Mục tiêu

Hiện chưa có kỹ thuật tự động nào đủ trưởng thành cho tiền xử lý; các công cụ cho phép áp nhiều thuật toán nhưng **không xét thuật toán nào hợp với dataset**,
và bước tiền xử lý trong AutoML thường chỉ là biến đổi để dữ liệu **đúng định dạng** chứ không nhằm tăng hiệu năng. Bài tự động hoá 6 chức năng:

| # | Chức năng |
|---|---|
| 1 | Tự động phát hiện **dòng trùng** |
| 2 | Tự động phát hiện **kiểu dữ liệu** của đặc trưng (cả kiểu thống kê) |
| 3 | Tự động **điền giá trị thiếu** |
| 4 | Tự động **mã hoá đặc trưng hạng mục** |
| 5 | Tự động **giảm đặc trưng** (chọn đặc trưng; trích đặc trưng tuỳ chọn) |
| 6 | Tự động **co giãn đặc trưng** (scaling) |

**Khảo sát AutoML** (Table 1 của bài): Auto-Keras, DataRobot, H2O-DriverlessAI không có tiền xử lý/sinh đặc trưng; TransmogrifAI nhận diện kiểu cơ bản và nâng cao
(điện thoại, địa chỉ, tiền tệ) nhưng không ổn định; H2O nhận diện kiểu cơ bản, nhiều tuỳ chọn biến đổi nhưng **không hỗ trợ chọn**; Auto-sklearn yêu cầu khai báo kiểu thủ công
và chỉ nhận dữ liệu số; AutoWeka và TPOT chỉ hỗ trợ chọn mô hình.

### 15.3 Phương pháp

**Nguyên tắc thiết kế**: cách hiển nhiên là **hoán vị mọi kỹ thuật** rồi đánh giá mọi tổ hợp — nhưng quá tốn thời gian/tính toán và thiếu chuẩn đánh giá tổ hợp.
Vì vậy Auto-Prep xử lý **từng tác vụ độc lập**, ra quyết định hợp lý ở mỗi bước dựa trên dataset.

```
 (file dataset, cột mục tiêu)
    ▼
 A. Phát hiện kiểu dữ liệu ─► B. Xử lý giá trị thiếu ─► C. Mã hoá hạng mục ─► D. Chọn đặc trưng ─► E. Scaling ─► F. Trích đặc trưng (tuỳ chọn)
    (+ phát hiện dòng trùng)    (phát hiện → trực quan hoá → bỏ cột thiếu nhiều → thử nhiều cách → KHUYẾN NGHỊ cách tốt nhất)
    ▼
 Dữ liệu sẵn sàng cho mô hình ML
```

#### A. Tự động phát hiện kiểu dữ liệu (Fig. 1)

Mục tiêu không chỉ là kiểu cơ bản mà cả **kiểu thống kê** (hạng mục, rời rạc, liên tục). Hai bước:

1. Dùng suy luận của **pandas** để có kiểu cơ bản `int`, `float`, `object` (pandas xếp rất nhiều cột vào `object`, không tự nhận datetime).
2. **Kiểm tra lại từng phần tử** của cột `object` (lấy cảm hứng từ *brute-force guessing* của thư viện Messytables: lấy mẫu, thử ép sang mọi kiểu, bỏ phiếu đa số)
   theo **luật có thứ tự ưu tiên** — đã khớp kiểu trước thì không xét kiểu sau:

| Ưu tiên | Kiểu | Luật |
|---|---|---|
| 1 | **Bool** | Đúng **2 giá trị phân biệt** |
| 2 | **Date** | Dài **tối đa 10 ký tự** và chứa `-` hoặc `/`; thử chuyển sang `datetime64[ns]` của pandas (xử lý mọi định dạng mm/dd/yyyy, yyyy-mm-dd...); chuyển thành công thì **tách ra cột ngày, tháng, năm** (vừa nhận kiểu vừa làm feature engineering) |
| 3 | **Time** | Chứa `:` và tối đa 8 ký tự (hh:mm:ss) |
| 4 | **Category** | Tập **hữu hạn** giá trị văn bản |
| 5 | **String/object** | Phần còn lại |

Với cột số: **rời rạc** nếu số giá trị duy nhất hữu hạn, **liên tục** nếu (gần như) vô hạn.

#### B. Tự động xử lý giá trị thiếu (Fig. 2, Fig. 7)

```
 Phát hiện thiếu ─► Trực quan hoá (tỉ lệ + cơ chế) ─► Bỏ cột thiếu > 90% ─► Impute bằng mọi kỹ thuật ứng viên ─► Chấm điểm ─► Khuyến nghị
```

**(1) Phát hiện** — ba dạng biểu diễn thiếu:
- Chuẩn: `NAN`, `n/a`, ô trống.
- Không chuẩn: `—`, `-`, `na`, `?`...
- Theo ngữ cảnh: ví dụ cột có miền 0–100 thì `9999` là thiếu.
Hai dạng đầu có **danh sách mặc định**; dạng ba **hỏi người dùng** trước mỗi lần phát hiện có muốn thêm giá trị đặc biệt nào được coi là thiếu.

**(2) Cơ chế thiếu** (MCAR / MAR / MNAR): MNAR **không kiểm định được** vì thiếu thông tin. Để nhận biết phụ thuộc giữa các cột: mã hoá thiếu = 1, có = 0, tính
**hệ số tương quan Pearson (PCC)** giữa chỉ báo thiếu của từng cặp cột — các điểm (1,1) và (0,0) xuất hiện nhiều thì có phụ thuộc. **PCC > 0,8** → cơ chế **có lẽ là MAR**.

**(3) Trực quan hoá** để người dùng tự suy luận cơ chế:
- **Seaborn heatmap**: cột nào thiếu, tỉ lệ, thiếu rải rác hay thành khối lớn.
- **missingno matrix**: hiển thị mật độ để thấy **mẫu hình thiếu** (ví dụ nhóm cột cùng thiếu → nhiều khả năng MAR; rải rác → nhiều khả năng MCAR).
- **missingno heatmap**: ma trận PCC của chỉ báo thiếu giữa các cột (−1: cột này có thì cột kia thiếu; 0: độc lập; 1: cùng có/cùng thiếu); bỏ qua cột không thiếu.

**(4) Ngưỡng thiếu chấp nhận được**: tài liệu không thống nhất (≤ 5% không đáng kể; > 10% dễ lệch; có nghiên cứu cho thấy tới 90% vẫn không lệch nếu MAR và mô hình impute đúng)
→ Auto-Prep **giữ cột thiếu < 90%**, **bỏ cột thiếu nhiều hơn**; người dùng đổi được ngưỡng.

**(5) Kỹ thuật ứng viên theo cơ chế** (cài đặt bằng scikit-learn):

| Cơ chế | Ứng viên |
|---|---|
| MCAR | mean, median, mode, most frequent, KNN |
| MAR | KNN (không dùng mean/mode vì bỏ qua phụ thuộc giữa cột) |
| MNAR | Coi thiếu là **một hạng mục riêng**; **multiple imputation** |

Không dùng **xoá theo dòng (listwise deletion)** — vì khi đánh giá bằng bộ phân loại, xoá dòng thường "thắng" một cách vô lý (ví dụ chỉ còn một dòng đầy đủ).

**(6) Chọn kỹ thuật**: không có ground truth của giá trị thiếu và dataset có thể chứa nhiều cơ chế cùng lúc → **đánh giá gián tiếp**: với mỗi cột có thiếu, áp từng kỹ thuật ứng viên,
rồi huấn luyện **một số mô hình cơ bản** và lấy **accuracy trung bình** làm **điểm impute** của kỹ thuật:

| Tác vụ | Mô hình đánh giá |
|---|---|
| Phân loại | Naïve Bayes, Decision Tree (information gain), Linear Discriminant Analysis |
| Hồi quy | Linear Regression, Support Vector Regression, Random Forest Regressor |

Auto-Prep **không tự áp** kỹ thuật điểm cao nhất mà **hiển thị điểm mọi kỹ thuật và khuyến nghị** kỹ thuật cao nhất; người dùng có thể theo hoặc chọn khác.
(Ở bước này cột hạng mục tạm được **label encode** để đưa qua mô hình.)

#### C. Tự động mã hoá dữ liệu định tính (Fig. 8)

- Chia dữ liệu định tính thành: **bool** (đúng 2 giá trị), **categorical** (kiểu category — gồm *nominal* không thứ tự và *ordinal* có thứ tự), **object** (chuỗi vô hạn khả năng như email, địa chỉ).
- Theo khảo sát: **label/ordinal encoding** hợp với ordinal; với nominal, label encoding ngầm áp thứ tự → **one-hot** tốt hơn. Phân biệt nominal/ordinal rất khó vì phụ thuộc ngữ cảnh
  (màu kẹo không có thứ tự, màu đèn giao thông thì có).
- Cách làm: dữ liệu đã được label encode từ bước B → thử **one-hot chỉ cho cột kiểu category**, so accuracy, **chọn cách cho accuracy cao hơn**.
  Cột bool giữ nguyên (không đổi gì); cột object giữ nguyên (one-hot gây **lời nguyền số chiều**).
- Khảo sát các cách khác: Leave-One-Out encoding (trung bình target của các dòng cùng giá trị; cách ngây thơ O(n²)), Hash encoding (giới hạn số chiều bằng tham số).

#### D. Tự động chọn đặc trưng — **Backward Elimination** (Fig. 9)

```
 B1. Chọn mức ý nghĩa, thường 5% (p = 0,05)
 B2. Fit mô hình với TẤT CẢ đặc trưng
 B3. Tìm đặc trưng có p-value CAO NHẤT
 B4. Nếu p-value đó > mức ý nghĩa → sang B5; ngược lại → B6 (xong)
 B5. Xoá đặc trưng đó, fit lại mô hình, quay lại B3
 B6. Kết thúc — các đặc trưng còn lại đều có p-value < 0,05
```

#### E. Tự động co giãn đặc trưng

- Mô hình **nhạy** với scale: dùng gradient descent (hồi quy logistic/tuyến tính, mạng nơ-ron) và dựa trên khoảng cách (K-means, KNN, SVM). Mô hình **cây** gần như bất biến với scale
  (tách nút theo từng đặc trưng riêng).
- Hai cách: **Normalization** — tốt hơn cho thuật toán dựa trên khoảng cách; **Standardization** — tốt nhất cho mô hình dùng gradient descent.
- Vì lựa chọn phụ thuộc **loại mô hình** chứ không xác định được chỉ từ dữ liệu → **người dùng chọn** tham số `"Normalize"`, `"Standardize"` hoặc `"False"`.

#### F. Trích đặc trưng (tuỳ chọn)

Dùng **PCA**, nhưng **mặc định tắt**: không phải lúc nào cũng cần, có thể tốn kém, thành phần chính khó diễn giải hơn đặc trưng gốc, và chọn sai số thành phần có thể mất thông tin.

### 15.4 Thiết kế đánh giá

| Hạng mục | Chi tiết |
|---|---|
| Dataset | 11 dataset từ UCI, OpenML, Kaggle, chọn đa dạng đặc trưng, kích thước, vấn đề dữ liệu |
| Phân loại (6) | Chẩn đoán ung thư, yêu cầu bảo hiểm ô tô, Tic-Tac-Toe, Musk (nhị phân); hạt lúa mì, lỗi tấm thép (đa lớp) |
| Hồi quy (5) | Chất lượng không khí, ô tô, khách hàng thương mại điện tử, giá nhà, **thời tiết Szeged 2006–2016** |
| Mô hình | SVM (ung thư, bảo hiểm, Tic-Tac-Toe, hạt lúa mì), Decision Tree (Musk), Random Forest (tấm thép); Linear Regression (mọi dataset hồi quy) |
| So sánh | Cùng mô hình trên dữ liệu **Auto-Prep xử lý** vs dữ liệu **tiền xử lý thủ công** |
| Thước đo | Phân loại: confusion matrix, accuracy, precision, recall, F1. Hồi quy: R², MAE, MSE, RMSE (giá nhà dùng sai số trên log giá) |

### 15.5 Kết quả

- **Phân loại**: accuracy trên dữ liệu Auto-Prep **tăng hoặc gần bằng** so với dữ liệu thủ công (Table 4). Precision của dataset bảo hiểm ô tô **thấp ở cả hai cách** →
  dataset này có thể cần tiền xử lý nhiều hơn.
- **Hồi quy**: biểu đồ phân tán dự đoán–thực tế và các thước đo R², MAE, MSE, RMSE (Table 9–12) cho thấy phương pháp hoạt động hiệu quả.
- Kết luận của tác giả: Auto-Prep vừa **đơn giản hoá, tự động hoá** toàn bộ tiền xử lý, vừa **cải thiện hiệu năng** mô hình. Khi hiệu năng chưa thoả đáng là do dữ liệu cần
  làm sạch nhiều hơn khả năng hiện tại của công cụ.

### 15.6 Hạn chế và hướng phát triển (do tác giả nêu)

- **Chưa xử lý outlier và dữ liệu mất cân bằng**.
- Chưa nhận diện kiểu real-valued, interval, ordinal (có thể dùng mô hình Bayes trong tài liệu).
- Kỹ thuật impute/encoding được khuyến nghị dựa trên **bộ phân loại/hồi quy cơ bản** — chưa chắc tối ưu cho mô hình của người dùng → cho phép người dùng **chỉ định mô hình** để đánh giá.
- Trực quan hoá nên **tương tác** hơn; mở rộng sang bài toán khác như phân cụm (khi đó đánh giá impute bằng DBSCAN, k-means).

---

## 16. Data Preprocessing for Supervised Learning

| | |
|---|---|
| **Tác giả** | S. B. Kotsiantis, D. Kanellopoulos, P. E. Pintelas (University of Patras) |
| **Nguồn** | *International Journal of Computer Science* vol. 1 no. 1, 2006 (WASET) |
| **Loại bài** | Bài tổng quan (overview) các thuật toán tiền xử lý |
| **File** | `paper/Data_preprocessing_for_supervised_leanin.pdf` |

### 16.1 Tóm tắt

Thành công của ML phụ thuộc trước hết vào **biểu diễn và chất lượng dữ liệu**. Nhiều thông tin không liên quan, dư thừa, nhiễu hay không tin cậy khiến việc học khó hơn;
chuẩn bị và lọc dữ liệu chiếm nhiều thời gian xử lý. Tiền xử lý gồm **làm sạch, chuẩn hoá, biến đổi, trích và chọn đặc trưng**, sản phẩm là **tập huấn luyện cuối cùng**.
Vì **không có một chuỗi thuật toán tiền xử lý nào tốt nhất cho mọi dataset**, bài trình bày các thuật toán nổi tiếng nhất cho **từng bước** để người dùng chọn.

### 16.2 Cấu trúc nội dung — 6 bước tiền xử lý

```
 1. Chọn mẫu & phát hiện outlier ─► 2. Giá trị thiếu ─► 3. Rời rạc hoá ─► 4. Chuẩn hoá ─► 5. Chọn đặc trưng ─► 6. Xây dựng đặc trưng
    (instance selection)                                  (discretization)  (normalization)  (feature selection)  (feature construction)
```

### 16.3 Phương pháp — Bước 1: Chọn mẫu (instance selection) và phát hiện outlier

**Hai họ**: *filter* (chỉ xét giảm dữ liệu, không xét thuật toán học) và *wrapper* (dùng chính thuật toán ML để quyết định chọn mẫu).

**Làm sạch từng biến** (variable-by-variable — một cách filter): đánh dấu giá trị đáng ngờ theo quan hệ với một phân phối xác suất
(ví dụ phân phối chuẩn mean 5, độ lệch chuẩn 3, giá trị 10 là đáng ngờ). Metadata giúp phát hiện vấn đề (Table I):

| Vấn đề | Metadata | Ví dụ / heuristic |
|---|---|---|
| Giá trị không hợp lệ | **cardinality** | cardinality(gender) > 2 → có vấn đề |
| | **max, min** | max, min không được nằm ngoài miền cho phép |
| | **variance, deviation** | phương sai, độ lệch không được vượt ngưỡng |
| Lỗi chính tả | giá trị đặc trưng | **sắp xếp** giá trị thường đưa giá trị viết sai nằm cạnh giá trị đúng |

- **Inlier**: giá trị nằm *bên trong* phân phối nhưng sai → khó phân biệt với dữ liệu tốt.
- **Làm sạch đa biến**: khó hơn nhưng cần thiết — ví dụ phát hiện outlier dựa trên **khoảng cách** (RT) và dựa trên **mật độ** (**LOF**).
- **Loại trùng lặp** (duplicate instance identification).
- **Wrapper loại mẫu gán nhãn sai** (Brodley & Friedl): (1) dùng **m thuật toán học** gắn thẻ mỗi mẫu là đúng/sai nhãn; (2) huấn luyện bộ phân loại trên dữ liệu đã **bỏ mẫu bị coi là sai nhãn**;
  việc lọc có thể dựa trên thẻ của một hoặc nhiều trong m bộ phân loại cơ sở.

**Chọn mẫu để xử lý dữ liệu quá lớn** — bài toán tối ưu: giữ chất lượng khai phá trong khi tối thiểu kích thước mẫu:
- **Random sampling**: chọn ngẫu nhiên.
- **Stratified sampling**: khi lớp phân bố không đều, chọn mẫu lớp thiểu số với tần suất cao hơn để cân bằng.
- Đường cong học: khi dữ liệu tăng, độ chính xác tăng chậm dần; nghiên cứu cây quyết định trên 19 dataset thấy **đạt bình nguyên chỉ sau rất ít mẫu**.
- **Khung hợp nhất (Reinartz)**: lấy mẫu thống kê ban đầu → **phân cụm** thành nhóm mẫu tương tự → mỗi nhóm chọn/xây dựng một tập **prototype** đại diện nhỏ hơn → tập prototype là đầu ra.

**Dữ liệu mất cân bằng** — nguyên nhân thiên lệch: bộ học tối thiểu lỗi trên tập huấn luyện nên bỏ qua lớp ít mẫu; và **overfit** lớp ít mẫu. Giải pháp chọn mẫu:
- **Over-sampling**: nhân bản mẫu của lớp thiểu số.
- **Downsizing**: bỏ bớt mẫu của lớp đa số.

### 16.4 Bước 2: Giá trị đặc trưng bị thiếu

**Nguồn gốc của "không biết"** cần xét: (i) giá trị bị quên/mất; (ii) đặc trưng **không áp dụng** cho mẫu đó; (iii) người thiết kế tập huấn luyện **không quan tâm** giá trị đó (*don't-care*).

| Phương pháp | Cách làm |
|---|---|
| Bỏ mẫu có giá trị thiếu | Bỏ mọi mẫu có ít nhất một giá trị thiếu — đơn giản nhất |
| Most common feature value | Điền bằng giá trị xuất hiện nhiều nhất của đặc trưng |
| **Concept** most common feature value | Điền bằng giá trị phổ biến nhất **trong cùng lớp** |
| Mean substitution | Điền bằng trung bình; cách tốt hơn là trung bình **của các mẫu cùng lớp** |
| Hồi quy / phân loại | Xây mô hình trên các mẫu đầy đủ, coi đặc trưng thiếu là biến đầu ra, các đặc trưng liên quan khác là biến dự báo |
| Hot deck imputation | Tìm mẫu **tương tự nhất** và lấy giá trị của nó |
| Coi thiếu là giá trị đặc biệt | "unknown" trở thành **một giá trị mới** của đặc trưng |

### 16.5 Bước 3: Rời rạc hoá

Mục tiêu: **giảm mạnh số giá trị** của đặc trưng liên tục (nhiều giá trị làm học chậm và kém); nhiều thuật toán học ký hiệu/logic chỉ xử lý dữ liệu hạng mục.
Vấn đề mở: chọn **biên khoảng** và **số khoảng (arity)**.

**Quy trình rời rạc hoá tổng quát (Fig. 1)**:

```
 Thuộc tính liên tục ─► SẮP XẾP ─► Chọn điểm cắt ứng viên / cặp khoảng kề ─► ĐÁNH GIÁ bằng một thước đo ─► thoả mãn?
        ▲                                                                                                    │ có
        │                                                     ┌──────────────────────────────────────────────┘
        └──── chưa đạt tiêu chí dừng ◄── TÁCH (split) hoặc GỘP (merge) khoảng ◄──┘ ──► đạt tiêu chí dừng ─► Thuộc tính đã rời rạc hoá
```

| Phân loại | Phương pháp |
|---|---|
| **Không giám sát** (không xét nhãn) | **Equal size (width)**: chia [min, max] thành k khoảng bằng nhau · **Equal frequency**: mỗi khoảng chứa số mẫu bằng nhau |
| **Có giám sát** (xét nhãn) | **Khiops** — bottom-up, tối ưu toàn cục **chi-square** · **Error-based** (Maas) — tìm điểm cắt tối thiểu tổng FP + FN trên train · **Entropy** — top-down, chọn đệ quy điểm cắt **tối thiểu entropy**, dừng theo **Minimum Description Length** |
| Hướng tìm | **Top-down**: tách dần từ một khoảng · **Bottom-up**: gộp dần từ các khoảng một giá trị |
| Tĩnh vs động | **Tĩnh** (binning, entropy): số khoảng mỗi đặc trưng độc lập · **Động**: tìm k khoảng cho mọi đặc trưng cùng lúc (bắt được phụ thuộc) — so sánh bằng cross-validation **không thấy cải thiện đáng kể** so với tĩnh |

Kết luận của bài: các nghiên cứu so sánh thấy **phương pháp dựa trên entropy tốt nhất tổng thể**.

### 16.6 Bước 4: Chuẩn hoá dữ liệu

"Thu nhỏ" giá trị đặc trưng khi chênh lệch min–max lớn (ví dụ 0,01 và 1000); quan trọng với **mạng nơ-ron** và **k-NN**.

```
 Min-max:  v′ = (v − min_A) / (max_A − min_A) · (new_max_A − new_min_A) + new_min_A
 Z-score:  v′ = (v − mean_A) / stand_dev_A
```

### 16.7 Bước 5: Chọn đặc trưng (feature selection)

**Phân loại đặc trưng**:
- **Relevant**: ảnh hưởng tới output, vai trò không thể thay bằng đặc trưng khác.
- **Irrelevant**: không ảnh hưởng tới output, giá trị như sinh ngẫu nhiên.
- **Redundant**: một đặc trưng có thể đảm nhận vai trò của đặc trưng khác.
- Ngoài ra có **phụ thuộc lẫn nhau** (interdependence): hai hay nhiều đặc trưng chỉ mang thông tin quan trọng khi đi cùng nhau.

**Khung chọn đặc trưng (Fig. 2)**:

```
 Tập đặc trưng gốc ─► SINH tập con ─► ĐÁNH GIÁ (độ "tốt" của tập con) ─► tiêu chí dừng? ── chưa ──► quay lại SINH
                                                                              └── rồi ──► KIỂM CHỨNG tập con đã chọn
 Tiêu chí dừng: (i) thêm/bớt đặc trưng không cho tập con tốt hơn; (ii) đạt tập con tối ưu theo hàm đánh giá
 Tìm kiếm toàn bộ có 2ᴺ tập con → quá tốn; heuristic / ngẫu nhiên giảm chi phí nhưng chấp nhận giảm chất lượng
```

**Filter** (độc lập thuật toán học) — 4 loại hàm đánh giá:

| Loại | Ưu tiên X hơn Y nếu |
|---|---|
| **Distance** | X tạo chênh lệch lớn hơn giữa hai xác suất có điều kiện theo lớp (bài toán 2 lớp) |
| **Information** | Information gain của X lớn hơn |
| **Dependence** | Tương quan của X với lớp C lớn hơn |
| **Consistency** | Ít mâu thuẫn hơn (hai mẫu mâu thuẫn nếu cùng giá trị trên tập đặc trưng nhưng khác lớp) |

Thuật toán filter tiêu biểu:
- **Relief**: lấy mẫu ngẫu nhiên; với mỗi mẫu tìm **Near Hit** (gần nhất cùng lớp) và **Near Miss** (gần nhất khác lớp) theo khoảng cách Euclid; trọng số đặc trưng (khởi tạo 0)
  **tăng** nếu đặc trưng phân biệt mẫu với Near Miss, **giảm** nếu phân biệt với Near Hit; chọn mọi đặc trưng có trọng số ≥ ngưỡng.
- **Dùng thuật toán học làm bộ tiền xử lý**: chạy C4.5, chọn đặc trưng xuất hiện trong cây đã tỉa (cho bộ học dựa trên mẫu); cây quyết định "oblivious" chọn đặc trưng cho mạng Bayes;
  **BDSFS** — boosted decision stumps chạy k vòng, mỗi vòng bỏ qua đặc trưng đã chọn, đặc trưng được chọn ở vòng nào thì vào tập kết quả.
- **NNFS**: chọn đặc trưng bằng mạng nơ-ron như tỉa kiến trúc — loại trọng số lớp vào; trọng số nối với đặc trưng quan trọng có giá trị tuyệt đối lớn, đặc trưng không quan trọng ≈ 0.
  Một số cách so độ nổi bật (saliency) của đặc trưng ứng viên với một **đặc trưng nhiễu**.
- **LVF** (theo tính nhất quán, chịu được nhiễu nếu biết trước mức nhiễu): mỗi vòng sinh ngẫu nhiên tập con S; nếu S ít đặc trưng hơn tập tốt nhất và **nhất quán ít nhất bằng** thì thay thế.
  **LVS**: biến thể giảm số lần kiểm tra cho dataset lớn.
- **Hall**: tập con tốt là tập gồm đặc trưng **tương quan cao với lớp nhưng ít tương quan với nhau**.
- **Predominant correlation** (Yu & Liu): filter nhanh xác định đặc trưng liên quan và dư thừa mà **không cần phân tích tương quan từng cặp**.

**Wrapper** (dùng thuật toán học làm hàm đánh giá, ước lượng bằng cross-validation):
- **Forward stepwise**: lần lượt thêm biến cải thiện mô hình nhất — nhanh tìm tập nhỏ hiệu quả nhưng **có thể bỏ sót biến phụ thuộc lẫn nhau**.
- **Backward stepwise**: bắt đầu với mọi biến, mỗi vòng bỏ biến mà việc bỏ cải thiện nhiều nhất (hoặc giảm ít nhất) — xử lý tốt phụ thuộc lẫn nhau nhưng các lần đánh giá đầu tốn kém.
- Naïve Bayes (giả định độc lập có điều kiện) được lợi khi bỏ đặc trưng dư thừa → hay dùng **forward**; cây quyết định và bộ học dựa trên mẫu hay dùng **backward**.
- **SFFS / SBFS** (sequential floating): số đặc trưng thêm/bớt thay đổi ở từng giai đoạn; **adaptive floating search** tốt hơn nhưng tốn thời gian hơn nhiều.
- **Thuật toán di truyền**: khai thác **epistasis** (phụ thuộc giữa các bit) nên hợp với bài toán này, nhưng cần rất nhiều lần đánh giá.
- **Hybrid** (cho dữ liệu nhiều chiều): dùng thước đo theo đặc điểm dữ liệu chọn tập con tốt nhất cho mỗi kích thước, rồi cross-validation chọn tập cuối cùng giữa các kích thước.

Nhận xét của bài: tập con tối ưu **luôn tương đối với một hàm đánh giá**; so sánh nhiều kỹ thuật **không tìm ra người thắng thật sự**; wrapper thường cho kết quả tốt hơn filter
(vì khớp với tương tác giữa thuật toán học và dữ liệu) nhưng **chậm hơn nhiều**.

### 16.8 Bước 6: Xây dựng đặc trưng (feature construction / transformation)

Giải quyết **tương tác giữa đặc trưng** bằng cách tạo đặc trưng mới → bộ phân loại gọn và chính xác hơn, dễ hiểu hơn.

| Dạng | Định nghĩa | Ví dụ thuật toán |
|---|---|---|
| **Mở rộng không gian** (construction) | Từ a₁..aₙ thêm aₙ₊₁..aₙ₊ₘ, ví dụ phép **logic** giữa aᵢ và aⱼ | **GALA**: tạo đặc trưng nhị phân mới tại mỗi nút cây bằng branch-and-bound, kết hợp đặc trưng có InfoGain cao nhất với đặc trưng gốc qua AND, OR, NOT · **at-least M-of-N** (Zheng): đúng nếu ít nhất M trong N điều kiện đúng |
| **Trích xuất** (extraction) | b₁..bₘ (m < n), bᵢ = fᵢ(a₁..aₙ), ví dụ b₁(x) = c₁·a₁(x) + c₂·a₂(x) | **FICUS**: sinh đặc trưng theo **ngữ pháp tổng quát** với tập hàm xây dựng do người dùng đặc tả |

**Chọn đặc trưng hay xây dựng đặc trưng?** Tuỳ miền ứng dụng và dữ liệu:

| | Feature selection | Feature construction |
|---|---|---|
| Chi phí đo | **Giảm** (bỏ bớt đặc trưng) | — |
| Ý nghĩa vật lý | **Giữ nguyên** — giúp hiểu quá trình sinh dữ liệu | Có thể **không có ý nghĩa vật lý rõ ràng** |
| Khả năng phân biệt | Giới hạn trong tập đặc trưng có sẵn | Có thể **tốt hơn** tập con tốt nhất của đặc trưng gốc |

### 16.9 Kết luận của bài

Thành công của thuật toán học phụ thuộc chất lượng dữ liệu; mọi thuật toán học quy nạp phụ thuộc mạnh vào **tập huấn luyện cuối cùng** do bước tiền xử lý tạo ra.
Chọn mẫu giúp bỏ nhiễu/dư thừa và cho phép chạy ML trên dữ liệu quá lớn; giá trị thiếu nên được tiền xử lý; rời rạc hoá dựa trên **entropy** tốt nhất tổng thể;
wrapper tốt hơn nhưng chậm hơn filter; xây dựng đặc trưng có thể phân biệt tốt hơn nhưng khó diễn giải. **Không có chuỗi tiền xử lý duy nhất tốt nhất cho mọi dataset.**


# Tài liệu tham khảo khoa học — Module **Data Processing**

> **Mục đích**: nguồn trích dẫn cho phần thiết kế & hiện thực khối *Data Processing*
> (validate --> clean --> feature engineering) của MLOps framework, nối tiếp khối Data Collection đã có.
> **Ngày tra cứu**: 2026-10-05. **Công cụ**: Semantic Scholar Graph API (số trích dẫn, metadata),
> Unpaywall API (xác minh open access), Google Scholar / web search (tìm ứng viên).
> **Số trích dẫn** trong bảng lấy từ Semantic Scholar ngày tra cứu — dùng để xếp ưu tiên, không phải con số cố định.

## Tiêu chí lọc đã áp dụng

| Tiêu chí | Cách áp dụng |
|---|---|
| Công bố trong 5 năm | 2021–2026 (tính theo năm công bố chính thức; bản arXiv có thể sớm hơn vài tháng) |
| Đọc được toàn văn, không cần tài khoản | Mọi link đã kiểm tra bằng HTTP request và/hoặc Unpaywall. Bài nào bản nhà xuất bản đóng thì dùng bản arXiv/kỷ yếu mở và **ghi rõ** |
| Uy tín / ảnh hưởng | Ưu tiên venue mạnh (VLDB, SIGMOD, EDBT, ICLR, NeurIPS, ACM CSUR, JSS, IEEE Access) và số trích dẫn cao |
| Một bài — một khía cạnh | Mỗi mục bên dưới ghi rõ **khía cạnh** bài đó phụ trách; tránh survey "rộng nhưng nông" trùng lặp nhau |

**Chú thích mức độ mở**: `OA gold` = nhà xuất bản mở hoàn toàn; `OA bronze/hybrid` = bài miễn phí trên trang nhà
xuất bản nhưng tạp chí không mở hoàn toàn; `arXiv` = dùng bản preprint/author version vì bản chính thức bị khoá.

---

## 1. Bảng tổng hợp 20 bài chọn chính

| # | Khía cạnh | Bài báo (rút gọn) | Năm | Venue | Cit. | Truy cập |
|---|---|---|---|---|---|---|
| 1 | Khái niệm & kiến trúc MLOps | Kreuzberger et al. — *MLOps: Overview, Definition, and Architecture* | 2023 | IEEE Access | 716 | OA gold |
| 2 | Quy trình + đảm bảo chất lượng theo pha | Studer et al. — *Towards CRISP-ML(Q)* | 2021 | MAKE (MDPI) | 278 | OA gold |
| 3 | Khung data-centric AI | Zha et al. — *Data-centric AI: A Survey* | 2023 | ACM CSUR | 531 | arXiv |
| 4 | Thách thức thu thập + chất lượng dữ liệu | Whang et al. — *Data collection and quality challenges in deep learning* | 2023 | VLDB Journal | 598 | arXiv (bản NXB đóng) |
| 5 | Yêu cầu chất lượng dữ liệu theo từng giai đoạn pipeline | Priestley et al. — *A Survey of Data Quality Requirements That Matter in ML Development Pipelines* | 2023 | ACM JDIQ | 82 | OA bronze |
| 6 | Chiều đo chất lượng + công cụ đánh giá | Zhou et al. — *A Survey on Data Quality Dimensions and Tools for ML* | 2024 | IEEE AITest | 36 | arXiv (CC BY) |
| 7 | Tiêu chuẩn ISO/IEC 25012 ↔ công cụ mã nguồn mở | Papastergios & Gounaris — *A survey of open-source data quality tools* | 2024 | arXiv | 8 | arXiv |
| 8 | Thực nghiệm: lỗi chất lượng ⇒ sụt hiệu năng (dữ liệu bảng) | Mohammed, Budach et al. — *The effects of data quality on ML performance on tabular data* | 2022/2025 | Information Systems | 197 | arXiv + OA hybrid |
| 9 | Thực nghiệm: lỗi dữ liệu lúc **serving** | Schelter et al. — *JENGA* | 2021 | EDBT | 57 | OA (OpenProceedings) |
| 10 | Tự sinh ràng buộc validation | Song & He — *Auto-Validate* | 2021 | SIGMOD | 25 | arXiv |
| 11 | Debug phân phối dữ liệu xuyên pipeline | Grafberger et al. — *mlinspect* | 2021 | SIGMOD | 43 | OA gold |
| 12 | Nguyên nhân gốc lỗi dữ liệu trong pipeline | Foidl et al. — *Data pipeline quality* | 2024 | JSS | 52 | OA (CC BY) |
| 13 | Observability cho pipeline ML production | Shankar & Parameswaran — *Towards Observability for Production ML Pipelines* | 2022 | PVLDB | 33 | arXiv |
| 14 | Tổng quan phương pháp data cleaning cho ML | Côté et al. — *Data cleaning and ML: a systematic literature review* | 2024 | Automated Softw. Eng. | 109 | arXiv (bản NXB đóng) |
| 15 | Catalogue "data smell" | Shome, Cruz & van Deursen — *Data Smells in Public Datasets* | 2022 | CAIN | 26 | OA gold |
| 16 | Imputation: khi nào đáng làm phức tạp | Le Morvan & Varoquaux — *Imputation for prediction: beware of diminishing returns* | 2025 | ICLR | 21 | arXiv |
| 17 | Tự động chọn pipeline tiền xử lý (dữ liệu bảng) | Li, Chen & Chu — *DiffPrep* | 2023 | SIGMOD / PACMMOD | 39 | OA bronze |
| 18 | Tiền xử lý ảnh hưởng xếp hạng mô hình | Tschalzev et al. — *A Data-Centric Perspective on Evaluating ML Models for Tabular Data* | 2024 | NeurIPS D&B | 27 | arXiv |
| 19 | Rò rỉ dữ liệu (gồm rò rỉ theo thời gian) | Kapoor & Narayanan — *Leakage and the reproducibility crisis* | 2023 | Patterns | 1186 | OA gold |
| 20 | Mở rộng AIOps: tiền xử lý log/metric | Zhang et al. — *A Survey of AIOps for Failure Management in the Era of LLMs* | 2024 | arXiv | 41 | arXiv |

---

## 2. Nhóm A — Khái niệm, quy trình, kiến trúc

### [1] Machine Learning Operations (MLOps): Overview, Definition, and Architecture
- **Tác giả / nguồn**: D. Kreuzberger, N. Kühl, S. Hirschl. *IEEE Access*, vol. 11, 2023. DOI `10.1109/ACCESS.2023.3262138`.
- **Truy cập**: OA gold — <https://ieeexplore.ieee.org/document/10081336> · bản arXiv: <https://arxiv.org/abs/2205.02302>
- **Trích dẫn**: 716 · **Khía cạnh**: *định nghĩa + kiến trúc tổng thể*.
- **Nội dung**: tổng hợp từ literature review + phỏng vấn chuyên gia + khảo sát công cụ, rút ra 9 nguyên lý MLOps
  (CI/CD, orchestration, versioning, reproducibility, ...), các vai trò, và một kiến trúc end-to-end
  trong đó *feature engineering pipeline* và *data versioning* là thành phần hạng nhất.
- **Dùng cho**: trích dẫn định nghĩa MLOps và vị trí của khối Data Processing trong vòng đời; đối chiếu kiến trúc ở §2 của `CLAUDE.md`.

### [2] Towards CRISP-ML(Q): A Machine Learning Process Model with Quality Assurance Methodology
- **Tác giả / nguồn**: S. Studer, T. B. Bui, C. Drescher, A. Hanuschkin, L. Winkler, S. Peters, K.-R. Müller.
  *Machine Learning and Knowledge Extraction* 3(2), 392–413, 2021. DOI `10.3390/make3020020`.
- **Truy cập**: OA gold (MDPI) — <https://www.mdpi.com/2504-4990/3/2/20> · bản arXiv: <https://arxiv.org/abs/2003.05155>
- **Trích dẫn**: 278 · **Khía cạnh**: *quy trình chuẩn + đảm bảo chất lượng theo từng tác vụ*.
- **Nội dung**: mở rộng CRISP-DM thành 6 pha cho ML; với **mỗi tác vụ** nêu rủi ro và biện pháp QA tương ứng.
  Pha *Data Preparation* có checklist: lựa chọn feature, xử lý thiếu/nhiễu, chuẩn hoá, cân bằng lớp, và yêu cầu
  **mọi bước phải lặp lại được trên dữ liệu mới**.
- **Dùng cho**: khung lập luận "tại sao mỗi bước xử lý cần một tiêu chí chấp nhận" — nền cho Dataset Contract ở §8 `CLAUDE.md`.

### [3] Data-centric Artificial Intelligence: A Survey
- **Tác giả / nguồn**: D. Zha, Z. P. Bhat, K.-H. Lai, F. Yang, Z. Jiang, S. Zhong, X. Hu. *ACM Computing Surveys*, 2023/2025.
- **Truy cập**: <https://arxiv.org/abs/2303.10158>
- **Trích dẫn**: 531 · **Khía cạnh**: *khung khái niệm data-centric*.
- **Nội dung**: chia công việc về dữ liệu thành 3 mục tiêu — *training data development* (thu thập, gán nhãn,
  chuẩn bị, giảm chiều, tăng cường), *inference data development*, *data maintenance* (hiểu dữ liệu, bảo đảm
  chất lượng, tăng tốc) — kèm trục "tự động hoá" và "con người tham gia", và bảng benchmark.
- **Dùng cho**: đặt tên và ranh giới cho các khối con của module; biện minh việc tách *data maintenance*
  (monitoring/drift) khỏi *training data development*.

### [4] Data collection and quality challenges in deep learning: a data-centric AI perspective
- **Tác giả / nguồn**: S. E. Whang, Y. Roh, H. Song, J.-G. Lee. *The VLDB Journal* 32, 2023.
- **Truy cập**: bản nhà xuất bản **đóng**; dùng bản arXiv toàn văn: <https://arxiv.org/abs/2112.06409>
- **Trích dẫn**: 598 · **Khía cạnh**: *tổng quan thách thức dữ liệu* (thu thập, gán nhãn, cải thiện, validation).
- **Nội dung**: phân loại kỹ thuật thu thập (discovery, augmentation, generation), gán nhãn (semi/weak supervision),
  cải thiện dữ liệu hiện có, và **data validation** như một bước bắt buộc trước huấn luyện; nhấn mạnh tương tác
  giữa chất lượng dữ liệu và độ tin cậy mô hình.
- **Dùng cho**: phần "bối cảnh & động cơ" của chương Data Processing; liên hệ ngược với khối Data Collection đã làm.

---

## 3. Nhóm B — Chất lượng dữ liệu: chiều đo, yêu cầu, tiêu chuẩn, công cụ

### [5] A Survey of Data Quality Requirements That Matter in ML Development Pipelines
- **Tác giả / nguồn**: M. Priestley, F. O'Donnell, E. Simperl. *ACM Journal of Data and Information Quality* 15(2), 2023.
  DOI `10.1145/3592616`.
- **Truy cập**: OA bronze — PDF miễn phí: <https://dl.acm.org/doi/10.1145/3592616>
- **Trích dẫn**: 82 · **Khía cạnh**: *yêu cầu chất lượng dữ liệu gắn với từng giai đoạn pipeline*.
- **Nội dung**: thay vì liệt kê chiều đo chung chung, bài dùng quan điểm **fitness-for-use** và ánh xạ yêu cầu DQ
  theo nơi dữ liệu xuất hiện trong vòng đời ML (thu thập, chuẩn bị, huấn luyện, triển khai) — chỉ ra rằng cùng một
  chiều đo mang ý nghĩa khác nhau ở các giai đoạn khác nhau.
- **Dùng cho**: thiết kế **nhiều tầng validate** (raw / processed / features) của framework — chứng minh vì sao
  mỗi tầng cần bộ expectation riêng chứ không dùng chung một suite.

### [6] A Survey on Data Quality Dimensions and Tools for Machine Learning
- **Tác giả / nguồn**: Y. Zhou, F. Tu, K. Sha, J. Ding, H. Chen. *IEEE AITest 2024* (invited paper).
- **Truy cập**: arXiv CC BY — <https://arxiv.org/abs/2406.19614>
- **Trích dẫn**: 36 · **Khía cạnh**: *chiều đo chất lượng + khảo sát công cụ*.
- **Nội dung**: khung 5 nhóm (bản thân dữ liệu, nguồn dữ liệu, hệ thống truy cập, tác vụ, con người) với 29 chiều đo;
  rà soát 17 công cụ đánh giá và cải thiện chất lượng dữ liệu trong 5 năm, so sánh phạm vi và hạn chế.
- **Dùng cho**: chọn tập chiều đo sẽ hiện thực trong Dataset Contract (completeness, consistency, timeliness, validity...).

### [7] A survey of open-source data quality tools: shedding light on the materialization of data quality dimensions in practice
- **Tác giả / nguồn**: V. Papastergios, A. Gounaris. arXiv:2407.18649, 2024.
- **Truy cập**: <https://arxiv.org/abs/2407.18649>
- **Trích dẫn**: 8 · **Khía cạnh**: *tiêu chuẩn ISO/IEC 25012 ↔ công cụ thực tế*.
- **Nội dung**: so sánh 6 công cụ mã nguồn mở — **Great Expectations**, Deequ, dbt Core, Soda Core, Apache Griffin,
  MobyDQ — theo 15 chiều của mô hình chất lượng dữ liệu **ISO/IEC 25012**; chỉ rõ chiều nào được công cụ nào
  hiện thực hoá và chiều nào không công cụ nào phủ.
- **Dùng cho**: **bài sát nhất về mặt công cụ** cho framework này, vì tech stack đang dùng Great Expectations 1.18.1.
  Dùng để biện minh lựa chọn công cụ và chỉ ra khoảng trống phải tự bù bằng code.
- **Ghi chú tiêu chuẩn**: bộ **ISO/IEC 5259-1..5 (2024–2025)** — *Data quality for analytics and machine learning* —
  là tiêu chuẩn sát nhất với module này nhưng **có phí**, không đáp ứng yêu cầu "đọc toàn văn miễn phí".
  Bài [7] và [5] là đường dẫn học thuật mở gần nhất tới nội dung tiêu chuẩn đó (ISO/IEC 5259 kế thừa ISO/IEC 25012).

### [8] The effects of data quality on machine learning performance on tabular data
- **Tác giả / nguồn**: S. Mohammed, L. Budach, M. Feuerpfeil, N. Ihde, A. Nathansen, N. Noack, H. Patzlaff,
  F. Naumann, H. Harmouch. *Information Systems*, 2025 (bản preprint 2022).
- **Truy cập**: <https://arxiv.org/abs/2207.14529> · bản tạp chí OA hybrid: DOI `10.1016/j.is.2025.102549`
- **Trích dẫn**: 197 · **Khía cạnh**: *thực nghiệm định lượng — lỗi chất lượng ⇒ sụt hiệu năng*.
- **Nội dung**: "gây ô nhiễm" có kiểm soát trên nhiều chiều chất lượng (completeness, accuracy, consistency,
  feature/target accuracy, uniqueness, class balance) với mức độ tăng dần, đo tác động lên nhiều thuật toán
  trên **dữ liệu dạng bảng** cho cả classification và regression.
- **Dùng cho**: **căn cứ số** để đặt ngưỡng cảnh báo / ngưỡng chặn trong expectation suite, thay vì chọn ngưỡng cảm tính.
  Rất khớp vì framework cũng chạy cả classification và regression trên dữ liệu bảng.

---

## 4. Nhóm C — Validation, kiểm thử và quan sát pipeline dữ liệu

### [9] JENGA — A Framework to Study the Impact of Data Errors on the Predictions of Machine Learning Models
- **Tác giả / nguồn**: S. Schelter, T. Rukat, F. Biessmann. *EDBT 2021*.
- **Truy cập**: OA — <https://openproceedings.org/2021/conf/edbt/p134.pdf>
- **Trích dẫn**: 57 · **Khía cạnh**: *kiểm thử độ bền của mô hình trước lỗi dữ liệu lúc **serving***.
- **Nội dung**: thư viện mô phỏng các lỗi dữ liệu thực tế (giá trị thiếu, nhiễu đo, lệch phân phối, lỗi mã hoá)
  trên dữ liệu suy luận và đo mức sụt hiệu năng; phân biệt rõ lỗi lúc *train* và lỗi lúc *serve*.
- **Dùng cho**: thiết kế bộ test cho module; và biện minh cơ chế **fail-soft** (tách dòng xấu, pipeline vẫn chạy)
  nêu ở §3.1 `CLAUDE.md` — cần biết lỗi nào mô hình chịu được, lỗi nào phải chặn.

### [10] Auto-Validate: Unsupervised Data Validation Using Data-Domain Patterns Inferred from Data Lakes
- **Tác giả / nguồn**: J. Song, Y. He. *SIGMOD 2021*.
- **Truy cập**: <https://arxiv.org/abs/2104.04659>
- **Trích dẫn**: 25 · **Khía cạnh**: *tự sinh ràng buộc validation thay vì viết tay*.
- **Nội dung**: suy luận "data-domain pattern" của từng cột từ dữ liệu lịch sử, tự sinh ràng buộc kiểm tra
  với đảm bảo tỉ lệ false-positive; so sánh với luật viết tay.
- **Dùng cho**: hướng tự động hoá cho Dataset Contract — sinh expectation ban đầu từ dữ liệu `observations/`
  đã thu thập, giảm công khai báo khi thêm bài toán mới.

### [11] mlinspect: A Data Distribution Debugger for Machine Learning Pipelines
- **Tác giả / nguồn**: S. Grafberger, S. Guha, J. Stoyanovich, S. Schelter. *SIGMOD 2021*. DOI `10.1145/3448016.3452759`.
- **Truy cập**: OA gold — <https://dl.acm.org/doi/10.1145/3448016.3452759> ·
  bản lưu trữ: <https://pure.uva.nl/ws/files/134258464/Data_distribution_debugging_in_machine_learning_pipelines.pdf>
- **Trích dẫn**: 43 · **Khía cạnh**: *phát hiện "data distribution bug" xuyên suốt pipeline*.
- **Nội dung**: trích xuất pipeline pandas/scikit-learn thành **logical query plan**, gắn annotation để theo dõi
  phân phối dữ liệu đi qua từng toán tử — phát hiện lỗi kiểu "bước join/filter làm mất một nhóm dữ liệu"
  mà **không cần sửa code pipeline**.
- **Dùng cho**: mô hình tham chiếu cho "operator tổng quát" ở §8 `CLAUDE.md` — kiểm tra theo *cấu trúc pipeline*
  chứ không theo tên cột; đúng tinh thần framework không viết cứng tên cột.

### [12] Data pipeline quality: Influencing factors, root causes of data-related issues, and processing problem areas for developers
- **Tác giả / nguồn**: H. Foidl, V. Golendukhina, R. Ramler, M. Felderer. *Journal of Systems and Software* 207, 111855, 2024.
- **Truy cập**: OA (CC BY) — <https://doi.org/10.1016/j.jss.2023.111855>
- **Trích dẫn**: 52 · **Khía cạnh**: *nguyên nhân gốc của lỗi dữ liệu, từ góc nhìn kỹ sư*.
- **Nội dung**: nghiên cứu thực nghiệm (phân tích tài liệu + khảo sát) rút ra danh mục **yếu tố ảnh hưởng**
  (con người, kỹ thuật, tổ chức), **nguyên nhân gốc** của sự cố dữ liệu và các **vùng vấn đề** khi xử lý dữ liệu.
- **Dùng cho**: checklist rủi ro khi thiết kế module; đối chiếu với các hạn chế của kiến trúc kế thừa ở §9 `CLAUDE.md`.

### [13] Towards Observability for Production Machine Learning Pipelines
- **Tác giả / nguồn**: S. Shankar, A. G. Parameswaran. *PVLDB* 15(13), 2022.
- **Truy cập**: <https://arxiv.org/abs/2108.13557>
- **Trích dẫn**: 33 · **Khía cạnh**: *observability — ghi vết dữ liệu để chẩn đoán sau sự cố*.
- **Nội dung**: lập luận rằng monitoring kiểu "ngưỡng + cảnh báo" là chưa đủ; cần ghi lại dữ liệu và metadata đủ để
  **truy ngược** nguyên nhân khi chất lượng dự đoán tụt, và nêu các thách thức kỹ thuật (lấy mẫu, chi phí lưu trữ, join log).
- **Dùng cho**: thiết kế lớp `_manifests/` + log cho module xử lý, mở rộng mẫu đã dùng trong Data Collection.

---

## 5. Nhóm D — Làm sạch dữ liệu & xử lý giá trị thiếu

### [14] Data cleaning and machine learning: a systematic literature review
- **Tác giả / nguồn**: P.-O. Côté, A. Nikanjam, N. Ahmed, D. Humeniuk, F. Khomh. *Automated Software Engineering* 31, 2024.
- **Truy cập**: bản Springer **đóng**; dùng bản arXiv toàn văn: <https://arxiv.org/abs/2310.01765>
- **Trích dẫn**: 109 · **Khía cạnh**: *tổng quan có hệ thống về phương pháp cleaning cho ML*.
- **Nội dung**: SLR trên hơn 100 bài, phân loại theo hai chiều — *cleaning for ML* (làm sạch để mô hình tốt hơn) và
  *ML for cleaning* (dùng mô hình để làm sạch); tổng hợp kỹ thuật cho outlier, duplicate, inconsistency, missing value,
  mislabel, và chỉ ra khoảng trống nghiên cứu.
- **Dùng cho**: bản đồ phương pháp để chọn cleaning operator theo `semantic_type` của từng cột.

### [15] Data Smells in Public Datasets
- **Tác giả / nguồn**: A. Shome, L. Cruz, A. van Deursen. *CAIN 2022* (IEEE/ACM Int. Conf. on AI Engineering). DOI `10.1145/3522664.3528621`.
- **Truy cập**: OA gold — <https://dl.acm.org/doi/10.1145/3522664.3528621> · bản arXiv: <https://arxiv.org/abs/2203.08007>
- **Trích dẫn**: 26 · **Khía cạnh**: *catalogue dấu hiệu dữ liệu có vấn đề (data smell)*.
- **Nội dung**: định nghĩa "data smell" tương tự code smell, đề xuất catalogue phân theo *believability*,
  *understandability*, *consistency*, và khảo sát mức phổ biến trên các bộ dữ liệu công khai.
- **Dùng cho**: nguồn luật kiểm tra cụ thể, có thể dịch thẳng thành expectation trong Great Expectations.

### [16] Imputation for prediction: beware of diminishing returns
- **Tác giả / nguồn**: M. Le Morvan, G. Varoquaux. *ICLR 2025* (bản preprint 2024).
- **Truy cập**: <https://arxiv.org/abs/2407.19804>
- **Trích dẫn**: 21 · **Khía cạnh**: *đánh giá thực nghiệm giá trị thực của imputation*.
- **Nội dung**: thực nghiệm quy mô lớn cho thấy với bài toán **dự báo** (khác với bài toán ước lượng tham số),
  imputation phức tạp thường **không** cải thiện đáng kể so với phương pháp đơn giản, nhất là khi mô hình học được
  cơ chế thiếu dữ liệu; chi phí tính toán tăng nhưng lợi ích giảm dần.
- **Dùng cho**: quyết định "không làm quá tay" ở bước xử lý thiếu dữ liệu — sát với thực tế dữ liệu OpenAQ
  có cột null toàn phần (`temperature` / `relativehumidity`) và coverage không đều giữa các trạm.

---

## 6. Nhóm E — Feature engineering & tiền xử lý cho dữ liệu bảng

### [17] DiffPrep: Differentiable Data Preprocessing Pipeline Search for Learning over Tabular Data
- **Tác giả / nguồn**: P. Li, Z. Chen, X. Chu, K. Rong. *Proc. ACM Manag. Data (SIGMOD)* 1(2), 2023. DOI `10.1145/3589328`.
- **Truy cập**: OA bronze — <https://dl.acm.org/doi/10.1145/3589328> · bản arXiv: <https://arxiv.org/abs/2308.10915>
- **Trích dẫn**: 39 · **Khía cạnh**: *tự động chọn chuỗi tiền xử lý, khả vi, theo từng cột*.
- **Nội dung**: coi việc chọn pipeline tiền xử lý (imputation, outlier, chuẩn hoá, mã hoá...) là bài toán tối ưu
  khả vi, tối ưu **đồng thời** với tham số mô hình; cho phép mỗi cột có pipeline riêng.
- **Dùng cho**: cơ sở học thuật cho ý tưởng "operator chọn theo `semantic_type`" và cho hướng mở rộng tự động hoá
  cấu hình tiền xử lý thay vì khai báo tay trong YAML.

### [18] A Data-Centric Perspective on Evaluating Machine Learning Models for Tabular Data
- **Tác giả / nguồn**: A. Tschalzev, S. Marton, S. Lüdtke, C. Bartelt, H. Stuckenschmidt. *NeurIPS 2024 Datasets & Benchmarks*.
- **Truy cập**: <https://arxiv.org/abs/2407.02112>
- **Trích dẫn**: 27 · **Khía cạnh**: *tiền xử lý quyết định kết quả so sánh mô hình*.
- **Nội dung**: chứng minh bằng thực nghiệm rằng **thứ hạng mô hình thay đổi đáng kể** theo pipeline tiền xử lý;
  khoảng cách giữa các mô hình thu hẹp khi dùng tiền xử lý do chuyên gia thiết kế; mọi mô hình đều hưởng lợi từ
  feature engineering. Đề xuất quy trình đánh giá data-centric.
- **Dùng cho**: lập luận bắt buộc **cố định và version hoá pipeline tiền xử lý** trước khi so sánh model /
  chạy promotion gate — chống đúng lỗi "rò rỉ thống kê" và "danh sách feature bị lặp" ở §9 `CLAUDE.md`.

### [19] Leakage and the reproducibility crisis in machine-learning-based science
- **Tác giả / nguồn**: S. Kapoor, A. Narayanan. *Patterns* 4(9), 100804, 2023. DOI `10.1016/j.patter.2023.100804`.
- **Truy cập**: OA gold — <https://doi.org/10.1016/j.patter.2023.100804> · bản arXiv: <https://arxiv.org/abs/2207.07048>
- **Trích dẫn**: 1186 · **Khía cạnh**: *phân loại rò rỉ dữ liệu, gồm rò rỉ theo thời gian*.
- **Nội dung**: khảo sát 294 bài ở 17 lĩnh vực, phát hiện rò rỉ dữ liệu lan rộng; đưa ra **taxonomy 8 kiểu rò rỉ**
  (thiếu tách train/test, tiền xử lý trên toàn bộ dữ liệu, feature chứa thông tin tương lai, temporal leakage,
  lựa chọn feature trên tập test...) và mẫu "model info sheet" để tự kiểm.
- **Dùng cho**: **trực tiếp liên quan tới thiết kế nhãn của framework** — nhãn tính trên cửa sổ `(t, t+H]`, quy ước
  `event_time` chỉ chứa thông tin đã biết tại `t`, time-based split, và nguyên tắc transformer *fit-once / apply-many*
  (fit scaler trên tập train, không fit lại theo từng batch).

---

## 7. Nhóm F — Mở rộng: data processing trong AIOps

### [20] A Survey of AIOps for Failure Management in the Era of Large Language Models
- **Tác giả / nguồn**: L. Zhang, T. Jia, M. Jia, Y. Wu, A. Liu, Y. Yang, Z. Wu, X. Hu, P. S. Yu, Y. Li. arXiv:2406.11213, 2024.
- **Truy cập**: <https://arxiv.org/abs/2406.11213>
- **Trích dẫn**: 41 · **Khía cạnh**: *tiền xử lý dữ liệu vận hành (log, metric, trace)*.
- **Nội dung**: chia vòng đời AIOps thành **data preprocessing** --> failure perception --> root cause analysis -->
  auto remediation. Phần data preprocessing tổng hợp **log parsing** (tách template khỏi tham số),
  **metric imputation**, và tóm tắt đầu vào — tức lớp tương đương "flatten + clean" cho dữ liệu vận hành.
- **Dùng cho**: đối chiếu cách AIOps chuẩn hoá dữ liệu bán cấu trúc (log) với cách framework flatten JSON thành bảng;
  và cho phần monitoring/drift sau này.

---

## 8. Bản đồ: bài báo ↔ quyết định thiết kế của framework

| Quyết định thiết kế trong framework | Bài tham chiếu |
|---|---|
| Vị trí của Data Processing trong vòng đời MLOps | [1], [2], [3] |
| Dataset Contract (YAML khai báo cột + ràng buộc) | [5], [6], [10] |
| Chọn Great Expectations; biết công cụ phủ được chiều nào | [7] |
| Đặt ngưỡng cho expectation (bao nhiêu là "đủ xấu" để chặn) | [8], [9] |
| Validate nhiều tầng raw / processed / features | [5], [11] |
| Cơ chế fail-soft (tách dòng xấu, pipeline tiếp tục) | [9], [12] |
| Operator chọn theo `semantic_type`, không theo tên cột | [11], [14], [17] |
| Luật cleaning cụ thể cho từng kiểu lỗi | [14], [15] |
| Xử lý giá trị thiếu (cột null toàn phần, coverage thấp) | [16] |
| Transformer artifact fit-once / apply-many (chống rò rỉ thống kê) | [18], [19] |
| Feature engineering theo event time, chỉ dùng dữ liệu `≤ t` | [19] |
| Observability & manifest cho mỗi lần chạy | [12], [13] |
| Mở rộng sang dữ liệu vận hành / monitoring | [20] |

---

## 9. Danh sách dự phòng (dùng khi cần thêm chiều sâu)

| Bài | Năm | Venue | Cit. | Vì sao có thể cần | Truy cập |
|---|---|---|---|---|---|
| Qi et al. — *Auto-FP: An Experimental Study of Automated Feature Preprocessing for Tabular Data* | 2024 | EDBT | 8 | So sánh 15 thuật toán tìm chuỗi tiền xử lý; bổ sung thực nghiệm cho [17] | <https://arxiv.org/abs/2310.02540> |
| de la Rúa Martínez et al. — *The Hopsworks Feature Store for Machine Learning* | 2024 | SIGMOD Companion | 18 | Kiến trúc feature store, point-in-time correctness | Bản ACM **đóng**; bản tác giả: <https://content.hopsworks.ai/hubfs/The_Hopsworks_Feature_Store_for_Machine_Learning.pdf> |
| Mumuni & Mumuni — *Automated data processing and feature engineering for deep learning and big data applications: a survey* | 2024 | J. Information and Intelligence | 209 | Survey rộng về tự động hoá tiền xử lý | OA — <https://doi.org/10.1016/j.jiixd.2024.01.002> |
| Eken et al. — *A Multivocal Review of MLOps Practices, Challenges and Open Issues* | 2024 | ACM CSUR | 44 | Thực tiễn công nghiệp (gồm cả nguồn xám) | OA hybrid — <https://arxiv.org/abs/2406.09737> |
| Shankar et al. — *Operationalizing Machine Learning: An Interview Study* | 2022 | arXiv | 73 | Phỏng vấn kỹ sư ML về quy trình dữ liệu thực tế | <https://arxiv.org/abs/2209.09125> |
| Müller, Abdelaal & Stjelja — *Open-Source Drift Detection Tools in Action* | 2024 | DaWaK | 7 | Đánh giá **Evidently AI** và công cụ drift khác — đúng tech stack | <https://arxiv.org/abs/2404.18673> |
| Zhong et al. — *A Survey of Time Series Anomaly Detection Methods in the AIOps Domain* | 2023 | arXiv | 25 | Mở rộng AIOps cho dữ liệu chuỗi thời gian | <https://arxiv.org/abs/2308.00393> |
| Idowu et al. — *Management of Machine Learning Lifecycle Artifacts: A Survey* | 2022 | SIGMOD Record | 76 | Versioning dữ liệu & artifact, lineage | OA — <https://arxiv.org/abs/2210.11831> |
| Borisov et al. — *Deep Neural Networks and Tabular Data: A Survey* | 2022 | IEEE TNNLS | 1363 | Đặc thù dữ liệu bảng (nếu cần biện minh chọn XGBoost) | <https://arxiv.org/abs/2110.01889> |
| Grinsztajn et al. — *Why do tree-based models still outperform deep learning on typical tabular data?* | 2022 | NeurIPS | 677 | Như trên, góc nhìn thực nghiệm | <https://arxiv.org/abs/2207.08815> |

---

## 10. Đã cân nhắc nhưng **loại** — và lý do

| Tài liệu | Lý do loại |
|---|---|
| **ISO/IEC 5259-1..5:2024–2025** — *AI — Data quality for analytics and ML* | Tiêu chuẩn **trả phí**, không đọc được toàn văn miễn phí. Thay bằng [7] (ánh xạ ISO/IEC 25012) và [5] |
| **ISO/IEC 25012:2008** | Trả phí, và ngoài khung 5 năm |
| *A survey on dataset quality in machine learning*, Information and Software Technology 2023 (336 cit.) | Bản ScienceDirect **đóng**, không có bản preprint hợp lệ |
| Breck et al. — *Data Validation for Machine Learning* (SysML 2019) | Nền tảng của TFDV nhưng **ngoài khung 5 năm**. Có thể trích dẫn như công trình gốc, nhưng không tính vào 20 bài |
| Li et al. — *CleanML* (ICDE 2021) | Trùng nội dung nhiều với [14] và [8]; [8] sát hơn vì làm trên dữ liệu bảng với nhiều chiều chất lượng |
| Gebru et al. — *Datasheets for Datasets*; Pushkarna et al. — *Data Cards* (FAccT 2022) | Thuộc về **tài liệu hoá dataset** hơn là xử lý dữ liệu; để dành cho chương governance nếu có |
| Các bài AIOps dùng LLM để parse log (LILAC, DivLog, LogParser-LLM...) | Quá chuyên sâu một kỹ thuật, lệch khỏi phạm vi dữ liệu bảng; [20] đã bao phủ ở mức tổng quan |

---

## 11. Cách tái lập việc tra cứu này

```bash
# Metadata + số trích dẫn (Semantic Scholar, không cần API key, có rate limit)
curl -s "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,venue,citationCount,authors,openAccessPdf" \
  -H "Content-Type: application/json" \
  -d '{"ids":["ARXIV:2205.02302","DOI:10.1145/3592616"]}'

# Xác minh open access (Unpaywall)
curl -s "https://api.unpaywall.org/v2/10.1145/3592616?email=<email>"
```

Endpoint `/paper/search` của Semantic Scholar bị giới hạn tốc độ rất chặt khi không có API key —
nên dùng search engine (Google Scholar / Semantic Scholar web) để tìm ứng viên, rồi gọi `/paper/batch`
với danh sách DOI/arXiv ID để lấy metadata hàng loạt trong một request.

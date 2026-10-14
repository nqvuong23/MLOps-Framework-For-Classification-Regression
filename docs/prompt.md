## prompt kiếm API


## prompt kêu nó nghĩ ra bài toán từ nguồn API

```
tôi đã triển khai data collection nhưng đã lâu ngày chưa xem lại nên bị quên, tôi có nhớ là tôi đã dùng 2 nguồn API:  1 cái là thời tiết, 1 cái là chất lượng không khí. hiện tại tôi muốn tổng hợp và phân tích lại như sau:

1. Liêt kê tên nguồn, thông tin cơ bản về 2 nguồn đó.
2. thông tin chi tiết về 2 API đó, mỗi API trình bày:
- tên API, format của API, có bao nhiêu loại API có thể gọi mỗi nguồn
- thông tin chi tiết output có thể trả về của API đó (dạng json trong body http response)
- phân tích cấu trúc API trả về, mỗi nguồn có phải chỉ có 1 API có thể lấy? tập trung lấy chi tiết càng tốt
- Mỗi API có thể lấy data từ mốc thời gian nào tới mốc thời gian nào (mốc tối đa)
3. Lựa chọn bài toán cho mỗi nguồn:
- mỗi nguồn đề xuất 3 bài toán phân loại và 3 bài toán hồi quy
- trong mỗi bài toán phân loại/hồi quy chỉ rõ xem có nhãn sẵn hay phải tự phân tích và gán thủ công (đọc toàn bộ output của API chứa thông tin dữ liệu dataset để phân tích lựa chọn bài toán và nhãn như thế nào)
- trong mỗi bài toán phân loại/hồi quy, nên lấy tập dataset training/validation/test (có thể là 70%-15%-15%) và inferenece (dùng cho model sau khi đã deploy xong) như thế nào (từ mốc thời gian nào tới mốc thời gian nào, tập training/validate/test có thể là chỉ call API đúng 1 lần/mỗi lần training, còn inference dataset thì mỗi ngày lấy một lần kể từ thời điểm training xong)

Hãy trình bày thông tin vào file markdown trong thư mục docs/
```

```
bắt đầu với open-meteo, tôi muốn thử bài toán phân loại "24 giờ tới thuộc loại hiện tượng thời tiết nào?" (WX-C1). Hãy viết 1 file markdown trình bày 1 bản kế hoạch thực hiện tiền xử lý cho bài toán phân loại:

- phân tích bài toán: nhiệm vụ của model, input, output của model, model nên phân loại hiện tượng thời tiết tập trung 1 thành phố của 1 quốc gia bất kỳ hay trả lời rộng.
- xác định chu kỳ mỗi lần training: lần training đầu tiên nên lấy nhiều dataset (khoảng 10 năm gần nhất hay sao), từ lần 2 trở đi nên lấy dataset đã dùng từ lần 1 + dataset từ thời điểm sau training lần 1 tới sát lần training thứ 2. ví dụ chu kỳ training là 1 tháng và lần 1 training vào ngày 1/10/2026, thì dataset của lần trainining thứ 3 (1/12/2026) sẽ = dataset lần 1 (nhiều cỡ 10 năm do là lần đầu) + dataset các tháng sau đó (từ ngày 1/10/2026 đến 1/12/2026)
- phân tích dataset: tập training + validation + test nên dùng API nào, model era5 hay gì, ...
- chỉ tập trung vào quy trình tiền xử lý: thu thập --> định dạng bảng --> làm sạch (dọn dẹp missing value, kiểu dữ liệu sai lệnh ...) --> gán nhãn nếu chưa có hoặc xác định nhãn --> validation (bước làm sạch có xong chưa, làm sạch có bị sót lại bản ghi nào chưa cleaning không) --> feature engineering --> xong.
```



## prompt viết code cho tiền xử lý

```
tôi muốn thực hành tiền xử lý cho bài toán phân loại "WX-C1" này, mục tiêu là hiểu rõ từng giai đoạn xử lý. tôi cần bạn viết code thực hiện từng chức năng riêng lẻ, không cần viết thành 1 pipeline hoàn chỉnh bằng airflow như trước tại tôi muốn hiểu rõ hơn các bước con trước khi kết nối chúng thành 1 pipeline, yêu cầu cụ thể như sau:


- mỗi chức năng (thu thập, làm phẳng thành dạng bảng, làm sạch, gán nhãn, validation, feature engineering) tách thành từng file python riêng lẻ để dễ quan sát và chạy test: collection.py,  flatten.py, cleaning.py, labeling.py, validation.py, feature_engineering.py. toàn bộ bỏ vào thư mục /test.
- nơi lưu trữ dataset tại local luôn, không cần push lên s3 để thuận tiện
- tool thì sử dụng thư viện của python, không bắt buộc theo các tech stack hiện có, tránh dùng thư viện nặng như spark, vì mục tiêu là hiểu và test
- vì mục tiêu là bóc tách từng thành phần và chạy độc lập để quan sát rõ hơn workflow nên không yêu cầu viết code phức tạp thành 1 pipeline.
- tôi đã xóa đi các file/folder liên quan đến airflow, test trước đó để tránh làm phân tâm.
- viết file markdown trình bày ngắn gọn quy trình test và chạy demo.


--> mục tiêu là mô phỏng tiền xử lý, học và hiểu rõ hơn.
```

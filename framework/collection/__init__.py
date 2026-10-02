"""
Data Collection
===============
Thu thập dữ liệu training từ API bên ngoài theo chu kỳ:

    gọi API (JSON)  →  landing (lưu nguyên bản)  →  flatten thành bảng quan sát
                    →  gán nhãn đã "chín"        →  bảng training (Parquet)

Mỗi bài toán khai báo trong `problems/<problem_id>/collection.yaml`; code ở đây không biết
tên cột hay ngưỡng của bài toán nào. Không có cleaning / feature engineering — đó là các khối sau.
"""

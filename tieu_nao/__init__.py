"""
tieu_nao - Package Tiểu não Rồng Thần.

Tiểu não là CẦU NỐI giữa Cây linh hồn và Model.
Tiểu não ÉP Model làm việc, KHÔNG tự suy luận.

Nhiệm vụ:
    - Nhận lệnh từ Cây linh hồn.
    - ÉP Model làm đúng hợp đồng.
    - Chuyển kết quả Model về Cây.

Gồm 6 file chính:
    - __init__.py: đánh dấu package.
    - nhan_lenh.py: nhận lệnh từ Cây linh hồn.
    - ep_model.py: ÉP Model làm việc.
    - sinh_code.py: sinh code mới.
    - sua_code.py: sửa code lỗi.
    - kiem_tra_cung.py: kiểm tra cứng (syntax, format).

Thư mục con:
    - model/: bộ dò + gọi Model (12 file).
    - sanbox/: sandbox (6 file + giao_dien/).

Nguyên tắc:
    - Tiểu não KHÔNG suy luận — chỉ điều phối.
    - Mọi suy luận → giao cho Model.
    - Model = công cụ thuần, không giữ ngữ cảnh.
"""
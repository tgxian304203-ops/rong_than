"""
tra_web.api - Sub-package chứa các kết nối API tra web Rồng Thần.

Gồm 3 file:
    - __init__.py: đánh dấu sub-package.
    - serpjet.py: kết nối SERPJET (1.000 lượt/tháng).
    - tavily.py: kết nối Tavily (1.000 lượt/tháng).
    - brightdata.py: kết nối Bright Data (5.000 credit/tháng).

Mỗi file cung cấp:
    - tim_kiem_<tên>(key, cau_hoi, so_ket_qua): tìm kiếm.
    - kiem_tra_key_<tên>(key): kiểm tra key.
    - lay_quota_<tên>(key): lấy quota.
    - <tên>_san_sang(): kiểm tra API sẵn sàng.

Thứ tự xoay API (theo Phần 4):
    1. SERPJET (ưu tiên cao nhất).
    2. Tavily.
    3. Bright Data.

Tầng dữ liệu: Không (Tra web không lưu).
"""
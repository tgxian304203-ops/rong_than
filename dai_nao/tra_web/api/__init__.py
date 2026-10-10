"""
tra_web.api - Sub-package chứa các kết nối API tra web Rồng Thần.

Gồm 3 file:
    - __init__.py: đánh dấu sub-package.
    - serpjet.py: kết nối SERPJET.
    - tavily.py: kết nối Tavily.
    - brightdata.py: kết nối Bright Data.

Mỗi file cung cấp:
    - tim_kiem_<tên>(key, cau_hoi, so_ket_qua): tìm kiếm.
    - kiem_tra_key_<tên>(key): kiểm tra key.
    - lay_quota_<tên>(key): lấy quota.
    - <tên>_san_sang(): kiểm tra API sẵn sàng.

Thứ tự xoay API: SERPJET → Tavily → Bright Data.
"""

__all__ = ["serpjet", "tavily", "brightdata"]
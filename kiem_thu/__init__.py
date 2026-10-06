"""
kiem_thu - Package kiểm thử cho dự án Rồng Thần.

Bao gồm các module test cho từng phần:
    - thu_dai_nao.py: test Đại não
    - thu_tieu_nao.py: test Tiểu não
    - thu_tra_web.py: test Tra web
    - thu_sandbox.py: test Sandbox
    - thu_giao_dien.py: test Giao diện
    - thu_anh.py: test xử lý ảnh
    - thu_file.py: test xử lý file
    - thu_dang_ky.py: test đăng ký tài khoản
    - thu_dang_nhap.py: test đăng nhập
    - du_lieu_mau/: thư mục chứa dữ liệu mẫu

Chạy test:
    python -m kiem_thu.thu_dai_nao
    python -m kiem_thu.thu_tieu_nao
    ...
"""

__version__ = "1.0.0"
__all__ = [
    "thu_dai_nao",
    "thu_tieu_nao",
    "thu_tra_web",
    "thu_sandbox",
    "thu_giao_dien",
    "thu_anh",
    "thu_file",
    "thu_dang_ky",
    "thu_dang_nhap",
]
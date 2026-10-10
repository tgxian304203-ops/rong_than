"""
tien_do.py - Quản lý tiến độ ở Cây linh hồn.

Nhiệm vụ:
    - Tạo tiến độ khi bắt đầu dự án.
    - Cập nhật tiến độ sau mỗi bước.
    - Thêm bước vào lịch sử.
    - Đọc tiến độ cho Boss Thế.

Khác với luu_tru/tien_do.py:
    - File này là tầng wrapper (dùng cho Cây linh hồn).
    - Gọi hàm từ luu_tru/tien_do.py.
"""

from luu_tru import tien_do as _tien_do


# ================================================================
# TẠO TIẾN ĐỘ
# ================================================================
def tao_tien_do(chu_so_huu, id_chat, tong_buoc=0):
    """Tạo tiến độ mới cho chat."""
    return _tien_do.tao_tien_do(chu_so_huu, id_chat, tong_buoc)


# ================================================================
# ĐỌC TIẾN ĐỘ
# ================================================================
def doc_tien_do(chu_so_huu, id_chat):
    """Đọc tiến độ hiện tại."""
    return _tien_do.doc_tien_do(chu_so_huu, id_chat)


# ================================================================
# CẬP NHẬT TIẾN ĐỘ
# ================================================================
def cap_nhat_tien_do(chu_so_huu, id_chat, buoc_hien_tai=None,
                     tong_buoc=None, trang_thai=None):
    """Cập nhật tiến độ."""
    return _tien_do.cap_nhat(
        chu_so_huu, id_chat,
        buoc_hien_tai=buoc_hien_tai,
        tong_buoc=tong_buoc,
        trang_thai=trang_thai,
    )


# ================================================================
# THÊM BƯỚC VÀO LỊCH SỬ
# ================================================================
def them_buoc(chu_so_huu, id_chat, ten_buoc, ket_qua="xong"):
    """Thêm 1 bước vào lịch sử."""
    return _tien_do.them_buoc(chu_so_huu, id_chat, ten_buoc, ket_qua)


# ================================================================
# TĂNG BƯỚC
# ================================================================
def tang_buoc(chu_so_huu, id_chat):
    """Tăng bước hiện tại lên 1."""
    return _tien_do.tang_buoc(chu_so_huu, id_chat)


# ================================================================
# ĐÁNH DẤU XONG / LỖI
# ================================================================
def danh_dau_xong(chu_so_huu, id_chat):
    """Đánh dấu tiến độ đã xong."""
    return _tien_do.danh_dau_xong(chu_so_huu, id_chat)


def danh_dau_loi(chu_so_huu, id_chat):
    """Đánh dấu tiến độ bị lỗi."""
    return _tien_do.danh_dau_loi(chu_so_huu, id_chat)


# ================================================================
# XÓA TIẾN ĐỘ
# ================================================================
def xoa_tien_do(chu_so_huu, id_chat):
    """Xóa tiến độ."""
    return _tien_do.xoa(chu_so_huu, id_chat)


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat_tien_do(chu_so_huu, id_chat):
    """Trả chuỗi tóm tắt tiến độ."""
    return _tien_do.tom_tat(chu_so_huu, id_chat)


def phan_tram_hoan_thanh(chu_so_huu, id_chat):
    """Tính % hoàn thành."""
    return _tien_do.phan_tram_hoan_thanh(chu_so_huu, id_chat)
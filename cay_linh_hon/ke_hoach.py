"""
ke_hoach.py - Quản lý kế hoạch ở Cây linh hồn.

Nhiệm vụ:
    - Tạo kế hoạch khi Boss đầu lập.
    - Chia nhỏ kế hoạch thành các bước.
    - Đánh dấu bước đã xong.
    - Đọc kế hoạch cho Boss Thế tiếp tục.

Kế hoạch gồm:
    - danh_sach_buoc: [{"ten": "...", "trang_thai": "chua_lam|xong|loi"}]
    - buoc_hien_tai: chỉ số bước đang làm.

Nguyên tắc:
    - Kế hoạch lưu trong collection hop_dong (dùng chung).
    - Cập nhật liên tục.
"""

import time

from luu_tru import hop_dong as _hop_dong


# ================================================================
# TRẠNG THÁI BƯỚC
# ================================================================
BHUOC_CHUA_LAM = "chua_lam"
BHUOC_DANG_LAM = "dang_lam"
BHUOC_XONG = "xong"
BHUOC_LOI = "loi"


# ================================================================
# TẠO KẾ HOẠCH
# ================================================================
def tao_ke_hoach(chu_so_huu, id_chat, danh_sach_buoc):
    """
    Tạo kế hoạch với danh sách bước.

    danh_sach_buoc: ["Bước 1", "Bước 2", ...] hoặc
                    [{"ten": "..."}, ...].

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat or not danh_sach_buoc:
        return False

    buoc_chuan_hoa = []
    for b in danh_sach_buoc:
        if isinstance(b, str):
            buoc_chuan_hoa.append({
                "ten": b,
                "trang_thai": BHUOC_CHUA_LAM,
                "thoi_gian": 0,
            })
        elif isinstance(b, dict):
            buoc_chuan_hoa.append({
                "ten": b.get("ten", ""),
                "trang_thai": b.get("trang_thai", BHUOC_CHUA_LAM),
                "thoi_gian": b.get("thoi_gian", 0),
            })

    du_lieu = {
        "danh_sach_buoc": buoc_chuan_hoa,
        "buoc_hien_tai": 0,
        "thoi_gian_tao_ke_hoach": int(time.time()),
    }

    return _hop_dong.cap_nhat(chu_so_huu, id_chat, **du_lieu)


# ================================================================
# ĐỌC KẾ HOẠCH
# ================================================================
def doc_ke_hoach(chu_so_huu, id_chat):
    """
    Đọc kế hoạch hiện tại.

    Trả về: dict hoặc None.
    """
    hop_dong = _hop_dong.doc_hop_dong(chu_so_huu, id_chat)
    if not hop_dong:
        return None

    return {
        "danh_sach_buoc": hop_dong.get("danh_sach_buoc", []),
        "buoc_hien_tai": hop_dong.get("buoc_hien_tai", 0),
    }


# ================================================================
# ĐÁNH DẤU BƯỚC XONG
# ================================================================
def danh_dau_buoc_xong(chu_so_huu, id_chat, chi_so_buoc):
    """
    Đánh dấu bước đã xong.

    Trả về: True/False.
    """
    ke_hoach = doc_ke_hoach(chu_so_huu, id_chat)
    if not ke_hoach:
        return False

    danh_sach = ke_hoach.get("danh_sach_buoc", [])
    if chi_so_buoc < 0 or chi_so_buoc >= len(danh_sach):
        return False

    danh_sach[chi_so_buoc]["trang_thai"] = BHUOC_XONG
    danh_sach[chi_so_buoc]["thoi_gian"] = int(time.time())

    buoc_moi = chi_so_buoc + 1

    return _hop_dong.cap_nhat(
        chu_so_huu, id_chat,
        danh_sach_buoc=danh_sach,
        buoc_hien_tai=buoc_moi,
    )


# ================================================================
# ĐÁNH DẤU BƯỚC LỖI
# ================================================================
def danh_dau_buoc_loi(chu_so_huu, id_chat, chi_so_buoc):
    """Đánh dấu bước bị lỗi."""
    ke_hoach = doc_ke_hoach(chu_so_huu, id_chat)
    if not ke_hoach:
        return False

    danh_sach = ke_hoach.get("danh_sach_buoc", [])
    if chi_so_buoc < 0 or chi_so_buoc >= len(danh_sach):
        return False

    danh_sach[chi_so_buoc]["trang_thai"] = BHUOC_LOI
    danh_sach[chi_so_buoc]["thoi_gian"] = int(time.time())

    return _hop_dong.cap_nhat(
        chu_so_huu, id_chat,
        danh_sach_buoc=danh_sach,
    )


# ================================================================
# LẤY BƯỚC HIỆN TẠI
# ================================================================
def lay_buoc_hien_tai(chu_so_huu, id_chat):
    """Lấy thông tin bước đang làm."""
    ke_hoach = doc_ke_hoach(chu_so_huu, id_chat)
    if not ke_hoach:
        return None

    danh_sach = ke_hoach.get("danh_sach_buoc", [])
    chi_so = ke_hoach.get("buoc_hien_tai", 0)

    if chi_so < 0 or chi_so >= len(danh_sach):
        return None

    return danh_sach[chi_so]


# ================================================================
# ĐẾM BƯỚC
# ================================================================
def dem_buoc(chu_so_huu, id_chat):
    """
    Đếm số bước đã xong / tổng.

    Trả về: dict {xong, tong}.
    """
    ke_hoach = doc_ke_hoach(chu_so_huu, id_chat)
    if not ke_hoach:
        return {"xong": 0, "tong": 0}

    danh_sach = ke_hoach.get("danh_sach_buoc", [])
    so_xong = sum(1 for b in danh_sach if b.get("trang_thai") == BHUOC_XONG)

    return {"xong": so_xong, "tong": len(danh_sach)}


# ================================================================
# XÓA KẾ HOẠCH
# ================================================================
def xoa_ke_hoach(chu_so_huu, id_chat):
    """Xóa kế hoạch (reset danh sách bước)."""
    return _hop_dong.cap_nhat(
        chu_so_huu, id_chat,
        danh_sach_buoc=[],
        buoc_hien_tai=0,
    )
"""
luu_loi.py - Lưu lỗi vào Cây linh hồn.

Nhiệm vụ:
    - Lưu lỗi sau khi Model chạy lỗi.
    - Lưu vào huong_dan (blacklist) để Boss tránh.
    - Lưu vào code_da_viet (ket_qua).

Lỗi gồm:
    - loai_loi: syntax / runtime / timeout / khac.
    - thong_diep: mô tả lỗi.
    - dong: dòng lỗi (nếu có).
    - cach_sua: cách đã sửa (nếu có).

Nguyên tắc:
    - Lỗi lưu vào blacklist → Boss không lặp lại.
    - Cập nhật liên tục.
"""

import time

from luu_tru.ghi_nho import (
    luu_code_da_viet as _luu_code,
    lay_code_da_viet as _lay_code,
)

from cay_linh_hon.huong_dan import (
    them_vao_blacklist,
    them_da_thu,
)


# ================================================================
# LƯU LỖI
# ================================================================
def luu_loi(chu_so_huu, id_chat, buoc, loi):
    """
    Lưu lỗi cho 1 bước.

    loi: {
        loai_loi, thong_diep, dong, cach_sua
    }

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat or not loi:
        return False

    du_lieu_loi = {
        "loai_loi": loi.get("loai_loi", "khac"),
        "thong_diep": loi.get("thong_diep", ""),
        "dong": loi.get("dong"),
        "cach_sua": loi.get("cach_sua", ""),
        "thoi_gian": int(time.time()),
    }

    # Ghi vào huong_dan (blacklist)
    if du_lieu_loi["thong_diep"]:
        them_vao_blacklist(chu_so_huu, id_chat, {
            "loai": "loi",
            "noi_dung": du_lieu_loi["thong_diep"][:200],
            "buoc": buoc,
        })

    # Ghi vào code_da_viet
    code_cu = _lay_code(chu_so_huu, id_chat, buoc)
    if not code_cu:
        return False

    return _luu_code({
        "chu_so_huu": chu_so_huu,
        "id_chat": id_chat,
        "buoc": buoc,
        "file": code_cu.get("file", ""),
        "code": code_cu.get("code", ""),
        "phien_ban": (code_cu.get("phien_ban", 0) or 0) + 1,
        "loi": du_lieu_loi,
        "thoi_gian": int(time.time()),
    })


# ================================================================
# LƯU LỖI + CÁCH SỬA
# ================================================================
def luu_loi_va_cach_sua(chu_so_huu, id_chat, buoc,
                        loai_loi, thong_diep, cach_sua):
    """
    Lưu lỗi + cách sửa vào huong_dan để Boss nhớ.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat:
        return False

    ket_qua = luu_loi(chu_so_huu, id_chat, buoc, {
        "loai_loi": loai_loi,
        "thong_diep": thong_diep,
        "cach_sua": cach_sua,
    })

    if cach_sua:
        them_da_thu(chu_so_huu, id_chat, {
            "loai_loi": loai_loi,
            "cach_sua": cach_sua[:200],
        })

    return ket_qua


# ================================================================
# ĐỌC LỖI
# ================================================================
def doc_loi(chu_so_huu, id_chat, buoc):
    """Đọc lỗi của 1 bước."""
    du_lieu = _lay_code(chu_so_huu, id_chat, buoc)
    if not du_lieu:
        return None
    return du_lieu.get("loi")


# ================================================================
# ĐẾM SỐ LỖI
# ================================================================
def dem_loi(chu_so_huu, id_chat):
    """Đếm số bước có lỗi."""
    from luu_tru.ghi_nho import lay_tat_ca_code
    tat_ca = lay_tat_ca_code(chu_so_huu, id_chat)

    dem = 0
    for item in tat_ca:
        if item.get("loi"):
            dem += 1

    return dem


# ================================================================
# ĐẾM SỐ LẦN LỖI CÙNG LOẠI
# ================================================================
def dem_loi_cung_loai(chu_so_huu, id_chat, loai_loi):
    """Đếm số lần lỗi cùng loại."""
    from luu_tru.ghi_nho import lay_tat_ca_code
    tat_ca = lay_tat_ca_code(chu_so_huu, id_chat)

    dem = 0
    for item in tat_ca:
        loi = item.get("loi") or {}
        if loi.get("loai_loi") == loai_loi:
            dem += 1

    return dem


# ================================================================
# TÓM TẮT LỖI
# ================================================================
def tom_tat_loi(chu_so_huu, id_chat, buoc):
    """Tạo chuỗi tóm tắt lỗi."""
    loi = doc_loi(chu_so_huu, id_chat, buoc)
    if not loi:
        return ""

    return (
        f"[{loi.get('loai_loi', 'khac')}] "
        f"{loi.get('thong_diep', '')[:200]}"
    )


# ================================================================
# XÓA LỖI CỦA 1 BƯỚC
# ================================================================
def xoa_loi_buoc(chu_so_huu, id_chat, buoc):
    """Xóa lỗi của 1 bước (khi đã sửa xong)."""
    from luu_tru.ghi_nho import luu_code_da_viet as _luu
    du_lieu = _lay_code(chu_so_huu, id_chat, buoc)
    if not du_lieu:
        return False

    return _luu({
        "chu_so_huu": chu_so_huu,
        "id_chat": id_chat,
        "buoc": buoc,
        "file": du_lieu.get("file", ""),
        "code": du_lieu.get("code", ""),
        "phien_ban": (du_lieu.get("phien_ban", 0) or 0) + 1,
        "loi": None,
        "thoi_gian": int(time.time()),
    })
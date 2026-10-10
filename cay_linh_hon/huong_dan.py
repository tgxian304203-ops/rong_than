"""
huong_dan.py - Quản lý hướng dẫn ở Cây linh hồn.

Nhiệm vụ:
    - Ghi hướng dẫn mới (Boss viết).
    - Cập nhật hướng dẫn khi phát hiện lỗi.
    - Thêm blacklist (những gì không nên làm).
    - Cập nhật thông tin mới (từ tra web).
    - Đọc hướng dẫn cho Boss Thế.

Hướng dẫn gồm:
    - nen_lam_gi: nên làm gì để không sai.
    - blacklist: danh sách những gì không nên làm.
    - da_thu: những gì đã thử.
    - thong_tin_moi: thông tin mới từ tra web.

Nguyên tắc:
    - Boss là bên viết/cập nhật.
    - Ghi vào kho 2 (Cây linh hồn).
"""

from luu_tru.ghi_nho import (
    luu_huong_dan as _luu_huong_dan,
    lay_huong_dan as _lay_huong_dan,
    cap_nhat_huong_dan as _cap_nhat_huong_dan,
    them_blacklist as _them_blacklist,
)


# ================================================================
# GHI HƯỚNG DẪN MỚI (BOSS VIẾT)
# ================================================================
def ghi_huong_dan(chu_so_huu, id_chat, nen_lam_gi="",
                  da_thu=None, blacklist=None, thong_tin_moi=None):
    """
    Ghi hướng dẫn mới khi Boss đầu lập kế hoạch.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat:
        return False

    import time

    huong_dan = {
        "chu_so_huu": chu_so_huu,
        "id_chat": id_chat,
        "nen_lam_gi": nen_lam_gi or "",
        "da_thu": da_thu or [],
        "blacklist": blacklist or [],
        "thong_tin_moi": thong_tin_moi or {},
        "thoi_gian_cap_nhat": int(time.time()),
    }

    return _luu_huong_dan(huong_dan)


# ================================================================
# CẬP NHẬT HƯỚNG DẪN
# ================================================================
def cap_nhat_huong_dan(chu_so_huu, id_chat, du_lieu_moi):
    """
    Cập nhật hướng dẫn (khi phát hiện lỗi, cập nhật info mới).

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat or not du_lieu_moi:
        return False
    return _cap_nhat_huong_dan(chu_so_huu, id_chat, du_lieu_moi)


# ================================================================
# ĐỌC HƯỚNG DẪN (BOSS THẾ ĐỌC)
# ================================================================
def doc_huong_dan(chu_so_huu, id_chat):
    """Đọc hướng dẫn — dùng cho Boss Thế khi tiếp quản."""
    return _lay_huong_dan(chu_so_huu, id_chat)


# ================================================================
# THÊM BLACKLIST
# ================================================================
def them_vao_blacklist(chu_so_huu, id_chat, muc_moi):
    """
    Thêm 1 mục vào blacklist (những gì không nên làm).

    Trả về: True/False.
    """
    return _them_blacklist(chu_so_huu, id_chat, muc_moi)


# ================================================================
# THÊM ĐÃ THỬ
# ================================================================
def them_da_thu(chu_so_huu, id_chat, muc_moi):
    """Thêm 1 mục vào danh sách đã thử."""
    huong_dan = doc_huong_dan(chu_so_huu, id_chat)
    if not huong_dan:
        return False

    da_thu = huong_dan.get("da_thu", [])
    if muc_moi in da_thu:
        return True
    da_thu.append(muc_moi)

    return cap_nhat_huong_dan(chu_so_huu, id_chat, {"da_thu": da_thu})


# ================================================================
# CẬP NHẬT THÔNG TIN MỚI (TỪ TRA WEB)
# ================================================================
def cap_nhat_thong_tin_moi(chu_so_huu, id_chat, thong_tin):
    """
    Cập nhật thông tin mới từ tra web.

    Trả về: True/False.
    """
    huong_dan = doc_huong_dan(chu_so_huu, id_chat)
    if not huong_dan:
        thong_tin_cu = {}
    else:
        thong_tin_cu = huong_dan.get("thong_tin_moi", {}) or {}

    thong_tin_cu.update(thong_tin)

    return cap_nhat_huong_dan(chu_so_huu, id_chat, {
        "thong_tin_moi": thong_tin_cu,
    })


# ================================================================
# TÓM TẮT HƯỚNG DẪN
# ================================================================
def tom_tat_huong_dan(chu_so_huu, id_chat):
    """Trả chuỗi tóm tắt hướng dẫn."""
    huong_dan = doc_huong_dan(chu_so_huu, id_chat)
    if not huong_dan:
        return ""

    phan = []
    if huong_dan.get("nen_lam_gi"):
        phan.append(f"Nên làm: {huong_dan['nen_lam_gi']}")

    blacklist = huong_dan.get("blacklist", [])
    if blacklist:
        phan.append(f"Tránh: {', '.join(str(x) for x in blacklist[:5])}")

    return "\n".join(phan)
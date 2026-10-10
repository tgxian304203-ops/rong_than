"""
liet_ke_du_an.py - Liệt kê dự án của Cây linh hồn.

Nhiệm vụ:
    - Liệt kê tất cả chat có cây linh hồn của user.
    - Đếm số node / code / lỗi trong từng cây.
    - Trả thông tin tóm tắt cho giao diện.

Nguyên tắc:
    - Chỉ đọc — không sửa.
    - Dữ liệu từ 2 kho.
"""

from luu_tru.ghi_nho import (
    lay_danh_sach_chat_nhanh_cua,
    lay_danh_sach_du_an_cua,
    lay_danh_sach_tro_chuyen_cua,
    lay_danh_sach_node,
    lay_tat_ca_code,
    lay_hop_dong,
    lay_huong_dan,
    lay_tien_do,
)


# ================================================================
# ĐẾM NODE TRONG CÂY
# ================================================================
def _dem_node(chu_so_huu, id_chat):
    """Đếm số node trong cây linh hồn của 1 chat."""
    try:
        danh_sach = lay_danh_sach_node(chu_so_huu, id_chat)
        return len(danh_sach) if danh_sach else 0
    except Exception:
        return 0


def _dem_code(chu_so_huu, id_chat):
    """Đếm số code đã viết."""
    try:
        danh_sach = lay_tat_ca_code(chu_so_huu, id_chat)
        return len(danh_sach) if danh_sach else 0
    except Exception:
        return 0


# ================================================================
# TÓM TẮT 1 CHAT
# ================================================================
def _tom_tat_chat(chu_so_huu, id_chat):
    """
    Tạo tóm tắt cho 1 chat.

    Trả về: dict.
    """
    tom_tat = {
        "id_chat": id_chat,
        "co_hop_dong": False,
        "co_huong_dan": False,
        "co_tien_do": False,
        "so_node": 0,
        "so_code": 0,
    }

    try:
        hop_dong = lay_hop_dong(chu_so_huu, id_chat)
        if hop_dong:
            tom_tat["co_hop_dong"] = True
            tom_tat["dang_lam_gi"] = hop_dong.get("dang_lam_gi", "")
            tom_tat["dang_lam_toi_dau"] = hop_dong.get("dang_lam_toi_dau", "")
            tom_tat["tiep_theo_lam_gi"] = hop_dong.get("tiep_theo_lam_gi", "")
    except Exception:
        pass

    try:
        huong_dan = lay_huong_dan(chu_so_huu, id_chat)
        if huong_dan:
            tom_tat["co_huong_dan"] = True
            tom_tat["so_blacklist"] = len(huong_dan.get("blacklist", []))
    except Exception:
        pass

    try:
        tien_do = lay_tien_do(chu_so_huu, id_chat)
        if tien_do:
            tom_tat["co_tien_do"] = True
            tom_tat["buoc_hien_tai"] = tien_do.get("buoc_hien_tai", 0)
            tom_tat["tong_buoc"] = tien_do.get("tong_buoc", 0)
            tom_tat["trang_thai"] = tien_do.get("trang_thai", "")
    except Exception:
        pass

    tom_tat["so_node"] = _dem_node(chu_so_huu, id_chat)
    tom_tat["so_code"] = _dem_code(chu_so_huu, id_chat)

    return tom_tat


# ================================================================
# LIỆT KÊ CHAT NHANH
# ================================================================
def liet_ke_chat_nhanh(chu_so_huu):
    """
    Liệt kê tất cả chat nhanh của user.

    Trả về: list dict.
    """
    if not chu_so_huu:
        return []

    try:
        danh_sach = lay_danh_sach_chat_nhanh_cua(chu_so_huu) or []
    except Exception:
        return []

    ket_qua = []
    for chat in danh_sach:
        id_chat = chat.get("id")
        if not id_chat:
            continue

        muc = {
            "id": id_chat,
            "ten": chat.get("ten", "Chat mới"),
            "ngay_tao": chat.get("ngay_tao", 0),
        }
        muc.update(_tom_tat_chat(chu_so_huu, id_chat))
        ket_qua.append(muc)

    return ket_qua


# ================================================================
# LIỆT KÊ DỰ ÁN
# ================================================================
def liet_ke_du_an(chu_so_huu):
    """
    Liệt kê tất cả dự án của user.

    Trả về: list dict.
    """
    if not chu_so_huu:
        return []

    try:
        danh_sach = lay_danh_sach_du_an_cua(chu_so_huu) or []
    except Exception:
        return []

    ket_qua = []
    for du_an in danh_sach:
        id_du_an = du_an.get("id")
        if not id_du_an:
            continue

        muc = {
            "id": id_du_an,
            "ten": du_an.get("ten", "Dự án"),
            "ngay_tao": du_an.get("ngay_tao", 0),
            "so_tro_chuyen": 0,
        }

        try:
            tro_chuyen = lay_danh_sach_tro_chuyen_cua(id_du_an, chu_so_huu) or []
            muc["so_tro_chuyen"] = len(tro_chuyen)
        except Exception:
            pass

        ket_qua.append(muc)

    return ket_qua


# ================================================================
# LIỆT KÊ TRÒ CHUYỆN TRONG DỰ ÁN
# ================================================================
def liet_ke_tro_chuyen(chu_so_huu, id_du_an):
    """Liệt kê trò chuyện trong 1 dự án."""
    if not chu_so_huu or not id_du_an:
        return []

    try:
        danh_sach = lay_danh_sach_tro_chuyen_cua(id_du_an, chu_so_huu) or []
    except Exception:
        return []

    ket_qua = []
    for tro in danh_sach:
        id_tro = tro.get("id")
        if not id_tro:
            continue

        muc = {
            "id": id_tro,
            "ten": tro.get("ten", "Trò chuyện"),
            "id_du_an": id_du_an,
            "ngay_tao": tro.get("ngay_tao", 0),
        }
        muc.update(_tom_tat_chat(chu_so_huu, id_tro))
        ket_qua.append(muc)

    return ket_qua


# ================================================================
# LIỆT KÊ TẤT CẢ (chat + dự án)
# ================================================================
def liet_ke_tat_ca(chu_so_huu):
    """
    Liệt kê toàn bộ chat + dự án của user.

    Trả về: dict {chat_nhanh, du_an}.
    """
    return {
        "chat_nhanh": liet_ke_chat_nhanh(chu_so_huu),
        "du_an": liet_ke_du_an(chu_so_huu),
    }


# ================================================================
# ĐẾM TỔNG
# ================================================================
def dem_tong(chu_so_huu):
    """Đếm tổng số chat + dự án."""
    ket_qua = liet_ke_tat_ca(chu_so_huu)
    return {
        "so_chat_nhanh": len(ket_qua.get("chat_nhanh", [])),
        "so_du_an": len(ket_qua.get("du_an", [])),
    }
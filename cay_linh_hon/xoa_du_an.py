"""
xoa_du_an.py - Xóa dự án / chat khỏi Cây linh hồn.

Nhiệm vụ:
    - Xóa 1 chat nhanh (kèm cây linh hồn của chat đó).
    - Xóa 1 dự án (kèm tất cả trò chuyện + cây).
    - Xóa 1 trò chuyện.
    - Xóa toàn bộ cây của 1 user (khi xóa tài khoản).

Nguyên tắc:
    - Xóa 1 chat → xóa cây của chat đó ở KHO 2.
    - KHÔNG ảnh hưởng chat khác.
    - Có cảnh báo trước khi xóa (ở tầng giao diện).
"""

from luu_tru.ghi_nho import (
    xoa_chat_nhanh_theo_id,
    xoa_du_an_theo_id,
    xoa_tro_chuyen_theo_id,
    xoa_toan_bo_cay_cua_chat,
    xoa_toan_bo_cay_cua_user,
)


# ================================================================
# XÓA CHAT NHANH
# ================================================================
def xoa_chat_nhanh(chu_so_huu, id_chat):
    """
    Xóa 1 chat nhanh + cây linh hồn của chat đó.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat:
        return False

    # Xóa kho 1
    try:
        xoa_chat_nhanh_theo_id(id_chat, chu_so_huu)
    except Exception:
        pass

    # Xóa kho 2 (cây linh hồn)
    try:
        xoa_toan_bo_cay_cua_chat(chu_so_huu, id_chat)
    except Exception:
        pass

    return True


# ================================================================
# XÓA DỰ ÁN
# ================================================================
def xoa_du_an(chu_so_huu, id_du_an):
    """
    Xóa 1 dự án + tất cả trò chuyện + cây của dự án.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_du_an:
        return False

    # Lấy danh sách trò chuyện trước khi xóa
    try:
        from luu_tru.ghi_nho import lay_danh_sach_tro_chuyen_cua
        danh_sach_tro = lay_danh_sach_tro_chuyen_cua(id_du_an, chu_so_huu) or []
    except Exception:
        danh_sach_tro = []

    # Xóa cây linh hồn của từng trò chuyện
    for tro in danh_sach_tro:
        id_tro = tro.get("id")
        if id_tro:
            try:
                xoa_toan_bo_cay_cua_chat(chu_so_huu, id_tro)
            except Exception:
                pass

    # Xóa dự án (kho 1 — xóa luôn trò chuyện + tin nhắn)
    try:
        xoa_du_an_theo_id(id_du_an)
    except Exception:
        pass

    return True


# ================================================================
# XÓA TRÒ CHUYỆN
# ================================================================
def xoa_tro_chuyen(chu_so_huu, id_tro):
    """
    Xóa 1 trò chuyện + cây linh hồn của nó.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_tro:
        return False

    # Xóa kho 1
    try:
        xoa_tro_chuyen_theo_id(id_tro, chu_so_huu)
    except Exception:
        pass

    # Xóa kho 2 (cây linh hồn)
    try:
        xoa_toan_bo_cay_cua_chat(chu_so_huu, id_tro)
    except Exception:
        pass

    return True


# ================================================================
# XÓA TOÀN BỘ CÂY CỦA USER
# ================================================================
def xoa_toan_bo_cua_user(chu_so_huu):
    """
    Xóa toàn bộ cây linh hồn của 1 user (khi xóa tài khoản).

    Trả về: True/False.
    """
    if not chu_so_huu:
        return False

    try:
        return xoa_toan_bo_cay_cua_user(chu_so_huu)
    except Exception:
        return False


# ================================================================
# ĐẾM SỐ CÂY SẼ XÓA
# ================================================================
def dem_cay_se_xoa(chu_so_huu):
    """
    Đếm số cây linh hồn sẽ bị xóa nếu xóa user.

    Trả về: int.
    """
    if not chu_so_huu:
        return 0

    try:
        from luu_tru.ghi_nho import (
            lay_danh_sach_chat_nhanh_cua,
            lay_danh_sach_du_an_cua,
            lay_danh_sach_tro_chuyen_cua,
        )

        dem = 0

        # Chat nhanh
        danh_sach_chat = lay_danh_sach_chat_nhanh_cua(chu_so_huu) or []
        dem += len(danh_sach_chat)

        # Dự án + trò chuyện
        danh_sach_du_an = lay_danh_sach_du_an_cua(chu_so_huu) or []
        for du_an in danh_sach_du_an:
            id_du_an = du_an.get("id")
            if id_du_an:
                danh_sach_tro = lay_danh_sach_tro_chuyen_cua(id_du_an, chu_so_huu) or []
                dem += len(danh_sach_tro)

        return dem
    except Exception:
        return 0


# ================================================================
# XÁC NHẬN TRƯỚC KHI XÓA
# ================================================================
def tao_canh_bao_xoa_chat(chu_so_huu, id_chat):
    """Tạo chuỗi cảnh báo trước khi xóa chat."""
    try:
        from luu_tru.ghi_nho import lay_tat_ca_code
        so_code = len(lay_tat_ca_code(chu_so_huu, id_chat))
    except Exception:
        so_code = 0

    if so_code > 0:
        return (
            f"Chat này có {so_code} file code đã viết. "
            "Khi xóa chat, toàn bộ code này sẽ bị xóa. "
            "Bạn có chắc chắn?"
        )

    return "Bạn có chắc muốn xóa chat này?"


def tao_canh_bao_xoa_du_an(chu_so_huu, id_du_an):
    """Tạo chuỗi cảnh báo trước khi xóa dự án."""
    try:
        from luu_tru.ghi_nho import lay_danh_sach_tro_chuyen_cua
        danh_sach = lay_danh_sach_tro_chuyen_cua(id_du_an, chu_so_huu) or []
        so_tro = len(danh_sach)
    except Exception:
        so_tro = 0

    if so_tro > 0:
        return (
            f"Dự án này có {so_tro} trò chuyện. "
            "Khi xóa dự án, toàn bộ trò chuyện + cây linh hồn sẽ bị xóa. "
            "Bạn có chắc chắn?"
        )

    return "Bạn có chắc muốn xóa dự án này?"
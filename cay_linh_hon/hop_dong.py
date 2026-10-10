"""
hop_dong.py - Quản lý hợp đồng ở Cây linh hồn.

Nhiệm vụ:
    - Ghi hợp đồng mới (Đại não ghi lần đầu).
    - Cập nhật hợp đồng sau mỗi sự kiện.
    - Đọc hợp đồng cho Boss Thế.
    - Xóa hợp đồng khi chat bị xóa.

Hợp đồng gồm 3 trường:
    - dang_lam_gi
    - dang_lam_toi_dau
    - tiep_theo_lam_gi

Nguyên tắc:
    - Đại não là bên ghi/cập nhật.
    - Cập nhật LIÊN TỤC.
"""

from luu_tru import hop_dong as _hop_dong


# ================================================================
# GHI HỢP ĐỒNG MỚI (ĐẠI NÃO GHI)
# ================================================================
def ghi_hop_dong(chu_so_huu, id_chat, dang_lam_gi="",
                 dang_lam_toi_dau="", tiep_theo_lam_gi=""):
    """
    Ghi hợp đồng mới khi Boss đầu lập kế hoạch.

    Trả về: True/False.
    """
    return _hop_dong.tao_hop_dong(
        chu_so_huu, id_chat,
        dang_lam_gi=dang_lam_gi,
        dang_lam_toi_dau=dang_lam_toi_dau,
        tiep_theo_lam_gi=tiep_theo_lam_gi,
    )


# ================================================================
# CẬP NHẬT HỢP ĐỒNG (SAU MỖI SỰ KIỆN)
# ================================================================
def cap_nhat_hop_dong(chu_so_huu, id_chat,
                      dang_lam_gi=None,
                      dang_lam_toi_dau=None,
                      tiep_theo_lam_gi=None):
    """
    Cập nhật hợp đồng sau mỗi sự kiện.

    Trả về: True/False.
    """
    return _hop_dong.cap_nhat(
        chu_so_huu, id_chat,
        dang_lam_gi=dang_lam_gi,
        dang_lam_toi_dau=dang_lam_toi_dau,
        tiep_theo_lam_gi=tiep_theo_lam_gi,
    )


# ================================================================
# ĐỌC HỢP ĐỒNG (BOSS THẾ ĐỌC)
# ================================================================
def doc_hop_dong(chu_so_huu, id_chat):
    """
    Đọc hợp đồng — dùng cho Boss Thế khi tiếp quản.

    Trả về: dict hoặc None.
    """
    return _hop_dong.doc_hop_dong(chu_so_huu, id_chat)


# ================================================================
# XÓA HỢP ĐỒNG
# ================================================================
def xoa_hop_dong(chu_so_huu, id_chat):
    """Xóa hợp đồng khi chat bị xóa."""
    return _hop_dong.xoa(chu_so_huu, id_chat)


# ================================================================
# TÓM TẮT HỢP ĐỒNG
# ================================================================
def tom_tat_hop_dong(chu_so_huu, id_chat):
    """Trả chuỗi tóm tắt hợp đồng."""
    return _hop_dong.tom_tat(chu_so_huu, id_chat)
"""
hop_dong.py - Quản lý hợp đồng Rồng Thần (kho 2).

Nhiệm vụ:
    - Định nghĩa schema hợp đồng (hop_dong).
    - Cung cấp hàm tạo/cập nhật/đọc hợp đồng.
    - Hợp đồng gồm 3 trường chính:
        + dang_lam_gi
        + dang_lam_toi_dau
        + tiep_theo_lam_gi
    - Cập nhật LIÊN TỤC sau mỗi sự kiện.

Nguyên tắc:
    - Mọi hợp đồng gắn chu_so_huu + id_chat.
    - Hợp đồng là CỦA RIÊNG mỗi chat.
    - Không lưu lịch sử phiên bản cũ — chỉ lưu bản mới nhất.
"""

import time

from luu_tru.ghi_nho import (
    luu_hop_dong as _luu_hop_dong,
    lay_hop_dong as _lay_hop_dong,
    cap_nhat_hop_dong as _cap_nhat_hop_dong,
    xoa_hop_dong as _xoa_hop_dong,
)


# ================================================================
# TẠO HỢP ĐỒNG MỚI
# ================================================================
def tao_hop_dong(chu_so_huu, id_chat, dang_lam_gi="",
                 dang_lam_toi_dau="", tiep_theo_lam_gi=""):
    """
    Tạo hợp đồng mới cho 1 chat.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat:
        return False

    hop_dong = {
        "chu_so_huu": chu_so_huu,
        "id_chat": id_chat,
        "dang_lam_gi": dang_lam_gi,
        "dang_lam_toi_dau": dang_lam_toi_dau,
        "tiep_theo_lam_gi": tiep_theo_lam_gi,
        "thoi_gian_cap_nhat": int(time.time()),
        "phien_ban": 1,
    }

    return _luu_hop_dong(hop_dong)


# ================================================================
# ĐỌC HỢP ĐỒNG
# ================================================================
def doc_hop_dong(chu_so_huu, id_chat):
    """
    Đọc hợp đồng hiện tại của 1 chat.

    Trả về: dict hoặc None.
    """
    if not chu_so_huu or not id_chat:
        return None
    return _lay_hop_dong(chu_so_huu, id_chat)


# ================================================================
# CẬP NHẬT HỢP ĐỒNG
# ================================================================
def cap_nhat(chu_so_huu, id_chat,
             dang_lam_gi=None,
             dang_lam_toi_dau=None,
             tiep_theo_lam_gi=None):
    """
    Cập nhật hợp đồng (chỉ cập nhật trường được truyền).

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat:
        return False

    du_lieu_moi = {}

    if dang_lam_gi is not None:
        du_lieu_moi["dang_lam_gi"] = dang_lam_gi

    if dang_lam_toi_dau is not None:
        du_lieu_moi["dang_lam_toi_dau"] = dang_lam_toi_dau

    if tiep_theo_lam_gi is not None:
        du_lieu_moi["tiep_theo_lam_gi"] = tiep_theo_lam_gi

    if not du_lieu_moi:
        return False

    return _cap_nhat_hop_dong(chu_so_huu, id_chat, du_lieu_moi)


# ================================================================
# CẬP NHẬT TOÀN BỘ (đè hết)
# ================================================================
def cap_nhat_toan_bo(chu_so_huu, id_chat, dang_lam_gi,
                     dang_lam_toi_dau, tiep_theo_lam_gi):
    """
    Cập nhật cả 3 trường cùng lúc.

    Trả về: True/False.
    """
    return cap_nhat(
        chu_so_huu, id_chat,
        dang_lam_gi=dang_lam_gi,
        dang_lam_toi_dau=dang_lam_toi_dau,
        tiep_theo_lam_gi=tiep_theo_lam_gi,
    )


# ================================================================
# XÓA HỢP ĐỒNG
# ================================================================
def xoa(chu_so_huu, id_chat):
    """Xóa hợp đồng của 1 chat."""
    if not chu_so_huu or not id_chat:
        return False
    return _xoa_hop_dong(chu_so_huu, id_chat)


# ================================================================
# LẤY TÓM TẮT HỢP ĐỒNG
# ================================================================
def tom_tat(chu_so_huu, id_chat):
    """
    Lấy tóm tắt hợp đồng dạng chuỗi.

    Trả về: chuỗi hoặc "".
    """
    hop_dong = doc_hop_dong(chu_so_huu, id_chat)
    if not hop_dong:
        return ""

    phan = []
    if hop_dong.get("dang_lam_gi"):
        phan.append(f"Đang làm: {hop_dong['dang_lam_gi']}")
    if hop_dong.get("dang_lam_toi_dau"):
        phan.append(f"Tới đâu: {hop_dong['dang_lam_toi_dau']}")
    if hop_dong.get("tiep_theo_lam_gi"):
        phan.append(f"Tiếp theo: {hop_dong['tiep_theo_lam_gi']}")

    return "\n".join(phan)


# ================================================================
# KIỂM TRA HỢP ĐỒNG TỒN TẠI
# ================================================================
def co_hop_dong(chu_so_huu, id_chat):
    """Kiểm tra hợp đồng đã tồn tại chưa."""
    return doc_hop_dong(chu_so_huu, id_chat) is not None
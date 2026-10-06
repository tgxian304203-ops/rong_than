"""
session.py - Quản lý dự án + chat nhanh + chat mới Rồng Thần.
------------------------------------------------------------
ĐÃ SỬA: Cho phép chế độ KHÁCH dùng New Chat + Tạo dự án.
    - Khách  : trả về đối tượng tạm (id + tên), KHÔNG lưu kho.
    - Tài khoản: lưu vào kho 1 như cũ.

Nhiệm vụ:
    - lay_danh_sach_du_an(): danh sách dự án.
    - tao_du_an(du_lieu): tạo dự án mới.
    - xoa_du_an(du_lieu): xóa dự án theo id.
    - lay_danh_sach_chat_nhanh(): danh sách chat nhanh.
    - tao_chat_nhanh(du_lieu): tạo chat nhanh mới.
    - xoa_chat_nhanh(du_lieu): xóa chat nhanh theo id.
    - tao_chat_moi(du_lieu): alias của tao_chat_nhanh.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import secrets
import time

from flask import session as phien_flask

from dai_nao.ghi_nho import (
    lay_danh_sach_du_an_cua,
    luu_du_an,
    lay_du_an,
    xoa_du_an_theo_id,
    lay_danh_sach_chat_nhanh_cua,
    luu_chat_nhanh,
    xoa_chat_nhanh_theo_id,
)


# ----------------------------------------------------------------
# GHI LOG
# ----------------------------------------------------------------
def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ----------------------------------------------------------------
# TIỆN ÍCH
# ----------------------------------------------------------------
def _tao_id():
    return "id-" + secrets.token_hex(8)


def _lay_ten_dang_nhap():
    """Lấy tên đăng nhập. Trả None nếu là khách."""
    return phien_flask.get("ten_dang_nhap")


# ================================================================
# DỰ ÁN
# ================================================================
def lay_danh_sach_du_an():
    """
    Trả danh sách dự án.
    Khách → trả danh sách rỗng (vì khách không lưu dự án).
    """
    ten = _lay_ten_dang_nhap()
    if not ten:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_du_an_cua(ten)
    return {"thanh_cong": True, "danh_sach": danh_sach or []}


def tao_du_an(du_lieu):
    """
    Tạo dự án mới.
    - Tài khoản: lưu kho 1.
    - Khách    : trả về dự án tạm (id ngẫu nhiên, không lưu).
    """
    ten_tk = _lay_ten_dang_nhap()

    ten_du_an = (du_lieu.get("ten") or "").strip()
    if not ten_du_an:
        return {"thanh_cong": False, "loi": "Thiếu tên dự án."}

    du_an_moi = {
        "id": _tao_id(),
        "ten": ten_du_an,
        "ngay_tao": int(time.time()),
    }

    # Khách → không lưu kho, chỉ trả tạm
    if not ten_tk:
        du_an_moi["chu_so_huu"] = "khach"
        du_an_moi["tam"] = True
        _ghi_log("dai-nao", f"Khách tạo dự án tạm '{ten_du_an}' (không lưu)")
        return {"thanh_cong": True, "du_an": du_an_moi, "tam": True}

    # Tài khoản → lưu kho 1
    du_an_moi["chu_so_huu"] = ten_tk
    du_an_moi["tam"] = False

    if not luu_du_an(du_an_moi):
        return {"thanh_cong": False, "loi": "Không lưu được dự án."}

    _ghi_log("dai-nao", f"Tạo dự án '{ten_du_an}' cho tài khoản {ten_tk}")
    return {"thanh_cong": True, "du_an": du_an_moi}


def xoa_du_an(du_lieu):
    """
    Xóa dự án theo id.
    - Tài khoản: xóa trong kho 1.
    - Khách    : chỉ báo thành công (không có gì trong kho).
    """
    ten_tk = _lay_ten_dang_nhap()
    id_xoa = du_lieu.get("id")

    if not id_xoa:
        return {"thanh_cong": False, "loi": "Thiếu id dự án."}

    # Khách → báo thành công luôn (vì không lưu kho)
    if not ten_tk:
        return {"thanh_cong": True}

    du_an = lay_du_an(id_xoa)
    if not du_an:
        # Không tìm thấy trong kho → cũng coi như đã xóa (tránh lỗi UI)
        return {"thanh_cong": True}

    if du_an.get("chu_so_huu") != ten_tk:
        return {"thanh_cong": False, "loi": "Không có quyền xóa dự án này."}

    if not xoa_du_an_theo_id(id_xoa):
        return {"thanh_cong": False, "loi": "Không xóa được dự án."}

    _ghi_log("dai-nao", f"Xóa dự án id={id_xoa} của tài khoản {ten_tk}")
    return {"thanh_cong": True}


# ================================================================
# CHAT NHANH
# ================================================================
def lay_danh_sach_chat_nhanh():
    """
    Trả danh sách chat nhanh.
    Khách → trả rỗng.
    """
    ten = _lay_ten_dang_nhap()
    if not ten:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_chat_nhanh_cua(ten)
    return {"thanh_cong": True, "danh_sach": danh_sach or []}


def tao_chat_nhanh(du_lieu):
    """
    Tạo chat nhanh mới.
    - Tài khoản: lưu kho 1.
    - Khách    : trả về chat tạm (id ngẫu nhiên, không lưu).
    """
    ten_tk = _lay_ten_dang_nhap()
    ten_chat = (du_lieu.get("ten") or "Chat mới").strip()

    chat_moi = {
        "id": _tao_id(),
        "ten": ten_chat,
        "ngay_tao": int(time.time()),
    }

    # Khách → không lưu kho
    if not ten_tk:
        chat_moi["chu_so_huu"] = "khach"
        chat_moi["tam"] = True
        _ghi_log("dai-nao", f"Khách tạo chat tạm '{ten_chat}' (không lưu)")
        return {"thanh_cong": True, "chat": chat_moi, "tam": True}

    # Tài khoản → lưu kho 1
    chat_moi["chu_so_huu"] = ten_tk
    chat_moi["tam"] = False

    if not luu_chat_nhanh(chat_moi):
        return {"thanh_cong": False, "loi": "Không lưu được chat."}

    _ghi_log("dai-nao", f"Tạo chat nhanh '{ten_chat}' cho tài khoản {ten_tk}")
    return {"thanh_cong": True, "chat": chat_moi}


def xoa_chat_nhanh(du_lieu):
    """
    Xóa chat nhanh theo id.
    - Tài khoản: xóa kho 1.
    - Khách    : báo thành công luôn.
    """
    ten_tk = _lay_ten_dang_nhap()
    id_xoa = du_lieu.get("id")

    if not id_xoa:
        return {"thanh_cong": False, "loi": "Thiếu id chat."}

    # Khách → báo thành công (không có gì trong kho)
    if not ten_tk:
        return {"thanh_cong": True}

    if not xoa_chat_nhanh_theo_id(id_xoa, ten_tk):
        # Không tìm thấy → cũng coi như đã xóa
        return {"thanh_cong": True}

    _ghi_log("dai-nao", f"Xóa chat nhanh id={id_xoa} của tài khoản {ten_tk}")
    return {"thanh_cong": True}


# ================================================================
# CHAT MỚI (alias)
# ================================================================
def tao_chat_moi(du_lieu):
    """Tạo cuộc trò chuyện mới — alias của tao_chat_nhanh."""
    return tao_chat_nhanh(du_lieu)
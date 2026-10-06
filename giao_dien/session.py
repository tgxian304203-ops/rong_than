"""
session.py - Quản lý dự án + chat nhanh + chat mới Rồng Thần.

Nhiệm vụ:
    - lay_danh_sach_du_an(): danh sách dự án của tài khoản hiện tại.
    - tao_du_an(du_lieu): tạo dự án mới.
    - xoa_du_an(du_lieu): xóa dự án theo id.
    - lay_danh_sach_chat_nhanh(): danh sách chat nhanh.
    - tao_chat_nhanh(du_lieu): tạo chat nhanh mới.
    - xoa_chat_nhanh(du_lieu): xóa chat nhanh theo id.
    - tao_chat_moi(du_lieu): tạo chat mới (alias của tao_chat_nhanh).

Quy tắc:
    - Mọi dự án / chat thuộc về tài khoản đang đăng nhập.
    - Nếu chưa đăng nhập (chế độ khách), không lưu — trả về lỗi.
    - Lưu vào kho 1 (collection du_an và lich_su_chat).

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import secrets
import time

from flask import session as phien_flask

# ----------------------------------------------------------------
# IMPORT TẦNG DỮ LIỆU
# ----------------------------------------------------------------
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
    """Sinh id ngẫu nhiên cho dự án / chat."""
    return "id-" + secrets.token_hex(8)


def _lay_ten_dang_nhap():
    """Lấy tên đăng nhập hiện tại từ Flask session."""
    return phien_flask.get("ten_dang_nhap")


# ----------------------------------------------------------------
# DỰ ÁN
# ----------------------------------------------------------------
def lay_danh_sach_du_an():
    """
    Trả danh sách dự án của tài khoản hiện tại.
    Nếu chưa đăng nhập → trả danh sách rỗng.
    """
    ten = _lay_ten_dang_nhap()
    if not ten:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_du_an_cua(ten)
    return {"thanh_cong": True, "danh_sach": danh_sach or []}


def tao_du_an(du_lieu):
    """
    Tạo dự án mới cho tài khoản hiện tại.
    du_lieu: { ten }
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": False, "loi": "Chưa đăng nhập."}

    ten_du_an = (du_lieu.get("ten") or "").strip()
    if not ten_du_an:
        return {"thanh_cong": False, "loi": "Thiếu tên dự án."}

    du_an_moi = {
        "id": _tao_id(),
        "ten": ten_du_an,
        "chu_so_huu": ten_tk,
        "ngay_tao": int(time.time()),
    }

    if not luu_du_an(du_an_moi):
        return {"thanh_cong": False, "loi": "Không lưu được dự án."}

    _ghi_log("dai-nao", f"Tạo dự án '{ten_du_an}' cho tài khoản {ten_tk}")
    return {"thanh_cong": True, "du_an": du_an_moi}


def xoa_du_an(du_lieu):
    """
    Xóa dự án theo id.
    du_lieu: { id }
    Chỉ cho phép xóa dự án thuộc về tài khoản hiện tại.
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": False, "loi": "Chưa đăng nhập."}

    id_xoa = du_lieu.get("id")
    if not id_xoa:
        return {"thanh_cong": False, "loi": "Thiếu id dự án."}

    du_an = lay_du_an(id_xoa)
    if not du_an:
        return {"thanh_cong": False, "loi": "Không tìm thấy dự án."}

    # Chỉ xóa được dự án của chính mình
    if du_an.get("chu_so_huu") != ten_tk:
        return {"thanh_cong": False, "loi": "Không có quyền xóa dự án này."}

    if not xoa_du_an_theo_id(id_xoa):
        return {"thanh_cong": False, "loi": "Không xóa được dự án."}

    _ghi_log("dai-nao", f"Xóa dự án id={id_xoa} của tài khoản {ten_tk}")
    return {"thanh_cong": True}


# ----------------------------------------------------------------
# CHAT NHANH
# ----------------------------------------------------------------
def lay_danh_sach_chat_nhanh():
    """Trả danh sách chat nhanh của tài khoản hiện tại."""
    ten = _lay_ten_dang_nhap()
    if not ten:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_chat_nhanh_cua(ten)
    return {"thanh_cong": True, "danh_sach": danh_sach or []}


def tao_chat_nhanh(du_lieu):
    """
    Tạo chat nhanh mới.
    du_lieu: { ten } — nếu không có tên, mặc định "Chat mới".
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": False, "loi": "Chưa đăng nhập."}

    ten_chat = (du_lieu.get("ten") or "Chat mới").strip()

    chat_moi = {
        "id": _tao_id(),
        "ten": ten_chat,
        "chu_so_huu": ten_tk,
        "ngay_tao": int(time.time()),
    }

    if not luu_chat_nhanh(chat_moi):
        return {"thanh_cong": False, "loi": "Không lưu được chat."}

    _ghi_log("dai-nao", f"Tạo chat nhanh '{ten_chat}' cho tài khoản {ten_tk}")
    return {"thanh_cong": True, "chat": chat_moi}


def xoa_chat_nhanh(du_lieu):
    """
    Xóa chat nhanh theo id.
    du_lieu: { id }
    Chỉ cho phép xóa chat thuộc về tài khoản hiện tại.
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": False, "loi": "Chưa đăng nhập."}

    id_xoa = du_lieu.get("id")
    if not id_xoa:
        return {"thanh_cong": False, "loi": "Thiếu id chat."}

    # Xóa theo id + chủ sở hữu để chắc chắn đúng người
    if not xoa_chat_nhanh_theo_id(id_xoa, ten_tk):
        return {"thanh_cong": False, "loi": "Không tìm thấy chat."}

    _ghi_log("dai-nao", f"Xóa chat nhanh id={id_xoa} của tài khoản {ten_tk}")
    return {"thanh_cong": True}


# ----------------------------------------------------------------
# CHAT MỚI (alias của chat nhanh)
# ----------------------------------------------------------------
def tao_chat_moi(du_lieu):
    """
    Tạo cuộc trò chuyện mới.
    Về bản chất giống tao_chat_nhanh, chỉ khác tên hàm cho rõ ngữ nghĩa.
    """
    return tao_chat_nhanh(du_lieu)
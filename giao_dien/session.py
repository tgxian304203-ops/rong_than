"""
session.py - Quản lý dự án + chat nhanh + chat mới Rồng Thần.
------------------------------------------------------------
ĐÃ SỬA:
    - Chat nhanh tài khoản: giới hạn 10 chat gần nhất.
      Khi vượt 10 → xóa chat cũ nhất.
    - Dự án: KHÔNG tự xóa, chỉ xóa khi user bấm [X].
    - Khách: trả về tạm, app.js tự lưu localStorage.

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
# HẰNG SỐ
# ----------------------------------------------------------------
GIOI_HAN_CHAT_NHANH = 10
CHU_SO_HUU_KHACH = "khach"


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
    return phien_flask.get("ten_dang_nhap")


# ================================================================
# DỰ ÁN — KHÔNG giới hạn, KHÔNG tự xóa
# ================================================================
def lay_danh_sach_du_an():
    ten = _lay_ten_dang_nhap()
    if not ten:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_du_an_cua(ten) or []
    # Sắp xếp mới nhất lên đầu
    danh_sach.sort(key=lambda d: d.get("ngay_tao", 0), reverse=True)
    return {"thanh_cong": True, "danh_sach": danh_sach}


def tao_du_an(du_lieu):
    ten_tk = _lay_ten_dang_nhap()

    ten_du_an = (du_lieu.get("ten") or "").strip()
    if not ten_du_an:
        return {"thanh_cong": False, "loi": "Thiếu tên dự án."}

    du_an_moi = {
        "id": _tao_id(),
        "ten": ten_du_an,
        "ngay_tao": int(time.time()),
    }

    # Khách → trả tạm, KHÔNG lưu kho
    if not ten_tk:
        du_an_moi["chu_so_huu"] = CHU_SO_HUU_KHACH
        du_an_moi["tam"] = True
        _ghi_log("dai-nao", f"Khách tạo dự án tạm '{ten_du_an}'")
        return {"thanh_cong": True, "du_an": du_an_moi, "tam": True}

    # Tài khoản → lưu kho 1
    du_an_moi["chu_so_huu"] = ten_tk
    du_an_moi["tam"] = False

    if not luu_du_an(du_an_moi):
        return {"thanh_cong": False, "loi": "Không lưu được dự án."}

    _ghi_log("dai-nao", f"Tạo dự án '{ten_du_an}' cho {ten_tk}")
    return {"thanh_cong": True, "du_an": du_an_moi}


def xoa_du_an(du_lieu):
    """
    Xóa dự án — CHỈ khi user bấm [X].
    Không có giới hạn, không tự xóa.
    """
    ten_tk = _lay_ten_dang_nhap()
    id_xoa = du_lieu.get("id")

    if not id_xoa:
        return {"thanh_cong": False, "loi": "Thiếu id dự án."}

    if not ten_tk:
        return {"thanh_cong": True}

    du_an = lay_du_an(id_xoa)
    if not du_an:
        return {"thanh_cong": True}

    if du_an.get("chu_so_huu") != ten_tk:
        return {"thanh_cong": False, "loi": "Không có quyền xóa dự án này."}

    if not xoa_du_an_theo_id(id_xoa):
        return {"thanh_cong": False, "loi": "Không xóa được dự án."}

    _ghi_log("dai-nao", f"Xóa dự án id={id_xoa} của {ten_tk}")
    return {"thanh_cong": True}


# ================================================================
# CHAT NHANH — giới hạn 10, tự xóa cũ nhất
# ================================================================
def lay_danh_sach_chat_nhanh():
    ten = _lay_ten_dang_nhap()
    if not ten:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_chat_nhanh_cua(ten) or []
    danh_sach.sort(key=lambda c: c.get("ngay_tao", 0), reverse=True)
    return {"thanh_cong": True, "danh_sach": danh_sach}


def tao_chat_nhanh(du_lieu):
    ten_tk = _lay_ten_dang_nhap()
    ten_chat = (du_lieu.get("ten") or "Chat mới").strip()

    chat_moi = {
        "id": _tao_id(),
        "ten": ten_chat,
        "ngay_tao": int(time.time()),
    }

    # Khách → trả tạm
    if not ten_tk:
        chat_moi["chu_so_huu"] = CHU_SO_HUU_KHACH
        chat_moi["tam"] = True
        _ghi_log("dai-nao", f"Khách tạo chat tạm '{ten_chat}'")
        return {"thanh_cong": True, "chat": chat_moi, "tam": True}

    # Tài khoản → kiểm tra giới hạn 10
    chat_moi["chu_so_huu"] = ten_tk
    chat_moi["tam"] = False

    # Đếm số chat hiện có (trước khi thêm)
    danh_sach_hien_co = lay_danh_sach_chat_nhanh_cua(ten_tk) or []
    if len(danh_sach_hien_co) >= GIOI_HAN_CHAT_NHANH:
        # Tìm chat cũ nhất (ngay_tao nhỏ nhất) và xóa
        danh_sach_hien_co.sort(key=lambda c: c.get("ngay_tao", 0))
        so_can_xoa = len(danh_sach_hien_co) - GIOI_HAN_CHAT_NHANH + 1
        for i in range(so_can_xoa):
            chat_cu = danh_sach_hien_co[i]
            xoa_chat_nhanh_theo_id(chat_cu.get("id"), ten_tk)
            _ghi_log("dai-nao",
                     f"Vượt giới hạn {GIOI_HAN_CHAT_NHANH} chat. "
                     f"Xóa chat cũ: {chat_cu.get('id')}")

    if not luu_chat_nhanh(chat_moi):
        return {"thanh_cong": False, "loi": "Không lưu được chat."}

    _ghi_log("dai-nao", f"Tạo chat nhanh '{ten_chat}' cho {ten_tk}")
    return {"thanh_cong": True, "chat": chat_moi}


def xoa_chat_nhanh(du_lieu):
    """
    Xóa chat nhanh — CHỈ khi user bấm [X].
    """
    ten_tk = _lay_ten_dang_nhap()
    id_xoa = du_lieu.get("id")

    if not id_xoa:
        return {"thanh_cong": False, "loi": "Thiếu id chat."}

    if not ten_tk:
        return {"thanh_cong": True}

    if not xoa_chat_nhanh_theo_id(id_xoa, ten_tk):
        return {"thanh_cong": True}

    _ghi_log("dai-nao", f"Xóa chat nhanh id={id_xoa} của {ten_tk}")
    return {"thanh_cong": True}


# ================================================================
# CHAT MỚI (alias)
# ================================================================
def tao_chat_moi(du_lieu):
    return tao_chat_nhanh(du_lieu)
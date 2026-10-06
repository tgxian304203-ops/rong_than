"""
session.py - Quản lý dự án + chat nhanh + trò chuyện trong dự án.
------------------------------------------------------------
ĐÃ SỬA: Thêm trò chuyện trong dự án.
    - Mỗi dự án có nhiều trò chuyện.
    - Mỗi trò chuyện có nhiều tin nhắn.
    - Trò chuyện trong các dự án khác nhau hoàn toàn.

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
    luu_tro_chuyen,
    lay_danh_sach_tro_chuyen_cua,
    lay_tro_chuyen,
    xoa_tro_chuyen_theo_id,
    luu_tin_nhan_tro_chuyen,
    lay_tin_nhan_tro_chuyen_cua,
)


GIOI_HAN_CHAT_NHANH = 10
CHU_SO_HUU_KHACH = "khach"


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _tao_id():
    return "id-" + secrets.token_hex(8)


def _lay_ten_dang_nhap():
    return phien_flask.get("ten_dang_nhap")


# ================================================================
# DỰ ÁN
# ================================================================
def lay_danh_sach_du_an():
    ten = _lay_ten_dang_nhap()
    if not ten:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_du_an_cua(ten) or []
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

    if not ten_tk:
        du_an_moi["chu_so_huu"] = CHU_SO_HUU_KHACH
        du_an_moi["tam"] = True
        return {"thanh_cong": True, "du_an": du_an_moi, "tam": True}

    du_an_moi["chu_so_huu"] = ten_tk
    du_an_moi["tam"] = False

    if not luu_du_an(du_an_moi):
        return {"thanh_cong": False, "loi": "Không lưu được dự án."}

    return {"thanh_cong": True, "du_an": du_an_moi}


def xoa_du_an(du_lieu):
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
        return {"thanh_cong": False, "loi": "Không có quyền."}

    if not xoa_du_an_theo_id(id_xoa):
        return {"thanh_cong": False, "loi": "Không xóa được."}

    return {"thanh_cong": True}


# ================================================================
# CHAT NHANH (giới hạn 10)
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

    if not ten_tk:
        chat_moi["chu_so_huu"] = CHU_SO_HUU_KHACH
        chat_moi["tam"] = True
        return {"thanh_cong": True, "chat": chat_moi, "tam": True}

    chat_moi["chu_so_huu"] = ten_tk
    chat_moi["tam"] = False

    # Giới hạn 10
    danh_sach_hien_co = lay_danh_sach_chat_nhanh_cua(ten_tk) or []
    if len(danh_sach_hien_co) >= GIOI_HAN_CHAT_NHANH:
        danh_sach_hien_co.sort(key=lambda c: c.get("ngay_tao", 0))
        so_can_xoa = len(danh_sach_hien_co) - GIOI_HAN_CHAT_NHANH + 1
        for i in range(so_can_xoa):
            xoa_chat_nhanh_theo_id(danh_sach_hien_co[i].get("id"), ten_tk)

    if not luu_chat_nhanh(chat_moi):
        return {"thanh_cong": False, "loi": "Không lưu được."}

    return {"thanh_cong": True, "chat": chat_moi}


def xoa_chat_nhanh(du_lieu):
    ten_tk = _lay_ten_dang_nhap()
    id_xoa = du_lieu.get("id")
    if not id_xoa:
        return {"thanh_cong": False, "loi": "Thiếu id."}
    if not ten_tk:
        return {"thanh_cong": True}

    xoa_chat_nhanh_theo_id(id_xoa, ten_tk)
    return {"thanh_cong": True}


# ================================================================
# TRÒ CHUYỆN TRONG DỰ ÁN
# ================================================================
def tao_tro_chuyen(du_lieu):
    """
    Tạo trò chuyện mới trong dự án.
    du_lieu: { id_du_an, ten }
    """
    ten_tk = _lay_ten_dang_nhap()
    id_du_an = du_lieu.get("id_du_an")
    ten_tro = (du_lieu.get("ten") or "Trò chuyện mới").strip()

    if not id_du_an:
        return {"thanh_cong": False, "loi": "Thiếu id dự án."}

    # Tài khoản: kiểm tra dự án thuộc mình
    if ten_tk:
        du_an = lay_du_an(id_du_an)
        if not du_an:
            return {"thanh_cong": False, "loi": "Không tìm thấy dự án."}
        if du_an.get("chu_so_huu") != ten_tk:
            return {"thanh_cong": False, "loi": "Không có quyền."}
        chu_so_huu = ten_tk
    else:
        chu_so_huu = CHU_SO_HUU_KHACH

    tro_moi = {
        "id": _tao_id(),
        "id_du_an": id_du_an,
        "ten": ten_tro,
        "chu_so_huu": chu_so_huu,
        "ngay_tao": int(time.time()),
    }

    # Khách → chỉ trả tạm, không lưu kho
    if not ten_tk:
        tro_moi["tam"] = True
        return {"thanh_cong": True, "tro_chuyen": tro_moi, "tam": True}

    if not luu_tro_chuyen(tro_moi):
        return {"thanh_cong": False, "loi": "Không lưu được."}

    return {"thanh_cong": True, "tro_chuyen": tro_moi}


def lay_danh_sach_tro_chuyen():
    """
    Lấy danh sách trò chuyện của 1 dự án.
    Query string: ?id_du_an=xxx
    """
    from flask import request
    id_du_an = request.args.get("id_du_an")
    if not id_du_an:
        return {"thanh_cong": False, "loi": "Thiếu id dự án."}

    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_tro_chuyen_cua(id_du_an, ten_tk) or []
    danh_sach.sort(key=lambda t: t.get("ngay_tao", 0), reverse=True)
    return {"thanh_cong": True, "danh_sach": danh_sach}


def xoa_tro_chuyen(du_lieu):
    ten_tk = _lay_ten_dang_nhap()
    id_tro = du_lieu.get("id_tro_chuyen")
    if not id_tro:
        return {"thanh_cong": False, "loi": "Thiếu id."}
    if not ten_tk:
        return {"thanh_cong": True}

    xoa_tro_chuyen_theo_id(id_tro, ten_tk)
    return {"thanh_cong": True}


# ================================================================
# TIN NHẮN TRONG TRÒ CHUYỆN
# ================================================================
def luu_tin_nhan(du_lieu):
    """
    Lưu 1 tin nhắn vào trò chuyện.
    du_lieu: { id_du_an, id_tro_chuyen, vai_tro, noi_dung }
    """
    ten_tk = _lay_ten_dang_nhap()
    id_du_an = du_lieu.get("id_du_an")
    id_tro = du_lieu.get("id_tro_chuyen")
    vai_tro = du_lieu.get("vai_tro") or "nguoi"
    noi_dung = (du_lieu.get("noi_dung") or "").strip()

    if not id_du_an or not id_tro or not noi_dung:
        return {"thanh_cong": False, "loi": "Thiếu thông tin."}

    # Khách → không lưu server (client tự lưu localStorage)
    if not ten_tk:
        return {"thanh_cong": True, "tam": True}

    tin = {
        "id": _tao_id(),
        "id_du_an": id_du_an,
        "id_tro_chuyen": id_tro,
        "chu_so_huu": ten_tk,
        "vai_tro": vai_tro,
        "noi_dung": noi_dung,
        "thoi_gian": int(time.time()),
    }

    if not luu_tin_nhan_tro_chuyen(tin):
        return {"thanh_cong": False, "loi": "Không lưu được."}

    return {"thanh_cong": True, "tin_nhan": tin}


def lay_tin_nhan():
    """
    Lấy tin nhắn của 1 trò chuyện.
    Query: ?id_du_an=xxx&id_tro_chuyen=yyy
    """
    from flask import request
    id_du_an = request.args.get("id_du_an")
    id_tro = request.args.get("id_tro_chuyen")
    if not id_du_an or not id_tro:
        return {"thanh_cong": False, "loi": "Thiếu thông tin."}

    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_tin_nhan_tro_chuyen_cua(id_du_an, id_tro, ten_tk) or []
    danh_sach.sort(key=lambda t: t.get("thoi_gian", 0))
    return {"thanh_cong": True, "danh_sach": danh_sach}


# ================================================================
# CHAT MỚI (alias)
# ================================================================
def tao_chat_moi(du_lieu):
    return tao_chat_nhanh(du_lieu)
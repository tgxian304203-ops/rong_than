"""
session.py - Quản lý dự án + chat nhanh + trò chuyện trong dự án.
------------------------------------------------------------
ĐÃ SỬA:
    - ngay_tao dùng mili giây để sort chính xác.
    - Chat nhanh mới nhất lên đầu, vượt 10 xóa cũ nhất.
    - Xóa trò chuyện → xóa luôn ảnh/file GridFS.
    - Tạo trò chuyện: nếu không tìm thấy dự án trong DB → tự lưu lại.
    - Thêm hàm lay_tin_nhan_chat_nhanh để load chat cũ.
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
    cap_nhat_ten_chat_nhanh,
    xoa_file_theo_tro_chuyen,
    lay_tin_nhan_chat_nhanh,
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


def _bay_giay():
    return int(time.time() * 1000)


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
        "ngay_tao": _bay_giay(),
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
# CHAT NHANH
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
        "ngay_tao": _bay_giay(),
    }

    if not ten_tk:
        chat_moi["chu_so_huu"] = CHU_SO_HUU_KHACH
        chat_moi["tam"] = True
        return {"thanh_cong": True, "chat": chat_moi, "tam": True}

    chat_moi["chu_so_huu"] = ten_tk
    chat_moi["tam"] = False

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


def doi_ten_chat_nhanh(du_lieu):
    ten_tk = _lay_ten_dang_nhap()
    id_chat = du_lieu.get("id")
    ten_moi = (du_lieu.get("ten") or "").strip()

    if not id_chat or not ten_moi:
        return {"thanh_cong": False, "loi": "Thiếu thông tin."}

    if not ten_tk:
        return {"thanh_cong": True, "tam": True}

    if not cap_nhat_ten_chat_nhanh(id_chat, ten_tk, ten_moi):
        return {"thanh_cong": False, "loi": "Không cập nhật được."}

    return {"thanh_cong": True}


def lay_tin_nhan_chat_nhanh_cua(id_chat):
    """
    Lấy tin nhắn cũ của 1 chat nhanh.
    Trả về { thanh_cong, danh_sach }.
    """
    if not id_chat:
        return {"thanh_cong": False, "loi": "Thiếu id chat."}

    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_tin_nhan_chat_nhanh(id_chat, ten_tk) or []
    return {"thanh_cong": True, "danh_sach": danh_sach}


# ================================================================
# TRÒ CHUYỆN TRONG DỰ ÁN
# ================================================================
def _dam_bao_du_an_ton_tai(id_du_an, ten_tk):
    """
    Đảm bảo dự án có trong DB.
    Nếu chưa có (do khách tạo trước khi đăng nhập) → lưu lại.
    """
    du_an = lay_du_an(id_du_an)
    if du_an:
        return du_an
    du_an_moi = {
        "id": id_du_an,
        "ten": "Dự án đã khôi phục",
        "chu_so_huu": ten_tk,
        "ngay_tao": _bay_giay(),
        "tam": False,
    }
    if luu_du_an(du_an_moi):
        return du_an_moi
    return None


def tao_tro_chuyen(du_lieu):
    ten_tk = _lay_ten_dang_nhap()
    id_du_an = du_lieu.get("id_du_an")
    ten_tro = (du_lieu.get("ten") or "Trò chuyện mới").strip()

    if not id_du_an:
        return {"thanh_cong": False, "loi": "Thiếu id dự án."}

    if ten_tk:
        du_an = _dam_bao_du_an_ton_tai(id_du_an, ten_tk)
        if not du_an:
            return {"thanh_cong": False, "loi": "Không thể tạo/lưu dự án."}
        chu_so_huu = ten_tk
    else:
        chu_so_huu = CHU_SO_HUU_KHACH

    tro_moi = {
        "id": _tao_id(),
        "id_du_an": id_du_an,
        "ten": ten_tro,
        "chu_so_huu": chu_so_huu,
        "ngay_tao": _bay_giay(),
    }

    if not ten_tk:
        tro_moi["tam"] = True
        return {"thanh_cong": True, "tro_chuyen": tro_moi, "tam": True}

    if not luu_tro_chuyen(tro_moi):
        return {"thanh_cong": False, "loi": "Không lưu được."}

    return {"thanh_cong": True, "tro_chuyen": tro_moi}


def lay_danh_sach_tro_chuyen():
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

    try:
        xoa_file_theo_tro_chuyen(id_tro, ten_tk)
    except Exception:
        pass

    xoa_tro_chuyen_theo_id(id_tro, ten_tk)
    return {"thanh_cong": True}


# ================================================================
# TIN NHẮN TRONG TRÒ CHUYỆN
# ================================================================
def luu_tin_nhan(du_lieu):
    ten_tk = _lay_ten_dang_nhap()
    id_du_an = du_lieu.get("id_du_an")
    id_tro = du_lieu.get("id_tro_chuyen")
    vai_tro = du_lieu.get("vai_tro") or "nguoi"
    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    urls_anh = du_lieu.get("urls_anh") or []
    urls_file = du_lieu.get("urls_file") or []

    if not id_du_an or not id_tro:
        return {"thanh_cong": False, "loi": "Thiếu thông tin."}

    if not noi_dung and not urls_anh and not urls_file:
        return {"thanh_cong": False, "loi": "Không có nội dung."}

    if not ten_tk:
        return {"thanh_cong": True, "tam": True}

    tin = {
        "id": _tao_id(),
        "id_du_an": id_du_an,
        "id_tro_chuyen": id_tro,
        "chu_so_huu": ten_tk,
        "vai_tro": vai_tro,
        "noi_dung": noi_dung,
        "thoi_gian": _bay_giay(),
    }
    if urls_anh:
        tin["urls_anh"] = list(urls_anh)
    if urls_file:
        tin["urls_file"] = list(urls_file)

    if not luu_tin_nhan_tro_chuyen(tin):
        return {"thanh_cong": False, "loi": "Không lưu được."}

    return {"thanh_cong": True, "tin_nhan": tin}


def lay_tin_nhan():
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
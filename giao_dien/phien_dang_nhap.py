"""
phien_dang_nhap.py - Quản lý phiên đăng nhập Rồng Thần.

Nhiệm vụ:
    - luu_phien(ten_dang_nhap): tạo phiên mới, lưu kho 1 + Flask session.
    - xoa_phien(): xóa phiên hiện tại khỏi kho 1 + Flask session.
    - lay_phien(): lấy thông tin phiên hiện tại.
    - da_dang_nhap(): kiểm tra đã đăng nhập chưa.

Quy tắc:
    - Phiên lưu vào kho 1 (collection phien_dang_nhap).
    - TTL 7 ngày — MongoDB tự xóa phiên hết hạn.
    - Đồng bộ với Flask session để kiểm tra nhanh không cần query.
    - Token phiên sinh ngẫu nhiên bằng secrets.token_urlsafe(32).

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import time
import secrets

from flask import session as phien_flask

# ----------------------------------------------------------------
# IMPORT TẦNG DỮ LIỆU
# ----------------------------------------------------------------
from dai_nao.ghi_nho import (
    luu_phien_dang_nhap,
    lay_phien_dang_nhap,
    xoa_phien_dang_nhap,
    gia_han_phien_dang_nhap,
)


# ----------------------------------------------------------------
# HẰNG SỐ
# ----------------------------------------------------------------
THOI_GIAN_PHIEN = 7 * 24 * 60 * 60  # 7 ngày (giây)

KHOA_TOKEN = "token_phien"
KHOA_TEN = "ten_dang_nhap"
KHOA_DA_DANG_NHAP = "da_dang_nhap"
KHOA_THOI_GIAN = "thoi_gian_dang_nhap"


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
# SINH TOKEN PHIÊN
# ----------------------------------------------------------------
def _tao_token():
    """Sinh token phiên ngẫu nhiên 32 byte URL-safe."""
    return secrets.token_urlsafe(32)


# ----------------------------------------------------------------
# LƯU PHIÊN
# ----------------------------------------------------------------
def luu_phien(ten_dang_nhap):
    """
    Tạo phiên đăng nhập mới.
    - Lưu vào kho 1 (collection phien_dang_nhap).
    - Lưu vào Flask session để kiểm tra nhanh.

    Trả về: { thanh_cong, token? }
    """
    if not ten_dang_nhap:
        return {"thanh_cong": False, "loi": "Thiếu tên đăng nhập."}

    token = _tao_token()
    thoi_gian = int(time.time())

    phien_moi = {
        "token": token,
        "ten_dang_nhap": ten_dang_nhap,
        "thoi_gian_tao": thoi_gian,
        "thoi_gian_het_han": thoi_gian + THOI_GIAN_PHIEN,
    }

    if not luu_phien_dang_nhap(phien_moi):
        return {"thanh_cong": False, "loi": "Không lưu được phiên."}

    # Đồng bộ vào Flask session
    phien_flask[KHOA_DA_DANG_NHAP] = True
    phien_flask[KHOA_TEN] = ten_dang_nhap
    phien_flask[KHOA_TOKEN] = token
    phien_flask[KHOA_THOI_GIAN] = thoi_gian

    _ghi_log("dai-nao", f"Tạo phiên đăng nhập cho {ten_dang_nhap}")
    return {"thanh_cong": True, "token": token}


# ----------------------------------------------------------------
# XÓA PHIÊN
# ----------------------------------------------------------------
def xoa_phien():
    """
    Xóa phiên đăng nhập hiện tại khỏi kho 1 + Flask session.
    """
    token = phien_flask.get(KHOA_TOKEN)
    ten = phien_flask.get(KHOA_TEN)

    if token:
        xoa_phien_dang_nhap(token)

    phien_flask.clear()

    if ten:
        _ghi_log("dai-nao", f"Đăng xuất: {ten}")

    return {"thanh_cong": True}


# ----------------------------------------------------------------
# LẤY PHIÊN
# ----------------------------------------------------------------
def lay_phien():
    """
    Lấy thông tin phiên hiện tại từ Flask session.
    Kiểm tra lại với kho 1 để chắc chắn phiên còn hiệu lực.
    """
    token = phien_flask.get(KHOA_TOKEN)
    ten = phien_flask.get(KHOA_TEN)

    if not token or not ten:
        return {"da_dang_nhap": False}

    # Kiểm tra lại với kho 1 (phòng khi phiên đã bị xóa từ nơi khác)
    phien_db = lay_phien_dang_nhap(token)
    if not phien_db:
        # Phiên không còn trong kho — xóa Flask session
        phien_flask.clear()
        return {"da_dang_nhap": False}

    # Kiểm tra hết hạn (phòng khi TTL chưa kịp xóa)
    if phien_db.get("thoi_gian_het_han", 0) < int(time.time()):
        xoa_phien_dang_nhap(token)
        phien_flask.clear()
        return {"da_dang_nhap": False}

    return {
        "da_dang_nhap": True,
        "ten_dang_nhap": ten,
        "thoi_gian_dang_nhap": phien_db.get("thoi_gian_tao", 0),
        "thoi_gian_het_han": phien_db.get("thoi_gian_het_han", 0),
    }


# ----------------------------------------------------------------
# KIỂM TRA ĐÃ ĐĂNG NHẬP
# ----------------------------------------------------------------
def da_dang_nhap():
    """Kiểm tra đã đăng nhập chưa (kiểm tra nhanh từ Flask session)."""
    return bool(phien_flask.get(KHOA_DA_DANG_NHAP) and phien_flask.get(KHOA_TEN))


# ----------------------------------------------------------------
# GIA HẠN PHIÊN
# ----------------------------------------------------------------
def gia_han_phien():
    """
    Gia hạn phiên hiện tại thêm 7 ngày.
    Dùng khi người dùng hoạt động — tránh bị đăng xuất giữa chừng.
    """
    token = phien_flask.get(KHOA_TOKEN)
    if not token:
        return {"thanh_cong": False, "loi": "Không có phiên để gia hạn."}

    thoi_gian_moi = int(time.time()) + THOI_GIAN_PHIEN
    if not gia_han_phien_dang_nhap(token, thoi_gian_moi):
        return {"thanh_cong": False, "loi": "Không gia hạn được phiên."}

    return {"thanh_cong": True, "thoi_gian_het_han": thoi_gian_moi}
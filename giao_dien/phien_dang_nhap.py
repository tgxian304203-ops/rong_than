"""
phien_dang_nhap.py - Quản lý phiên đăng nhập.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho.
"""

import time
import secrets

from flask import session as phien_flask

from luu_tru.ghi_nho import (
    luu_phien_dang_nhap,
    lay_phien_dang_nhap,
    xoa_phien_dang_nhap,
    gia_han_phien_dang_nhap,
)


THOI_GIAN_PHIEN = 7 * 24 * 60 * 60

KHOA_TOKEN = "token_phien"
KHOA_TEN = "ten_dang_nhap"
KHOA_DA_DANG_NHAP = "da_dang_nhap"
KHOA_THOI_GIAN = "thoi_gian_dang_nhap"


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _tao_token():
    return secrets.token_urlsafe(32)


def luu_phien(ten_dang_nhap):
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

    phien_flask[KHOA_DA_DANG_NHAP] = True
    phien_flask[KHOA_TEN] = ten_dang_nhap
    phien_flask[KHOA_TOKEN] = token
    phien_flask[KHOA_THOI_GIAN] = thoi_gian

    _ghi_log("dai-nao", f"Tạo phiên đăng nhập cho {ten_dang_nhap}")
    return {"thanh_cong": True, "token": token}


def xoa_phien():
    token = phien_flask.get(KHOA_TOKEN)
    ten = phien_flask.get(KHOA_TEN)

    if token:
        xoa_phien_dang_nhap(token)

    phien_flask.clear()

    if ten:
        _ghi_log("dai-nao", f"Đăng xuất: {ten}")

    return {"thanh_cong": True}


def lay_phien():
    token = phien_flask.get(KHOA_TOKEN)
    ten = phien_flask.get(KHOA_TEN)

    if not token or not ten:
        return {"da_dang_nhap": False}

    phien_db = lay_phien_dang_nhap(token)
    if not phien_db:
        phien_flask.clear()
        return {"da_dang_nhap": False}

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


def da_dang_nhap():
    return bool(phien_flask.get(KHOA_DA_DANG_NHAP) and phien_flask.get(KHOA_TEN))


def gia_han_phien():
    token = phien_flask.get(KHOA_TOKEN)
    if not token:
        return {"thanh_cong": False, "loi": "Không có phiên để gia hạn."}

    thoi_gian_moi = int(time.time()) + THOI_GIAN_PHIEN
    if not gia_han_phien_dang_nhap(token, thoi_gian_moi):
        return {"thanh_cong": False, "loi": "Không gia hạn được phiên."}

    return {"thanh_cong": True, "thoi_gian_het_han": thoi_gian_moi}
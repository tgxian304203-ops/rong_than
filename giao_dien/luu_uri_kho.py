"""
luu_uri_kho.py - Lưu URI 2 kho MongoDB.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho.
"""

import re
import time

from flask import session as phien_flask

from luu_tru.ghi_nho import (
    luu_uri_kho_cua,
    lay_uri_kho_cua,
)


CHU_SO_HUU_KHACH = "khach"


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _lay_chu_so_huu():
    ten = phien_flask.get("ten_dang_nhap")
    if ten:
        return ten
    return CHU_SO_HUU_KHACH


def _kiem_tra_dinh_dang_uri(uri):
    if not uri or not isinstance(uri, str):
        return False
    return uri.startswith("mongodb://") or uri.startswith("mongodb+srv://")


def _che_mat_khau(uri):
    if not uri:
        return ""
    mau = r"^(mongodb(?:\+srv)?://[^:]+:)([^@]+)(@.+)$"
    khop = re.match(mau, uri)
    if khop:
        return khop.group(1) + "***" + khop.group(3)
    return uri


def luu_uri_kho(du_lieu):
    chu_so_huu = _lay_chu_so_huu()

    so_kho = du_lieu.get("kho")
    uri = (du_lieu.get("uri") or "").strip()

    if so_kho not in (1, 2):
        return {"thanh_cong": False, "loi": "Số kho phải là 1 hoặc 2."}

    if not uri:
        return {"thanh_cong": False, "loi": "Thiếu URI."}

    if not _kiem_tra_dinh_dang_uri(uri):
        return {
            "thanh_cong": False,
            "loi": "URI không đúng định dạng MongoDB. Phải bắt đầu bằng "
                   "'mongodb://' hoặc 'mongodb+srv://'.",
        }

    if not luu_uri_kho_cua(chu_so_huu, so_kho, uri):
        return {"thanh_cong": False, "loi": "Không lưu được URI."}

    _ghi_log("dai-nao", f"Lưu URI kho {so_kho} cho {chu_so_huu}")

    return {
        "thanh_cong": True,
        "kho": so_kho,
        "uri_da_che": _che_mat_khau(uri),
        "thoi_gian": int(time.time()),
    }


def lay_uri_kho():
    chu_so_huu = _lay_chu_so_huu()

    uri_kho_1 = lay_uri_kho_cua(chu_so_huu, 1) or ""
    uri_kho_2 = lay_uri_kho_cua(chu_so_huu, 2) or ""

    return {
        "thanh_cong": True,
        "kho_1": _che_mat_khau(uri_kho_1),
        "kho_2": _che_mat_khau(uri_kho_2),
    }
"""
luu_uri_kho.py - Lưu URI 2 kho MongoDB Rồng Thần.
------------------------------------------------------------
ĐÃ SỬA: Cho phép chế độ KHÁCH lưu URI kho.
    - Khách  : chu_so_huu = "khach"
    - Tài khoản: chu_so_huu = ten_dang_nhap

Nhiệm vụ:
    - luu_uri_kho(du_lieu): nhận { kho: 1|2, uri }, lưu vào kho 1.
    - lay_uri_kho(): trả URI đã lưu (che mật khẩu).

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import re
import time

from flask import session as phien_flask

from dai_nao.ghi_nho import (
    luu_uri_kho_cua,
    lay_uri_kho_cua,
)


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


# ----------------------------------------------------------------
# LƯU URI KHO
# ----------------------------------------------------------------
def luu_uri_kho(du_lieu):
    """
    Lưu URI kho MongoDB.
    KHÔNG yêu cầu đăng nhập — khách vẫn lưu được.
    du_lieu: { kho: 1|2, uri: "..." }
    """
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


# ----------------------------------------------------------------
# LẤY URI KHO
# ----------------------------------------------------------------
def lay_uri_kho():
    """
    Trả URI 2 kho đã lưu của chủ sở hữu hiện tại (đã che mật khẩu).
    """
    chu_so_huu = _lay_chu_so_huu()

    uri_kho_1 = lay_uri_kho_cua(chu_so_huu, 1) or ""
    uri_kho_2 = lay_uri_kho_cua(chu_so_huu, 2) or ""

    return {
        "thanh_cong": True,
        "kho_1": _che_mat_khau(uri_kho_1),
        "kho_2": _che_mat_khau(uri_kho_2),
    }
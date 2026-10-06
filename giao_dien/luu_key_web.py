"""
luu_key_web.py - Lưu + quản lý API Key tra web Rồng Thần.
------------------------------------------------------------
ĐÃ SỬA: Cho phép chế độ KHÁCH lưu key tra web.
    - Khách  : chu_so_huu = "khach"
    - Tài khoản: chu_so_huu = ten_dang_nhap

Nhiệm vụ:
    - luu_key_web(du_lieu): nhận key, nhận diện provider, lưu kho 1.
    - lay_danh_sach_key_web(): trả danh sách key tra web.
    - xoa_key_web(du_lieu): xóa 1 key theo id.
    - lay_quota_key_web(): lấy quota thật từ API.

Quy tắc:
    - Nhận diện provider bằng tiền tố key:
        + tvly-  → Tavily
        + brd-   → Bright Data
        + còn lại độ dài >= 20 → SERPJET (fallback)
    - Key lưu với loai_key = "tra_web".

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import time
import secrets

import requests
from flask import session as phien_flask

from dai_nao.ghi_nho import (
    luu_key_da_luu,
    lay_danh_sach_key_cua,
    lay_key_da_luu,
    xoa_key_da_luu,
    cap_nhat_quota_key,
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


def _tao_id():
    return "keyweb-" + secrets.token_hex(8)


def _nhan_dien_provider(key):
    """
    Nhận diện provider tra web dựa vào tiền tố + độ dài.
    Trả về: "Tavily" | "Bright Data" | "SERPJET" | None
    """
    k = (key or "").strip()
    kl = k.lower()

    if kl.startswith("tvly-"):
        return "Tavily"
    if kl.startswith("brd-"):
        return "Bright Data"
    # SERPJET dùng chuỗi hex dài
    if len(k) >= 20:
        return "SERPJET"
    return None


# ----------------------------------------------------------------
# LẤY QUOTA THẬT
# ----------------------------------------------------------------
def _lay_quota_serpjet(key):
    try:
        r = requests.get(
            "https://serpjet.com/api/v1/account",
            params={"api_key": key},
            timeout=10,
        )
        if r.status_code != 200:
            return 0 if r.status_code in (401, 403) else None
        du_lieu = r.json()
        da_dung = du_lieu.get("used", 0)
        tong = du_lieu.get("quota", 1000)
        if tong <= 0:
            return 100
        con_lai = max(0, tong - da_dung)
        return int(con_lai / tong * 100)
    except Exception:
        return None


def _lay_quota_tavily(key):
    try:
        r = requests.get(
            "https://api.tavily.com/usage",
            params={"api_key": key},
            timeout=10,
        )
        if r.status_code != 200:
            return 0 if r.status_code in (401, 403) else None
        du_lieu = r.json()
        da_dung = du_lieu.get("usage", 0)
        tong = du_lieu.get("limit", 1000)
        if tong <= 0:
            return 100
        con_lai = max(0, tong - da_dung)
        return int(con_lai / tong * 100)
    except Exception:
        return None


def _lay_quota_brightdata(key):
    try:
        r = requests.get(
            "https://api.brightdata.com/customer/balance",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if r.status_code != 200:
            return 0 if r.status_code in (401, 403) else None
        du_lieu = r.json()
        con_lai = du_lieu.get("balance", 0)
        tong = 5000
        if tong <= 0:
            return 100
        return int(min(100, con_lai / tong * 100))
    except Exception:
        return None


def _lay_quota(key, provider):
    if provider == "SERPJET":
        return _lay_quota_serpjet(key)
    if provider == "Tavily":
        return _lay_quota_tavily(key)
    if provider == "Bright Data":
        return _lay_quota_brightdata(key)
    return None


# ----------------------------------------------------------------
# LƯU KEY TRA WEB
# ----------------------------------------------------------------
def luu_key_web(du_lieu):
    """
    Lưu API Key tra web mới.
    KHÔNG yêu cầu đăng nhập.
    """
    chu_so_huu = _lay_chu_so_huu()

    key = (du_lieu.get("key") or "").strip()
    if not key:
        return {"thanh_cong": False, "loi": "Thiếu key."}

    provider = _nhan_dien_provider(key)
    if provider is None:
        return {
            "thanh_cong": False,
            "loi": "Không nhận diện được provider. Key phải là "
                   "Tavily (tvly-...), Bright Data (brd-...) hoặc SERPJET.",
        }

    # Lấy quota ban đầu (có thể None nếu API lỗi tạm thời)
    phan_tram = _lay_quota(key, provider)
    if phan_tram is None:
        phan_tram = 100

    key_moi = {
        "id": _tao_id(),
        "key": key,
        "provider": provider,
        "loai_key": "tra_web",
        "chu_so_huu": chu_so_huu,
        "phan_tram": phan_tram,
        "ngay_tao": int(time.time()),
        "lan_kiem_tra_cuoi": int(time.time()),
    }

    if not luu_key_da_luu(key_moi):
        return {"thanh_cong": False, "loi": "Không lưu được key."}

    _ghi_log("tra-web",
             f"Lưu key tra web provider={provider} cho {chu_so_huu}")

    return {
        "thanh_cong": True,
        "key": {
            "id": key_moi["id"],
            "provider": provider,
            "phan_tram": phan_tram,
        },
    }


# ----------------------------------------------------------------
# LẤY DANH SÁCH KEY TRA WEB
# ----------------------------------------------------------------
def lay_danh_sach_key_web():
    """
    Trả danh sách key tra web của chủ sở hữu hiện tại.
    """
    chu_so_huu = _lay_chu_so_huu()
    danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []

    ket_qua = []
    for k in danh_sach:
        if k.get("loai_key") != "tra_web":
            continue
        ket_qua.append({
            "id": k.get("id"),
            "provider": k.get("provider"),
            "ten": k.get("provider"),
            "phan_tram": k.get("phan_tram", 100),
        })

    return {"thanh_cong": True, "danh_sach": ket_qua}


# ----------------------------------------------------------------
# XÓA KEY TRA WEB
# ----------------------------------------------------------------
def xoa_key_web(du_lieu):
    """
    Xóa key tra web theo id.
    """
    chu_so_huu = _lay_chu_so_huu()

    id_xoa = du_lieu.get("id")
    if not id_xoa:
        return {"thanh_cong": False, "loi": "Thiếu id key."}

    key = lay_key_da_luu(id_xoa)
    if not key:
        return {"thanh_cong": False, "loi": "Không tìm thấy key."}

    if key.get("chu_so_huu") != chu_so_huu:
        return {"thanh_cong": False, "loi": "Không có quyền xóa key này."}

    if not xoa_key_da_luu(id_xoa):
        return {"thanh_cong": False, "loi": "Không xóa được key."}

    _ghi_log("tra-web", f"Xóa key tra web id={id_xoa} của {chu_so_huu}")
    return {"thanh_cong": True}


# ----------------------------------------------------------------
# LẤY QUOTA KEY TRA WEB
# ----------------------------------------------------------------
def lay_quota_key_web():
    """
    Lấy quota thật của từng key tra web từ API provider.
    """
    chu_so_huu = _lay_chu_so_huu()
    danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    ket_qua = []

    for k in danh_sach:
        if k.get("loai_key") != "tra_web":
            continue
        phan_tram_moi = _lay_quota(k.get("key"), k.get("provider"))
        if phan_tram_moi is not None:
            cap_nhat_quota_key(k.get("id"), phan_tram_moi)
        else:
            phan_tram_moi = k.get("phan_tram", 100)

        ket_qua.append({
            "id": k.get("id"),
            "provider": k.get("provider"),
            "ten": k.get("provider"),
            "phan_tram": phan_tram_moi,
        })

    return {"thanh_cong": True, "danh_sach": ket_qua}
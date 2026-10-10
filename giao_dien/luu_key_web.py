"""
luu_key_web.py - Lưu + quản lý API Key tra web.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho.
"""

import time
import secrets

import requests
from flask import session as phien_flask

from luu_tru.ghi_nho import (
    luu_key_da_luu,
    lay_danh_sach_key_web_cua,
    lay_key_da_luu,
    xoa_key_da_luu,
    cap_nhat_quota_key,
)


CHU_SO_HUU_KHACH = "khach"
LOAI_KEY_TRA_WEB = "tra_web"

BANG_PROVIDER = [
    {"tien_to": "sj_",   "provider": "SERPJET"},
    {"tien_to": "tvly-", "provider": "Tavily"},
    {"tien_to": "brd-",  "provider": "Bright Data"},
]


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


def _nhan_dien_provider(key):
    k = (key or "").strip()
    for muc in BANG_PROVIDER:
        if k.startswith(muc["tien_to"]):
            return muc["provider"]
    return None


def _tao_id():
    return "keyweb-" + secrets.token_hex(8)


def _lay_quota_tavily(key):
    try:
        r = requests.get(
            "https://api.tavily.com/usage",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if r.status_code in (401, 403):
            return 0
        if r.status_code != 200:
            return None
        du_lieu = r.json() or {}
        khoa = du_lieu.get("key") or {}
        gioi_han = khoa.get("limit")
        da_dung = khoa.get("usage", 0)
        if gioi_han and gioi_han > 0:
            con_lai = max(0, gioi_han - da_dung)
            return int(con_lai / gioi_han * 100)
        return 100
    except Exception:
        return None


def _lay_quota(key, provider):
    if provider == "Tavily":
        return _lay_quota_tavily(key)
    return 100


def luu_key_web(du_lieu):
    chu_so_huu = _lay_chu_so_huu()

    key = (du_lieu.get("key") or "").strip()
    if not key:
        return {"thanh_cong": False, "loi": "Thiếu key."}

    provider = _nhan_dien_provider(key)
    if provider is None:
        return {
            "thanh_cong": False,
            "loi": "Không nhận diện được provider. Key phải bắt đầu bằng "
                   "'sj_' (SERPJET), 'tvly-' (Tavily) hoặc 'brd-' (Bright Data).",
        }

    phan_tram = _lay_quota(key, provider)
    if phan_tram is None:
        phan_tram = 100

    key_moi = {
        "id": _tao_id(),
        "key": key,
        "provider": provider,
        "loai_key": LOAI_KEY_TRA_WEB,
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


def lay_danh_sach_key_web():
    chu_so_huu = _lay_chu_so_huu()
    danh_sach = lay_danh_sach_key_web_cua(chu_so_huu) or []

    ket_qua = []
    for k in danh_sach:
        ket_qua.append({
            "id": k.get("id"),
            "provider": k.get("provider"),
            "ten": k.get("provider"),
            "phan_tram": k.get("phan_tram", 100),
        })

    return {"thanh_cong": True, "danh_sach": ket_qua}


def xoa_key_web(du_lieu):
    chu_so_huu = _lay_chu_so_huu()

    id_xoa = du_lieu.get("id")
    if not id_xoa:
        return {"thanh_cong": False, "loi": "Thiếu id key."}

    key = lay_key_da_luu(id_xoa)
    if not key:
        return {"thanh_cong": False, "loi": "Không tìm thấy key."}

    if key.get("chu_so_huu") != chu_so_huu:
        return {"thanh_cong": False, "loi": "Không có quyền xóa key này."}

    if key.get("loai_key") != LOAI_KEY_TRA_WEB:
        return {"thanh_cong": False, "loi": "Key này không phải key tra web."}

    if not xoa_key_da_luu(id_xoa):
        return {"thanh_cong": False, "loi": "Không xóa được key."}

    _ghi_log("tra-web", f"Xóa key tra web id={id_xoa} của {chu_so_huu}")
    return {"thanh_cong": True}


def lay_quota_key_web():
    chu_so_huu = _lay_chu_so_huu()
    danh_sach = lay_danh_sach_key_web_cua(chu_so_huu) or []
    ket_qua = []

    for k in danh_sach:
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
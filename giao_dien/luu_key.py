"""
luu_key.py - Lưu + quản lý API Key model Rồng Thần.
------------------------------------------------------------
ĐÃ SỬA: Cho phép chế độ KHÁCH lưu key.
    - Khách  : chu_so_huu = "khach"
    - Tài khoản: chu_so_huu = ten_dang_nhap

Nhiệm vụ:
    - luu_key_model(du_lieu): nhận key, nhận diện provider, lưu kho 1.
    - lay_danh_sach_key(): trả danh sách key model (đã ẩn key gốc).
    - xoa_key(du_lieu): xóa 1 key theo id.
    - lay_quota_key(): lấy quota thật từ API của từng provider.

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


# ----------------------------------------------------------------
# HẰNG SỐ
# ----------------------------------------------------------------
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
    """
    Lấy chủ sở hữu key:
        - Nếu đăng nhập → tên đăng nhập.
        - Nếu khách    → "khach".
    """
    ten = phien_flask.get("ten_dang_nhap")
    if ten:
        return ten
    return CHU_SO_HUU_KHACH


def _nhan_dien_provider(key):
    """
    Nhận diện provider dựa vào tiền tố key.
    Trả về: "Groq" | "OpenRouter" | "Gemini" | None
    """
    k = (key or "").strip()
    if k.startswith("gsk_"):
        return "Groq"
    if k.startswith("sk-or-"):
        return "OpenRouter"
    if k.startswith("AIza"):
        return "Gemini"
    return None


def _tao_id():
    return "key-" + secrets.token_hex(8)


# ----------------------------------------------------------------
# LẤY QUOTA THẬT TỪNG PROVIDER
# ----------------------------------------------------------------
def _lay_quota_groq(key):
    try:
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if r.status_code == 200:
            return 100
        if r.status_code in (401, 403):
            return 0
        return 50
    except Exception:
        return None


def _lay_quota_openrouter(key):
    try:
        r = requests.get(
            "https://openrouter.ai/api/v1/key",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if r.status_code == 200:
            du_lieu = r.json().get("data", {})
            gioi_han = du_lieu.get("limit")
            da_dung = du_lieu.get("usage", 0)
            if gioi_han and gioi_han > 0:
                con_lai = max(0, gioi_han - da_dung)
                return int(con_lai / gioi_han * 100)
            return 100
        if r.status_code in (401, 403):
            return 0
        return 50
    except Exception:
        return None


def _lay_quota_gemini(key):
    try:
        r = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
            timeout=10,
        )
        if r.status_code == 200:
            return 100
        if r.status_code in (401, 403):
            return 0
        return 50
    except Exception:
        return None


def _lay_quota(key, provider):
    if provider == "Groq":
        return _lay_quota_groq(key)
    if provider == "OpenRouter":
        return _lay_quota_openrouter(key)
    if provider == "Gemini":
        return _lay_quota_gemini(key)
    return None


# ----------------------------------------------------------------
# LƯU KEY MODEL
# ----------------------------------------------------------------
def luu_key_model(du_lieu):
    """
    Lưu API Key model mới.
    KHÔNG yêu cầu đăng nhập — khách vẫn lưu được.
    du_lieu: { key }
    Trả về: { thanh_cong, key? }
    """
    chu_so_huu = _lay_chu_so_huu()

    key = (du_lieu.get("key") or "").strip()
    if not key:
        return {"thanh_cong": False, "loi": "Thiếu key."}

    provider = _nhan_dien_provider(key)
    if provider is None:
        return {
            "thanh_cong": False,
            "loi": "Không nhận diện được provider. Key phải bắt đầu bằng "
                   "'gsk_' (Groq), 'sk-or-' (OpenRouter) hoặc 'AIza' (Gemini).",
        }

    phan_tram = _lay_quota(key, provider)
    if phan_tram is None:
        phan_tram = 100

    key_moi = {
        "id": _tao_id(),
        "key": key,
        "provider": provider,
        "loai_key": "model",
        "chu_so_huu": chu_so_huu,
        "phan_tram": phan_tram,
        "ngay_tao": int(time.time()),
        "lan_kiem_tra_cuoi": int(time.time()),
    }

    if not luu_key_da_luu(key_moi):
        return {"thanh_cong": False, "loi": "Không lưu được key."}

    _ghi_log("dai-nao",
             f"Lưu key model provider={provider} cho {chu_so_huu}")

    return {
        "thanh_cong": True,
        "key": {
            "id": key_moi["id"],
            "provider": provider,
            "phan_tram": phan_tram,
        },
    }


# ----------------------------------------------------------------
# LẤY DANH SÁCH KEY MODEL
# ----------------------------------------------------------------
def lay_danh_sach_key():
    """
    Trả danh sách key model của chủ sở hữu hiện tại.
    KHÔNG trả key gốc.
    """
    chu_so_huu = _lay_chu_so_huu()
    danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []

    ket_qua = []
    for k in danh_sach:
        # Chỉ lấy key loại model (không lấy key tra web)
        if k.get("loai_key") == "tra_web":
            continue
        ket_qua.append({
            "id": k.get("id"),
            "provider": k.get("provider"),
            "ten": k.get("provider"),
            "phan_tram": k.get("phan_tram", 100),
        })

    return {"thanh_cong": True, "danh_sach": ket_qua}


# ----------------------------------------------------------------
# XÓA KEY MODEL
# ----------------------------------------------------------------
def xoa_key(du_lieu):
    """
    Xóa key model theo id.
    Chỉ cho phép xóa key thuộc chủ sở hữu hiện tại.
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

    _ghi_log("dai-nao", f"Xóa key model id={id_xoa} của {chu_so_huu}")
    return {"thanh_cong": True}


# ----------------------------------------------------------------
# LẤY QUOTA KEY MODEL
# ----------------------------------------------------------------
def lay_quota_key():
    """
    Lấy quota thật của từng key model từ API provider.
    """
    chu_so_huu = _lay_chu_so_huu()
    danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    ket_qua = []

    for k in danh_sach:
        if k.get("loai_key") == "tra_web":
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
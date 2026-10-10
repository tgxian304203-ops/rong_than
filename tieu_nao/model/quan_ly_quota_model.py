"""
quan_ly_quota_model.py - Quản lý quota key Model.

Nhiệm vụ:
    - Lấy quota thật từ API provider.
    - Cập nhật quota vào kho 1.
    - Lấy quota chi tiết.

Nguyên tắc:
    - Chỉ key loai_nao = tieu_boss.
    - Cập nhật quota mỗi 60 giây.
"""

import time

import requests


# ================================================================
# GHI LOG
# ================================================================
def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ================================================================
# HẰNG SỐ
# ================================================================
TIMEOUT = 10
LOAI_NAO_MODEL = "tieu_boss"


# ================================================================
# LẤY QUOTA GROQ
# ================================================================
def _lay_quota_groq(key):
    """Lấy quota Groq từ API."""
    ket_qua = {"phan_tram": None, "loai_quota": "phut"}

    if not key:
        return ket_qua

    try:
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=TIMEOUT,
        )

        if r.status_code == 200:
            ket_qua["phan_tram"] = 100
            return ket_qua
        if r.status_code in (401, 403):
            ket_qua["phan_tram"] = 0
            ket_qua["loai_quota"] = "key_sai"
            return ket_qua
        if r.status_code == 429:
            ket_qua["phan_tram"] = 0
            ket_qua["loai_quota"] = "het_quota"
            return ket_qua

        ket_qua["phan_tram"] = 50
        return ket_qua
    except Exception:
        return ket_qua


# ================================================================
# LẤY QUOTA OPENROUTER
# ================================================================
def _lay_quota_openrouter(key):
    """Lấy quota OpenRouter từ API."""
    ket_qua = {"phan_tram": None, "loai_quota": "ngay"}

    if not key:
        return ket_qua

    try:
        r = requests.get(
            "https://openrouter.ai/api/v1/key",
            headers={"Authorization": f"Bearer {key}"},
            timeout=TIMEOUT,
        )

        if r.status_code == 200:
            du_lieu = r.json().get("data", {})
            gioi_han = du_lieu.get("limit")
            da_dung = du_lieu.get("usage", 0)

            if gioi_han and gioi_han > 0:
                con_lai = max(0, gioi_han - da_dung)
                ket_qua["phan_tram"] = int(con_lai / gioi_han * 100)
            else:
                ket_qua["phan_tram"] = 100
            return ket_qua

        if r.status_code in (401, 403):
            ket_qua["phan_tram"] = 0
            ket_qua["loai_quota"] = "key_sai"
            return ket_qua
        if r.status_code == 429:
            ket_qua["phan_tram"] = 0
            ket_qua["loai_quota"] = "het_quota"
            return ket_qua

        ket_qua["phan_tram"] = 50
        return ket_qua
    except Exception:
        return ket_qua


# ================================================================
# LẤY QUOTA GEMINI
# ================================================================
def _lay_quota_gemini(key):
    """Lấy quota Gemini từ API."""
    ket_qua = {"phan_tram": None, "loai_quota": "phut"}

    if not key:
        return ket_qua

    try:
        r = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
            timeout=TIMEOUT,
        )

        if r.status_code == 200:
            ket_qua["phan_tram"] = 100
            return ket_qua
        if r.status_code in (401, 403):
            ket_qua["phan_tram"] = 0
            ket_qua["loai_quota"] = "key_sai"
            return ket_qua
        if r.status_code == 429:
            ket_qua["phan_tram"] = 0
            ket_qua["loai_quota"] = "het_quota"
            return ket_qua

        ket_qua["phan_tram"] = 50
        return ket_qua
    except Exception:
        return ket_qua


# ================================================================
# LẤY QUOTA THEO PROVIDER
# ================================================================
def lay_quota(provider, key):
    """Lấy quota hiện tại từ API provider."""
    if not provider or not key:
        return {"phan_tram": None, "loai_quota": ""}

    if provider == "Groq":
        return _lay_quota_groq(key)
    if provider == "OpenRouter":
        return _lay_quota_openrouter(key)
    if provider == "Gemini":
        return _lay_quota_gemini(key)

    return {"phan_tram": None, "loai_quota": ""}


# ================================================================
# CẬP NHẬT QUOTA
# ================================================================
def cap_nhat_quota(chu_so_huu):
    """Cập nhật quota cho tất cả key Model của user."""
    ket_qua = []

    if not chu_so_huu:
        return ket_qua

    try:
        from luu_tru.ghi_nho import (
            lay_danh_sach_key_cua,
            cap_nhat_quota_key,
        )
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    except Exception:
        return ket_qua

    for key in danh_sach:
        if key.get("loai_key") == "tra_web":
            continue
        if key.get("loai_nao") != LOAI_NAO_MODEL:
            continue

        provider = key.get("provider", "")
        key_id = key.get("id", "")
        key_str = key.get("key", "")

        kq = lay_quota(provider, key_str)
        phan_tram = kq.get("phan_tram")

        if phan_tram is not None:
            try:
                cap_nhat_quota_key(key_id, phan_tram)
            except Exception:
                pass

        ket_qua.append({
            "key_id": key_id,
            "provider": provider,
            "phan_tram": phan_tram,
            "loai_quota": kq.get("loai_quota", ""),
        })

    _ghi_log("tieu-nao", f"Cập nhật quota {len(ket_qua)} key Model")
    return ket_qua


# ================================================================
# MÀU QUOTA
# ================================================================
def lay_mau_quota(phan_tram):
    """Xác định màu theo phần trăm."""
    if phan_tram is None:
        return "khong_ro"
    if phan_tram >= 50:
        return "xanh"
    if phan_tram >= 20:
        return "vang"
    if phan_tram > 0:
        return "do"
    return "den"


def lay_class_quota(phan_tram):
    """Trả class CSS cho quota."""
    bang = {
        "xanh": "quota-xanh",
        "vang": "quota-vang",
        "do": "quota-do",
        "den": "quota-den",
        "khong_ro": "",
    }
    return bang.get(lay_mau_quota(phan_tram), "")


# ================================================================
# TỔNG HỢP
# ================================================================
def tong_hop_quota(chu_so_huu):
    """Tổng hợp quota trung bình."""
    chi_tiet = cap_nhat_quota(chu_so_huu)

    tat_ca = [
        k.get("phan_tram") for k in chi_tiet
        if k.get("phan_tram") is not None
    ]

    if not tat_ca:
        return {"phan_tram_tb": 100, "so_key": 0, "mau": "khong_ro"}

    phan_tram_tb = int(sum(tat_ca) / len(tat_ca))
    return {
        "phan_tram_tb": phan_tram_tb,
        "so_key": len(tat_ca),
        "mau": lay_mau_quota(phan_tram_tb),
    }


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat_quota(chu_so_huu):
    """Tạo chuỗi tóm tắt quota Model."""
    chi_tiet = cap_nhat_quota(chu_so_huu)
    if not chi_tiet:
        return "❌ Không có key Model."

    phan = ["📊 Model:"]
    for kq in chi_tiet:
        key_id = kq.get("key_id", "")[:8]
        phan_tram = kq.get("phan_tram")
        mau = lay_mau_quota(phan_tram)

        bieu_tuong = {
            "xanh": "🟢",
            "vang": "🟡",
            "do": "🔴",
            "den": "⚫",
            "khong_ro": "⚪",
        }.get(mau, "⚪")

        phan.append(f"  {bieu_tuong} {key_id}: {phan_tram}%")

    return "\n".join(phan)
"""
luu_key.py - Lưu + quản lý API Key model Rồng Thần.

Nhiệm vụ:
    - luu_key_model(du_lieu): nhận key, nhận diện provider, lưu vào kho 1.
    - lay_danh_sach_key(): trả danh sách key model (đã ẩn key gốc).
    - xoa_key(du_lieu): xóa 1 key theo id.
    - lay_quota_key(): lấy quota thật từ API của từng provider.

Quy tắc:
    - Mỗi key thuộc về tài khoản đang đăng nhập.
    - Key gốc KHÔNG trả về client — chỉ trả id, provider, phần trăm.
    - Nhận diện provider theo tiền tố key:
        + gsk_ → Groq
        + sk-or- → OpenRouter
        + AIza → Gemini
    - Quota lấy thật từ API provider.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import time

import requests
from flask import session as phien_flask

# ----------------------------------------------------------------
# IMPORT TẦNG DỮ LIỆU
# ----------------------------------------------------------------
from dai_nao.ghi_nho import (
    luu_key_da_luu,
    lay_danh_sach_key_cua,
    lay_key_da_luu,
    xoa_key_da_luu,
    cap_nhat_quota_key,
)


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
def _lay_ten_dang_nhap():
    """Lấy tên đăng nhập hiện tại từ Flask session."""
    return phien_flask.get("ten_dang_nhap")


def _nhan_dien_provider(key):
    """
    Nhận diện provider dựa vào tiền tố key.
    Trả về: "Groq" | "OpenRouter" | "Gemini" | "Không rõ"
    """
    k = (key or "").strip()
    if k.startswith("gsk_"):
        return "Groq"
    if k.startswith("sk-or-"):
        return "OpenRouter"
    if k.startswith("AIza"):
        return "Gemini"
    return "Không rõ"


def _tao_id():
    import secrets
    return "key-" + secrets.token_hex(8)


# ----------------------------------------------------------------
# LẤY QUOTA THẬT TỪNG PROVIDER
# ----------------------------------------------------------------
def _lay_quota_groq(key):
    """
    Groq: gọi GET /openai/v1/models để kiểm tra key còn hiệu lực.
    Quota Groq dựa trên rate limit — không có endpoint quota chính thức.
    Trả về % ước lượng: 100 nếu key hoạt động, 0 nếu key lỗi.
    """
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
        return 50  # trạng thái lạ
    except Exception:
        return None  # không lấy được


def _lay_quota_openrouter(key):
    """
    OpenRouter: GET /api/v1/key trả về thông tin key + giới hạn.
    """
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
            return 100  # không có giới hạn
        if r.status_code in (401, 403):
            return 0
        return 50
    except Exception:
        return None


def _lay_quota_gemini(key):
    """
    Gemini: gọi GET /v1beta/models để kiểm tra key còn hiệu lực.
    Gemini có giới hạn RPM/RPD nhưng không có endpoint quota chính thức.
    Trả về 100 nếu key hoạt động, 0 nếu key lỗi.
    """
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
    """Gọi hàm lấy quota tương ứng provider."""
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
    du_lieu: { key }
    Trả về: { thanh_cong, key? } — key trả về đã ẩn nội dung gốc.
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": False, "loi": "Chưa đăng nhập."}

    key = (du_lieu.get("key") or "").strip()
    if not key:
        return {"thanh_cong": False, "loi": "Thiếu key."}

    provider = _nhan_dien_provider(key)
    if provider == "Không rõ":
        return {
            "thanh_cong": False,
            "loi": "Không nhận diện được provider. Key phải bắt đầu bằng "
                   "'gsk_' (Groq), 'sk-or-' (OpenRouter) hoặc 'AIza' (Gemini).",
        }

    # Lấy quota ban đầu
    phan_tram = _lay_quota(key, provider)
    if phan_tram is None:
        phan_tram = 100  # lần đầu chưa kiểm tra được thì mặc định 100

    key_moi = {
        "id": _tao_id(),
        "key": key,
        "provider": provider,
        "chu_so_huu": ten_tk,
        "phan_tram": phan_tram,
        "ngay_tao": int(time.time()),
        "lan_kiem_tra_cuoi": int(time.time()),
    }

    if not luu_key_da_luu(key_moi):
        return {"thanh_cong": False, "loi": "Không lưu được key."}

    _ghi_log("dai-nao", f"Lưu key model provider={provider} cho tài khoản {ten_tk}")

    # Trả về bản đã ẩn key gốc
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
    Trả danh sách key model của tài khoản hiện tại.
    KHÔNG trả key gốc — chỉ id, provider, phần trăm.
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_key_cua(ten_tk) or []

    ket_qua = []
    for k in danh_sach:
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
    du_lieu: { id }
    Chỉ cho phép xóa key thuộc tài khoản hiện tại.
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": False, "loi": "Chưa đăng nhập."}

    id_xoa = du_lieu.get("id")
    if not id_xoa:
        return {"thanh_cong": False, "loi": "Thiếu id key."}

    key = lay_key_da_luu(id_xoa)
    if not key:
        return {"thanh_cong": False, "loi": "Không tìm thấy key."}

    if key.get("chu_so_huu") != ten_tk:
        return {"thanh_cong": False, "loi": "Không có quyền xóa key này."}

    if not xoa_key_da_luu(id_xoa):
        return {"thanh_cong": False, "loi": "Không xóa được key."}

    _ghi_log("dai-nao", f"Xóa key model id={id_xoa} của tài khoản {ten_tk}")
    return {"thanh_cong": True}


# ----------------------------------------------------------------
# LẤY QUOTA KEY MODEL (cập nhật thật từ API)
# ----------------------------------------------------------------
def lay_quota_key():
    """
    Lấy quota thật của từng key model từ API provider.
    Cập nhật vào kho 1, trả về danh sách mới.
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_key_cua(ten_tk) or []
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
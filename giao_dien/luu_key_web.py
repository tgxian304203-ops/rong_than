"""
luu_key_web.py - Lưu + quản lý API Key tra web Rồng Thần.

Nhiệm vụ:
    - luu_key_web(du_lieu): nhận key, nhận diện provider, lưu vào kho 1.
    - lay_danh_sach_key_web(): trả danh sách key tra web (đã ẩn key gốc).
    - xoa_key_web(du_lieu): xóa 1 key theo id.
    - lay_quota_key_web(): lấy quota thật từ API của từng provider.

Quy tắc:
    - Mỗi key thuộc về tài khoản đang đăng nhập.
    - Key gốc KHÔNG trả về client — chỉ trả id, provider, phần trăm.
    - Nhận diện provider bằng cách GỌI THỬ API:
        + Thử SERPJET trước.
        + Nếu không được, thử Tavily.
        + Nếu không được, thử Bright Data.
    - Key lưu vào collection key_da_luu với loai_key = "tra_web"
      (phân biệt với key model: loai_key = "model").
    - Quota lấy thật từ API provider.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import time
import secrets

import requests
from flask import session as phien_flask

# ----------------------------------------------------------------
# IMPORT TẦNG DỮ LIỆU
# ----------------------------------------------------------------
from dai_nao.ghi_nho import (
    luu_key_da_luu,
    lay_danh_sach_key_web_cua,
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


def _tao_id():
    return "keyweb-" + secrets.token_hex(8)


# ----------------------------------------------------------------
# NHẬN DIỆN PROVIDER BẰNG CÁCH GỌI THỬ API
# ----------------------------------------------------------------
def _thu_serpjet(key):
    """
    SERPJET: gọi GET /account để kiểm tra key.
    Trả về: True nếu key hợp lệ.
    """
    try:
        r = requests.get(
            "https://serpjet.com/api/v1/account",
            params={"api_key": key},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


def _thu_tavily(key):
    """
    Tavily: gọi POST /search với query ngắn để kiểm tra key.
    Trả về: True nếu key hợp lệ.
    """
    try:
        r = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": key, "query": "test", "max_results": 1},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


def _thu_brightdata(key):
    """
    Bright Data: gọi GET /customer để kiểm tra key.
    Trả về: True nếu key hợp lệ.
    """
    try:
        r = requests.get(
            "https://api.brightdata.com/customer",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


def _nhan_dien_provider(key):
    """
    Nhận diện provider tra web bằng cách gọi thử API.
    Trả về: "SERPJET" | "Tavily" | "Bright Data" | None
    """
    if _thu_serpjet(key):
        return "SERPJET"
    if _thu_tavily(key):
        return "Tavily"
    if _thu_brightdata(key):
        return "Bright Data"
    return None


# ----------------------------------------------------------------
# LẤY QUOTA THẬT TỪNG PROVIDER
# ----------------------------------------------------------------
def _lay_quota_serpjet(key):
    """
    SERPJET: GET /account trả về số lượt còn lại.
    Trả về % hoặc None nếu không lấy được.
    """
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
    """
    Tavily: GET /usage trả về số lượt còn lại.
    """
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
    """
    Bright Data: GET /customer/balance trả về credit còn lại.
    """
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
        # Bright Data free: 5000 credit/tháng
        tong = 5000
        if tong <= 0:
            return 100
        return int(min(100, con_lai / tong * 100))
    except Exception:
        return None


def _lay_quota(key, provider):
    """Gọi hàm lấy quota tương ứng provider."""
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
    if provider is None:
        return {
            "thanh_cong": False,
            "loi": "Key không hợp lệ với SERPJET, Tavily hoặc Bright Data.",
        }

    phan_tram = _lay_quota(key, provider)
    if phan_tram is None:
        phan_tram = 100

    key_moi = {
        "id": _tao_id(),
        "key": key,
        "provider": provider,
        "loai_key": "tra_web",  # phân biệt với key model
        "chu_so_huu": ten_tk,
        "phan_tram": phan_tram,
        "ngay_tao": int(time.time()),
        "lan_kiem_tra_cuoi": int(time.time()),
    }

    if not luu_key_da_luu(key_moi):
        return {"thanh_cong": False, "loi": "Không lưu được key."}

    _ghi_log("tra-web", f"Lưu key tra web provider={provider} cho tài khoản {ten_tk}")

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
    Trả danh sách key tra web của tài khoản hiện tại.
    KHÔNG trả key gốc — chỉ id, provider, phần trăm.
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_key_web_cua(ten_tk) or []

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
# XÓA KEY TRA WEB
# ----------------------------------------------------------------
def xoa_key_web(du_lieu):
    """
    Xóa key tra web theo id.
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

    _ghi_log("tra-web", f"Xóa key tra web id={id_xoa} của tài khoản {ten_tk}")
    return {"thanh_cong": True}


# ----------------------------------------------------------------
# LẤY QUOTA KEY TRA WEB (cập nhật thật từ API)
# ----------------------------------------------------------------
def lay_quota_key_web():
    """
    Lấy quota thật của từng key tra web từ API provider.
    Cập nhật vào kho 1, trả về danh sách mới.
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": True, "danh_sach": []}

    danh_sach = lay_danh_sach_key_web_cua(ten_tk) or []
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
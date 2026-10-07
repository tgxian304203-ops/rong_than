"""
serpjet.py - Kết nối SERPJET API Tra web Rồng Thần.

Nhiệm vụ:
    - tim_kiem_serpjet(key, cau_hoi, so_ket_qua): tìm kiếm Google qua SERPJET.
    - kiem_tra_key_serpjet(key): kiểm tra key.
    - lay_quota_serpjet(key): lấy quota từ API.
    - serpjet_san_sang(): kiểm tra module sẵn sàng.

ĐÃ SỬA:
    - L31: Thêm FALLBACK cho endpoint + header auth. Thử lần lượt
      nhiều tổ hợp endpoint/header khi gặp 404/401/403.

Quy tắc:
    - Key format: sj_xxxxx
    - Free tier: 1.000 lượt/tháng, reset ngày 1.
    - Hỗ trợ 10 loại: search, images, videos, news, shopping, maps,
      places, scholar, patents, autocomplete.

Trả về:
    {
        thanh_cong: bool,
        ket_qua: [{tieu_de, mo_ta, url}],
        nguon: "SERPJET",
        loi: str,
        loai_loi: str,
    }

Tầng dữ liệu: Không.
"""

import time


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
# HẰNG SỐ — FALLBACK ENDPOINT & AUTH (L31)
# ================================================================
# Danh sách endpoint khả dụng
CAC_ENDPOINT_TIM_KIEM = [
    "https://api.serpjet.io/v1/search",
    "https://api.serpjet.io/search",
    "https://serpjet.io/api/v1/search",
]

# Danh sách endpoint kiểm tra tài khoản
CAC_ENDPOINT_TAI_KHOAN = [
    "https://api.serpjet.io/v1/account",
    "https://api.serpjet.io/account",
    "https://serpjet.io/api/v1/account",
]

# Danh sách kiểu auth khả dụng
CAC_KIEP_AUTH = ["x_api_key", "bearer"]

TIMEOUT = 30


# ================================================================
# TẠO HEADER AUTH
# ================================================================
def _tao_header_auth(key, kieu_auth="x_api_key"):
    """Tạo header Authorization theo kiểu."""
    if kieu_auth == "x_api_key":
        return {"X-API-KEY": key}
    elif kieu_auth == "bearer":
        return {"Authorization": f"Bearer {key}"}
    return {}


# ================================================================
# TÌM KIẾM
# ================================================================
def tim_kiem_serpjet(key, cau_hoi, so_ket_qua=5, loai="search", gl="vn", hl="vi"):
    """
    Tìm kiếm qua SERPJET (có fallback endpoint + auth).

    ĐÃ SỬA L31: Thử lần lượt nhiều tổ hợp (endpoint × auth) khi lỗi.
    """
    ket_qua = {
        "thanh_cong": False,
        "ket_qua": [],
        "nguon": "SERPJET",
        "loi": "",
        "loai_loi": "",
    }

    if not key or not cau_hoi:
        ket_qua["loi"] = "Thiếu key hoặc câu hỏi."
        return ket_qua

    try:
        import requests
    except ImportError:
        ket_qua["loi"] = "Chưa cài requests."
        return ket_qua

    # Chuẩn hóa số kết quả
    try:
        so_ket_qua = max(1, min(100, int(so_ket_qua)))
    except (ValueError, TypeError):
        so_ket_qua = 5

    params = {
        "q": cau_hoi,
        "type": loai,
        "gl": gl,
        "hl": hl,
        "num": so_ket_qua,
    }

    lich_su = []

    # Thử lần lượt endpoint × auth
    for url in CAC_ENDPOINT_TIM_KIEM:
        for kieu_auth in CAC_KIEP_AUTH:
            headers = _tao_header_auth(key, kieu_auth)
            try:
                r = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=TIMEOUT,
                )

                lich_su.append({
                    "url": url,
                    "auth": kieu_auth,
                    "status": r.status_code,
                })

                if r.status_code == 200:
                    du_lieu = r.json()
                    danh_sach = _trich_ket_qua(du_lieu, loai)
                    ket_qua["thanh_cong"] = True
                    ket_qua["ket_qua"] = _chuan_hoa_ket_qua(danh_sach)
                    ket_qua["url_dung"] = url
                    ket_qua["auth_dung"] = kieu_auth

                    _ghi_log(
                        "tra-web",
                        f"SERPJET OK ({url}, {kieu_auth}): "
                        f"{len(ket_qua['ket_qua'])} kết quả",
                    )
                    return ket_qua

                # Lỗi auth/endpoint → thử tổ hợp khác
                if r.status_code in (401, 403, 404):
                    continue

                # Lỗi 429 → hết quota
                if r.status_code == 429:
                    ket_qua["loi"] = "Hết quota (429)."
                    ket_qua["loai_loi"] = "het_quota"
                    ket_qua["lich_su"] = lich_su
                    return ket_qua

                # Lỗi khác → thử tiếp
                continue

            except Exception as e:
                lich_su.append({
                    "url": url,
                    "auth": kieu_auth,
                    "loi": str(e)[:100],
                })
                continue

    # Hết tất cả tổ hợp
    ket_qua["loi"] = "Tất cả endpoint/auth SERPJET đều thất bại."
    ket_qua["loai_loi"] = "khac"
    ket_qua["lich_su"] = lich_su
    return ket_qua


# ================================================================
# TRÍCH KẾT QUẢ TỪ JSON
# ================================================================
def _trich_ket_qua(du_lieu, loai):
    if not du_lieu or not isinstance(du_lieu, dict):
        return []

    danh_sach = (
        du_lieu.get("organic")
        or du_lieu.get("web")
        or du_lieu.get("results")
        or du_lieu.get("news")
        or du_lieu.get("shopping")
        or du_lieu.get("places")
        or du_lieu.get("items")
        or []
    )

    if not isinstance(danh_sach, list):
        return []

    return danh_sach


# ================================================================
# CHUẨN HÓA KẾT QUẢ
# ================================================================
def _chuan_hoa_ket_qua(danh_sach):
    if not danh_sach:
        return []

    ket_qua = []
    for item in danh_sach:
        if not isinstance(item, dict):
            continue

        tieu_de = item.get("title") or item.get("name") or ""
        mo_ta = (
            item.get("snippet")
            or item.get("description")
            or item.get("snippet_highlighted")
            or ""
        )
        url = item.get("link") or item.get("url") or item.get("href") or ""

        if not url and not tieu_de:
            continue

        ket_qua.append({
            "tieu_de": tieu_de.strip(),
            "mo_ta": mo_ta.strip(),
            "url": url.strip(),
        })

    return ket_qua


# ================================================================
# KIỂM TRA KEY
# ================================================================
def kiem_tra_key_serpjet(key):
    """Kiểm tra key SERPJET (có fallback endpoint + auth)."""
    if not key:
        return False, "Thiếu key."

    if not key.startswith("sj_"):
        return False, "Key không đúng format (phải bắt đầu bằng sj_)."

    try:
        import requests
        for url in CAC_ENDPOINT_TAI_KHOAN:
            for kieu_auth in CAC_KIEP_AUTH:
                try:
                    r = requests.get(
                        url,
                        headers=_tao_header_auth(key, kieu_auth),
                        timeout=10,
                    )
                    if r.status_code == 200:
                        return True, ""
                    if r.status_code in (401, 403):
                        return False, "Key sai hoặc hết hạn."
                    # 404 → thử tổ hợp khác
                except Exception:
                    continue

        return False, "Không kiểm tra được key."
    except ImportError:
        return False, "Chưa cài requests."
    except Exception as e:
        return False, f"Lỗi kiểm tra key: {e}"


# ================================================================
# LẤY QUOTA
# ================================================================
def lay_quota_serpjet(key):
    """Lấy quota SERPJET (có fallback)."""
    ket_qua = {
        "phan_tram": 100,
        "con_lai": None,
        "tong": 1000,
        "loai_quota": "thang",
    }

    if not key:
        return ket_qua

    try:
        import requests
        for url in CAC_ENDPOINT_TAI_KHOAN:
            for kieu_auth in CAC_KIEP_AUTH:
                try:
                    r = requests.get(
                        url,
                        headers=_tao_header_auth(key, kieu_auth),
                        timeout=10,
                    )
                    if r.status_code == 200:
                        du_lieu = r.json()
                        da_dung = du_lieu.get("used", 0) or 0
                        tong = du_lieu.get("quota", 1000) or 1000
                        con_lai = max(0, tong - da_dung)
                        phan_tram = int(con_lai / tong * 100) if tong > 0 else 100
                        return {
                            "phan_tram": phan_tram,
                            "con_lai": con_lai,
                            "tong": tong,
                            "loai_quota": "thang",
                        }
                    if r.status_code in (401, 403):
                        ket_qua["phan_tram"] = 0
                        ket_qua["loai_quota"] = "key_sai"
                        return ket_qua
                except Exception:
                    continue
    except ImportError:
        pass
    except Exception:
        pass

    return ket_qua


# ================================================================
# HÀM PHỤ
# ================================================================
def tim_kiem_nhanh(key, cau_hoi):
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua=5)


def tim_kiem_tin_tuc(key, cau_hoi, so_ket_qua=5):
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua, loai="news")


def tim_kiem_hinh_anh(key, cau_hoi, so_ket_qua=5):
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua, loai="images")


def tim_kiem_video(key, cau_hoi, so_ket_qua=5):
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua, loai="videos")


def tim_kiem_mua_sam(key, cau_hoi, so_ket_qua=5, gl="us"):
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua, loai="shopping", gl=gl, hl="en")


def tim_kiem_hoc_thuat(key, cau_hoi, so_ket_qua=5):
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua, loai="scholar")


def serpjet_san_sang():
    try:
        import requests
        return True
    except ImportError:
        return False


def tom_tat(ket_qua):
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ SERPJET: {len(ket_qua.get('ket_qua', []))} kết quả"
    return f"❌ SERPJET [{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')[:100]}"


def danh_sach_loai_tim_kiem():
    return [
        "search", "images", "videos", "news", "shopping",
        "maps", "places", "scholar", "patents", "autocomplete",
    ]
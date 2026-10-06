"""
serpjet.py - Kết nối SERPJET API Tra web Rồng Thần.

Nhiệm vụ:
    - tim_kiem_serpjet(key, cau_hoi, so_ket_qua): tìm kiếm Google qua SERPJET.
    - kiem_tra_key_serpjet(key): kiểm tra key.
    - lay_quota_serpjet(key): lấy quota từ API.
    - serpjet_san_sang(): kiểm tra module sẵn sàng.
    - _chuan_hoa_ket_qua(du_lieu): chuẩn hóa kết quả.

Quy tắc:
    - Endpoint: https://api.serpjet.io/v1/search
    - Auth: header X-API-KEY hoặc ?api_key=
    - Key format: sj_xxxxx
    - Free tier: 1.000 lượt/tháng, reset ngày 1 [citation:1][citation:5].
    - Hỗ trợ 10 loại: search, images, videos, news, shopping, maps, places, scholar, patents, autocomplete [citation:1].

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
# HẰNG SỐ
# ================================================================
URL_SERPJET = "https://api.serpjet.io/v1/search"
URL_SERPJET_ACCOUNT = "https://api.serpjet.io/v1/account"
TIMEOUT = 30


# ================================================================
# TÌM KIẾM
# ================================================================
def tim_kiem_serpjet(key, cau_hoi, so_ket_qua=5, loai="search", gl="vn", hl="vi"):
    """
    Tìm kiếm qua SERPJET.

    key: API key (sj_xxx).
    cau_hoi: từ khóa tìm kiếm.
    so_ket_qua: số kết quả (1-100).
    loai: search | images | videos | news | shopping | maps | places | scholar | patents | autocomplete.
    gl: mã quốc gia (vn, us, de, jp...).
    hl: ngôn ngữ (vi, en, zh-cn...).

    Trả về: dict kết quả.
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
    headers = {
        "X-API-KEY": key,
    }

    try:
        r = requests.get(
            URL_SERPJET,
            params=params,
            headers=headers,
            timeout=TIMEOUT,
        )

        # Xử lý lỗi
        if r.status_code != 200:
            try:
                from tra_web.xu_ly_loi_api import phan_tich_loi
                mo_ta, loai_loi = phan_tich_loi(r.status_code, r.text[:500], "SERPJET")
                ket_qua["loi"] = mo_ta
                ket_qua["loai_loi"] = loai_loi
            except ImportError:
                ket_qua["loi"] = f"SERPJET trả {r.status_code}."
                ket_qua["loai_loi"] = "khac"
            return ket_qua

        # Parse JSON
        du_lieu = r.json()

        # Chuẩn hóa kết quả
        danh_sach = _trich_ket_qua(du_lieu, loai)
        ket_qua["thanh_cong"] = True
        ket_qua["ket_qua"] = _chuan_hoa_ket_qua(danh_sach)

        _ghi_log(
            "tra-web",
            f"SERPJET: {len(ket_qua['ket_qua'])} kết quả cho '{cau_hoi[:50]}'",
        )

        return ket_qua

    except Exception as e:
        try:
            from tra_web.xu_ly_loi_api import xu_ly_exception
            ket_qua_loi = xu_ly_exception(e, "SERPJET")
            ket_qua["loi"] = ket_qua_loi.get("loi", str(e))
            ket_qua["loai_loi"] = ket_qua_loi.get("loai_loi", "khac")
        except ImportError:
            ket_qua["loi"] = f"Lỗi SERPJET: {e}"
            ket_qua["loai_loi"] = "khac"
        return ket_qua


# ================================================================
# TRÍCH KẾT QUẢ TỪ JSON
# ================================================================
def _trich_ket_qua(du_lieu, loai):
    """
    Trích kết quả từ JSON của SERPJET.

    Cấu trúc JSON trả về có thể có nhiều dạng tùy loại.
    """
    if not du_lieu or not isinstance(du_lieu, dict):
        return []

    # SERPJET trả về các mảng tùy loại: web, organic, results, shopping...
    danh_sach = (
        du_lieu.get("organic")
        or du_lieu.get("web")
        or du_lieu.get("results")
        or du_lieu.get("news")
        or du_lieu.get("shopping")
        or du_lieu.get("places")
        or []
    )

    if not isinstance(danh_sach, list):
        return []

    return danh_sach


# ================================================================
# CHUẨN HÓA KẾT QUẢ
# ================================================================
def _chuan_hoa_ket_qua(danh_sach):
    """
    Chuẩn hóa kết quả về format {tieu_de, mo_ta, url}.
    """
    if not danh_sach:
        return []

    ket_qua = []
    for item in danh_sach:
        if not isinstance(item, dict):
            continue

        tieu_de = (
            item.get("title")
            or item.get("name")
            or ""
        )
        mo_ta = (
            item.get("snippet")
            or item.get("description")
            or item.get("snippet_highlighted")
            or ""
        )
        url = (
            item.get("link")
            or item.get("url")
            or item.get("href")
            or ""
        )

        # Nếu không có URL → bỏ qua
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
    """
    Kiểm tra key SERPJET còn hiệu lực không.

    Trả về: (True, "") hoặc (False, "lỗi").
    """
    if not key:
        return False, "Thiếu key."

    # Kiểm tra format key
    if not key.startswith("sj_"):
        return False, "Key không đúng format (phải bắt đầu bằng sj_)."

    try:
        import requests
        r = requests.get(
            URL_SERPJET_ACCOUNT,
            headers={"X-API-KEY": key},
            timeout=10,
        )

        if r.status_code == 200:
            return True, ""
        if r.status_code in (401, 403):
            return False, "Key sai hoặc hết hạn."
        return False, f"SERPJET trả {r.status_code}."
    except ImportError:
        return False, "Chưa cài requests."
    except Exception as e:
        return False, f"Lỗi kiểm tra key: {e}"


# ================================================================
# LẤY QUOTA
# ================================================================
def lay_quota_serpjet(key):
    """
    Lấy quota SERPJET.

    SERPJET free tier: 1.000 lượt/tháng [citation:1][citation:5].

    Trả về dict { phan_tram, con_lai, tong, loai_quota }.
    """
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
        r = requests.get(
            URL_SERPJET_ACCOUNT,
            headers={"X-API-KEY": key},
            timeout=10,
        )

        if r.status_code != 200:
            if r.status_code in (401, 403):
                ket_qua["phan_tram"] = 0
                ket_qua["loai_quota"] = "key_sai"
            return ket_qua

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

    except ImportError:
        return ket_qua
    except Exception:
        return ket_qua


# ================================================================
# HÀM PHỤ: TÌM KIẾM NHANH
# ================================================================
def tim_kiem_nhanh(key, cau_hoi):
    """Tìm kiếm nhanh với mặc định (search, vn, vi, 5 kết quả)."""
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua=5)


# ================================================================
# HÀM PHỤ: CÁC LOẠI TÌM KIẾM
# ================================================================
def tim_kiem_tin_tuc(key, cau_hoi, so_ket_qua=5):
    """Tìm tin tức."""
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua, loai="news")


def tim_kiem_hinh_anh(key, cau_hoi, so_ket_qua=5):
    """Tìm hình ảnh."""
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua, loai="images")


def tim_kiem_video(key, cau_hoi, so_ket_qua=5):
    """Tìm video."""
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua, loai="videos")


def tim_kiem_mua_sam(key, cau_hoi, so_ket_qua=5, gl="us"):
    """Tìm shopping (có giá)."""
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua, loai="shopping", gl=gl, hl="en")


def tim_kiem_hoc_thuat(key, cau_hoi, so_ket_qua=5):
    """Tìm scholar."""
    return tim_kiem_serpjet(key, cau_hoi, so_ket_qua, loai="scholar")


# ================================================================
# HÀM PHỤ: KIỂM TRA SẴN SÀNG
# ================================================================
def serpjet_san_sang():
    """Kiểm tra module SERPJET sẵn sàng."""
    try:
        import requests
        return True
    except ImportError:
        return False


# ================================================================
# HÀM PHỤ: TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả SERPJET."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return f"✅ SERPJET: {len(ket_qua.get('ket_qua', []))} kết quả"

    return f"❌ SERPJET [{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')[:100]}"


# ================================================================
# HÀM PHỤ: DANH SÁCH LOẠI TÌM KIẾM
# ================================================================
def danh_sach_loai_tim_kiem():
    """Trả danh sách 10 loại tìm kiếm SERPJET hỗ trợ [citation:1]."""
    return [
        "search", "images", "videos", "news", "shopping",
        "maps", "places", "scholar", "patents", "autocomplete",
    ]
"""
brightdata.py - Kết nối Bright Data API Tra web Rồng Thần.

Nhiệm vụ:
    - tim_kiem_brightdata(key, cau_hoi, so_ket_qua, zone): tìm kiếm qua SERP API.
    - lay_noi_dung_brightdata(key, url, zone): lấy nội dung qua Web Unlocker API.
    - kiem_tra_key_brightdata(key): kiểm tra key.
    - lay_quota_brightdata(key): lấy quota từ API.
    - brightdata_san_sang(): kiểm tra module sẵn sàng.

Quy tắc:
    - Endpoint: https://api.brightdata.com/request
    - Auth: Bearer <API_KEY>.
    - Key format: API key từ dashboard.
    - Free tier: 5.000 credit/tháng, reset ngày 1.
    - SERP API: 1 credit/request, hỗ trợ Google/Bing/DuckDuckGo/Yandex.
    - Web Unlocker API: 1 credit/request, bypass anti-bot.
    - Cần zone name khi gọi.

Trả về:
    {
        thanh_cong: bool,
        ket_qua: [{tieu_de, mo_ta, url}],
        nguon: "Bright Data",
        loi: str,
        loai_loi: str,
    }

Tầng dữ liệu: Không.
"""

import time
import json


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
URL_BRIGHTDATA = "https://api.brightdata.com/request"
TIMEOUT = 60


# ================================================================
# TÌM KIẾM QUA SERP API
# ================================================================
def tim_kiem_brightdata(key, cau_hoi, so_ket_qua=5, zone="serp_api1",
                        search_engine="google", country="vn", language="vi"):
    """
    Tìm kiếm qua Bright Data SERP API.

    key: API key.
    cau_hoi: từ khóa tìm kiếm.
    so_ket_qua: số kết quả (1-20).
    zone: tên zone SERP API (mặc định serp_api1).
    search_engine: google | bing | duckduckgo | yandex.
    country: mã quốc gia (vn, us, de...).
    language: ngôn ngữ (vi, en...).

    Trả về: dict kết quả.
    """
    ket_qua = {
        "thanh_cong": False,
        "ket_qua": [],
        "nguon": "Bright Data",
        "loi": "",
        "loai_loi": "",
    }

    if not key or not cau_hoi:
        ket_qua["loi"] = "Thiếu key hoặc câu hỏi."
        return ket_qua

    if not zone:
        ket_qua["loi"] = "Thiếu zone name."
        return ket_qua

    try:
        import requests
    except ImportError:
        ket_qua["loi"] = "Chưa cài requests."
        return ket_qua

    # Chuẩn hóa số kết quả
    try:
        so_ket_qua = max(1, min(20, int(so_ket_qua)))
    except (ValueError, TypeError):
        so_ket_qua = 5

    # URL của SERP API
    # Format: https://www.google.com/search?q=...&num=...&gl=...&hl=...
    url_serp = (
        f"https://www.{search_engine}.com/search"
        f"?q={requests.utils.quote(cau_hoi)}"
        f"&num={so_ket_qua}"
        f"&gl={country}"
        f"&hl={language}"
    )

    # Body cho Bright Data API
    body = {
        "zone": zone,
        "url": url_serp,
        "format": "json",
    }

    try:
        r = requests.post(
            URL_BRIGHTDATA,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=TIMEOUT,
        )

        # Xử lý lỗi
        if r.status_code != 200:
            try:
                from tra_web.xu_ly_loi_api import phan_tich_loi
                mo_ta, loai_loi = phan_tich_loi(r.status_code, r.text[:500], "Bright Data")
                ket_qua["loi"] = mo_ta
                ket_qua["loai_loi"] = loai_loi
            except ImportError:
                ket_qua["loi"] = f"Bright Data trả {r.status_code}."
                ket_qua["loai_loi"] = "khac"
            return ket_qua

        # Parse JSON
        du_lieu = r.json()

        # Trích kết quả
        danh_sach = _trich_ket_qua_serp(du_lieu)
        ket_qua["thanh_cong"] = True
        ket_qua["ket_qua"] = _chuan_hoa_ket_qua(danh_sach)

        _ghi_log(
            "tra-web",
            f"Bright Data: {len(ket_qua['ket_qua'])} kết quả cho '{cau_hoi[:50]}'",
        )

        return ket_qua

    except Exception as e:
        try:
            from tra_web.xu_ly_loi_api import xu_ly_exception
            ket_qua_loi = xu_ly_exception(e, "Bright Data")
            ket_qua["loi"] = ket_qua_loi.get("loi", str(e))
            ket_qua["loai_loi"] = ket_qua_loi.get("loai_loi", "khac")
        except ImportError:
            ket_qua["loi"] = f"Lỗi Bright Data: {e}"
            ket_qua["loai_loi"] = "khac"
        return ket_qua


# ================================================================
# LẤY NỘI DUNG QUA WEB UNLOCKER API
# ================================================================
def lay_noi_dung_brightdata(key, url, zone="web_unlocker1", format="markdown"):
    """
    Lấy nội dung trang web qua Bright Data Web Unlocker API.

    key: API key.
    url: URL cần lấy nội dung.
    zone: tên zone Web Unlocker (mặc định web_unlocker1).
    format: raw | markdown | html.

    Trả về: dict { thanh_cong, noi_dung, loi, loai_loi }.
    """
    ket_qua = {
        "thanh_cong": False,
        "noi_dung": "",
        "loi": "",
        "loai_loi": "",
    }

    if not key or not url:
        ket_qua["loi"] = "Thiếu key hoặc URL."
        return ket_qua

    if not zone:
        ket_qua["loi"] = "Thiếu zone name."
        return ket_qua

    try:
        import requests
    except ImportError:
        ket_qua["loi"] = "Chưa cài requests."
        return ket_qua

    body = {
        "zone": zone,
        "url": url,
        "format": format,
    }

    try:
        r = requests.post(
            URL_BRIGHTDATA,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=TIMEOUT,
        )

        if r.status_code != 200:
            try:
                from tra_web.xu_ly_loi_api import phan_tich_loi
                mo_ta, loai_loi = phan_tich_loi(r.status_code, r.text[:500], "Bright Data")
                ket_qua["loi"] = mo_ta
                ket_qua["loai_loi"] = loai_loi
            except ImportError:
                ket_qua["loi"] = f"Bright Data trả {r.status_code}."
                ket_qua["loai_loi"] = "khac"
            return ket_qua

        # Trả về nội dung
        ket_qua["thanh_cong"] = True
        ket_qua["noi_dung"] = r.text

        return ket_qua

    except Exception as e:
        try:
            from tra_web.xu_ly_loi_api import xu_ly_exception
            ket_qua_loi = xu_ly_exception(e, "Bright Data")
            ket_qua["loi"] = ket_qua_loi.get("loi", str(e))
            ket_qua["loai_loi"] = ket_qua_loi.get("loai_loi", "khac")
        except ImportError:
            ket_qua["loi"] = f"Lỗi Bright Data: {e}"
            ket_qua["loai_loi"] = "khac"
        return ket_qua


# ================================================================
# TRÍCH KẾT QUẢ SERP
# ================================================================
def _trich_ket_qua_serp(du_lieu):
    """
    Trích kết quả từ JSON của Bright Data SERP API.

    Cấu trúc có thể có nhiều dạng tùy search engine.
    """
    if not du_lieu:
        return []

    # Bright Data có thể trả về JSON trực tiếp hoặc nested
    if isinstance(du_lieu, str):
        try:
            du_lieu = json.loads(du_lieu)
        except (json.JSONDecodeError, ValueError):
            return []

    if not isinstance(du_lieu, dict):
        return []

    # Thử các tên trường phổ biến
    danh_sach = (
        du_lieu.get("organic")
        or du_lieu.get("organic_results")
        or du_lieu.get("results")
        or du_lieu.get("web")
        or du_lieu.get("items")
        or []
    )

    if isinstance(danh_sach, list):
        return danh_sach

    return []


# ================================================================
# CHUẨN HÓA KẾT QUẢ
# ================================================================
def _chuan_hoa_ket_qua(danh_sach):
    """Chuẩn hóa kết quả về format {tieu_de, mo_ta, url}."""
    if not danh_sach:
        return []

    ket_qua = []
    for item in danh_sach:
        if not isinstance(item, dict):
            continue

        tieu_de = item.get("title") or item.get("name") or ""
        mo_ta = item.get("snippet") or item.get("description") or ""
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
def kiem_tra_key_brightdata(key):
    """
    Kiểm tra key Bright Data còn hiệu lực không.

    Gọi thử 1 request đơn giản.

    Trả về: (True, "") hoặc (False, "lỗi").
    """
    if not key:
        return False, "Thiếu key."

    try:
        import requests
        # Gọi thử Web Unlocker với URL test
        r = requests.post(
            URL_BRIGHTDATA,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "zone": "web_unlocker1",
                "url": "https://geo.brdtest.com/welcome.txt",
                "format": "raw",
            },
            timeout=30,
        )

        if r.status_code == 200:
            return True, ""
        if r.status_code == 401:
            return False, "Key sai hoặc hết hạn."
        if r.status_code == 403:
            return False, "Không có quyền (có thể do zone sai)."
        if r.status_code == 429:
            return False, "Hết quota."
        return False, f"Bright Data trả {r.status_code}."
    except ImportError:
        return False, "Chưa cài requests."
    except Exception as e:
        return False, f"Lỗi kiểm tra key: {e}"


# ================================================================
# LẤY QUOTA
# ================================================================
def lay_quota_brightdata(key):
    """
    Lấy quota Bright Data.

    Bright Data free tier: 5.000 credit/tháng, reset ngày 1 [citation:1][citation:5].

    Trả về dict { phan_tram, con_lai, tong, loai_quota }.
    """
    ket_qua = {
        "phan_tram": 100,
        "con_lai": None,
        "tong": 5000,
        "loai_quota": "thang",
    }

    if not key:
        return ket_qua

    # Bright Data không có endpoint công khai lấy quota
    # Chỉ trả về thông tin mặc định
    return ket_qua


# ================================================================
# HÀM PHỤ: TÌM KIẾM NHANH
# ================================================================
def tim_kiem_nhanh(key, cau_hoi, zone="serp_api1"):
    """Tìm kiếm nhanh với mặc định (google, vn, vi, 5 kết quả)."""
    return tim_kiem_brightdata(key, cau_hoi, so_ket_qua=5, zone=zone)


def tim_kiem_bing(key, cau_hoi, so_ket_qua=5, zone="serp_api1"):
    """Tìm kiếm qua Bing."""
    return tim_kiem_brightdata(key, cau_hoi, so_ket_qua,
                               zone=zone, search_engine="bing")


def tim_kiem_duckduckgo(key, cau_hoi, so_ket_qua=5, zone="serp_api1"):
    """Tìm kiếm qua DuckDuckGo."""
    return tim_kiem_brightdata(key, cau_hoi, so_ket_qua,
                               zone=zone, search_engine="duckduckgo")


# ================================================================
# HÀM PHỤ: KIỂM TRA SẴN SÀNG
# ================================================================
def brightdata_san_sang():
    """Kiểm tra module Bright Data sẵn sàng."""
    try:
        import requests
        return True
    except ImportError:
        return False


# ================================================================
# HÀM PHỤ: TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả Bright Data."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return f"✅ Bright Data: {len(ket_qua.get('ket_qua', []))} kết quả"

    return f"❌ Bright Data [{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')[:100]}"


# ================================================================
# HÀM PHỤ: CÁC SEARCH ENGINE HỖ TRỢ
# ================================================================
def danh_sach_search_engine():
    """Trả danh sách search engine Bright Data hỗ trợ [citation:1]."""
    return ["google", "bing", "duckduckgo", "yandex"]


# ================================================================
# HÀM PHỤ: CÁC ZONE MẶC ĐỊNH
# ================================================================
def danh_sach_zone_mac_dinh():
    """Trả danh sách zone mặc định."""
    return {
        "serp": "serp_api1",
        "unlocker": "web_unlocker1",
        "browser": "browser_api1",
    }
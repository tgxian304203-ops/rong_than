"""
brightdata.py - Kết nối Bright Data API Tra web Rồng Thần.
"""

import time
import json


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


URL_BRIGHTDATA = "https://api.brightdata.com/request"
TIMEOUT = 60


def tim_kiem_brightdata(key, cau_hoi, so_ket_qua=5, zone="serp_api1",
                        search_engine="google", country="vn", language="vi"):
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

    try:
        so_ket_qua = max(1, min(20, int(so_ket_qua)))
    except (ValueError, TypeError):
        so_ket_qua = 5

    url_serp = (
        f"https://www.{search_engine}.com/search"
        f"?q={requests.utils.quote(cau_hoi)}"
        f"&num={so_ket_qua}"
        f"&gl={country}"
        f"&hl={language}"
    )

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

        if r.status_code != 200:
            try:
                from dai_nao.tra_web.xu_ly_loi_api import phan_tich_loi
                mo_ta, loai_loi = phan_tich_loi(r.status_code, r.text[:500], "Bright Data")
                ket_qua["loi"] = mo_ta
                ket_qua["loai_loi"] = loai_loi
            except ImportError:
                ket_qua["loi"] = f"Bright Data trả {r.status_code}."
                ket_qua["loai_loi"] = "khac"
            return ket_qua

        du_lieu = r.json()

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
            from dai_nao.tra_web.xu_ly_loi_api import xu_ly_exception
            ket_qua_loi = xu_ly_exception(e, "Bright Data")
            ket_qua["loi"] = ket_qua_loi.get("loi", str(e))
            ket_qua["loai_loi"] = ket_qua_loi.get("loai_loi", "khac")
        except ImportError:
            ket_qua["loi"] = f"Lỗi Bright Data: {e}"
            ket_qua["loai_loi"] = "khac"
        return ket_qua


def lay_noi_dung_brightdata(key, url, zone="web_unlocker1", format="markdown"):
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
                from dai_nao.tra_web.xu_ly_loi_api import phan_tich_loi
                mo_ta, loai_loi = phan_tich_loi(r.status_code, r.text[:500], "Bright Data")
                ket_qua["loi"] = mo_ta
                ket_qua["loai_loi"] = loai_loi
            except ImportError:
                ket_qua["loi"] = f"Bright Data trả {r.status_code}."
                ket_qua["loai_loi"] = "khac"
            return ket_qua

        ket_qua["thanh_cong"] = True
        ket_qua["noi_dung"] = r.text

        return ket_qua

    except Exception as e:
        try:
            from dai_nao.tra_web.xu_ly_loi_api import xu_ly_exception
            ket_qua_loi = xu_ly_exception(e, "Bright Data")
            ket_qua["loi"] = ket_qua_loi.get("loi", str(e))
            ket_qua["loai_loi"] = ket_qua_loi.get("loai_loi", "khac")
        except ImportError:
            ket_qua["loi"] = f"Lỗi Bright Data: {e}"
            ket_qua["loai_loi"] = "khac"
        return ket_qua


def _trich_ket_qua_serp(du_lieu):
    if not du_lieu:
        return []

    if isinstance(du_lieu, str):
        try:
            du_lieu = json.loads(du_lieu)
        except (json.JSONDecodeError, ValueError):
            return []

    if not isinstance(du_lieu, dict):
        return []

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


def _chuan_hoa_ket_qua(danh_sach):
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


def kiem_tra_key_brightdata(key):
    if not key:
        return False, "Thiếu key."

    try:
        import requests
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


def lay_quota_brightdata(key):
    ket_qua = {
        "phan_tram": 100,
        "con_lai": None,
        "tong": 5000,
        "loai_quota": "thang",
    }

    if not key:
        return ket_qua

    return ket_qua


def tim_kiem_nhanh(key, cau_hoi, zone="serp_api1"):
    return tim_kiem_brightdata(key, cau_hoi, so_ket_qua=5, zone=zone)


def tim_kiem_bing(key, cau_hoi, so_ket_qua=5, zone="serp_api1"):
    return tim_kiem_brightdata(key, cau_hoi, so_ket_qua,
                               zone=zone, search_engine="bing")


def tim_kiem_duckduckgo(key, cau_hoi, so_ket_qua=5, zone="serp_api1"):
    return tim_kiem_brightdata(key, cau_hoi, so_ket_qua,
                               zone=zone, search_engine="duckduckgo")


def brightdata_san_sang():
    try:
        import requests
        return True
    except ImportError:
        return False


def tom_tat(ket_qua):
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return f"✅ Bright Data: {len(ket_qua.get('ket_qua', []))} kết quả"

    return f"❌ Bright Data [{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')[:100]}"


def danh_sach_search_engine():
    return ["google", "bing", "duckduckgo", "yandex"]


def danh_sach_zone_mac_dinh():
    return {
        "serp": "serp_api1",
        "unlocker": "web_unlocker1",
        "browser": "browser_api1",
    }
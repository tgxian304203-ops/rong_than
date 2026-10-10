"""
tavily.py - Kết nối Tavily API Tra web Rồng Thần.
"""

import time


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


URL_TAVILY = "https://api.tavily.com/search"
URL_TAVILY_USAGE = "https://api.tavily.com/usage"
TIMEOUT = 30


def tim_kiem_tavily(key, cau_hoi, so_ket_qua=5, do_sau="basic",
                    chu_de="general", khoang_thoi_gian=None,
                    bao_gom_tra_loi=False, keyless=False):
    ket_qua = {
        "thanh_cong": False,
        "ket_qua": [],
        "nguon": "Tavily",
        "loi": "",
        "loai_loi": "",
    }

    if not cau_hoi:
        ket_qua["loi"] = "Thiếu câu hỏi."
        return ket_qua

    if not key and not keyless:
        ket_qua["loi"] = "Thiếu key Tavily."
        return ket_qua

    try:
        import requests
    except ImportError:
        ket_qua["loi"] = "Chưa cài requests."
        return ket_qua

    try:
        so_ket_qua = max(0, min(20, int(so_ket_qua)))
    except (ValueError, TypeError):
        so_ket_qua = 5

    body = {
        "query": cau_hoi,
        "search_depth": do_sau,
        "topic": chu_de,
        "max_results": so_ket_qua,
        "include_answer": bao_gom_tra_loi,
        "include_raw_content": False,
        "include_images": False,
    }
    if khoang_thoi_gian:
        body["time_range"] = khoang_thoi_gian

    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    if keyless and not key:
        headers["X-Tavily-Access-Mode"] = "keyless"

    try:
        r = requests.post(
            URL_TAVILY,
            headers=headers,
            json=body,
            timeout=TIMEOUT,
        )

        if r.status_code != 200:
            try:
                from dai_nao.tra_web.xu_ly_loi_api import phan_tich_loi
                mo_ta, loai_loi = phan_tich_loi(r.status_code, r.text[:500], "Tavily")
                ket_qua["loi"] = mo_ta
                ket_qua["loai_loi"] = loai_loi
            except ImportError:
                ket_qua["loi"] = f"Tavily trả {r.status_code}."
                ket_qua["loai_loi"] = "khac"
            return ket_qua

        du_lieu = r.json()

        danh_sach = du_lieu.get("results", [])
        ket_qua["thanh_cong"] = True
        ket_qua["ket_qua"] = _chuan_hoa_ket_qua(danh_sach)

        if bao_gom_tra_loi and du_lieu.get("answer"):
            ket_qua["tra_loi_ai"] = du_lieu["answer"]

        _ghi_log(
            "tra-web",
            f"Tavily: {len(ket_qua['ket_qua'])} kết quả cho '{cau_hoi[:50]}'",
        )

        return ket_qua

    except Exception as e:
        try:
            from dai_nao.tra_web.xu_ly_loi_api import xu_ly_exception
            ket_qua_loi = xu_ly_exception(e, "Tavily")
            ket_qua["loi"] = ket_qua_loi.get("loi", str(e))
            ket_qua["loai_loi"] = ket_qua_loi.get("loai_loi", "khac")
        except ImportError:
            ket_qua["loi"] = f"Lỗi Tavily: {e}"
            ket_qua["loai_loi"] = "khac"
        return ket_qua


def _chuan_hoa_ket_qua(danh_sach):
    if not danh_sach:
        return []

    ket_qua = []
    for item in danh_sach:
        if not isinstance(item, dict):
            continue

        tieu_de = item.get("title", "")
        mo_ta = item.get("content", "")
        url = item.get("url", "")

        if not url and not tieu_de:
            continue

        ket_qua.append({
            "tieu_de": tieu_de.strip(),
            "mo_ta": mo_ta.strip(),
            "url": url.strip(),
            "diem": item.get("score", 0.0),
            "ngay_xuat_ban": item.get("published_date"),
        })

    return ket_qua


def kiem_tra_key_tavily(key):
    if not key:
        return False, "Thiếu key."

    if not key.startswith("tvly-"):
        return False, "Key không đúng format (phải bắt đầu bằng tvly-)."

    try:
        import requests
        r = requests.post(
            URL_TAVILY,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "query": "test",
                "search_depth": "basic",
                "max_results": 1,
            },
            timeout=10,
        )

        if r.status_code == 200:
            return True, ""
        if r.status_code == 401:
            return False, "Key sai hoặc hết hạn."
        if r.status_code == 429:
            return False, "Hết quota hoặc vượt rate limit."
        return False, f"Tavily trả {r.status_code}."
    except ImportError:
        return False, "Chưa cài requests."
    except Exception as e:
        return False, f"Lỗi kiểm tra key: {e}"


def lay_quota_tavily(key):
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
            URL_TAVILY_USAGE,
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )

        if r.status_code != 200:
            if r.status_code in (401, 403):
                ket_qua["phan_tram"] = 0
                ket_qua["loai_quota"] = "key_sai"
            return ket_qua

        du_lieu = r.json()
        da_dung = du_lieu.get("usage", 0) or 0
        tong = du_lieu.get("limit", 1000) or 1000

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


def tim_kiem_nhanh(key, cau_hoi):
    return tim_kiem_tavily(key, cau_hoi, so_ket_qua=5)


def tim_kiem_tin_tuc(key, cau_hoi, so_ket_qua=5):
    return tim_kiem_tavily(key, cau_hoi, so_ket_qua, chu_de="news",
                           khoang_thoi_gian="week")


def tim_kiem_chuyen_sau(key, cau_hoi, so_ket_qua=5):
    return tim_kiem_tavily(key, cau_hoi, so_ket_qua, do_sau="advanced")


def tim_kiem_keyless(cau_hoi, so_ket_qua=5):
    return tim_kiem_tavily("", cau_hoi, so_ket_qua, keyless=True)


def tavily_san_sang():
    try:
        import requests
        return True
    except ImportError:
        return False


def tom_tat(ket_qua):
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return f"✅ Tavily: {len(ket_qua.get('ket_qua', []))} kết quả"

    return f"❌ Tavily [{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')[:100]}"


def chi_phi_search(do_sau="basic"):
    return 2 if do_sau == "advanced" else 1
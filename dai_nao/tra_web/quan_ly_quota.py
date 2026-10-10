"""
quan_ly_quota.py - Theo dõi quota API Tra web Rồng Thần.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho.
"""

import time


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


QUOTA_MAC_DINH = {
    "SERPJET": 1000,
    "Tavily": 1000,
    "Bright Data": 5000,
}


def _lay_quota_serpjet(key):
    ket_qua = {
        "phan_tram": None,
        "con_lai": None,
        "tong": QUOTA_MAC_DINH["SERPJET"],
        "loai_quota": "thang",
    }

    if not key:
        return ket_qua

    try:
        import requests
        r = requests.get(
            "https://serpjet.com/api/v1/account",
            params={"api_key": key},
            timeout=10,
        )

        if r.status_code != 200:
            if r.status_code in (401, 403):
                ket_qua["phan_tram"] = 0
                ket_qua["loai_quota"] = "key_sai"
            return ket_qua

        du_lieu = r.json()
        da_dung = du_lieu.get("used", 0) or 0
        tong = du_lieu.get("quota", QUOTA_MAC_DINH["SERPJET"]) or QUOTA_MAC_DINH["SERPJET"]

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
        ket_qua["phan_tram"] = 100
        return ket_qua


def _lay_quota_tavily(key):
    ket_qua = {
        "phan_tram": None,
        "con_lai": None,
        "tong": QUOTA_MAC_DINH["Tavily"],
        "loai_quota": "thang",
    }

    if not key:
        return ket_qua

    try:
        import requests
        r = requests.get(
            "https://api.tavily.com/usage",
            params={"api_key": key},
            timeout=10,
        )

        if r.status_code != 200:
            if r.status_code in (401, 403):
                ket_qua["phan_tram"] = 0
                ket_qua["loai_quota"] = "key_sai"
            return ket_qua

        du_lieu = r.json()
        da_dung = du_lieu.get("usage", 0) or 0
        tong = du_lieu.get("limit", QUOTA_MAC_DINH["Tavily"]) or QUOTA_MAC_DINH["Tavily"]

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
        ket_qua["phan_tram"] = 100
        return ket_qua


def _lay_quota_brightdata(key):
    ket_qua = {
        "phan_tram": None,
        "con_lai": None,
        "tong": QUOTA_MAC_DINH["Bright Data"],
        "loai_quota": "thang",
    }

    if not key:
        return ket_qua

    try:
        import requests
        r = requests.get(
            "https://api.brightdata.com/customer/balance",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )

        if r.status_code != 200:
            if r.status_code in (401, 403):
                ket_qua["phan_tram"] = 0
                ket_qua["loai_quota"] = "key_sai"
            return ket_qua

        du_lieu = r.json()
        con_lai = du_lieu.get("balance", 0) or 0
        tong = QUOTA_MAC_DINH["Bright Data"]

        phan_tram = int(min(100, con_lai / tong * 100)) if tong > 0 else 100

        return {
            "phan_tram": phan_tram,
            "con_lai": con_lai,
            "tong": tong,
            "loai_quota": "thang",
        }
    except ImportError:
        return ket_qua
    except Exception:
        ket_qua["phan_tram"] = 100
        return ket_qua


def lay_quota(provider, key):
    ket_qua = {
        "provider": provider or "",
        "key_id": "",
        "phan_tram": None,
        "con_lai": None,
        "tong": None,
        "loai_quota": "",
        "thoi_gian": int(time.time()),
    }

    if not provider or not key:
        return ket_qua

    p = provider.strip()

    if p == "SERPJET":
        kq = _lay_quota_serpjet(key)
    elif p == "Tavily":
        kq = _lay_quota_tavily(key)
    elif p == "Bright Data":
        kq = _lay_quota_brightdata(key)
    else:
        return ket_qua

    ket_qua.update(kq)
    return ket_qua


def cap_nhat_quota(key_id, phan_tram):
    if not key_id:
        return False

    try:
        from luu_tru.ghi_nho import cap_nhat_quota_key
        return cap_nhat_quota_key(key_id, phan_tram)
    except Exception as e:
        _ghi_log("loi", f"Cập nhật quota tra web lỗi: {e}")
        return False


def lay_quota_tu_kho(key_id):
    if not key_id:
        return {}

    try:
        from luu_tru.ghi_nho import lay_key_da_luu
        key = lay_key_da_luu(key_id)
        if not key:
            return {}
        return {
            "phan_tram": key.get("phan_tram", 100),
            "lan_kiem_tra_cuoi": key.get("lan_kiem_tra_cuoi", 0),
        }
    except Exception:
        return {}


def cap_nhat_tat_ca(chu_so_huu):
    ket_qua = []

    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_web_cua
        danh_sach = lay_danh_sach_key_web_cua(chu_so_huu) or []
    except ImportError:
        return ket_qua

    for key_info in danh_sach:
        provider = key_info.get("provider", "")
        key = key_info.get("key", "")
        key_id = key_info.get("id", "")

        kq = lay_quota(provider, key)
        kq["key_id"] = key_id

        if kq.get("phan_tram") is not None:
            cap_nhat_quota(key_id, kq["phan_tram"])

        ket_qua.append(kq)

    _ghi_log(
        "tra-web",
        f"Cập nhật quota {len(ket_qua)} key tra web cho {chu_so_huu}",
    )
    return ket_qua


def lay_quota_chi_tiet(chu_so_huu):
    ket_qua = {"SERPJET": [], "Tavily": [], "Bright Data": []}

    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_web_cua
        danh_sach = lay_danh_sach_key_web_cua(chu_so_huu) or []
    except ImportError:
        return ket_qua

    for key_info in danh_sach:
        provider = key_info.get("provider", "")
        key = key_info.get("key", "")
        key_id = key_info.get("id", "")

        kq = lay_quota(provider, key)
        kq["key_id"] = key_id

        if provider in ket_qua:
            ket_qua[provider].append(kq)

    return ket_qua


def lay_mau_quota(phan_tram):
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
    mau = lay_mau_quota(phan_tram)
    bang = {
        "xanh": "quota-xanh",
        "vang": "quota-vang",
        "do": "quota-do",
        "den": "quota-den",
        "khong_ro": "",
    }
    return bang.get(mau, "")


def tong_hop_quota(chu_so_huu):
    chi_tiet = lay_quota_chi_tiet(chu_so_huu)

    tat_ca = []
    for ds in chi_tiet.values():
        tat_ca.extend([k.get("phan_tram") for k in ds if k.get("phan_tram") is not None])

    if not tat_ca:
        return {"phan_tram_tb": 100, "so_key": 0, "mau": "khong_ro"}

    phan_tram_tb = int(sum(tat_ca) / len(tat_ca))
    return {
        "phan_tram_tb": phan_tram_tb,
        "so_key": len(tat_ca),
        "mau": lay_mau_quota(phan_tram_tb),
    }


def tom_tat_quota(chu_so_huu):
    chi_tiet = lay_quota_chi_tiet(chu_so_huu)
    phan = []

    for provider in ["SERPJET", "Tavily", "Bright Data"]:
        danh_sach = chi_tiet.get(provider, [])
        if not danh_sach:
            continue

        phan.append(f"📊 {provider}:")
        for kq in danh_sach:
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

    return "\n".join(phan) if phan else "❌ Không có key tra web."


def can_cap_nhat_lai(key_id, nguong_giay=60):
    if not key_id:
        return True

    kq = lay_quota_tu_kho(key_id)
    lan_cuoi = kq.get("lan_kiem_tra_cuoi", 0)
    if not lan_cuoi:
        return True

    return (int(time.time()) - lan_cuoi) > nguong_giay


def quota_thap_nhat(chu_so_huu):
    chi_tiet = lay_quota_chi_tiet(chu_so_huu)
    tat_ca = []
    for ds in chi_tiet.values():
        tat_ca.extend([k for k in ds if k.get("phan_tram") is not None])

    if not tat_ca:
        return None

    tat_ca.sort(key=lambda k: k.get("phan_tram", 100))
    return tat_ca[0]


def dem_key_theo_mau(chu_so_huu):
    chi_tiet = lay_quota_chi_tiet(chu_so_huu)
    dem = {"xanh": 0, "vang": 0, "do": 0, "den": 0, "khong_ro": 0}

    for ds in chi_tiet.values():
        for kq in ds:
            mau = lay_mau_quota(kq.get("phan_tram"))
            dem[mau] = dem.get(mau, 0) + 1

    return dem


def key_con_dung_duoc(chu_so_huu, nguong=20):
    chi_tiet = lay_quota_chi_tiet(chu_so_huu)
    ket_qua = []

    for ds in chi_tiet.values():
        for kq in ds:
            if kq.get("phan_tram") is not None and kq["phan_tram"] >= nguong:
                ket_qua.append(kq)

    return ket_qua


def danh_sach_api_ho_tro():
    return ["SERPJET", "Tavily", "Bright Data"]


def quota_mac_dinh(provider):
    return QUOTA_MAC_DINH.get(provider, 0)
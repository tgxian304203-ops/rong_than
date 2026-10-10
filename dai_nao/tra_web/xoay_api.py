"""
xoay_api.py - Quản lý xoay API Tra web Rồng Thần.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho.
"""

import time


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


THU_TU_API = ["SERPJET", "Tavily", "Bright Data"]

QUOTA_MAC_DINH = {
    "SERPJET": 1000,
    "Tavily": 1000,
    "Bright Data": 5000,
}


def _collection_trang_thai():
    try:
        from luu_tru.ghi_nho import _ket_noi_kho_2
        db, _ = _ket_noi_kho_2()
        if db is None:
            return None
        return db["trang_thai_api_tra_web"]
    except Exception:
        return None


def _lay_danh_sach_api(chu_so_huu):
    if not chu_so_huu:
        return []

    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_web_cua
        danh_sach_key = lay_danh_sach_key_web_cua(chu_so_huu) or []
    except ImportError:
        return []
    except Exception:
        return []

    ket_qua = []
    for key in danh_sach_key:
        provider = (key.get("provider") or "").strip()
        if provider in THU_TU_API:
            ket_qua.append(key)

    return ket_qua


def danh_dau_het_quota(provider, key_id=""):
    if not provider:
        return False

    col = _collection_trang_thai()
    if col is None:
        return False

    now = time.localtime()
    thang_sau = now.tm_mon + 1
    nam_sau = now.tm_year
    if thang_sau > 12:
        thang_sau = 1
        nam_sau += 1

    thoi_gian_hoi = int(time.mktime((
        nam_sau, thang_sau, 1, 0, 0, 0, 0, 0, -1
    )))

    try:
        col.update_one(
            {"provider": provider, "key_id": key_id},
            {
                "$set": {
                    "provider": provider,
                    "key_id": key_id,
                    "het_quota": True,
                    "thoi_gian_het": int(time.time()),
                    "thoi_gian_hoi": thoi_gian_hoi,
                }
            },
            upsert=True,
        )
        _ghi_log("tra-web", f"Đánh dấu {provider} hết quota.")
        return True
    except Exception:
        return False


def kiem_tra_hoi_quota(provider, key_id=""):
    if not provider:
        return True

    col = _collection_trang_thai()
    if col is None:
        return True

    try:
        trang_thai = col.find_one({"provider": provider, "key_id": key_id})
        if not trang_thai:
            return True

        if not trang_thai.get("het_quota"):
            return True

        thoi_gian_hoi = trang_thai.get("thoi_gian_hoi", 0)
        if not thoi_gian_hoi:
            return True

        if int(time.time()) >= thoi_gian_hoi:
            col.update_one(
                {"provider": provider, "key_id": key_id},
                {"$set": {"het_quota": False, "thoi_gian_hoi_phuc": int(time.time())}},
            )
            _ghi_log("tra-web", f"{provider} đã hồi quota.")
            return True

        return False
    except Exception:
        return True


def api_tiep_theo(danh_sach_api, api_hien_tai=""):
    if not danh_sach_api:
        return None

    danh_sach_sap_xep = []
    for provider in THU_TU_API:
        for api in danh_sach_api:
            if api.get("provider") == provider:
                danh_sach_sap_xep.append(api)

    if not api_hien_tai:
        for api in danh_sach_sap_xep:
            if kiem_tra_hoi_quota(api.get("provider"), api.get("id", "")):
                return api
        return None

    vi_tri = -1
    for i, api in enumerate(danh_sach_sap_xep):
        if api.get("provider") == api_hien_tai:
            vi_tri = i
            break

    if vi_tri >= 0:
        for i in range(vi_tri + 1, len(danh_sach_sap_xep)):
            if kiem_tra_hoi_quota(danh_sach_sap_xep[i].get("provider"),
                                  danh_sach_sap_xep[i].get("id", "")):
                return danh_sach_sap_xep[i]

    for i in range(0, vi_tri if vi_tri >= 0 else len(danh_sach_sap_xep)):
        if kiem_tra_hoi_quota(danh_sach_sap_xep[i].get("provider"),
                              danh_sach_sap_xep[i].get("id", "")):
            _ghi_log("tra-web", "Hết API → quay lại từ đầu.")
            return danh_sach_sap_xep[i]

    return None


def xoay_vong(danh_sach_api):
    if not danh_sach_api:
        return []

    con_dung = []
    het_quota = []

    for api in danh_sach_api:
        provider = api.get("provider", "")
        key_id = api.get("id", "")
        if kiem_tra_hoi_quota(provider, key_id):
            con_dung.append(api)
        else:
            het_quota.append(api)

    return con_dung + het_quota


def xoay_api(chu_so_huu, api_hien_tai=""):
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        _ghi_log("tra-web", f"Không có API tra web cho {chu_so_huu}.")
        return None

    danh_sach_moi = xoay_vong(danh_sach)
    api_tiep = api_tiep_theo(danh_sach_moi, api_hien_tai)

    if api_tiep:
        _ghi_log("tra-web", f"Xoay sang API: {api_tiep.get('provider')}")

    return api_tiep


def dem_api_con_dung(chu_so_huu):
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return 0

    dem = 0
    for api in danh_sach:
        if kiem_tra_hoi_quota(api.get("provider"), api.get("id", "")):
            dem += 1
    return dem


def dem_api_het_quota(chu_so_huu):
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return 0

    dem = 0
    for api in danh_sach:
        if not kiem_tra_hoi_quota(api.get("provider"), api.get("id", "")):
            dem += 1
    return dem


def xoa_trang_thai(provider, key_id=""):
    col = _collection_trang_thai()
    if col is None:
        return False

    try:
        col.delete_one({"provider": provider, "key_id": key_id})
        return True
    except Exception:
        return False


def reset_tat_ca(chu_so_huu):
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return False

    for api in danh_sach:
        xoa_trang_thai(api.get("provider"), api.get("id", ""))

    _ghi_log("tra-web", f"Reset trạng thái API tra web cho {chu_so_huu}")
    return True


def tom_tat_trang_thai(chu_so_huu):
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return "❌ Không có API tra web."

    phan = []
    for api in danh_sach:
        provider = api.get("provider", "")
        key_id = api.get("id", "")[:8]
        con_dung = kiem_tra_hoi_quota(provider, api.get("id", ""))
        bieu_tuong = "✅" if con_dung else "⏸️"
        phan.append(f"{bieu_tuong} {provider} / {key_id}")

    return "\n".join(phan)


def thoi_gian_hoi_gan_nhat(chu_so_huu):
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return None

    col = _collection_trang_thai()
    if col is None:
        return None

    thoi_gian_min = None
    now = int(time.time())

    for api in danh_sach:
        provider = api.get("provider")
        key_id = api.get("id", "")

        if kiem_tra_hoi_quota(provider, key_id):
            return 0

        try:
            trang_thai = col.find_one({"provider": provider, "key_id": key_id})
            if not trang_thai:
                continue
            thoi_gian_hoi = trang_thai.get("thoi_gian_hoi", 0)
            if thoi_gian_hoi:
                con_lai = max(0, thoi_gian_hoi - now)
                if thoi_gian_min is None or con_lai < thoi_gian_min:
                    thoi_gian_min = con_lai
        except Exception:
            continue

    return thoi_gian_min


def lay_trang_thai_chi_tiet(chu_so_huu):
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return []

    col = _collection_trang_thai()

    ket_qua = []
    for api in danh_sach:
        provider = api.get("provider", "")
        key_id = api.get("id", "")

        trang_thai = {}
        if col is not None:
            try:
                trang_thai = col.find_one({"provider": provider, "key_id": key_id}) or {}
            except Exception:
                trang_thai = {}

        ket_qua.append({
            "provider": provider,
            "key_id": key_id,
            "con_dung": kiem_tra_hoi_quota(provider, key_id),
            "het_quota": trang_thai.get("het_quota", False),
            "thoi_gian_hoi": trang_thai.get("thoi_gian_hoi", 0),
        })

    return ket_qua


def danh_sach_api_ho_tro():
    return list(THU_TU_API)


def quota_mac_dinh(provider):
    return QUOTA_MAC_DINH.get(provider, 0)
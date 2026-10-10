"""
tong_hop.py - Tổng hợp kết quả Tra web Rồng Thần.
"""

import re


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


SO_KET_QUA_TOI_DA = 5
DO_DAI_MO_TA_TOI_DA = 300
DO_DAI_TONG_HOP_TOI_DA = 3000


def tong_hop(danh_sach_ket_qua, cau_hoi=""):
    if not danh_sach_ket_qua:
        return ""

    danh_sach = _loai_trung(danh_sach_ket_qua)

    if cau_hoi:
        danh_sach = _sap_xep_theo_lien_quan(danh_sach, cau_hoi)

    danh_sach = danh_sach[:SO_KET_QUA_TOI_DA]

    phan = []
    for i, item in enumerate(danh_sach, 1):
        tieu_de = (item.get("tieu_de") or "").strip()
        mo_ta = (item.get("mo_ta") or "").strip()
        url = (item.get("url") or "").strip()

        if len(mo_ta) > DO_DAI_MO_TA_TOI_DA:
            mo_ta = mo_ta[:DO_DAI_MO_TA_TOI_DA].rstrip() + "..."

        dong = f"{i}. {tieu_de}" if tieu_de else f"{i}."
        if mo_ta:
            dong += f"\n   {mo_ta}"
        if url:
            dong += f"\n   🔗 {url}"

        phan.append(dong)

    ket_qua = "\n\n".join(phan)

    if len(ket_qua) > DO_DAI_TONG_HOP_TOI_DA:
        ket_qua = ket_qua[:DO_DAI_TONG_HOP_TOI_DA] + "\n\n..."

    return ket_qua


def tong_hop_co_noi_dung(danh_sach_ket_qua, noi_dung_dict=None, cau_hoi=""):
    if not danh_sach_ket_qua:
        return ""

    noi_dung_dict = noi_dung_dict or {}
    danh_sach = _loai_trung(danh_sach_ket_qua)

    if cau_hoi:
        danh_sach = _sap_xep_theo_lien_quan(danh_sach, cau_hoi)

    danh_sach = danh_sach[:SO_KET_QUA_TOI_DA]

    phan = []
    for i, item in enumerate(danh_sach, 1):
        tieu_de = (item.get("tieu_de") or "").strip()
        mo_ta = (item.get("mo_ta") or "").strip()
        url = (item.get("url") or "").strip()

        noi_dung = noi_dung_dict.get(url, "")
        if noi_dung:
            mo_ta = noi_dung[:DO_DAI_MO_TA_TOI_DA * 2]
        elif len(mo_ta) > DO_DAI_MO_TA_TOI_DA:
            mo_ta = mo_ta[:DO_DAI_MO_TA_TOI_DA].rstrip() + "..."

        dong = f"{i}. {tieu_de}" if tieu_de else f"{i}."
        if mo_ta:
            dong += f"\n   {mo_ta}"
        if url:
            dong += f"\n   🔗 {url}"

        phan.append(dong)

    ket_qua = "\n\n".join(phan)

    if len(ket_qua) > DO_DAI_TONG_HOP_TOI_DA:
        ket_qua = ket_qua[:DO_DAI_TONG_HOP_TOI_DA] + "\n\n..."

    return ket_qua


def _loai_trung(danh_sach):
    if not danh_sach:
        return []

    ban_do = {}

    for item in danh_sach:
        if not isinstance(item, dict):
            continue

        url = (item.get("url") or "").strip()

        if not url:
            khoa = (item.get("tieu_de") or "")[:100]
        else:
            khoa = _chuan_hoa_url(url)

        if not khoa:
            continue

        if khoa in ban_do:
            cu = ban_do[khoa]
            if len(item.get("mo_ta") or "") > len(cu.get("mo_ta") or ""):
                ban_do[khoa] = item
        else:
            ban_do[khoa] = item

    return list(ban_do.values())


def _chuan_hoa_url(url):
    if not url:
        return ""

    url = url.split("?")[0]
    url = url.rstrip("/")
    url = re.sub(r"^https?://(www\.)?", "https://", url)
    return url.lower()


def _sap_xep_theo_lien_quan(danh_sach, cau_hoi):
    if not danh_sach or not cau_hoi:
        return danh_sach

    tu_khoa = _trich_tu_khoa(cau_hoi)
    if not tu_khoa:
        return danh_sach

    def diem(item):
        tieu_de = (item.get("tieu_de") or "").lower()
        mo_ta = (item.get("mo_ta") or "").lower()
        url = (item.get("url") or "").lower()

        d = 0
        for tk in tu_khoa:
            if tk in tieu_de:
                d += 3
            if tk in mo_ta:
                d += 1
            if tk in url:
                d += 2

        return -d

    try:
        return sorted(danh_sach, key=diem)
    except Exception:
        return danh_sach


def _trich_tu_khoa(cau_hoi):
    if not cau_hoi:
        return []

    tu_dem = {
        "là", "gì", "của", "và", "có", "cho", "với", "thì",
        "một", "các", "những", "này", "đó", "kia", "được",
        "không", "như", "thế", "nào", "khi", "tại", "sao",
        "ai", "ở", "đâu", "bao", "nhiêu", "cách", "hãy",
        "cho", "tôi", "mình", "bạn", "về", "trong",
    }

    tu = re.findall(r"\b[a-zA-Zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]{3,}\b", cau_hoi.lower())

    ket_qua = []
    for t in tu:
        if t not in tu_dem and t not in ket_qua:
            ket_qua.append(t)

    return ket_qua[:10]


def _tao_tom_tat(danh_sach, so_luong=3):
    if not danh_sach:
        return ""

    phan = []
    for i, item in enumerate(danh_sach[:so_luong], 1):
        mo_ta = (item.get("mo_ta") or "").strip()
        if mo_ta:
            phan.append(mo_ta[:150])

    return "\n".join(phan)


def tong_hop_dict(danh_sach_ket_qua, cau_hoi=""):
    if not danh_sach_ket_qua:
        return {"tong": 0, "ket_qua": [], "tom_tat": "", "nguon": []}

    danh_sach = _loai_trung(danh_sach_ket_qua)
    if cau_hoi:
        danh_sach = _sap_xep_theo_lien_quan(danh_sach, cau_hoi)

    danh_sach = danh_sach[:SO_KET_QUA_TOI_DA]

    nguon = list(set([item.get("url", "").split("/")[2] for item in danh_sach if item.get("url") and "/" in item.get("url")]))

    return {
        "tong": len(danh_sach),
        "ket_qua": danh_sach,
        "tom_tat": _tao_tom_tat(danh_sach),
        "nguon": nguon[:5],
    }


def gop_mo_ta(danh_sach, so_luong=3):
    if not danh_sach:
        return ""

    phan = []
    for item in danh_sach[:so_luong]:
        mo_ta = (item.get("mo_ta") or "").strip()
        if mo_ta:
            phan.append(mo_ta)

    return "\n\n".join(phan)


def dem_url_duy_nhat(danh_sach):
    if not danh_sach:
        return 0

    da_gap = set()
    for item in danh_sach:
        url = _chuan_hoa_url(item.get("url", ""))
        if url:
            da_gap.add(url)

    return len(da_gap)


def loc_chat_luong(danh_sach, do_dai_mo_ta_toi_thieu=50):
    if not danh_sach:
        return []

    return [
        item for item in danh_sach
        if len((item.get("mo_ta") or "").strip()) >= do_dai_mo_ta_toi_thieu
    ]


def tom_tat_ngan(danh_sach, so_ky_tu=500):
    if not danh_sach:
        return ""

    ket_qua = tong_hop(danh_sach)
    if len(ket_qua) <= so_ky_tu:
        return ket_qua

    return ket_qua[:so_ky_tu].rstrip() + "..."
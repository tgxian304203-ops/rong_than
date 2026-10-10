"""
loc_log.py - Lọc log theo loại Rồng Thần.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho.
"""

import re
import time


SO_LOG_MAC_DINH = 100
SO_LOG_TOI_DA = 1000
LOAI_HOP_LE = ["dai-nao", "tieu-nao", "tra-web", "sandbox", "loi"]
LOAI_TAT_CA = ["tat-ca", "all", "", None]


def _chuan_hoa_loai(loai):
    if loai in LOAI_TAT_CA:
        return None
    if not loai:
        return None
    loai = str(loai).strip().lower()
    if loai in LOAI_TAT_CA:
        return None
    if loai in LOAI_HOP_LE:
        return loai
    return None


def _chuan_hoa_so_luong(so_luong):
    try:
        return max(1, min(SO_LOG_TOI_DA, int(so_luong)))
    except (ValueError, TypeError):
        return SO_LOG_MAC_DINH


def loc_log(loai="tat-ca", so_luong=SO_LOG_MAC_DINH):
    try:
        from logs.doc_log import doc_log
    except ImportError:
        return []

    loai_chuan = _chuan_hoa_loai(loai)
    so_luong = _chuan_hoa_so_luong(so_luong)

    return doc_log(so_luong, loai=loai_chuan, moi_nhat_truoc=True)


def loc_nhieu_loai(danh_sach_loai, so_luong=SO_LOG_MAC_DINH):
    if not danh_sach_loai:
        return loc_log("tat-ca", so_luong)

    loai_hop_le = [l for l in danh_sach_loai if l in LOAI_HOP_LE]
    if not loai_hop_le:
        return loc_log("tat-ca", so_luong)

    try:
        from luu_tru.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
    except ImportError:
        return []
    except Exception:
        return []

    if db is None:
        return []

    so_luong = _chuan_hoa_so_luong(so_luong)

    try:
        con_tro = (
            db["logs"]
            .find({"loai": {"$in": loai_hop_le}})
            .sort("thoi_gian", -1)
            .limit(so_luong)
        )

        try:
            from logs.doc_log import _chuan_hoa_log
            return [_chuan_hoa_log(log) for log in con_tro]
        except ImportError:
            return list(con_tro)
    except Exception:
        return []


def loc_theo_tu_khoa(tu_khoa, loai="tat-ca", so_luong=SO_LOG_MAC_DINH):
    if not tu_khoa:
        return loc_log(loai, so_luong)

    so_luong_lay = min(SO_LOG_TOI_DA, _chuan_hoa_so_luong(so_luong) * 5)
    danh_sach = loc_log(loai, so_luong_lay)

    if not danh_sach:
        return []

    try:
        tu_khoa_regex = re.compile(re.escape(tu_khoa.strip()), re.IGNORECASE)
    except re.error:
        return []

    ket_qua = []
    for log in danh_sach:
        noi_dung = log.get("noi_dung", "")
        if tu_khoa_regex.search(noi_dung):
            ket_qua.append(log)
            if len(ket_qua) >= so_luong:
                break

    return ket_qua


def loc_theo_thoi_gian(tu_thoi_gian, den_thoi_gian, loai="tat-ca",
                       so_luong=SO_LOG_MAC_DINH):
    try:
        from logs.doc_log import doc_log_theo_thoi_gian
    except ImportError:
        return []

    loai_chuan = _chuan_hoa_loai(loai)
    so_luong = _chuan_hoa_so_luong(so_luong)

    return doc_log_theo_thoi_gian(
        tu_thoi_gian, den_thoi_gian,
        loai=loai_chuan, so_luong=so_luong,
    )


def loc_ket_hop(loai="tat-ca", tu_khoa="", tu_thoi_gian=None,
                den_thoi_gian=None, so_luong=SO_LOG_MAC_DINH):
    so_luong = _chuan_hoa_so_luong(so_luong)

    if tu_thoi_gian and den_thoi_gian:
        danh_sach = loc_theo_thoi_gian(
            tu_thoi_gian, den_thoi_gian, loai,
            so_luong=min(SO_LOG_TOI_DA, so_luong * 5),
        )
    else:
        danh_sach = loc_log(loai, min(SO_LOG_TOI_DA, so_luong * 5))

    if not danh_sach:
        return []

    if tu_khoa:
        try:
            regex = re.compile(re.escape(tu_khoa.strip()), re.IGNORECASE)
            danh_sach = [log for log in danh_sach if regex.search(log.get("noi_dung", ""))]
        except re.error:
            pass

    return danh_sach[:so_luong]


def thong_ke_loc(loai="tat-ca"):
    loai_chuan = _chuan_hoa_loai(loai)

    try:
        from logs.doc_log import dem_log
        so_luong = dem_log(loai_chuan)
    except ImportError:
        so_luong = 0

    danh_sach = loc_log(loai, 5)

    return {
        "loai": loai_chuan or "tat-ca",
        "so_luong": so_luong,
        "moi_nhat": danh_sach,
    }


def loc_dai_nao(so_luong=SO_LOG_MAC_DINH):
    return loc_log("dai-nao", so_luong)


def loc_tieu_nao(so_luong=SO_LOG_MAC_DINH):
    return loc_log("tieu-nao", so_luong)


def loc_tra_web(so_luong=SO_LOG_MAC_DINH):
    return loc_log("tra-web", so_luong)


def loc_sandbox(so_luong=SO_LOG_MAC_DINH):
    return loc_log("sandbox", so_luong)


def loc_loi(so_luong=SO_LOG_MAC_DINH):
    return loc_log("loi", so_luong)


def loc_theo_nhieu_tu_khoa(danh_sach_tu_khoa, loai="tat-ca",
                           so_luong=SO_LOG_MAC_DINH):
    if not danh_sach_tu_khoa:
        return loc_log(loai, so_luong)

    try:
        mau = "|".join(re.escape(tk.strip()) for tk in danh_sach_tu_khoa if tk)
        if not mau:
            return loc_log(loai, so_luong)
        regex = re.compile(mau, re.IGNORECASE)
    except re.error:
        return loc_log(loai, so_luong)

    so_luong_lay = min(SO_LOG_TOI_DA, _chuan_hoa_so_luong(so_luong) * 5)
    danh_sach = loc_log(loai, so_luong_lay)

    ket_qua = []
    for log in danh_sach:
        if regex.search(log.get("noi_dung", "")):
            ket_qua.append(log)
            if len(ket_qua) >= so_luong:
                break

    return ket_qua


def loc_theo_do_dai(do_dai_toi_thieu=100, loai="tat-ca",
                    so_luong=SO_LOG_MAC_DINH):
    so_luong_lay = min(SO_LOG_TOI_DA, _chuan_hoa_so_luong(so_luong) * 3)
    danh_sach = loc_log(loai, so_luong_lay)

    ket_qua = []
    for log in danh_sach:
        if len(log.get("noi_dung", "")) >= do_dai_toi_thieu:
            ket_qua.append(log)
            if len(ket_qua) >= so_luong:
                break

    return ket_qua


def loc_hom_nay(loai="tat-ca", so_luong=SO_LOG_MAC_DINH):
    try:
        now = time.localtime()
        bat_dau_ngay = int(time.mktime((
            now.tm_year, now.tm_mon, now.tm_mday,
            0, 0, 0, 0, 0, -1,
        )))
        ket_thuc = int(time.time())

        return loc_theo_thoi_gian(bat_dau_ngay, ket_thuc, loai, so_luong)
    except Exception:
        return []


def loc_gan_day(so_gio=24, loai="tat-ca", so_luong=SO_LOG_MAC_DINH):
    try:
        ket_thuc = int(time.time())
        bat_dau = ket_thuc - so_gio * 3600

        return loc_theo_thoi_gian(bat_dau, ket_thuc, loai, so_luong)
    except Exception:
        return []


def danh_sach_bo_loc():
    return [
        {"ma": "tat-ca", "ten": "Tất cả"},
        {"ma": "dai-nao", "ten": "Đại não"},
        {"ma": "tieu-nao", "ten": "Tiểu não"},
        {"ma": "tra-web", "ten": "Tra web"},
        {"ma": "sandbox", "ten": "Sandbox"},
        {"ma": "loi", "ten": "Lỗi"},
    ]


def lay_theo_bo_loc(ma_bo_loc, so_luong=SO_LOG_MAC_DINH):
    return loc_log(ma_bo_loc, so_luong)


def dem_theo_bo_loc(ma_bo_loc):
    try:
        from logs.doc_log import dem_log
        loai_chuan = _chuan_hoa_loai(ma_bo_loc)
        return dem_log(loai_chuan)
    except ImportError:
        return 0
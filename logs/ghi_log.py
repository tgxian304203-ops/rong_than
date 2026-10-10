"""
ghi_log.py - Ghi log hoạt động Rồng Thần.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho.
"""

import os
import time


LOAI_HOP_LE = ["dai-nao", "tieu-nao", "tra-web", "sandbox", "loi"]

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_LOG_LOCAL = os.path.join(THU_MUC_GOC, "du_lieu", "nhat_ky.log")

NGAY = 24 * 3600
NGAY_XOA_LOG_CU = 30


def _ghi_file_local(loai, noi_dung, thoi_gian):
    try:
        os.makedirs(os.path.dirname(FILE_LOG_LOCAL), exist_ok=True)
        thoi_gian_str = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(thoi_gian)
        )
        noi_dung_ngan = str(noi_dung)[:500]
        dong = f"[{thoi_gian_str}] [{loai}] {noi_dung_ngan}\n"
        with open(FILE_LOG_LOCAL, "a", encoding="utf-8") as f:
            f.write(dong)
        return True
    except Exception:
        return False


def _ghi_kho_1(loai, noi_dung, thoi_gian):
    try:
        from luu_tru.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
        if db is None:
            return False
        db["logs"].insert_one({
            "thoi_gian": thoi_gian,
            "loai": loai,
            "noi_dung": str(noi_dung)[:500],
        })
        return True
    except Exception:
        return False


def ghi_log(loai, noi_dung):
    if not loai or not noi_dung:
        return False

    loai = str(loai).strip().lower()
    if loai not in LOAI_HOP_LE:
        loai = "loi"

    thoi_gian = int(time.time())

    ket_qua_file = _ghi_file_local(loai, noi_dung, thoi_gian)
    ket_qua_db = _ghi_kho_1(loai, noi_dung, thoi_gian)

    return ket_qua_file or ket_qua_db


def ghi_log_dai_nao(noi_dung):
    return ghi_log("dai-nao", noi_dung)


def ghi_log_tieu_nao(noi_dung):
    return ghi_log("tieu-nao", noi_dung)


def ghi_log_tra_web(noi_dung):
    return ghi_log("tra-web", noi_dung)


def ghi_log_sandbox(noi_dung):
    return ghi_log("sandbox", noi_dung)


def ghi_log_loi(noi_dung):
    return ghi_log("loi", noi_dung)


def ghi_nhanh(noi_dung, loai_mac_dinh="dai-nao"):
    if not noi_dung:
        return False

    t = str(noi_dung).lower()

    if "lỗi" in t or "error" in t or "fail" in t:
        loai = "loi"
    elif "tiểu não" in t or "tieu-nao" in t or "model" in t:
        loai = "tieu-nao"
    elif "tra web" in t or "search" in t or "serpjet" in t or "tavily" in t:
        loai = "tra-web"
    elif "sandbox" in t or "chạy code" in t or "pyodide" in t:
        loai = "sandbox"
    else:
        loai = loai_mac_dinh

    return ghi_log(loai, noi_dung)


def xoa_log_cu(ngay=NGAY_XOA_LOG_CU):
    if ngay < 1:
        return 0

    nguong = int(time.time()) - ngay * NGAY

    try:
        from luu_tru.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
        if db is None:
            return 0
        ket_qua = db["logs"].delete_many({
            "thoi_gian": {"$lt": nguong},
        })
        return ket_qua.deleted_count
    except Exception:
        return 0


def xoa_tat_ca_log():
    try:
        from luu_tru.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
        if db is None:
            return 0
        ket_qua = db["logs"].delete_many({})
        return ket_qua.deleted_count
    except Exception:
        return 0


def dem_log(loai=None):
    try:
        from luu_tru.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
        if db is None:
            return 0

        dieu_kien = {}
        if loai:
            dieu_kien["loai"] = loai

        return db["logs"].count_documents(dieu_kien)
    except Exception:
        return 0


def ghi_log_co_thoi_gian(loai, noi_dung, thoi_gian_bat_dau):
    try:
        thoi_gian_chay = round(time.time() - thoi_gian_bat_dau, 3)
        noi_dung_full = f"{noi_dung} ({thoi_gian_chay}s)"
        return ghi_log(loai, noi_dung_full)
    except Exception:
        return ghi_log(loai, noi_dung)


def ghi_nhieu(danh_sach_log):
    if not danh_sach_log:
        return 0

    dem = 0
    for item in danh_sach_log:
        if isinstance(item, dict):
            loai = item.get("loai", "")
            noi_dung = item.get("noi_dung", "")
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            loai, noi_dung = item[0], item[1]
        else:
            continue

        if ghi_log(loai, noi_dung):
            dem += 1

    return dem


def danh_sach_loai_log():
    return list(LOAI_HOP_LE)


def loai_hop_le(loai):
    return loai in LOAI_HOP_LE
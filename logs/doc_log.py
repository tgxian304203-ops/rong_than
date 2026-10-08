"""
doc_log.py - Đọc log cho giao diện Rồng Thần.

ĐÃ SỬA:
    - FIX: Format thời gian theo giờ VIỆT NAM (UTC+7) cố định,
           không phụ thuộc server.
"""

import time


# ================================================================
# HẰNG SỐ
# ================================================================
SO_LOG_MAC_DINH = 100
SO_LOG_TOI_DA = 1000
LOAI_HOP_LE = ["dai-nao", "tieu-nao", "tra-web", "sandbox", "loi"]

# Múi giờ Việt Nam = UTC+7
TZ_VIET_NAM = 7 * 3600


# ================================================================
# ĐỊNH DẠNG THỜI GIAN — THEO GIỜ VIỆT NAM (UTC+7)
# ================================================================
def _dinh_dang_thoi_gian(timestamp):
    """
    Định dạng timestamp thành chuỗi đọc được — LUÔN THEO UTC+7.

    Trả về: "HH:MM:SS" hoặc "YYYY-MM-DD HH:MM:SS" nếu khác ngày.
    """
    if not timestamp:
        return ""

    try:
        now_vn = time.gmtime(time.time() + TZ_VIET_NAM)
        tg_vn = time.gmtime(int(timestamp) + TZ_VIET_NAM)

        # Cùng ngày (theo giờ VN) → chỉ hiện giờ
        if (tg_vn.tm_year, tg_vn.tm_mon, tg_vn.tm_mday) == \
           (now_vn.tm_year, now_vn.tm_mon, now_vn.tm_mday):
            return time.strftime("%H:%M:%S", tg_vn)

        # Khác ngày → hiện đầy đủ
        return time.strftime("%Y-%m-%d %H:%M:%S", tg_vn)
    except (ValueError, OSError):
        return ""


def _chuan_hoa_log(log):
    """Chuẩn hóa 1 log về dict đúng format."""
    if not log or not isinstance(log, dict):
        return {}

    tg = log.get("thoi_gian", 0)

    id_str = ""
    if "_id" in log:
        try:
            id_str = str(log["_id"])
        except Exception:
            id_str = ""

    return {
        "id": id_str,
        "thoi_gian": tg,
        "thoi_gian_hien_thi": _dinh_dang_thoi_gian(tg),
        "loai": log.get("loai", ""),
        "noi_dung": log.get("noi_dung", ""),
    }


# ================================================================
# HÀM CHÍNH: ĐỌC LOG
# ================================================================
def doc_log(so_luong=SO_LOG_MAC_DINH, loai=None, moi_nhat_truoc=True):
    """Đọc log từ kho 1."""
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
    except ImportError:
        return []
    except Exception:
        return []

    try:
        so_luong = max(1, min(SO_LOG_TOI_DA, int(so_luong)))
    except (ValueError, TypeError):
        so_luong = SO_LOG_MAC_DINH

    dieu_kien = {}
    if loai and loai in LOAI_HOP_LE:
        dieu_kien["loai"] = loai

    try:
        huong = -1 if moi_nhat_truoc else 1
        con_tro = db["logs"].find(dieu_kien).sort("thoi_gian", huong).limit(so_luong)
        danh_sach = [_chuan_hoa_log(log) for log in con_tro]
        return [log for log in danh_sach if log]
    except Exception:
        return []


# ================================================================
# ĐỌC LOG MỚI NHẤT
# ================================================================
def doc_log_moi_nhat(so_luong=SO_LOG_MAC_DINH):
    return doc_log(so_luong, loai=None, moi_nhat_truoc=True)


# ================================================================
# ĐỌC LOG THEO LOẠI
# ================================================================
def doc_log_theo_loai(loai, so_luong=SO_LOG_MAC_DINH):
    return doc_log(so_luong, loai=loai, moi_nhat_truoc=True)


# ================================================================
# ĐỌC LOG THEO THỜI GIAN
# ================================================================
def doc_log_theo_thoi_gian(tu_thoi_gian, den_thoi_gian, loai=None,
                          so_luong=SO_LOG_MAC_DINH):
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
    except ImportError:
        return []
    except Exception:
        return []

    try:
        so_luong = max(1, min(SO_LOG_TOI_DA, int(so_luong)))
    except (ValueError, TypeError):
        so_luong = SO_LOG_MAC_DINH

    dieu_kien = {
        "thoi_gian": {
            "$gte": int(tu_thoi_gian),
            "$lte": int(den_thoi_gian),
        }
    }
    if loai and loai in LOAI_HOP_LE:
        dieu_kien["loai"] = loai

    try:
        con_tro = db["logs"].find(dieu_kien).sort("thoi_gian", -1).limit(so_luong)
        danh_sach = [_chuan_hoa_log(log) for log in con_tro]
        return [log for log in danh_sach if log]
    except Exception:
        return []


# ================================================================
# ĐỌC TOÀN BỘ LOG
# ================================================================
def doc_log_tat_ca(loai=None):
    return doc_log(SO_LOG_TOI_DA, loai=loai, moi_nhat_truoc=True)


# ================================================================
# XÓA LOG
# ================================================================
def xoa_log(loai=None):
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
    except ImportError:
        return 0
    except Exception:
        return 0

    dieu_kien = {}
    if loai and loai in LOAI_HOP_LE:
        dieu_kien["loai"] = loai

    try:
        ket_qua = db["logs"].delete_many(dieu_kien)
        return ket_qua.deleted_count
    except Exception:
        return 0


def xoa_log_cu(ngay=30):
    if ngay < 1:
        return 0

    nguong = int(time.time()) - ngay * 24 * 3600

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
        ket_qua = db["logs"].delete_many({
            "thoi_gian": {"$lt": nguong},
        })
        return ket_qua.deleted_count
    except Exception:
        return 0


# ================================================================
# ĐẾM LOG
# ================================================================
def dem_log(loai=None):
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()

        dieu_kien = {}
        if loai and loai in LOAI_HOP_LE:
            dieu_kien["loai"] = loai

        return db["logs"].count_documents(dieu_kien)
    except Exception:
        return 0


def dem_log_theo_loai():
    ket_qua = {loai: 0 for loai in LOAI_HOP_LE}

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()

        for loai in LOAI_HOP_LE:
            ket_qua[loai] = db["logs"].count_documents({"loai": loai})

        ket_qua["tong"] = db["logs"].count_documents({})
    except Exception:
        ket_qua["tong"] = 0

    return ket_qua


# ================================================================
# TẢI LOG VỀ MÁY
# ================================================================
def xuat_log_thanh_chuoi(loai=None, so_luong=SO_LOG_TOI_DA):
    danh_sach = doc_log(so_luong, loai=loai, moi_nhat_truoc=False)

    if not danh_sach:
        return ""

    phan = []
    for log in danh_sach:
        tg = log.get("thoi_gian_hien_thi", "")
        loai_log = log.get("loai", "")
        noi_dung = log.get("noi_dung", "")
        phan.append(f"[{tg}] [{loai_log}] {noi_dung}")

    return "\n".join(phan)


# ================================================================
# HÀM PHỤ
# ================================================================
def lay_5_log_gan_nhat():
    return doc_log_moi_nhat(5)


def dem_log_hom_nay(loai=None):
    try:
        now_vn = time.gmtime(time.time() + TZ_VIET_NAM)
        bat_dau_ngay_vn = int(
            time.mktime((now_vn.tm_year, now_vn.tm_mon, now_vn.tm_mday,
                         0, 0, 0, 0, 0, -1))
        ) - TZ_VIET_NAM

        danh_sach = doc_log_theo_thoi_gian(bat_dau_ngay_vn, int(time.time()), loai=loai)
        return len(danh_sach)
    except Exception:
        return 0


def thong_ke_nhanh():
    return {
        "tong": dem_log(),
        "hom_nay": dem_log_hom_nay(),
        "theo_loai": dem_log_theo_loai(),
        "moi_nhat": lay_5_log_gan_nhat(),
    }


def danh_sach_loai_log():
    return list(LOAI_HOP_LE)


def loai_hop_le(loai):
    return loai in LOAI_HOP_LE
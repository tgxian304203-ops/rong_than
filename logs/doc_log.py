"""
doc_log.py - Đọc log cho giao diện Rồng Thần.

Nhiệm vụ:
    - doc_log(so_luong, loai): đọc log từ kho 1.
    - doc_log_moi_nhat(so_luong): đọc N log mới nhất.
    - doc_log_theo_loai(loai, so_luong): đọc log theo loại.
    - doc_log_theo_thoi_gian(tu, den): đọc log trong khoảng thời gian.
    - doc_log_tat_ca(): đọc toàn bộ log.
    - xoa_log(loai): xóa log (tất cả hoặc theo loại).
    - dem_log_theo_loai(): đếm log theo từng loại.

Quy tắc (theo Phần 4):
    - Đọc log từ kho 1, collection logs.
    - Trả về list dict { thoi_gian, loai, noi_dung }.
    - Sắp xếp mới nhất trước.
    - Định dạng thời gian cho hiển thị.

Trả về:
    - list log hoặc dict thống kê.

Tầng dữ liệu: dai_nao/ghi_nho.py (kho 1).
"""

import time


# ================================================================
# HẰNG SỐ
# ================================================================
SO_LOG_MAC_DINH = 100
SO_LOG_TOI_DA = 1000
LOAI_HOP_LE = ["dai-nao", "tieu-nao", "tra-web", "sandbox", "loi"]


# ================================================================
# ĐỊNH DẠNG THỜI GIAN
# ================================================================
def _dinh_dang_thoi_gian(timestamp):
    """
    Định dạng timestamp thành chuỗi đọc được.

    Trả về: "HH:MM:SS" hoặc "YYYY-MM-DD HH:MM:SS" nếu khác ngày.
    """
    if not timestamp:
        return ""

    try:
        now = time.localtime()
        tg = time.localtime(int(timestamp))

        # Cùng ngày → chỉ hiện giờ
        if (tg.tm_year, tg.tm_mon, tg.tm_mday) == (now.tm_year, now.tm_mon, now.tm_mday):
            return time.strftime("%H:%M:%S", tg)

        # Khác ngày → hiện đầy đủ
        return time.strftime("%Y-%m-%d %H:%M:%S", tg)
    except (ValueError, OSError):
        return ""


def _chuan_hoa_log(log):
    """
    Chuẩn hóa 1 log về dict đúng format.

    Trả về: {
        thoi_gian, thoi_gian_hien_thi, loai, noi_dung,
    }
    """
    if not log or not isinstance(log, dict):
        return {}

    tg = log.get("thoi_gian", 0)

    # Chuyển ObjectId _id thành str (nếu có)
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
    """
    Đọc log từ kho 1.

    so_luong: số log cần đọc (tối đa 1000).
    loai: lọc theo loại (None = tất cả).
    moi_nhat_truoc: True → mới nhất trước.

    Trả về: list log đã chuẩn hóa.
    """
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
    except ImportError:
        return []
    except Exception:
        return []

    # Chuẩn hóa số lượng
    try:
        so_luong = max(1, min(SO_LOG_TOI_DA, int(so_luong)))
    except (ValueError, TypeError):
        so_luong = SO_LOG_MAC_DINH

    # Điều kiện lọc
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
    """Đọc N log mới nhất."""
    return doc_log(so_luong, loai=None, moi_nhat_truoc=True)


# ================================================================
# ĐỌC LOG THEO LOẠI
# ================================================================
def doc_log_theo_loai(loai, so_luong=SO_LOG_MAC_DINH):
    """Đọc log theo loại."""
    return doc_log(so_luong, loai=loai, moi_nhat_truoc=True)


# ================================================================
# ĐỌC LOG THEO THỜI GIAN
# ================================================================
def doc_log_theo_thoi_gian(tu_thoi_gian, den_thoi_gian, loai=None,
                          so_luong=SO_LOG_MAC_DINH):
    """
    Đọc log trong khoảng thời gian.

    tu_thoi_gian: timestamp bắt đầu.
    den_thoi_gian: timestamp kết thúc.
    """
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
    """Đọc toàn bộ log (tối đa 1000)."""
    return doc_log(SO_LOG_TOI_DA, loai=loai, moi_nhat_truoc=True)


# ================================================================
# XÓA LOG
# ================================================================
def xoa_log(loai=None):
    """
    Xóa log khỏi kho 1.

    loai: None → xóa tất cả, hoặc tên loại cụ thể.

    Trả về: số log đã xóa.
    """
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
    """
    Xóa log cũ hơn N ngày.

    Trả về: số log đã xóa.
    """
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
    """Đếm số log."""
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
    """
    Đếm log theo từng loại.

    Trả về: dict { "dai-nao": N, "tieu-nao": N, ... }.
    """
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
    """
    Xuất log thành chuỗi để tải về máy.

    Trả về: chuỗi text.
    """
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
# HÀM PHỤ: LẤY NHANH 5 LOG GẦN NHẤT
# ================================================================
def lay_5_log_gan_nhat():
    """Lấy 5 log gần nhất để hiển thị nhanh."""
    return doc_log_moi_nhat(5)


# ================================================================
# HÀM PHỤ: ĐẾM LOG TRONG NGÀY
# ================================================================
def dem_log_hom_nay(loai=None):
    """Đếm số log của ngày hôm nay."""
    try:
        now = time.localtime()
        bat_dau_ngay = int(time.mktime((
            now.tm_year, now.tm_mon, now.tm_mday,
            0, 0, 0, 0, 0, -1,
        )))

        danh_sach = doc_log_theo_thoi_gian(bat_dau_ngay, int(time.time()), loai=loai)
        return len(danh_sach)
    except Exception:
        return 0


# ================================================================
# HÀM PHỤ: LẤY THỐNG KÊ NHANH
# ================================================================
def thong_ke_nhanh():
    """
    Lấy thống kê nhanh cho dashboard.

    Trả về: {
        tong, hom_nay, theo_loai, moi_nhat
    }
    """
    return {
        "tong": dem_log(),
        "hom_nay": dem_log_hom_nay(),
        "theo_loai": dem_log_theo_loai(),
        "moi_nhat": lay_5_log_gan_nhat(),
    }


# ================================================================
# HÀM PHỤ: DANH SÁCH LOẠI LOG
# ================================================================
def danh_sach_loai_log():
    """Trả danh sách 5 loại log."""
    return list(LOAI_HOP_LE)


def loai_hop_le(loai):
    """Kiểm tra loại log có hợp lệ không."""
    return loai in LOAI_HOP_LE
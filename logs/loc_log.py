"""
loc_log.py - Lọc log theo loại Rồng Thần.

Nhiệm vụ:
    - loc_log(loai, so_luong): lọc log theo loại.
    - loc_nhieu_loai(danh_sach_loai, so_luong): lọc theo nhiều loại.
    - loc_theo_tu_khoa(tu_khoa, so_luong): lọc theo từ khóa trong nội dung.
    - loc_theo_thoi_gian(tu, den, loai): lọc theo thời gian.
    - loc_ket_hop(loai, tu_khoa, tu_thoi_gian, den_thoi_gian): lọc kết hợp.
    - thong_ke_loc(loai): thống kê theo bộ lọc.

Quy tắc (theo Phần 4):
    - 5 loại log: dai-nao, tieu-nao, tra-web, sandbox, loi.
    - Bộ lọc "Tất cả" → không lọc.
    - Sắp xếp mới nhất trước.
    - Giới hạn 1-1000 log.
    - Có hỗ trợ lọc theo từ khóa.

Trả về:
    - list log đã lọc.

Tầng dữ liệu: dai_nao/ghi_nho.py (kho 1).
"""

import re
import time


# ================================================================
# HẰNG SỐ
# ================================================================
SO_LOG_MAC_DINH = 100
SO_LOG_TOI_DA = 1000
LOAI_HOP_LE = ["dai-nao", "tieu-nao", "tra-web", "sandbox", "loi"]
LOAI_TAT_CA = ["tat-ca", "all", "", None]


# ================================================================
# CHUẨN HÓA LOẠI
# ================================================================
def _chuan_hoa_loai(loai):
    """
    Chuẩn hóa loại log.

    Trả về: tên loại hoặc None (nếu lọc tất cả).
    """
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
    """Chuẩn hóa số lượng log."""
    try:
        return max(1, min(SO_LOG_TOI_DA, int(so_luong)))
    except (ValueError, TypeError):
        return SO_LOG_MAC_DINH


# ================================================================
# LỌC LOG THEO LOẠI
# ================================================================
def loc_log(loai="tat-ca", so_luong=SO_LOG_MAC_DINH):
    """
    Lọc log theo loại.

    loai: "tat-ca" | "dai-nao" | "tieu-nao" | "tra-web" | "sandbox" | "loi".
    so_luong: số log tối đa.

    Trả về: list log.
    """
    try:
        from logs.doc_log import doc_log
    except ImportError:
        return []

    loai_chuan = _chuan_hoa_loai(loai)
    so_luong = _chuan_hoa_so_luong(so_luong)

    return doc_log(so_luong, loai=loai_chuan, moi_nhat_truoc=True)


# ================================================================
# LỌC NHIỀU LOẠI
# ================================================================
def loc_nhieu_loai(danh_sach_loai, so_luong=SO_LOG_MAC_DINH):
    """
    Lọc log theo nhiều loại cùng lúc.

    danh_sach_loai: list tên loại.

    Trả về: list log.
    """
    if not danh_sach_loai:
        return loc_log("tat-ca", so_luong)

    # Chuẩn hóa danh sách
    loai_hop_le = [l for l in danh_sach_loai if l in LOAI_HOP_LE]
    if not loai_hop_le:
        return loc_log("tat-ca", so_luong)

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
    except ImportError:
        return []
    except Exception:
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


# ================================================================
# LỌC THEO TỪ KHÓA
# ================================================================
def loc_theo_tu_khoa(tu_khoa, loai="tat-ca", so_luong=SO_LOG_MAC_DINH):
    """
    Lọc log có chứa từ khóa trong nội dung.

    tu_khoa: chuỗi cần tìm (không phân biệt hoa/thường).
    """
    if not tu_khoa:
        return loc_log(loai, so_luong)

    # Lấy nhiều log hơn để lọc
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


# ================================================================
# LỌC THEO THỜI GIAN
# ================================================================
def loc_theo_thoi_gian(tu_thoi_gian, den_thoi_gian, loai="tat-ca",
                       so_luong=SO_LOG_MAC_DINH):
    """
    Lọc log trong khoảng thời gian.

    tu_thoi_gian, den_thoi_gian: timestamp (int).
    """
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


# ================================================================
# LỌC KẾT HỢP
# ================================================================
def loc_ket_hop(loai="tat-ca", tu_khoa="", tu_thoi_gian=None,
                den_thoi_gian=None, so_luong=SO_LOG_MAC_DINH):
    """
    Lọc log kết hợp nhiều điều kiện.

    loai: loại log.
    tu_khoa: từ khóa trong nội dung.
    tu_thoi_gian, den_thoi_gian: khoảng thời gian.
    so_luong: số log tối đa.
    """
    so_luong = _chuan_hoa_so_luong(so_luong)

    # Lọc theo thời gian trước (nếu có)
    if tu_thoi_gian and den_thoi_gian:
        danh_sach = loc_theo_thoi_gian(
            tu_thoi_gian, den_thoi_gian, loai,
            so_luong=min(SO_LOG_TOI_DA, so_luong * 5),
        )
    else:
        danh_sach = loc_log(loai, min(SO_LOG_TOI_DA, so_luong * 5))

    if not danh_sach:
        return []

    # Lọc theo từ khóa (nếu có)
    if tu_khoa:
        try:
            regex = re.compile(re.escape(tu_khoa.strip()), re.IGNORECASE)
            danh_sach = [log for log in danh_sach if regex.search(log.get("noi_dung", ""))]
        except re.error:
            pass

    # Giới hạn số lượng
    return danh_sach[:so_luong]


# ================================================================
# THỐNG KÊ THEO BỘ LỌC
# ================================================================
def thong_ke_loc(loai="tat-ca"):
    """
    Thống kê số log theo bộ lọc.

    Trả về: dict { loai, so_luong, moi_nhat }.
    """
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


# ================================================================
# LỌC NHANH THEO 5 LOẠI
# ================================================================
def loc_dai_nao(so_luong=SO_LOG_MAC_DINH):
    """Lọc log Đại não."""
    return loc_log("dai-nao", so_luong)


def loc_tieu_nao(so_luong=SO_LOG_MAC_DINH):
    """Lọc log Tiểu não."""
    return loc_log("tieu-nao", so_luong)


def loc_tra_web(so_luong=SO_LOG_MAC_DINH):
    """Lọc log Tra web."""
    return loc_log("tra-web", so_luong)


def loc_sandbox(so_luong=SO_LOG_MAC_DINH):
    """Lọc log Sandbox."""
    return loc_log("sandbox", so_luong)


def loc_loi(so_luong=SO_LOG_MAC_DINH):
    """Lọc log Lỗi."""
    return loc_log("loi", so_luong)


# ================================================================
# LỌC THEO NHIỀU TỪ KHÓA
# ================================================================
def loc_theo_nhieu_tu_khoa(danh_sach_tu_khoa, loai="tat-ca",
                           so_luong=SO_LOG_MAC_DINH):
    """
    Lọc log khớp BẤT KỲ từ khóa nào trong danh sách.

    danh_sach_tu_khoa: list từ khóa.
    """
    if not danh_sach_tu_khoa:
        return loc_log(loai, so_luong)

    # Tạo regex
    try:
        mau = "|".join(re.escape(tk.strip()) for tk in danh_sach_tu_khoa if tk)
        if not mau:
            return loc_log(loai, so_luong)
        regex = re.compile(mau, re.IGNORECASE)
    except re.error:
        return loc_log(loai, so_luong)

    # Lấy nhiều log hơn để lọc
    so_luong_lay = min(SO_LOG_TOI_DA, _chuan_hoa_so_luong(so_luong) * 5)
    danh_sach = loc_log(loai, so_luong_lay)

    ket_qua = []
    for log in danh_sach:
        if regex.search(log.get("noi_dung", "")):
            ket_qua.append(log)
            if len(ket_qua) >= so_luong:
                break

    return ket_qua


# ================================================================
# LỌC LOG CÓ ĐỘ DÀI NỘI DUNG
# ================================================================
def loc_theo_do_dai(do_dai_toi_thieu=100, loai="tat-ca",
                    so_luong=SO_LOG_MAC_DINH):
    """
    Lọc log có nội dung dài hơn N ký tự.
    """
    so_luong_lay = min(SO_LOG_TOI_DA, _chuan_hoa_so_luong(so_luong) * 3)
    danh_sach = loc_log(loai, so_luong_lay)

    ket_qua = []
    for log in danh_sach:
        if len(log.get("noi_dung", "")) >= do_dai_toi_thieu:
            ket_qua.append(log)
            if len(ket_qua) >= so_luong:
                break

    return ket_qua


# ================================================================
# LỌC LOG HÔM NAY
# ================================================================
def loc_hom_nay(loai="tat-ca", so_luong=SO_LOG_MAC_DINH):
    """Lọc log của ngày hôm nay."""
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
    """Lọc log trong N giờ gần nhất."""
    try:
        ket_thuc = int(time.time())
        bat_dau = ket_thuc - so_gio * 3600

        return loc_theo_thoi_gian(bat_dau, ket_thuc, loai, so_luong)
    except Exception:
        return []


# ================================================================
# HÀM PHỤ: DANH SÁCH BỘ LỌC
# ================================================================
def danh_sach_bo_loc():
    """Trả danh sách bộ lọc cho giao diện."""
    return [
        {"ma": "tat-ca", "ten": "Tất cả"},
        {"ma": "dai-nao", "ten": "Đại não"},
        {"ma": "tieu-nao", "ten": "Tiểu não"},
        {"ma": "tra-web", "ten": "Tra web"},
        {"ma": "sandbox", "ten": "Sandbox"},
        {"ma": "loi", "ten": "Lỗi"},
    ]


# ================================================================
# HÀM PHỤ: LẤY NHANH THEO BỘ LỌC
# ================================================================
def lay_theo_bo_loc(ma_bo_loc, so_luong=SO_LOG_MAC_DINH):
    """
    Lấy log theo mã bộ lọc.

    ma_bo_loc: "tat-ca" | "dai-nao" | "tieu-nao" | "tra-web" | "sandbox" | "loi".
    """
    return loc_log(ma_bo_loc, so_luong)


# ================================================================
# HÀM PHỤ: ĐẾM THEO BỘ LỌC
# ================================================================
def dem_theo_bo_loc(ma_bo_loc):
    """Đếm số log theo bộ lọc."""
    try:
        from logs.doc_log import dem_log
        loai_chuan = _chuan_hoa_loai(ma_bo_loc)
        return dem_log(loai_chuan)
    except ImportError:
        return 0
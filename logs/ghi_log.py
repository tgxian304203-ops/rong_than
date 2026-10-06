"""
ghi_log.py - Ghi log hoạt động Rồng Thần.

Nhiệm vụ:
    - ghi_log(loai, noi_dung): ghi 1 dòng log.
    - ghi_log_dai_nao(noi_dung): ghi log Đại não.
    - ghi_log_tieu_nao(noi_dung): ghi log Tiểu não.
    - ghi_log_tra_web(noi_dung): ghi log Tra web.
    - ghi_log_sandbox(noi_dung): ghi log Sandbox.
    - ghi_log_loi(noi_dung): ghi log Lỗi.
    - xoa_log_cu(ngay): xóa log cũ hơn N ngày.

Quy tắc (theo Phần 4):
    - 5 loại log: dai-nao, tieu-nao, tra-web, sandbox, loi.
    - Ghi vào file du_lieu/nhat_ky.log + kho 1 (MongoDB).
    - Mỗi dòng log có: thoi_gian, loai, noi_dung.
    - Cập nhật realtime.
    - Tự động xóa log cũ sau 30 ngày.
    - Không làm sập luồng chính nếu ghi lỗi.

Trả về:
    - True/False cho mỗi hàm ghi.

Tầng dữ liệu: dai_nao/ghi_nho.py (kho 1).
"""

import os
import time


# ================================================================
# HẰNG SỐ
# ================================================================
LOAI_HOP_LE = ["dai-nao", "tieu-nao", "tra-web", "sandbox", "loi"]

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_LOG_LOCAL = os.path.join(THU_MUC_GOC, "du_lieu", "nhat_ky.log")

NGAY = 24 * 3600
NGAY_XOA_LOG_CU = 30


# ================================================================
# GHI LOG VÀO FILE LOCAL
# ================================================================
def _ghi_file_local(loai, noi_dung, thoi_gian):
    """
    Ghi log vào file du_lieu/nhat_ky.log (backup).
    Không làm sập luồng chính nếu lỗi.
    """
    try:
        os.makedirs(os.path.dirname(FILE_LOG_LOCAL), exist_ok=True)

        # Định dạng thời gian đọc được
        thoi_gian_str = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(thoi_gian)
        )

        # Cắt ngắn nội dung
        noi_dung_ngan = str(noi_dung)[:500]

        dong = f"[{thoi_gian_str}] [{loai}] {noi_dung_ngan}\n"

        with open(FILE_LOG_LOCAL, "a", encoding="utf-8") as f:
            f.write(dong)

        return True
    except Exception:
        return False


# ================================================================
# GHI LOG VÀO KHO 1
# ================================================================
def _ghi_kho_1(loai, noi_dung, thoi_gian):
    """
    Ghi log vào kho 1, collection logs.
    """
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
        db["logs"].insert_one({
            "thoi_gian": thoi_gian,
            "loai": loai,
            "noi_dung": str(noi_dung)[:500],
        })
        return True
    except Exception:
        return False


# ================================================================
# HÀM CHÍNH
# ================================================================
def ghi_log(loai, noi_dung):
    """
    Ghi 1 dòng log.

    loai: "dai-nao" | "tieu-nao" | "tra-web" | "sandbox" | "loi".
    noi_dung: mô tả hoạt động.

    Trả về: True nếu ghi thành công (ít nhất 1 nơi).
    """
    if not loai or not noi_dung:
        return False

    # Chuẩn hóa loại
    loai = str(loai).strip().lower()
    if loai not in LOAI_HOP_LE:
        loai = "loi"  # mặc định nếu loại lạ

    thoi_gian = int(time.time())

    # Ghi song song 2 nơi (file + DB)
    ket_qua_file = _ghi_file_local(loai, noi_dung, thoi_gian)
    ket_qua_db = _ghi_kho_1(loai, noi_dung, thoi_gian)

    return ket_qua_file or ket_qua_db


# ================================================================
# CÁC HÀM GHI LOG CHUYÊN BIỆT
# ================================================================
def ghi_log_dai_nao(noi_dung):
    """Ghi log Đại não."""
    return ghi_log("dai-nao", noi_dung)


def ghi_log_tieu_nao(noi_dung):
    """Ghi log Tiểu não."""
    return ghi_log("tieu-nao", noi_dung)


def ghi_log_tra_web(noi_dung):
    """Ghi log Tra web."""
    return ghi_log("tra-web", noi_dung)


def ghi_log_sandbox(noi_dung):
    """Ghi log Sandbox."""
    return ghi_log("sandbox", noi_dung)


def ghi_log_loi(noi_dung):
    """Ghi log Lỗi."""
    return ghi_log("loi", noi_dung)


# ================================================================
# GHI LOG NHANH (chỉ nội dung, tự đoán loại)
# ================================================================
def ghi_nhanh(noi_dung, loai_mac_dinh="dai-nao"):
    """
    Ghi log nhanh, tự đoán loại nếu không rõ.

    Trả về: True/False.
    """
    if not noi_dung:
        return False

    t = str(noi_dung).lower()

    # Tự đoán loại
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


# ================================================================
# XÓA LOG CŨ
# ================================================================
def xoa_log_cu(ngay=NGAY_XOA_LOG_CU):
    """
    Xóa log cũ hơn N ngày khỏi kho 1.
    Mặc định 30 ngày.

    Trả về: số log đã xóa.
    """
    if ngay < 1:
        return 0

    nguong = int(time.time()) - ngay * NGAY

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
# XÓA TOÀN BỘ LOG
# ================================================================
def xoa_tat_ca_log():
    """Xóa toàn bộ log trong kho 1."""
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
        ket_qua = db["logs"].delete_many({})
        return ket_qua.deleted_count
    except Exception:
        return 0


# ================================================================
# ĐẾM LOG
# ================================================================
def dem_log(loai=None):
    """
    Đếm số log trong kho 1.

    loai: nếu có → đếm theo loại, nếu None → đếm tất cả.
    """
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()

        dieu_kien = {}
        if loai:
            dieu_kien["loai"] = loai

        return db["logs"].count_documents(dieu_kien)
    except Exception:
        return 0


# ================================================================
# HÀM PHỤ: GHI LOG CÓ THỜI GIAN CHẠY
# ================================================================
def ghi_log_co_thoi_gian(loai, noi_dung, thoi_gian_bat_dau):
    """
    Ghi log kèm thời gian chạy.

    thoi_gian_bat_dau: timestamp bắt đầu (float).
    """
    try:
        thoi_gian_chay = round(time.time() - thoi_gian_bat_dau, 3)
        noi_dung_full = f"{noi_dung} ({thoi_gian_chay}s)"
        return ghi_log(loai, noi_dung_full)
    except Exception:
        return ghi_log(loai, noi_dung)


# ================================================================
# HÀM PHỤ: GHI NHIỀU LOG CÙNG LÚC
# ================================================================
def ghi_nhieu(danh_sach_log):
    """
    Ghi nhiều log cùng lúc.

    danh_sach_log: list [(loai, noi_dung)] hoặc [{"loai": ..., "noi_dung": ...}].

    Trả về: số log ghi thành công.
    """
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


# ================================================================
# HÀM PHỤ: DANH SÁCH LOẠI LOG HỢP LỆ
# ================================================================
def danh_sach_loai_log():
    """Trả danh sách 5 loại log hợp lệ."""
    return list(LOAI_HOP_LE)


def loai_hop_le(loai):
    """Kiểm tra loại log có hợp lệ không."""
    return loai in LOAI_HOP_LE
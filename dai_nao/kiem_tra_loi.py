"""
kiem_tra_loi.py - Kiểm tra lỗi ở Đại não.

Nhiệm vụ:
    - Kiểm tra lỗi từ kết quả Model.
    - Kiểm tra lỗi từ kết quả Boss.
    - Phân loại lỗi.
    - Trả gợi ý sửa lỗi.

Nguyên tắc:
    - Đại não gọi hàm này sau khi Model/Boss trả kết quả.
    - Nếu có lỗi → ghi vào cây linh hồn (blacklist).
    - Không tự sửa — chỉ phát hiện + ghi nhận.
"""

import re


# ================================================================
# GHI LOG
# ================================================================
def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ================================================================
# LOẠI LỖI
# ================================================================
LOAI_SYNTAX = "syntax"
LOAI_RUNTIME = "runtime"
LOAI_TIMEOUT = "timeout"
LOAI_LOGIC = "logic"
LOAI_KHAC = "khac"


# ================================================================
# KIỂM TRA KẾT QUẢ MODEL
# ================================================================
def kiem_tra_ket_qua_model(ket_qua):
    """
    Kiểm tra kết quả Model trả về có lỗi không.

    ket_qua: {
        stdout, stderr, returncode, thanh_cong
    }

    Trả về: {
        co_loi: bool,
        loai_loi: str,
        thong_diep: str,
        dong: int?,
        goi_y: [str],
    }
    """
    ket_qua_loi = {
        "co_loi": False,
        "loai_loi": "",
        "thong_diep": "",
        "dong": None,
        "goi_y": [],
    }

    if not ket_qua:
        return ket_qua_loi

    # 1. Kiểm tra thanh_cong
    if ket_qua.get("thanh_cong") is True:
        return ket_qua_loi

    # 2. Kiểm tra returncode
    returncode = ket_qua.get("returncode", 0)
    if returncode not in (0, None):
        ket_qua_loi["co_loi"] = True

    # 3. Kiểm tra stderr
    stderr = ket_qua.get("stderr", "")
    if stderr:
        ket_qua_loi["co_loi"] = True
        ket_qua_loi["thong_diep"] = stderr[:500]
        ket_qua_loi["loai_loi"] = _doan_loai_loi(stderr)
        ket_qua_loi["dong"] = _trich_so_dong(stderr)
        ket_qua_loi["goi_y"] = _goi_y_theo_loai(ket_qua_loi["loai_loi"])
        return ket_qua_loi

    # 4. Nếu có lỗi nhưng không có stderr
    if ket_qua_loi["co_loi"]:
        ket_qua_loi["thong_diep"] = f"Lỗi không rõ (returncode={returncode})."
        ket_qua_loi["loai_loi"] = LOAI_KHAC
        ket_qua_loi["goi_y"] = ["Xem log để biết chi tiết."]

    return ket_qua_loi


# ================================================================
# KIỂM TRA KẾT QUẢ BOSS
# ================================================================
def kiem_tra_ket_qua_boss(ket_qua):
    """
    Kiểm tra kết quả Boss trả về có lỗi không.

    Trả về: giống kiem_tra_ket_qua_model.
    """
    ket_qua_loi = {
        "co_loi": False,
        "loai_loi": "",
        "thong_diep": "",
        "dong": None,
        "goi_y": [],
    }

    if not ket_qua:
        ket_qua_loi["co_loi"] = True
        ket_qua_loi["thong_diep"] = "Boss không trả kết quả."
        ket_qua_loi["loai_loi"] = LOAI_KHAC
        return ket_qua_loi

    if not isinstance(ket_qua, dict):
        ket_qua_loi["co_loi"] = True
        ket_qua_loi["thong_diep"] = "Kết quả Boss không phải dict."
        ket_qua_loi["loai_loi"] = LOAI_KHAC
        return ket_qua_loi

    # Kiểm tra trường lỗi
    if ket_qua.get("loi"):
        ket_qua_loi["co_loi"] = True
        ket_qua_loi["thong_diep"] = str(ket_qua["loi"])[:500]
        ket_qua_loi["loai_loi"] = _doan_loai_loi(ket_qua_loi["thong_diep"])
        ket_qua_loi["goi_y"] = _goi_y_theo_loai(ket_qua_loi["loai_loi"])
        return ket_qua_loi

    # Kiểm tra rỗng
    if not ket_qua.get("tra_loi") and not ket_qua.get("code"):
        ket_qua_loi["co_loi"] = True
        ket_qua_loi["thong_diep"] = "Boss trả về rỗng."
        ket_qua_loi["loai_loi"] = LOAI_KHAC
        ket_qua_loi["goi_y"] = ["Thử lại hoặc đổi Boss."]
        return ket_qua_loi

    return ket_qua_loi


# ================================================================
# ĐOÁN LOẠI LỖI
# ================================================================
def _doan_loai_loi(thong_diep):
    """Đoán loại lỗi từ thông điệp."""
    if not thong_diep:
        return LOAI_KHAC

    t = thong_diep.lower()

    if "syntaxerror" in t or "syntax error" in t:
        return LOAI_SYNTAX
    if "timeout" in t or "timed out" in t:
        return LOAI_TIMEOUT
    if "traceback" in t or "runtimeerror" in t:
        return LOAI_RUNTIME
    if "nameerror" in t or "typeerror" in t or "valueerror" in t:
        return LOAI_RUNTIME
    if "indexerror" in t or "keyerror" in t or "attributeerror" in t:
        return LOAI_RUNTIME

    return LOAI_KHAC


# ================================================================
# TRÍCH SỐ DÒNG
# ================================================================
def _trich_so_dong(thong_diep):
    """Trích số dòng từ thông điệp lỗi."""
    if not thong_diep:
        return None

    mau = [
        r"line\s+(\d+)",
        r":(\d+):\d+",
        r"at\s+\S+\s+\((\d+):",
        r"Dòng\s+(\d+)",
    ]

    for m in mau:
        khop = re.search(m, thong_diep, re.I)
        if khop:
            try:
                return int(khop.group(1))
            except (ValueError, IndexError):
                continue

    return None


# ================================================================
# GỢI Ý THEO LOẠI LỖI
# ================================================================
def _goi_y_theo_loai(loai_loi):
    """Trả gợi ý sửa lỗi theo loại."""
    bang = {
        LOAI_SYNTAX: [
            "Kiểm tra dấu ngoặc, dấu hai chấm, dấu chấm phẩy.",
            "Kiểm tra indent (thụt lề) trong Python.",
        ],
        LOAI_RUNTIME: [
            "Kiểm tra biến đã khai báo chưa.",
            "Kiểm tra kiểu dữ liệu.",
            "Kiểm tra chỉ số mảng / dict.",
        ],
        LOAI_TIMEOUT: [
            "Tăng timeout.",
            "Kiểm tra vòng lặp vô hạn.",
        ],
        LOAI_LOGIC: [
            "Kiểm tra logic của thuật toán.",
            "Kiểm tra điều kiện if/else.",
        ],
        LOAI_KHAC: [
            "Xem chi tiết trong stderr.",
            "Thử chạy lại.",
        ],
    }

    return bang.get(loai_loi, bang[LOAI_KHAC])


# ================================================================
# KIỂM TRA TỔNG HỢP
# ================================================================
def kiem_tra_tong_hop(ket_qua, la_boss=False):
    """
    Kiểm tra tổng hợp — tự chọn hàm theo nguồn.

    ket_qua: dict kết quả.
    la_boss: True nếu là Boss, False nếu là Model.

    Trả về: {
        co_loi: bool,
        loai_loi: str,
        thong_diep: str,
        dong: int?,
        goi_y: [str],
    }
    """
    if la_boss:
        return kiem_tra_ket_qua_boss(ket_qua)
    return kiem_tra_ket_qua_model(ket_qua)


# ================================================================
# GHI LỖI VÀO CÂY
# ================================================================
def ghi_loi_vao_cay(chu_so_huu, id_chat, buoc, ket_qua_loi):
    """
    Ghi lỗi vào cây linh hồn (blacklist).

    Trả về: True/False.
    """
    if not ket_qua_loi or not ket_qua_loi.get("co_loi"):
        return False

    try:
        from cay_linh_hon.luu_loi import luu_loi
        return luu_loi(chu_so_huu, id_chat, buoc, {
            "loai_loi": ket_qua_loi.get("loai_loi", LOAI_KHAC),
            "thong_diep": ket_qua_loi.get("thong_diep", ""),
            "dong": ket_qua_loi.get("dong"),
        })
    except Exception as e:
        _ghi_log("loi", f"Ghi lỗi vào cây lỗi: {e}")
        return False


# ================================================================
# TÓM TẮT LỖI
# ================================================================
def tom_tat_loi(ket_qua_loi):
    """Tạo chuỗi tóm tắt lỗi."""
    if not ket_qua_loi or not ket_qua_loi.get("co_loi"):
        return ""

    dong = f" (dòng {ket_qua_loi['dong']})" if ket_qua_loi.get("dong") else ""
    return (
        f"❌ [{ket_qua_loi.get('loai_loi', LOAI_KHAC)}]{dong}: "
        f"{ket_qua_loi.get('thong_diep', '')[:200]}"
    )


# ================================================================
# KIỂM TRA CÓ NÊN SỬA LẠI KHÔNG
# ================================================================
def nen_sua_lai(ket_qua_loi):
    """
    Kiểm tra có nên yêu cầu Model sửa lại không.

    Trả về: True/False.
    """
    if not ket_qua_loi or not ket_qua_loi.get("co_loi"):
        return False

    loai_loi = ket_qua_loi.get("loai_loi", "")

    # Syntax, runtime, logic → nên sửa
    return loai_loi in (LOAI_SYNTAX, LOAI_RUNTIME, LOAI_LOGIC)


# ================================================================
# ĐẾM SỐ LẦN LỖI CÙNG LOẠI
# ================================================================
def dem_loi_cung_loai(chu_so_huu, id_chat, loai_loi):
    """Đếm số lần lỗi cùng loại (để biết có nên dừng không)."""
    try:
        from cay_linh_hon.luu_loi import dem_loi_cung_loai as _dem
        return _dem(chu_so_huu, id_chat, loai_loi)
    except Exception:
        return 0
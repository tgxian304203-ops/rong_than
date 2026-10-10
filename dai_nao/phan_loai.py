"""
phan_loai.py - Phân loại yêu cầu của user.

Nhiệm vụ:
    - Phân loại ĐƠN GIẢN / DỰ ÁN.
    - Phân loại loại: code / toán / văn / khác.
    - Phân loại lĩnh vực: 12 lĩnh vực.
    - Trích xuất 5 yếu tố (nếu cần).

Nguyên tắc:
    - Đây là logic Đại não — không gọi model.
    - Dùng từ khóa + pattern để phân loại.
    - Kết quả dùng cho dieu_phoi.
"""

import re


# ================================================================
# LOẠI YÊU CẦU
# ================================================================
LOAI_DON_GIAN = "don_gian"
LOAI_DU_AN = "du_an"

# Loại nội dung
LOAI_CODE = "code"
LOAI_TOAN = "toan"
LOAI_VAN = "van"
LOAI_KHAC = "khac"


# ================================================================
# TỪ KHÓA PHÂN LOẠI DỰ ÁN
# ================================================================
TU_KHOA_DU_AN = [
    "dự án", "làm app", "làm web", "làm game", "xây dựng",
    "tạo ứng dụng", "viết phần mềm", "lập trình", "toàn bộ",
    "nhiều bước", "từng bước", "kế hoạch", "hệ thống",
    "quản lý", "website", "web app", "mobile", "chatbot",
    "ai agent", "bot", "crawler", "api", "backend", "frontend",
]


# ================================================================
# TỪ KHÓA PHÂN LOẠI CODE
# ================================================================
TU_KHOA_CODE = [
    "code", "hàm", "function", "class", "python", "javascript",
    "html", "css", "java", "c++", "sql", "viết code", "lập trình",
    "sửa code", "tối ưu code", "debug", "lỗi", "thuật toán",
    "script", "chương trình",
]


# ================================================================
# TỪ KHÓA PHÂN LOẠI TOÁN
# ================================================================
TU_KHOA_TOAN = [
    "toán", "phương trình", "tính", "giải", "tích phân",
    "đạo hàm", "hình học", "đại số", "xác suất", "thống kê",
    "số học", "logarit", "lượng giác", "hàm số", "bất đẳng thức",
]


# ================================================================
# TỪ KHÓA PHÂN LOẠI VĂN
# ================================================================
TU_KHOA_VAN = [
    "văn", "bài văn", "đoạn văn", "viết văn", "thơ", "truyện",
    "tiểu luận", "nghị luận", "phân tích", "cảm nhận",
    "thuyết minh", "miêu tả", "kể chuyện",
]


# ================================================================
# 12 LĨNH VỰC
# ================================================================
LINH_VUC_HOP_LE = [
    "toán", "văn", "code", "bug", "khoa học", "đời sống",
    "kinh doanh", "sáng tạo", "học tập", "tra cứu",
    "kỹ thuật", "luật - hành chính",
]


# ================================================================
# PHÂN LOẠI CHÍNH
# ================================================================
def phan_loai(noi_dung):
    """
    Phân loại yêu cầu.

    Trả về: {
        loai: "don_gian" | "du_an",
        loai_noi_dung: "code" | "toan" | "van" | "khac",
        linh_vuc: str,
        do_dai: int,
    }
    """
    ket_qua = {
        "loai": LOAI_DON_GIAN,
        "loai_noi_dung": LOAI_KHAC,
        "linh_vuc": "",
        "do_dai": 0,
    }

    if not noi_dung:
        return ket_qua

    noi_dung_lower = noi_dung.lower().strip()
    ket_qua["do_dai"] = len(noi_dung_lower)

    # Đếm từ khóa
    diem_du_an = _dem_tu_khoa(noi_dung_lower, TU_KHOA_DU_AN)
    diem_code = _dem_tu_khoa(noi_dung_lower, TU_KHOA_CODE)
    diem_toan = _dem_tu_khoa(noi_dung_lower, TU_KHOA_TOAN)
    diem_van = _dem_tu_khoa(noi_dung_lower, TU_KHOA_VAN)

    # Phân loại đơn giản / dự án
    if diem_du_an >= 1 or _co_dau_hieu_du_an(noi_dung_lower):
        ket_qua["loai"] = LOAI_DU_AN

    # Phân loại nội dung (ưu tiên theo điểm)
    diem_cao_nhat = max(diem_code, diem_toan, diem_van)

    if diem_cao_nhat == 0:
        ket_qua["loai_noi_dung"] = LOAI_KHAC
    elif diem_code == diem_cao_nhat:
        ket_qua["loai_noi_dung"] = LOAI_CODE
    elif diem_toan == diem_cao_nhat:
        ket_qua["loai_noi_dung"] = LOAI_TOAN
    elif diem_van == diem_cao_nhat:
        ket_qua["loai_noi_dung"] = LOAI_VAN

    # Lĩnh vực
    ket_qua["linh_vuc"] = _doan_linh_vuc(noi_dung_lower, ket_qua["loai_noi_dung"])

    return ket_qua


# ================================================================
# ĐẾM TỪ KHÓA
# ================================================================
def _dem_tu_khoa(noi_dung, danh_sach_tu_khoa):
    """Đếm số từ khóa xuất hiện trong nội dung."""
    dem = 0
    for tu in danh_sach_tu_khoa:
        if tu in noi_dung:
            dem += 1
    return dem


# ================================================================
# DẤU HIỆU DỰ ÁN
# ================================================================
def _co_dau_hieu_du_an(noi_dung):
    """
    Kiểm tra có dấu hiệu dự án không (dài, nhiều bước, phức tạp).
    """
    # Quá dài
    if len(noi_dung) > 500:
        return True

    # Có đánh số bước
    if re.search(r"\b(bước \d|\d\.\s|b1|b2)\b", noi_dung, re.I):
        return True

    # Có yêu cầu nhiều phần
    if noi_dung.count(" và ") >= 3:
        return True

    return False


# ================================================================
# ĐOÁN LĨNH VỰC
# ================================================================
def _doan_linh_vuc(noi_dung, loai_noi_dung):
    """Đoán lĩnh vực từ nội dung."""
    if loai_noi_dung == LOAI_CODE:
        if "bug" in noi_dung or "lỗi" in noi_dung:
            return "bug"
        return "code"

    if loai_noi_dung == LOAI_TOAN:
        return "toán"

    if loai_noi_dung == LOAI_VAN:
        return "văn"

    # Đoán theo từ khóa khác
    bang = {
        "khoa học": ["khoa học", "vật lý", "hóa học", "sinh học"],
        "kinh doanh": ["kinh doanh", "bán hàng", "marketing", "tài chính"],
        "sáng tạo": ["sáng tạo", "thiết kế", "vẽ", "nghệ thuật"],
        "học tập": ["học", "ôn thi", "bài tập", "giảng"],
        "tra cứu": ["tra cứu", "tìm hiểu", "thông tin"],
        "kỹ thuật": ["kỹ thuật", "cơ khí", "điện", "xây dựng"],
        "luật - hành chính": ["luật", "pháp", "hành chính", "thủ tục"],
    }

    for linh_vuc, tu_khoa in bang.items():
        for tu in tu_khoa:
            if tu in noi_dung:
                return linh_vuc

    return "đời sống"


# ================================================================
# LẤY LOẠI NỘI DUNG
# ================================================================
def lay_loai_noi_dung(noi_dung):
    """Lấy loại nội dung (code / toan / van / khac)."""
    ket_qua = phan_loai(noi_dung)
    return ket_qua.get("loai_noi_dung", LOAI_KHAC)


# ================================================================
# LÀ DỰ ÁN KHÔNG
# ================================================================
def la_du_an(noi_dung):
    """Kiểm tra có phải dự án không."""
    ket_qua = phan_loai(noi_dung)
    return ket_qua.get("loai") == LOAI_DU_AN


def la_don_gian(noi_dung):
    """Kiểm tra có phải đơn giản không."""
    ket_qua = phan_loai(noi_dung)
    return ket_qua.get("loai") == LOAI_DON_GIAN


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat_phan_loai(ket_qua):
    """Tạo chuỗi tóm tắt phân loại."""
    if not ket_qua:
        return ""
    return (
        f"Loại: {ket_qua.get('loai')} | "
        f"Nội dung: {ket_qua.get('loai_noi_dung')} | "
        f"Lĩnh vực: {ket_qua.get('linh_vuc')}"
    )
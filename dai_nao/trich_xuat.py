"""
trich_xuat.py - Trích xuất 5 yếu tố Rồng Thần.

Nhiệm vụ:
    - trich_xuat_5_yeu_to(noi_dung): trích xuất 5 yếu tố từ câu người dùng.

5 yếu tố (theo Phần 4):
    1. Hành động — người dùng muốn làm gì?
    2. Đối tượng — tác động lên cái gì?
    3. Thuộc tính — đặc điểm, tính chất?
    4. Ràng buộc — giới hạn, yêu cầu bắt buộc?
    5. Ngữ cảnh — bối cảnh xung quanh?

Trả về:
    {
        hanh_dong: str,
        doi_tuong: str,
        thuoc_tinh: str,
        rang_buoc: str,
        ngu_canh: str,
    }

Quy tắc:
    - Không đoán bừa. Nếu không xác định được → để rỗng.
    - Dùng từ khóa + mẫu câu.
    - Đây là bước 2 trong luồng 12 bước của xu_ly_task.py.
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
# BẢNG TỪ KHÓA HÀNH ĐỘNG
# ================================================================
HANH_DONG = {
    "tạo_moi": [
        "làm", "tạo", "viết", "sinh", "xây", "dựng", "chế",
        "thiết kế", "vẽ", "generate", "create", "build", "make",
    ],
    "sửa": ["sửa", "fix", "chỉnh", "refactor", "cải thiện", "khắc phục"],
    "tối_ưu": ["tối ưu", "optimize", "cải thiện tốc độ", "nhanh hơn", "gọn hơn"],
    "tính": ["tính", "giải", "tìm", "tính toán", "solve", "compute"],
    "phân_tích": ["phân tích", "kiểm tra", "đánh giá", "review", "analyze"],
    "giải_thích": [
        "giải thích", "hiểu", "nghĩa là gì", "là gì", "explain",
        "tại sao", "vì sao", "như thế nào",
    ],
    "dịch": ["dịch", "translate", "chuyển ngữ"],
    "tóm_tắt": ["tóm tắt", "summary", "summarize", "rút gọn"],
    "so_sánh": ["so sánh", "compare", "khác nhau", "giống nhau"],
    "hướng_dẫn": ["hướng dẫn", "chỉ", "dạy", "tutorial", "how to", "cách"],
    "liệt_kê": ["liệt kê", "kể", "list", "đưa ra danh sách"],
    "tìm_kiếm": ["tìm", "tra", "search", "look up", "tra cứu"],
    "chuyển_đổi": ["chuyển", "convert", "đổi sang", "đổi thành"],
    "xóa": ["xóa", "bỏ", "delete", "remove"],
}


# ================================================================
# BẢNG TỪ KHÓA ĐỐI TƯỢNG
# ================================================================
DOI_TUONG = {
    "web": ["web", "website", "trang web", "landing page", "giao diện"],
    "form": ["form", "biểu mẫu", "đăng ký", "đăng nhập"],
    "hàm": ["hàm", "function", "def"],
    "class": ["class", "lớp", "oop"],
    "API": ["api", "endpoint", "rest", "graphql"],
    "database": ["database", "cơ sở dữ liệu", "sql", "mongodb", "mysql"],
    "AI": ["ai", "model", "chatbot", "trí tuệ nhân tạo"],
    "script": ["script", "tool", "bot", "crawler"],
    "phương_trình": ["phương trình", "pt", "bất phương trình", "hệ phương trình"],
    "biểu_thức": ["biểu thức", "expression", "công thức"],
    "số": ["số", "tổng", "hiệu", "tích", "thương"],
    "hình": ["hình", "tam giác", "hình tròn", "hình vuông", "đa giác"],
    "đoạn_văn": ["đoạn văn", "bài văn", "tiểu luận", "nghị luận"],
    "email": ["email", "thư"],
    "đoạn_code": ["đoạn code", "code", "chương trình"],
    "lỗi": ["lỗi", "bug", "error"],
    "tài_liệu": ["tài liệu", "văn bản", "document"],
    "file": ["file", "tệp"],
    "ảnh": ["ảnh", "hình ảnh", "image"],
    "video": ["video", "clip"],
    "câu_hỏi": ["câu hỏi", "question"],
}


# ================================================================
# BẢNG TỪ KHÓA THUỘC TÍNH
# ================================================================
THUOC_TINH = {
    # Tính từ thẩm mỹ
    "đẹp": ["đẹp", "xinh", "dễ thương", "cute", "beautiful"],
    "xấu": ["xấu", "ugly"],
    "đơn_giản": ["đơn giản", "dễ hiểu", "simple", "basic"],
    "phức_tạp": ["phức tạp", "khó", "complex"],
    "chuyên_nghiệp": ["chuyên nghiệp", "professional", "pro"],
    "sáng_tạo": ["sáng tạo", "creative", "độc đáo"],

    # Tính chất kỹ thuật
    "nhanh": ["nhanh", "fast", "tốc độ cao", "hiệu quả"],
    "gọn": ["gọn", "ngắn", "compact", "minimal"],
    "tối_ưu": ["tối ưu", "optimized", "hiệu suất"],
    "bảo_mật": ["bảo mật", "an toàn", "secure"],
    "mở_rộng": ["mở rộng", "scale", "có thể mở rộng"],
    "tự_động": ["tự động", "automatic", "auto"],
    "thời_gian_thực": ["thời gian thực", "real-time", "realtime"],
    "đa_nền_tảng": ["đa nền tảng", "cross-platform", "đa thiết bị"],
    "đáp_ứng": ["đáp ứng", "responsive", "mobile-first"],

    # Màu sắc
    "màu_đỏ": ["màu đỏ", "đỏ", "red"],
    "màu_xanh": ["màu xanh", "xanh", "blue", "green"],
    "màu_vàng": ["màu vàng", "vàng", "yellow"],
    "màu_đen": ["màu đen", "đen", "black"],
    "màu_trắng": ["màu trắng", "trắng", "white"],

    # Kích thước
    "nhỏ": ["nhỏ", "bé", "small", "mini"],
    "lớn": ["lớn", "to", "big", "large"],
    "vừa": ["vừa", "medium"],
}


# ================================================================
# BẢNG TỪ KHÓA RÀNG BUỘC
# ================================================================
RANG_BUOC = {
    "số_dòng": ["dòng", "line", "dưới", "trên", "tối đa", "ít nhất"],
    "số_ký_tự": ["ký tự", "character", "chữ"],
    "thời_gian": ["giây", "phút", "giờ", "ngày", "tuần", "tháng", "năm", "trong vòng"],
    "dung_lượng": ["mb", "gb", "kb", "byte", "dung lượng"],
    "không_dùng": ["không dùng", "không cần", "đừng", "tránh", "không sử dụng"],
    "chỉ_dùng": ["chỉ dùng", "chỉ cần", "chỉ sử dụng"],
    "bắt_buộc": ["bắt buộc", "phải", "cần phải", "required", "must"],
    "tùy_chọn": ["tùy chọn", "nếu có thể", "optional", "không bắt buộc"],
    "ngôn_ngữ": ["bằng python", "bằng js", "bằng java", "bằng html", "bằng css"],
    "framework": ["dùng react", "dùng vue", "dùng django", "dùng flask", "dùng node"],
    "thư_viện": ["dùng thư viện", "không dùng thư viện", "cài thêm"],
    "chi_phí": ["miễn phí", "free", "trả phí", "không tốn tiền", "rẻ"],
}


# ================================================================
# BẢNG TỪ KHÓA NGỮ CẢNH
# ================================================================
NGU_CANH = {
    "đối_tượng_người_dùng": [
        "cho học sinh", "cho sinh viên", "cho trẻ em", "cho người già",
        "cho người mới", "cho người mới bắt đầu", "cho dân chuyên",
        "cho giáo viên", "cho phụ huynh",
    ],
    "quy_mô": [
        "nhỏ", "cá nhân", "lớn", "doanh nghiệp", "công ty",
        "startup", "tổ chức", "team", "nhóm",
    ],
    "mục_đích": [
        "để học", "để dạy", "để bán", "để kiếm tiền", "để giải trí",
        "để thử nghiệm", "để demo", "để sản xuất",
    ],
    "nền_tảng": [
        "trên web", "trên mobile", "trên desktop", "trên điện thoại",
        "trên máy tính", "trên android", "trên ios",
    ],
    "môi_trường": [
        "local", "trên server", "trên cloud", "trên render",
        "trên heroku", "trên vps",
    ],
    "thời_điểm": [
        "hôm nay", "ngày mai", "tuần này", "tuần sau",
        "tháng này", "gấp", "khẩn cấp",
    ],
    "cảm_xúc": [
        "vui", "buồn", "tức", "bực", "mệt", "hào hứng",
        "lo lắng", "hồi hộp",
    ],
}


# ================================================================
# TRÍCH XUẤT HÀNH ĐỘNG
# ================================================================
def _trich_hanh_dong(noi_dung):
    """
    Trích xuất hành động chính.
    Ưu tiên hành động đứng đầu câu hoặc sau chủ ngữ.
    """
    for loai, tu_khoa in HANH_DONG.items():
        for tk in tu_khoa:
            # Tìm vị trí từ khóa trong câu
            vi_tri = noi_dung.find(tk)
            if vi_tri >= 0:
                # Kiểm tra ranh giới từ
                truoc = noi_dung[vi_tri - 1] if vi_tri > 0 else " "
                sau = noi_dung[vi_tri + len(tk)] if vi_tri + len(tk) < len(noi_dung) else " "
                if not truoc.isalnum() and not sau.isalnum():
                    return tk, loai
    return "", ""


# ================================================================
# TRÍCH XUẤT ĐỐI TƯỢNG
# ================================================================
def _trich_doi_tuong(noi_dung):
    """Trích xuất đối tượng chính."""
    for loai, tu_khoa in DOI_TUONG.items():
        for tk in tu_khoa:
            if tk in noi_dung:
                # Kiểm tra ranh giới
                vi_tri = noi_dung.find(tk)
                truoc = noi_dung[vi_tri - 1] if vi_tri > 0 else " "
                sau = noi_dung[vi_tri + len(tk)] if vi_tri + len(tk) < len(noi_dung) else " "
                if not truoc.isalnum() or not sau.isalnum():
                    return tk, loai
    return "", ""


# ================================================================
# TRÍCH XUẤT THUỘC TÍNH
# ================================================================
def _trich_thuoc_tinh(noi_dung):
    """Trích xuất thuộc tính — có thể có nhiều."""
    ket_qua = []
    for loai, tu_khoa in THUOC_TINH.items():
        for tk in tu_khoa:
            if tk in noi_dung:
                vi_tri = noi_dung.find(tk)
                truoc = noi_dung[vi_tri - 1] if vi_tri > 0 else " "
                sau = noi_dung[vi_tri + len(tk)] if vi_tri + len(tk) < len(noi_dung) else " "
                if not truoc.isalnum() or not sau.isalnum():
                    ket_qua.append(tk)
                    break
    return ", ".join(ket_qua) if ket_qua else ""


# ================================================================
# TRÍCH XUẤT RÀNG BUỘC
# ================================================================
def _trich_rang_buoc(noi_dung):
    """Trích xuất ràng buộc — có thể có nhiều."""
    ket_qua = []
    for loai, tu_khoa in RANG_BUOC.items():
        for tk in tu_khoa:
            if tk in noi_dung:
                vi_tri = noi_dung.find(tk)
                truoc = noi_dung[vi_tri - 1] if vi_tri > 0 else " "
                sau = noi_dung[vi_tri + len(tk)] if vi_tri + len(tk) < len(noi_dung) else " "
                if not truoc.isalnum() or not sau.isalnum():
                    # Cố gắng lấy cả số đi kèm
                    pham_vi = noi_dung[max(0, vi_tri - 15):vi_tri + len(tk) + 15]
                    ket_qua.append(pham_vi.strip())
                    break
    return " | ".join(ket_qua) if ket_qua else ""


# ================================================================
# TRÍCH XUẤT NGỮ CẢNH
# ================================================================
def _trich_ngu_canh(noi_dung):
    """Trích xuất ngữ cảnh — có thể có nhiều."""
    ket_qua = []
    for loai, tu_khoa in NGU_CANH.items():
        for tk in tu_khoa:
            if tk in noi_dung:
                ket_qua.append(tk)
                break
    return ", ".join(ket_qua) if ket_qua else ""


# ================================================================
# HÀM CHÍNH
# ================================================================
def trich_xuat_5_yeu_to(noi_dung):
    """
    Trích xuất 5 yếu tố từ câu người dùng.

    noi_dung: chuỗi đã được chuẩn hóa (từ chuan_hoa.py).
    Trả về: dict 5 yếu tố.
    """
    if not noi_dung or not isinstance(noi_dung, str):
        return {
            "hanh_dong": "",
            "doi_tuong": "",
            "thuoc_tinh": "",
            "rang_buoc": "",
            "ngu_canh": "",
        }

    noi_dung = noi_dung.strip()
    noi_dung_lower = noi_dung.lower()

    # Trích xuất từng yếu tố
    hanh_dong, loai_hanh_dong = _trich_hanh_dong(noi_dung_lower)
    doi_tuong, loai_doi_tuong = _trich_doi_tuong(noi_dung_lower)
    thuoc_tinh = _trich_thuoc_tinh(noi_dung_lower)
    rang_buoc = _trich_rang_buoc(noi_dung_lower)
    ngu_canh = _trich_ngu_canh(noi_dung_lower)

    ket_qua = {
        "hanh_dong": hanh_dong,
        "doi_tuong": doi_tuong,
        "thuoc_tinh": thuoc_tinh,
        "rang_buoc": rang_buoc,
        "ngu_canh": ngu_canh,
        # Metadata phụ (giúp duyệt cây)
        "loai_hanh_dong": loai_hanh_dong,
        "loai_doi_tuong": loai_doi_tuong,
    }

    # Ghi log nếu thiếu yếu tố
    so_yeu_to = sum(1 for k in ("hanh_dong", "doi_tuong", "thuoc_tinh", "rang_buoc", "ngu_canh") if ket_qua[k])
    if so_yeu_to < 5:
        _ghi_log("dai-nao", f"Trích xuất: {so_yeu_to}/5 yếu tố từ '{noi_dung[:50]}'")

    return ket_qua


# ================================================================
# HÀM PHỤ: KIỂM TRA ĐỦ 5 YẾU TỐ
# ================================================================
def du_5_yeu_to(yeu_to, muc_do=5):
    """
    Kiểm tra đã đủ 5 yếu tố chưa.

    yeu_to: dict 5 yếu tố.
    muc_do: mức độ yêu cầu (5 = đủ cả 5, 4 = đủ 4/5, ...).

    Trả về: (True/False, danh_sách_thiếu)
    """
    if not yeu_to or not isinstance(yeu_to, dict):
        return False, ["hanh_dong", "doi_tuong", "thuoc_tinh", "rang_buoc", "ngu_canh"]

    can = ("hanh_dong", "doi_tuong", "thuoc_tinh", "rang_buoc", "ngu_canh")
    thieu = [k for k in can if not yeu_to.get(k)]

    return len(thieu) <= (5 - muc_do), thieu


# ================================================================
# HÀM PHỤ: TÓM TẮT 5 YẾU TỐ CHO LOG
# ================================================================
def tom_tat_5_yeu_to(yeu_to):
    """Tạo chuỗi tóm tắt 5 yếu tố để ghi log."""
    if not yeu_to:
        return "(rỗng)"
    phan = []
    for k in ("hanh_dong", "doi_tuong", "thuoc_tinh", "rang_buoc", "ngu_canh"):
        v = yeu_to.get(k)
        if v:
            phan.append(f"{k}={v}")
    return " | ".join(phan) if phan else "(rỗng)"
"""
xu_ly_tra_web.py - Xử lý task tra web Rồng Thần (bản mạnh).

Nhiệm vụ:
    - xu_ly_tra_web(noi_dung, yeu_to, loai_task): xử lý task tra web.
    - can_tra_web(noi_dung, loai_task): kiểm tra có cần tra web.
    - phan_loai_tra_web(noi_dung): phân loại task tra web.
    - tong_hop_ket_qua(danh_sach): tổng hợp kết quả.
    - tao_cau_tra_loi(ket_qua, noi_dung): tạo câu trả lời.

Nhận biết tra web:
    - 15 nhóm tín hiệu, 200+ từ khóa.
    - Kiểm tra câu hỏi, cụm danh từ, mốc thời gian.
    - Phân loại task cần tra web.

Quy tắc:
    - Tra web KHÔNG lưu gì vào cây quyết định.
    - Tra web chỉ lấy dữ liệu — Đại não mới xử lý.
    - Tự xoay API khi hết quota.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import re
import time


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
# HẰNG SỐ
# ================================================================
SO_KET_QUA_TOI_DA = 5
DO_DAI_MO_TA_TOI_DA = 300


# ================================================================
# 15 NHÓM TÍN HIỆU — 200+ TỪ KHÓA
# ================================================================
TIN_HIEU_TRA_WEB = {

    # 1. THỜI GIAN
    "thoi_gian": [
        "hôm nay", "hôm qua", "hôm kia", "tuần này", "tuần trước",
        "tuần sau", "tháng này", "tháng trước", "tháng sau",
        "năm nay", "năm ngoái", "năm sau",
        "quý này", "quý trước", "quý sau",
        "mới nhất", "gần đây", "gần nhất", "vừa", "vừa mới",
        "hiện tại", "bây giờ", "hiện nay", "hiện giờ",
        "sắp tới", "tương lai", "dự báo", "dự đoán",
        "mới", "cũ", "cập nhật",
    ],

    # 2. SỰ KIỆN THỜI SỰ
    "su_kien": [
        "tin tức", "tin mới", "tin nóng", "thời sự", "sự kiện",
        "diễn biến", "tình hình", "bối cảnh",
        "bầu cử", "chiến tranh", "xung đột", "hòa bình",
        "dịch bệnh", "đại dịch", "covid",
        "thiên tai", "bão", "lũ", "động đất", "sóng thần",
        "khủng hoảng", "biểu tình", "đảo chính",
    ],

    # 3. TÀI CHÍNH / KINH TẾ
    "tai_chinh": [
        "giá vàng", "giá xăng", "giá dầu", "giá đô", "giá usd",
        "tỉ giá", "tỷ giá", "lãi suất", "lạm phát",
        "chứng khoán", "cổ phiếu", "trái phiếu", "bitcoin", "crypto",
        "thị trường", "kinh tế", "gdp", "cpi",
        "đầu tư", "lợi nhuận", "doanh thu", "tài chính",
    ],

    # 4. THỂ THAO
    "the_thao": [
        "bóng đá", "bóng rổ", "tennis", "cầu lông", "bóng chuyền",
        "world cup", "olympic", "asian cup", "sea games",
        "ngoại hạng anh", "la liga", "serie a", "bundesliga",
        "champions league", "europa league",
        "đội tuyển", "cầu thủ", "huấn luyện viên", "hlv",
        "trận đấu", "tỉ số", "bàn thắng",
    ],

    # 5. ĐỊNH NGHĨA / KHÁI NIỆM
    "dinh_nghia": [
        "là gì", "định nghĩa", "nghĩa là", "khái niệm",
        "khái niệm là", "định nghĩa là", "có nghĩa là",
        "là ai", "tiểu sử", "lí lịch", "lý lịch",
        "nguồn gốc", "xuất xứ", "lịch sử của",
        "ra đời khi nào", "ai sáng lập", "ai tạo ra",
    ],

    # 6. SO SÁNH
    "so_sanh": [
        "so sánh", "khác nhau", "giống nhau", "khác gì", "giống gì",
        "cái nào tốt hơn", "cái nào hay hơn", "cái nào rẻ hơn",
        "nên chọn", "nên dùng", "nên mua", "hay hơn",
        " vs ", " hay ", " hoặc ",
        "ưu nhược điểm", "ưu điểm", "nhược điểm",
        "review", "đánh giá", "nhận xét",
    ],

    # 7. HƯỚNG DẪN
    "huong_dan": [
        "cách", "hướng dẫn", "làm sao", "làm thế nào",
        "how to", "tutorial", "hướng dẫn cách",
        "bước", "các bước", "quy trình",
        "cài đặt", "sử dụng", "cấu hình", "setup", "install",
        "chỉ cách", "chỉ cho", "dạy cách",
    ],

    # 8. SỐ LIỆU / THỐNG KÊ
    "so_lieu": [
        "số liệu", "thống kê", "báo cáo", "nghiên cứu",
        "dân số", "diện tích", "tỉ lệ", "tỷ lệ", "phần trăm",
        "top 10", "top 5", "top 100", "xếp hạng", "bảng xếp hạng",
        "bao nhiêu", "có bao nhiêu", "có mấy",
        "trung bình", "tổng số", "số lượng",
    ],

    # 9. ĐỊA LÝ / VỊ TRÍ
    "dia_ly": [
        "ở đâu", "tọa lạc", "địa chỉ", "vị trí", "nằm ở",
        "quốc gia nào", "nước nào", "thành phố nào", "tỉnh nào",
        "bản đồ", "khoảng cách", "gần", "xa",
        "châu lục", "đại dương", "biển", "núi", "sông",
    ],

    # 10. SẢN PHẨM / MUA SẮM
    "san_pham": [
        "giá", "bao nhiêu tiền", "mua ở đâu", "mua online",
        "sản phẩm", "mẫu mới", "phiên bản mới",
        "khuyến mãi", "giảm giá", "sale", "khuyến mại",
        "tốt không", "có tốt không", "đáng mua không",
        "chính hãng", "uy tín", "chất lượng",
    ],

    # 11. LIÊN HỆ / THÔNG TIN NGƯỜI
    "lien_he": [
        "email của", "số điện thoại của", "sđt của", "phone của",
        "địa chỉ của", "website của", "fanpage của",
        "liên hệ", "liên lạc", "contact",
        "facebook của", "instagram của", "youtube của", "tiktok của",
        "kênh của", "trang của", "group của",
    ],

    # 12. LẬP TRÌNH / TÀI LIỆU
    "lap_trinh": [
        "tài liệu", "docs", "documentation", "api",
        "thư viện", "framework", "package", "module",
        "version mới nhất", "phiên bản mới nhất",
        "cách dùng", "cách sử dụng", "cú pháp",
        "hoạt động thế nào", "nguyên lý", "cơ chế",
        "lỗi phổ biến", "best practice", "chuẩn",
    ],

    # 13. Y TẾ / SỨC KHỎE
    "y_te": [
        "triệu chứng", "bệnh", "thuốc", "điều trị",
        "cách chữa", "phòng bệnh", "chữa bệnh",
        "dinh dưỡng", "chế độ ăn", "thực đơn",
        "bác sĩ", "bệnh viện", "phòng khám",
        "xét nghiệm", "chẩn đoán", "sức khỏe",
    ],

    # 14. PHÁP LUẬT / THỦ TỤC
    "phap_luat": [
        "luật", "quy định", "thủ tục", "hồ sơ", "giấy tờ",
        "điều kiện", "mức phạt", "xử phạt", "vi phạm",
        "đăng ký", "xin cấp", "chứng nhận",
        "hợp đồng", "điều khoản", "quyền lợi", "nghĩa vụ",
        "khiếu nại", "tố cáo", "kiện",
    ],

    # 15. HỌC THUẬT / NGHIÊN CỨU
    "hoc_thuat": [
        "nghiên cứu", "báo cáo khoa học", "luận văn", "luận án",
        "đề tài", "chuyên đề", "sáng kiến",
        "tài liệu tham khảo", "trích dẫn", "citation",
        "số liệu nghiên cứu", "kết quả nghiên cứu",
        "phương pháp nghiên cứu", "khảo sát",
    ],
}


# ================================================================
# TỪ NGHI VẤN — TÍN HIỆU CÂU HỎI
# ================================================================
TU_NGHI_VAN = [
    "ai", "gì", "nào", "đâu", "khi nào", "bao giờ", "bao nhiêu",
    "thế nào", "như thế nào", "ra sao", "làm sao", "tại sao",
    "vì sao", "cái gì", "con gì", "ở đâu", "bằng cách nào",
]


# ================================================================
# LOẠI TRA WEB
# ================================================================
LOAI_TRA_WEB = {
    "tin_tuc": TIN_HIEU_TRA_WEB["su_kien"] + TIN_HIEU_TRA_WEB["thoi_gian"],
    "tai_chinh": TIN_HIEU_TRA_WEB["tai_chinh"],
    "the_thao": TIN_HIEU_TRA_WEB["the_thao"],
    "định_nghĩa": TIN_HIEU_TRA_WEB["dinh_nghia"],
    "so_sanh": TIN_HIEU_TRA_WEB["so_sanh"],
    "hướng_dẫn": TIN_HIEU_TRA_WEB["huong_dan"],
    "so_lieu": TIN_HIEU_TRA_WEB["so_lieu"],
    "dia_ly": TIN_HIEU_TRA_WEB["dia_ly"],
    "san_pham": TIN_HIEU_TRA_WEB["san_pham"],
    "lien_he": TIN_HIEU_TRA_WEB["lien_he"],
    "lap_trinh": TIN_HIEU_TRA_WEB["lap_trinh"],
    "y_te": TIN_HIEU_TRA_WEB["y_te"],
    "phap_luat": TIN_HIEU_TRA_WEB["phap_luat"],
    "hoc_thuat": TIN_HIEU_TRA_WEB["hoc_thuat"],
}


# ================================================================
# PHÁT HIỆN CỤM DANH TỪ RIÊNG
# ================================================================
TEN_RIENG_GOI_Y = [
    # Tổ chức / công ty
    r"\b(google|facebook|meta|apple|microsoft|amazon|tesla|nvidia|openai)\b",
    r"\b(samsung|sony|xiaomi|huawei|oppo|vivo|realme)\b",
    r"\b(shopee|lazada|tiki|sendo|grab|gojek|be|be group)\b",
    r"\b(viettel|vinaphone|mobifone|vietcombank|techcombank|vpbank)\b",
    # Quốc gia / thành phố
    r"\b(việt nam|mỹ|trung quốc|nhật|hàn|pháp|đức|anh|nga|ấn độ)\b",
    r"\b(hà nội|sài gòn|hồ chí minh|đà nẵng|huế|cần thơ|hải phòng)\b",
    r"\b(tokyo|seoul|beijing|new york|london|paris|berlin|moscow)\b",
    # Người nổi tiếng
    r"\b(elon musk|bill gates|mark zuckerberg|steve jobs|jeff bezos)\b",
    r"\b(messi|ronaldo|neymar|mbappe|haaland)\b",
    # Công nghệ
    r"\b(python|javascript|java|golang|rust|typescript|react|vue|angular)\b",
    r"\b(chatgpt|gpt-\d|claude|gemini|copilot)\b",
]


# ================================================================
# PHÁT HIỆN MỐC THỜI GIAN
# ================================================================
def _co_moc_thoi_gian(noi_dung):
    """Kiểm tra có mốc thời gian cụ thể không."""
    if not noi_dung:
        return False
    # Năm 2020-2030
    if re.search(r"\b20[2-3]\d\b", noi_dung):
        return True
    # Tháng 1-12
    if re.search(r"\b(tháng|thg)\s*(1[0-2]|[1-9])\b", noi_dung, re.I):
        return True
    # Quý 1-4
    if re.search(r"\bquý\s*[1-4]\b", noi_dung, re.I):
        return True
    # Ngày cụ thể
    if re.search(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", noi_dung):
        return True
    return False


# ================================================================
# PHÁT HIỆN TÊN RIÊNG
# ================================================================
def _co_ten_rieng(noi_dung):
    """Kiểm tra có tên riêng (công ty, người, địa danh) không."""
    if not noi_dung:
        return False
    t = noi_dung.lower()
    for mau in TEN_RIENG_GOI_Y:
        if re.search(mau, t):
            return True
    return False


# ================================================================
# PHÁT HIỆN CÂU HỎI
# ================================================================
def _la_cau_hoi(noi_dung):
    """Kiểm tra có phải câu hỏi không."""
    if not noi_dung:
        return False
    if "?" in noi_dung:
        return True
    t = noi_dung.lower()
    for tv in TU_NGHI_VAN:
        if re.search(r"\b" + re.escape(tv) + r"\b", t):
            return True
    return False


# ================================================================
# KIỂM TRA CẦN TRA WEB
# ================================================================
def can_tra_web(noi_dung, loai_task=None):
    """
    Kiểm tra task có cần tra web không.

    Trả về: (can_tra: bool, ly_do: str)
    """
    if not noi_dung:
        return False, "Không có nội dung."

    t = noi_dung.lower()
    ly_do_list = []

    # 1. Kiểm tra 15 nhóm từ khóa
    for nhom, tu_khoa in TIN_HIEU_TRA_WEB.items():
        for tk in tu_khoa:
            if tk in t:
                ly_do_list.append(f"từ khóa '{tk}' ({nhom})")
                break
        if ly_do_list:
            break  # Đã đủ 1 lý do

    # 2. Kiểm tra mốc thời gian cụ thể
    if not ly_do_list and _co_moc_thoi_gian(noi_dung):
        ly_do_list.append("có mốc thời gian cụ thể")

    # 3. Kiểm tra tên riêng
    if not ly_do_list and _co_ten_rieng(noi_dung):
        ly_do_list.append("có tên riêng (công ty/người/địa danh)")

    # 4. Kiểm tra loại task
    if not ly_do_list and loai_task:
        nhom = (loai_task.get("nhom") or "").lower()
        if nhom in ("tra cứu", "tin tức", "so sánh", "định nghĩa"):
            ly_do_list.append(f"task thuộc nhóm '{nhom}'")

    if ly_do_list:
        return True, " | ".join(ly_do_list[:2])

    return False, ""


# ================================================================
# PHÂN LOẠI TRA WEB
# ================================================================
def phan_loai_tra_web(noi_dung):
    """Phân loại task tra web. Trả về tên loại hoặc ''."""
    if not noi_dung:
        return ""

    t = noi_dung.lower()

    # Ưu tiên theo thứ tự
    uu_tien = [
        "tin_tuc", "tai_chinh", "the_thao", "y_te", "phap_luat",
        "hoc_thuat", "lap_trinh", "san_pham", "lien_he",
        "so_sanh", "hướng_dẫn", "so_lieu", "dia_ly", "định_nghĩa",
    ]

    for loai in uu_tien:
        for tk in LOAI_TRA_WEB.get(loai, []):
            if tk in t:
                return loai

    return ""


# ================================================================
# TẠO TRUY VẤN
# ================================================================
def _tao_truy_van(noi_dung, loai=""):
    """Tạo truy vấn tìm kiếm tối ưu."""
    if not noi_dung:
        return ""

    tu_bo = [
        "cho tôi", "giúp tôi", "hãy", "vui lòng", "làm ơn",
        "có thể", "bạn", "ơi", "ạ", "nhé", "nha", "đi",
        "tôi muốn", "mình muốn", "tôi cần", "mình cần",
        "cho mình", "cho tôi biết", "cho mình biết",
    ]

    ket_qua = noi_dung
    for tu in tu_bo:
        ket_qua = re.sub(r"\b" + re.escape(tu) + r"\b", "", ket_qua, flags=re.I)

    ket_qua = re.sub(r"[.!?]+$", "", ket_qua.strip())
    ket_qua = re.sub(r"\s+", " ", ket_qua).strip()

    if len(ket_qua) < 5:
        ket_qua = noi_dung.strip()

    return ket_qua[:200]


# ================================================================
# GỌI TRA WEB
# ================================================================
def _goi_tra_web(cau_hoi):
    """Gọi công cụ Tra web."""
    ket_qua = {"thanh_cong": False, "ket_qua": [], "nguon": [], "loi": ""}

    if not cau_hoi:
        ket_qua["loi"] = "Câu hỏi rỗng."
        return ket_qua

    try:
        from dai_nao.goi_tra_web import goi_tra_web
        ket_qua_tho = goi_tra_web(cau_hoi)
    except ImportError:
        ket_qua["loi"] = "goi_tra_web.py chưa có."
        return ket_qua
    except Exception as e:
        ket_qua["loi"] = f"Tra web lỗi: {e}"
        return ket_qua

    if not ket_qua_tho:
        ket_qua["loi"] = "Tra web không trả kết quả."
        return ket_qua

    if isinstance(ket_qua_tho, str):
        ket_qua["thanh_cong"] = True
        ket_qua["ket_qua"] = [{"tieu_de": "", "mo_ta": ket_qua_tho, "url": ""}]
        ket_qua["nguon"] = ["tra_web"]
    elif isinstance(ket_qua_tho, dict):
        ket_qua["thanh_cong"] = bool(ket_qua_tho.get("thanh_cong", True))
        ket_qua["ket_qua"] = ket_qua_tho.get("ket_qua", []) or []
        ket_qua["nguon"] = ket_qua_tho.get("nguon", []) or []
        ket_qua["loi"] = ket_qua_tho.get("loi", "")
    elif isinstance(ket_qua_tho, list):
        ket_qua["thanh_cong"] = True
        ket_qua["ket_qua"] = ket_qua_tho
    else:
        ket_qua["loi"] = "Kết quả không hợp lệ."

    return ket_qua


# ================================================================
# TỔNG HỢP KẾT QUẢ
# ================================================================
def tong_hop_ket_qua(danh_sach):
    """Tổng hợp kết quả tìm kiếm thành chuỗi."""
    if not danh_sach:
        return ""

    phan = []
    for i, item in enumerate(danh_sach[:SO_KET_QUA_TOI_DA], 1):
        tieu_de = (item.get("tieu_de") or "").strip()
        mo_ta = (item.get("mo_ta") or "").strip()
        url = (item.get("url") or "").strip()

        if len(mo_ta) > DO_DAI_MO_TA_TOI_DA:
            mo_ta = mo_ta[:DO_DAI_MO_TA_TOI_DA] + "..."

        dong = f"{i}. {tieu_de}"
        if mo_ta:
            dong += f"\n   {mo_ta}"
        if url:
            dong += f"\n   🔗 {url}"

        phan.append(dong)

    return "\n\n".join(phan)


# ================================================================
# TẠO CÂU TRẢ LỜI
# ================================================================
def tao_cau_tra_loi(ket_qua_tra_web, noi_dung_goc, loai=""):
    """Tạo câu trả lời cho user."""
    phan = []

    if not ket_qua_tra_web.get("thanh_cong"):
        phan.append("🌐 Ta đã thử tra web nhưng chưa có kết quả.")
        if ket_qua_tra_web.get("loi"):
            phan.append(f"\n🔴 Lỗi: {ket_qua_tra_web['loi']}")
        phan.append(
            "\n💡 Bạn có thể:\n"
            "  1. Kiểm tra lại API key tra web đã dán chưa.\n"
            "  2. Đợi API reset quota (mỗi tháng).\n"
            "  3. Hỏi cụ thể hơn để ta xử lý bằng kiến thức sẵn có."
        )
        return "\n".join(phan)

    danh_sach = ket_qua_tra_web.get("ket_qua", [])
    if not danh_sach:
        phan.append("🌐 Ta tra web nhưng không tìm thấy kết quả phù hợp.")
        phan.append("💡 Bạn thử hỏi cách khác nhé.")
        return "\n".join(phan)

    mo_dau = {
        "tin_tuc": "🌐 Đây là tin tức mới nhất ta tìm được:",
        "tai_chinh": "🌐 Đây là thông tin tài chính mới nhất:",
        "the_thao": "🌐 Đây là tin thể thao mới nhất:",
        "định_nghĩa": "🌐 Đây là định nghĩa ta tra được:",
        "so_sanh": "🌐 Đây là thông tin so sánh ta tìm được:",
        "hướng_dẫn": "🌐 Đây là hướng dẫn ta tìm được:",
        "so_lieu": "🌐 Đây là số liệu ta tra được:",
        "dia_ly": "🌐 Đây là thông tin địa lý ta tra được:",
        "san_pham": "🌐 Đây là thông tin sản phẩm ta tìm được:",
        "lien_he": "🌐 Đây là thông tin liên hệ ta tra được:",
        "lap_trinh": "🌐 Đây là tài liệu lập trình ta tra được:",
        "y_te": "🌐 Đây là thông tin y tế ta tra được:",
        "phap_luat": "🌐 Đây là thông tin pháp luật ta tra được:",
        "hoc_thuat": "🌐 Đây là tài liệu học thuật ta tra được:",
    }

    phan.append(mo_dau.get(loai, "🌐 Đây là kết quả ta tra được từ web:"))
    phan.append("")
    phan.append(tong_hop_ket_qua(danh_sach))

    nguon = ket_qua_tra_web.get("nguon", [])
    if nguon:
        phan.append(f"\n📚 Nguồn: {', '.join(nguon)}")

    return "\n".join(phan)


# ================================================================
# HÀM CHÍNH
# ================================================================
def xu_ly_tra_web(noi_dung, yeu_to=None, loai_task=None):
    """Xử lý task tra web. Trả về dict đầy đủ."""
    ket_qua = {
        "thanh_cong": False, "tra_loi": "", "ket_qua_tho": [],
        "nguon": [], "so_ket_qua": 0, "loi": "",
    }

    if not noi_dung:
        ket_qua["loi"] = "Không có nội dung."
        return ket_qua

    _ghi_log("tra-web", f"Nhận task tra web: {noi_dung[:80]}")

    # 1. Phân loại
    loai = phan_loai_tra_web(noi_dung)

    # 2. Tạo truy vấn
    truy_van = _tao_truy_van(noi_dung, loai)

    # 3. Gọi tra web
    ket_qua_tra = _goi_tra_web(truy_van)

    if not ket_qua_tra.get("thanh_cong"):
        ket_qua["loi"] = ket_qua_tra.get("loi", "")
        ket_qua["tra_loi"] = tao_cau_tra_loi(ket_qua_tra, noi_dung, loai)
        return ket_qua

    # 4. Tổng hợp
    danh_sach = ket_qua_tra.get("ket_qua", [])[:SO_KET_QUA_TOI_DA]

    ket_qua.update({
        "thanh_cong": True,
        "ket_qua_tho": danh_sach,
        "nguon": ket_qua_tra.get("nguon", []),
        "so_ket_qua": len(danh_sach),
        "tra_loi": tao_cau_tra_loi(ket_qua_tra, noi_dung, loai),
    })

    _ghi_log(
        "tra-web",
        f"Tra web thành công: {len(danh_sach)} kết quả, loại={loai}",
    )

    return ket_qua


# ================================================================
# HÀM PHỤ
# ================================================================
def trich_url(danh_sach):
    if not danh_sach:
        return []
    return [item.get("url") for item in danh_sach if item.get("url")]


def trich_tieu_de(danh_sach):
    if not danh_sach:
        return []
    return [item.get("tieu_de") for item in danh_sach if item.get("tieu_de")]


def gop_mo_ta(danh_sach):
    if not danh_sach:
        return ""
    tat_ca = [item.get("mo_ta", "") for item in danh_sach if item.get("mo_ta")]
    return "\n\n".join(tat_ca)


def liet_ke_tin_hieu():
    """Liệt kê các nhóm tín hiệu tra web."""
    return {
        nhom: len(tu_khoa)
        for nhom, tu_khoa in TIN_HIEU_TRA_WEB.items()
    }


def dem_tu_khoa():
    """Đếm tổng số từ khóa tra web."""
    return sum(len(tk) for tk in TIN_HIEU_TRA_WEB.values())
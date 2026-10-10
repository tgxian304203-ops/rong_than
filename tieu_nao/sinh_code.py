"""
sinh_code.py - Sinh code mới bằng Model.

Nhiệm vụ:
    - Nhận yêu cầu sinh code.
    - Tạo prompt cho Model.
    - Gọi Model qua goi_model.
    - Trích code từ kết quả Model.
    - Trả về code + ngôn ngữ.

Nguyên tắc:
    - Model là công cụ — không giữ ngữ cảnh.
    - Dùng key Model (không dùng key Boss).
    - Nếu Model lỗi → xoay key Model.
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
# NGÔN NGỮ HỖ TRỢ
# ================================================================
NGON_NGU_HO_TRO = [
    "python", "javascript", "typescript", "html", "css",
    "json", "sql", "bash", "markdown", "php", "ruby", "go", "rust",
]


# ================================================================
# SINH CODE
# ================================================================
def sinh_code(du_lieu):
    """
    Sinh code từ yêu cầu.

    du_lieu: {
        noi_dung, chu_so_huu, id_chat, lich_su, buoc
    }

    Trả về: {
        thanh_cong, code?, ngon_ngu?, tra_loi?, loi?
    }
    """
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    noi_dung = du_lieu.get("noi_dung", "")
    if not noi_dung:
        return {"thanh_cong": False, "loi": "Thiếu yêu cầu."}

    # Đoán ngôn ngữ từ yêu cầu
    ngon_ngu = doan_ngon_ngu(noi_dung)

    # Tạo prompt cho Model
    prompt = _tao_prompt_sinh_code(noi_dung, ngon_ngu)

    du_lieu_prompt = dict(du_lieu)
    du_lieu_prompt["noi_dung"] = prompt

    # Gọi Model
    try:
        from tieu_nao.model.goi_model import goi_model
        ket_qua = goi_model(du_lieu_prompt)
    except Exception as e:
        _ghi_log("loi", f"Gọi Model lỗi: {e}")
        return {"thanh_cong": False, "loi": f"Gọi Model lỗi: {e}"}

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    tra_loi = ket_qua.get("tra_loi", "")

    # Trích code từ kết quả
    code = _trich_code(tra_loi, ngon_ngu)

    if not code:
        # Model trả lời mà không có code → trả lời thẳng
        return {
            "thanh_cong": True,
            "tra_loi": tra_loi,
            "code": None,
            "ngon_ngu": None,
        }

    _ghi_log("tieu-nao", f"Sinh code OK: {len(code)} ký tự ({ngon_ngu})")

    return {
        "thanh_cong": True,
        "tra_loi": tra_loi,
        "code": code,
        "ngon_ngu": ngon_ngu,
    }


# ================================================================
# TẠO PROMPT
# ================================================================
def _tao_prompt_sinh_code(noi_dung, ngon_ngu):
    """Tạo prompt yêu cầu Model sinh code."""
    return f"""Viết code {ngon_ngu} cho yêu cầu sau:

{noi_dung}

Yêu cầu:
- Chỉ trả về code trong khối markdown có ghi ngôn ngữ.
- Không giải thích dài dòng.
- Code phải chạy được."""


# ================================================================
# ĐOÁN NGÔN NGỮ
# ================================================================
def doan_ngon_ngu(noi_dung):
    """Đoán ngôn ngữ lập trình từ yêu cầu."""
    if not noi_dung:
        return "python"

    t = noi_dung.lower()

    bang = {
        "python": ["python", "py ", ".py", "django", "flask", "pandas", "numpy"],
        "javascript": ["javascript", "js ", ".js", "node", "react", "vue"],
        "typescript": ["typescript", "ts ", ".ts", "tsx"],
        "html": ["html", "<html", "<div", "<body"],
        "css": ["css", "style", "giao diện"],
        "sql": ["sql", "select ", "insert ", "database"],
        "bash": ["bash", "shell", "terminal", "command line"],
        "json": ["json", "{}"],
    }

    for ngon_ngu, tu_khoa in bang.items():
        for tu in tu_khoa:
            if tu in t:
                return ngon_ngu

    return "python"


# ================================================================
# TRÍCH CODE
# ================================================================
def _trich_code(tra_loi, ngon_ngu):
    """Trích code từ câu trả lời Model (bỏ dấu backtick)."""
    if not tra_loi:
        return ""

    bt = chr(96) * 3

    # Thử tìm code có ghi ngôn ngữ
    mau = bt + ngon_ngu + r"\s*([\s\S]*?)" + bt
    khop = re.search(mau, tra_loi, re.IGNORECASE)
    if khop:
        return khop.group(1).strip()

    # Thử tìm code không ghi ngôn ngữ
    mau = bt + r"(?:\w+)?\s*([\s\S]*?)" + bt
    khop = re.search(mau, tra_loi)
    if khop:
        return khop.group(1).strip()

    # Không có code block → trả nguyên (có thể Model trả code trực tiếp)
    return ""


# ================================================================
# SINH CODE NHANH
# ================================================================
def sinh_code_nhanh(noi_dung, chu_so_huu="khach", id_chat=""):
    """Sinh code nhanh không cần đầy đủ du_lieu."""
    return sinh_code({
        "noi_dung": noi_dung,
        "chu_so_huu": chu_so_huu,
        "id_chat": id_chat,
        "lich_su": [],
    })


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả sinh code."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        if ket_qua.get("code"):
            return f"✅ Sinh code: {len(ket_qua['code'])} ký tự ({ket_qua.get('ngon_ngu', '')})"
        return f"✅ Trả lời: {len(ket_qua.get('tra_loi', ''))} ký tự"
    return f"❌ Sinh code lỗi: {ket_qua.get('loi', '')[:100]}"
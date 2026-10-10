"""
sinh_code.py - Sinh code mới bằng Model.

SỬA:
    - Prompt yêu cầu Model dùng thư viện cho phép.
    - Với dự án web → yêu cầu sinh cả backend + frontend.
"""

import re


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _in_debug(noi_dung):
    try:
        print(f"[DEBUG-SINH-CODE] {noi_dung}", flush=True)
    except Exception:
        pass


NGON_NGU_HO_TRO = [
    "python", "javascript", "typescript", "html", "css",
    "json", "sql", "bash", "markdown", "php", "ruby", "go", "rust",
]


def sinh_code(du_lieu):
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    noi_dung = du_lieu.get("noi_dung", "")
    if not noi_dung:
        return {"thanh_cong": False, "loi": "Thiếu yêu cầu."}

    ngon_ngu = doan_ngon_ngu(noi_dung)
    _in_debug(f"Ngôn ngữ đoán: {ngon_ngu}")

    # Nếu là web → sinh cả backend + frontend
    if la_du_an_web(noi_dung):
        _in_debug("Dự án WEB → sinh backend + frontend")
        ngon_ngu = "python"  # backend chính

    prompt = _tao_prompt_sinh_code(noi_dung, ngon_ngu)
    _in_debug(f"Prompt: {prompt[:200]}")

    du_lieu_prompt = dict(du_lieu)
    du_lieu_prompt["noi_dung"] = prompt

    try:
        from tieu_nao.model.goi_model import goi_model
        ket_qua = goi_model(du_lieu_prompt)
    except Exception as e:
        _ghi_log("loi", f"Gọi Model lỗi: {e}")
        return {"thanh_cong": False, "loi": f"Gọi Model lỗi: {e}"}

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    tra_loi = ket_qua.get("tra_loi", "")
    code = _trich_code(tra_loi, ngon_ngu)

    if not code:
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


def la_du_an_web(noi_dung):
    """Kiểm tra có phải dự án web không."""
    if not noi_dung:
        return False
    t = noi_dung.lower()
    tu_khoa = [
        "web", "website", "trang web", "app web",
        "html", "css", "javascript",
        "frontend", "backend",
        "giao diện", "giao dien",
        "trang chủ", "trang chu",
        "dashboard", "form", "bảng",
    ]
    for tk in tu_khoa:
        if tk in t:
            return True
    return False


def _tao_prompt_sinh_code(noi_dung, ngon_ngu):
    """
    Tạo prompt yêu cầu Model sinh code.

    - Yêu cầu dùng thư viện chuẩn + thư viện đã cài.
    - Không dùng thư viện lạ.
    """
    phan = [
        f"Viết code {ngon_ngu} cho yêu cầu sau:",
        "",
        noi_dung,
        "",
        "YÊU CẦU:",
        "- Chỉ trả về code trong khối markdown có ghi ngôn ngữ.",
        "- Không giải thích dài dòng.",
        "- Code phải chạy được.",
        "- Chỉ dùng thư viện có sẵn:",
        "  + Python: flask, flask-cors, flask-jwt-extended, pymongo,",
        "    requests, numpy, pandas, sympy, openpyxl, python-dotenv,",
        "    python-docx, PyPDF2, Pillow, PyYAML, bcrypt, werkzeug,",
        "    jinja2, python-dateutil, pytz.",
        "  + KHÔNG dùng thư viện lạ chưa cài.",
        "- Với dự án web: viết backend Python (Flask) trước,",
        "  frontend HTML/CSS/JS viết riêng.",
    ]
    return "\n".join(phan)


def doan_ngon_ngu(noi_dung):
    if not noi_dung:
        return "python"

    t = noi_dung.lower()

    bang = {
        "python": ["python", "py ", ".py", "django", "flask", "pandas", "numpy"],
        "javascript": ["javascript", "js ", ".js", "node", "react", "vue"],
        "typescript": ["typescript", "ts ", ".ts", "tsx"],
        "html": ["html", "<html", "<div", "<body"],
        "css": ["css", "style"],
        "sql": ["sql", "select ", "insert ", "database"],
        "bash": ["bash", "shell", "terminal"],
        "json": ["json"],
    }

    for ngon_ngu, tu_khoa in bang.items():
        for tu in tu_khoa:
            if tu in t:
                return ngon_ngu

    return "python"


def _trich_code(tra_loi, ngon_ngu):
    if not tra_loi:
        return ""

    bt = chr(96) * 3

    mau = bt + ngon_ngu + r"\s*([\s\S]*?)" + bt
    khop = re.search(mau, tra_loi, re.IGNORECASE)
    if khop:
        return khop.group(1).strip()

    mau = bt + r"(?:\w+)?\s*([\s\S]*?)" + bt
    khop = re.search(mau, tra_loi)
    if khop:
        return khop.group(1).strip()

    return ""


def sinh_code_nhanh(noi_dung, chu_so_huu="khach", id_chat=""):
    return sinh_code({
        "noi_dung": noi_dung,
        "chu_so_huu": chu_so_huu,
        "id_chat": id_chat,
        "lich_su": [],
    })


def tom_tat(ket_qua):
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        if ket_qua.get("code"):
            return f"✅ Sinh code: {len(ket_qua['code'])} ký tự ({ket_qua.get('ngon_ngu', '')})"
        return f"✅ Trả lời: {len(ket_qua.get('tra_loi', ''))} ký tự"
    return f"❌ Sinh code lỗi: {ket_qua.get('loi', '')[:100]}"
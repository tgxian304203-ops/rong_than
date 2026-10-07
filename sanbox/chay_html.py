"""
chay_html.py - Chạy code HTML qua Sandbox Rồng Thần.

Nhiệm vụ:
    - chay_html_backend(code): kiểm tra cú pháp HTML ở backend (CÁCH 3).
    - chay_html(du_lieu): API — trả code + trạng thái.
    - tao_html_sandbox(code): tạo HTML sandbox đầy đủ (fallback).

ĐÃ SỬA:
    - CÁCH 3: Backend kiểm tra cú pháp HTML cơ bản, trả code cho client.
    - HTML không "chạy" như Python — chỉ render trên client.
    - Client render HTML trong iframe.

Quy tắc:
    - HTML là ngôn ngữ khai báo → không có runtime error.
    - Backend kiểm tra: thẻ cân bằng, độ dài, ký tự lạ.
    - Client render HTML → hiển thị kết quả.

Trả về:
    {
        thanh_cong: bool,
        code: str,
        ngon_ngu: "html",
        loi: str,
        canh_bao: str,
        thoi_gian: float,
    }
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
DO_DAI_CODE_TOI_DA = 100000


# ================================================================
# KIỂM TRA CÚ PHÁP HTML
# ================================================================
def _kiem_tra_the_can_balanced(code):
    """
    Kiểm tra các thẻ HTML phổ biến có cân bằng không.

    Trả về: (True, []) hoặc (False, [danh sách thẻ không cân bằng]).
    """
    the_can_kiem_tra = [
        "html", "head", "body", "div", "span", "p", "a",
        "ul", "ol", "li", "table", "tr", "td", "th",
        "form", "input", "button", "script", "style",
    ]

    thieu = []
    for the in the_can_kiem_tra:
        # Thẻ tự đóng (input, br, img, ...) — bỏ qua
        if the in ("input", "br", "img", "hr", "meta", "link"):
            continue

        # Đếm thẻ mở và đóng
        mau_mo = rf"<{the}\b[^>]*?(?<!/)>"
        mau_dong = rf"</{the}\s*>"

        so_mo = len(re.findall(mau_mo, code, re.I))
        so_dong = len(re.findall(mau_dong, code, re.I))

        if so_mo != so_dong:
            thieu.append(f"<{the}> ({so_mo} mở, {so_dong} đóng)")

    if thieu:
        return False, thieu
    return True, []


def _kiem_tra_ky_tu_la(code):
    """
    Kiểm tra ký tự lạ (không phải ASCII, không phải tiếng Việt, không phải emoji).

    Trả về: list ký tự lạ (tối đa 10).
    """
    if not code:
        return []

    # Cho phép: ASCII, tiếng Việt, emoji, ký tự đặc biệt HTML
    mau_hop_le = re.compile(
        r"[\x00-\x7F"
        r"\u00C0-\u1EF9"  # Latin mở rộng + tiếng Việt
        r"\u1F00-\u1FFF"  # Greek mở rộng
        r"\u2000-\u206F"  # Dấu câu
        r"\u2190-\u21FF"  # Mũi tên
        r"\u2200-\u22FF"  # Toán học
        r"\u2600-\u26FF"  # Biểu tượng
        r"\u2700-\u27BF"  # Dingbat
        r"\u1F300-\u1F9FF"  # Emoji
        r"\uFE00-\uFE0F"  # Biến thể
        r"]"
    )

    ky_tu_la = []
    for c in code:
        if not mau_hop_le.match(c):
            ky_tu_la.append(c)
            if len(ky_tu_la) >= 10:
                break

    return ky_tu_la


# ================================================================
# CHẠY HTML Ở BACKEND (CÁCH 3)
# ================================================================
def chay_html_backend(code):
    """
    Kiểm tra cú pháp HTML ở backend.

    HTML không "chạy" như Python — chỉ render trên client.
    Backend kiểm tra:
        - Độ dài.
        - Thẻ cân bằng.
        - Ký tự lạ.

    Trả về dict đầy đủ.
    """
    ket_qua = {
        "thanh_cong": False,
        "code": "",
        "ngon_ngu": "html",
        "loi": "",
        "canh_bao": "",
        "thoi_gian": 0.0,
    }

    if not code:
        ket_qua["loi"] = "Code rỗng."
        return ket_qua

    if len(code) > DO_DAI_CODE_TOI_DA:
        ket_qua["loi"] = f"Code quá dài (>{DO_DAI_CODE_TOI_DA} ký tự)."
        return ket_qua

    thoi_gian_bat_dau = time.time()

    # Kiểm tra thẻ cân bằng
    the_ok, the_loi = _kiem_tra_the_can_balanced(code)
    if not the_ok:
        ket_qua["loi"] = "Thẻ HTML không cân bằng: " + ", ".join(the_loi[:5])
        ket_qua["code"] = code
        ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
        return ket_qua

    # Kiểm tra ký tự lạ
    ky_tu_la = _kiem_tra_ky_tu_la(code)
    if ky_tu_la:
        ket_qua["canh_bao"] = "Có ký tự lạ: " + " ".join(repr(c) for c in ky_tu_la[:5])

    ket_qua["thanh_cong"] = True
    ket_qua["code"] = code
    ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)

    _ghi_log(
        "sandbox",
        f"Kiểm tra HTML backend: {len(code)} ký tự, OK",
    )

    return ket_qua


# ================================================================
# TÁCH CODE HTML
# ================================================================
def _tach_code_html(code):
    """Tách code HTML thành markup, style, script."""
    ket_qua = {"markup": "", "style": "", "script": ""}

    if not code:
        return ket_qua

    khop_style = re.findall(r"<style[^>]*>([\s\S]*?)</style>", code, re.I)
    if khop_style:
        ket_qua["style"] = "\n".join(khop_style).strip()

    khop_script = re.findall(r"<script[^>]*>([\s\S]*?)</script>", code, re.I)
    if khop_script:
        ket_qua["script"] = "\n".join(khop_script).strip()

    html_con_lai = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", code, flags=re.I)
    html_con_lai = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", html_con_lai, flags=re.I)
    html_con_lai = html_con_lai.strip()

    if html_con_lai:
        ket_qua["markup"] = html_con_lai
    else:
        ket_qua["markup"] = _tao_html_mau(code)

    return ket_qua


def _tao_html_mau(code):
    """Tạo HTML mẫu nếu user chỉ cung cấp CSS hoặc JS."""
    if not re.search(r"<[a-zA-Z]", code) and "{" in code:
        return '<div class="container">Hello World</div>'

    if re.search(r"\b(console\.log|function|const|let|var)\b", code):
        return '<div id="app">Hello World</div>'

    return "<h1>Hello Rồng Thần 🐉</h1>"


# ================================================================
# HÀM CHÍNH — API
# ================================================================
def chay_html(du_lieu):
    """
    API chính — kiểm tra HTML backend + trả code cho client.

    CÁCH 3: Backend kiểm tra, client render.
    """
    ket_qua = {
        "thanh_cong": False,
        "che_do": "backend",
        "code": "",
        "ngon_ngu": "html",
        "loi": "",
        "canh_bao": "",
        "huong_dan_client": {},
    }

    if not du_lieu:
        ket_qua["loi"] = "Không có dữ liệu."
        return ket_qua

    code = du_lieu.get("code") or ""

    if not code:
        ket_qua["loi"] = "Code rỗng."
        return ket_qua

    # Kiểm tra backend
    ket_qua_backend = chay_html_backend(code)

    ket_qua.update({
        "thanh_cong": ket_qua_backend.get("thanh_cong", False),
        "code": code,
        "loi": ket_qua_backend.get("loi", ""),
        "canh_bao": ket_qua_backend.get("canh_bao", ""),
        "thoi_gian": ket_qua_backend.get("thoi_gian", 0.0),
    })

    return ket_qua


# ================================================================
# TẠO HTML SANDBOX ĐẦY ĐỦ (FALLBACK)
# ================================================================
def tao_html_sandbox(code, timeout=10):
    """
    Tạo HTML hoàn chỉnh để render code HTML trong iframe.

    Fallback nếu client không tự render được.
    """
    phan = _tach_code_html(code)

    markup = phan.get("markup", "")
    style = phan.get("style", "")
    script = phan.get("script", "")

    # Nếu markup đã có <html> → trả nguyên
    if "<html" in markup.lower():
        if style:
            markup = markup.replace("</head>", f"<style>{style}</style></head>")
        if script:
            markup = markup.replace("</body>", f"<script>{script}</script></body>")
        return markup

    # Ngược lại → bọc HTML đầy đủ
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sandbox HTML - Rồng Thần</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; padding: 10px; font-family: sans-serif; }}
        {style}
    </style>
</head>
<body>
    {markup}
    <script>
        {script}
    </script>
</body>
</html>"""


# ================================================================
# KIỂM TRA CÚ PHÁP
# ================================================================
def kiem_tra_cu_phap_html(code):
    """Kiểm tra cú pháp HTML cơ bản."""
    if not code:
        return False, "Code rỗng."

    ok, the_loi = _kiem_tra_the_can_balanced(code)
    if not ok:
        return False, "Thẻ không cân bằng: " + ", ".join(the_loi[:5])

    return True, ""


def sandbox_san_sang():
    """Sandbox sẵn sàng."""
    return True


def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ HTML OK: {len(ket_qua.get('code', ''))} ký tự"
    return f"❌ HTML lỗi: {(ket_qua.get('loi') or '')[:150]}"
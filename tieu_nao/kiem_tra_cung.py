"""
kiem_tra_cung.py - Kiểm tra cứng code (syntax, format).

Nhiệm vụ:
    - Kiểm tra cú pháp code (syntax).
    - Kiểm tra format (dấu ngoặc, indent).
    - Kiểm tra độ dài.
    - KHÔNG chạy code — chỉ đọc.

Nguyên tắc:
    - Đây là kiểm tra TĨNH (static) trước khi chạy sandbox.
    - Nếu fail → báo lỗi luôn, không cần chạy sandbox.
    - Hỗ trợ Python, JS, HTML.
"""

import ast
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
# HẰNG SỐ
# ================================================================
DO_DAI_CODE_TOI_DA = 100000
DO_DAI_CODE_TOI_THIEU = 1


# ================================================================
# KIỂM TRA CỨNG
# ================================================================
def kiem_tra_cung(code, ngon_ngu="python"):
    """
    Kiểm tra cứng code.

    Trả về: { thanh_cong: bool, loi: str? }
    """
    if not code:
        return {"thanh_cong": False, "loi": "Code rỗng."}

    # Kiểm tra độ dài
    if len(code) < DO_DAI_CODE_TOI_THIEU:
        return {"thanh_cong": False, "loi": "Code quá ngắn."}

    if len(code) > DO_DAI_CODE_TOI_DA:
        return {"thanh_cong": False, "loi": "Code quá dài."}

    # Kiểm tra theo ngôn ngữ
    if ngon_ngu == "python":
        return _kiem_tra_python(code)
    if ngon_ngu in ("javascript", "typescript", "js", "ts"):
        return _kiem_tra_javascript(code)
    if ngon_ngu == "html":
        return _kiem_tra_html(code)

    # Ngôn ngữ khác → bỏ qua
    return {"thanh_cong": True}


# ================================================================
# KIỂM TRA PYTHON
# ================================================================
def _kiem_tra_python(code):
    """Kiểm tra cú pháp Python bằng ast.parse."""
    try:
        ast.parse(code)
        return {"thanh_cong": True}
    except SyntaxError as e:
        dong = e.lineno if e.lineno else "?"
        return {
            "thanh_cong": False,
            "loi": f"Lỗi cú pháp dòng {dong}: {e.msg}",
        }
    except Exception as e:
        return {"thanh_cong": False, "loi": f"Lỗi parse: {e}"}


# ================================================================
# KIỂM TRA JAVASCRIPT / TYPESCRIPT
# ================================================================
def _kiem_tra_javascript(code):
    """Kiểm tra cú pháp JS (kiểm tra cơ bản)."""
    # Kiểm tra dấu ngoặc cân bằng
    kiem_tra_ngoac = _kiem_tra_ngoac_can_bang(code)
    if not kiem_tra_ngoac.get("thanh_cong"):
        return kiem_tra_ngoac

    return {"thanh_cong": True}


# ================================================================
# KIỂM TRA HTML
# ================================================================
def _kiem_tra_html(code):
    """Kiểm tra cú pháp HTML cơ bản."""
    # Kiểm tra thẻ cân bằng
    the_kiem_tra = ["html", "head", "body", "div", "span", "p", "a",
                    "ul", "ol", "li", "table", "form", "script", "style"]

    thieu = []
    for the in the_kiem_tra:
        so_mo = len(re.findall(rf"<{the}\b", code, re.I))
        so_dong = len(re.findall(rf"</{the}\s*>", code, re.I))
        if so_mo != so_dong:
            thieu.append(f"<{the}> ({so_mo} mở, {so_dong} đóng)")

    if thieu:
        return {
            "thanh_cong": False,
            "loi": "Thẻ không cân bằng: " + ", ".join(thieu[:5]),
        }

    return {"thanh_cong": True}


# ================================================================
# KIỂM TRA NGOẶC CÂN BẰNG
# ================================================================
def _kiem_tra_ngoac_can_bang(code):
    """Kiểm tra ngoặc (), {}, [] có cân bằng không."""
    cap = {"(": ")", "{": "}", "[": "]"}
    nguoc = {")": "(", "}": "{", "]": "["}
    stack = []

    # Bỏ chuỗi và comment để tránh đếm sai
    code_sach = _xoa_chuoi_va_comment(code)

    for i, c in enumerate(code_sach):
        if c in cap:
            stack.append((c, i))
        elif c in nguoc:
            if not stack:
                return {
                    "thanh_cong": False,
                    "loi": f"Ngoặc đóng dư tại vị trí {i}: {c}",
                }
            mo, _ = stack.pop()
            if mo != nguoc[c]:
                return {
                    "thanh_cong": False,
                    "loi": f"Ngoặc không khớp: {mo} ... {c}",
                }

    if stack:
        con_lai = [f"{c} tại {i}" for c, i in stack[:3]]
        return {
            "thanh_cong": False,
            "loi": "Ngoặc mở chưa đóng: " + ", ".join(con_lai),
        }

    return {"thanh_cong": True}


def _xoa_chuoi_va_comment(code):
    """Xóa chuỗi và comment để đếm ngoặc chính xác."""
    # Xóa comment // và /* */
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    # Xóa comment # (Python)
    code = re.sub(r"#[^\n]*", "", code)
    # Xóa chuỗi (đơn giản)
    code = re.sub(r'"[^"]*"', '""', code)
    code = re.sub(r"'[^']*'", "''", code)
    code = re.sub(r"`[^`]*`", "``", code)

    return code


# ================================================================
# KIỂM TRA ĐỘ DÀI
# ================================================================
def kiem_tra_do_dai(code, toi_da=DO_DAI_CODE_TOI_DA):
    """Kiểm tra code không vượt quá độ dài cho phép."""
    if not code:
        return {"thanh_cong": False, "loi": "Code rỗng."}
    if len(code) > toi_da:
        return {
            "thanh_cong": False,
            "loi": f"Code quá dài ({len(code)} > {toi_da}).",
        }
    return {"thanh_cong": True}


# ================================================================
# KIỂM TRA RỖNG
# ================================================================
def kiem_tra_rong(code):
    """Kiểm tra code có rỗng hoặc chỉ có comment không."""
    if not code or not code.strip():
        return {"thanh_cong": False, "loi": "Code rỗng."}

    # Bỏ comment
    code_sach = re.sub(r"#[^\n]*", "", code)
    code_sach = re.sub(r"//[^\n]*", "", code_sach)
    code_sach = re.sub(r"/\*[\s\S]*?\*/", "", code_sach)
    code_sach = re.sub(r'"""[\s\S]*?"""', "", code_sach)
    code_sach = re.sub(r"'''[\s\S]*?'''", "", code_sach)

    if not code_sach.strip():
        return {"thanh_cong": False, "loi": "Code chỉ có comment."}

    return {"thanh_cong": True}


# ================================================================
# KIỂM TRA TỔNG HỢP
# ================================================================
def kiem_tra_tong_hop(code, ngon_ngu="python"):
    """
    Kiểm tra tổng hợp: rỗng + độ dài + cú pháp.

    Trả về: { thanh_cong: bool, loi: str? }
    """
    # 1. Rỗng
    kq = kiem_tra_rong(code)
    if not kq.get("thanh_cong"):
        return kq

    # 2. Độ dài
    kq = kiem_tra_do_dai(code)
    if not kq.get("thanh_cong"):
        return kq

    # 3. Cú pháp
    return kiem_tra_cung(code, ngon_ngu)


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả kiểm tra."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return "✅ Kiểm tra cứng OK."
    return f"❌ Kiểm tra cứng lỗi: {ket_qua.get('loi', '')[:100]}"
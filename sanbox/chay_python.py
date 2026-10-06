"""
chay_python.py - Chạy code Python qua Sandbox Rồng Thần.

Nhiệm vụ:
    - chay_python(du_lieu): điều phối chạy code Python qua Pyodide.
    - _chuan_bi_du_lieu(code, timeout): chuẩn bị dữ liệu cho client.
    - _tao_huong_dan_client(code, timeout): tạo hướng dẫn JS cho client.
    - _kiem_tra_code_rỗng(code): kiểm tra code rỗng.
    - _uoc_luong_thoi_gian(code): ước lượng thời gian chạy.

Quy tắc:
    - Sandbox chạy CLIENT-SIDE bằng Pyodide (Python 3.13 qua WebAssembly).
    - Backend KHÔNG chạy code Python thật.
    - Backend trả hướng dẫn cho client để client chạy qua Pyodide.
    - Code chạy trong Web Worker để không block UI.
    - Timeout mặc định 10 giây (client-side).
    - Kết quả trả về qua stdout/stderr.

Trả về:
    {
        thanh_cong: bool,
        che_do: "client_side",
        code: str,
        ngon_ngu: "python",
        timeout: int,
        huong_dan_client: dict,
        loi: str,
    }

Tầng dữ liệu: Không.
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
TIMEOUT_MAC_DINH = 10        # giây
DO_DAI_CODE_TOI_DA = 50000   # ký tự
PYODIDE_VERSION = "v0.29.0"  # Pyodide mới nhất hỗ trợ Python 3.13.2


# ================================================================
# KIỂM TRA CODE
# ================================================================
def _kiem_tra_code_rong(code):
    """Kiểm tra code rỗng hoặc chỉ có comment."""
    if not code or not code.strip():
        return True

    # Bỏ comment
    code_clean = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
    code_clean = re.sub(r'"""[\s\S]*?"""', "", code_clean)
    code_clean = re.sub(r"'''[\s\S]*?'''", "", code_clean)

    return not code_clean.strip()


def _uoc_luong_thoi_gian(code):
    """
    Ước lượng thời gian chạy dựa trên code.
    Trả về số giây.
    """
    if not code:
        return 1

    so_dong = len(code.split("\n"))
    co_vong_lap = bool(re.search(r"\b(for|while)\b", code))
    co_numpy = "numpy" in code or "import np" in code
    co_pandas = "pandas" in code or "import pd" in code

    # Base
    thoi_gian = 1

    # Số dòng
    if so_dong > 100:
        thoi_gian += 2
    elif so_dong > 50:
        thoi_gian += 1

    # Vòng lặp
    if co_vong_lap:
        thoi_gian += 2

    # Thư viện nặng
    if co_numpy:
        thoi_gian += 1
    if co_pandas:
        thoi_gian += 2

    return min(thoi_gian, TIMEOUT_MAC_DINH)


def _chuan_bi_du_lieu(code, timeout=TIMEOUT_MAC_DINH):
    """
    Chuẩn bị dữ liệu cho client.

    Trả về: dict chứa code, timeout, pyodide_version, thư viện cần load.
    """
    if not code:
        return {}

    # Phát hiện import để tải trước thư viện
    imports = _trich_imports(code)

    return {
        "code": code,
        "timeout": timeout,
        "pyodide_version": PYODIDE_VERSION,
        "imports": imports,
        "do_dai": len(code),
        "so_dong": len(code.split("\n")),
    }


def _trich_imports(code):
    """
    Trích danh sách import từ code Python.
    Dùng để Pyodide tải trước package.
    """
    if not code:
        return []

    imports = set()

    # import x
    for khop in re.finditer(r"^\s*import\s+(\w+)", code, re.MULTILINE):
        imports.add(khop.group(1))

    # from x import y
    for khop in re.finditer(r"^\s*from\s+(\w+)", code, re.MULTILINE):
        imports.add(khop.group(1))

    # Bỏ các module builtin
    builtin = {
        "sys", "os", "re", "json", "time", "datetime", "math",
        "random", "collections", "itertools", "functools", "typing",
        "pathlib", "ast", "difflib", "hashlib", "secrets",
    }

    return list(imports - builtin)


# ================================================================
# TẠO HƯỚNG DẪN CHO CLIENT
# ================================================================
def _tao_huong_dan_client(code, timeout=TIMEOUT_MAC_DINH):
    """
    Tạo hướng dẫn JS cho client chạy code qua Pyodide.

    Trả về dict hướng dẫn:
        {
            "cach_chay": "pyodide",
            "pyodide_version": str,
            "code": str,
            "imports": [str],
            "timeout": int,
            "js_mau": str,       # Mã JS mẫu để client dùng
        }
    """
    du_lieu = _chuan_bi_du_lieu(code, timeout)
    imports = du_lieu.get("imports", [])

    # Tạo mã JS mẫu cho client
    js_mau = _tao_js_mau(code, imports, timeout)

    return {
        "cach_chay": "pyodide",
        "pyodide_version": PYODIDE_VERSION,
        "code": code,
        "imports": imports,
        "timeout": timeout,
        "js_mau": js_mau,
    }


def _tao_js_mau(code, imports, timeout):
    """Tạo mã JS mẫu để client chạy code Python qua Pyodide."""
    import json

    code_escaped = json.dumps(code)
    imports_escaped = json.dumps(imports)

    js = f"""// Chạy code Python qua Pyodide
async function chayPython() {{
    const output = document.getElementById('sandbox-output');
    output.textContent = '';

    try {{
        // Load Pyodide
        const pyodide = await loadPyodide({{
            indexURL: 'https://cdn.jsdelivr.net/pyodide/{PYODIDE_VERSION}/full/'
        }});

        // Tải trước các package cần thiết
        const imports = {imports_escaped};
        for (const pkg of imports) {{
            try {{
                await pyodide.loadPackage(pkg);
            }} catch (e) {{
                console.warn('Không load được package:', pkg);
            }}
        }}

        // Chạy code
        const code = {code_escaped};
        const ketQua = await pyodide.runPythonAsync(code);

        // Hiển thị kết quả
        if (ketQua !== undefined) {{
            output.textContent += ketQua;
        }}
    }} catch (err) {{
        output.textContent += 'Lỗi: ' + err.message;
    }}
}}

chayPython();"""

    return js


# ================================================================
# HÀM CHÍNH
# ================================================================
def chay_python(du_lieu):
    """
    Điều phối chạy code Python qua Sandbox.

    du_lieu: {
        code: str,          # Code Python cần chạy
        timeout: int?,      # Timeout (giây), mặc định 10
    }

    Trả về dict đầy đủ.
    """
    ket_qua = {
        "thanh_cong": False,
        "che_do": "client_side",
        "code": "",
        "ngon_ngu": "python",
        "timeout": TIMEOUT_MAC_DINH,
        "huong_dan_client": {},
        "loi": "",
    }

    if not du_lieu:
        ket_qua["loi"] = "Không có dữ liệu."
        return ket_qua

    code = du_lieu.get("code") or ""
    timeout = du_lieu.get("timeout") or TIMEOUT_MAC_DINH

    # Kiểm tra code
    if not code:
        ket_qua["loi"] = "Code rỗng."
        return ket_qua

    if _kiem_tra_code_rong(code):
        ket_qua["loi"] = "Code rỗng hoặc chỉ có comment."
        return ket_qua

    if len(code) > DO_DAI_CODE_TOI_DA:
        ket_qua["loi"] = f"Code quá dài (>{DO_DAI_CODE_TOI_DA} ký tự)."
        return ket_qua

    # Chuẩn hóa timeout
    try:
        timeout = max(1, min(30, int(timeout)))
    except (ValueError, TypeError):
        timeout = TIMEOUT_MAC_DINH

    # Ước lượng thời gian
    thoi_gian_uoc_tinh = _uoc_luong_thoi_gian(code)

    # Tạo hướng dẫn client
    huong_dan = _tao_huong_dan_client(code, timeout)

    ket_qua["thanh_cong"] = True
    ket_qua["code"] = code
    ket_qua["timeout"] = timeout
    ket_qua["huong_dan_client"] = huong_dan
    ket_qua["thoi_gian_uoc_tinh"] = thoi_gian_uoc_tinh

    _ghi_log(
        "sandbox",
        f"Chuẩn bị chạy Python: {len(code)} ký tự, "
        f"timeout={timeout}s, imports={huong_dan.get('imports', [])}",
    )

    return ket_qua


# ================================================================
# HÀM PHỤ: KIỂM TRA CÚ PHÁP
# ================================================================
def kiem_tra_cu_phap(code):
    """
    Kiểm tra cú pháp Python cơ bản (backend-side).
    Chỉ kiểm tra bằng ast.parse — không chạy code.

    Trả về: (True, "") hoặc (False, "lỗi").
    """
    if not code:
        return False, "Code rỗng."

    try:
        import ast
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Dòng {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


# ================================================================
# HÀM PHỤ: TẠO MÃ HTML CHO SANDBOX
# ================================================================
def tao_html_sandbox(code, timeout=TIMEOUT_MAC_DINH):
    """
    Tạo trang HTML hoàn chỉnh để chạy code Python qua Pyodide.

    Dùng khi cần hiển thị sandbox trong iframe.
    """
    huong_dan = _tao_huong_dan_client(code, timeout)
    js_mau = huong_dan.get("js_mau", "")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sandbox Rồng Thần</title>
    <script src="https://cdn.jsdelivr.net/pyodide/{PYODIDE_VERSION}/full/pyodide.js"></script>
    <style>
        body {{
            background: #000;
            color: #4ade80;
            font-family: monospace;
            padding: 10px;
            margin: 0;
        }}
        #sandbox-output {{
            background: #111;
            padding: 10px;
            border-radius: 8px;
            min-height: 100px;
            white-space: pre-wrap;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div id="sandbox-output">Đang tải Pyodide...</div>
    <script>
        {js_mau}
    </script>
</body>
</html>"""


# ================================================================
# HÀM PHỤ: KIỂM TRA SANDBOX SẴN SÀNG
# ================================================================
def sandbox_san_sang():
    """Kiểm tra sandbox sẵn sàng (có requests không)."""
    try:
        import requests
        return True
    except ImportError:
        return False


# ================================================================
# HÀM PHỤ: TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return (
            f"✅ Sandbox sẵn sàng: {ket_qua.get('do_dai', 0)} ký tự, "
            f"timeout={ket_qua.get('timeout')}s"
        )

    return f"❌ Sandbox lỗi: {ket_qua.get('loi', '')}"


# ================================================================
# HÀM PHỤ: DANH SÁCH PACKAGE PYODIDE HỖ TRỢ
# ================================================================
def danh_sach_package_ho_tro():
    """Trả danh sách package Pyodide hỗ trợ sẵn."""
    return [
        "numpy", "pandas", "scipy", "matplotlib", "scikit-learn",
        "sympy", "networkx", "statsmodels", "pillow", "lxml",
        "beautifulsoup4", "regex", "pyyaml", "cryptography",
        "micropip",
    ]


# ================================================================
# HÀM PHỤ: KIỂM TRA PYODIDE CÓ HỖ TRỢ PACKAGE
# ================================================================
def pyodide_ho_tro_package(ten_package):
    """Kiểm tra Pyodide có hỗ trợ package không."""
    return ten_package in danh_sach_package_ho_tro()
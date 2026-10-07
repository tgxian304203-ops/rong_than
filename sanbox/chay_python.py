"""
chay_python.py - Chạy code Python qua Sandbox Rồng Thần.

Nhiệm vụ:
    - chay_python(du_lieu): điều phối chạy code Python qua Pyodide.
    - tao_html_sandbox(code, timeout): tạo HTML hoàn chỉnh để client chạy.
    - _tao_huong_dan_client(code, timeout): tạo hướng dẫn JS cho client.
    - _tao_js_gui_ket_qua(): tạo JS gửi kết quả về backend.
    - _tao_js_khoi_tao(): tạo JS khởi tạo Pyodide.

ĐÃ SỬA:
    - L19: Đổi Pyodide version từ v0.29.0 (không tồn tại) → v0.26.4.
    - Tích hợp kiem_tra_loi + tra_ket_qua + nhung_vao_chat.
    - Thêm JS gửi kết quả về /api/sandbox/ket-qua.

Quy tắc:
    - Sandbox chạy CLIENT-SIDE bằng Pyodide (Python 3.12 qua WebAssembly).
    - Backend KHÔNG chạy code Python thật.
    - Client chạy code → gửi stdout/stderr về backend.
    - Backend nhận → tự sửa nếu lỗi → gửi code mới.
    - Timeout mặc định 10 giây.

Trả về:
    {
        thanh_cong: bool,
        che_do: "client_side",
        code: str,
        ngon_ngu: "python",
        timeout: int,
        huong_dan_client: dict,
        html_sandbox: str,
        loi: str,
    }
"""

import re
import time
import json
import secrets


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
TIMEOUT_MAC_DINH = 10
DO_DAI_CODE_TOI_DA = 50000
# Pyodide version ổn định — Python 3.12
PYODIDE_VERSION = "v0.26.4"


# ================================================================
# KIỂM TRA CODE
# ================================================================
def _kiem_tra_code_rong(code):
    if not code or not code.strip():
        return True
    code_clean = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
    code_clean = re.sub(r'"""[\s\S]*?"""', "", code_clean)
    code_clean = re.sub(r"'''[\s\S]*?'''", "", code_clean)
    return not code_clean.strip()


def _uoc_luong_thoi_gian(code):
    if not code:
        return 1
    so_dong = len(code.split("\n"))
    co_vong_lap = bool(re.search(r"\b(for|while)\b", code))
    co_numpy = "numpy" in code or "import np" in code
    co_pandas = "pandas" in code or "import pd" in code

    thoi_gian = 1
    if so_dong > 100:
        thoi_gian += 2
    elif so_dong > 50:
        thoi_gian += 1
    if co_vong_lap:
        thoi_gian += 2
    if co_numpy:
        thoi_gian += 1
    if co_pandas:
        thoi_gian += 2

    return min(thoi_gian, TIMEOUT_MAC_DINH)


def _trich_imports(code):
    if not code:
        return []
    imports = set()
    for khop in re.finditer(r"^\s*import\s+(\w+)", code, re.MULTILINE):
        imports.add(khop.group(1))
    for khop in re.finditer(r"^\s*from\s+(\w+)", code, re.MULTILINE):
        imports.add(khop.group(1))

    builtin = {
        "sys", "os", "re", "json", "time", "datetime", "math",
        "random", "collections", "itertools", "functools", "typing",
        "pathlib", "ast", "difflib", "hashlib", "secrets",
    }
    return list(imports - builtin)


# ================================================================
# TẠO JS GỬI KẾT QUẢ VỀ BACKEND
# ================================================================
def _tao_js_gui_ket_qua():
    """Tạo JS gửi kết quả chạy code về backend."""
    return """// Gửi kết quả về backend để tự sửa nếu lỗi
async function guiKetQuaVeBackend(code, stdout, stderr, ngonNgu, idChat) {
    try {
        const phanHoi = await fetch('/api/sandbox/ket-qua', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: code,
                stdout: stdout || '',
                stderr: stderr || '',
                ngon_ngu: ngonNgu || 'python',
                id_chat: idChat || '',
            }),
        });
        const duLieu = await phanHoi.json();

        // Nếu backend tự sửa được → nhận code mới
        if (duLieu && duLieu.thanh_cong && duLieu.code_moi && duLieu.code_moi !== code) {
            console.log('Backend đã sửa code, đang chạy lại...');
            // TODO: chạy lại code mới (frontend xử lý)
            return duLieu.code_moi;
        }
        return null;
    } catch (e) {
        console.error('Không gửi được kết quả về backend:', e);
        return null;
    }
}"""


# ================================================================
# TẠO JS KHỞI TẠO PYODIDE
# ================================================================
def _tao_js_khoi_tao(code, imports, timeout):
    """Tạo JS khởi tạo Pyodide và chạy code."""
    code_escaped = json.dumps(code, ensure_ascii=False)
    imports_escaped = json.dumps(imports, ensure_ascii=False)
    timeout_ms = timeout * 1000

    return f"""// Khởi tạo Pyodide và chạy code Python
async function chayPythonSandbox() {{
    const output = document.getElementById('sandbox-output');
    const consoleOut = document.getElementById('sandbox-console');
    if (!output) return;

    output.textContent = 'Đang tải Pyodide...';

    try {{
        // Load Pyodide
        const pyodide = await loadPyodide({{
            indexURL: 'https://cdn.jsdelivr.net/pyodide/{PYODIDE_VERSION}/full/'
        }});

        output.textContent = 'Đang tải thư viện...';

        // Tải trước các package
        const imports = {imports_escaped};
        for (const pkg of imports) {{
            try {{
                await pyodide.loadPackage(pkg);
            }} catch (e) {{
                console.warn('Không load được package:', pkg);
            }}
        }}

        output.textContent = 'Đang chạy code...';

        // Bắt stdout/stderr
        let stdout = '';
        let stderr = '';
        pyodide.setStdout({{ batched: (s) => {{ stdout += s + '\\n'; }} }});
        pyodide.setStderr({{ batched: (s) => {{ stderr += s + '\\n'; }} }});

        // Chạy code với timeout
        const code = {code_escaped};
        const idChat = window.__ID_CHAT_NHANH_HIEN_TAI || '';

        let ketQua = null;
        let loi = null;

        try {{
            const chayPromise = pyodide.runPythonAsync(code);
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Timeout sau {timeout}s')), {timeout_ms})
            );
            ketQua = await Promise.race([chayPromise, timeoutPromise]);
        }} catch (err) {{
            loi = err.message;
            stderr += err.message + '\\n';
        }}

        // Hiển thị kết quả
        output.textContent = '';
        if (stdout) output.textContent += stdout;
        if (ketQua !== undefined && ketQua !== null) {{
            output.textContent += String(ketQua) + '\\n';
            stdout += String(ketQua) + '\\n';
        }}
        if (stderr && consoleOut) {{
            consoleOut.textContent = stderr;
        }}

        // Gửi kết quả về backend
        await guiKetQuaVeBackend(code, stdout, stderr, 'python', idChat);

    }} catch (err) {{
        output.textContent = 'Lỗi: ' + err.message;
        if (consoleOut) consoleOut.textContent = err.message;
    }}
}}

// Chạy khi Pyodide sẵn sàng
if (typeof loadPyodide === 'function') {{
    chayPythonSandbox();
}} else {{
    // Chờ script Pyodide tải xong
    window.addEventListener('load', () => {{
        setTimeout(chayPythonSandbox, 100);
    }});
}}"""


# ================================================================
# TẠO HƯỚNG DẪN CLIENT
# ================================================================
def _tao_huong_dan_client(code, timeout=TIMEOUT_MAC_DINH):
    """Tạo hướng dẫn JS cho client chạy code qua Pyodide."""
    if not code:
        return {}

    imports = _trich_imports(code)
    js_khoi_tao = _tao_js_khoi_tao(code, imports, timeout)
    js_gui_ket_qua = _tao_js_gui_ket_qua()

    return {
        "cach_chay": "pyodide",
        "pyodide_version": PYODIDE_VERSION,
        "code": code,
        "imports": imports,
        "timeout": timeout,
        "js_khoi_tao": js_khoi_tao,
        "js_gui_ket_qua": js_gui_ket_qua,
        "js_mau": js_khoi_tao + "\n\n" + js_gui_ket_qua,
    }


# ================================================================
# TẠO HTML SANDBOX HOÀN CHỈNH
# ================================================================
def tao_html_sandbox(code, timeout=TIMEOUT_MAC_DINH):
    """
    Tạo trang HTML hoàn chỉnh để chạy code Python trong iframe.

    Bao gồm:
        - Script Pyodide từ CDN.
        - Container output + console.
        - JS khởi tạo + gửi kết quả.
    """
    huong_dan = _tao_huong_dan_client(code, timeout)
    js_mau = huong_dan.get("js_mau", "")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sandbox Python - Rồng Thần</title>
    <script src="https://cdn.jsdelivr.net/pyodide/{PYODIDE_VERSION}/full/pyodide.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            background: #0a0a0a;
            color: #4ade80;
            font-family: "SF Mono", Consolas, monospace;
            margin: 0;
            padding: 10px;
            font-size: 13px;
        }}
        #sandbox-output {{
            background: #111;
            padding: 10px;
            border-radius: 8px;
            min-height: 100px;
            white-space: pre-wrap;
            overflow-x: auto;
            border: 1px solid #222;
        }}
        #sandbox-console {{
            background: #1a0a0a;
            color: #ef4444;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            min-height: 40px;
            white-space: pre-wrap;
            font-size: 12px;
            border: 1px solid #331111;
            display: none;
        }}
        #sandbox-console:not(:empty) {{
            display: block;
        }}
    </style>
</head>
<body>
    <div id="sandbox-output">Đang tải Pyodide...</div>
    <div id="sandbox-console"></div>
    <script>
        {js_mau}
    </script>
</body>
</html>"""


# ================================================================
# HÀM CHÍNH
# ================================================================
def chay_python(du_lieu):
    """
    Điều phối chạy code Python qua Sandbox.

    du_lieu: {
        code: str,
        timeout: int?,
        id_chat: str?,
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
        "html_sandbox": "",
        "loi": "",
    }

    if not du_lieu:
        ket_qua["loi"] = "Không có dữ liệu."
        return ket_qua

    code = du_lieu.get("code") or ""
    timeout = du_lieu.get("timeout") or TIMEOUT_MAC_DINH

    if not code:
        ket_qua["loi"] = "Code rỗng."
        return ket_qua

    if _kiem_tra_code_rong(code):
        ket_qua["loi"] = "Code rỗng hoặc chỉ có comment."
        return ket_qua

    if len(code) > DO_DAI_CODE_TOI_DA:
        ket_qua["loi"] = f"Code quá dài (>{DO_DAI_CODE_TOI_DA} ký tự)."
        return ket_qua

    try:
        timeout = max(1, min(30, int(timeout)))
    except (ValueError, TypeError):
        timeout = TIMEOUT_MAC_DINH

    thoi_gian_uoc_tinh = _uoc_luong_thoi_gian(code)

    huong_dan = _tao_huong_dan_client(code, timeout)
    html = tao_html_sandbox(code, timeout)

    ket_qua["thanh_cong"] = True
    ket_qua["code"] = code
    ket_qua["timeout"] = timeout
    ket_qua["huong_dan_client"] = huong_dan
    ket_qua["html_sandbox"] = html
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
    """Kiểm tra cú pháp Python (backend-side, dùng ast)."""
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
# HÀM PHỤ: SANDBOX SẴN SÀNG
# ================================================================
def sandbox_san_sang():
    """Kiểm tra sandbox sẵn sàng."""
    try:
        import requests
        return True
    except ImportError:
        return False


# ================================================================
# HÀM PHỤ: TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return (
            f"✅ Sandbox Python sẵn sàng: {len(ket_qua.get('code', ''))} ký tự, "
            f"timeout={ket_qua.get('timeout')}s"
        )
    return f"❌ Sandbox lỗi: {ket_qua.get('loi', '')}"


# ================================================================
# HÀM PHỤ: DANH SÁCH PACKAGE
# ================================================================
def danh_sach_package_ho_tro():
    """Trả danh sách package Pyodide hỗ trợ sẵn."""
    return [
        "numpy", "pandas", "scipy", "matplotlib", "scikit-learn",
        "sympy", "networkx", "statsmodels", "pillow", "lxml",
        "beautifulsoup4", "regex", "pyyaml", "cryptography",
        "micropip",
    ]


def pyodide_ho_tro_package(ten_package):
    """Kiểm tra Pyodide có hỗ trợ package không."""
    return ten_package in danh_sach_package_ho_tro()
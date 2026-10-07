"""
chay_html.py - Chạy code HTML qua Sandbox Rồng Thần.

Nhiệm vụ:
    - chay_html(du_lieu): điều phối chạy code HTML/CSS/JS qua LiveCodes.
    - tao_html_sandbox(code, timeout): tạo HTML hoàn chỉnh để client chạy.
    - _tao_js_khoi_tao(container_id, config, timeout): JS khởi tạo playground.
    - _tao_js_gui_ket_qua(): JS gửi kết quả về backend.
    - _tach_code_html(code): tách HTML/CSS/JS.

ĐÃ SỬA:
    - L20: Sửa API LiveCodes — dùng ES module import thay vì window.livecodes.
    - Đổi version LiveCodes sang 0.14.1 (ổn định).
    - Tích hợp JS gửi kết quả về /api/sandbox/ket-qua.

Quy tắc:
    - Sandbox chạy CLIENT-SIDE bằng LiveCodes SDK.
    - Backend KHÔNG chạy code HTML thật.
    - Client chạy code → gửi stdout/stderr về backend.
    - Backend nhận → tự sửa nếu lỗi → gửi code mới.

Trả về:
    {
        thanh_cong: bool,
        che_do: "client_side",
        code: str,
        ngon_ngu: "html",
        timeout: int,
        huong_dan_client: dict,
        html_sandbox: str,
        loi: str,
    }
"""

import re
import time
import json


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
DO_DAI_CODE_TOI_DA = 100000
LIVECODES_VERSION = "0.14.1"


# ================================================================
# KIỂM TRA CODE
# ================================================================
def _kiem_tra_code_rong(code):
    if not code or not code.strip():
        return True
    code_clean = re.sub(r"<!--[\s\S]*?-->", "", code)
    code_clean = re.sub(r"/\*[\s\S]*?\*/", "", code_clean)
    code_clean = re.sub(r"//[^\n]*", "", code_clean)
    return not code_clean.strip()


def _uoc_luong_thoi_gian(code):
    if not code:
        return 1
    so_dong = len(code.split("\n"))
    co_js = "<script" in code.lower() or "function" in code.lower()
    co_vong_lap = bool(re.search(r"\b(for|while)\b", code))

    thoi_gian = 1
    if so_dong > 100:
        thoi_gian += 2
    elif so_dong > 50:
        thoi_gian += 1
    if co_js:
        thoi_gian += 1
    if co_vong_lap:
        thoi_gian += 1

    return min(thoi_gian, TIMEOUT_MAC_DINH)


# ================================================================
# TÁCH CODE HTML
# ================================================================
def _tach_code_html(code):
    """Tách code HTML thành markup, style, script."""
    ket_qua = {"markup": "", "style": "", "script": ""}

    if not code:
        return ket_qua

    # Tách <style>
    khop_style = re.findall(r"<style[^>]*>([\s\S]*?)</style>", code, re.I)
    if khop_style:
        ket_qua["style"] = "\n".join(khop_style).strip()

    # Tách <script>
    khop_script = re.findall(r"<script[^>]*>([\s\S]*?)</script>", code, re.I)
    if khop_script:
        ket_qua["script"] = "\n".join(khop_script).strip()

    # HTML còn lại
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
# TẠO JS GỬI KẾT QUẢ VỀ BACKEND
# ================================================================
def _tao_js_gui_ket_qua(container_id):
    """Tạo JS gửi kết quả chạy về backend."""
    return f"""// Gửi kết quả về backend để tự sửa nếu lỗi
async function guiKetQuaVeBackend_{container_id}(code, stdout, stderr) {{
    try {{
        const phanHoi = await fetch('/api/sandbox/ket-qua', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                code: code,
                stdout: stdout || '',
                stderr: stderr || '',
                ngon_ngu: 'html',
                id_chat: window.__ID_CHAT_NHANH_HIEN_TAI || '',
            }}),
        }});
        const duLieu = await phanHoi.json();

        if (duLieu && duLieu.thanh_cong && duLieu.code_moi && duLieu.code_moi !== code) {{
            console.log('Backend đã sửa code HTML, cần chạy lại.');
            return duLieu.code_moi;
        }}
        return null;
    }} catch (e) {{
        console.error('Không gửi được kết quả về backend:', e);
        return null;
    }}
}}"""


# ================================================================
# TẠO JS KHỞI TẠO PLAYGROUND
# ================================================================
def _tao_js_khoi_tao(container_id, config, timeout):
    """Tạo JS khởi tạo LiveCodes playground đúng API."""
    config_json = json.dumps(config, ensure_ascii=False)
    timeout_ms = timeout * 1000

    return f"""// Khởi tạo LiveCodes playground
const container_{container_id} = document.getElementById('{container_id}');
if (container_{container_id}) {{
    (async () => {{
        try {{
            // Import ES module — đúng API LiveCodes
            const {{ createPlayground }} = await import(
                'https://cdn.jsdelivr.net/npm/livecodes@{LIVECODES_VERSION}/esm/index.js'
            );

            // Tạo playground
            const playground = await createPlayground(container_{container_id}, {{
                config: {config_json},
                headless: false,
                view: 'result',
            }});

            // Lưu toàn cục
            window['__playground_{container_id}'] = playground;

            // Bắt console
            let stdout = '';
            let stderr = '';
            playground.watch('console', ({{ method, args }}) => {{
                const dong = (args || []).map(a => String(a)).join(' ') + '\\n';
                if (method === 'error' || method === 'warn') {{
                    stderr += dong;
                }} else {{
                    stdout += dong;
                }}

                const out = document.getElementById('{container_id}-console');
                if (out) {{
                    out.textContent += `[${{method}}] ${{dong}}`;
                }}
            }});

            // Chạy
            await playground.run();

            // Chờ 1s cho code chạy xong
            await new Promise(r => setTimeout(r, 1000));

            // Lấy kết quả
            const codeObj = await playground.getCode();
            const codeHienTai = codeObj.markup || '';

            // Gửi kết quả về backend
            await guiKetQuaVeBackend_{container_id}(codeHienTai, stdout, stderr);

            // Timeout cảnh báo
            setTimeout(() => {{
                console.warn('Sandbox chạy quá {timeout}s.');
            }}, {timeout_ms});

        }} catch (err) {{
            const container = document.getElementById('{container_id}');
            if (container) {{
                container.textContent = 'Lỗi khởi tạo sandbox: ' + err.message;
            }}
            console.error('LiveCodes lỗi:', err);
        }}
    }})();
}}"""


# ================================================================
# TẠO HƯỚNG DẪN CLIENT
# ================================================================
def _tao_huong_dan_client(code, timeout=TIMEOUT_MAC_DINH, container_id=""):
    """Tạo hướng dẫn JS cho client chạy HTML qua LiveCodes SDK."""
    phan = _tach_code_html(code)

    if not container_id:
        import secrets
        container_id = "sandbox_" + secrets.token_hex(6)

    config = {}
    if phan.get("markup"):
        config["markup"] = {"language": "html", "content": phan["markup"]}
    if phan.get("style"):
        config["style"] = {"language": "css", "content": phan["style"]}
    if phan.get("script"):
        config["script"] = {"language": "javascript", "content": phan["script"]}

    js_khoi_tao = _tao_js_khoi_tao(container_id, config, timeout)
    js_gui_ket_qua = _tao_js_gui_ket_qua(container_id)

    return {
        "cach_chay": "livecodes",
        "livecodes_version": LIVECODES_VERSION,
        "code": code,
        "phan": phan,
        "timeout": timeout,
        "container_id": container_id,
        "js_khoi_tao": js_khoi_tao,
        "js_gui_ket_qua": js_gui_ket_qua,
        "js_mau": js_khoi_tao + "\n\n" + js_gui_ket_qua,
    }


# ================================================================
# TẠO HTML SANDBOX HOÀN CHỈNH
# ================================================================
def tao_html_sandbox(code, timeout=TIMEOUT_MAC_DINH):
    """Tạo HTML hoàn chỉnh để chạy code HTML/CSS/JS trong iframe."""
    import secrets
    container_id = "sandbox_" + secrets.token_hex(6)

    huong_dan = _tao_huong_dan_client(code, timeout, container_id)
    js_mau = huong_dan.get("js_mau", "")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sandbox HTML - Rồng Thần</title>
    <style>
        * {{ box-sizing: border-box; }}
        html, body {{
            margin: 0;
            padding: 0;
            background: #000;
            color: #4ade80;
            font-family: -apple-system, monospace;
        }}
        #{container_id} {{
            width: 100%;
            min-height: 400px;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
        }}
        #{container_id}-console {{
            background: #0a0a0a;
            color: #facc15;
            padding: 10px;
            margin-top: 8px;
            border-radius: 8px;
            font-family: "SF Mono", Consolas, monospace;
            font-size: 12px;
            min-height: 40px;
            white-space: pre-wrap;
            border: 1px solid #222;
        }}
    </style>
</head>
<body>
    <div id="{container_id}"></div>
    <div id="{container_id}-console"></div>
    <script type="module">
        {js_mau}
    </script>
</body>
</html>"""


# ================================================================
# HÀM CHÍNH
# ================================================================
def chay_html(du_lieu):
    """Điều phối chạy code HTML/CSS/JS qua Sandbox."""
    ket_qua = {
        "thanh_cong": False,
        "che_do": "client_side",
        "code": "",
        "ngon_ngu": "html",
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

    huong_dan = _tao_huong_dan_client(code, timeout)
    html = tao_html_sandbox(code, timeout)

    ket_qua["thanh_cong"] = True
    ket_qua["code"] = code
    ket_qua["timeout"] = timeout
    ket_qua["huong_dan_client"] = huong_dan
    ket_qua["html_sandbox"] = html
    ket_qua["thoi_gian_uoc_tinh"] = _uoc_luong_thoi_gian(code)

    _ghi_log(
        "sandbox",
        f"Chuẩn bị chạy HTML: {len(code)} ký tự, timeout={timeout}s",
    )

    return ket_qua


# ================================================================
# HÀM PHỤ: KIỂM TRA CÚ PHÁP HTML
# ================================================================
def kiem_tra_cu_phap_html(code):
    """Kiểm tra cú pháp HTML cơ bản."""
    if not code:
        return False, "Code rỗng."

    the_can_kiem_tra = ["div", "span", "p", "a", "ul", "li", "table", "tr", "td"]
    for the in the_can_kiem_tra:
        so_mo = len(re.findall(rf"<{the}\b[^>]*>", code, re.I))
        so_dong = len(re.findall(rf"</{the}>", code, re.I))
        if so_mo != so_dong:
            return False, f"Thẻ <{the}> không cân bằng ({so_mo} mở, {so_dong} đóng)."
    return True, ""


def sandbox_san_sang():
    """Kiểm tra sandbox sẵn sàng."""
    try:
        import requests
        return True
    except ImportError:
        return False


def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return (
            f"✅ Sandbox HTML sẵn sàng: {len(ket_qua.get('code', ''))} ký tự, "
            f"timeout={ket_qua.get('timeout')}s"
        )
    return f"❌ Sandbox HTML lỗi: {ket_qua.get('loi', '')}"
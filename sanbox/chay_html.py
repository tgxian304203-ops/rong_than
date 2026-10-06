"""
chay_html.py - Chạy code HTML qua Sandbox Rồng Thần.

Nhiệm vụ:
    - chay_html(du_lieu): điều phối chạy code HTML/CSS/JS qua LiveCodes.
    - _chuan_bi_du_lieu(code, timeout): chuẩn bị dữ liệu cho client.
    - _tao_huong_dan_client(code, timeout): tạo hướng dẫn JS cho client.
    - _tach_code_html(code): tách HTML/CSS/JS từ code tổng hợp.
    - _tao_html_mau(code): tạo HTML mẫu nếu thiếu.

Quy tắc:
    - Sandbox chạy CLIENT-SIDE bằng LiveCodes SDK.
    - Backend KHÔNG chạy code HTML thật.
    - LiveCodes chạy trong trình duyệt, hỗ trợ 90+ ngôn ngữ.
    - Code HTML/CSS/JS được tách riêng cho từng editor.
    - Kết quả hiển thị trong iframe cách ly.
    - Timeout mặc định 10 giây.

Trả về:
    {
        thanh_cong: bool,
        che_do: "client_side",
        code: str,
        ngon_ngu: "html",
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
TIMEOUT_MAC_DINH = 10
DO_DAI_CODE_TOI_DA = 100000
LIVECODES_VERSION = "0.14.1"


# ================================================================
# KIỂM TRA CODE
# ================================================================
def _kiem_tra_code_rong(code):
    """Kiểm tra code rỗng hoặc chỉ có comment/khoảng trắng."""
    if not code or not code.strip():
        return True

    # Bỏ comment HTML
    code_clean = re.sub(r"<!--[\s\S]*?-->", "", code)
    # Bỏ comment CSS/JS
    code_clean = re.sub(r"/\*[\s\S]*?\*/", "", code_clean)
    code_clean = re.sub(r"//[^\n]*", "", code_clean)

    return not code_clean.strip()


def _uoc_luong_thoi_gian(code):
    """Ước lượng thời gian chạy dựa trên code."""
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
# TÁCH CODE HTML/CSS/JS
# ================================================================
def _tach_code_html(code):
    """
    Tách code HTML thành 3 phần: HTML, CSS, JS.

    Trả về: dict { markup, style, script }.
    """
    ket_qua = {
        "markup": "",
        "style": "",
        "script": "",
    }

    if not code:
        return ket_qua

    # 1. Tách <style>...</style>
    khop_style = re.findall(r"<style[^>]*>([\s\S]*?)</style>", code, re.I)
    if khop_style:
        ket_qua["style"] = "\n".join(khop_style).strip()

    # 2. Tách <script>...</script>
    khop_script = re.findall(r"<script[^>]*>([\s\S]*?)</script>", code, re.I)
    if khop_script:
        ket_qua["script"] = "\n".join(khop_script).strip()

    # 3. Phần HTML còn lại (bỏ style + script)
    html_con_lai = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", code, flags=re.I)
    html_con_lai = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", html_con_lai, flags=re.I)
    html_con_lai = html_con_lai.strip()

    # 4. Nếu HTML còn lại có <html>, <body>, <div>... → giữ
    if html_con_lai:
        ket_qua["markup"] = html_con_lai
    else:
        # Không có HTML → tạo HTML mẫu
        ket_qua["markup"] = _tao_html_mau(code)

    return ket_qua


def _tao_html_mau(code):
    """Tạo HTML mẫu nếu user chỉ cung cấp CSS hoặc JS."""
    # Nếu chỉ có CSS
    if not re.search(r"<[a-zA-Z]", code) and "{" in code:
        return "<div class=\"container\">Hello World</div>"

    # Nếu chỉ có JS
    if re.search(r"\b(console\.log|function|const|let|var)\b", code):
        return "<div id=\"app\">Hello World</div>"

    # Mặc định
    return "<h1>Hello Rồng Thần 🐉</h1>"


# ================================================================
# TẠO HƯỚNG DẪN CHO CLIENT
# ================================================================
def _tao_huong_dan_client(code, timeout=TIMEOUT_MAC_DINH):
    """
    Tạo hướng dẫn JS cho client chạy code HTML qua LiveCodes SDK.

    Trả về dict hướng dẫn.
    """
    # Tách code
    phan = _tach_code_html(code)

    # Tạo mã JS mẫu cho client
    js_mau = _tao_js_mau(phan, timeout)

    return {
        "cach_chay": "livecodes",
        "livecodes_version": LIVECODES_VERSION,
        "code": code,
        "phan": phan,
        "timeout": timeout,
        "js_mau": js_mau,
    }


def _tao_js_mau(phan, timeout):
    """Tạo mã JS mẫu để client chạy code qua LiveCodes SDK."""
    import json

    markup = json.dumps(phan.get("markup", ""))
    style = json.dumps(phan.get("style", ""))
    script = json.dumps(phan.get("script", ""))
    timeout_ms = timeout * 1000

    js = f"""// Chạy code HTML/CSS/JS qua LiveCodes SDK
async function chayHtml() {{
    const container = document.getElementById('sandbox-output');
    if (!container) return;

    // Xóa playground cũ nếu có
    if (window.__livecodes_playground) {{
        try {{
            await window.__livecodes_playground.destroy();
        }} catch (e) {{}}
        window.__livecodes_playground = null;
    }}

    // Tạo playground mới
    const {{ createPlayground }} = window.livecodes || {{}};
    if (!createPlayground) {{
        container.textContent = 'Lỗi: LiveCodes chưa tải xong.';
        return;
    }}

    try {{
        const playground = await createPlayground(container, {{
            config: {{
                markup: {{ language: 'html', content: {markup} }},
                style: {{ language: 'css', content: {style} }},
                script: {{ language: 'javascript', content: {script} }},
            }},
            headless: false,
            view: 'result',
        }});

        window.__livecodes_playground = playground;

        // Chạy
        await playground.run();

        // Theo dõi console
        playground.watch('console', (data) => {{
            const out = document.getElementById('sandbox-console');
            if (out) {{
                out.textContent += `[${{data.method}}] ${{data.args.join(' ')}}\\n`;
            }}
        }});

        // Timeout cảnh báo
        setTimeout(() => {{
            console.warn('Sandbox chạy quá {timeout}s.');
        }}, {timeout_ms});
    }} catch (err) {{
        container.textContent = 'Lỗi: ' + err.message;
    }}
}}

// Chờ LiveCodes tải xong
if (window.livecodes) {{
    chayHtml();
}} else {{
    window.addEventListener('load', chayHtml);
}}"""

    return js


# ================================================================
# HÀM CHÍNH
# ================================================================
def chay_html(du_lieu):
    """
    Điều phối chạy code HTML/CSS/JS qua Sandbox.

    du_lieu: {
        code: str,          # Code HTML/CSS/JS cần chạy
        timeout: int?,      # Timeout (giây)
    }

    Trả về dict đầy đủ.
    """
    ket_qua = {
        "thanh_cong": False,
        "che_do": "client_side",
        "code": "",
        "ngon_ngu": "html",
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

    # Tạo hướng dẫn
    huong_dan = _tao_huong_dan_client(code, timeout)

    ket_qua["thanh_cong"] = True
    ket_qua["code"] = code
    ket_qua["timeout"] = timeout
    ket_qua["huong_dan_client"] = huong_dan
    ket_qua["thoi_gian_uoc_tinh"] = _uoc_luong_thoi_gian(code)

    _ghi_log(
        "sandbox",
        f"Chuẩn bị chạy HTML: {len(code)} ký tự, timeout={timeout}s",
    )

    return ket_qua


# ================================================================
# HÀM PHỤ: TẠO HTML SANDBOX HOÀN CHỈNH
# ================================================================
def tao_html_sandbox(code, timeout=TIMEOUT_MAC_DINH):
    """
    Tạo trang HTML hoàn chỉnh để chạy code trong iframe.
    Dùng khi cần hiển thị sandbox độc lập.
    """
    huong_dan = _tao_huong_dan_client(code, timeout)
    js_mau = huong_dan.get("js_mau", "")
    phan = huong_dan.get("phan", {})

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sandbox HTML - Rồng Thần</title>
    <script src="https://cdn.jsdelivr.net/npm/livecodes@{LIVECODES_VERSION}"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            background: #000;
            color: #4ade80;
            font-family: -apple-system, monospace;
            margin: 0;
            padding: 10px;
        }}
        #sandbox-output {{
            background: #111;
            border-radius: 8px;
            min-height: 300px;
            border: 1px solid #333;
        }}
        #sandbox-console {{
            background: #0a0a0a;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            font-family: monospace;
            font-size: 12px;
            color: #facc15;
            min-height: 60px;
            white-space: pre-wrap;
            border: 1px solid #333;
        }}
    </style>
</head>
<body>
    <div id="sandbox-output">Đang tải LiveCodes...</div>
    <div id="sandbox-console"></div>
    <script>
        {js_mau}
    </script>
</body>
</html>"""


# ================================================================
# HÀM PHỤ: KIỂM TRA CÚ PHÁP HTML CƠ BẢN
# ================================================================
def kiem_tra_cu_phap_html(code):
    """
    Kiểm tra cú pháp HTML cơ bản (backend-side).
    Chỉ kiểm tra cân bằng thẻ cơ bản.
    """
    if not code:
        return False, "Code rỗng."

    # Đếm thẻ mở/đóng cho các thẻ phổ biến
    the_can_kiem_tra = ["div", "span", "p", "a", "ul", "li", "table", "tr", "td"]

    for the in the_can_kiem_tra:
        so_mo = len(re.findall(rf"<{the}\b[^>]*>", code, re.I))
        so_dong = len(re.findall(rf"</{the}>", code, re.I))
        if so_mo != so_dong:
            return False, f"Thẻ <{the}> không cân bằng ({so_mo} mở, {so_dong} đóng)."

    return True, ""


# ================================================================
# HÀM PHỤ: KIỂM TRA SANDBOX SẴN SÀNG
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
    """Tạo chuỗi tóm tắt kết quả."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return (
            f"✅ Sandbox HTML sẵn sàng: {len(ket_qua.get('code', ''))} ký tự, "
            f"timeout={ket_qua.get('timeout')}s"
        )

    return f"❌ Sandbox HTML lỗi: {ket_qua.get('loi', '')}"


# ================================================================
# HÀM PHỤ: DANH SÁCH TEMPLATE
# ================================================================
def danh_sach_template():
    """Trả danh sách template LiveCodes hỗ trợ."""
    return [
        "blank", "html", "react", "vue", "svelte", "solid",
        "typescript", "python", "go", "ruby", "php", "cpp",
        "markdown", "mdx", "astro", "tailwind",
    ]
"""
nhung_vao_chat.py - Nhúng LiveCodes vào chat Rồng Thần.

Nhiệm vụ:
    - nhung_vao_chat(du_lieu): tạo mã nhúng LiveCodes vào chat.
    - _tao_container(id_container): tạo thẻ div container.
    - _tao_script_khoi_tao(container_id, config): tạo script khởi tạo playground.
    - _tao_script_hien_thi_ket_qua(): tạo script hiển thị kết quả.
    - _tao_css_sandbox(): tạo CSS cho sandbox trong chat.
    - tao_html_day_du(du_lieu): tạo HTML hoàn chỉnh (container + script + css).

Quy tắc (theo LiveCodes SDK):
    - Dùng createPlayground(container, options) [citation:1][citation:8].
    - Container là thẻ div trong chat.
    - Config chứa markup, style, script [citation:2].
    - Dùng getCode() lấy result HTML [citation:3][citation:14].
    - Dùng watch('console') bắt output [citation:9][citation:14].
    - Dùng watch('tests') bắt test [citation:9][citation:10].
    - Dùng show() chuyển panel [citation:14][citation:15].
    - Dùng destroy() dọn khi cần [citation:12][citation:17].

Trả về:
    {
        thanh_cong: bool,
        html: str,           # HTML nhúng đầy đủ
        container_id: str,   # ID của container
        js_khoi_tao: str,    # JS khởi tạo playground
        js_hien_thi: str,    # JS hiển thị kết quả
        css: str,            # CSS cho sandbox
        loi: str,
    }

Tầng dữ liệu: Không.
"""

import re
import time
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
LIVECODES_CDN = "https://cdn.jsdelivr.net/npm/livecodes@0.14.1"
TIMEOUT_MAC_DINH = 10


# ================================================================
# TẠO CONTAINER
# ================================================================
def _tao_container(id_container, chieu_cao=400):
    """
    Tạo thẻ div container cho LiveCodes.

    id_container: ID duy nhất cho container.
    chieu_cao: chiều cao tối thiểu (px).
    """
    return f"""<div id="{id_container}" class="sandbox-container" style="min-height: {chieu_cao}px;"></div>"""


# ================================================================
# TẠO SCRIPT KHỞI TẠO
# ================================================================
def _tao_script_khoi_tao(container_id, config=None, headless=False, view="result"):
    """
    Tạo script khởi tạo playground.

    container_id: ID container.
    config: dict { markup: {language, content}, style: {...}, script: {...} }.
    headless: chạy không hiển thị output.
    view: "result" | "editor" | "console".
    """
    import json

    config = config or {}
    config_json = json.dumps(config, ensure_ascii=False)

    return f"""// Khởi tạo LiveCodes playground
const container = document.getElementById('{container_id}');
if (!container) {{
    console.error('Không tìm thấy container: {container_id}');
}} else {{
    (async () => {{
        try {{
            // Import SDK từ CDN
            const {{ createPlayground }} = await import('{LIVECODES_CDN}');

            // Tạo playground
            const playground = await createPlayground(container, {{
                config: {config_json},
                headless: {str(headless).lower()},
                view: '{view}',
            }});

            // Lưu vào biến toàn cục để có thể truy cập sau
            window['__playground_{container_id}'] = playground;

            // Đăng ký watcher console
            playground.watch('console', ({{ method, args }}) => {{
                const out = document.getElementById('{container_id}-console');
                if (out) {{
                    out.textContent += `[${{method}}] ${{args.join(' ')}}\\n`;
                }}
            }});

            // Đăng ký watcher tests
            playground.watch('tests', ({{ results, error }}) => {{
                const out = document.getElementById('{container_id}-tests');
                if (out && results) {{
                    out.textContent = results.map(r =>
                        `[${{r.status}}] ${{r.testPath.join(' > ')}}`
                    ).join('\\n');
                }}
            }});

            // Chạy playground
            await playground.run();

            console.log('Playground {container_id} đã sẵn sàng.');
        }} catch (err) {{
            console.error('Lỗi khởi tạo playground:', err);
            container.textContent = 'Lỗi khởi tạo sandbox: ' + err.message;
        }}
    }})();
}}"""


# ================================================================
# TẠO SCRIPT HIỂN THỊ KẾT QUẢ
# ================================================================
def _tao_script_hien_thi_ket_qua(container_id):
    """
    Tạo script hiển thị kết quả (stdout, stderr, result HTML).

    Cần 3 thẻ: {container_id}-stdout, {container_id}-stderr, {container_id}-result.
    """
    return f"""// Hiển thị kết quả
async function hienThiKetQua_{container_id}() {{
    const playground = window['__playground_{container_id}'];
    if (!playground) {{
        console.warn('Playground chưa sẵn sàng.');
        return;
    }}

    try {{
        // Lấy code + result HTML
        const code = await playground.getCode();

        // Hiển thị result HTML trong iframe
        const resultFrame = document.getElementById('{container_id}-result');
        if (resultFrame && code.result) {{
            resultFrame.srcdoc = code.result;
        }}

        // Chuyển sang panel console nếu cần
        await playground.show('console');
    }} catch (err) {{
        console.error('Lỗi lấy kết quả:', err);
    }}
}}"""


# ================================================================
# TẠO CSS SANDBOX
# ================================================================
def _tao_css_sandbox():
    """Tạo CSS cho sandbox trong chat."""
    return """/* CSS cho Sandbox trong chat Rồng Thần */
.sandbox-container {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 10px;
    margin: 10px 0;
    overflow: hidden;
}

.sandbox-container iframe {
    width: 100%;
    min-height: 300px;
    border: none;
    border-radius: 8px;
    background: #fff;
}

.sandbox-console,
.sandbox-stderr,
.sandbox-tests {
    background: rgba(0, 0, 0, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px 10px;
    margin-top: 8px;
    font-family: "SF Mono", Consolas, monospace;
    font-size: 12px;
    line-height: 1.4;
    color: #4ade80;
    max-height: 150px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.sandbox-stderr {
    color: #ef4444;
}

.sandbox-tests {
    color: #facc15;
}"""


# ================================================================
# HÀM CHÍNH
# ================================================================
def nhung_vao_chat(du_lieu):
    """
    Tạo mã nhúng LiveCodes vào chat.

    du_lieu: {
        code: str,              # Code HTML/CSS/JS hoặc Python
        ngon_ngu: str,          # "html" | "python" | "javascript"
        timeout: int?,          # Timeout (giây)
        headless: bool?,        # Chạy ẩn hay không
        view: str?,             # "result" | "editor" | "console"
    }

    Trả về dict đầy đủ.
    """
    ket_qua = {
        "thanh_cong": False,
        "html": "",
        "container_id": "",
        "js_khoi_tao": "",
        "js_hien_thi": "",
        "css": "",
        "loi": "",
    }

    if not du_lieu:
        ket_qua["loi"] = "Không có dữ liệu."
        return ket_qua

    code = du_lieu.get("code") or ""
    ngon_ngu = (du_lieu.get("ngon_ngu") or "html").lower()
    headless = du_lieu.get("headless", False)
    view = du_lieu.get("view", "result")

    if not code:
        ket_qua["loi"] = "Code rỗng."
        return ket_qua

    # Tạo ID container duy nhất
    container_id = "sandbox_" + secrets.token_hex(6)

    # Tạo config cho LiveCodes
    config = _tao_config(code, ngon_ngu)

    # Tạo các phần
    container = _tao_container(container_id, chieu_cao=400)
    js_khoi_tao = _tao_script_khoi_tao(container_id, config, headless, view)
    js_hien_thi = _tao_script_hien_thi_ket_qua(container_id)
    css = _tao_css_sandbox()

    # Tạo HTML đầy đủ
    html_day_du = tao_html_day_du({
        "container_id": container_id,
        "config": config,
        "headless": headless,
        "view": view,
    })

    ket_qua.update({
        "thanh_cong": True,
        "html": html_day_du,
        "container_id": container_id,
        "js_khoi_tao": js_khoi_tao,
        "js_hien_thi": js_hien_thi,
        "css": css,
    })

    _ghi_log(
        "sandbox",
        f"Nhúng LiveCodes vào chat: container={container_id}, "
        f"ngon_ngu={ngon_ngu}",
    )

    return ket_qua


# ================================================================
# TẠO CONFIG CHO LIVECODES
# ================================================================
def _tao_config(code, ngon_ngu):
    """
    Tạo config object cho LiveCodes từ code + ngôn ngữ.

    Trả về: dict { markup, style, script }.
    """
    config = {}

    if ngon_ngu == "html":
        # Tách HTML/CSS/JS
        phan = _tach_html(code)
        config["markup"] = {"language": "html", "content": phan.get("markup", "")}
        if phan.get("style"):
            config["style"] = {"language": "css", "content": phan["style"]}
        if phan.get("script"):
            config["script"] = {"language": "javascript", "content": phan["script"]}

    elif ngon_ngu == "python":
        config["script"] = {"language": "python", "content": code}

    elif ngon_ngu in ("javascript", "js"):
        config["script"] = {"language": "javascript", "content": code}

    elif ngon_ngu == "css":
        config["style"] = {"language": "css", "content": code}

    else:
        # Mặc định: HTML
        config["markup"] = {"language": "html", "content": code}

    return config


def _tach_html(code):
    """Tách HTML thành markup, style, script."""
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
    ket_qua["markup"] = html_con_lai.strip()

    return ket_qua


# ================================================================
# TẠO HTML ĐẦY ĐỦ
# ================================================================
def tao_html_day_du(du_lieu):
    """
    Tạo HTML hoàn chỉnh để nhúng vào chat.

    du_lieu: {
        container_id: str,
        config: dict,
        headless: bool,
        view: str,
    }

    Trả về: chuỗi HTML.
    """
    if not du_lieu:
        return ""

    container_id = du_lieu.get("container_id", "sandbox_" + secrets.token_hex(4))
    config = du_lieu.get("config", {})
    headless = du_lieu.get("headless", False)
    view = du_lieu.get("view", "result")

    js_khoi_tao = _tao_script_khoi_tao(container_id, config, headless, view)
    js_hien_thi = _tao_script_hien_thi_ket_qua(container_id)
    css = _tao_css_sandbox()

    return f"""<style>
{css}
</style>

<div id="{container_id}" class="sandbox-container"></div>

<div id="{container_id}-stdout" class="sandbox-console"></div>
<div id="{container_id}-stderr" class="sandbox-stderr"></div>
<div id="{container_id}-tests" class="sandbox-tests"></div>

<script type="module">
{js_khoi_tao}

// Hiển thị kết quả sau khi chạy
setTimeout(() => {{
    hienThiKetQua_{container_id}();
}}, {TIMEOUT_MAC_DINH * 1000});
</script>"""


# ================================================================
# HÀM PHỤ: TẠO NHANH HTML
# ================================================================
def tao_nhanh_html(code, ngon_ngu="html"):
    """Tạo nhanh HTML nhúng chỉ với code, không cần config."""
    return nhung_vao_chat({"code": code, "ngon_ngu": ngon_ngu})


def tao_nhanh_python(code):
    """Tạo nhanh sandbox Python."""
    return nhung_vao_chat({"code": code, "ngon_ngu": "python"})


# ================================================================
# HÀM PHỤ: TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return f"✅ Sandbox nhúng OK: {ket_qua.get('container_id', '')}"

    return f"❌ Nhúng sandbox lỗi: {ket_qua.get('loi', '')}"


# ================================================================
# HÀM PHỤ: KIỂM TRA CÓ SẴN SÀNG
# ================================================================
def san_sang():
    """Kiểm tra module sẵn sàng."""
    try:
        import requests
        return True
    except ImportError:
        return False


# ================================================================
# HÀM PHỤ: DANH SÁCH NGÔN NGỮ HỖ TRỢ
# ================================================================
def danh_sach_ngon_ngu():
    """Trả danh sách ngôn ngữ LiveCodes hỗ trợ (90+)."""
    return [
        "html", "css", "javascript", "typescript", "jsx", "tsx",
        "python", "ruby", "php", "go", "rust", "cpp", "c", "csharp",
        "java", "kotlin", "swift", "dart", "lua", "perl", "r",
        "sql", "graphql", "markdown", "mdx", "yaml", "json", "toml",
        "vue", "svelte", "react", "solid", "preact", "astro",
        "tailwind", "scss", "less", "stylus",
    ]
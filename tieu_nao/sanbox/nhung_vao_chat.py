"""
nhung_vao_chat.py - Nhúng LiveCodes vào chat Rồng Thần.
"""

import re
import secrets


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


LIVECODES_CDN = "https://cdn.jsdelivr.net/npm/livecodes@0.14.1"
TIMEOUT_MAC_DINH = 10


def _tao_container(id_container, chieu_cao=400):
    return f"""<div id="{id_container}" class="sandbox-container" style="min-height: {chieu_cao}px;"></div>"""


def _tao_script_khoi_tao(container_id, config=None, headless=False, view="result"):
    import json

    config = config or {}
    config_json = json.dumps(config, ensure_ascii=False)

    return f"""const container = document.getElementById('{container_id}');
if (!container) {{
    console.error('Không tìm thấy container: {container_id}');
}} else {{
    (async () => {{
        try {{
            const {{ createPlayground }} = await import('{LIVECODES_CDN}');

            const playground = await createPlayground(container, {{
                config: {config_json},
                headless: {str(headless).lower()},
                view: '{view}',
            }});

            window['__playground_{container_id}'] = playground;

            playground.watch('console', ({{ method, args }}) => {{
                const out = document.getElementById('{container_id}-console');
                if (out) {{
                    out.textContent += `[${{method}}] ${{args.join(' ')}}\\n`;
                }}
            }});

            playground.watch('tests', ({{ results, error }}) => {{
                const out = document.getElementById('{container_id}-tests');
                if (out && results) {{
                    out.textContent = results.map(r =>
                        `[${{r.status}}] ${{r.testPath.join(' > ')}}`
                    ).join('\\n');
                }}
            }});

            await playground.run();

            console.log('Playground {container_id} đã sẵn sàng.');
        }} catch (err) {{
            console.error('Lỗi khởi tạo playground:', err);
            container.textContent = 'Lỗi khởi tạo sandbox: ' + err.message;
        }}
    }})();
}}"""


def _tao_script_hien_thi_ket_qua(container_id):
    return f"""async function hienThiKetQua_{container_id}() {{
    const playground = window['__playground_{container_id}'];
    if (!playground) {{
        console.warn('Playground chưa sẵn sàng.');
        return;
    }}

    try {{
        const code = await playground.getCode();

        const resultFrame = document.getElementById('{container_id}-result');
        if (resultFrame && code.result) {{
            resultFrame.srcdoc = code.result;
        }}

        await playground.show('console');
    }} catch (err) {{
        console.error('Lỗi lấy kết quả:', err);
    }}
}}"""


def _tao_css_sandbox():
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


def nhung_vao_chat(du_lieu):
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

    container_id = "sandbox_" + secrets.token_hex(6)
    config = _tao_config(code, ngon_ngu)

    container = _tao_container(container_id, chieu_cao=400)
    js_khoi_tao = _tao_script_khoi_tao(container_id, config, headless, view)
    js_hien_thi = _tao_script_hien_thi_ket_qua(container_id)
    css = _tao_css_sandbox()

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


def _tao_config(code, ngon_ngu):
    config = {}

    if ngon_ngu == "html":
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
        config["markup"] = {"language": "html", "content": code}

    return config


def _tach_html(code):
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
    ket_qua["markup"] = html_con_lai.strip()

    return ket_qua


def tao_html_day_du(du_lieu):
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

setTimeout(() => {{
    hienThiKetQua_{container_id}();
}}, {TIMEOUT_MAC_DINH * 1000});
</script>"""


def tao_nhanh_html(code, ngon_ngu="html"):
    return nhung_vao_chat({"code": code, "ngon_ngu": ngon_ngu})


def tao_nhanh_python(code):
    return nhung_vao_chat({"code": code, "ngon_ngu": "python"})


def tom_tat(ket_qua):
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return f"✅ Sandbox nhúng OK: {ket_qua.get('container_id', '')}"

    return f"❌ Nhúng sandbox lỗi: {ket_qua.get('loi', '')}"


def san_sang():
    try:
        import requests
        return True
    except ImportError:
        return False


def danh_sach_ngon_ngu():
    return [
        "html", "css", "javascript", "typescript", "jsx", "tsx",
        "python", "ruby", "php", "go", "rust", "cpp", "c", "csharp",
        "java", "kotlin", "swift", "dart", "lua", "perl", "r",
        "sql", "graphql", "markdown", "mdx", "yaml", "json", "toml",
        "vue", "svelte", "react", "solid", "preact", "astro",
        "tailwind", "scss", "less", "stylus",
    ]
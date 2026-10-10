"""
tra_ket_qua.py - Trả stdout/stderr từ Sandbox Rồng Thần.
"""

import json
import re


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


DO_DAI_OUTPUT_TOI_DA = 10000


def tra_ket_qua(ket_qua_client):
    ket_qua = {
        "thanh_cong": True,
        "stdout": "",
        "stderr": "",
        "result_html": "",
        "tests": [],
        "so_dong_stdout": 0,
        "so_dong_stderr": 0,
        "loi": "",
    }

    if not ket_qua_client or not isinstance(ket_qua_client, dict):
        ket_qua["loi"] = "Kết quả client rỗng."
        ket_qua["thanh_cong"] = False
        return ket_qua

    if ket_qua_client.get("error"):
        ket_qua["loi"] = str(ket_qua_client["error"])[:500]
        ket_qua["thanh_cong"] = False

    console = ket_qua_client.get("console", [])
    if isinstance(console, list):
        stdout, stderr = _trich_console(console)
        ket_qua["stdout"] = stdout
        ket_qua["stderr"] = stderr
        ket_qua["so_dong_stdout"] = len(stdout.split("\n")) if stdout else 0
        ket_qua["so_dong_stderr"] = len(stderr.split("\n")) if stderr else 0

    tests = ket_qua_client.get("tests")
    if isinstance(tests, dict):
        ket_qua["tests"] = _trich_test_results(tests)

    code = ket_qua_client.get("code")
    if isinstance(code, dict):
        ket_qua["result_html"] = _trich_result_html(code)

    if len(ket_qua["stdout"]) > DO_DAI_OUTPUT_TOI_DA:
        ket_qua["stdout"] = ket_qua["stdout"][:DO_DAI_OUTPUT_TOI_DA] + "..."
    if len(ket_qua["stderr"]) > DO_DAI_OUTPUT_TOI_DA:
        ket_qua["stderr"] = ket_qua["stderr"][:DO_DAI_OUTPUT_TOI_DA] + "..."
    if len(ket_qua["result_html"]) > DO_DAI_OUTPUT_TOI_DA:
        ket_qua["result_html"] = ket_qua["result_html"][:DO_DAI_OUTPUT_TOI_DA] + "..."

    if ket_qua["stderr"]:
        ket_qua["thanh_cong"] = False

    return ket_qua


def _trich_console(console):
    if not console or not isinstance(console, list):
        return "", ""

    stdout_lines = []
    stderr_lines = []

    for item in console:
        if not isinstance(item, dict):
            continue

        method = (item.get("method") or "").lower()
        args = item.get("args", [])

        if isinstance(args, list):
            dong = " ".join(_chuyen_sang_chuoi(a) for a in args)
        else:
            dong = _chuyen_sang_chuoi(args)

        if method in ("error", "warn"):
            stderr_lines.append(f"[{method}] {dong}")
        elif method in ("log", "info", "debug"):
            stdout_lines.append(dong)
        else:
            stdout_lines.append(f"[{method}] {dong}")

    return "\n".join(stdout_lines), "\n".join(stderr_lines)


def _chuyen_sang_chuoi(gia_tri):
    if gia_tri is None:
        return "None"
    if isinstance(gia_tri, (str, int, float, bool)):
        return str(gia_tri)
    if isinstance(gia_tri, (list, dict)):
        try:
            return json.dumps(gia_tri, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(gia_tri)
    return str(gia_tri)


def _trich_test_results(tests):
    if not tests or not isinstance(tests, dict):
        return []

    if tests.get("error"):
        return [{
            "status": "error",
            "testPath": [],
            "errors": [str(tests["error"])[:500]],
        }]

    results = tests.get("results", [])
    if not isinstance(results, list):
        return []

    ket_qua = []
    for r in results:
        if not isinstance(r, dict):
            continue

        ket_qua.append({
            "status": r.get("status", "unknown"),
            "testPath": r.get("testPath", []),
            "errors": r.get("errors", []),
        })

    return ket_qua


def _trich_result_html(code):
    if not code or not isinstance(code, dict):
        return ""

    result = code.get("result", "")
    if result:
        return str(result)

    return ""


def tao_js_lay_ket_qua():
    return """// Lấy kết quả từ LiveCodes SDK
async function layKetQua(playground) {
    const ketQua = {
        console: [],
        tests: null,
        code: null,
        error: null,
    };

    try {
        playground.watch('console', ({ method, args }) => {
            ketQua.console.push({
                method: method,
                args: args,
                thoi_gian: Date.now(),
            });
        });

        playground.watch('tests', ({ results, error }) => {
            ketQua.tests = {
                results: results || [],
                error: error || null,
            };
        });

        await playground.run();
        await new Promise(r => setTimeout(r, 500));
        ketQua.code = await playground.getCode();

        try {
            const testKetQua = await playground.runTests();
            if (testKetQua && testKetQua.results) {
                ketQua.tests = { results: testKetQua.results, error: null };
            }
        } catch (e) {
        }

    } catch (err) {
        ketQua.error = err.message;
    }

    return ketQua;
}"""


def tao_js_hien_thi_ket_qua():
    return """// Hiển thị kết quả lên UI
function hienThiKetQua(ketQua) {
    const out = document.getElementById('sandbox-stdout');
    if (out && ketQua.stdout) {
        out.textContent = ketQua.stdout;
    }

    const err = document.getElementById('sandbox-stderr');
    if (err && ketQua.stderr) {
        err.textContent = ketQua.stderr;
    }

    if (ketQua.result_html) {
        let iframe = document.getElementById('sandbox-result');
        if (!iframe) {
            iframe = document.createElement('iframe');
            iframe.id = 'sandbox-result';
            iframe.style.width = '100%';
            iframe.style.height = '300px';
            iframe.style.border = '1px solid #333';
            iframe.style.borderRadius = '8px';
            document.getElementById('sandbox-output').appendChild(iframe);
        }
        iframe.srcdoc = ketQua.result_html;
    }

    if (ketQua.tests && ketQua.tests.length > 0) {
        const testOut = document.getElementById('sandbox-tests');
        if (testOut) {
            testOut.textContent = ketQua.tests.map(t =>
                `[${t.status}] ${t.testPath.join(' > ')} ${t.errors.length ? '❌' : '✅'}`
            ).join('\\n');
        }
    }
}"""


def tom_tat(ket_qua):
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        so_dong = ket_qua.get("so_dong_stdout", 0)
        return f"✅ Sandbox chạy OK: {so_dong} dòng stdout."

    if ket_qua.get("stderr"):
        return f"❌ Sandbox lỗi: {ket_qua['stderr'][:150]}"

    if ket_qua.get("loi"):
        return f"❌ Sandbox lỗi: {ket_qua['loi'][:150]}"

    return "⚠️ Sandbox không có kết quả."


def co_ket_qua(ket_qua):
    if not ket_qua:
        return False
    return bool(ket_qua.get("stdout") or ket_qua.get("result_html"))


def dem_test(ket_qua):
    ket_qua_dem = {"pass": 0, "fail": 0, "skip": 0, "error": 0, "tong": 0}

    if not ket_qua or not ket_qua.get("tests"):
        return ket_qua_dem

    for t in ket_qua["tests"]:
        status = t.get("status", "unknown")
        if status in ket_qua_dem:
            ket_qua_dem[status] += 1
        ket_qua_dem["tong"] += 1

    return ket_qua_dem


def lay_stderr(ket_qua):
    if not ket_qua:
        return ""
    return ket_qua.get("stderr", "")


def lay_stdout(ket_qua):
    if not ket_qua:
        return ""
    return ket_qua.get("stdout", "")


def lay_result_html(ket_qua):
    if not ket_qua:
        return ""
    return ket_qua.get("result_html", "")
"""
kiem_tra_loi.py - Bắt lỗi, timeout cho Sandbox Rồng Thần.

Sửa: dai_nao.doc_loi → dai_nao.kiem_tra_loi.
"""

import re
import time


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


TIMEOUT_MAC_DINH = 10
SO_LAN_RETRY_COMPILER = 3


def kiem_tra_loi(ket_qua_client):
    ket_qua = {
        "thanh_cong": True,
        "co_loi": False,
        "loai_loi": "",
        "thong_diep": "",
        "dong": None,
        "goi_y": [],
        "js_bo_sung": "",
    }

    if not ket_qua_client or not isinstance(ket_qua_client, dict):
        return ket_qua

    if ket_qua_client.get("error"):
        ket_qua["thanh_cong"] = False
        ket_qua["co_loi"] = True
        ket_qua["thong_diep"] = str(ket_qua_client["error"])[:500]
        ket_qua["loai_loi"] = "runtime"
        ket_qua["goi_y"] = ["Kiểm tra lại code.", "Xem console output."]
        return ket_qua

    console = ket_qua_client.get("console", [])
    if isinstance(console, list):
        for item in console:
            if not isinstance(item, dict):
                continue
            method = (item.get("method") or "").lower()
            if method == "error":
                args = item.get("args", [])
                thong_diep = " ".join(str(a) for a in args)[:500]
                ket_qua["thanh_cong"] = False
                ket_qua["co_loi"] = True
                ket_qua["loai_loi"] = "console"
                ket_qua["thong_diep"] = thong_diep
                dong = _trich_so_dong(thong_diep)
                if dong:
                    ket_qua["dong"] = dong
                ket_qua["goi_y"] = _goi_y_theo_loi(thong_diep)
                return ket_qua

    tests = ket_qua_client.get("tests")
    if isinstance(tests, dict):
        if tests.get("error"):
            ket_qua["thanh_cong"] = False
            ket_qua["co_loi"] = True
            ket_qua["loai_loi"] = "test"
            ket_qua["thong_diep"] = str(tests["error"])[:500]
            return ket_qua

        results = tests.get("results", [])
        if isinstance(results, list):
            for r in results:
                if not isinstance(r, dict):
                    continue
                status = r.get("status", "")
                if status == "fail":
                    ket_qua["thanh_cong"] = False
                    ket_qua["co_loi"] = True
                    ket_qua["loai_loi"] = "test"
                    errors = r.get("errors", [])
                    ket_qua["thong_diep"] = " ".join(str(e) for e in errors)[:500]
                    return ket_qua

    return ket_qua


def phan_tich_loi_sandbox(stderr):
    ket_qua = {
        "loai_loi": "",
        "thong_diep": "",
        "dong": None,
        "goi_y": [],
    }

    if not stderr:
        return ket_qua

    try:
        from dai_nao.kiem_tra_loi import (
            _doan_loai_loi,
            _trich_so_dong as _trich_dong_dai_nao,
            _goi_y_theo_loai,
        )
        ket_qua["loai_loi"] = _doan_loai_loi(stderr)
        ket_qua["thong_diep"] = stderr[:500]
        ket_qua["dong"] = _trich_dong_dai_nao(stderr)
        ket_qua["goi_y"] = _goi_y_theo_loai(ket_qua["loai_loi"])
        return ket_qua
    except ImportError:
        pass
    except Exception:
        pass

    ket_qua["thong_diep"] = stderr[:500]
    ket_qua["dong"] = _trich_so_dong(stderr)
    ket_qua["loai_loi"] = _doan_loai_loi(stderr)
    ket_qua["goi_y"] = _goi_y_theo_loi(stderr)

    return ket_qua


def _doan_loai_loi(stderr):
    if not stderr:
        return "khac"
    t = stderr.lower()
    if "timeout" in t or "timed out" in t:
        return "timeout"
    if "syntaxerror" in t or "syntax error" in t:
        return "syntax"
    if "referenceerror" in t or "nameerror" in t:
        return "reference"
    if "typeerror" in t:
        return "type"
    if "compile" in t or "compilation" in t:
        return "compile"
    return "khac"


def _trich_so_dong(stderr):
    if not stderr:
        return None
    mau = [
        r"line\s+(\d+)",
        r":(\d+):\d+",
        r"at\s+\S+\s+\((\d+):",
    ]
    for m in mau:
        khop = re.search(m, stderr, re.I)
        if khop:
            try:
                return int(khop.group(1))
            except (ValueError, IndexError):
                continue
    return None


def _goi_y_theo_loi(stderr):
    if not stderr:
        return []
    t = stderr.lower()
    if "timeout" in t:
        return ["Tăng timeout.", "Kiểm tra code có vòng lặp vô hạn không."]
    if "syntax" in t:
        return ["Kiểm tra dấu ngoặc, dấu chấm phẩy."]
    if "reference" in t:
        return ["Kiểm tra biến đã khai báo chưa."]
    if "type" in t:
        return ["Kiểm tra kiểu dữ liệu."]
    if "compile" in t:
        return ["Kiểm tra compiler có sẵn không."]
    return ["Xem console để biết chi tiết."]


def _tao_timeout_js(timeout=TIMEOUT_MAC_DINH):
    timeout_ms = timeout * 1000
    return f"""// Timeout cho SDK call
function voiTimeout(promise, ms = {timeout_ms}) {{
    return Promise.race([
        promise,
        new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Timeout sau ' + (ms/1000) + 's')), ms)
        )
    ]);
}}"""


def _tao_watcher_loi_js():
    return """// Bắt console output
let consoleOutput = [];
let consoleErrors = [];

playground.watch('console', ({ method, args }) => {
    const item = { method, args, thoi_gian: Date.now() };
    consoleOutput.push(item);
    if (method === 'error') {
        consoleErrors.push(item);
    }
    const out = document.getElementById('sandbox-console');
    if (out) {
        out.textContent += `[${method}] ${args.join(' ')}\\n`;
    }
});"""


def _tao_watcher_test_js():
    return """// Bắt test results
let testResults = [];

playground.watch('tests', ({ results, error }) => {
    if (error) {
        consoleErrors.push({ method: 'test-error', args: [error] });
        return;
    }
    testResults = results;
    const out = document.getElementById('sandbox-tests');
    if (out) {
        out.textContent = results.map(r =>
            `[${r.status}] ${r.testPath.join(' > ')}`
        ).join('\\n');
    }
});"""


def _tao_retry_js(so_lan=SO_LAN_RETRY_COMPILER):
    return f"""// Retry compile {so_lan} lần nếu lỗi
async function chayVoiRetry(playground, soLan = {so_lan}) {{
    for (let i = 1; i <= soLan; i++) {{
        try {{
            await playground.run();
            return true;
        }} catch (err) {{
            console.warn(`Lần chạy ${{i}} lỗi:`, err.message);
            if (i === soLan) throw err;
            await new Promise(r => setTimeout(r, 500 * i));
        }}
    }}
    return false;
}}"""


def _tao_destroy_js():
    return """// Dọn playground khi thoát
async function donPlayground() {
    if (window.__livecodes_playground) {
        try {
            await window.__livecodes_playground.destroy();
        } catch (e) {
            console.warn('Không dọn được playground:', e);
        }
        window.__livecodes_playground = null;
    }
}

window.addEventListener('beforeunload', donPlayground);"""


def tao_js_bo_sung(timeout=TIMEOUT_MAC_DINH):
    phan = [
        "// === JS bổ sung cho Sandbox Rồng Thần ===",
        "",
        _tao_timeout_js(timeout),
        "",
        _tao_watcher_loi_js(),
        "",
        _tao_watcher_test_js(),
        "",
        _tao_retry_js(),
        "",
        _tao_destroy_js(),
        "",
        "// === Hết JS bổ sung ===",
    ]
    return "\n".join(phan)


def kiem_tra_ket_qua_chay(ket_qua_client):
    kq = kiem_tra_loi(ket_qua_client)
    return kq["thanh_cong"], kq["thong_diep"]


def tom_tat_loi(ket_qua):
    if not ket_qua:
        return ""
    if not ket_qua.get("co_loi"):
        return "✅ Không có lỗi."
    dong = f" (dòng {ket_qua['dong']})" if ket_qua.get("dong") else ""
    return (
        f"❌ [{ket_qua.get('loai_loi', 'khac')}]{dong}: "
        f"{ket_qua.get('thong_diep', '')[:150]}"
    )


def danh_sach_loai_loi():
    return [
        "timeout", "compile", "syntax", "reference",
        "type", "runtime", "console", "test", "khac",
    ]


def la_loi_timeout(thong_diep):
    if not thong_diep:
        return False
    t = thong_diep.lower()
    return "timeout" in t or "timed out" in t


def la_loi_compile(thong_diep):
    if not thong_diep:
        return False
    t = thong_diep.lower()
    return "compile" in t or "compilation" in t or "compiler" in t
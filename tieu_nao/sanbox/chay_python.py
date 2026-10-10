"""
chay_python.py - Chạy code Python qua Sandbox Rồng Thần.
"""

import os
import re
import sys
import time
import tempfile
import subprocess


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


TIMEOUT_MAC_DINH = 5
DO_DAI_CODE_TOI_DA = 50000
DO_DAI_OUTPUT_TOI_DA = 50000

IMPORT_CAM = [
    "os.system",
    "subprocess",
    "shutil.rmtree",
    "shutil.move",
    "pathlib.Path.home",
    "open('/etc",
    'open("/etc',
    "open('/root",
    'open("/root',
]


def _kiem_tra_an_toan(code):
    if not code:
        return False, "Code rỗng."

    code_lower = code.lower()

    for mau in IMPORT_CAM:
        if mau.lower() in code_lower:
            return False, f"Code chứa pattern nguy hiểm: '{mau}'."

    if "os.remove(" in code_lower or "os.rmdir(" in code_lower:
        return False, "Code chứa lệnh xóa file: 'os.remove' / 'os.rmdir'."

    if "os.unlink(" in code_lower:
        return False, "Code chứa lệnh xóa file: 'os.unlink'."

    return True, ""


def chay_python_backend(code, timeout=TIMEOUT_MAC_DINH):
    ket_qua = {
        "thanh_cong": False,
        "stdout": "",
        "stderr": "",
        "returncode": -1,
        "thoi_gian": 0.0,
        "loi": "",
    }

    if not code:
        ket_qua["loi"] = "Code rỗng."
        return ket_qua

    if len(code) > DO_DAI_CODE_TOI_DA:
        ket_qua["loi"] = f"Code quá dài (>{DO_DAI_CODE_TOI_DA} ký tự)."
        return ket_qua

    an_toan, ly_do = _kiem_tra_an_toan(code)
    if not an_toan:
        ket_qua["loi"] = ly_do
        ket_qua["stderr"] = ly_do
        return ket_qua

    try:
        timeout = max(1, min(15, int(timeout)))
    except (ValueError, TypeError):
        timeout = TIMEOUT_MAC_DINH

    thoi_gian_bat_dau = time.time()
    ten_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            ten_file = f.name

        ket_qua_subprocess = subprocess.run(
            [sys.executable, ten_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )

        ket_qua["stdout"] = (ket_qua_subprocess.stdout or "")[:DO_DAI_OUTPUT_TOI_DA]
        ket_qua["stderr"] = (ket_qua_subprocess.stderr or "")[:DO_DAI_OUTPUT_TOI_DA]
        ket_qua["returncode"] = ket_qua_subprocess.returncode
        ket_qua["thanh_cong"] = (ket_qua_subprocess.returncode == 0)

    except subprocess.TimeoutExpired:
        ket_qua["loi"] = f"Code chạy quá {timeout} giây — bị hủy."
        ket_qua["stderr"] = f"Timeout sau {timeout}s."
    except Exception as e:
        ket_qua["loi"] = f"Lỗi chạy code: {e}"
        ket_qua["stderr"] = str(e)
    finally:
        if ten_file and os.path.exists(ten_file):
            try:
                os.unlink(ten_file)
            except Exception:
                pass

    ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)

    _ghi_log(
        "sandbox",
        f"Chạy backend: {len(code)} ký tự, "
        f"returncode={ket_qua['returncode']}, "
        f"tg={ket_qua['thoi_gian']}s",
    )

    return ket_qua


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

    thoi_gian = 1
    if so_dong > 100:
        thoi_gian += 2
    elif so_dong > 50:
        thoi_gian += 1
    if co_vong_lap:
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


def chay_python(du_lieu):
    ket_qua = {
        "thanh_cong": False,
        "che_do": "backend",
        "code": "",
        "ngon_ngu": "python",
        "timeout": TIMEOUT_MAC_DINH,
        "stdout": "",
        "stderr": "",
        "returncode": -1,
        "huong_dan_client": {},
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

    ket_qua_backend = chay_python_backend(code, timeout)

    ket_qua.update({
        "thanh_cong": ket_qua_backend.get("thanh_cong", False),
        "code": code,
        "stdout": ket_qua_backend.get("stdout", ""),
        "stderr": ket_qua_backend.get("stderr", ""),
        "returncode": ket_qua_backend.get("returncode", -1),
        "loi": ket_qua_backend.get("loi", ""),
        "thoi_gian": ket_qua_backend.get("thoi_gian", 0.0),
    })

    return ket_qua


def kiem_tra_cu_phap(code):
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


def sandbox_san_sang():
    return True


def tom_tat(ket_qua):
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        so_dong = len((ket_qua.get("stdout") or "").split("\n"))
        return f"✅ Sandbox chạy OK: {so_dong} dòng stdout."
    return f"❌ Sandbox lỗi: {(ket_qua.get('loi') or ket_qua.get('stderr') or '')[:150]}"


def danh_sach_package_ho_tro():
    return [
        "numpy", "pandas", "scipy", "matplotlib", "scikit-learn",
        "sympy", "networkx", "statsmodels", "pillow", "requests",
    ]


def pyodide_ho_tro_package(ten_package):
    return ten_package in danh_sach_package_ho_tro()
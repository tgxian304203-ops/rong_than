"""
chay_python.py - Chạy code Python qua Sandbox Rồng Thần.

SỬA:
    - Tự cài thư viện khi gặp ModuleNotFoundError.
    - Thêm DEBUG.
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


def _in_debug(noi_dung):
    try:
        print(f"[DEBUG-CHAY-PYTHON] {noi_dung}", flush=True)
    except Exception:
        pass


TIMEOUT_MAC_DINH = 5
DO_DAI_CODE_TOI_DA = 50000
DO_DAI_OUTPUT_TOI_DA = 50000
SO_LAN_CAI_TOI_DA = 3

# Thư viện cấm
IMPORT_CAM = [
    "os.system",
    "shutil.rmtree",
    "shutil.move",
    "pathlib.Path.home",
    "open('/etc",
    'open("/etc',
    "open('/root",
    'open("/root',
]

# Thư viện cho phép tự cài
THU_VIEN_CHO_PHEP = {
    "dotenv": "python-dotenv",
    "flask": "Flask",
    "flask_cors": "flask-cors",
    "flask_jwt_extended": "flask-jwt-extended",
    "jwt": "PyJWT",
    "pymongo": "pymongo",
    "bson": "pymongo",
    "dnspython": "dnspython",
    "requests": "requests",
    "numpy": "numpy",
    "pandas": "pandas",
    "sympy": "sympy",
    "openpyxl": "openpyxl",
    "docx": "python-docx",
    "PyPDF2": "PyPDF2",
    "PIL": "Pillow",
    "yaml": "PyYAML",
    "bcrypt": "bcrypt",
    "dateutil": "python-dateutil",
    "pytz": "pytz",
    "werkzeug": "Werkzeug",
    "jinja2": "Jinja2",
    "markupsafe": "MarkupSafe",
    "itsdangerous": "itsdangerous",
    "click": "click",
    "blinker": "blinker",
}


def _kiem_tra_an_toan(code):
    if not code:
        return False, "Code rỗng."

    code_lower = code.lower()

    for mau in IMPORT_CAM:
        if mau.lower() in code_lower:
            return False, f"Code chứa pattern nguy hiểm: '{mau}'."

    if "os.remove(" in code_lower or "os.rmdir(" in code_lower:
        return False, "Code chứa lệnh xóa file."

    if "os.unlink(" in code_lower:
        return False, "Code chứa lệnh xóa file."

    return True, ""


def _trich_module_thieu(stderr):
    """Trích tên module thiếu từ stderr."""
    if not stderr:
        return None

    mau = r"ModuleNotFoundError: No module named '([^']+)'"
    khop = re.search(mau, stderr)
    if khop:
        return khop.group(1)

    mau = r"ImportError: cannot import name '([^']+)'"
    khop = re.search(mau, stderr)
    if khop:
        return khop.group(1)

    return None


def _cai_thu_vien(ten_module):
    """Cài thư viện bằng pip."""
    if not ten_module:
        return False

    ten_goc = ten_module.split(".")[0]

    if ten_goc not in THU_VIEN_CHO_PHEP:
        _in_debug(f"Thư viện '{ten_goc}' không được phép cài.")
        return False

    ten_pip = THU_VIEN_CHO_PHEP[ten_goc]

    _in_debug(f"Đang cài '{ten_pip}'...")

    try:
        ket_qua = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", ten_pip],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if ket_qua.returncode == 0:
            _in_debug(f"✅ Cài '{ten_pip}' thành công.")
            return True
        _in_debug(f"❌ Cài '{ten_pip}' lỗi: {ket_qua.stderr[:200]}")
        return False
    except Exception as e:
        _in_debug(f"❌ Cài '{ten_pip}' exception: {e}")
        return False


def _chay_mot_lan(code, timeout):
    """Chạy code 1 lần."""
    ten_file = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            ten_file = f.name

        ket_qua = subprocess.run(
            [sys.executable, ten_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )

        return {
            "stdout": (ket_qua.stdout or "")[:DO_DAI_OUTPUT_TOI_DA],
            "stderr": (ket_qua.stderr or "")[:DO_DAI_OUTPUT_TOI_DA],
            "returncode": ket_qua.returncode,
        }
    finally:
        if ten_file and os.path.exists(ten_file):
            try:
                os.unlink(ten_file)
            except Exception:
                pass


def chay_python_backend(code, timeout=TIMEOUT_MAC_DINH):
    ket_qua = {
        "thanh_cong": False,
        "stdout": "",
        "stderr": "",
        "returncode": -1,
        "thoi_gian": 0.0,
        "loi": "",
        "so_lan_cai": 0,
    }

    if not code:
        ket_qua["loi"] = "Code rỗng."
        return ket_qua

    if len(code) > DO_DAI_CODE_TOI_DA:
        ket_qua["loi"] = f"Code quá dài."
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

    # Vòng lặp: chạy → nếu thiếu thư viện → cài → chạy lại
    for lan_cai in range(SO_LAN_CAI_TOI_DA + 1):
        try:
            ket_qua_chay = _chay_mot_lan(code, timeout)
        except subprocess.TimeoutExpired:
            ket_qua["loi"] = f"Code chạy quá {timeout} giây — bị hủy."
            ket_qua["stderr"] = f"Timeout sau {timeout}s."
            break
        except Exception as e:
            ket_qua["loi"] = f"Lỗi chạy code: {e}"
            ket_qua["stderr"] = str(e)
            break

        ket_qua["stdout"] = ket_qua_chay["stdout"]
        ket_qua["stderr"] = ket_qua_chay["stderr"]
        ket_qua["returncode"] = ket_qua_chay["returncode"]
        ket_qua["thanh_cong"] = (ket_qua_chay["returncode"] == 0)

        # Nếu thành công → dừng
        if ket_qua["thanh_cong"]:
            break

        # Kiểm tra có thiếu thư viện không
        module_thieu = _trich_module_thieu(ket_qua_chay["stderr"])

        if not module_thieu:
            # Lỗi khác, không phải thiếu thư viện → dừng
            break

        if lan_cai >= SO_LAN_CAI_TOI_DA:
            _in_debug(f"Hết số lần cài thư viện.")
            break

        # Cài thư viện
        cai_ok = _cai_thu_vien(module_thieu)
        if not cai_ok:
            break

        ket_qua["so_lan_cai"] = lan_cai + 1

    ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)

    _ghi_log(
        "sandbox",
        f"Chạy backend: {len(code)} ký tự, "
        f"returncode={ket_qua['returncode']}, "
        f"tg={ket_qua['thoi_gian']}s, "
        f"cài={ket_qua['so_lan_cai']} lần",
    )

    return ket_qua


def _kiem_tra_code_rong(code):
    if not code or not code.strip():
        return True
    code_clean = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
    code_clean = re.sub(r'"""[\s\S]*?"""', "", code_clean)
    code_clean = re.sub(r"'''[\s\S]*?'''", "", code_clean)
    return not code_clean.strip()


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
        ket_qua["loi"] = f"Code quá dài."
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
    return list(THU_VIEN_CHO_PHEP.values())
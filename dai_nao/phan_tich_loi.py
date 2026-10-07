"""
phan_tich_loi.py - Phân tích nguyên nhân lỗi Rồng Thần (bản mạnh x5).

Nhiệm vụ:
    - phan_tich(stderr, code=None, code_cu=None): phân tích lỗi đầy đủ.
    - 15 nhóm phân tích: ngữ cảnh, AST, data flow, control flow,
      scope, dependency, import, diff, đa lỗi, semantic, performance,
      fix đa cấp, patch, flow chart, chất lượng code.

ĐÃ SỬA:
    - L16: Regex trích biến/hàm hỗ trợ tiếng Việt có dấu
      (không chỉ [a-zA-Z_]).

Quy tắc:
    - Đọc lỗi qua doc_loi.py.
    - Tìm dòng code gây lỗi.
    - Trích traceback đầy đủ.
    - Dùng ast module phân tích Python.
    - Dùng difflib để so sánh code cũ/mới.
    - Sinh test case + patch + flow chart.
    - Đánh giá rủi ro sửa + chất lượng code.

Trả về dict đầy đủ 25+ trường.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import re
import time
import ast
import difflib


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
# REGEX HỖ TRỢ TIẾNG VIỆT (L16)
# ================================================================
# Ký tự chữ cái: bao gồm a-z, A-Z, dấu gạch dưới, VÀ tiếng Việt có dấu.
CHU_CAI = (
    r"a-zA-Z"
    r"àáảãạăằắẳẵặâầấẩẫậ"
    r"ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬ"
    r"đĐ"
    r"èéẻẽẹêềếểễệ"
    r"ÈÉẺẼẸÊỀẾỂỄỆ"
    r"ìíỉĩị"
    r"ÌÍỈĨỊ"
    r"òóỏõọôồốổỗộơờớởỡợ"
    r"ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢ"
    r"ùúủũụưừứửữự"
    r"ÙÚỦŨỤƯỪỨỬỮỰ"
    r"ỳýỷỹỵ"
    r"ỲÝỶỸỴ"
)

# Tên biến/hàm: bắt đầu bằng chữ cái hoặc _, theo sau là chữ cái/số/_
MAU_TEN_BIEN = rf"\b([{CHU_CAI}_][{CHU_CAI}0-9_]*)\b"


def _tao_mau_bien():
    """Trả về regex tên biến hỗ trợ tiếng Việt (L16)."""
    return MAU_TEN_BIEN


# ================================================================
# BẢNG NGUYÊN NHÂN GỐC (MỞ RỘNG)
# ================================================================
NGUYEN_NHAN_GOC = {
    "NameError": [
        "Biến/hàm chưa được định nghĩa trước khi sử dụng.",
        "Có thể do gõ sai tên (viết hoa/thường).",
        "Có thể do biến nằm ngoài scope (dùng ngoài hàm).",
        "Có thể do thiếu import thư viện.",
    ],
    "TypeError": [
        "Toán tử/hàm nhận sai kiểu dữ liệu.",
        "Có thể do cộng/trừ số với chuỗi.",
        "Có thể do gọi hàm thiếu/thừa tham số.",
        "Có thể do truyền None vào hàm không cho phép.",
    ],
    "ValueError": [
        "Hàm nhận giá trị không hợp lệ (ví dụ: int('abc')).",
        "Có thể do dữ liệu đầu vào không đúng định dạng.",
        "Có thể do unpacking số phần tử không khớp.",
    ],
    "ImportError": [
        "Module chưa được cài đặt hoặc tên viết sai.",
        "Có thể do thiếu thư viện trong yeu_cau.txt.",
        "Có thể do import vòng (circular import).",
    ],
    "ModuleNotFoundError": [
        "Module chưa cài đặt.",
        "Có thể do quên thêm vào yeu_cau.txt khi deploy.",
        "Có thể do môi trường ảo chưa kích hoạt.",
    ],
    "SyntaxError": [
        "Cú pháp Python sai.",
        "Có thể do thiếu dấu : sau if/for/def.",
        "Có thể do thiếu dấu đóng ngoặc.",
        "Có thể do dùng từ khóa Python làm tên biến.",
    ],
    "IndentationError": [
        "Thụt lề không nhất quán.",
        "Có thể do trộn tab và space.",
        "Có thể do thiếu/thừa space sau dấu :.",
    ],
    "IndexError": [
        "Truy cập index vượt quá độ dài list/string.",
        "Có thể do vòng lặp chạy quá số phần tử.",
        "Có thể do list rỗng.",
    ],
    "KeyError": [
        "Key không tồn tại trong dict.",
        "Có thể do gõ sai tên key.",
        "Có thể do dict rỗng.",
    ],
    "AttributeError": [
        "Object không có thuộc tính đó.",
        "Có thể do dùng sai kiểu (str thay vì list).",
        "Có thể do typo tên thuộc tính.",
    ],
    "ZeroDivisionError": [
        "Mẫu số bằng 0.",
        "Có thể do dữ liệu đầu vào chưa kiểm tra.",
        "Có thể do biến mẫu chưa được gán.",
    ],
    "RecursionError": [
        "Đệ quy không có điều kiện dừng.",
        "Có thể do điều kiện dừng không bao giờ đạt.",
        "Có thể do đệ quy lẫn nhau (A gọi B gọi A).",
    ],
    "MemoryError": [
        "Dữ liệu quá lớn so với RAM.",
        "Có thể do list/array phình to.",
        "Có thể do vòng lặp vô hạn append.",
    ],
    "FileNotFoundError": [
        "File không tồn tại tại đường dẫn.",
        "Có thể do đường dẫn tương đối sai.",
        "Có thể do file bị xóa hoặc di chuyển.",
    ],
    "PermissionError": [
        "Không có quyền truy cập file/thư mục.",
        "Có thể do chạy user không đủ quyền.",
        "Có thể do file đang bị process khác giữ.",
    ],
    "UnicodeDecodeError": [
        "File có encoding khác utf-8.",
        "Có thể do đọc file nhị phân như text.",
    ],
    "TimeoutError": [
        "Hàm chờ quá lâu.",
        "Có thể do mạng chậm hoặc server không phản hồi.",
    ],
    "JS_ReferenceError": [
        "Biến chưa khai báo (let/const/var).",
        "Có thể do gõ sai tên biến.",
        "Có thể do biến trong block scope ({}).",
    ],
    "JS_TypeError": [
        "Toán tử nhận sai kiểu.",
        "Có thể do truy cập thuộc tính của null/undefined.",
        "Có thể do gọi method không tồn tại.",
    ],
    "JS_MaxCallStack": [
        "Đệ quy không có điều kiện dừng.",
        "Có thể do vòng lặp vô hạn gọi hàm.",
    ],
    "JS_UnhandledPromiseRejection": [
        "Promise reject nhưng không có .catch().",
        "Có thể do quên try/catch trong async.",
    ],
    "Java_NullPointerException": [
        "Biến chưa được khởi tạo.",
        "Có thể do gọi method trên null object.",
    ],
    "Java_ArrayIndexOutOfBounds": [
        "Truy cập mảng vượt phạm vi.",
    ],
    "HTTP_401": [
        "Chưa đăng nhập hoặc token hết hạn.",
        "Có thể do token sai format.",
    ],
    "HTTP_403": [
        "Tài khoản không có quyền.",
        "Có thể do IP bị chặn.",
    ],
    "HTTP_404": [
        "URL sai hoặc resource không tồn tại.",
        "Có thể do route chưa đăng ký.",
    ],
    "HTTP_429": [
        "Vượt rate limit — gọi API quá nhiều.",
        "Có thể do nhiều client dùng cùng key.",
    ],
    "HTTP_500": [
        "Server gặp lỗi runtime.",
        "Có thể do query DB lỗi.",
    ],
    "DB_Atlas_IPWhitelist": [
        "IP hiện tại chưa được whitelist trong Atlas.",
        "Có thể do Render IP thay đổi.",
    ],
    "DB_DuplicateKey": [
        "Đã tồn tại document với key unique.",
        "Có thể do insert 2 lần cùng _id.",
    ],
    "Docker_OOMKilled": ["Container dùng vượt memory limit."],
    "Docker_CrashLoop": ["App crash khi khởi động."],
    "OS_PermissionDenied": ["Thiếu quyền chmod."],
    "OS_DiskFull": ["Ổ đĩa đã đầy."],
}


# ================================================================
# LIÊN KẾT LỖI NHÂN QUẢ
# ================================================================
QUAN_HE_NHAN_QUA = {
    "ConnectionRefusedError": ["TimeoutError", "ConnectionResetError"],
    "TimeoutError": ["ConnectionAbortedError"],
    "PermissionError": ["FileNotFoundError"],
    "ImportError": ["ModuleNotFoundError"],
    "AttributeError": ["TypeError"],
    "KeyError": ["IndexError"],
    "HTTP_401": ["HTTP_403"],
    "HTTP_500": ["HTTP_502", "HTTP_503"],
    "Docker_OOMKilled": ["Docker_CrashLoop"],
    "DB_ConnectionRefused": ["DB_Timeout", "DB_AuthFailed"],
    "MemoryError": ["RecursionError"],
    "ZeroDivisionError": ["ValueError"],
}


# ================================================================
# TEST CASE MẪU
# ================================================================
TEST_CASE = {
    "NameError": [
        "# Test: biến được khai báo trước khi dùng\nx = 5\nassert x == 5",
    ],
    "TypeError": [
        "# Test: cộng 2 số cùng kiểu\nassert 1 + 2 == 3",
        "# Test: ép kiểu trước khi cộng\nassert int('5') + 3 == 8",
    ],
    "ValueError": [
        "# Test: int() với chuỗi số\nassert int('123') == 123",
    ],
    "IndexError": [
        "# Test: kiểm tra len trước khi truy cập\nlst = [1, 2, 3]\nassert lst[2] == 3",
    ],
    "KeyError": [
        "# Test: dùng dict.get()\nd = {'a': 1}\nassert d.get('b', 0) == 0",
    ],
    "ZeroDivisionError": [
        "# Test: kiểm tra mẫu số\na, b = 10, 2\nassert b != 0\nassert a / b == 5",
    ],
    "AttributeError": [
        "# Test: kiểm tra thuộc tính tồn tại\ns = 'abc'\nassert hasattr(s, 'upper')",
    ],
    "ImportError": [
        "# Test: import thư viện\nimport json\nassert json is not None",
    ],
    "SyntaxError": [
        "# Test: cú pháp đúng\nx = 5\nif x > 0:\n    print('OK')",
    ],
    "RecursionError": [
        "# Test: đệ quy có điều kiện dừng\ndef fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n-1)\nassert fact(5) == 120",
    ],
    "HTTP_401": [
        "# Test: gọi API với token\n# import requests\n# r = requests.get(url, headers={'Authorization': 'Bearer TOKEN'})\n# assert r.status_code == 200",
    ],
    "HTTP_404": [
        "# Test: kiểm tra URL trả 200\n# import requests\n# r = requests.get('https://example.com')\n# assert r.status_code == 200",
    ],
    "HTTP_429": [
        "# Test: retry với backoff\n# import time\n# for i in range(3):\n#     if thu_lai(): break\n#     time.sleep(2 ** i)",
    ],
}


# ================================================================
# ĐÁNH GIÁ RỦI RO
# ================================================================
RUI_RO_THEO_LOAI = {
    "NameError": {"muc_do": "thap", "ly_do": "Khai báo biến — ít ảnh hưởng."},
    "TypeError": {"muc_do": "trung_binh", "ly_do": "Ép kiểu có thể mất dữ liệu."},
    "ValueError": {"muc_do": "trung_binh", "ly_do": "Bọc try/except có thể che lỗi thật."},
    "ImportError": {"muc_do": "thap", "ly_do": "Thêm import không ảnh hưởng."},
    "SyntaxError": {"muc_do": "thap", "ly_do": "Sửa cú pháp ít ảnh hưởng."},
    "IndexError": {"muc_do": "trung_binh", "ly_do": "Thêm kiểm tra len có thể bỏ case."},
    "KeyError": {"muc_do": "thap", "ly_do": "dict.get() an toàn nhưng che lỗi."},
    "AttributeError": {"muc_do": "cao", "ly_do": "Có thể do logic sai tầng trên."},
    "ZeroDivisionError": {"muc_do": "trung_binh", "ly_do": "Thêm if bỏ case cần xử lý."},
    "RecursionError": {"muc_do": "cao", "ly_do": "Sửa đệ quy thay đổi kết quả."},
    "MemoryError": {"muc_do": "cao", "ly_do": "Cần refactor — ảnh hưởng nhiều module."},
    "HTTP_401": {"muc_do": "thap", "ly_do": "Thêm token — ít ảnh hưởng."},
    "HTTP_429": {"muc_do": "thap", "ly_do": "Thêm retry — không đổi logic."},
    "DB_Atlas_IPWhitelist": {"muc_do": "thap", "ly_do": "Chỉ thêm IP."},
}


# ================================================================
# TIỆN ÍCH CHUNG (SỬA L16)
# ================================================================
def _trich_bien_lien_quan(code, dong_bi_loi):
    """
    Trích tên biến/hàm từ dòng lỗi.

    SỬA L16: Dùng regex hỗ trợ tiếng Việt có dấu.
    """
    if not code or not dong_bi_loi:
        return []
    noi_dung = dong_bi_loi.get("noi_dung", "")
    if not noi_dung:
        return []

    # Regex hỗ trợ tiếng Việt
    cac_bien = re.findall(MAU_TEN_BIEN, noi_dung)

    tu_khoa = {
        "if", "else", "elif", "for", "while", "def", "class", "return",
        "import", "from", "as", "try", "except", "finally", "with",
        "and", "or", "not", "in", "is", "None", "True", "False",
        "print", "len", "range", "int", "str", "float", "list", "dict",
        "set", "tuple", "type", "input", "open", "self",
    }
    ket_qua = []
    for b in cac_bien:
        if b not in tu_khoa and len(b) >= 2 and b not in ket_qua:
            ket_qua.append(b)
    return ket_qua[:10]


def _lay_ngu_canh_dong(code, so_dong, so_truoc=5, so_sau=5):
    if not code or not so_dong:
        return []
    cac_dong = code.split("\n")
    tong = len(cac_dong)
    bat_dau = max(1, so_dong - so_truoc)
    ket_thuc = min(tong, so_dong + so_sau)
    ket_qua = []
    for i in range(bat_dau, ket_thuc + 1):
        ket_qua.append({
            "so_dong": i,
            "noi_dung": cac_dong[i - 1],
            "danh_dau": (i == so_dong),
        })
    return ket_qua


def _tim_ham_chua(code, so_dong):
    """
    Tìm hàm chứa dòng lỗi.

    SỬA L16: Tên hàm hỗ trợ tiếng Việt.
    """
    if not code or not so_dong:
        return None
    cac_dong = code.split("\n")
    if so_dong > len(cac_dong):
        return None

    mau_ham = rf"^(\s*)def\s+([{CHU_CAI}_][{CHU_CAI}0-9_]*)\s*\("
    mau_class = rf"^class\s+([{CHU_CAI}_][{CHU_CAI}0-9_]*)"

    for i in range(so_dong - 1, -1, -1):
        dong = cac_dong[i]
        khop = re.match(mau_ham, dong)
        if khop:
            return {
                "ten_ham": khop.group(2),
                "so_dong_bat_dau": i + 1,
                "thut_le": len(khop.group(1)),
            }
        if re.match(mau_class, dong):
            break
    return None


def _tim_class_chua(code, so_dong):
    """
    Tìm class chứa dòng lỗi.

    SỬA L16: Tên class hỗ trợ tiếng Việt.
    """
    if not code or not so_dong:
        return None
    cac_dong = code.split("\n")
    mau_class = rf"^class\s+([{CHU_CAI}_][{CHU_CAI}0-9_]*)"
    for i in range(so_dong - 1, -1, -1):
        dong = cac_dong[i]
        khop = re.match(mau_class, dong)
        if khop:
            return {"ten_class": khop.group(1), "so_dong_bat_dau": i + 1}
    return None


# ================================================================
# PHÂN TÍCH AST PYTHON
# ================================================================
def _phan_tich_ast(code, so_dong_loi=None):
    """Phân tích AST Python đầy đủ."""
    ket_qua = {
        "parse_duoc": False, "loi_cu_phap": "",
        "ham": [], "class_": [], "import_": [],
        "bien_gan": [], "bien_dung": [],
        "bien_chua_khai_bao": [],
        "ham_goi": [], "ham_chua_dinh_nghia": [],
        "vong_lap_vo_han": [],
        "code_chet": [],
        "import_khong_dung": [],
        "o_n2": [],
    }
    if not code:
        return ket_qua
    try:
        cay = ast.parse(code)
    except SyntaxError as e:
        ket_qua["loi_cu_phap"] = f"Dòng {e.lineno}: {e.msg}"
        return ket_qua

    ket_qua["parse_duoc"] = True
    tap_ham = set()
    tap_class = set()
    tap_import = set()

    for node in ast.walk(cay):
        if isinstance(node, ast.FunctionDef):
            tap_ham.add(node.name)
            ket_qua["ham"].append({
                "ten": node.name, "so_dong": node.lineno,
                "tham_so": [a.arg for a in node.args.args],
            })
        elif isinstance(node, ast.ClassDef):
            tap_class.add(node.name)
            method = [i.name for i in node.body if isinstance(i, ast.FunctionDef)]
            ket_qua["class_"].append({
                "ten": node.name, "so_dong": node.lineno, "method": method,
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                tap_import.add(alias.name.split(".")[0])
                ket_qua["import_"].append({
                    "module": alias.name, "so_dong": node.lineno, "loai": "import",
                })
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            if mod:
                tap_import.add(mod)
            ket_qua["import_"].append({
                "module": node.module or "", "so_dong": node.lineno, "loai": "from",
            })
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    ket_qua["bien_gan"].append(target.id)
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name):
                ket_qua["bien_gan"].append(node.target.id)
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                ket_qua["bien_dung"].append(node.id)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                ket_qua["ham_goi"].append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                ket_qua["ham_goi"].append(node.func.attr)
        elif isinstance(node, ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                if not any(isinstance(n, ast.Break) for n in ast.walk(node)):
                    ket_qua["vong_lap_vo_han"].append(node.lineno)
        elif isinstance(node, ast.For):
            for con in ast.walk(node):
                if isinstance(con, (ast.For, ast.While)) and con is not node:
                    ket_qua["o_n2"].append(node.lineno)
                    break

    try:
        tap_builtin = set(dir(__builtins__)) if not isinstance(__builtins__, dict) \
                      else set(__builtins__.keys())
    except Exception:
        tap_builtin = {"print", "len", "range", "int", "str", "float",
                       "list", "dict", "set", "tuple", "type", "input", "open"}

    ten_ham = {h["ten"] for h in ket_qua["ham"]}
    tham_so = set()
    for h in ket_qua["ham"]:
        tham_so.update(h["tham_so"])

    bien_da_gan = set(ket_qua["bien_gan"])
    bien_da_dung = set(ket_qua["bien_dung"])

    for bien in bien_da_dung:
        if bien in tap_builtin or bien in bien_da_gan:
            continue
        if bien in ten_ham or bien in tham_so or bien in tap_class:
            continue
        if bien in {"self", "cls"}:
            continue
        if bien not in ket_qua["bien_chua_khai_bao"]:
            ket_qua["bien_chua_khai_bao"].append(bien)

    for h in ket_qua["ham_goi"]:
        if h in tap_builtin or h in ten_ham:
            continue
        if h not in ket_qua["ham_chua_dinh_nghia"]:
            ket_qua["ham_chua_dinh_nghia"].append(h)

    for imp in ket_qua["import_"]:
        mod = imp.get("module", "").split(".")[0]
        if mod and mod not in bien_da_dung:
            ket_qua["import_khong_dung"].append(mod)

    for node in ast.walk(cay):
        if isinstance(node, (ast.FunctionDef, ast.Module)):
            for i, stmt in enumerate(node.body):
                if isinstance(stmt, ast.Return) and i < len(node.body) - 1:
                    ket_qua["code_chet"].append(node.body[i + 1].lineno)

    ket_qua["bien_chua_khai_bao"] = list(dict.fromkeys(ket_qua["bien_chua_khai_bao"]))
    ket_qua["ham_chua_dinh_nghia"] = list(dict.fromkeys(ket_qua["ham_chua_dinh_nghia"]))
    ket_qua["bien_gan"] = list(dict.fromkeys(ket_qua["bien_gan"]))
    ket_qua["bien_dung"] = list(dict.fromkeys(ket_qua["bien_dung"]))
    ket_qua["ham_goi"] = list(dict.fromkeys(ket_qua["ham_goi"]))
    ket_qua["import_khong_dung"] = list(dict.fromkeys(ket_qua["import_khong_dung"]))
    ket_qua["o_n2"] = list(dict.fromkeys(ket_qua["o_n2"]))
    ket_qua["code_chet"] = list(dict.fromkeys(ket_qua["code_chet"]))

    return ket_qua


# ================================================================
# PHÂN TÍCH LUỒNG DỮ LIỆU (SỬA L16)
# ================================================================
def _phan_tich_luong_du_lieu(code, bien_lien_quan):
    """
    Truy vết biến: gán ở đâu, sửa ở đâu, dùng ở đâu.

    SỬA L16: Regex hỗ trợ tiếng Việt.
    """
    if not code or not bien_lien_quan:
        return []

    cac_dong = code.split("\n")
    ket_qua = []

    for bien in bien_lien_quan[:5]:
        vi_tri_gan = []
        vi_tri_dung = []
        vi_tri_sua = []

        # Regex tìm biến (an toàn với ký tự đặc biệt)
        mau_bien = re.escape(bien)

        for i, dong in enumerate(cac_dong, 1):
            if re.search(r"\b" + mau_bien + r"\s*=", dong) and \
               not re.search(r"==", dong):
                vi_tri_gan.append(i)
            if re.search(r"\b" + mau_bien + r"\s*\+=", dong) or \
               re.search(r"\b" + mau_bien + r"\s*-=", dong):
                vi_tri_sua.append(i)
            if re.search(r"\b" + mau_bien + r"\b", dong) and \
               i not in vi_tri_gan:
                vi_tri_dung.append(i)

        ket_qua.append({
            "bien": bien,
            "gan_o": vi_tri_gan,
            "sua_o": vi_tri_sua,
            "dung_o": vi_tri_dung,
            "so_lan_dung": len(vi_tri_dung),
        })

    return ket_qua


# ================================================================
# PHÂN TÍCH LUỒNG ĐIỀU KHIỂN
# ================================================================
def _phan_tich_luong_dieu_khien(code, so_dong_loi):
    if not code or not so_dong_loi:
        return []

    cac_dong = code.split("\n")
    duong_di = []
    thut_le_hien_tai = None

    for i in range(max(0, so_dong_loi - 50), so_dong_loi):
        dong = cac_dong[i]
        if not dong.strip():
            continue

        thut_le = len(dong) - len(dong.lstrip())
        dong_strip = dong.strip()

        if (dong_strip.startswith("if ") or dong_strip.startswith("elif ") or
            dong_strip.startswith("else") or dong_strip.startswith("for ") or
            dong_strip.startswith("while ") or dong_strip.startswith("try") or
            dong_strip.startswith("except") or dong_strip.startswith("with ")):
            if thut_le_hien_tai is None or thut_le <= thut_le_hien_tai + 4:
                duong_di.append({
                    "so_dong": i + 1,
                    "noi_dung": dong_strip,
                    "thut_le": thut_le,
                })

    return duong_di[-10:]


# ================================================================
# PHÂN TÍCH SCOPE
# ================================================================
def _phan_tich_scope(code, bien_lien_quan):
    """
    SỬA L16: Regex hỗ trợ tiếng Việt.
    """
    if not code or not bien_lien_quan:
        return {}

    ket_qua = {"bien_local": [], "bien_global": [], "bien_ngoai": []}
    mau_ten = rf"[{CHU_CAI}_][{CHU_CAI}0-9_]*"
    co_global = set(re.findall(rf"\bglobal\s+({mau_ten})", code))
    co_nonlocal = set(re.findall(rf"\bnonlocal\s+({mau_ten})", code))

    for bien in bien_lien_quan:
        if bien in co_global:
            ket_qua["bien_global"].append(bien)
        elif bien in co_nonlocal:
            ket_qua["bien_ngoai"].append(bien)
        else:
            ket_qua["bien_local"].append(bien)

    return ket_qua


# ================================================================
# PHÂN TÍCH DEPENDENCY (SỬA L16)
# ================================================================
def _phan_tich_dependency(code, ham_chua):
    """
    SỬA L16: Regex hỗ trợ tiếng Việt.
    """
    if not code or not ham_chua:
        return {}

    ten_ham = ham_chua.get("ten_ham", "")
    if not ten_ham:
        return {}

    cac_dong = code.split("\n")
    goi_ham_khac = set()
    bi_goi_boi = []

    mau_goi = rf"\b([{CHU_CAI}_][{CHU_CAI}0-9_]*)\s*\("

    so_dong_bat_dau = ham_chua.get("so_dong_bat_dau", 0) - 1
    thut_le_goc = ham_chua.get("thut_le", 0)
    for i in range(so_dong_bat_dau + 1, len(cac_dong)):
        dong = cac_dong[i]
        if dong.strip() and (len(dong) - len(dong.lstrip())) <= thut_le_goc:
            break
        for m in re.finditer(mau_goi, dong):
            ten = m.group(1)
            if ten not in {"if", "for", "while", "return", "print"}:
                goi_ham_khac.add(ten)

    mau_ham_goi = re.escape(ten_ham) + r"\s*\("
    for i, dong in enumerate(cac_dong, 1):
        if re.search(mau_ham_goi, dong):
            if i != ham_chua.get("so_dong_bat_dau"):
                bi_goi_boi.append(i)

    return {
        "ten_ham": ten_ham,
        "goi_ham_khac": sorted(goi_ham_khac),
        "bi_goi_boi_dong": bi_goi_boi[:10],
        "so_call_site": len(bi_goi_boi),
    }


# ================================================================
# PHÂN TÍCH IMPORT
# ================================================================
def _phan_tich_import(code):
    if not code:
        return {}

    import_ = re.findall(r"^\s*(?:from\s+(\S+)\s+)?import\s+(.+?)(?:\s+as\s+\w+)?$",
                        code, re.MULTILINE)
    danh_sach = set()
    for mod, _ in import_:
        if mod:
            danh_sach.add(mod.split(".")[0])

    return {
        "so_import": len(danh_sach),
        "danh_sach": sorted(danh_sach),
        "co_import_vong": False,
    }


# ================================================================
# SO SÁNH CODE CŨ/MỚI
# ================================================================
def _so_sanh_code(code_cu, code_moi):
    if not code_cu or not code_moi:
        return {}

    dong_cu = code_cu.splitlines()
    dong_moi = code_moi.splitlines()

    diff = list(difflib.unified_diff(
        dong_cu, dong_moi,
        lineterm="",
        fromfile="code_cu", tofile="code_moi", n=2,
    ))

    so_them = sum(1 for d in diff if d.startswith("+") and not d.startswith("+++"))
    so_xoa = sum(1 for d in diff if d.startswith("-") and not d.startswith("---"))

    return {
        "so_them": so_them,
        "so_xoa": so_xoa,
        "diff": "\n".join(diff[:100]),
    }


# ================================================================
# PHÂN TÍCH ĐA LỖI
# ================================================================
def _phan_tich_da_loi(stderr):
    try:
        from dai_nao.doc_loi import doc_loi_nhieu
        danh_sach = doc_loi_nhieu(stderr)
    except ImportError:
        return []

    if len(danh_sach) <= 1:
        return danh_sach

    ket_qua = []
    for i, muc in enumerate(danh_sach):
        ket_qua.append({
            "thu_tu": i,
            "loai_loi": muc.get("loai_loi"),
            "ngon_ngu": muc.get("ngon_ngu"),
            "mo_ta": muc.get("mo_ta"),
            "la_goc": (i == 0),
        })

    return ket_qua


# ================================================================
# PHÂN TÍCH NGỮ NGHĨA (SỬA L16)
# ================================================================
def _phan_tich_ngu_nghia(code, ast_loi):
    if not code:
        return {}

    ket_qua = {
        "ten_bien_dang_ngo": [],
        "ham_khong_return": [],
        "ham_return_nhieu_kieu": [],
    }

    goi_y_kieu = {
        "so_": "int", "count": "int", "total": "int", "amount": "int",
        "ten_": "str", "name": "str", "text": "str", "message": "str",
        "danh_sach": "list", "list_": "list", "items": "list",
        "dict_": "dict", "map_": "dict",
    }
    for bien in (ast_loi or {}).get("bien_gan", []):
        for tien_to, kieu_goi_y in goi_y_kieu.items():
            if bien.lower().startswith(tien_to):
                mau = r"\b" + re.escape(bien) + r"\s*=\s*(['\"])"
                if kieu_goi_y != "str" and re.search(mau, code):
                    ket_qua["ten_bien_dang_ngo"].append({
                        "bien": bien,
                        "goi_y": kieu_goi_y,
                        "thuc_te": "str",
                    })

    return ket_qua


# ================================================================
# PHÂN TÍCH HIỆU NĂNG (SỬA L16)
# ================================================================
def _phan_tich_hieu_nang(code, ast_loi):
    if not code:
        return {}

    ket_qua = {
        "vong_lap_long": [],
        "goi_ham_trong_vong_lap": [],
    }

    for dong in (ast_loi or {}).get("o_n2", []):
        ket_qua["vong_lap_long"].append({"so_dong": dong})

    cac_dong = code.split("\n")
    trong_vong_lap = False
    thut_le_vong = 0
    mau_vong = r"^\s*(for|while)\s"
    mau_goi = r"\b(len|range|print|append)\s*\("

    for i, dong in enumerate(cac_dong, 1):
        thut_le = len(dong) - len(dong.lstrip())
        if re.match(mau_vong, dong):
            trong_vong_lap = True
            thut_le_vong = thut_le
        elif trong_vong_lap and dong.strip() and thut_le <= thut_le_vong:
            trong_vong_lap = False

        if trong_vong_lap:
            for m in re.finditer(mau_goi, dong):
                ket_qua["goi_ham_trong_vong_lap"].append({
                    "so_dong": i, "ham": m.group(1),
                })

    return ket_qua


# ================================================================
# SINH FIX ĐA CẤP
# ================================================================
def _sinh_fix_da_cap(loai_loi, code, dong_bi_loi, thong_tin):
    fix = {"fix_nhanh": "", "fix_chuan": "", "fix_phong_ngua": ""}

    dong = dong_bi_loi.get("noi_dung", "").strip() if dong_bi_loi else ""
    so_dong = dong_bi_loi.get("so_dong") if dong_bi_loi else None

    code_mau = thong_tin.get("code_sua_mau", "")
    if code_mau:
        fix["fix_chuan"] = code_mau

    if loai_loi == "NameError":
        fix["fix_nhanh"] = f"# Thêm dòng khai báo trước dòng {so_dong}"
        fix["fix_phong_ngua"] = "# Khởi tạo biến mặc định ở đầu hàm"
    elif loai_loi == "IndexError":
        fix["fix_nhanh"] = f"if len(lst) > i:\n    val = lst[i]"
        fix["fix_phong_ngua"] = "if lst and i < len(lst):\n    ..."
    elif loai_loi == "KeyError":
        fix["fix_nhanh"] = "val = d.get(key)"
        fix["fix_phong_ngua"] = "val = d.get(key, mac_dinh)"
    elif loai_loi == "ZeroDivisionError":
        fix["fix_nhanh"] = "if b != 0:\n    kq = a / b"
        fix["fix_phong_ngua"] = "if b:\n    kq = a / b\nelse:\n    kq = 0"
    elif loai_loi == "TypeError":
        fix["fix_nhanh"] = "# Ép kiểu trước khi tính"
        fix["fix_phong_ngua"] = "assert isinstance(x, (int, float))"
    elif loai_loi == "RecursionError":
        fix["fix_nhanh"] = "# Thêm điều kiện dừng"
        fix["fix_phong_ngua"] = "import sys\nsys.setrecursionlimit(10000)"
    else:
        fix["fix_nhanh"] = thong_tin.get("goi_y", [""])[0] if thong_tin.get("goi_y") else ""

    return fix


# ================================================================
# SINH PATCH
# ================================================================
def _sinh_patch(code_cu, code_moi):
    if not code_cu or not code_moi:
        return ""

    dong = list(difflib.unified_diff(
        code_cu.splitlines(),
        code_moi.splitlines(),
        fromfile="code_cu.py",
        tofile="code_moi.py",
        lineterm="", n=2,
    ))
    return "\n".join(dong)


# ================================================================
# VẼ FLOW CHART ASCII
# ================================================================
def _ve_flow_chart(code, so_dong_loi):
    if not code or not so_dong_loi:
        return ""

    cac_dong = code.split("\n")
    if so_dong_loi > len(cac_dong):
        return ""

    ket_qua = ["Bắt đầu"]
    for i in range(max(0, so_dong_loi - 20), so_dong_loi):
        dong = cac_dong[i].strip()
        if not dong:
            continue
        if dong.startswith("if ") or dong.startswith("elif "):
            ket_qua.append(f"  ├─ {dong[:50]}")
        elif dong.startswith("else"):
            ket_qua.append(f"  ├─ else")
        elif dong.startswith("for ") or dong.startswith("while "):
            ket_qua.append(f"  ├─ Vòng lặp: {dong[:40]}")
        elif dong.startswith("try"):
            ket_qua.append("  ├─ Try")
        elif dong.startswith("except"):
            ket_qua.append(f"  ├─ Except: {dong[:40]}")
    ket_qua.append(f"  └─ 💥 LỖI ở dòng {so_dong_loi}")

    return "\n".join(ket_qua)


# ================================================================
# CHẤM ĐIỂM CHẤT LƯỢNG CODE
# ================================================================
def _cham_diem_chat_luong(code, ast_loi):
    if not code or not ast_loi:
        return {"diem": 0, "chi_tiet": {}, "goi_y": []}

    diem = 10
    chi_tiet = {}
    goi_y = []

    so_bien_loi = len(ast_loi.get("bien_chua_khai_bao", []))
    if so_bien_loi > 0:
        diem -= min(3, so_bien_loi)
        chi_tiet["bien_chua_khai_bao"] = -min(3, so_bien_loi)
        goi_y.append(f"Có {so_bien_loi} biến chưa khai báo.")

    so_ham_loi = len(ast_loi.get("ham_chua_dinh_nghia", []))
    if so_ham_loi > 0:
        diem -= min(2, so_ham_loi)
        chi_tiet["ham_chua_dinh_nghia"] = -min(2, so_ham_loi)

    so_import_thua = len(ast_loi.get("import_khong_dung", []))
    if so_import_thua > 0:
        diem -= min(2, so_import_thua)
        chi_tiet["import_khong_dung"] = -min(2, so_import_thua)
        goi_y.append(f"Có {so_import_thua} import không dùng — nên xóa.")

    so_o_n2 = len(ast_loi.get("o_n2", []))
    if so_o_n2 > 0:
        diem -= min(2, so_o_n2)
        chi_tiet["o_n2"] = -min(2, so_o_n2)
        goi_y.append(f"Có {so_o_n2} vòng lặp lồng — có thể chậm.")

    so_code_chet = len(ast_loi.get("code_chet", []))
    if so_code_chet > 0:
        diem -= 1
        chi_tiet["code_chet"] = -1
        goi_y.append("Có code chết sau return.")

    return {
        "diem": max(0, diem),
        "chi_tiet": chi_tiet,
        "goi_y": goi_y,
    }


# ================================================================
# SINH TEST CASE
# ================================================================
def _sinh_test_case(loai_loi, code=None, dong_bi_loi=None):
    if loai_loi in TEST_CASE:
        return list(TEST_CASE[loai_loi])

    test_tu_dong = []
    if code and dong_bi_loi:
        noi_dung = dong_bi_loi.get("noi_dung", "").strip()
        so_dong = dong_bi_loi.get("so_dong")
        if noi_dung:
            test_tu_dong.append(
                f"# Test dòng {so_dong}:\n"
                f"# Dòng cũ: {noi_dung}\n"
                f"# assert ... kiểm tra kết quả đúng."
            )
    test_tu_dong.append(
        "# Test cơ bản:\n"
        "# try:\n"
        "#     ket_qua = ham()\n"
        "#     assert ket_qua is not None\n"
        "# except Exception as e:\n"
        "#     print('Lỗi còn:', e)"
    )
    return test_tu_dong


# ================================================================
# ĐÁNH GIÁ RỦI RO
# ================================================================
def _danh_gia_rui_ro(loai_loi, code, ham_chua, ast_loi):
    ket_qua = {"muc_do": "trung_binh", "ly_do": "Chưa đánh giá.", "anh_huong": [], "canh_bao": ""}

    if loai_loi in RUI_RO_THEO_LOAI:
        thong_tin = RUI_RO_THEO_LOAI[loai_loi]
        ket_qua["muc_do"] = thong_tin["muc_do"]
        ket_qua["ly_do"] = thong_tin["ly_do"]

    if code and ham_chua:
        ten_ham = ham_chua.get("ten_ham", "")
        if ten_ham:
            so_lan_goi = len(re.findall(r"\b" + re.escape(ten_ham) + r"\s*\(", code))
            if so_lan_goi > 3:
                ket_qua["muc_do"] = "cao"
                ket_qua["ly_do"] += f" Hàm '{ten_ham}' được gọi {so_lan_goi} lần."
                ket_qua["canh_bao"] = "Cần test kỹ tất cả call site."
            ket_qua["anh_huong"].append(f"Hàm '{ten_ham}' ({so_lan_goi} call sites)")

    if ast_loi and ast_loi.get("parse_duoc"):
        so_bien_loi = len(ast_loi.get("bien_chua_khai_bao", []))
        if so_bien_loi > 3:
            ket_qua["muc_do"] = "cao"
            ket_qua["canh_bao"] += f" Có {so_bien_loi} biến chưa khai báo."

    return ket_qua


# ================================================================
# SINH GIẢ THUYẾT
# ================================================================
def _sinh_gia_thuyet(loai_loi, code, dong_bi_loi, ast_loi):
    gia_thuyet = []

    for nn in NGUYEN_NHAN_GOC.get(loai_loi, [])[:3]:
        gia_thuyet.append({
            "gia_thuyet": nn, "xac_suat": "cao",
            "cach_kiem_tra": "Đọc kỹ dòng bị lỗi + các dòng xung quanh.",
        })

    if ast_loi and ast_loi.get("parse_duoc"):
        for b in ast_loi.get("bien_chua_khai_bao", [])[:2]:
            gia_thuyet.append({
                "gia_thuyet": f"Biến '{b}' chưa được khai báo.",
                "xac_suat": "cao",
                "cach_kiem_tra": f"Thêm `print({b})` trước dòng lỗi.",
            })
        for h in ast_loi.get("ham_chua_dinh_nghia", [])[:2]:
            gia_thuyet.append({
                "gia_thuyet": f"Hàm '{h}' được gọi nhưng chưa định nghĩa.",
                "xac_suat": "trung_binh",
                "cach_kiem_tra": f"Tìm `def {h}` trong code.",
            })
        for v in ast_loi.get("vong_lap_vo_han", [])[:1]:
            gia_thuyet.append({
                "gia_thuyet": f"Vòng lặp while True ở dòng {v} có thể vô hạn.",
                "xac_suat": "trung_binh",
                "cach_kiem_tra": "Kiểm tra có `break` không.",
            })

    if not gia_thuyet:
        gia_thuyet.append({
            "gia_thuyet": "Chưa xác định rõ — cần đọc kỹ code.",
            "xac_suat": "thap",
            "cach_kiem_tra": "In các biến liên quan trước dòng lỗi.",
        })

    return gia_thuyet[:5]


# ================================================================
# ĐỀ XUẤT CÁCH SỬA
# ================================================================
def _de_xuat_cach_sua(ket_qua, thong_tin, code):
    cach_sua = []
    code_mau = thong_tin.get("code_sua_mau", "")
    if code_mau:
        cach_sua.append(f"Code mẫu:\n{code_mau}")

    for goi_y in thong_tin.get("goi_y", []):
        if goi_y not in cach_sua:
            cach_sua.append(goi_y)

    dong_bi_loi = ket_qua.get("dong_bi_loi")
    if dong_bi_loi:
        cach_sua.append(f"Xem dòng {dong_bi_loi.get('so_dong')}: "
                        f"{dong_bi_loi.get('noi_dung', '').strip()}")

    loai = ket_qua.get("loai_loi", "")
    if loai == "NameError":
        bien = ket_qua.get("bien_lien_quan", [])
        if bien:
            cach_sua.append(f"Kiểm tra biến '{bien[0]}' đã gán chưa.")
    elif loai == "IndexError":
        cach_sua.append("Kiểm tra `len()` trước khi truy cập.")
    elif loai == "KeyError":
        cach_sua.append("Dùng `dict.get(key, mặc_định)`.")
    elif loai == "ZeroDivisionError":
        cach_sua.append("Thêm `if mẫu != 0:` trước phép chia.")
    elif loai == "AttributeError":
        cach_sua.append("Dùng `dir(obj)` xem thuộc tính.")
    elif loai in ("HTTP_429", "API_RateLimit"):
        cach_sua.append("Chờ 1 phút rồi retry. Xoay key.")
    elif loai in ("TimeoutError", "API_Timeout"):
        cach_sua.append("Tăng timeout: requests.get(url, timeout=30).")

    if ket_qua.get("ngon_ngu") == "Python" and loai not in ("SyntaxError", "IndentationError"):
        cach_sua.append("Bọc try/except để phòng lỗi tương tự.")

    da_gap = []
    for c in cach_sua:
        if c not in da_gap:
            da_gap.append(c)
    return da_gap


# ================================================================
# HÀM CHÍNH
# ================================================================
def phan_tich(stderr, code=None, code_cu=None):
    """
    Phân tích lỗi đầy đủ (bản mạnh x5).

    ĐÃ SỬA L16: Regex trích biến/hàm hỗ trợ tiếng Việt có dấu.

    stderr: chuỗi lỗi.
    code: code hiện tại.
    code_cu: code cũ (để so sánh, tùy chọn).

    Trả về dict đầy đủ 25+ trường.
    """
    ket_qua = {
        "co_loi": False, "loai_loi": "", "ngon_ngu": "",
        "nguyen_nhan_goc": "", "dong_bi_loi": None, "frames": [],
        "bien_lien_quan": [], "ngu_canh_dong": [],
        "cach_sua": [], "do_kho_sua": "trung_binh",
        "loi_lien_quan": [], "gia_thuyet": [], "test_case": [],
        "rui_ro": {}, "ham_chua": None, "class_chua": None,
        "ast_loi": None, "luong_du_lieu": [], "luong_dieu_khien": [],
        "scope": {}, "dependency": {}, "import_": {},
        "diff": {}, "da_loi": [], "ngu_nghia": {},
        "hieu_nang": {}, "fix_da_cap": {}, "patch": "",
        "flow_chart": "", "chat_luong": {},
    }

    if not stderr:
        return ket_qua

    try:
        from dai_nao.doc_loi import doc_loi, trich_traceback, tim_dong_bi_loi
        thong_tin = doc_loi(stderr)
    except ImportError:
        _ghi_log("loi", "doc_loi.py chưa có.")
        return ket_qua

    if not thong_tin.get("co_loi"):
        return ket_qua

    ket_qua.update({
        "co_loi": True,
        "loai_loi": thong_tin.get("loai_loi", ""),
        "ngon_ngu": thong_tin.get("ngon_ngu", ""),
        "do_kho_sua": thong_tin.get("thoi_gian_sua", "trung_binh"),
    })

    try:
        ket_qua["frames"] = trich_traceback(stderr)
    except Exception:
        pass

    dong_bi_loi = None
    if code:
        try:
            dong_bi_loi = tim_dong_bi_loi(stderr, code)
            ket_qua["dong_bi_loi"] = dong_bi_loi
            if dong_bi_loi:
                sd = dong_bi_loi.get("so_dong")
                ket_qua["bien_lien_quan"] = _trich_bien_lien_quan(code, dong_bi_loi)
                ket_qua["ngu_canh_dong"] = _lay_ngu_canh_dong(code, sd, 5, 5)
                ket_qua["ham_chua"] = _tim_ham_chua(code, sd)
                ket_qua["class_chua"] = _tim_class_chua(code, sd)
        except Exception as e:
            _ghi_log("loi", f"Tìm dòng lỗi lỗi: {e}")

    ast_loi = None
    if code and ket_qua["ngon_ngu"] == "Python":
        try:
            ast_loi = _phan_tich_ast(code, dong_bi_loi.get("so_dong") if dong_bi_loi else None)
            ket_qua["ast_loi"] = {
                "parse_duoc": ast_loi["parse_duoc"],
                "loi_cu_phap": ast_loi["loi_cu_phap"],
                "so_ham": len(ast_loi["ham"]),
                "so_class": len(ast_loi["class_"]),
                "so_import": len(ast_loi["import_"]),
                "bien_chua_khai_bao": ast_loi["bien_chua_khai_bao"],
                "ham_chua_dinh_nghia": ast_loi["ham_chua_dinh_nghia"],
                "vong_lap_vo_han": ast_loi["vong_lap_vo_han"],
                "code_chet": ast_loi["code_chet"],
                "import_khong_dung": ast_loi["import_khong_dung"],
                "o_n2": ast_loi["o_n2"],
            }
        except Exception as e:
            _ghi_log("loi", f"AST lỗi: {e}")

    ket_qua["luong_du_lieu"] = _phan_tich_luong_du_lieu(code, ket_qua["bien_lien_quan"])
    ket_qua["luong_dieu_khien"] = _phan_tich_luong_dieu_khien(
        code, dong_bi_loi.get("so_dong") if dong_bi_loi else None)
    ket_qua["scope"] = _phan_tich_scope(code, ket_qua["bien_lien_quan"])
    ket_qua["dependency"] = _phan_tich_dependency(code, ket_qua["ham_chua"])
    ket_qua["import_"] = _phan_tich_import(code)
    ket_qua["da_loi"] = _phan_tich_da_loi(stderr)
    ket_qua["ngu_nghia"] = _phan_tich_ngu_nghia(code, ast_loi)
    ket_qua["hieu_nang"] = _phan_tich_hieu_nang(code, ast_loi)

    if code_cu and code:
        ket_qua["diff"] = _so_sanh_code(code_cu, code)

    nn_list = NGUYEN_NHAN_GOC.get(ket_qua["loai_loi"], [])
    ket_qua["nguyen_nhan_goc"] = nn_list[0] if nn_list else thong_tin.get("mo_ta", "")

    ket_qua["loi_lien_quan"] = QUAN_HE_NHAN_QUA.get(ket_qua["loai_loi"], [])
    ket_qua["gia_thuyet"] = _sinh_gia_thuyet(ket_qua["loai_loi"], code, dong_bi_loi, ast_loi)
    ket_qua["cach_sua"] = _de_xuat_cach_sua(ket_qua, thong_tin, code)
    ket_qua["test_case"] = _sinh_test_case(ket_qua["loai_loi"], code, dong_bi_loi)
    ket_qua["rui_ro"] = _danh_gia_rui_ro(ket_qua["loai_loi"], code, ket_qua["ham_chua"], ast_loi)

    ket_qua["fix_da_cap"] = _sinh_fix_da_cap(
        ket_qua["loai_loi"], code, dong_bi_loi, thong_tin)

    ket_qua["chat_luong"] = _cham_diem_chat_luong(code, ast_loi)

    ket_qua["flow_chart"] = _ve_flow_chart(
        code, dong_bi_loi.get("so_dong") if dong_bi_loi else None)

    return ket_qua


# ================================================================
# SINH PATCH
# ================================================================
def sinh_patch(code_cu, code_moi):
    return _sinh_patch(code_cu, code_moi)


# ================================================================
# CÁC HÀM PHỤ
# ================================================================
def tim_nguyen_nhan_goc(stderr):
    try:
        from dai_nao.doc_loi import doc_loi
        tt = doc_loi(stderr)
    except ImportError:
        return ""
    loai = tt.get("loai_loi", "")
    if not loai:
        return ""
    nn = NGUYEN_NHAN_GOC.get(loai, [])
    return nn[0] if nn else tt.get("mo_ta", "")


def lien_ket_loi(stderr):
    try:
        from dai_nao.doc_loi import doc_loi
        tt = doc_loi(stderr)
    except ImportError:
        return []
    return QUAN_HE_NHAN_QUA.get(tt.get("loai_loi", ""), [])


def de_xuat_cach_sua(stderr, code=None):
    return phan_tich(stderr, code).get("cach_sua", [])


def danh_gia_do_kho(stderr):
    try:
        from dai_nao.doc_loi import doc_loi
        return doc_loi(stderr).get("thoi_gian_sua", "trung_binh")
    except ImportError:
        return "trung_binh"


def cham_diem_code(code):
    ast_loi = _phan_tich_ast(code) if code else None
    return _cham_diem_chat_luong(code, ast_loi)


# ================================================================
# LƯU PHÂN TÍCH VÀO KHO 2
# ================================================================
def luu_phan_tich(ket_qua):
    if not ket_qua or not ket_qua.get("co_loi"):
        return False
    try:
        from dai_nao.ghi_nho import luu_lich_su_hoc
        luu_lich_su_hoc({
            "loai": "phan_tich_loi",
            "loai_loi": ket_qua.get("loai_loi"),
            "nguyen_nhan_goc": ket_qua.get("nguyen_nhan_goc"),
            "dong_bi_loi": ket_qua.get("dong_bi_loi"),
            "cach_sua": ket_qua.get("cach_sua"),
            "rui_ro": ket_qua.get("rui_ro"),
            "chat_luong": ket_qua.get("chat_luong"),
            "thoi_gian": int(time.time()),
        })
        return True
    except Exception as e:
        _ghi_log("loi", f"Không lưu được phân tích: {e}")
        return False


# ================================================================
# TÓM TẮT CHO UI
# ================================================================
def tom_tat(ket_qua):
    if not ket_qua or not ket_qua.get("co_loi"):
        return ""

    phan = []
    phan.append(f"🔴 Lỗi: {ket_qua.get('loai_loi', 'Không rõ')}")
    phan.append(f"📖 Ngôn ngữ: {ket_qua.get('ngon_ngu', 'Không rõ')}")
    phan.append(f"🎯 Nguyên nhân: {ket_qua.get('nguyen_nhan_goc', '')}")

    dong = ket_qua.get("dong_bi_loi")
    if dong:
        phan.append(f"📍 Dòng {dong.get('so_dong')}: {dong.get('noi_dung', '').strip()}")

    ham = ket_qua.get("ham_chua")
    if ham:
        phan.append(f"🔧 Trong hàm: {ham.get('ten_ham', '')}()")

    cach_sua = ket_qua.get("cach_sua", [])
    if cach_sua:
        phan.append("💡 Cách sửa:")
        for i, c in enumerate(cach_sua[:3], 1):
            phan.append(f"  {i}. {c}")

    gt = ket_qua.get("gia_thuyet", [])
    if gt:
        phan.append("🔍 Giả thuyết:")
        for i, g in enumerate(gt[:3], 1):
            phan.append(f"  {i}. [{g.get('xac_suat')}] {g.get('gia_thuyet')}")

    test = ket_qua.get("test_case", [])
    if test:
        phan.append("🧪 Test:")
        phan.append("  " + test[0].replace("\n", "\n  "))

    rr = ket_qua.get("rui_ro", {})
    if rr.get("muc_do"):
        phan.append(f"⚠️ Rủi ro sửa: {rr['muc_do']} — {rr.get('ly_do', '')}")

    cl = ket_qua.get("chat_luong", {})
    if cl.get("diem") is not None:
        phan.append(f"📊 Điểm code: {cl['diem']}/10")

    fc = ket_qua.get("flow_chart", "")
    if fc:
        phan.append("📈 Luồng:")
        phan.append("  " + fc.replace("\n", "\n  "))

    return "\n".join(phan)


def tom_tat_ngan(ket_qua):
    if not ket_qua or not ket_qua.get("co_loi"):
        return ""
    return (f"🔴 {ket_qua.get('loai_loi')} @ dòng "
            f"{ket_qua.get('dong_bi_loi', {}).get('so_dong', '?')}: "
            f"{ket_qua.get('nguyen_nhan_goc', '')[:60]}")
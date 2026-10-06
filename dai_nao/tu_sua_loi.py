"""
tu_sua_loi.py - Tự sửa lỗi có trong từ điển Rồng Thần.

Nhiệm vụ:
    - tu_sua_loi(code, stderr, ngon_ngu): sửa code dựa trên lỗi.
    - Thu thập cách sửa từ 3 nguồn:
        1. Từ điển lỗi kho 2 (ưu tiên cao).
        2. Mẫu sửa có sẵn trong file này.
        3. Cách sửa tự động theo loại lỗi (regex).

Quy tắc:
    - Chỉ sửa lỗi có trong từ điển hoặc có mẫu sửa.
    - Không đoán bừa. Nếu không chắc → trả None.
    - Luôn giữ code gốc để so sánh.
    - Ghi log mỗi lần sửa.

Trả về:
    {
        thanh_cong: bool,
        code_moi: str,       # Code đã sửa (nếu thành công)
        so_dong_sua: int,    # Số dòng đã sửa
        cach_sua: str,       # Mô tả cách sửa
        nguon: str,          # "tu_dien" | "mau" | "tu_dong"
        loi_con_lai: str,    # Lỗi còn lại sau khi sửa (nếu có)
    }

Tầng dữ liệu: dai_nao/ghi_nho.py
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
# MẪU SỬA TỰ ĐỘNG THEO LOẠI LỖI
# Mỗi mẫu: (regex tìm, hàm thay thế / chuỗi thay thế, mô tả)
# ================================================================
MAU_SUA = {
    # ------------------------------------------------------------
    # Python
    # ------------------------------------------------------------
    "NameError": [
        # print(x) khi x chưa gán → thêm x = 0 trước
        (
            r"^(\s*)(print\s*\(\s*)([a-zA-Z_]\w*)(\s*\))",
            None,  # xử lý động
            "Thêm biến khai báo trước print()",
        ),
    ],
    "ZeroDivisionError": [
        # a / b → kiểm tra mẫu trước
        (
            r"(\w+)\s*/\s*(\w+)",
            r"(\2 if \2 != 0 else 0)",
            "Bọc phép chia bằng điều kiện mẫu != 0",
        ),
    ],
    "KeyError": [
        # d[key] → d.get(key)
        (
            r"(\w+)\[['\"](\w+)['\"]\]",
            r"\1.get('\2')",
            "Đổi dict[key] thành dict.get(key)",
        ),
    ],
    "IndexError": [
        # lst[i] → kiểm tra len trước
        (
            r"(\w+)\[(\d+)\]",
            None,  # xử lý động
            "Thêm kiểm tra len trước khi truy cập",
        ),
    ],
    "FileNotFoundError": [
        # open('file') → thêm kiểm tra os.path.exists
        (
            r"open\s*\(\s*(['\"][^'\"]+['\"])\s*\)",
            r"open(\1) if __import__('os').path.exists(\1) else None",
            "Kiểm tra file tồn tại trước khi mở",
        ),
    ],
    "RecursionError": [
        # def f(): ... f() ... → thêm điều kiện dừng
        (
            r"def\s+(\w+)\s*\(([^)]*)\):",
            None,  # xử lý động
            "Thêm điều kiện dừng cho đệ quy",
        ),
    ],
    "IndentationError": [
        # Dòng không thụt lề đúng
        (
            r"^(\s*)(if|for|while|def|class)\s+(.+):\s*\n(?!\s)",
            r"\1\2 \3:\n    pass",
            "Thêm pass sau dấu : nếu thiếu thân",
        ),
    ],
    "AttributeError": [
        # str.xyz() → giữ nguyên, cần biết object
        (
            r"(['\"]\w+['\"])\.(\w+)\s*\(",
            None,  # xử lý động
            "Kiểm tra thuộc tính có tồn tại không",
        ),
    ],
    "SyntaxError": [
        # print('abc' → print('abc')
        (
            r"(print\s*\(\s*['\"][^'\"]*['\"])(\s*)$",
            r"\1)",
            "Thêm dấu đóng ngoặc",
        ),
    ],
    "UnicodeDecodeError": [
        # open('file', 'r') → open('file', 'r', encoding='utf-8', errors='replace')
        (
            r"open\s*\(\s*(['\"][^'\"]+['\"])\s*,\s*(['\"]r['\"])\s*\)",
            r"open(\1, \2, encoding='utf-8', errors='replace')",
            "Thêm encoding='utf-8' và errors='replace'",
        ),
    ],
    "TypeError": [
        # int + str → ép kiểu
        (
            r"(['\"]\d+['\"])\s*\+\s*(\d+)",
            r"int(\1) + \2",
            "Ép chuỗi số thành int trước khi cộng",
        ),
        (
            r"(\d+)\s*\+\s*(['\"]\d+['\"])",
            r"\1 + int(\2)",
            "Ép chuỗi số thành int trước khi cộng",
        ),
    ],
    "ValueError": [
        # int(x) → try/except
        (
            r"(\w+)\s*=\s*int\s*\(([^)]+)\)",
            r"try:\n    \1 = int(\2)\nexcept ValueError:\n    \1 = 0",
            "Bọc int() trong try/except",
        ),
    ],

    # ------------------------------------------------------------
    # JavaScript
    # ------------------------------------------------------------
    "JS_ReferenceError": [
        (
            r"console\.log\((\w+)\)",
            r"let \1;\nconsole.log(\1);",
            "Khai báo biến trước khi dùng",
        ),
    ],
    "JS_TypeError": [
        # obj.foo → obj?.foo
        (
            r"(\w+)\.(\w+)",
            r"\1?.\2",
            "Dùng optional chaining",
        ),
    ],

    # ------------------------------------------------------------
    # Web / API
    # ------------------------------------------------------------
    "HTTP_429": [
        # requests.get(url) → thêm retry
        (
            r"(requests\.(?:get|post)\s*\([^)]+\))",
            r"\1  # Thêm retry với backoff",
            "Thêm retry cho 429",
        ),
    ],
    "API_Timeout": [
        (
            r"requests\.(get|post)\s*\(([^)]+)\)",
            r"requests.\1(\2, timeout=30)",
            "Thêm timeout=30 cho request",
        ),
    ],
}


# ================================================================
# SỬA ĐỘNG THEO LOẠI LỖI
# ================================================================
def _sua_dong_nameerror(code, thong_tin_loi):
    """
    Sửa NameError: tìm tên biến chưa khai báo, thêm khai báo trước dòng lỗi.
    """
    ten_bien = thong_tin_loi.get("ten_bien", "")
    if not ten_bien:
        return None

    cac_dong = code.split("\n")
    for i, dong in enumerate(cac_dong):
        if re.search(r"\b" + re.escape(ten_bien) + r"\b", dong) and \
           not re.search(re.escape(ten_bien) + r"\s*=", dong):
            # Thêm khai báo trước dòng này
            thut_le = len(dong) - len(dong.lstrip())
            khai_bao = " " * thut_le + f"{ten_bien} = None  # Tự sửa: khai báo biến"
            cac_dong.insert(i, khai_bao)
            return "\n".join(cac_dong)
    return None


def _sua_dong_indexerror(code, thong_tin_loi):
    """
    Sửa IndexError: bọc truy cập list trong if len.
    """
    cac_dong = code.split("\n")
    for i, dong in enumerate(cac_dong):
        # Tìm lst[số]
        khop = re.search(r"(\w+)\[(\d+)\]", dong)
        if khop:
            ten_list = khop.group(1)
            so_index = khop.group(2)
            thut_le = " " * (len(dong) - len(dong.lstrip()))
            # Bọc trong if
            dong_moi = dong.replace(
                f"{ten_list}[{so_index}]",
                f"{ten_list}[{so_index}] if {so_index} < len({ten_list}) else None"
            )
            cac_dong[i] = dong_moi
            return "\n".join(cac_dong)
    return None


def _sua_dong_recursionerror(code, thong_tin_loi):
    """
    Sửa RecursionError: thêm điều kiện dừng cho hàm đệ quy.
    """
    cac_dong = code.split("\n")
    for i, dong in enumerate(cac_dong):
        khop = re.match(r"^(\s*)def\s+(\w+)\s*\(([^)]*)\):", dong)
        if khop:
            thut_le = khop.group(1)
            ten_ham = khop.group(2)
            # Kiểm tra hàm có gọi chính nó không
            than_ham = "\n".join(cac_dong[i + 1:i + 20])
            if ten_ham in than_ham:
                # Thêm điều kiện dừng
                dong_dung = (
                    f"{thut_le}    if not {ten_ham}:  "
                    f"# Tự sửa: điều kiện dừng\n"
                    f"{thut_le}        return None"
                )
                cac_dong.insert(i + 1, dong_dung)
                return "\n".join(cac_dong)
    return None


def _sua_dong_attributeerror(code, thong_tin_loi):
    """
    Sửa AttributeError: bọc hasattr() trước khi gọi.
    """
    cac_dong = code.split("\n")
    for i, dong in enumerate(cac_dong):
        # Tìm obj.method()
        khop = re.search(r"(\w+)\.(\w+)\s*\(", dong)
        if khop:
            ten_obj = khop.group(1)
            ten_method = khop.group(2)
            # Chỉ sửa nếu object không phải self
            if ten_obj != "self":
                thut_le = " " * (len(dong) - len(dong.lstrip()))
                dong_moi = (
                    f"{thut_le}if hasattr({ten_obj}, '{ten_method}'):\n"
                    f"{thut_le}    {dong.strip()}"
                )
                cac_dong[i] = dong_moi
                return "\n".join(cac_dong)
    return None


# Bảng điều phối sửa động
SUA_DONG = {
    "NameError": _sua_dong_nameerror,
    "IndexError": _sua_dong_indexerror,
    "RecursionError": _sua_dong_recursionerror,
    "AttributeError": _sua_dong_attributeerror,
}


# ================================================================
# SỬA BẰNG MẪU REGEX
# ================================================================
def _sua_bang_mau(code, loai_loi):
    """
    Sửa code bằng mẫu regex có sẵn.
    Trả về (code_moi, mo_ta) hoặc (None, "").
    """
    danh_sach_mau = MAU_SUA.get(loai_loi, [])
    for mau in danh_sach_mau:
        regex, thay_the, mo_ta = mau
        if thay_the is None:
            continue  # Mẫu động, bỏ qua
        try:
            code_moi = re.sub(regex, thay_the, code, count=1)
            if code_moi != code:
                return code_moi, mo_ta
        except re.error:
            continue
    return None, ""


# ================================================================
# TRA TỪ ĐIỂN LỖI KHO 2
# ================================================================
def _sua_bang_tu_dien(code, loai_loi):
    """
    Tra từ điển lỗi kho 2, lấy cách sửa mẫu.
    Trả về (code_moi, mo_ta) hoặc (None, "").
    """
    try:
        from dai_nao.doc_loi import tra_tu_dien_loi
        muc = tra_tu_dien_loi(loai_loi)
    except ImportError:
        return None, ""

    if not muc:
        return None, ""

    # Từ điển có thể có "cach_sua_mau" (regex + replacement)
    mau = muc.get("cach_sua_mau") or muc.get("code_sua_mau")
    if not mau:
        return None, ""

    # Nếu là cặp (regex, thay_thế)
    if isinstance(mau, dict):
        regex = mau.get("regex")
        thay_the = mau.get("thay_the")
        if regex and thay_the:
            try:
                code_moi = re.sub(regex, thay_the, code, count=1)
                if code_moi != code:
                    return code_moi, muc.get("mo_ta", "Từ từ điển lỗi")
            except re.error:
                pass

    return None, ""


# ================================================================
# SỬA ĐỘNG
# ================================================================
def _sua_dong(code, loai_loi, thong_tin_loi):
    """
    Sửa code bằng hàm động (theo loại lỗi).
    Trả về (code_moi, mo_ta) hoặc (None, "").
    """
    ham_sua = SUA_DONG.get(loai_loi)
    if not ham_sua:
        return None, ""

    try:
        code_moi = ham_sua(code, thong_tin_loi)
        if code_moi and code_moi != code:
            return code_moi, f"Sửa động cho {loai_loi}"
    except Exception as e:
        _ghi_log("loi", f"Sửa động lỗi: {e}")

    return None, ""


# ================================================================
# ĐẾM SỐ DÒNG THAY ĐỔI
# ================================================================
def _dem_dong_sua(code_cu, code_moi):
    """Đếm số dòng thay đổi giữa code cũ và mới."""
    if not code_cu or not code_moi:
        return 0

    dong_cu = code_cu.split("\n")
    dong_moi = code_moi.split("\n")

    try:
        import difflib
        diff = list(difflib.unified_diff(dong_cu, dong_moi, lineterm="", n=0))
    except Exception:
        return abs(len(dong_moi) - len(dong_cu))

    so_dong = 0
    for d in diff:
        if (d.startswith("+") or d.startswith("-")) and \
           not d.startswith("+++") and not d.startswith("---"):
            so_dong += 1
    return so_dong


# ================================================================
# KIỂM TRA LỖI CÒN LẠI
# ================================================================
def _kiem_tra_loi_con_lai(code_moi, ngon_ngu="python"):
    """
    Chạy code để kiểm tra còn lỗi không.
    Chỉ hỗ trợ Python (dùng ast.parse).
    """
    if not code_moi or ngon_ngu.lower() != "python":
        return ""

    try:
        import ast
        ast.parse(code_moi)
        return ""  # Không còn lỗi cú pháp
    except SyntaxError as e:
        return f"Dòng {e.lineno}: {e.msg}"


# ================================================================
# HÀM CHÍNH
# ================================================================
def tu_sua_loi(code, stderr, ngon_ngu="python"):
    """
    Tự sửa lỗi dựa trên stderr.

    code: code gốc.
    stderr: chuỗi lỗi từ sandbox.
    ngon_ngu: "python" | "html" | "javascript" | "java"...

    Trả về dict đầy đủ.
    """
    ket_qua = {
        "thanh_cong": False,
        "code_moi": code,
        "so_dong_sua": 0,
        "cach_sua": "",
        "nguon": "",
        "loi_con_lai": "",
    }

    if not code or not stderr:
        return ket_qua

    # 1. Đọc lỗi
    try:
        from dai_nao.doc_loi import doc_loi
        thong_tin_loi = doc_loi(stderr)
    except ImportError:
        _ghi_log("loi", "doc_loi.py chưa có.")
        return ket_qua

    if not thong_tin_loi.get("co_loi"):
        return ket_qua

    loai_loi = thong_tin_loi.get("loai_loi", "")
    if not loai_loi:
        return ket_qua

    _ghi_log("dai-nao", f"Tự sửa lỗi loại: {loai_loi}")

    # 2. Thử 3 nguồn sửa theo thứ tự ưu tiên
    code_moi = None
    cach_sua = ""
    nguon = ""

    # Nguồn 1: Từ điển lỗi kho 2 (ưu tiên cao)
    code_moi, cach_sua = _sua_bang_tu_dien(code, loai_loi)
    if code_moi:
        nguon = "tu_dien"

    # Nguồn 2: Mẫu regex có sẵn
    if not code_moi:
        code_moi, cach_sua = _sua_bang_mau(code, loai_loi)
        if code_moi:
            nguon = "mau"

    # Nguồn 3: Sửa động theo loại lỗi
    if not code_moi:
        code_moi, cach_sua = _sua_dong(code, loai_loi, thong_tin_loi)
        if code_moi:
            nguon = "tu_dong"

    # 3. Không sửa được → trả code gốc
    if not code_moi:
        _ghi_log("dai-nao", f"Không sửa được lỗi {loai_loi} — cần Tiểu não.")
        return ket_qua

    # 4. Đếm số dòng đã sửa
    so_dong_sua = _dem_dong_sua(code, code_moi)

    # 5. Kiểm tra lỗi còn lại
    loi_con_lai = _kiem_tra_loi_con_lai(code_moi, ngon_ngu)

    # 6. Trả kết quả
    ket_qua.update({
        "thanh_cong": True,
        "code_moi": code_moi,
        "so_dong_sua": so_dong_sua,
        "cach_sua": cach_sua,
        "nguon": nguon,
        "loi_con_lai": loi_con_lai,
    })

    _ghi_log(
        "dai-nao",
        f"Tự sửa thành công: {so_dong_sua} dòng, nguồn={nguon}",
    )

    return ket_qua


# ================================================================
# LƯU LỊCH SỬ SỬA
# ================================================================
def luu_lich_su_sua(loai_loi, ket_qua_sua, code_goc, code_moi):
    """Lưu lịch sử sửa lỗi vào kho 2."""
    if not ket_qua_sua or not ket_qua_sua.get("thanh_cong"):
        return False

    try:
        from dai_nao.ghi_nho import luu_lich_su_hoc
        luu_lich_su_hoc({
            "loai": "tu_sua_loi",
            "loai_loi": loai_loi,
            "nguon": ket_qua_sua.get("nguon"),
            "cach_sua": ket_qua_sua.get("cach_sua"),
            "so_dong_sua": ket_qua_sua.get("so_dong_sua"),
            "code_goc": code_goc[:500],
            "code_moi": code_moi[:500],
            "thoi_gian": int(time.time()),
        })
        return True
    except Exception as e:
        _ghi_log("loi", f"Không lưu được lịch sử sửa: {e}")
        return False


# ================================================================
# HÀM PHỤ: CHỈ LẤY CÁCH SỬA
# ================================================================
def lay_cach_sua(loai_loi):
    """
    Lấy danh sách cách sửa cho loại lỗi (không sửa code).
    Trả về list mô tả.
    """
    ket_qua = []

    # Từ mẫu có sẵn
    for mau in MAU_SUA.get(loai_loi, []):
        if len(mau) >= 3:
            ket_qua.append(mau[2])

    # Từ từ điển
    try:
        from dai_nao.doc_loi import tra_tu_dien_loi
        muc = tra_tu_dien_loi(loai_loi)
        if muc:
            goi_y = muc.get("goi_y", [])
            if isinstance(goi_y, list):
                ket_qua.extend(goi_y)
    except ImportError:
        pass

    return ket_qua


# ================================================================
# HÀM PHỤ: KIỂM TRA CÓ SỬA ĐƯỢC KHÔNG
# ================================================================
def co_the_sua(loai_loi):
    """Kiểm tra loại lỗi có mẫu sửa tự động không."""
    if loai_loi in MAU_SUA:
        return True
    if loai_loi in SUA_DONG:
        return True
    try:
        from dai_nao.doc_loi import tra_tu_dien_loi
        return tra_tu_dien_loi(loai_loi) is not None
    except ImportError:
        return False


# ================================================================
# HÀM PHỤ: THỐNG KÊ
# ================================================================
def thong_ke_mau_sua():
    """Đếm số mẫu sửa theo loại lỗi."""
    return {loai: len(mau) for loai, mau in MAU_SUA.items()}


def lay_tat_ca_loai_co_mau():
    """Trả danh sách loại lỗi có mẫu sửa."""
    return sorted(set(list(MAU_SUA.keys()) + list(SUA_DONG.keys())))
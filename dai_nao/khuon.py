"""
khuon.py - Ép model trả về đúng format Rồng Thần.

Nhiệm vụ:
    - lay_khuon(loai_task): trả về khuôn JSON cho loại task.
    - tao_prompt_khuon(khuon): tạo prompt ép model trả theo khuôn.
    - kiem_tra_khuon(du_lieu, khuon): kiểm tra du_lieu có đúng khuôn không.
    - sua_khuon(du_lieu, khuon): cố gắng sửa du_lieu cho khớp khuôn.

Khuôn dùng để:
    - Ép model trả về format cố định.
    - Chống model tự do viết lung tung.
    - Đảm bảo model A và model B trả giống nhau.

Các khuôn có sẵn:
    - "lam_web"     — dự án web nhiều file.
    - "lam_python"  — dự án Python nhiều file.
    - "viet_van"    — viết văn dài.
    - "sua_bug"     — sửa lỗi code.
    - "giai_toan"   — giải toán.

Tầng dữ liệu: (không có — thuần logic)
"""

import re
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
# KHUÔN — LOẠI TASK LÀM WEB
# ================================================================
KHUON_LAM_WEB = {
    "ten": "lam_web",
    "mo_ta": "Khuôn dự án web nhiều file",
    "cac_truong": {
        "id_du_an": {"kieu": "str", "bat_buoc": True, "mo_ta": "Mã dự án (VD web-pokemon)"},
        "yeu_cau_goc": {"kieu": "str", "bat_buoc": True, "mo_ta": "Yêu cầu gốc của user"},
        "ngon_ngu": {"kieu": "str", "bat_buoc": True, "mo_ta": "HTML / JavaScript / Python"},
        "ds_file": {
            "kieu": "list",
            "bat_buoc": True,
            "mo_ta": "Danh sách file cần làm",
            "mau_item": {
                "ten_file": "str",
                "vai_tro": "str",
                "phu_thuoc": "list[str]",
                "mo_ta": "str",
            },
        },
        "quy_uoc_chung": {
            "kieu": "dict",
            "bat_buoc": False,
            "mo_ta": "Quy ước dự án (camelCase, không dùng framework...)",
        },
    },
}

# ================================================================
# KHUÔN — LOẠI TASK LÀM PYTHON
# ================================================================
KHUON_LAM_PYTHON = {
    "ten": "lam_python",
    "mo_ta": "Khuôn dự án Python nhiều file",
    "cac_truong": {
        "id_du_an": {"kieu": "str", "bat_buoc": True},
        "yeu_cau_goc": {"kieu": "str", "bat_buoc": True},
        "ds_file": {
            "kieu": "list",
            "bat_buoc": True,
            "mau_item": {
                "ten_file": "str",
                "vai_tro": "str",
                "import_tu": "list[str]",
            },
        },
    },
}

# ================================================================
# KHUÔN — LOẠI TASK VIẾT VĂN
# ================================================================
KHUON_VIET_VAN = {
    "ten": "viet_van",
    "mo_ta": "Khuôn viết văn dài",
    "cac_truong": {
        "loai_van": {"kieu": "str", "bat_buoc": True, "mo_ta": "Nghị luận / miêu tả / tự sự"},
        "chu_de": {"kieu": "str", "bat_buoc": True},
        "do_dai": {"kieu": "int", "bat_buoc": True, "mo_ta": "Số chữ yêu cầu"},
        "dan_y": {
            "kieu": "dict",
            "bat_buoc": False,
            "mo_ta": "Mở bài / thân bài / kết bài",
        },
        "noi_dung": {"kieu": "str", "bat_buoc": True, "mo_ta": "Toàn bộ bài văn"},
    },
}

# ================================================================
# KHUÔN — LOẠI TASK SỬA BUG
# ================================================================
KHUON_SUA_BUG = {
    "ten": "sua_bug",
    "mo_ta": "Khuôn sửa lỗi code",
    "cac_truong": {
        "loai_loi": {"kieu": "str", "bat_buoc": True, "mo_ta": "NameError / TypeError..."},
        "dong_loi": {"kieu": "int", "bat_buoc": False},
        "code_goc": {"kieu": "str", "bat_buoc": True},
        "code_da_sua": {"kieu": "str", "bat_buoc": True},
        "cach_sua": {"kieu": "str", "bat_buoc": True, "mo_ta": "Mô tả cách sửa"},
        "dong_sua": {"kieu": "list", "bat_buoc": False, "mo_ta": "Các dòng đã sửa"},
    },
}

# ================================================================
# KHUÔN — LOẠI TASK GIẢI TOÁN
# ================================================================
KHUON_GIAI_TOAN = {
    "ten": "giai_toan",
    "mo_ta": "Khuôn giải toán",
    "cac_truong": {
        "loai_toan": {"kieu": "str", "bat_buoc": True, "mo_ta": "số học / đại số / hình học"},
        "de_bai": {"kieu": "str", "bat_buoc": True},
        "cach_giai": {"kieu": "str", "bat_buoc": True, "mo_ta": "Các bước giải"},
        "ket_qua": {"kieu": "str", "bat_buoc": True},
        "code_minh_hoa": {"kieu": "str", "bat_buoc": False, "mo_ta": "Code Python minh họa"},
    },
}

# ================================================================
# BẢNG KHUÔN
# ================================================================
BANG_KHUON = {
    "lam_web": KHUON_LAM_WEB,
    "lam_python": KHUON_LAM_PYTHON,
    "viet_van": KHUON_VIET_VAN,
    "sua_bug": KHUON_SUA_BUG,
    "giai_toan": KHUON_GIAI_TOAN,
}


# ================================================================
# LẤY KHUÔN
# ================================================================
def lay_khuon(loai_task):
    """Lấy khuôn theo loại task."""
    if not loai_task:
        return None
    return BANG_KHUON.get(loai_task)


def lay_tat_ca_loai_khuon():
    """Trả về danh sách loại khuôn có sẵn."""
    return list(BANG_KHUON.keys())


# ================================================================
# TẠO PROMPT ÉP MODEL TRẢ THEO KHUÔN
# ================================================================
def tao_prompt_khuon(khuon, noi_dung_goc=""):
    """
    Tạo prompt ép model trả về đúng khuôn JSON.

    khuon: dict khuôn (lấy từ lay_khuon).
    noi_dung_goc: yêu cầu gốc của user (nếu có).
    """
    if not khuon:
        return ""

    ten_khuon = khuon.get("ten", "")
    mo_ta = khuon.get("mo_ta", "")
    cac_truong = khuon.get("cac_truong", {})

    # Xây schema mẫu
    schema_mau = _tao_schema_mau(cac_truong)

    prompt = f"""Bạn là trợ lý phân tích dự án. Nhiệm vụ: trả về JSON theo ĐÚNG khuôn sau.

═══════════════════════════════════════════
LOẠI KHUÔN: {ten_khuon}
MÔ TẢ: {mo_ta}
═══════════════════════════════════════════

{f'YÊU CẦU GỐC CỦA USER:{chr(10)}{noi_dung_goc}{chr(10)}' if noi_dung_goc else ''}

═══════════════════════════════════════════
KHUÔN JSON (BẮT BUỘC — KHÔNG THÊM TRƯỜNG KHÁC):
═══════════════════════════════════════════
{schema_mau}

═══════════════════════════════════════════
QUY TẮC:
═══════════════════════════════════════════
1. Trả về CHỈ JSON — không có text giải thích.
2. ĐÚNG các trường trong khuôn — KHÔNG thêm trường khác.
3. Các trường "bat_buoc: true" — PHẢI có, không được rỗng.
4. Đúng kiểu dữ liệu (str, int, list, dict).
5. Không bịa dữ liệu — nếu không biết → để "".

CHỈ TRẢ VỀ JSON."""

    return prompt


def _tao_schema_mau(cac_truong, do_sau=0):
    """Tạo schema mẫu JSON từ các trường."""
    if not cac_truong or do_sau > 3:
        return "{}"

    indent = "  " * (do_sau + 1)
    dong = ["{"]
    cac_muc = list(cac_truong.items())

    for i, (ten, thong_tin) in enumerate(cac_muc):
        kieu = thong_tin.get("kieu", "str")
        bat_buoc = thong_tin.get("bat_buoc", False)
        mo_ta = thong_tin.get("mo_ta", "")

        dau_phay = "," if i < len(cac_muc) - 1 else ""
        chu_thich = f"  // {mo_ta}" if mo_ta else ""
        chu_thich += "  (BẮT BUỘC)" if bat_buoc else ""

        if kieu == "str":
            gia_tri = '""'
        elif kieu == "int":
            gia_tri = "0"
        elif kieu == "list":
            mau_item = thong_tin.get("mau_item")
            if mau_item:
                item_str = _tao_schema_mau(mau_item, do_sau + 2)
                gia_tri = f"[{chr(10)}{indent}  {item_str}{chr(10)}{indent}]"
            else:
                gia_tri = "[]"
        elif kieu == "dict":
            gia_tri = "{}"
        else:
            gia_tri = "null"

        dong.append(f'{indent}"{ten}": {gia_tri}{dau_phay}{chu_thich}')

    dong.append("  " * do_sau + "}")
    return chr(10).join(dong)


# ================================================================
# KIỂM TRA KHUÔN
# ================================================================
def kiem_tra_khuon(du_lieu, khuon):
    """
    Kiểm tra du_lieu có đúng khuôn không.

    Trả về: (True/False, ly_do)
    """
    if not du_lieu or not isinstance(du_lieu, dict):
        return False, "Dữ liệu không phải dict."

    if not khuon or not isinstance(khuon, dict):
        return False, "Khuôn không hợp lệ."

    cac_truong = khuon.get("cac_truong", {})
    if not cac_truong:
        return False, "Khuôn rỗng."

    thieu = []
    sai_kieu = []

    for ten, thong_tin in cac_truong.items():
        bat_buoc = thong_tin.get("bat_buoc", False)
        kieu = thong_tin.get("kieu", "str")

        # Kiểm tra tồn tại
        if ten not in du_lieu:
            if bat_buoc:
                thieu.append(ten)
            continue

        gia_tri = du_lieu[ten]

        # Kiểm tra bắt buộc không được rỗng
        if bat_buoc and gia_tri in (None, "", [], {}):
            thieu.append(ten)
            continue

        # Kiểm tra kiểu
        if kieu == "str" and not isinstance(gia_tri, str):
            sai_kieu.append(f"{ten} phải là str")
        elif kieu == "int" and not isinstance(gia_tri, int):
            sai_kieu.append(f"{ten} phải là int")
        elif kieu == "list" and not isinstance(gia_tri, list):
            sai_kieu.append(f"{ten} phải là list")
        elif kieu == "dict" and not isinstance(gia_tri, dict):
            sai_kieu.append(f"{ten} phải là dict")

    if thieu:
        return False, f"Thiếu trường bắt buộc: {', '.join(thieu)}"
    if sai_kieu:
        return False, "Sai kiểu: " + " | ".join(sai_kieu)

    return True, ""


# ================================================================
# SỬA KHUÔN
# ================================================================
def sua_khuon(du_lieu, khuon):
    """
    Cố gắng sửa du_lieu cho khớp khuôn:
        - Thêm trường thiếu với giá trị rỗng.
        - Ép kiểu nếu có thể.

    Trả về dict đã sửa.
    """
    if not du_lieu or not isinstance(du_lieu, dict):
        return {}

    if not khuon or not isinstance(khuon, dict):
        return du_lieu

    cac_truong = khuon.get("cac_truong", {})
    ket_qua = dict(du_lieu)

    for ten, thong_tin in cac_truong.items():
        kieu = thong_tin.get("kieu", "str")

        if ten not in ket_qua or ket_qua[ten] is None:
            # Gán giá trị mặc định
            if kieu == "str":
                ket_qua[ten] = ""
            elif kieu == "int":
                ket_qua[ten] = 0
            elif kieu == "list":
                ket_qua[ten] = []
            elif kieu == "dict":
                ket_qua[ten] = {}
            continue

        # Ép kiểu nếu sai
        gia_tri = ket_qua[ten]
        if kieu == "str" and not isinstance(gia_tri, str):
            ket_qua[ten] = str(gia_tri)
        elif kieu == "int" and not isinstance(gia_tri, int):
            try:
                ket_qua[ten] = int(gia_tri)
            except (ValueError, TypeError):
                ket_qua[ten] = 0
        elif kieu == "list" and not isinstance(gia_tri, list):
            if isinstance(gia_tri, str):
                ket_qua[ten] = [gia_tri]
            else:
                ket_qua[ten] = []
        elif kieu == "dict" and not isinstance(gia_tri, dict):
            ket_qua[ten] = {}

    return ket_qua


# ================================================================
# TRÍCH JSON TỪ RESPONSE MODEL
# ================================================================
def trich_json_tu_response(chuoi):
    """
    Trích JSON từ response model (có thể có markdown ```json ... ```).
    Trả về dict/list hoặc None.
    """
    if not chuoi:
        return None

    chuoi = chuoi.strip()

    # 1. Parse trực tiếp
    try:
        return json.loads(chuoi)
    except (json.JSONDecodeError, ValueError):
        pass

    # 2. Bỏ markdown ```json ... ```
    mau_markdown = r"```(?:json)?\s*([\s\S]*?)```"
    khop = re.search(mau_markdown, chuoi)
    if khop:
        try:
            return json.loads(khop.group(1).strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # 3. Tìm { ... } đầu tiên
    vi_tri_dau = chuoi.find("{")
    vi_tri_cuoi = chuoi.rfind("}")
    if vi_tri_dau >= 0 and vi_tri_cuoi > vi_tri_dau:
        chuoi_json = chuoi[vi_tri_dau:vi_tri_cuoi + 1]
        try:
            return json.loads(chuoi_json)
        except (json.JSONDecodeError, ValueError):
            pass

    # 4. Sửa lỗi phổ biến (comment, dấu phẩy cuối)
    chuoi_clean = re.sub(r"//[^\n]*", "", chuoi)
    chuoi_clean = re.sub(r",(\s*[}\]])", r"\1", chuoi_clean)
    vi_tri_dau = chuoi_clean.find("{")
    vi_tri_cuoi = chuoi_clean.rfind("}")
    if vi_tri_dau >= 0 and vi_tri_cuoi > vi_tri_dau:
        try:
            return json.loads(chuoi_clean[vi_tri_dau:vi_tri_cuoi + 1])
        except (json.JSONDecodeError, ValueError):
            pass

    return None


# ================================================================
# HÀM PHỤ
# ================================================================
def lay_ten_khuon(khuon):
    """Lấy tên khuôn."""
    if not khuon:
        return ""
    return khuon.get("ten", "")


def so_truong_khuon(khuon):
    """Đếm số trường trong khuôn."""
    if not khuon:
        return 0
    return len(khuon.get("cac_truong", {}))


def so_truong_bat_buoc(khuon):
    """Đếm số trường bắt buộc trong khuôn."""
    if not khuon:
        return 0
    cac_truong = khuon.get("cac_truong", {})
    return sum(1 for t in cac_truong.values() if t.get("bat_buoc", False))
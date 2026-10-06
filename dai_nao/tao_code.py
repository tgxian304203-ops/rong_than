"""
tao_code.py - Ghép code từ node cây quyết định Rồng Thần.

Nhiệm vụ:
    - tao_code_tu_node(node, yeu_to, noi_dung): tạo code từ 1 node.
    - ghep_nhieu_node(danh_sach_node): ghép nhiều node thành 1 file.
    - thay_bien_trong_code(code, bien_dict): thay biến mẫu bằng giá trị thật.
    - boc_code_voi_khung(code, ngon_ngu): bọc code với khung template.

Quy tắc:
    - Code mẫu có placeholder: {{ten_bien}}, {{gia_tri}}...
    - Node cha + node con có thể ghép lại.
    - Không sửa code gốc trong node.
    - Sinh code sạch, có comment rõ ràng.

Trả về:
    {
        thanh_cong: bool,
        code: str,
        ngon_ngu: str,
        so_node: int,
        bien_da_thay: list,
        loi: str?,
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
# HẰNG SỐ
# ================================================================
MAU_BIEN = r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}"


# ================================================================
# LẤY THUỘC TÍNH NODE
# ================================================================
def _lay(node, ten_truong, mac_dinh=None):
    """Lấy thuộc tính node (Nut object hoặc dict)."""
    if node is None:
        return mac_dinh
    if isinstance(node, dict):
        return node.get(ten_truong, mac_dinh)
    return getattr(node, ten_truong, mac_dinh)


# ================================================================
# TRÍCH BIẾN TỪ CODE MẪU
# ================================================================
def _trich_bien(code):
    """Trích danh sách tên biến placeholder {{ten_bien}} từ code."""
    if not code:
        return []
    return list(dict.fromkeys(re.findall(MAU_BIEN, code)))


# ================================================================
# THAY BIẾN TRONG CODE
# ================================================================
def thay_bien_trong_code(code, bien_dict):
    """
    Thay các placeholder {{ten_bien}} bằng giá trị thực.

    code: chuỗi code có placeholder.
    bien_dict: dict { ten_bien: gia_tri }.

    Trả về: (code_moi, list_bien_da_thay, list_bien_thieu).
    """
    if not code:
        return code, [], []

    bien_dict = bien_dict or {}
    bien_da_thay = []
    bien_thieu = []

    def _thay(match):
        ten = match.group(1)
        if ten in bien_dict:
            gia_tri = bien_dict[ten]
            if gia_tri is None:
                gia_tri = ""
            bien_da_thay.append(ten)
            return str(gia_tri)
        bien_thieu.append(ten)
        return match.group(0)  # giữ nguyên nếu thiếu

    code_moi = re.sub(MAU_BIEN, _thay, code)
    return code_moi, list(dict.fromkeys(bien_da_thay)), list(dict.fromkeys(bien_thieu))


# ================================================================
# TRÍCH BIẾN TỪ 5 YẾU TỐ
# ================================================================
def _bien_tu_yeu_to(yeu_to, noi_dung):
    """
    Tạo dict giá trị biến từ 5 yếu tố + nội dung.
    Dùng để thay placeholder.
    """
    yeu_to = yeu_to or {}
    bien = {}

    # Từ 5 yếu tố
    if yeu_to.get("hanh_dong"):
        bien["hanh_dong"] = yeu_to["hanh_dong"]
    if yeu_to.get("doi_tuong"):
        bien["doi_tuong"] = yeu_to["doi_tuong"]
    if yeu_to.get("thuoc_tinh"):
        bien["thuoc_tinh"] = yeu_to["thuoc_tinh"]
    if yeu_to.get("rang_buoc"):
        bien["rang_buoc"] = yeu_to["rang_buoc"]
    if yeu_to.get("ngu_canh"):
        bien["ngu_canh"] = yeu_to["ngu_canh"]

    # Từ nội dung
    if noi_dung:
        bien["noi_dung"] = noi_dung
        bien["tieu_de"] = noi_dung[:80]

    # Mặc định
    bien.setdefault("ten_ham", "ham_moi")
    bien.setdefault("ten_class", "ClassMoi")
    bien.setdefault("ten_file", "main")
    bien.setdefault("thoi_gian", str(int(time.time())))

    return bien


# ================================================================
# BỌC CODE VỚI KHUNG TEMPLATE
# ================================================================
KHUNG_TEMPLATE = {
    "python": {
        "dau": '"""\n{mo_ta}\n"""\n\n',
        "cuoi": "",
    },
    "html": {
        "dau": (
            "<!DOCTYPE html>\n"
            "<html lang=\"vi\">\n"
            "<head>\n"
            "    <meta charset=\"UTF-8\">\n"
            "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            "    <title>{tieu_de}</title>\n"
            "</head>\n"
            "<body>\n"
        ),
        "cuoi": "\n</body>\n</html>",
    },
    "javascript": {
        "dau": "// {mo_ta}\n\n",
        "cuoi": "",
    },
    "css": {
        "dau": "/* {mo_ta} */\n\n",
        "cuoi": "",
    },
}


def boc_code_voi_khung(code, ngon_ngu, mo_ta="", tieu_de=""):
    """
    Bọc code trong khung template (dành cho HTML).

    code: code gốc.
    ngon_ngu: "python" | "html" | "javascript" | "css".
    mo_ta: mô tả (cho comment).
    tieu_de: tiêu đề (cho HTML title).
    """
    if not code or not ngon_ngu:
        return code

    khung = KHUNG_TEMPLATE.get(ngon_ngu.lower())
    if not khung:
        return code

    dau = khung["dau"].format(mo_ta=mo_ta or "Code do Rồng Thần tạo", tieu_de=tieu_de or "Rồng Thần")
    cuoi = khung["cuoi"]

    return dau + code + cuoi


# ================================================================
# TẠO CODE TỪ 1 NODE
# ================================================================
def tao_code_tu_node(node, yeu_to=None, noi_dung=""):
    """
    Tạo code từ 1 node.

    node: Nut object hoặc dict.
    yeu_to: dict 5 yếu tố.
    noi_dung: nội dung task gốc.

    Trả về dict đầy đủ.
    """
    ket_qua = {
        "thanh_cong": False,
        "code": "",
        "ngon_ngu": "",
        "so_node": 0,
        "bien_da_thay": [],
        "bien_thieu": [],
        "loi": "",
    }

    if not node:
        ket_qua["loi"] = "Không có node."
        return ket_qua

    # Lấy code mẫu từ node
    hanh_dong = _lay(node, "hanh_dong", {}) or {}
    if not isinstance(hanh_dong, dict):
        hanh_dong = {"code": str(hanh_dong)}

    code_mau = hanh_dong.get("code") or _lay(node, "code") or ""
    ngon_ngu = hanh_dong.get("ngon_ngu") or _lay(node, "ngon_ngu") or "python"

    if not code_mau:
        ket_qua["loi"] = "Node không có code mẫu."
        return ket_qua

    # Chuẩn bị biến
    bien = _bien_tu_yeu_to(yeu_to, noi_dung)

    # Thay biến
    code_moi, bien_da_thay, bien_thieu = thay_bien_trong_code(code_mau, bien)

    # Bọc khung (nếu HTML và chưa có <html>)
    if ngon_ngu.lower() == "html" and "<html" not in code_moi.lower():
        mo_ta = _lay(node, "ten") or "Code HTML do Rồng Thần tạo"
        code_moi = boc_code_voi_khung(code_moi, "html", mo_ta, bien.get("tieu_de", ""))

    ket_qua.update({
        "thanh_cong": True,
        "code": code_moi,
        "ngon_ngu": ngon_ngu,
        "so_node": 1,
        "bien_da_thay": bien_da_thay,
        "bien_thieu": bien_thieu,
    })

    _ghi_log(
        "dai-nao",
        f"Tạo code từ node '{_lay(node, 'ten', _lay(node, 'id', ''))}' "
        f"({ngon_ngu}), thay {len(bien_da_thay)} biến",
    )

    return ket_qua


# ================================================================
# GHÉP NHIỀU NODE
# ================================================================
def ghep_nhieu_node(danh_sach_node, yeu_to=None, noi_dung=""):
    """
    Ghép nhiều node thành 1 file code.

    danh_sach_node: list Nut hoặc dict — theo thứ tự ghép.
    yeu_to: dict 5 yếu tố.
    noi_dung: nội dung task.

    Trả về dict đầy đủ.
    """
    ket_qua = {
        "thanh_cong": False,
        "code": "",
        "ngon_ngu": "",
        "so_node": 0,
        "bien_da_thay": [],
        "bien_thieu": [],
        "loi": "",
    }

    if not danh_sach_node:
        ket_qua["loi"] = "Danh sách node rỗng."
        return ket_qua

    bien = _bien_tu_yeu_to(yeu_to, noi_dung)
    cac_phan_code = []
    tat_ca_ngon_ngu = []
    tat_ca_bien_da_thay = []
    tat_ca_bien_thieu = []

    for node in danh_sach_node:
        if not node:
            continue

        hanh_dong = _lay(node, "hanh_dong", {}) or {}
        if not isinstance(hanh_dong, dict):
            continue

        code_mau = hanh_dong.get("code") or ""
        ngon_ngu = hanh_dong.get("ngon_ngu") or "python"

        if not code_mau:
            continue

        # Thay biến
        code_moi, da_thay, thieu = thay_bien_trong_code(code_mau, bien)

        tat_ca_ngon_ngu.append(ngon_ngu)
        tat_ca_bien_da_thay.extend(da_thay)
        tat_ca_bien_thieu.extend(thieu)

        # Thêm comment tên node
        ten_node = _lay(node, "ten", "") or _lay(node, "id", "")
        if ten_node:
            if ngon_ngu.lower() == "python":
                cac_phan_code.append(f"# --- {ten_node} ---")
            elif ngon_ngu.lower() in ("javascript", "js"):
                cac_phan_code.append(f"// --- {ten_node} ---")
            elif ngon_ngu.lower() == "css":
                cac_phan_code.append(f"/* --- {ten_node} --- */")
            elif ngon_ngu.lower() == "html":
                cac_phan_code.append(f"<!-- {ten_node} -->")

        cac_phan_code.append(code_moi)
        cac_phan_code.append("")

    if not cac_phan_code:
        ket_qua["loi"] = "Không node nào có code mẫu."
        return ket_qua

    code_tong = "\n".join(cac_phan_code)

    # Ngôn ngữ chính
    ngon_ngu_chinh = "python"
    if tat_ca_ngon_ngu:
        ngon_ngu_chinh = max(set(tat_ca_ngon_ngu), key=tat_ca_ngon_ngu.count)

    # Bọc khung HTML nếu cần
    if ngon_ngu_chinh.lower() == "html" and "<html" not in code_tong.lower():
        code_tong = boc_code_voi_khung(
            code_tong, "html",
            "Code HTML do Rồng Thần ghép từ nhiều node",
            bien.get("tieu_de", ""),
        )

    ket_qua.update({
        "thanh_cong": True,
        "code": code_tong,
        "ngon_ngu": ngon_ngu_chinh,
        "so_node": len(danh_sach_node),
        "bien_da_thay": list(dict.fromkeys(tat_ca_bien_da_thay)),
        "bien_thieu": list(dict.fromkeys(tat_ca_bien_thieu)),
    })

    _ghi_log(
        "dai-nao",
        f"Ghép {len(danh_sach_node)} node thành code {ngon_ngu_chinh}",
    )

    return ket_qua


# ================================================================
# TẠO CODE TỪ CẢ CÂY (node chính + nhánh con)
# ================================================================
def tao_code_tu_cay(node_goc, yeu_to=None, noi_dung=""):
    """
    Tạo code từ node gốc + tất cả node con có code mẫu.
    Duyệt BFS để ghép theo thứ tự tầng.

    Trả về dict như ghep_nhieu_node.
    """
    if not node_goc:
        return {"thanh_cong": False, "loi": "Không có node gốc."}

    danh_sach = []
    hang_doi = [node_goc]

    while hang_doi:
        node = hang_doi.pop(0)
        danh_sach.append(node)
        con = _lay(node, "nhanh_con", []) or []
        if isinstance(con, list):
            hang_doi.extend(con)

    return ghep_nhieu_node(danh_sach, yeu_to, noi_dung)


# ================================================================
# THAY BIẾN TRONG CODE HTML (thay text, id, class)
# ================================================================
def thay_bien_html(code, thay_the_dict):
    """
    Thay các thành phần trong HTML: id, class, text.

    thay_the_dict: dict
        {
            "id": {"cu": "moi"},
            "class": {"cu": "moi"},
            "text": {"cu": "moi"},
        }
    """
    if not code or not thay_the_dict:
        return code

    code_moi = code

    # Thay id
    for cu, moi in (thay_the_dict.get("id") or {}).items():
        code_moi = re.sub(
            r'id=["\']' + re.escape(cu) + r'["\']',
            f'id="{moi}"',
            code_moi,
        )

    # Thay class
    for cu, moi in (thay_the_dict.get("class") or {}).items():
        code_moi = re.sub(
            r'class=["\']' + re.escape(cu) + r'["\']',
            f'class="{moi}"',
            code_moi,
        )

    # Thay text (giữa > ... <)
    for cu, moi in (thay_the_dict.get("text") or {}).items():
        code_moi = code_moi.replace(">" + cu + "<", ">" + moi + "<")

    return code_moi


# ================================================================
# CHÈN CODE VÀO VỊ TRÍ MARKER
# ================================================================
def chen_code_vao_marker(code, marker, code_chen):
    """
    Chèn code vào vị trí có marker.

    marker: chuỗi đánh dấu (ví dụ: "<!-- CONTENT -->").
    code_chen: code cần chèn.
    """
    if not code or not marker:
        return code
    return code.replace(marker, code_chen + "\n" + marker)


# ================================================================
# KIỂM TRA CÚ PHÁP CODE (Python)
# ================================================================
def kiem_tra_cu_phap_python(code):
    """Kiểm tra cú pháp Python. Trả về (True, "") hoặc (False, lỗi)."""
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


# ================================================================
# LÀM SẠCH CODE
# ================================================================
def lam_sach_code(code, ngon_ngu="python"):
    """Làm sạch code: bỏ dòng trống thừa, chuẩn hóa indent."""
    if not code:
        return code

    cac_dong = code.split("\n")

    # Bỏ dòng trống liên tiếp
    ket_qua = []
    dong_trong_truoc = False
    for dong in cac_dong:
        if not dong.strip():
            if dong_trong_truoc:
                continue
            dong_trong_truoc = True
        else:
            dong_trong_truoc = False
        ket_qua.append(dong.rstrip())

    return "\n".join(ket_qua).strip() + "\n"


# ================================================================
# TẠO CODE NHANH TỪ NHIỀU NODE (API gộp)
# ================================================================
def tao_code(danh_sach_node, yeu_to=None, noi_dung="", lam_sach=True):
    """
    API gộp: nhận 1 node hoặc list node → trả code.

    Tự phát hiện: nếu 1 node → tao_code_tu_node, nếu nhiều → ghep_nhieu_node.
    """
    if not danh_sach_node:
        return {"thanh_cong": False, "loi": "Không có node.", "code": "", "ngon_ngu": ""}

    if isinstance(danh_sach_node, list):
        ket_qua = ghep_nhieu_node(danh_sach_node, yeu_to, noi_dung)
    else:
        ket_qua = tao_code_tu_node(danh_sach_node, yeu_to, noi_dung)

    if ket_qua.get("thanh_cong") and lam_sach:
        ket_qua["code"] = lam_sach_code(ket_qua["code"], ket_qua.get("ngon_ngu", "python"))

    return ket_qua
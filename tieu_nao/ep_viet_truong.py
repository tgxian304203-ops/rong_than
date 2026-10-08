"""
ep_viet_truong.py - Bước 3 Tiểu não: Ép model viết trường chuẩn Rồng Thần.

Nhiệm vụ:
    - ep_viet_truong(task, ngu_canh, chu_so_huu): tạo prompt + gọi model + validate.
    - _tao_prompt(task, ngu_canh): tạo prompt yêu cầu model sinh node.
    - _goi_va_lay_json(chu_so_huu, prompt): gọi do_model + parse JSON.
    - _trich_json(chuoi): trích JSON từ response model.
    - _validate_node(node): validate node theo schema.

ĐÃ SỬA (fix "code chưa cụ thể"):
    - FIX 1: Thêm rule phân số (Fraction) — "1/2 + 1/3" phải dùng Fraction.
    - FIX 2: Yêu cầu HTML phải có body đầy đủ (không chỉ <h1>).
    - FIX 3: Thêm ví dụ cụ thể cho từng loại task phổ biến.
    - FIX 4: Yêu cầu code có comment giải thích.
    - FIX 5: Prompt ngắn gọn (< 80 dòng).

Các fix cũ giữ nguyên:
    - Bỏ "cach_giai" khỏi TRUONG_BAT_BUOC.
    - Validate code không rỗng nếu loai = "chay_code".

Quy tắc (theo Phần 4, bước 3):
    - Tạo prompt yêu cầu model sinh node theo JSON schema.
    - Gửi đến model qua do_model.py.
    - Validate JSON. Sai → retry 3 lần.
    - Vẫn sai → báo lỗi.
    - Đúng → trả node về Đại não.

Trả về:
    - dict node (chuẩn schema) hoặc None nếu thất bại.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import re
import json
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
SO_LAN_RETRY = 3


# ================================================================
# SCHEMA NODE BẮT BUỘC
# ================================================================
TRUONG_BAT_BUOC = [
    "id",
    "ten",
    "linh_vuc",
    "loai_van_de",
    "cach_giai_phap",
    "dieu_kien",
    "hanh_dong",
]


# ================================================================
# FIX 5: PROMPT NGẮN GỌN + FIX 1, 2, 3, 4
# ================================================================
def _tao_prompt(task, ngu_canh=None):
    """
    Tạo prompt yêu cầu model sinh node.

    FIX 1: Thêm rule phân số.
    FIX 2: Yêu cầu HTML có body đầy đủ.
    FIX 3: Ví dụ cụ thể cho từng loại.
    FIX 4: Code có comment.
    FIX 5: Prompt ngắn gọn.
    """
    ngu_canh = ngu_canh or {}

    noi_dung = task.get("noi_dung", "")
    yeu_to = task.get("yeu_to", {}) or {}
    loai_task = task.get("loai_task", {}) or {}

    linh_vuc = loai_task.get("linh_vuc", "") or yeu_to.get("linh_vuc", "")
    nhom = loai_task.get("nhom", "")
    loai = loai_task.get("loai", "")

    ngu_canh_str = ""
    if ngu_canh:
        manh = []
        for key in ("hoi_thoai", "du_an", "ngon_ngu", "moi_truong"):
            v = ngu_canh.get(key, {})
            if v:
                manh.append(f"- {key}: {str(v)[:120]}")
        if manh:
            ngu_canh_str = "\nNgữ cảnh:\n" + "\n".join(manh)

    prompt = f"""Bạn là Tiểu não Rồng Thần — chuyên gia code.

TASK: "{noi_dung}"

Phân loại:
- Lĩnh vực: {linh_vuc or '(chưa rõ)'}
- Nhóm: {nhom or '(chưa rõ)'}
- Loại: {loai or '(chưa rõ)'}
{ngu_canh_str}

═══════════════════════════════════════
QUY TẮC VIẾT CODE (BẮT BUỘC):
═══════════════════════════════════════
1. Code PHẢI CỤ THỂ cho task — KHÔNG viết boilerplate.
2. Code PHẢI ĐẦY ĐỦ — đóng thẻ, đóng hàm, KHÔNG cắt cụt.
3. Code PHẢI có COMMENT giải thích các bước chính.

QUY TẮC ĐẶC BIỆT THEO LOẠI TASK:

▸ NẾU TASK LIÊN QUAN PHÂN SỐ (có dạng "a/b"):
   → Dùng `from fractions import Fraction`
   → VD: "1/2 + 1/3" → 
     ```
     from fractions import Fraction
     # Cộng hai phân số
     ket_qua = Fraction(1, 2) + Fraction(1, 3)
     print(f"1/2 + 1/3 = {{ket_qua}}")  # 5/6
     ```
   → KHÔNG dùng `sum(args)` cho phân số.

▸ NẾU TASK YÊU CẦU WEB/HTML:
   → PHẢI có <html>, <head>, <body> đầy đủ.
   → PHẢI có nội dung cụ thể trong body (sản phẩm, form, bảng, ...).
   → KHÔNG chỉ viết <h1>tiêu đề</h1> rồi hết.
   → VD task "web bán thẻ bài":
     - Header có logo + menu.
     - Có danh sách sản phẩm (thẻ bài).
     - Có giỏ hàng.
     - Có footer.

▸ NẾU TASK YÊU CẦU VĂN/NGHỊ LUẬN:
   → KHÔNG viết code. Đặt hanh_dong.loai = "tra_loi".
   → hanh_dong.code = "" (rỗng).
   → Ghi nội dung vào cach_giai_phap và ten.

▸ NẾU TASK TOÁN ĐƠN GIẢN:
   → VD "1+1" → 
     ```
     def cong(a, b):
         # Cộng hai số
         return a + b
     
     print(cong(1, 1))
     ```

▸ NẾU TASK YÊU CẦU AI/API KEY:
   → Code phải có xử lý MẢNG key, xoay key, retry.
   → KHÔNG viết Flask boilerplate.

═══════════════════════════════════════
TRẢ VỀ JSON (đúng 7 trường):
═══════════════════════════════════════
{{
  "id": "nut-<16 hex ngẫu nhiên>",
  "ten": "Tên ngắn gọn (tối đa 80 ký tự)",
  "linh_vuc": "toán | văn | code | bug | khoa học | đời sống | kinh doanh | sáng tạo | học tập | tra cứu | kỹ thuật | luật - hành chính",
  "loai_van_de": "nhóm vấn đề",
  "cach_giai_phap": "cách giải ngắn (gạch_dưới)",
  "dieu_kien": {{
    "chua": ["từ khóa 1", "từ khóa 2"]
  }},
  "hanh_dong": {{
    "loai": "chay_code | tra_loi | tra_web",
    "code": "CODE ĐẦY ĐỦ Ở ĐÂY, CÓ COMMENT",
    "ngon_ngu": "python | html | javascript"
  }}
}}

CHỈ TRẢ VỀ JSON. KHÔNG giải thích."""

    return prompt


# ================================================================
# TRÍCH JSON TỪ RESPONSE
# ================================================================
def _trich_json(chuoi):
    if not chuoi:
        return None

    chuoi = chuoi.strip()

    try:
        return json.loads(chuoi)
    except (json.JSONDecodeError, ValueError):
        pass

    mau_markdown = r"```(?:json)?\s*([\s\S]*?)```"
    khop = re.search(mau_markdown, chuoi)
    if khop:
        try:
            return json.loads(khop.group(1).strip())
        except (json.JSONDecodeError, ValueError):
            pass

    vi_tri_dau = chuoi.find("{")
    vi_tri_cuoi = chuoi.rfind("}")
    if vi_tri_dau >= 0 and vi_tri_cuoi > vi_tri_dau:
        chuoi_json = chuoi[vi_tri_dau:vi_tri_cuoi + 1]
        try:
            return json.loads(chuoi_json)
        except (json.JSONDecodeError, ValueError):
            pass

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
# VALIDATE NODE
# ================================================================
def _validate_node(node):
    if not node or not isinstance(node, dict):
        return False, "Node không phải dict."

    thieu = []
    for truong in TRUONG_BAT_BUOC:
        if truong not in node or node[truong] in (None, "", [], {}):
            thieu.append(truong)

    if thieu:
        return False, f"Thiếu trường: {', '.join(thieu)}"

    if not isinstance(node["dieu_kien"], dict):
        return False, "dieu_kien không phải dict."

    if not isinstance(node["hanh_dong"], dict):
        return False, "hanh_dong không phải dict."

    loai_hd = (node["hanh_dong"].get("loai") or "").strip()
    if loai_hd == "chay_code":
        code = (node["hanh_dong"].get("code") or "").strip()
        if not code:
            return False, "hanh_dong.loai='chay_code' nhưng code rỗng."
        # Kiểm tra code bị cắt cụt
        if code.count("<") != code.count(">"):
            return False, "Code HTML có thẻ không đóng (bị cắt cụt)."

    return True, ""


# ================================================================
# GỌI MODEL VÀ LẤY JSON
# ================================================================
def _goi_va_lay_json(chu_so_huu, prompt):
    try:
        from tieu_nao.do_model import do_model
    except ImportError:
        return None, "do_model.py chưa có."

    ket_qua = do_model(chu_so_huu, prompt)

    if not ket_qua.get("thanh_cong"):
        return None, ket_qua.get("loi", "Không gọi được model.")

    chuoi_tra_loi = ket_qua.get("ket_qua", "")
    if not chuoi_tra_loi:
        return None, "Model trả về rỗng."

    node = _trich_json(chuoi_tra_loi)
    if not node:
        return None, "Không parse được JSON từ response."

    return node, ""


# ================================================================
# HÀM CHÍNH
# ================================================================
def ep_viet_truong(task, ngu_canh=None, chu_so_huu=""):
    if not task:
        return None

    if not chu_so_huu:
        _ghi_log("loi", "ep_viet_truong: thiếu chu_so_huu.")
        return None

    prompt = _tao_prompt(task, ngu_canh)

    for lan_thu in range(1, SO_LAN_RETRY + 1):
        _ghi_log("tieu-nao", f"Ép viết trường lần {lan_thu}/{SO_LAN_RETRY}")

        node, loi = _goi_va_lay_json(chu_so_huu, prompt)

        if not node:
            _ghi_log("loi", f"Lần {lan_thu} thất bại: {loi}")
            time.sleep(1)
            continue

        hop_le, ly_do = _validate_node(node)
        if not hop_le:
            _ghi_log("loi", f"Node không hợp lệ: {ly_do}")
            node = _chuan_hoa_node(node)
            hop_le2, _ = _validate_node(node)
            if hop_le2:
                _ghi_log("tieu-nao", "Đã chuẩn hóa node thành công.")
                return node
            time.sleep(1)
            continue

        _ghi_log(
            "tieu-nao",
            f"Ép viết trường thành công lần {lan_thu}: "
            f"'{node.get('ten', '')[:60]}'",
        )
        return node

    _ghi_log("loi", f"Ép viết trường thất bại sau {SO_LAN_RETRY} lần.")
    return None


# ================================================================
# CHUẨN HÓA NODE
# ================================================================
def _chuan_hoa_node(node):
    if not isinstance(node, dict):
        return node

    if not node.get("id") or not isinstance(node["id"], str):
        node["id"] = "nut-" + secrets.token_hex(8)
    elif not node["id"].startswith("nut-"):
        node["id"] = "nut-" + node["id"][:16]

    if not node.get("ten"):
        node["ten"] = (node.get("cach_giai_phap") or "node mới")[:80]

    if not isinstance(node.get("dieu_kien"), dict):
        node["dieu_kien"] = {
            "chua": [],
            "yeu_to_can": ["hanh_dong", "doi_tuong"],
        }

    if not node.get("cach_giai_phap"):
        node["cach_giai_phap"] = node.get("ten", "chưa rõ")

    if not isinstance(node.get("hanh_dong"), dict):
        node["hanh_dong"] = {
            "loai": "tra_loi",
            "code": "",
            "ngon_ngu": "",
        }

    return node


# ================================================================
# HÀM PHỤ
# ================================================================
def ep_viet_truong_mot_lan(task, ngu_canh=None, chu_so_huu=""):
    if not task or not chu_so_huu:
        return None

    prompt = _tao_prompt(task, ngu_canh)
    node, _ = _goi_va_lay_json(chu_so_huu, prompt)
    if not node:
        return None

    hop_le, _ = _validate_node(node)
    if not hop_le:
        node = _chuan_hoa_node(node)

    return node


def tao_prompt_nhieu_node(task, so_luong=3, ngu_canh=None):
    prompt_goc = _tao_prompt(task, ngu_canh)
    prompt = prompt_goc.replace(
        "TRẢ VỀ JSON (đúng 7 trường):",
        f"TRẢ VỀ JSON ARRAY chứa {so_luong} object (mỗi object đúng 7 trường):",
    )
    prompt = prompt.replace(
        "CHỈ TRẢ VỀ JSON. KHÔNG giải thích.",
        "CHỈ TRẢ VỀ JSON ARRAY. KHÔNG giải thích.",
    )
    return prompt


def ep_viet_nhieu_node(task, so_luong=3, ngu_canh=None, chu_so_huu=""):
    if not task or not chu_so_huu:
        return []

    prompt = tao_prompt_nhieu_node(task, so_luong, ngu_canh)

    try:
        from tieu_nao.do_model import do_model
    except ImportError:
        return []

    ket_qua = do_model(chu_so_huu, prompt)
    if not ket_qua.get("thanh_cong"):
        return []

    chuoi = ket_qua.get("ket_qua", "")
    ket_qua_list = _trich_json_array(chuoi)
    if not ket_qua_list:
        return []

    ket_qua_hop_le = []
    for node in ket_qua_list:
        if isinstance(node, dict):
            hop_le, _ = _validate_node(node)
            if not hop_le:
                node = _chuan_hoa_node(node)
            ket_qua_hop_le.append(node)

    return ket_qua_hop_le


def _trich_json_array(chuoi):
    if not chuoi:
        return []

    chuoi = chuoi.strip()

    try:
        ket_qua = json.loads(chuoi)
        if isinstance(ket_qua, list):
            return ket_qua
    except (json.JSONDecodeError, ValueError):
        pass

    mau_markdown = r"```(?:json)?\s*([\s\S]*?)```"
    khop = re.search(mau_markdown, chuoi)
    if khop:
        try:
            ket_qua = json.loads(khop.group(1).strip())
            if isinstance(ket_qua, list):
                return ket_qua
        except (json.JSONDecodeError, ValueError):
            pass

    vi_tri_dau = chuoi.find("[")
    vi_tri_cuoi = chuoi.rfind("]")
    if vi_tri_dau >= 0 and vi_tri_cuoi > vi_tri_dau:
        try:
            ket_qua = json.loads(chuoi[vi_tri_dau:vi_tri_cuoi + 1])
            if isinstance(ket_qua, list):
                return ket_qua
        except (json.JSONDecodeError, ValueError):
            pass

    return []


def tom_tat_node(node):
    if not node:
        return ""
    return (
        f"[{node.get('linh_vuc', '?')}/{node.get('loai_van_de', '?')}/"
        f"{node.get('cach_giai_phap', '?')}] {node.get('ten', '')[:60]}"
    )


def so_lan_retry_toi_da():
    return SO_LAN_RETRY
"""
ep_viet_truong.py - Bước 3 Tiểu não: Ép model viết trường chuẩn Rồng Thần.

Nhiệm vụ:
    - ep_viet_truong(task, ngu_canh, chu_so_huu): tạo prompt + gọi model + validate.
    - _tao_prompt(task, ngu_canh): tạo prompt yêu cầu model sinh node.
    - _goi_va_lay_json(chu_so_huu, prompt): gọi do_model + parse JSON.
    - _trich_json(chuoi): trích JSON từ response model.
    - _validate_node(node): validate node theo schema.

ĐÃ SỬA:
    - Prompt chi tiết hơn, yêu cầu model SUY LUẬN trước khi viết code.
    - Thêm ví dụ cụ thể cho từng loại task.
    - Yêu cầu code CỤ THỂ, KHÔNG dùng code mẫu chung.

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
    "cach_giai",
    "hanh_dong",
]


# ================================================================
# TẠO PROMPT (SỬA — CHI TIẾT HƠN)
# ================================================================
def _tao_prompt(task, ngu_canh=None):
    """
    Tạo prompt yêu cầu model sinh node theo JSON schema.

    SỬA: Prompt chi tiết, có ví dụ, yêu cầu code cụ thể.
    """
    ngu_canh = ngu_canh or {}

    noi_dung = task.get("noi_dung", "")
    yeu_to = task.get("yeu_to", {}) or {}
    loai_task = task.get("loai_task", {}) or {}

    linh_vuc = loai_task.get("linh_vuc", "") or yeu_to.get("linh_vuc", "")
    nhom = loai_task.get("nhom", "")
    loai = loai_task.get("loai", "")

    # Ngữ cảnh
    ngu_canh_str = ""
    if ngu_canh:
        cac_manh = []
        for key in ("hoi_thoai", "du_an", "file", "linh_vuc", "ngon_ngu", "moi_truong", "cam_xuc"):
            v = ngu_canh.get(key, {})
            if v:
                cac_manh.append(f"- {key}: {str(v)[:200]}")
        if cac_manh:
            ngu_canh_str = "Ngữ cảnh:\n" + "\n".join(cac_manh)

    prompt = f"""Bạn là Tiểu não của Rồng Thần — chuyên gia viết code và giải quyết vấn đề.

NHIỆM VỤ CẦN XỬ LÝ:
\"{noi_dung}\"

5 yếu tố đã trích:
- Hành động: {yeu_to.get('hanh_dong', '(chưa rõ)')}
- Đối tượng: {yeu_to.get('doi_tuong', '(chưa rõ)')}
- Thuộc tính: {yeu_to.get('thuoc_tinh', '(chưa rõ)')}
- Ràng buộc: {yeu_to.get('rang_buoc', '(chưa rõ)')}
- Ngữ cảnh: {yeu_to.get('ngu_canh', '(chưa rõ)')}

Phân loại sẵn có:
- Lĩnh vực: {linh_vuc or '(chưa rõ)'}
- Nhóm: {nhom or '(chưa rõ)'}
- Loại: {loai or '(chưa rõ)'}

{ngu_canh_str}

═══════════════════════════════════════════
BƯỚC 1: SUY LUẬN TRƯỚC KHI VIẾT
═══════════════════════════════════════════
Hãy tự hỏi (KHÔNG cần ghi vào JSON):
1. Task này thực sự cần gì? (làm web? viết hàm? tạo AI? xử lý file?)
2. Code cần làm gì CỤ THỂ?
3. Cần thư viện nào?
4. Có ràng buộc gì đặc biệt không?

VÍ DỤ SUY LUẬN:
- Task "tạo AI dùng nhiều API key" → cần code xử lý NHIỀU API KEY (array keys, xoay key, retry khi hết quota). KHÔNG viết Flask boilerplate chung.
- Task "làm web bán hàng" → cần HTML có sản phẩm, giỏ hàng, thanh toán. KHÔNG viết `<h1>Web bán hàng</h1>`.
- Task "tính 1+1" → cần code Python `def cong(a,b): return a+b`. KHÔNG viết Flask.

═══════════════════════════════════════════
BƯỚC 2: VIẾT CODE CỤ THỂ
═══════════════════════════════════════════
- Code PHẢI phù hợp với task.
- KHÔNG viết code mẫu chung chung.
- Nếu task đơn giản → code đơn giản.
- Nếu task phức tạp → code phức tạp.

═══════════════════════════════════════════
BƯỚC 3: TRẢ VỀ JSON
═══════════════════════════════════════════
Hãy sinh 1 node mới dưới dạng JSON. Không giải thích gì thêm ngoài JSON.

Schema bắt buộc (đúng 8 trường):
{{
  "id": "nut-xxxxxxxx",
  "ten": "Tên node ngắn gọn (tối đa 80 ký tự)",
  "linh_vuc": "toán | văn | code | bug | khoa học | đời sống | kinh doanh | sáng tạo | học tập | tra cứu | kỹ thuật | luật - hành chính",
  "loai_van_de": "nhóm vấn đề (ví dụ: số học, tạo mới, runtime)",
  "cach_giai_phap": "cách giải (ví dụ: cộng số nguyên, làm web)",
  "dieu_kien": {{
    "chua": ["từ khóa 1", "từ khóa 2"],
    "yeu_to_can": ["hanh_dong", "doi_tuong"]
  }},
  "cach_giai": {{
    "mo_ta": "Mô tả cách giải bằng tiếng Việt",
    "cac_buoc": ["bước 1", "bước 2"],
    "vi_du": "Ví dụ minh họa"
  }},
  "hanh_dong": {{
    "loai": "tra_loi | chay_code | tra_web",
    "code": "CODE CỤ THỂ — viết code đầy đủ, có comment giải thích",
    "ngon_ngu": "python | html | javascript | ..."
  }}
}}

LƯU Ý QUAN TRỌNG:
- id: bắt đầu bằng "nut-" + 16 ký tự hex ngẫu nhiên.
- ten: ngắn gọn, mô tả ĐÚNG vấn đề (VD: "Tạo AI dùng nhiều API key", KHÔNG viết "Hàm mới").
- code: PHẢI là code CỤ THỂ cho task này. KHÔNG viết:
  * Flask boilerplate `app = Flask(__name__)` nếu task không yêu cầu web.
  * `<h1>Hello World</h1>` nếu task yêu cầu web bán hàng.
  * Code rỗng nếu task yêu cầu viết hàm.
- Không lưu kết quả cụ thể. Chỉ lưu quy tắc / thuật toán / cách giải.
- Node phải áp dụng được cho mọi task cùng loại.

Trả về CHỈ JSON, không có văn bản nào khác."""

    return prompt


# ================================================================
# TRÍCH JSON TỪ RESPONSE
# ================================================================
def _trich_json(chuoi):
    """Trích JSON từ response của model."""
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

    # 4. Sửa lỗi phổ biến
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
    """Kiểm tra node có đủ 8 trường bắt buộc không."""
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

    if not isinstance(node["cach_giai"], dict):
        return False, "cach_giai không phải dict."

    if not node["cach_giai"].get("mo_ta"):
        return False, "cach_giai.mo_ta rỗng."

    if not isinstance(node["hanh_dong"], dict):
        return False, "hanh_dong không phải dict."

    return True, ""


# ================================================================
# GỌI MODEL VÀ LẤY JSON
# ================================================================
def _goi_va_lay_json(chu_so_huu, prompt):
    """Gọi model qua do_model.py và parse JSON từ response."""
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
    """
    Bước 3: Ép model viết trường chuẩn.

    task: dict { noi_dung, yeu_to, loai_task }.
    ngu_canh: dict 10 loại ngữ cảnh.
    chu_so_huu: tên tài khoản.

    Trả về: dict node hoặc None nếu thất bại.
    """
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
            if "Không gọi được model" in loi or "rỗng" in loi:
                time.sleep(1)
                continue
            continue

        hop_le, ly_do = _validate_node(node)
        if not hop_le:
            _ghi_log("loi", f"Node không hợp lệ: {ly_do}")

            node = _chuan_hoa_node(node)
            hop_le2, ly_do2 = _validate_node(node)
            if hop_le2:
                _ghi_log("tieu-nao", f"Đã chuẩn hóa node thành công.")
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
    """Chuẩn hóa node: bổ sung trường thiếu, sửa format."""
    if not isinstance(node, dict):
        return node

    if not node.get("id") or not isinstance(node["id"], str):
        import secrets
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

    if not isinstance(node.get("cach_giai"), dict):
        node["cach_giai"] = {
            "mo_ta": str(node.get("cach_giai", "")),
            "cac_buoc": [],
            "vi_du": "",
        }
    elif not node["cach_giai"].get("mo_ta"):
        node["cach_giai"]["mo_ta"] = node.get("ten", "Chưa có mô tả.")

    if not isinstance(node.get("hanh_dong"), dict):
        node["hanh_dong"] = {
            "loai": "tra_loi",
            "code": "",
            "ngon_ngu": "",
        }

    return node


# ================================================================
# HÀM PHỤ: GỌI 1 LẦN
# ================================================================
def ep_viet_truong_mot_lan(task, ngu_canh=None, chu_so_huu=""):
    """Ép viết trường 1 lần (không retry)."""
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


# ================================================================
# HÀM PHỤ: TẠO PROMPT NHIỀU NODE
# ================================================================
def tao_prompt_nhieu_node(task, so_luong=3, ngu_canh=None):
    """Tạo prompt yêu cầu model sinh nhiều node cùng lúc."""
    prompt_goc = _tao_prompt(task, ngu_canh)

    prompt = prompt_goc.replace(
        "sinh 1 node mới dưới dạng JSON",
        f"sinh {so_luong} node mới dưới dạng JSON array",
    ).replace(
        "Trả về CHỈ JSON, không có văn bản nào khác.",
        f"Trả về CHỈ JSON array chứa {so_luong} object, "
        "mỗi object theo schema trên. Không có văn bản nào khác.",
    )

    return prompt


def ep_viet_nhieu_node(task, so_luong=3, ngu_canh=None, chu_so_huu=""):
    """Sinh nhiều node cùng lúc."""
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
    """Trích JSON array từ response."""
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


# ================================================================
# HÀM PHỤ
# ================================================================
def tom_tat_node(node):
    if not node:
        return ""
    return (
        f"[{node.get('linh_vuc', '?')}/{node.get('loai_van_de', '?')}/"
        f"{node.get('cach_giai_phap', '?')}] {node.get('ten', '')[:60]}"
    )


def so_lan_retry_toi_da():
    return SO_LAN_RETRY
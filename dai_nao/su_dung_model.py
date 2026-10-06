"""
su_dung_model.py - Gọi Tiểu não khi Đại não bí Rồng Thần.

Nhiệm vụ:
    - su_dung_model(task, ngu_canh): nhận task, gọi Tiểu não sinh node.
    - kiem_tra_node(node): validate node sinh ra từ Tiểu não.
    - chuan_hoa_node(node): chuẩn hóa node về đúng format.
    - goi_tieu_nao(task, ngu_canh): gọi trực tiếp module Tiểu não.

Quy tắc:
    - Đây là CẦU NỐI Đại não → Tiểu não.
    - Không sinh node tại đây — chỉ điều phối.
    - Validate node theo schema của cây quyết định.
    - Nếu Tiểu não lỗi → trả None, không sập.
    - Ghi log mỗi lần gọi.

Trả về:
    - Nut object (từ cay_quyet_dinh.py) nếu thành công.
    - None nếu thất bại.

Tầng dữ liệu: dai_nao/ghi_nho.py
Điều phối Tiểu não: tieu_nao/ep_viet_truong.py (sẽ làm sau).
"""

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
# SCHEMA NODE — các trường bắt buộc
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

TRUONG_MAC_DINH = {
    "phien_ban": 1,
    "score": 0.7,
    "so_lan_thu": 0,
    "thanh_cong": 0,
    "that_bai": 0,
    "do_kho": 0.5,
    "thoi_gian_uoc_tinh": 0,
    "phu_thuoc": [],
    "uu_tien": 50,
    "nhanh_con": [],
    "chia_se_voi": [],
    "muon_tu": "",
    "failed_paths": [],
    "blacklist": False,
    "ngu_canh_node": "",
    "lan_dung_cuoi": 0,
}


# ================================================================
# VALIDATE NODE
# ================================================================
def kiem_tra_node(node):
    """
    Kiểm tra node sinh ra có hợp lệ không.

    Trả về: (True, "") nếu OK, hoặc (False, "lỗi") nếu sai.
    """
    if not node:
        return False, "Node rỗng."

    # Nếu là Nut object → chuyển sang dict
    if hasattr(node, "sang_dict_phang"):
        node = node.sang_dict_phang()

    if not isinstance(node, dict):
        return False, "Node không phải dict."

    # Kiểm tra trường bắt buộc
    thieu = []
    for truong in TRUONG_BAT_BUOC:
        if truong not in node or node[truong] in (None, "", [], {}):
            thieu.append(truong)

    if thieu:
        return False, f"Thiếu trường: {', '.join(thieu)}"

    # Kiểm tra id
    if not isinstance(node.get("id"), str) or len(node["id"]) < 3:
        return False, "id không hợp lệ."

    # Kiểm tra lĩnh vực
    linh_vuc_hop_le = {
        "toán", "văn", "code", "bug", "khoa học", "đời sống",
        "kinh doanh", "sáng tạo", "học tập", "tra cứu",
        "kỹ thuật", "luật - hành chính", "khac",
    }
    if node.get("linh_vuc", "").lower() not in linh_vuc_hop_le:
        # Không bắt buộc phải nằm trong danh sách — chỉ cảnh báo
        pass

    # Kiểm tra cách giải có nội dung
    cach_giai = node.get("cach_giai", {})
    if isinstance(cach_giai, dict):
        if not cach_giai.get("mo_ta") and not cach_giai.get("cac_buoc"):
            return False, "cach_giai rỗng."
    elif not cach_giai:
        return False, "cach_giai rỗng."

    return True, ""


# ================================================================
# CHUẨN HÓA NODE
# ================================================================
def chuan_hoa_node(node):
    """
    Chuẩn hóa node về đúng format cây quyết định.
    - Bổ sung trường mặc định nếu thiếu.
    - Chuẩn hóa tên trường.
    - Đảm bảo dict đúng schema.
    """
    if not node:
        return None

    # Nếu là Nut object → dict
    if hasattr(node, "sang_dict_phang"):
        node = node.sang_dict_phang()

    if not isinstance(node, dict):
        return None

    ket_qua = dict(node)

    # Bổ sung trường mặc định
    for truong, gia_tri in TRUONG_MAC_DINH.items():
        if truong not in ket_qua:
            ket_qua[truong] = gia_tri

    # Chuẩn hóa một số trường
    ket_qua["ten"] = str(ket_qua.get("ten", ""))[:200]
    ket_qua["linh_vuc"] = str(ket_qua.get("linh_vuc", "")).lower()
    ket_qua["loai_van_de"] = str(ket_qua.get("loai_van_de", "")).lower()
    ket_qua["cach_giai_phap"] = str(ket_qua.get("cach_giai_phap", "")).lower()

    # Đảm bảo dieu_kien là dict
    if not isinstance(ket_qua.get("dieu_kien"), dict):
        ket_qua["dieu_kien"] = {
            "chua": [str(ket_qua.get("dieu_kien", ""))] if ket_qua.get("dieu_kien") else [],
            "yeu_to_can": ["hanh_dong", "doi_tuong"],
        }

    # Đảm bảo cach_giai là dict
    if not isinstance(ket_qua.get("cach_giai"), dict):
        ket_qua["cach_giai"] = {
            "mo_ta": str(ket_qua.get("cach_giai", "")),
            "cac_buoc": [],
        }

    # Đảm bảo hanh_dong là dict
    if not isinstance(ket_qua.get("hanh_dong"), dict):
        ket_qua["hanh_dong"] = {
            "loai": "tra_loi",
            "code": "",
            "ngon_ngu": "",
        }

    # Đảm bảo các trường list
    for truong_list in ("phu_thuoc", "nhanh_con", "chia_se_voi", "failed_paths"):
        if not isinstance(ket_qua.get(truong_list), list):
            ket_qua[truong_list] = []

    # Chuẩn hóa score
    try:
        ket_qua["score"] = float(ket_qua.get("score", 0.7))
        ket_qua["score"] = max(0.0, min(1.0, ket_qua["score"]))
    except (TypeError, ValueError):
        ket_qua["score"] = 0.7

    # Chuẩn hóa uu_tien
    try:
        ket_qua["uu_tien"] = int(ket_qua.get("uu_tien", 50))
        ket_qua["uu_tien"] = max(0, min(100, ket_qua["uu_tien"]))
    except (TypeError, ValueError):
        ket_qua["uu_tien"] = 50

    # Thời gian
    if not ket_qua.get("ngay_tao"):
        ket_qua["ngay_tao"] = int(time.time())

    return ket_qua


# ================================================================
# GỌI TIỂU NÃO
# ================================================================
def goi_tieu_nao(task, ngu_canh=None):
    """
    Gọi module Tiểu não để sinh node mới.

    task: dict { noi_dung, yeu_to, loai_task }.
    ngu_canh: dict 10 loại ngữ cảnh (tùy chọn).

    Trả về:
    - dict node (chưa chuẩn hóa) hoặc
    - None nếu Tiểu não chưa có.
    """
    ngu_canh = ngu_canh or {}

    # Thử nhiều module Tiểu não theo thứ tự ưu tiên
    cac_module = [
        ("tieu_nao.ep_viet_truong", "ep_viet_truong"),
        ("tieu_nao.tao_nhanh", "tao_nhanh"),
    ]

    for duong_dan, ten_ham in cac_module:
        try:
            module = __import__(duong_dan, fromlist=[ten_ham])
            ham = getattr(module, ten_ham, None)
            if not ham:
                continue

            ket_qua = ham(task, ngu_canh)
            if ket_qua:
                _ghi_log(
                    "tieu-nao",
                    f"Tiểu não sinh node thành công qua {duong_dan}",
                )
                return ket_qua

        except ImportError:
            continue
        except Exception as e:
            _ghi_log("loi", f"Tiểu não lỗi ({duong_dan}): {e}")
            continue

    _ghi_log("tieu-nao", "Tiểu não chưa có hoặc không sinh được node.")
    return None


# ================================================================
# HÀM CHÍNH
# ================================================================
def su_dung_model(task, ngu_canh=None):
    """
    Gọi Tiểu não sinh node khi Đại não bí.

    task: dict { noi_dung, yeu_to, loai_task }.
    ngu_canh: dict 10 loại ngữ cảnh.

    Trả về: Nut object (nếu thành công) hoặc None.
    """
    if not task:
        return None

    _ghi_log(
        "dai-nao",
        f"Gọi Tiểu não cho task: {str(task.get('noi_dung', ''))[:80]}",
    )

    # 1. Gọi Tiểu não
    node_tho = goi_tieu_nao(task, ngu_canh)
    if not node_tho:
        return None

    # 2. Validate node
    hop_le, ly_do = kiem_tra_node(node_tho)
    if not hop_le:
        _ghi_log("loi", f"Node từ Tiểu não không hợp lệ: {ly_do}")
        return None

    # 3. Chuẩn hóa node
    node_chuan = chuan_hoa_node(node_tho)
    if not node_chuan:
        _ghi_log("loi", "Không chuẩn hóa được node.")
        return None

    # 4. Chuyển dict → Nut object
    try:
        from dai_nao.cay_quyet_dinh import Nut
        node_obj = Nut(node_chuan)
    except ImportError:
        _ghi_log("loi", "cay_quyet_dinh.py chưa có — trả dict thay Nut.")
        return node_chuan
    except Exception as e:
        _ghi_log("loi", f"Không tạo được Nut: {e}")
        return node_chuan

    # 5. Ghi log thành công
    _ghi_log(
        "tieu-nao",
        f"Node mới: '{node_obj.ten}' ({node_obj.linh_vuc}/{node_obj.loai_van_de})",
    )

    return node_obj


# ================================================================
# HÀM PHỤ: KIỂM TRA TIỂU NÃO SẴN SÀNG
# ================================================================
def tieu_nao_san_sang():
    """Kiểm tra Tiểu não đã sẵn sàng chưa (có module không)."""
    cac_module = [
        "tieu_nao.ep_viet_truong",
        "tieu_nao.tao_nhanh",
        "tieu_nao.do_model",
    ]
    for duong_dan in cac_module:
        try:
            __import__(duong_dan)
            return True
        except ImportError:
            continue
    return False


# ================================================================
# HÀM PHỤ: LẤY DANH SÁCH MODULE TIỂU NÃO CÓ SẴN
# ================================================================
def liet_ke_module_tieu_nao():
    """Liệt kê module Tiểu não đã có."""
    tat_ca = [
        "tieu_nao.kiem_ke_key",
        "tieu_nao.lay_danh_sach_model",
        "tieu_nao.do_model",
        "tieu_nao.xoay_key",
        "tieu_nao.quan_ly_quota",
        "tieu_nao.quan_ly_loi",
        "tieu_nao.het_quota",
        "tieu_nao.ep_viet_truong",
        "tieu_nao.schema_node",
        "tieu_nao.tao_nhanh",
        "tieu_nao.api_groq",
        "tieu_nao.api_openrouter",
        "tieu_nao.api_gemini",
        "tieu_nao.api_chung",
    ]
    co_san = []
    for duong_dan in tat_ca:
        try:
            __import__(duong_dan)
            co_san.append(duong_dan)
        except ImportError:
            continue
    return co_san


# ================================================================
# HÀM PHỤ: TÓM TẮT NODE MỚI
# ================================================================
def tom_tat_node(node):
    """Tạo chuỗi tóm tắt node để log."""
    if not node:
        return ""

    if hasattr(node, "sang_dict_phang"):
        node = node.sang_dict_phang()

    return (
        f"[{node.get('linh_vuc', '?')}/{node.get('loai_van_de', '?')}/"
        f"{node.get('cach_giai_phap', '?')}] {node.get('ten', '')[:60]}"
    )
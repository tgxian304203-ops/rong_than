"""
su_dung_model.py - Gọi Tiểu não khi Đại não bí Rồng Thần.

Nhiệm vụ:
    - su_dung_model(task, ngu_canh, chu_so_huu): gọi Tiểu não sinh node.
    - kiem_tra_node(node): validate node sinh ra từ Tiểu não.
    - chuan_hoa_node(node): chuẩn hóa node về đúng format.
    - goi_tieu_nao(task, ngu_canh, chu_so_huu): gọi trực tiếp module Tiểu não.

ĐÃ SỬA (fix "Ta chưa hiểu rõ task này"):
    - FIX 1: Bỏ "cach_giai" khỏi TRUONG_BAT_BUOC — chỉ giữ 7 trường đúng
             theo schema mới của ep_viet_truong.py.
    - FIX 2: kiem_tra_node không đòi cach_giai.mo_ta nữa.
    - FIX 3: Kiểm tra hanh_dong.code hoặc cach_giai_phap mới là đủ.

Các fix cũ giữ nguyên:
    - Truyền chu_so_huu xuống ep_viet_truong và tao_nhanh.

Quy tắc:
    - Đây là CẦU NỐI Đại não → Tiểu não.
    - Không sinh node tại đây — chỉ điều phối.
    - Nếu Tiểu não lỗi → trả None, không sập.

Tầng dữ liệu: dai_nao/ghi_nho.py
Điều phối Tiểu não: tieu_nao/ep_viet_truong.py
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
# FIX 1: SCHEMA NODE — bỏ cach_giai, chỉ giữ 7 trường đúng
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
# FIX 2 + FIX 3: VALIDATE NODE — không đòi cach_giai nữa
# ================================================================
def kiem_tra_node(node):
    """Kiểm tra node sinh ra có hợp lệ không."""
    if not node:
        return False, "Node rỗng."

    if hasattr(node, "sang_dict_phang"):
        node = node.sang_dict_phang()

    if not isinstance(node, dict):
        return False, "Node không phải dict."

    thieu = []
    for truong in TRUONG_BAT_BUOC:
        if truong not in node or node[truong] in (None, "", [], {}):
            thieu.append(truong)

    if thieu:
        return False, f"Thiếu trường: {', '.join(thieu)}"

    if not isinstance(node.get("id"), str) or len(node["id"]) < 3:
        return False, "id không hợp lệ."

    if not isinstance(node.get("dieu_kien"), dict):
        return False, "dieu_kien không phải dict."

    if not isinstance(node.get("hanh_dong"), dict):
        return False, "hanh_dong không phải dict."

    # FIX 3: Node phải có nội dung thực (code HOẶC cach_giai_phap)
    hanh_dong = node.get("hanh_dong", {})
    code = (hanh_dong.get("code") or "").strip()
    loai_hd = (hanh_dong.get("loai") or "").strip()
    cach_giai_phap = (node.get("cach_giai_phap") or "").strip()

    if not code and loai_hd != "tra_web" and not cach_giai_phap:
        return False, "Node không có code, không có cach_giai_phap."

    return True, ""


# ================================================================
# CHUẨN HÓA NODE
# ================================================================
def chuan_hoa_node(node):
    """Chuẩn hóa node về đúng format cây quyết định."""
    if not node:
        return None

    if hasattr(node, "sang_dict_phang"):
        node = node.sang_dict_phang()

    if not isinstance(node, dict):
        return None

    ket_qua = dict(node)

    for truong, gia_tri in TRUONG_MAC_DINH.items():
        if truong not in ket_qua:
            ket_qua[truong] = gia_tri

    ket_qua["ten"] = str(ket_qua.get("ten", ""))[:200]
    ket_qua["linh_vuc"] = str(ket_qua.get("linh_vuc", "")).lower()
    ket_qua["loai_van_de"] = str(ket_qua.get("loai_van_de", "")).lower()
    ket_qua["cach_giai_phap"] = str(ket_qua.get("cach_giai_phap", "")).lower()

    if not isinstance(ket_qua.get("dieu_kien"), dict):
        ket_qua["dieu_kien"] = {
            "chua": [str(ket_qua.get("dieu_kien", ""))] if ket_qua.get("dieu_kien") else [],
            "yeu_to_can": ["hanh_dong", "doi_tuong"],
        }

    if not isinstance(ket_qua.get("hanh_dong"), dict):
        ket_qua["hanh_dong"] = {
            "loai": "tra_loi",
            "code": "",
            "ngon_ngu": "",
        }

    # Đảm bảo hanh_dong có đủ 3 trường
    hd = ket_qua["hanh_dong"]
    if not hd.get("loai"):
        hd["loai"] = "tra_loi"
    if "code" not in hd:
        hd["code"] = ""
    if "ngon_ngu" not in hd:
        hd["ngon_ngu"] = ""

    for truong_list in ("phu_thuoc", "nhanh_con", "chia_se_voi", "failed_paths"):
        if not isinstance(ket_qua.get(truong_list), list):
            ket_qua[truong_list] = []

    try:
        ket_qua["score"] = float(ket_qua.get("score", 0.7))
        ket_qua["score"] = max(0.0, min(1.0, ket_qua["score"]))
    except (TypeError, ValueError):
        ket_qua["score"] = 0.7

    try:
        ket_qua["uu_tien"] = int(ket_qua.get("uu_tien", 50))
        ket_qua["uu_tien"] = max(0, min(100, ket_qua["uu_tien"]))
    except (TypeError, ValueError):
        ket_qua["uu_tien"] = 50

    if not ket_qua.get("ngay_tao"):
        ket_qua["ngay_tao"] = int(time.time())

    return ket_qua


# ================================================================
# GỌI TIỂU NÃO
# ================================================================
def goi_tieu_nao(task, ngu_canh=None, chu_so_huu=""):
    """Gọi module Tiểu não để sinh node mới."""
    ngu_canh = ngu_canh or {}

    if not chu_so_huu:
        _ghi_log("loi", "goi_tieu_nao: thiếu chu_so_huu.")
        return None

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

            try:
                ket_qua = ham(task, ngu_canh, chu_so_huu)
            except TypeError:
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
def su_dung_model(task, ngu_canh=None, chu_so_huu=""):
    """Gọi Tiểu não sinh node khi Đại não bí."""
    if not task:
        return None

    if not chu_so_huu:
        _ghi_log("loi", "su_dung_model: thiếu chu_so_huu.")
        return None

    _ghi_log(
        "dai-nao",
        f"Gọi Tiểu não cho task: {str(task.get('noi_dung', ''))[:80]} "
        f"(tài khoản: {chu_so_huu})",
    )

    # 1. Gọi Tiểu não
    node_tho = goi_tieu_nao(task, ngu_canh, chu_so_huu)
    if not node_tho:
        return None

    # 2. Validate
    hop_le, ly_do = kiem_tra_node(node_tho)
    if not hop_le:
        _ghi_log("loi", f"Node từ Tiểu não không hợp lệ: {ly_do}")
        return None

    # 3. Chuẩn hóa
    node_chuan = chuan_hoa_node(node_tho)
    if not node_chuan:
        _ghi_log("loi", "Không chuẩn hóa được node.")
        return None

    # 4. Chuyển dict → Nut
    try:
        from dai_nao.cay_quyet_dinh import Nut
        node_obj = Nut(node_chuan)
    except ImportError:
        _ghi_log("loi", "cay_quyet_dinh.py chưa có — trả dict thay Nut.")
        return node_chuan
    except Exception as e:
        _ghi_log("loi", f"Không tạo được Nut: {e}")
        return node_chuan

    # 5. Log thành công
    _ghi_log(
        "tieu-nao",
        f"Node mới: '{node_obj.ten}' ({node_obj.linh_vuc}/{node_obj.loai_van_de})",
    )

    return node_obj


# ================================================================
# HÀM PHỤ
# ================================================================
def tieu_nao_san_sang():
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


def liet_ke_module_tieu_nao():
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


def tom_tat_node(node):
    if not node:
        return ""

    if hasattr(node, "sang_dict_phang"):
        node = node.sang_dict_phang()

    return (
        f"[{node.get('linh_vuc', '?')}/{node.get('loai_van_de', '?')}/"
        f"{node.get('cach_giai_phap', '?')}] {node.get('ten', '')[:60]}"
    )
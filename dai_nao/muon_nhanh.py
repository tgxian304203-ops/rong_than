"""
muon_nhanh.py - Cơ chế mượn nhánh Rồng Thần.

Nhiệm vụ:
    - tim_nhanh_gan_giong(noi_dung, loai_task, cay): tìm nhánh gần giống.
    - muon_nhanh(node_goc, noi_dung, loai_task, yeu_to): tạo nhánh mới.
    - kiem_tra_dieu_kien_muon(node_goc): kiểm tra score có đủ để mượn.

ĐÃ SỬA (fix "mượn nhánh sai lĩnh vực"):
    - FIX 1: Ngưỡng mượn từ 3.0 → 8.0 (chặt hơn nhiều).
    - FIX 2: Bắt buộc khớp lĩnh vực (linh_vuc node == linh_vuc task).
    - FIX 3: Bỏ cộng score vào điểm giống (score không phải độ giống).
    - FIX 4: Khớp từ đơn yêu cầu ≥ 5 ký tự (thay vì ≥ 3).
    - FIX 5: Yêu cầu khớp loai_van_de (nhóm) mới tính điểm mạnh.

Các fix cũ giữ nguyên:
    - L37: _thich_nghi_hanh_dong tự động thích nghi code.

Quy tắc (theo Phần 4):
    - Score < 0.5 → không mượn.
    - Score ≥ 0.5 → mượn cấu trúc và thích nghi.
    - Luôn tạo nhánh MỚI, không sửa nhánh cũ.
    - Ghi lại muon_tu = id_node_gốc.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import re
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
NGUONG_SCORE_MUON = 0.5       # score node gốc ≥ 0.5 mới mượn
SO_NODE_TOI_DA_XET = 200

# FIX 1: Nâng ngưỡng điểm giống từ 3.0 → 8.0
NGUONG_DIEM_GIONG = 8.0

# FIX 4: Yêu cầu từ đơn dài ≥ 5 ký tự mới tính khớp
DO_DAI_TU_TOI_THIEU = 5


# ================================================================
# TIỆN ÍCH
# ================================================================
def _lay(node, ten_truong, mac_dinh=None):
    if node is None:
        return mac_dinh
    if isinstance(node, dict):
        return node.get(ten_truong, mac_dinh)
    return getattr(node, ten_truong, mac_dinh)


def _tao_id():
    return "nut-" + secrets.token_hex(6)


# ================================================================
# KIỂM TRA ĐIỀU KIỆN MƯỢN
# ================================================================
def kiem_tra_dieu_kien_muon(node_goc):
    if node_goc is None:
        return False, "Node gốc không tồn tại."

    if bool(_lay(node_goc, "blacklist", False)):
        return False, "Node gốc đang bị blacklist."

    score = float(_lay(node_goc, "score", 0.0) or 0.0)
    if score < NGUONG_SCORE_MUON:
        return False, f"Score node gốc quá thấp ({score} < {NGUONG_SCORE_MUON})."

    co_cach_giai = bool(_lay(node_goc, "cach_giai"))
    co_quy_tac = bool(_lay(node_goc, "quy_tac"))
    co_hanh_dong = bool(_lay(node_goc, "hanh_dong"))

    if not (co_cach_giai or co_quy_tac or co_hanh_dong):
        return False, "Node gốc không có cách giải / quy tắc / hành động."

    return True, "Đủ điều kiện."


# ================================================================
# ĐẾM SỐ PHẦN TỬ TRONG TASK
# ================================================================
def _dem_tham_so_trong_noi_dung(noi_dung):
    if not noi_dung:
        return 0
    cac_so = re.findall(r"\b\d+(?:\.\d+)?\b", noi_dung)
    return len(cac_so)


# ================================================================
# SINH CODE LINH HOẠT VỚI *ARGS
# ================================================================
def _sinh_code_long(code_cu, so_luong):
    if not code_cu:
        return ""

    khop = re.search(
        r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*:\s*\n?\s*(return\s+.+)",
        code_cu,
    )
    if not khop:
        return ""

    ten_ham = khop.group(1)
    tham_so_cu = khop.group(2).strip()
    than_ham = khop.group(3).strip()

    so_tham_so_cu = len([t for t in tham_so_cu.split(",") if t.strip()])

    if so_tham_so_cu == so_luong:
        return code_cu

    than_moi = _thich_nghi_than_ham(than_ham, so_luong)
    if not than_moi:
        return ""

    code_moi = f"def {ten_ham}(*args):\n    return {than_moi}"
    return code_moi


def _thich_nghi_than_ham(than_ham, so_luong):
    if not than_ham:
        return ""

    if re.match(r"return\s+a\s*\+\s*b", than_ham):
        return "sum(args)"

    if re.match(r"return\s+a\s*\*\s*b", than_ham):
        return "math.prod(args) if hasattr(math, 'prod') else __import__('functools').reduce(lambda x, y: x * y, args, 1)"

    if re.match(r"return\s+a\s*-\s*b", than_ham):
        return "args[0] - sum(args[1:])"

    if re.match(r"return\s+a\s*/\s*b", than_ham):
        return "args[0] / args[1] if len(args) >= 2 else 0"

    if "max(" in than_ham:
        return "max(args)"

    if "min(" in than_ham:
        return "min(args)"

    if "sum" in than_ham and "len" in than_ham:
        return "sum(args) / len(args) if args else 0"

    return ""


# ================================================================
# THÍCH NGHI CÁCH GIẢI
# ================================================================
def _thich_nghi_cach_giai(node_goc, noi_dung, loai_task, yeu_to):
    cach_giai_goc = _lay(node_goc, "cach_giai", {}) or {}
    if not isinstance(cach_giai_goc, dict):
        cach_giai_goc = {"mo_ta": str(cach_giai_goc)}

    cach_giai_moi = dict(cach_giai_goc)

    if "mo_ta" in cach_giai_moi:
        mo_ta_goc = cach_giai_moi["mo_ta"]
        cach_giai_moi["mo_ta"] = (
            f"[Mượn từ '{_lay(node_goc, 'ten', '')}'] {mo_ta_goc}"
        )
    else:
        cach_giai_moi["mo_ta"] = cach_giai_goc.get("mo_ta", "")

    cach_giai_moi["muon_tu_ten"] = _lay(node_goc, "ten", "")
    cach_giai_moi["muon_tu_id"] = _lay(node_goc, "id", "")

    return cach_giai_moi


# ================================================================
# THÍCH NGHI HÀNH ĐỘNG
# ================================================================
def _thich_nghi_hanh_dong(node_goc, noi_dung, loai_task, yeu_to):
    hanh_dong_goc = _lay(node_goc, "hanh_dong", {}) or {}
    if not isinstance(hanh_dong_goc, dict):
        hanh_dong_goc = {"loai": str(hanh_dong_goc)}

    hanh_dong_moi = dict(hanh_dong_goc)

    code_cu = hanh_dong_moi.get("code") or ""

    if code_cu:
        code_moi = _thich_nghi_code_theo_task(code_cu, noi_dung, yeu_to)
        hanh_dong_moi["code"] = code_moi

        if not code_moi:
            hanh_dong_moi["code"] = ""
            _ghi_log(
                "dai-nao",
                f"Không thích nghi được code từ node "
                f"'{_lay(node_goc, 'ten', '')}' — để trống.",
            )

    hanh_dong_moi["muon_tu_ten"] = _lay(node_goc, "ten", "")
    hanh_dong_moi["muon_tu_id"] = _lay(node_goc, "id", "")

    return hanh_dong_moi


def _thich_nghi_code_theo_task(code_cu, noi_dung, yeu_to):
    if not code_cu:
        return ""

    if "{{" in code_cu and "}}" in code_cu:
        try:
            from dai_nao.tao_code import thay_bien_trong_code
            bien = _tao_bien_tu_yeu_to(yeu_to, noi_dung)
            code_moi, _, _ = thay_bien_trong_code(code_cu, bien)
            if code_moi and code_moi != code_cu:
                return code_moi
        except ImportError:
            pass

    so_luong = _dem_tham_so_trong_noi_dung(noi_dung)

    if so_luong <= 0:
        return code_cu

    if "def " in code_cu:
        code_moi = _sinh_code_long(code_cu, so_luong)
        if code_moi:
            return code_moi

        khop = re.search(r"def\s+\w+\s*\(([^)]*)\)", code_cu)
        if khop:
            so_tham_so_cu = len([t for t in khop.group(1).split(",") if t.strip()])
            if so_tham_so_cu == so_luong:
                return code_cu
            return ""

    return code_cu


def _tao_bien_tu_yeu_to(yeu_to, noi_dung):
    yeu_to = yeu_to or {}
    bien = {}

    for k in ("hanh_dong", "doi_tuong", "thuoc_tinh", "rang_buoc", "ngu_canh"):
        if yeu_to.get(k):
            bien[k] = yeu_to[k]

    if noi_dung:
        bien["noi_dung"] = noi_dung
        bien["tieu_de"] = noi_dung[:80]

    bien.setdefault("ten_ham", "ham_moi")
    bien.setdefault("ten_class", "ClassMoi")
    bien.setdefault("ten_file", "main")
    bien.setdefault("thoi_gian", str(int(time.time())))

    return bien


# ================================================================
# FIX 2, 3, 4, 5: TÍNH ĐIỂM GIỐNG — CHẶT HƠN
# ================================================================
def _diem_giong(node, noi_dung, loai_task):
    """
    Tính điểm giống giữa node và task.

    FIX 2: Bắt buộc khớp lĩnh vực.
    FIX 3: Không cộng score.
    FIX 4: Từ đơn ≥ 5 ký tự.
    FIX 5: Yêu cầu khớp nhóm mới cộng mạnh.
    """
    if node is None:
        return 0.0

    diem = 0.0
    noi_dung_lower = (noi_dung or "").lower()

    # FIX 2: Khớp lĩnh vực — BẮT BUỘC
    lv_node = (_lay(node, "linh_vuc", "") or "").lower().strip()
    lv_task = (loai_task.get("linh_vuc", "") or "").lower().strip()
    if not lv_node or not lv_task or lv_node != lv_task:
        # Lĩnh vực không khớp → trả 0 luôn, không cần tính tiếp
        return 0.0

    diem += 5.0

    # FIX 5: Khớp nhóm (loai_van_de) — cộng mạnh
    lvd_node = (_lay(node, "loai_van_de", "") or "").lower().strip()
    nhom_task = (loai_task.get("nhom", "") or "").lower().strip()
    if lvd_node and nhom_task and lvd_node == nhom_task:
        diem += 8.0

    # Khớp tên node (từ nguyên)
    ten = (_lay(node, "ten", "") or "").lower().strip()
    if ten and ten in noi_dung_lower:
        diem += min(10.0, len(ten) * 0.5)
    else:
        # FIX 4: Chỉ khớp từ đơn dài ≥ 5 ký tự
        for tu in ten.split():
            if len(tu) >= DO_DAI_TU_TOI_THIEU and tu in noi_dung_lower:
                diem += 0.8

    # Khớp ngôn ngữ trong code
    nn_node = (_lay(node, "hanh_dong", {}) or {}).get("ngon_ngu", "")
    if nn_node and nn_node.lower() in noi_dung_lower:
        diem += 3.0

    # FIX 3: KHÔNG cộng score nữa

    return diem


def tim_nhanh_gan_giong(noi_dung, loai_task, cay):
    """Tìm nhánh gần giống nhất trong cây."""
    if not cay or not cay.goc or not noi_dung:
        return None

    tat_ca = cay.duyet_tat_ca()[:SO_NODE_TOI_DA_XET]

    tot_nhat = None
    diem_tot_nhat = 0.0

    for node in tat_ca:
        if _lay(node, "id") == "root":
            continue
        if bool(_lay(node, "blacklist", False)):
            continue

        co_noi_dung = bool(
            _lay(node, "cach_giai") or _lay(node, "quy_tac") or _lay(node, "hanh_dong")
        )
        if not co_noi_dung:
            continue

        diem = _diem_giong(node, noi_dung, loai_task)
        if diem > diem_tot_nhat:
            diem_tot_nhat = diem
            tot_nhat = node

    # FIX 1: Ngưỡng mượn 8.0
    if tot_nhat and diem_tot_nhat < NGUONG_DIEM_GIONG:
        _ghi_log(
            "dai-nao",
            f"Điểm giống cao nhất = {diem_tot_nhat} < {NGUONG_DIEM_GIONG} — không mượn.",
        )
        return None

    return tot_nhat


# ================================================================
# TẠO NHÁNH MỚI TỪ NHÁNH GỐC
# ================================================================
def muon_nhanh(node_goc, noi_dung, loai_task, yeu_to=None):
    if not node_goc:
        return None

    du_dieu_kien, ly_do = kiem_tra_dieu_kien_muon(node_goc)
    if not du_dieu_kien:
        _ghi_log("dai-nao", f"Không mượn được: {ly_do}")
        return None

    yeu_to = yeu_to or {}

    try:
        from dai_nao.cay_quyet_dinh import Nut
    except ImportError:
        _ghi_log("loi", "cay_quyet_dinh.py chưa có — không tạo được Nut.")
        return None

    id_moi = _tao_id()
    linh_vuc = loai_task.get("linh_vuc", "") or _lay(node_goc, "linh_vuc", "")
    nhom = loai_task.get("nhom", "") or _lay(node_goc, "loai_van_de", "")
    loai = loai_task.get("loai", "") or _lay(node_goc, "cach_giai_phap", "")

    cach_giai_moi = _thich_nghi_cach_giai(node_goc, noi_dung, loai_task, yeu_to)
    hanh_dong_moi = _thich_nghi_hanh_dong(node_goc, noi_dung, loai_task, yeu_to)

    node_moi = Nut({
        "id": id_moi,
        "ten": noi_dung[:80] if noi_dung else f"Mượn từ {_lay(node_goc, 'ten', '')}",
        "phien_ban": 1,
        "dieu_kien": {
            "chua": _trich_tu_khoa(noi_dung),
            "yeu_to_can": ["hanh_dong", "doi_tuong"],
        },
        "quy_tac": _lay(node_goc, "quy_tac", ""),
        "thuat_toan": _lay(node_goc, "thuat_toan", {}),
        "cach_giai": cach_giai_moi,
        "hanh_dong": hanh_dong_moi,
        "score": 0.7,
        "so_lan_thu": 0,
        "thanh_cong": 0,
        "that_bai": 0,
        "do_kho": _lay(node_goc, "do_kho", 0.5),
        "thoi_gian_uoc_tinh": _lay(node_goc, "thoi_gian_uoc_tinh", 0),
        "phu_thuoc": [],
        "uu_tien": max(30, int(_lay(node_goc, "uu_tien", 50) or 50) - 10),
        "nhanh_con": [],
        "chia_se_voi": [],
        "muon_tu": _lay(node_goc, "id", ""),
        "failed_paths": [],
        "blacklist": False,
        "linh_vuc": linh_vuc,
        "loai_van_de": nhom,
        "cach_giai_phap": loai,
        "ngu_canh_node": "",
        "ngay_tao": int(time.time()),
        "lan_dung_cuoi": 0,
    })

    _ghi_log(
        "dai-nao",
        f"Mượn nhánh từ '{_lay(node_goc, 'ten', '')}' "
        f"(score={_lay(node_goc, 'score')}) → node mới {id_moi}",
    )

    return node_moi


# ================================================================
# HÀM PHỤ
# ================================================================
def _trich_tu_khoa(noi_dung, so_tu=5):
    if not noi_dung:
        return []
    cac_tu = [t.strip(".,!?;:") for t in noi_dung.split()]
    loc = [t for t in cac_tu if len(t) >= 3]
    return loc[:so_tu]


def luu_nhanh_muon(node_moi, cay, id_cha=None):
    if not node_moi or not cay:
        return False

    if not cay.them_node(node_moi, id_cha):
        return False

    try:
        from dai_nao.ghi_nho import luu_node
        du_lieu = node_moi.sang_dict_phang()
        du_lieu["node_cha"] = id_cha or "root"
        luu_node(du_lieu)
        return True
    except Exception as e:
        _ghi_log("loi", f"Không lưu được nhánh mượn: {e}")
        return False


# ================================================================
# HÀM CHÍNH GỘP
# ================================================================
def tim_va_muon(noi_dung, loai_task, yeu_to=None, cay=None):
    if cay is None:
        try:
            from dai_nao.cay_quyet_dinh import cay_tu_mongo
            cay = cay_tu_mongo()
        except Exception:
            return None, None

    node_goc = tim_nhanh_gan_giong(noi_dung, loai_task, cay)
    if not node_goc:
        _ghi_log("dai-nao", "Không tìm thấy nhánh gần giống để mượn.")
        return None, None

    node_moi = muon_nhanh(node_goc, noi_dung, loai_task, yeu_to)
    if not node_moi:
        return None, None

    return node_moi, node_goc
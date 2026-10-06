"""
uu_tien.py - Xếp hạng ưu tiên node Rồng Thần.

Nhiệm vụ:
    - tinh_uu_tien(node): tính điểm ưu tiên cho 1 node.
    - xep_hang(danh_sach_node): xếp hạng nhiều node.
    - chon_node_tot_nhat(danh_sach_node): chọn node tốt nhất.
    - cap_nhat_uu_tien(node): cập nhật trường uu_tien của node.

Công thức tính ưu tiên:
    uu_tien = score × 0.35
             + kinh_nghiem × 0.20
             + do_moi × 0.15
             + do_kho × 0.15
             + do_pho_bien × 0.15

Trong đó:
    - score: 0.0 – 1.0 (điểm tổng hợp node).
    - kinh_nghiem: min(1.0, so_lan_thu / 50) — càng dùng nhiều càng ưu tiên.
    - do_moi: 1.0 - (thoi_gian_tu_lan_dung_cuoi / 30_ngày) — mới dùng càng ưu tiên.
    - do_kho: 1.0 - do_kho — dễ hơn thì ưu tiên.
    - do_pho_bien: min(1.0, thanh_cong / 20) — thành công nhiều thì ưu tiên.

Quy tắc:
    - Node blacklist → uu_tien = 0.
    - Node score < 0.5 → giảm 30%.
    - Node mượn (muon_tu) → giảm 10%.
    - Node có chia_se_voi → tăng 5%.

Trả về:
    - tinh_uu_tien() → float 0.0 – 1.0.
    - xep_hang() → list [(node, diem)] đã sắp xếp.
    - chon_node_tot_nhat() → Nut object hoặc None.

Tầng dữ liệu: Không.
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
# HẰNG SỐ
# ================================================================
TRONG_SO = {
    "score": 0.35,
    "kinh_nghiem": 0.20,
    "do_moi": 0.15,
    "do_kho": 0.15,
    "do_pho_bien": 0.15,
}

NGAY = 24 * 60 * 60  # 1 ngày (giây)
NGUONG_MOI = 30 * NGAY  # 30 ngày
NGUONG_KINH_NGHIEM = 50  # số lần thử để đạt kinh nghiệm tối đa
NGUONG_PHO_BIEN = 20  # số lần thành công để đạt phổ biến tối đa

NGUONG_SCORE_THAP = 0.5  # score < 0.5 → giảm 30%
GIAM_SCORE_THAP = 0.30
GIAM_MUON = 0.10
TANG_CHIA_SE = 0.05


# ================================================================
# TIỆN ÍCH
# ================================================================
def _lay(node, ten_truong, mac_dinh=None):
    """Lấy thuộc tính node (Nut object hoặc dict)."""
    if node is None:
        return mac_dinh
    if isinstance(node, dict):
        return node.get(ten_truong, mac_dinh)
    return getattr(node, ten_truong, mac_dinh)


def _dat(node, ten_truong, gia_tri):
    """Đặt thuộc tính node (Nut object hoặc dict)."""
    if node is None:
        return
    if isinstance(node, dict):
        node[ten_truong] = gia_tri
    else:
        setattr(node, ten_truong, gia_tri)


# ================================================================
# TÍNH THÀNH PHẦN
# ================================================================
def _tinh_kinh_nghiem(node):
    """Kinh nghiệm = số lần thử / 50 (tối đa 1.0)."""
    so_lan_thu = int(_lay(node, "so_lan_thu", 0) or 0)
    return min(1.0, so_lan_thu / NGUONG_KINH_NGHIEM)


def _tinh_do_moi(node):
    """Độ mới = 1.0 - (thời gian từ lần dùng cuối / 30 ngày)."""
    lan_dung_cuoi = int(_lay(node, "lan_dung_cuoi", 0) or 0)
    if lan_dung_cuoi <= 0:
        return 0.5  # chưa dùng bao giờ → trung bình

    thoi_gian = int(time.time()) - lan_dung_cuoi
    if thoi_gian < 0:
        return 1.0  # vừa dùng xong
    if thoi_gian > NGUONG_MOI:
        return 0.0  # lâu rồi không dùng

    return round(1.0 - (thoi_gian / NGUONG_MOI), 3)


def _tinh_do_kho(node):
    """Độ khó: dễ → ưu tiên cao. Trả về 1.0 - do_kho."""
    do_kho = float(_lay(node, "do_kho", 0.5) or 0.5)
    do_kho = max(0.0, min(1.0, do_kho))
    return 1.0 - do_kho


def _tinh_do_pho_bien(node):
    """Độ phổ biến = số lần thành công / 20 (tối đa 1.0)."""
    thanh_cong = int(_lay(node, "thanh_cong", 0) or 0)
    return min(1.0, thanh_cong / NGUONG_PHO_BIEN)


# ================================================================
# ĐIỀU CHỈNH SAU KHI TÍNH
# ================================================================
def _dieu_chinh(uu_tien, node):
    """
    Điều chỉnh uu_tien theo các quy tắc đặc biệt.
    """
    score = float(_lay(node, "score", 0.0) or 0.0)
    muon_tu = _lay(node, "muon_tu", "") or ""
    chia_se_voi = _lay(node, "chia_se_voi", []) or []

    # 1. Score thấp → giảm 30%
    if score < NGUONG_SCORE_THAP:
        uu_tien = uu_tien * (1.0 - GIAM_SCORE_THAP)

    # 2. Node mượn → giảm 10%
    if muon_tu:
        uu_tien = uu_tien * (1.0 - GIAM_MUON)

    # 3. Có chia sẻ → tăng 5%
    if chia_se_voi:
        uu_tien = uu_tien * (1.0 + TANG_CHIA_SE)

    return round(min(1.0, max(0.0, uu_tien)), 3)


# ================================================================
# TÍNH ƯU TIÊN CHÍNH
# ================================================================
def tinh_uu_tien(node):
    """
    Tính điểm ưu tiên cho 1 node.

    Trả về: float 0.0 – 1.0.
    """
    if node is None:
        return 0.0

    # Node blacklist → 0
    if bool(_lay(node, "blacklist", False)):
        return 0.0

    # Lấy từng thành phần
    score = float(_lay(node, "score", 0.0) or 0.0)
    score = max(0.0, min(1.0, score))

    kinh_nghiem = _tinh_kinh_nghiem(node)
    do_moi = _tinh_do_moi(node)
    do_kho = _tinh_do_kho(node)
    do_pho_bien = _tinh_do_pho_bien(node)

    # Công thức
    uu_tien = (
        score * TRONG_SO["score"]
        + kinh_nghiem * TRONG_SO["kinh_nghiem"]
        + do_moi * TRONG_SO["do_moi"]
        + do_kho * TRONG_SO["do_kho"]
        + do_pho_bien * TRONG_SO["do_pho_bien"]
    )

    # Điều chỉnh
    uu_tien = _dieu_chinh(uu_tien, node)

    return round(uu_tien, 3)


# ================================================================
# XẾP HẠNG NHIỀU NODE
# ================================================================
def xep_hang(danh_sach_node, nguong_toi_thieu=0.0):
    """
    Xếp hạng nhiều node theo ưu tiên giảm dần.

    danh_sach_node: list Nut object hoặc dict.
    nguong_toi_thieu: bỏ node có ưu tiên < ngưỡng.

    Trả về: list [(node, diem)] đã sắp xếp.
    """
    if not danh_sach_node:
        return []

    ket_qua = []
    for node in danh_sach_node:
        diem = tinh_uu_tien(node)
        if diem >= nguong_toi_thieu:
            ket_qua.append((node, diem))

    # Sắp xếp giảm dần theo điểm
    ket_qua.sort(key=lambda x: x[1], reverse=True)
    return ket_qua


# ================================================================
# CHỌN NODE TỐT NHẤT
# ================================================================
def chon_node_tot_nhat(danh_sach_node, nguong_toi_thieu=0.3):
    """
    Chọn node có ưu tiên cao nhất.

    Trả về: Nut object (hoặc dict) hay None.
    """
    xep_hang_list = xep_hang(danh_sach_node, nguong_toi_thieu)
    if not xep_hang_list:
        return None
    return xep_hang_list[0][0]


# ================================================================
# CẬP NHẬT ƯU TIÊN VÀO NODE
# ================================================================
def cap_nhat_uu_tien(node):
    """
    Tính và cập nhật trường uu_tien (0–100) của node.
    Trả về giá trị mới.
    """
    if node is None:
        return 0

    diem = tinh_uu_tien(node)
    gia_tri_moi = int(diem * 100)
    _dat(node, "uu_tien", gia_tri_moi)
    return gia_tri_moi


# ================================================================
# LẤY CHI TIẾT ƯU TIÊN
# ================================================================
def chi_tiet_uu_tien(node):
    """
    Trả về chi tiết từng thành phần ưu tiên của node.

    Trả về dict:
        {
            score, kinh_nghiem, do_moi, do_kho, do_pho_bien,
            uu_tien_truoc_dieu_chinh, uu_tien_sau_dieu_chinh,
            dieu_chinh: { giam_score_thap, giam_muon, tang_chia_se }
        }
    """
    if node is None:
        return {}

    score = max(0.0, min(1.0, float(_lay(node, "score", 0.0) or 0.0)))
    kinh_nghiem = _tinh_kinh_nghiem(node)
    do_moi = _tinh_do_moi(node)
    do_kho = _tinh_do_kho(node)
    do_pho_bien = _tinh_do_pho_bien(node)

    truoc = (
        score * TRONG_SO["score"]
        + kinh_nghiem * TRONG_SO["kinh_nghiem"]
        + do_moi * TRONG_SO["do_moi"]
        + do_kho * TRONG_SO["do_kho"]
        + do_pho_bien * TRONG_SO["do_pho_bien"]
    )

    sau = _dieu_chinh(truoc, node)

    return {
        "score": round(score, 3),
        "kinh_nghiem": round(kinh_nghiem, 3),
        "do_moi": round(do_moi, 3),
        "do_kho": round(do_kho, 3),
        "do_pho_bien": round(do_pho_bien, 3),
        "uu_tien_truoc_dieu_chinh": round(truoc, 3),
        "uu_tien_sau_dieu_chinh": round(sau, 3),
        "dieu_chinh": {
            "giam_score_thap": score < NGUONG_SCORE_THAP,
            "giam_muon": bool(_lay(node, "muon_tu")),
            "tang_chia_se": bool(_lay(node, "chia_se_voi")),
            "blacklist": bool(_lay(node, "blacklist", False)),
        },
    }


# ================================================================
# HÀM PHỤ: XẾP HẠNG KÈM LÝ DO
# ================================================================
def xep_hang_kem_ly_do(danh_sach_node):
    """
    Xếp hạng node kèm lý do (cho log/debug).

    Trả về: list dict [{ node, diem, chi_tiet }].
    """
    if not danh_sach_node:
        return []

    ket_qua = []
    for node in danh_sach_node:
        diem = tinh_uu_tien(node)
        ket_qua.append({
            "node": node,
            "diem": diem,
            "chi_tiet": chi_tiet_uu_tien(node),
        })

    ket_qua.sort(key=lambda x: x["diem"], reverse=True)
    return ket_qua


# ================================================================
# HÀM PHỤ: TÓM TẮT XẾP HẠNG
# ================================================================
def tom_tat_xep_hang(danh_sach_node, so_hien=5):
    """Tạo chuỗi tóm tắt xếp hạng."""
    xep_hang_list = xep_hang(danh_sach_node)

    if not xep_hang_list:
        return "Không có node nào."

    phan = []
    for i, (node, diem) in enumerate(xep_hang_list[:so_hien], 1):
        ten = _lay(node, "ten", "") or _lay(node, "id", "?")
        phan.append(f"{i}. [{diem:.3f}] {ten[:60]}")

    return "\n".join(phan)


# ================================================================
# HÀM PHỤ: LỌC THEO NGƯỠNG
# ================================================================
def loc_theo_nguong(danh_sach_node, nguong=0.5):
    """Lọc node có ưu tiên >= ngưỡng."""
    return [node for node, diem in xep_hang(danh_sach_node) if diem >= nguong]


# ================================================================
# HÀM PHỤ: TOP N
# ================================================================
def lay_top_n(danh_sach_node, n=3):
    """Lấy N node có ưu tiên cao nhất."""
    xep_hang_list = xep_hang(danh_sach_node)
    return [node for node, _ in xep_hang_list[:n]]


# ================================================================
# HÀM PHỤ: SO SÁNH 2 NODE
# ================================================================
def so_sanh_hai_node(node_a, node_b):
    """
    So sánh 2 node theo ưu tiên.

    Trả về: -1 nếu a < b, 0 nếu bằng, 1 nếu a > b.
    """
    diem_a = tinh_uu_tien(node_a)
    diem_b = tinh_uu_tien(node_b)

    if diem_a > diem_b:
        return 1
    if diem_a < diem_b:
        return -1
    return 0
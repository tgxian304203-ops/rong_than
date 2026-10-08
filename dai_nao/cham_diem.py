"""
cham_diem.py - Chấm điểm node cây quyết định Rồng Thần.

Nhiệm vụ:
    - cham_diem(node): tính score cho 1 node.
    - cham_diem_nhieu(danh_sach): chấm điểm nhiều node, sắp xếp.
    - lay_do_tin_cay(node, yeu_to): ước lượng độ tin cậy của node.

Công thức (theo Phần 4):
    score = tỷ_lệ_thành_công * 0.4
          + độ_tin_cậy       * 0.2
          + ưu_tiên          * 0.2
          + độ_khó           * 0.2

ĐÃ NÂNG CẤP (Giai đoạn 1 — học pattern):
    - FIX 1: Node có pattern_regex → +0.10 (tổng quát, dùng nhiều lần).
    - FIX 2: Node có placeholder_map → +0.10 (thay biến được).
    - FIX 3: Node code cứng (không placeholder, không regex) → -0.10.
    - FIX 4: Node regex + placeholder → +0.15 (bonus tổng quát cao nhất).
    - FIX 5: Chặn score tối đa 1.0, tối thiểu 0.0.

Các fix cũ giữ nguyên:
    - Node chưa dùng → ty_le = 0.5 (không 1.0).
    - uu_tien mặc định = 30.
    - Node rỗng nội dung → 0 điểm.
    - Ngưỡng dùng = 0.75.

Quy tắc:
    - Node fail 3 lần → blacklist (score = 0).
    - Node fail > 50% → giảm 20%.
    - Score > 0.75 → dùng được.
    - Score > 0.95 → tin cậy cao.
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
    "ty_le_thanh_cong": 0.4,
    "do_tin_cay": 0.2,
    "uu_tien": 0.2,
    "do_kho": 0.2,
}

SO_LAN_FAIL_BLACKLIST = 3
TY_LE_FAIL_GIAM_DIEM = 0.5
MUC_GIAM_DIEM = 0.2

NGUONG_DUNG = 0.75
NGUONG_TIN_CAY_CAO = 0.95
NGUONG_MUON_NHANH = 0.5

TY_LE_MAC_DINH_NODE_MOI = 0.5
UU_TIEN_MAC_DINH_NODE_MOI = 30

# FIX 1, 2, 3, 4: Điểm thưởng cho node tổng quát
DIEM_CO_REGEX = 0.10
DIEM_CO_PLACEHOLDER = 0.10
DIEM_CODE_CUNG = -0.10
DIEM_REGEX_VA_PLACEHOLDER = 0.15  # Bonus cao nhất


# ================================================================
# LẤY THUỘC TÍNH NODE AN TOÀN
# ================================================================
def _lay(node, ten_truong, mac_dinh=None):
    if node is None:
        return mac_dinh
    if isinstance(node, dict):
        return node.get(ten_truong, mac_dinh)
    return getattr(node, ten_truong, mac_dinh)


# ================================================================
# KIỂM TRA NODE CÓ NỘI DUNG THỰC
# ================================================================
def kiem_tra_node_co_noi_dung_thuc(node):
    """
    Node phải có nội dung thực:
        - hanh_dong.code không rỗng, HOẶC
        - cach_giai.mo_ta không rỗng, HOẶC
        - hanh_dong.loai == "tra_web"
    """
    if node is None:
        return False

    hanh_dong = _lay(node, "hanh_dong", {}) or {}
    if isinstance(hanh_dong, dict):
        code = (hanh_dong.get("code") or "").strip()
        loai = (hanh_dong.get("loai") or "").strip()
        if code:
            return True
        if loai == "tra_web":
            return True

    cach_giai = _lay(node, "cach_giai", {}) or {}
    if isinstance(cach_giai, dict):
        mo_ta = (cach_giai.get("mo_ta") or "").strip()
        if mo_ta:
            return True
    elif isinstance(cach_giai, str) and cach_giai.strip():
        return True

    return False


# ================================================================
# FIX 1, 2, 3, 4: TÍNH ĐIỂM TỔNG QUÁT
# ================================================================
def _diem_tong_quat(node):
    """
    Tính điểm thưởng/phạt dựa trên độ "tổng quát" của node.

    FIX 1: Có pattern_regex → +0.10
    FIX 2: Có placeholder_map → +0.10
    FIX 3: Code cứng (không regex, không placeholder) → -0.10
    FIX 4: Có CẢ regex VÀ placeholder → +0.15 (bonus gộp, thay vì +0.20)
    """
    if node is None:
        return 0.0

    pattern_regex = (_lay(node, "pattern_regex", "") or "").strip()
    placeholder_map = _lay(node, "placeholder_map", {}) or {}
    co_placeholder = isinstance(placeholder_map, dict) and bool(placeholder_map)

    hanh_dong = _lay(node, "hanh_dong", {}) or {}
    if isinstance(hanh_dong, dict):
        code = (hanh_dong.get("code") or "").strip()
    else:
        code = ""

    # FIX 4: Node vừa có regex vừa có placeholder → bonus cao nhất
    if pattern_regex and co_placeholder:
        return DIEM_REGEX_VA_PLACEHOLDER

    # FIX 1: Có regex → +0.10
    if pattern_regex:
        return DIEM_CO_REGEX

    # FIX 2: Có placeholder → +0.10
    if co_placeholder:
        return DIEM_CO_PLACEHOLDER

    # FIX 3: Code cứng (không regex, không placeholder, có code) → -0.10
    if code:
        return DIEM_CODE_CUNG

    return 0.0


# ================================================================
# ĐỘ TIN CẬY
# ================================================================
def lay_do_tin_cay(node, yeu_to=None):
    if node is None:
        return 0.0

    thanh_cong = int(_lay(node, "thanh_cong", 0) or 0)
    so_lan_thu = int(_lay(node, "so_lan_thu", 0) or 0)

    if so_lan_thu == 0:
        ty_le = TY_LE_MAC_DINH_NODE_MOI
    else:
        ty_le = thanh_cong / so_lan_thu

    diem_kinh_nghiem = min(0.2, so_lan_thu * 0.01)

    diem_cach_giai = 0.0
    cach_giai = _lay(node, "cach_giai", {}) or {}
    hanh_dong = _lay(node, "hanh_dong", {}) or {}
    if cach_giai:
        diem_cach_giai += 0.05
    if hanh_dong:
        diem_cach_giai += 0.05

    diem_yeu_to = 0.0
    if yeu_to and isinstance(yeu_to, dict):
        dieu_kien = _lay(node, "dieu_kien", {}) or {}
        yeu_cau = dieu_kien.get("yeu_to_can", []) if isinstance(dieu_kien, dict) else []
        khop = sum(1 for yt in yeu_cau if yeu_to.get(yt))
        diem_yeu_to = min(0.1, khop * 0.03)

    do_tin_cay = ty_le + diem_kinh_nghiem + diem_cach_giai + diem_yeu_to
    return round(min(1.0, max(0.0, do_tin_cay)), 3)


# ================================================================
# HÀM CHÍNH: CHẤM ĐIỂM 1 NODE
# ================================================================
def cham_diem(node, yeu_to=None):
    """
    Tính score cho 1 node.

    FIX 1-4: Thêm điểm tổng quát vào score cuối.
    """
    if node is None:
        return 0.0

    if bool(_lay(node, "blacklist", False)):
        return 0.0

    if not kiem_tra_node_co_noi_dung_thuc(node):
        return 0.0

    thanh_cong = int(_lay(node, "thanh_cong", 0) or 0)
    so_lan_thu = int(_lay(node, "so_lan_thu", 0) or 0)

    if so_lan_thu <= 0:
        ty_le_thanh_cong = TY_LE_MAC_DINH_NODE_MOI
    else:
        ty_le_thanh_cong = thanh_cong / so_lan_thu

    do_tin_cay = lay_do_tin_cay(node, yeu_to)

    uu_tien = int(_lay(node, "uu_tien", UU_TIEN_MAC_DINH_NODE_MOI) or UU_TIEN_MAC_DINH_NODE_MOI)
    uu_tien_chuan = uu_tien / 100.0

    do_kho = float(_lay(node, "do_kho", 0.5) or 0.5)
    do_kho_chuan = 1.0 - do_kho

    score = (
        ty_le_thanh_cong * TRONG_SO["ty_le_thanh_cong"]
        + do_tin_cay * TRONG_SO["do_tin_cay"]
        + uu_tien_chuan * TRONG_SO["uu_tien"]
        + do_kho_chuan * TRONG_SO["do_kho"]
    )

    # FIX 1-4: Cộng điểm tổng quát
    score += _diem_tong_quat(node)

    that_bai = int(_lay(node, "that_bai", 0) or 0)
    if so_lan_thu > 0 and (that_bai / so_lan_thu) > TY_LE_FAIL_GIAM_DIEM:
        score = max(0.0, score - MUC_GIAM_DIEM)

    if that_bai >= SO_LAN_FAIL_BLACKLIST:
        score = 0.0

    # FIX 5: Chặn score trong khoảng [0.0, 1.0]
    return round(min(1.0, max(0.0, score)), 3)


# ================================================================
# HÀM PHỤ: CHẤM ĐIỂM NHIỀU NODE
# ================================================================
def cham_diem_nhieu(danh_sach_node, yeu_to=None):
    if not danh_sach_node:
        return []

    ket_qua = []
    for node in danh_sach_node:
        diem = cham_diem(node, yeu_to)
        ket_qua.append((node, diem))

    ket_qua.sort(key=lambda x: x[1], reverse=True)
    return ket_qua


# ================================================================
# HÀM PHỤ: LỌC NODE ĐỦ ĐIỂM
# ================================================================
def loc_node_du_diem(danh_sach_node, yeu_to=None, nguong=NGUONG_DUNG):
    ket_qua = cham_diem_nhieu(danh_sach_node, yeu_to)
    return [item for item in ket_qua if item[1] >= nguong]


# ================================================================
# HÀM PHỤ: LẤY NODE TỐT NHẤT
# ================================================================
def lay_node_tot_nhat(danh_sach_node, yeu_to=None):
    ket_qua = cham_diem_nhieu(danh_sach_node, yeu_to)
    if not ket_qua:
        return None
    return ket_qua[0][0]


# ================================================================
# HÀM PHỤ: XẾP HẠNG ƯU TIÊN
# ================================================================
def xep_hang_uu_tien(danh_sach_node):
    def khoa(node):
        uu_tien = int(_lay(node, "uu_tien", UU_TIEN_MAC_DINH_NODE_MOI) or UU_TIEN_MAC_DINH_NODE_MOI)
        score = float(_lay(node, "score", 0.0) or 0.0)
        return (uu_tien, score)

    return sorted(danh_sach_node, key=khoa, reverse=True)


# ================================================================
# HÀM PHỤ: ĐÁNH GIÁ MỨC TIN CẬY
# ================================================================
def danh_gia_muc_tin_cay(score):
    if score is None:
        return "hoi_lai_nhieu"
    if score > 0.95:
        return "ra_lenh_luon"
    if score >= 0.90:
        return "ra_lenh_ghi_chu"
    if score >= 0.70:
        return "hoi_lai_1_cau"
    return "hoi_lai_nhieu"


# ================================================================
# HÀM PHỤ: CẬP NHẬT SCORE SAU KHI DÙNG
# ================================================================
def cap_nhat_score_sau_dung(node, thanh_cong=True, duong_dan_sai=None):
    if node is None:
        return 0.0

    so_lan_thu = int(_lay(node, "so_lan_thu", 0) or 0) + 1
    thanh_cong_cu = int(_lay(node, "thanh_cong", 0) or 0)
    that_bai_cu = int(_lay(node, "that_bai", 0) or 0)

    if thanh_cong:
        thanh_cong_moi = thanh_cong_cu + 1
        that_bai_moi = that_bai_cu
    else:
        thanh_cong_moi = thanh_cong_cu
        that_bai_moi = that_bai_cu + 1

    if isinstance(node, dict):
        node["so_lan_thu"] = so_lan_thu
        node["thanh_cong"] = thanh_cong_moi
        node["that_bai"] = that_bai_moi
        node["lan_dung_cuoi"] = int(time.time())
        if duong_dan_sai:
            failed = node.get("failed_paths", [])
            if duong_dan_sai not in failed:
                failed.append(duong_dan_sai)
            node["failed_paths"] = failed
        if that_bai_moi >= SO_LAN_FAIL_BLACKLIST:
            node["blacklist"] = True
    else:
        node.so_lan_thu = so_lan_thu
        node.thanh_cong = thanh_cong_moi
        node.that_bai = that_bai_moi
        node.lan_dung_cuoi = int(time.time())
        if duong_dan_sai:
            if duong_dan_sai not in node.failed_paths:
                node.failed_paths.append(duong_dan_sai)
        if that_bai_moi >= SO_LAN_FAIL_BLACKLIST:
            node.blacklist = True

    score_moi = cham_diem(node)
    return score_moi


# ================================================================
# HÀM PHỤ: KIỂM TRA NODE CÓ PHẢI "TỔNG QUÁT" KHÔNG
# ================================================================
def node_co_tong_quat(node):
    """FIX 1+2: Node có regex hoặc placeholder → tổng quát."""
    if node is None:
        return False
    pattern_regex = (_lay(node, "pattern_regex", "") or "").strip()
    placeholder_map = _lay(node, "placeholder_map", {}) or {}
    return bool(pattern_regex) or bool(isinstance(placeholder_map, dict) and placeholder_map)
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

ĐÃ SỬA (fix "ngáo"):
    - FIX 1: Node chưa dùng (so_lan_thu=0) → ty_le = 0.5 (KHÔNG phải 1.0).
    - FIX 2: uu_tien mặc định = 30 (KHÔNG phải 50) → node mới khó vượt 0.7.
    - FIX 3: Node không có cach_giai.mo_ta và không có hanh_dong.code → score = 0.
    - FIX 4: Ngưỡng dùng = 0.75 (chặt hơn 0.7).
    - FIX 5: Thêm hàm kiem_tra_node_co_noi_dung_thuc.

Quy tắc:
    - Node fail 3 lần → blacklist (score = 0).
    - Node fail > 50% → giảm 20%.
    - Score < 0.5 → không dùng.
    - Score > 0.75 → dùng được.
    - Score > 0.95 → tin cậy cao, ra lệnh luôn.
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

# FIX 4: Nâng ngưỡng dùng từ 0.7 → 0.75
NGUONG_DUNG = 0.75
NGUONG_TIN_CAY_CAO = 0.95
NGUONG_MUON_NHANH = 0.5

# FIX 1 + FIX 2: Giá trị mặc định cho node mới
TY_LE_MAC_DINH_NODE_MOI = 0.5
UU_TIEN_MAC_DINH_NODE_MOI = 30


# ================================================================
# LẤY THUỘC TÍNH NODE AN TOÀN
# ================================================================
def _lay(node, ten_truong, mac_dinh=None):
    """Lấy thuộc tính node — hỗ trợ cả object Nut và dict."""
    if node is None:
        return mac_dinh
    if isinstance(node, dict):
        return node.get(ten_truong, mac_dinh)
    return getattr(node, ten_truong, mac_dinh)


# ================================================================
# FIX 3 + FIX 5: KIỂM TRA NODE CÓ NỘI DUNG THỰC
# ================================================================
def kiem_tra_node_co_noi_dung_thuc(node):
    """
    Node phải có nội dung thực mới được tính điểm:
        - hanh_dong.code không rỗng, HOẶC
        - cach_giai.mo_ta không rỗng, HOẶC
        - hanh_dong.loai == "tra_web" (được phép rỗng code)
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
# ĐỘ TIN CẬY
# ================================================================
def lay_do_tin_cay(node, yeu_to=None):
    """
    Ước lượng độ tin cậy của node.

    FIX 1: Node chưa dùng (so_lan_thu=0) → ty_le = 0.5 (không phải 0.5 base nữa,
    mà tính toán riêng để không thổi phồng).
    """
    if node is None:
        return 0.0

    thanh_cong = int(_lay(node, "thanh_cong", 0) or 0)
    so_lan_thu = int(_lay(node, "so_lan_thu", 0) or 0)

    if so_lan_thu == 0:
        # Node mới tinh — chưa có bằng chứng → tin cậy trung bình thấp
        ty_le = TY_LE_MAC_DINH_NODE_MOI
    else:
        ty_le = thanh_cong / so_lan_thu

    # Điểm cộng kinh nghiệm (tối đa 0.2)
    diem_kinh_nghiem = min(0.2, so_lan_thu * 0.01)

    # Điểm cộng có cách giải cụ thể
    diem_cach_giai = 0.0
    cach_giai = _lay(node, "cach_giai", {}) or {}
    hanh_dong = _lay(node, "hanh_dong", {}) or {}
    if cach_giai:
        diem_cach_giai += 0.05
    if hanh_dong:
        diem_cach_giai += 0.05

    # Điểm cộng khớp yếu tố
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

    FIX 1: Node chưa dùng (so_lan_thu=0) → ty_le_thanh_cong = 0.5.
    FIX 2: uu_tien mặc định = 30.
    FIX 3: Node rỗng nội dung → score = 0.
    """
    if node is None:
        return 0.0

    # --- Kiểm tra blacklist ---
    if bool(_lay(node, "blacklist", False)):
        return 0.0

    # FIX 3: Node rỗng nội dung → 0 điểm
    if not kiem_tra_node_co_noi_dung_thuc(node):
        return 0.0

    # --- Tỷ lệ thành công ---
    thanh_cong = int(_lay(node, "thanh_cong", 0) or 0)
    so_lan_thu = int(_lay(node, "so_lan_thu", 0) or 0)

    if so_lan_thu <= 0:
        # FIX 1: KHÔNG dùng 1.0 nữa — dùng 0.5
        ty_le_thanh_cong = TY_LE_MAC_DINH_NODE_MOI
    else:
        ty_le_thanh_cong = thanh_cong / so_lan_thu

    # --- Độ tin cậy ---
    do_tin_cay = lay_do_tin_cay(node, yeu_to)

    # --- Ưu tiên ---
    # FIX 2: mặc định 30 (thay vì 50)
    uu_tien = int(_lay(node, "uu_tien", UU_TIEN_MAC_DINH_NODE_MOI) or UU_TIEN_MAC_DINH_NODE_MOI)
    uu_tien_chuan = uu_tien / 100.0

    # --- Độ khó ---
    do_kho = float(_lay(node, "do_kho", 0.5) or 0.5)
    do_kho_chuan = 1.0 - do_kho

    # --- Công thức Phần 4 ---
    score = (
        ty_le_thanh_cong * TRONG_SO["ty_le_thanh_cong"]
        + do_tin_cay * TRONG_SO["do_tin_cay"]
        + uu_tien_chuan * TRONG_SO["uu_tien"]
        + do_kho_chuan * TRONG_SO["do_kho"]
    )

    # --- Giảm điểm nếu fail > 50% ---
    that_bai = int(_lay(node, "that_bai", 0) or 0)
    if so_lan_thu > 0 and (that_bai / so_lan_thu) > TY_LE_FAIL_GIAM_DIEM:
        score = max(0.0, score - MUC_GIAM_DIEM)

    # --- Blacklist nếu fail ≥ 3 lần ---
    if that_bai >= SO_LAN_FAIL_BLACKLIST:
        score = 0.0

    return round(min(1.0, max(0.0, score)), 3)


# ================================================================
# HÀM PHỤ: CHẤM ĐIỂM NHIỀU NODE
# ================================================================
def cham_diem_nhieu(danh_sach_node, yeu_to=None):
    """Chấm điểm nhiều node và sắp xếp theo score giảm dần."""
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
    """Lọc các node có score ≥ nguong."""
    ket_qua = cham_diem_nhieu(danh_sach_node, yeu_to)
    return [item for item in ket_qua if item[1] >= nguong]


# ================================================================
# HÀM PHỤ: LẤY NODE TỐT NHẤT
# ================================================================
def lay_node_tot_nhat(danh_sach_node, yeu_to=None):
    """Trả về node có score cao nhất (hoặc None)."""
    ket_qua = cham_diem_nhieu(danh_sach_node, yeu_to)
    if not ket_qua:
        return None
    return ket_qua[0][0]


# ================================================================
# HÀM PHỤ: XẾP HẠNG ƯU TIÊN
# ================================================================
def xep_hang_uu_tien(danh_sach_node):
    """Xếp hạng node theo uu_tien rồi đến score."""
    def khoa(node):
        uu_tien = int(_lay(node, "uu_tien", UU_TIEN_MAC_DINH_NODE_MOI) or UU_TIEN_MAC_DINH_NODE_MOI)
        score = float(_lay(node, "score", 0.0) or 0.0)
        return (uu_tien, score)

    return sorted(danh_sach_node, key=khoa, reverse=True)


# ================================================================
# HÀM PHỤ: ĐÁNH GIÁ MỨC TIN CẬY
# ================================================================
def danh_gia_muc_tin_cay(score):
    """
    Đánh giá mức tin cậy dựa trên score.
    """
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
    """Cập nhật node sau khi dùng."""
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
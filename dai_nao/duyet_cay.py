"""
duyet_cay.py - Thuật toán duyệt cây quyết định Rồng Thần.

Nhiệm vụ:
    - duyet_cay(noi_dung, loai_task, yeu_to): duyệt cây, trả về node khớp nhất.

ĐÃ NÂNG CẤP (Giai đoạn 1 — học pattern):
    - FIX 1: Thêm _diem_regex(node, noi_dung) — node có pattern_regex khớp
             → +10 điểm (ưu tiên cao nhất).
    - FIX 2: Node có pattern_regex khớp → KHÔNG cần dieu_kien.chua khớp nữa
             (vì pattern là điều kiện mạnh hơn).
    - FIX 3: Node có placeholder_map → +2 điểm (điểm "tổng quát").
    - FIX 4: Bổ sung vào _thu_thap_tat_ca để lay_tat_ca_node_khop cũng dùng regex.

Các fix cũ giữ nguyên:
    - Bỏ bonus sai cho hanh_dong/cach_giai.
    - Node không dieu_kien → KHÔNG khớp.
    - So sánh lĩnh vực bằng ==.

Trả về:
    Nut object hoặc None.
"""

import re


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
# ĐIỂM KHỚP THEO TẦNG
# ================================================================
DIEM_TANG = {
    "linh_vuc": 3.0,
    "loai_van_de": 5.0,
    "cach_giai_phap": 7.0,
    "ngu_canh_node": 2.0,
}

# FIX 1: Điểm thưởng cho node có pattern_regex khớp
DIEM_REGEX_KHOP = 10.0

# FIX 3: Điểm thưởng cho node có placeholder_map
DIEM_CO_PLACEHOLDER = 2.0


# ================================================================
# TÌM CÂY TỪ KHO 2
# ================================================================
def _lay_cay():
    try:
        from dai_nao.cay_quyet_dinh import cay_tu_mongo
        return cay_tu_mongo()
    except Exception as e:
        _ghi_log("loi", f"Không lấy được cây: {e}")
        return None


# ================================================================
# FIX 1: TÍNH ĐIỂM REGEX
# ================================================================
def _diem_regex(node, noi_dung):
    """
    Tính điểm nếu node có pattern_regex khớp task.

    FIX 1: Khớp regex → +DIEM_REGEX_KHOP (10 điểm).

    Trả về: (diem, khop_bool).
    """
    if not node:
        return 0.0, False

    # Lấy pattern_regex
    pattern = getattr(node, "pattern_regex", "") or ""
    if not pattern or not pattern.strip():
        return 0.0, False

    try:
        if re.search(pattern, noi_dung):
            return DIEM_REGEX_KHOP, True
    except re.error:
        pass

    return 0.0, False


# ================================================================
# FIX 3: ĐIỂM PLACEHOLDER
# ================================================================
def _diem_placeholder(node):
    """FIX 3: Node có placeholder_map → +2 điểm (tổng quát)."""
    if not node:
        return 0.0
    placeholder_map = getattr(node, "placeholder_map", {}) or {}
    if isinstance(placeholder_map, dict) and placeholder_map:
        return DIEM_CO_PLACEHOLDER
    return 0.0


# ================================================================
# KIỂM TRA ĐIỀU KIỆN KHỚP
# ================================================================
def _kiem_tra_dieu_kien(node, noi_dung, yeu_to):
    """
    Kiểm tra node có khớp với task không.

    FIX 2: Nếu node có pattern_regex → kiểm tra regex TRƯỚC.
           Nếu khớp regex → KHÔNG cần dieu_kien.chua khớp.

    Trả về: (True/False, điểm_khớp).
    """
    diem = 0.0

    # FIX 2: Ưu tiên kiểm tra regex trước
    diem_regex, khop_regex = _diem_regex(node, noi_dung)
    if khop_regex:
        return True, diem_regex

    # Nếu node có regex nhưng KHÔNG khớp → không xét dieu_kien nữa
    pattern = getattr(node, "pattern_regex", "") or ""
    if pattern and pattern.strip():
        return False, 0.0

    # --- Kiểm tra dieu_kien bình thường ---
    dieu_kien = node.dieu_kien

    if not dieu_kien:
        return False, 0.0

    # Trường hợp điều kiện là chuỗi
    if isinstance(dieu_kien, str):
        if dieu_kien.strip() and dieu_kien.lower() in noi_dung.lower():
            return True, 1.0
        return False, 0.0

    # Trường hợp điều kiện là dict
    if isinstance(dieu_kien, dict):
        co_noi_dung = False

        # 1. Kiểm tra "chua"
        chua = dieu_kien.get("chua", [])
        if chua:
            co_noi_dung = True
            so_khop = 0
            for tk in chua:
                if tk and tk.lower() in noi_dung.lower():
                    so_khop += 1
            if so_khop == 0:
                return False, 0.0
            diem += so_khop * 1.0

        # 2. Kiểm tra "khong_chua"
        khong_chua = dieu_kien.get("khong_chua", [])
        if khong_chua:
            co_noi_dung = True
            for tk in khong_chua:
                if tk and tk.lower() in noi_dung.lower():
                    return False, 0.0

        # 3. Kiểm tra "input"
        dang_input = dieu_kien.get("input", "")
        if dang_input == "so":
            co_noi_dung = True
            if not re.search(r"\d", noi_dung):
                return False, 0.0
            diem += 1.0
        elif dang_input == "chu":
            co_noi_dung = True
            if not re.search(r"[a-zA-Zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]", noi_dung):
                return False, 0.0
            diem += 1.0

        # 4. Kiểm tra "khong_dung_khi"
        khong_dung_khi = dieu_kien.get("khong_dung_khi", "")
        if khong_dung_khi:
            co_noi_dung = True
            if khong_dung_khi.lower() in noi_dung.lower():
                return False, 0.0

        # 5. Khớp yếu tố
        yeu_cau_yeu_to = dieu_kien.get("yeu_to_can", [])
        if yeu_cau_yeu_to:
            co_noi_dung = True
            for yt in yeu_cau_yeu_to:
                if yeu_to and yeu_to.get(yt):
                    diem += 1.5

        if not co_noi_dung:
            return False, 0.0

        return True, diem

    return False, 0.0


# ================================================================
# TÍNH ĐIỂM KHỚP 4 TẦNG
# ================================================================
def _diem_4_tang(node, loai_task):
    if not loai_task or not isinstance(loai_task, dict):
        return 0.0

    diem = 0.0

    lv_node = (node.linh_vuc or "").lower().strip()
    lv_task = (loai_task.get("linh_vuc") or "").lower().strip()
    if lv_node and lv_task and lv_node == lv_task:
        diem += DIEM_TANG["linh_vuc"]

    lvd_node = (node.loai_van_de or "").lower().strip()
    nhom_task = (loai_task.get("nhom") or "").lower().strip()
    if lvd_node and nhom_task and lvd_node == nhom_task:
        diem += DIEM_TANG["loai_van_de"]

    cg_node = (node.cach_giai_phap or "").lower().strip()
    loai_task_str = (loai_task.get("loai") or "").lower().strip()
    if cg_node and loai_task_str and cg_node == loai_task_str:
        diem += DIEM_TANG["cach_giai_phap"]

    nc_node = (node.ngu_canh_node or "").lower().strip()
    nc_task = (loai_task.get("ngu_canh", "") or "").lower().strip()
    if nc_node and nc_task and nc_node == nc_task:
        diem += DIEM_TANG["ngu_canh_node"]

    return diem


# ================================================================
# TÍNH ĐIỂM KHỚP TỪ KHÓA TRONG node.ten
# ================================================================
def _diem_ten(node, noi_dung):
    if not node.ten:
        return 0.0
    ten = node.ten.lower().strip()
    noi_dung_lower = noi_dung.lower()

    if ten in noi_dung_lower:
        return min(5.0, len(ten) * 0.3)

    diem = 0.0
    for tu in ten.split():
        if len(tu) >= 3 and tu in noi_dung_lower:
            diem += 0.5
    return min(5.0, diem)


# ================================================================
# KIỂM TRA NODE CÓ NỘI DUNG THỰC
# ================================================================
def _co_noi_dung_thuc(node):
    try:
        hanh_dong = node.hanh_dong or {}
        if isinstance(hanh_dong, dict):
            code = (hanh_dong.get("code") or "").strip()
            loai = (hanh_dong.get("loai") or "").strip()
            if code:
                return True
            if loai == "tra_web":
                return True

        cach_giai = node.cach_giai or {}
        if isinstance(cach_giai, dict):
            mo_ta = (cach_giai.get("mo_ta") or "").strip()
            if mo_ta:
                return True

        if isinstance(cach_giai, str) and cach_giai.strip():
            return True

    except Exception:
        pass
    return False


# ================================================================
# DUYỆT CÂY
# ================================================================
def _duyet_de_quy(node, noi_dung, loai_task, yeu_to, ket_qua):
    if not node:
        return

    if node.blacklist:
        for con in node.nhanh_con:
            _duyet_de_quy(con, noi_dung, loai_task, yeu_to, ket_qua)
        return

    khop, diem_dieu_kien = _kiem_tra_dieu_kien(node, noi_dung, yeu_to)

    if khop and _co_noi_dung_thuc(node):
        diem_4_tang = _diem_4_tang(node, loai_task)
        diem_ten = _diem_ten(node, noi_dung)
        diem_score = node.score * 1.0
        diem_placeholder = _diem_placeholder(node)

        tong_diem = (
            diem_dieu_kien
            + diem_4_tang
            + diem_ten
            + diem_score
            + diem_placeholder
        )

        if tong_diem > ket_qua[1]:
            ket_qua[1] = tong_diem
            ket_qua[0] = node

    for con in node.nhanh_con:
        _duyet_de_quy(con, noi_dung, loai_task, yeu_to, ket_qua)


# ================================================================
# HÀM CHÍNH
# ================================================================
def duyet_cay(noi_dung, loai_task, yeu_to=None):
    """Duyệt cây, trả về node khớp nhất."""
    if not noi_dung:
        return None

    yeu_to = yeu_to or {}

    cay = _lay_cay()
    if not cay or not cay.goc:
        _ghi_log("dai-nao", "Cây rỗng — không duyệt được.")
        return None

    ket_qua = [None, 0.0]
    _duyet_de_quy(cay.goc, noi_dung, loai_task, yeu_to, ket_qua)

    node_tot_nhat = ket_qua[0]
    diem_tot_nhat = ket_qua[1]

    if node_tot_nhat:
        co_regex = " [regex]" if node_tot_nhat.co_pattern() else ""
        _ghi_log(
            "dai-nao",
            f"Duyệt cây: chọn node '{node_tot_nhat.ten or node_tot_nhat.id}'"
            f"{co_regex} (điểm={round(diem_tot_nhat, 2)})",
        )
    else:
        _ghi_log("dai-nao", "Duyệt cây: không tìm thấy node khớp.")

    return node_tot_nhat


# ================================================================
# HÀM PHỤ: DUYỆT THEO LĨNH VỰC
# ================================================================
def duyet_theo_linh_vuc(linh_vuc, noi_dung, yeu_to=None):
    if not linh_vuc or not noi_dung:
        return None

    yeu_to = yeu_to or {}
    cay = _lay_cay()
    if not cay or not cay.goc:
        return None

    node_linh_vuc = None
    for con in cay.goc.nhanh_con:
        if (con.linh_vuc or "").lower() == linh_vuc.lower() or \
           (con.ten or "").lower() == linh_vuc.lower():
            node_linh_vuc = con
            break

    if not node_linh_vuc:
        return None

    loai_task_gia = {"linh_vuc": linh_vuc}
    ket_qua = [None, 0.0]
    _duyet_de_quy(node_linh_vuc, noi_dung, loai_task_gia, yeu_to, ket_qua)

    return ket_qua[0]


# ================================================================
# FIX 4: LẤY TẤT CẢ NODE KHỚP (có regex)
# ================================================================
def lay_tat_ca_node_khop(noi_dung, loai_task, yeu_to=None):
    if not noi_dung:
        return []

    yeu_to = yeu_to or {}
    cay = _lay_cay()
    if not cay or not cay.goc:
        return []

    ket_qua = []
    _thu_thap_tat_ca(cay.goc, noi_dung, loai_task, yeu_to, ket_qua)
    ket_qua.sort(key=lambda x: x[1], reverse=True)
    return [node for node, _ in ket_qua]


def _thu_thap_tat_ca(node, noi_dung, loai_task, yeu_to, ket_qua):
    if not node or node.blacklist:
        return

    khop, diem_dieu_kien = _kiem_tra_dieu_kien(node, noi_dung, yeu_to)
    if khop and _co_noi_dung_thuc(node):
        diem_4_tang = _diem_4_tang(node, loai_task)
        diem_ten = _diem_ten(node, noi_dung)
        diem_score = node.score * 1.0
        diem_placeholder = _diem_placeholder(node)
        tong = diem_dieu_kien + diem_4_tang + diem_ten + diem_score + diem_placeholder
        ket_qua.append((node, tong))

    for con in node.nhanh_con:
        _thu_thap_tat_ca(con, noi_dung, loai_task, yeu_to, ket_qua)


# ================================================================
# HÀM PHỤ: TÌM NODE CÓ REGEX KHỚP
# ================================================================
def tim_node_theo_regex(noi_dung, loai_task=None, yeu_to=None):
    """
    FIX 1: Tìm node có pattern_regex khớp task (ưu tiên regex).
    Trả về node đầu tiên khớp regex hoặc None.
    """
    if not noi_dung:
        return None

    cay = _lay_cay()
    if not cay:
        return None

    ds_co_pattern = cay.duyet_co_pattern()
    ket_qua = [None, 0.0]

    for node in ds_co_pattern:
        if node.blacklist:
            continue
        if not _co_noi_dung_thuc(node):
            continue

        diem_regex, khop = _diem_regex(node, noi_dung)
        if khop:
            diem_4_tang = _diem_4_tang(node, loai_task or {})
            diem_ten = _diem_ten(node, noi_dung)
            diem_score = node.score
            diem_placeholder = _diem_placeholder(node)
            tong = diem_regex + diem_4_tang + diem_ten + diem_score + diem_placeholder

            if tong > ket_qua[1]:
                ket_qua[1] = tong
                ket_qua[0] = node

    return ket_qua[0]
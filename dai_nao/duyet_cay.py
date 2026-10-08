"""
duyet_cay.py - Thuật toán duyệt cây quyết định Rồng Thần.

Nhiệm vụ:
    - duyet_cay(noi_dung, loai_task, yeu_to): duyệt cây, trả về node khớp nhất.

Quy tắc:
    - Duyệt theo 4 tầng: lĩnh vực → loại vấn đề → cách giải → ngữ cảnh.
    - Kiểm tra điều kiện khớp của node (BẮT BUỘC có dieu_kien).
    - Kiểm tra failed_paths (đã làm ở chong_lap_sai.py).
    - Trả về node tốt nhất hoặc None.

ĐÃ SỬA (fix "ngáo"):
    - FIX 1: Bỏ bonus sai cho hanh_dong/cach_giai (không còn +4đ).
    - FIX 2: Node không có dieu_kien → KHÔNG khớp (thay vì khớp 0.5).
    - FIX 3: So sánh lĩnh vực/nhóm/cách giải bằng == (không dùng `in` substring).
    - FIX 4: Điểm node.score nhân 2 → giảm còn nhân 1.0 để không lấn át.
    - FIX 5: Thêm kiểm tra node có nội dung thực (code hoặc mo_ta) mới tính điểm.

Trả về:
    Nut object (từ cay_quyet_dinh.py) hoặc None.
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
    "linh_vuc": 3.0,       # khớp tầng 1
    "loai_van_de": 5.0,    # khớp tầng 2 (quan trọng hơn)
    "cach_giai_phap": 7.0, # khớp tầng 3 (rất quan trọng)
    "ngu_canh_node": 2.0,  # khớp tầng 4 (phụ)
}


# ================================================================
# TÌM CÂY TỪ KHO 2
# ================================================================
def _lay_cay():
    """Lấy object Cay từ kho 2."""
    try:
        from dai_nao.cay_quyet_dinh import cay_tu_mongo
        return cay_tu_mongo()
    except Exception as e:
        _ghi_log("loi", f"Không lấy được cây: {e}")
        return None


# ================================================================
# KIỂM TRA ĐIỀU KIỆN KHỚP
# ================================================================
def _kiem_tra_dieu_kien(node, noi_dung, yeu_to):
    """
    Kiểm tra node có khớp với task không.

    FIX 2: Node không có dieu_kien → KHÔNG khớp (trả False, 0.0).

    node.dieu_kien có thể là:
        - dict: { "chua": [...], "input": "...", "khong_dung_khi": "..." }
        - str: chuỗi từ khóa chính

    Trả về: (True/False, điểm_khớp)
    """
    diem = 0.0
    dieu_kien = node.dieu_kien

    # FIX 2: Node rỗng điều kiện → KHÔNG khớp
    if not dieu_kien:
        return False, 0.0

    # ------------------------------------------------------------
    # Trường hợp điều kiện là chuỗi
    # ------------------------------------------------------------
    if isinstance(dieu_kien, str):
        if dieu_kien.strip() and dieu_kien.lower() in noi_dung.lower():
            return True, 1.0
        return False, 0.0

    # ------------------------------------------------------------
    # Trường hợp điều kiện là dict
    # ------------------------------------------------------------
    if isinstance(dieu_kien, dict):

        # Nếu dict rỗng hoàn toàn → không khớp
        co_noi_dung = False

        # 1. Kiểm tra "chua" — danh sách từ khóa phải có trong nội dung
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

        # 2. Kiểm tra "khong_chua" — danh sách từ khóa không được có
        khong_chua = dieu_kien.get("khong_chua", [])
        if khong_chua:
            co_noi_dung = True
            for tk in khong_chua:
                if tk and tk.lower() in noi_dung.lower():
                    return False, 0.0

        # 3. Kiểm tra "input" — dạng input mong đợi (số, chữ, ...)
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

        # 4. Kiểm tra "khong_dung_khi" — điều kiện loại trừ
        khong_dung_khi = dieu_kien.get("khong_dung_khi", "")
        if khong_dung_khi:
            co_noi_dung = True
            if khong_dung_khi.lower() in noi_dung.lower():
                return False, 0.0

        # 5. Khớp yếu tố (nếu node có yêu cầu)
        yeu_cau_yeu_to = dieu_kien.get("yeu_to_can", [])
        if yeu_cau_yeu_to:
            co_noi_dung = True
            for yt in yeu_cau_yeu_to:
                if yeu_to and yeu_to.get(yt):
                    diem += 1.5

        # Nếu dict chỉ có yeu_to_can mà không có "chua" → vẫn coi là hợp lệ
        # nhưng bắt buộc phải có ít nhất 1 yếu tố khớp
        if not co_noi_dung:
            return False, 0.0

        return True, diem

    # Điều kiện lạ → không khớp (an toàn)
    return False, 0.0


# ================================================================
# TÍNH ĐIỂM KHỚP 4 TẦNG
# ================================================================
def _diem_4_tang(node, loai_task):
    """
    Tính điểm khớp theo 4 tầng.
    FIX 3: So sánh bằng == (không dùng `in` substring).
    """
    if not loai_task or not isinstance(loai_task, dict):
        return 0.0

    diem = 0.0

    # Tầng 1: lĩnh vực — so sánh bằng
    lv_node = (node.linh_vuc or "").lower().strip()
    lv_task = (loai_task.get("linh_vuc") or "").lower().strip()
    if lv_node and lv_task and lv_node == lv_task:
        diem += DIEM_TANG["linh_vuc"]

    # Tầng 2: loại vấn đề — so sánh bằng
    lvd_node = (node.loai_van_de or "").lower().strip()
    nhom_task = (loai_task.get("nhom") or "").lower().strip()
    if lvd_node and nhom_task and lvd_node == nhom_task:
        diem += DIEM_TANG["loai_van_de"]

    # Tầng 3: cách giải — so sánh bằng
    cg_node = (node.cach_giai_phap or "").lower().strip()
    loai_task_str = (loai_task.get("loai") or "").lower().strip()
    if cg_node and loai_task_str and cg_node == loai_task_str:
        diem += DIEM_TANG["cach_giai_phap"]

    # Tầng 4: ngữ cảnh
    nc_node = (node.ngu_canh_node or "").lower().strip()
    nc_task = (loai_task.get("ngu_canh", "") or "").lower().strip()
    if nc_node and nc_task and nc_node == nc_task:
        diem += DIEM_TANG["ngu_canh_node"]

    return diem


# ================================================================
# TÍNH ĐIỂM KHỚP TỪ KHÓA TRONG node.ten
# ================================================================
def _diem_ten(node, noi_dung):
    """
    Nếu tên node xuất hiện trong nội dung → cộng điểm.
    """
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
    """
    Node phải có nội dung thực để được chọn:
        - hanh_dong.code không rỗng, HOẶC
        - cach_giai.mo_ta không rỗng, HOẶC
        - hanh_dong.loai == "tra_web" (được phép rỗng code)
    """
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

        # Có cách giải dạng string
        if isinstance(cach_giai, str) and cach_giai.strip():
            return True

    except Exception:
        pass
    return False


# ================================================================
# DUYỆT CÂY — TÌM NODE TỐT NHẤT
# ================================================================
def _duyet_de_quy(node, noi_dung, loai_task, yeu_to, ket_qua):
    """
    Duyệt đệ quy 1 node và cây con.
    """
    if not node:
        return

    # Bỏ qua node blacklist
    if node.blacklist:
        for con in node.nhanh_con:
            _duyet_de_quy(con, noi_dung, loai_task, yeu_to, ket_qua)
        return

    # Kiểm tra điều kiện khớp
    khop, diem_dieu_kien = _kiem_tra_dieu_kien(node, noi_dung, yeu_to)

    if khop:
        # FIX 5: Node phải có nội dung thực mới tính
        if _co_noi_dung_thuc(node):
            diem_4_tang = _diem_4_tang(node, loai_task)
            diem_ten = _diem_ten(node, noi_dung)
            # FIX 4: Giảm hệ số score từ 2.0 → 1.0
            diem_score = node.score * 1.0

            tong_diem = diem_dieu_kien + diem_4_tang + diem_ten + diem_score

            if tong_diem > ket_qua[1]:
                ket_qua[1] = tong_diem
                ket_qua[0] = node
        # FIX 1: KHÔNG cộng bonus cho hanh_dong / cach_giai nữa

    # Duyệt tiếp nhánh con
    for con in node.nhanh_con:
        _duyet_de_quy(con, noi_dung, loai_task, yeu_to, ket_qua)


# ================================================================
# HÀM CHÍNH
# ================================================================
def duyet_cay(noi_dung, loai_task, yeu_to=None):
    """
    Duyệt cây quyết định, trả về node khớp nhất.
    """
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
        _ghi_log(
            "dai-nao",
            f"Duyệt cây: chọn node '{node_tot_nhat.ten or node_tot_nhat.id}' "
            f"(điểm={round(diem_tot_nhat, 2)})",
        )
    else:
        _ghi_log("dai-nao", "Duyệt cây: không tìm thấy node khớp.")

    return node_tot_nhat


# ================================================================
# HÀM PHỤ: DUYỆT THEO LĨNH VỰC
# ================================================================
def duyet_theo_linh_vuc(linh_vuc, noi_dung, yeu_to=None):
    """Chỉ duyệt cây trong 1 lĩnh vực cụ thể."""
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
# HÀM PHỤ: LẤY TẤT CẢ NODE KHỚP
# ================================================================
def lay_tat_ca_node_khop(noi_dung, loai_task, yeu_to=None):
    """Trả về danh sách tất cả node khớp (đã sắp xếp theo điểm giảm dần)."""
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
    """Thu thập tất cả node khớp."""
    if not node or node.blacklist:
        return

    khop, diem_dieu_kien = _kiem_tra_dieu_kien(node, noi_dung, yeu_to)
    if khop and _co_noi_dung_thuc(node):
        diem_4_tang = _diem_4_tang(node, loai_task)
        diem_ten = _diem_ten(node, noi_dung)
        diem_score = node.score * 1.0
        tong = diem_dieu_kien + diem_4_tang + diem_ten + diem_score
        ket_qua.append((node, tong))

    for con in node.nhanh_con:
        _thu_thap_tat_ca(con, noi_dung, loai_task, yeu_to, ket_qua)
"""
duyet_cay.py - Thuật toán duyệt cây quyết định Rồng Thần.

Nhiệm vụ:
    - duyet_cay(noi_dung, loai_task, yeu_to): duyệt cây, trả về node khớp nhất.

Quy tắc:
    - Duyệt theo 4 tầng: lĩnh vực → loại vấn đề → cách giải → ngữ cảnh.
    - Kiểm tra điều kiện khớp của node.
    - Kiểm tra failed_paths (đã làm ở chong_lap_sai.py).
    - Trả về node tốt nhất hoặc None.

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

    node.dieu_kien có thể là:
        - dict: { "chua": [...], "input": "...", "khong_dung_khi": "..." }
        - str: chuỗi từ khóa chính

    Trả về: (True/False, điểm_khớp)
    """
    diem = 0.0
    dieu_kien = node.dieu_kien

    if not dieu_kien:
        # Không có điều kiện → coi như khớp yếu
        return True, 0.5

    # ------------------------------------------------------------
    # Trường hợp điều kiện là chuỗi
    # ------------------------------------------------------------
    if isinstance(dieu_kien, str):
        if dieu_kien.lower() in noi_dung.lower():
            return True, 1.0
        return False, 0.0

    # ------------------------------------------------------------
    # Trường hợp điều kiện là dict
    # ------------------------------------------------------------
    if isinstance(dieu_kien, dict):

        # 1. Kiểm tra "chua" — danh sách từ khóa phải có trong nội dung
        chua = dieu_kien.get("chua", [])
        if chua:
            so_khop = 0
            for tk in chua:
                if tk.lower() in noi_dung.lower():
                    so_khop += 1
            if so_khop == 0:
                return False, 0.0
            diem += so_khop * 1.0

        # 2. Kiểm tra "khong_chua" — danh sách từ khóa không được có
        khong_chua = dieu_kien.get("khong_chua", [])
        for tk in khong_chua:
            if tk.lower() in noi_dung.lower():
                return False, 0.0

        # 3. Kiểm tra "input" — dạng input mong đợi (số, chữ, ...)
        dang_input = dieu_kien.get("input", "")
        if dang_input == "so":
            if not re.search(r"\d", noi_dung):
                return False, 0.0
            diem += 1.0
        elif dang_input == "chu":
            if not re.search(r"[a-zA-Zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]", noi_dung):
                return False, 0.0
            diem += 1.0

        # 4. Kiểm tra "khong_dung_khi" — điều kiện loại trừ
        khong_dung_khi = dieu_kien.get("khong_dung_khi", "")
        if khong_dung_khi and khong_dung_khi.lower() in noi_dung.lower():
            return False, 0.0

        # 5. Khớp yếu tố (nếu node có yêu cầu)
        yeu_cau_yeu_to = dieu_kien.get("yeu_to_can", [])
        for yt in yeu_cau_yeu_to:
            if yeu_to and yeu_to.get(yt):
                diem += 1.5

        return True, diem

    # Điều kiện lạ → coi như khớp
    return True, 0.5


# ================================================================
# TÍNH ĐIỂM KHỚP 4 TẦNG
# ================================================================
def _diem_4_tang(node, loai_task):
    """
    Tính điểm khớp theo 4 tầng.
    So sánh linh_vuc / loai_van_de / cach_giai_phap / ngu_canh_node
    của node với loai_task đầu vào.
    """
    if not loai_task or not isinstance(loai_task, dict):
        return 0.0

    diem = 0.0

    # Tầng 1: lĩnh vực
    lv_node = (node.linh_vuc or "").lower()
    lv_task = (loai_task.get("linh_vuc") or "").lower()
    if lv_node and lv_task:
        if lv_node == lv_task:
            diem += DIEM_TANG["linh_vuc"]
        elif lv_node in lv_task or lv_task in lv_node:
            diem += DIEM_TANG["linh_vuc"] * 0.5

    # Tầng 2: loại vấn đề
    lvd_node = (node.loai_van_de or "").lower()
    nhom_task = (loai_task.get("nhom") or "").lower()
    if lvd_node and nhom_task:
        if lvd_node == nhom_task:
            diem += DIEM_TANG["loai_van_de"]
        elif lvd_node in nhom_task or nhom_task in lvd_node:
            diem += DIEM_TANG["loai_van_de"] * 0.5

    # Tầng 3: cách giải
    cg_node = (node.cach_giai_phap or "").lower()
    loai_task_str = (loai_task.get("loai") or "").lower()
    if cg_node and loai_task_str:
        if cg_node == loai_task_str:
            diem += DIEM_TANG["cach_giai_phap"]
        elif cg_node in loai_task_str or loai_task_str in cg_node:
            diem += DIEM_TANG["cach_giai_phap"] * 0.5

    # Tầng 4: ngữ cảnh
    nc_node = (node.ngu_canh_node or "").lower()
    if nc_node and nc_node in (loai_task.get("ngu_canh", "") or "").lower():
        diem += DIEM_TANG["ngu_canh_node"]

    return diem


# ================================================================
# TÍNH ĐIỂM KHỚP TỪ KHÓA TRONG node.ten
# ================================================================
def _diem_ten(node, noi_dung):
    """
    Nếu tên node xuất hiện trong nội dung → cộng điểm.
    Đây là tín hiệu mạnh (node có tên cụ thể).
    """
    if not node.ten:
        return 0.0
    ten = node.ten.lower()
    noi_dung_lower = noi_dung.lower()

    if ten in noi_dung_lower:
        # Tên càng dài khớp càng mạnh
        return min(5.0, len(ten) * 0.3)

    # Khớp từng từ trong tên
    diem = 0.0
    for tu in ten.split():
        if len(tu) >= 3 and tu in noi_dung_lower:
            diem += 0.5
    return min(5.0, diem)


# ================================================================
# DUYỆT CÂY — TÌM NODE TỐT NHẤT
# ================================================================
def _duyet_de_quy(node, noi_dung, loai_task, yeu_to, ket_qua):
    """
    Duyệt đệ quy 1 node và cây con.
    Cập nhật ket_qua[0] (node tốt nhất) và ket_qua[1] (điểm tốt nhất).
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
        # Tính điểm tổng
        diem_4_tang = _diem_4_tang(node, loai_task)
        diem_ten = _diem_ten(node, noi_dung)
        diem_score = node.score * 2.0

        # Bonus: node có hành động hoặc cách giải cụ thể
        diem_noi_dung = 0.0
        if node.hanh_dong:
            diem_noi_dung += 2.0
        if node.cach_giai:
            diem_noi_dung += 2.0

        tong_diem = (
            diem_dieu_kien
            + diem_4_tang
            + diem_ten
            + diem_score
            + diem_noi_dung
        )

        # Nếu node có nội dung thực (code/cách giải) → ưu tiên
        if tong_diem > ket_qua[1]:
            ket_qua[1] = tong_diem
            ket_qua[0] = node

    # Duyệt tiếp nhánh con
    for con in node.nhanh_con:
        _duyet_de_quy(con, noi_dung, loai_task, yeu_to, ket_qua)


# ================================================================
# HÀM CHÍNH
# ================================================================
def duyet_cay(noi_dung, loai_task, yeu_to=None):
    """
    Duyệt cây quyết định, trả về node khớp nhất.

    noi_dung: chuỗi đã chuẩn hóa.
    loai_task: dict phân loại từ phan_loai.py.
    yeu_to: dict 5 yếu tố từ trich_xuat.py.

    Trả về: Nut object hoặc None.
    """
    if not noi_dung:
        return None

    yeu_to = yeu_to or {}

    # Lấy cây từ kho 2
    cay = _lay_cay()
    if not cay or not cay.goc:
        _ghi_log("dai-nao", "Cây rỗng — không duyệt được.")
        return None

    # Duyệt đệ quy từ gốc
    ket_qua = [None, 0.0]  # [node_tốt_nhất, điểm_cao_nhất]
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
    """
    Chỉ duyệt cây trong 1 lĩnh vực cụ thể.
    Dùng khi biết chắc lĩnh vực (từ phan_loai.py).
    """
    if not linh_vuc or not noi_dung:
        return None

    yeu_to = yeu_to or {}
    cay = _lay_cay()
    if not cay or not cay.goc:
        return None

    # Tìm node lĩnh vực trong gốc
    node_linh_vuc = None
    for con in cay.goc.nhanh_con:
        if (con.linh_vuc or "").lower() == linh_vuc.lower() or \
           (con.ten or "").lower() == linh_vuc.lower():
            node_linh_vuc = con
            break

    if not node_linh_vuc:
        return None

    # Duyệt đệ quy chỉ trong lĩnh vực này
    loai_task_gia = {"linh_vuc": linh_vuc}
    ket_qua = [None, 0.0]
    _duyet_de_quy(node_linh_vuc, noi_dung, loai_task_gia, yeu_to, ket_qua)

    return ket_qua[0]


# ================================================================
# HÀM PHỤ: LẤY TẤT CẢ NODE KHỚP (để xếp hạng)
# ================================================================
def lay_tat_ca_node_khop(noi_dung, loai_task, yeu_to=None):
    """
    Trả về danh sách tất cả node khớp (đã sắp xếp theo điểm giảm dần).
    Dùng khi cần xếp hạng nhiều nhánh.
    """
    if not noi_dung:
        return []

    yeu_to = yeu_to or {}
    cay = _lay_cay()
    if not cay or not cay.goc:
        return []

    ket_qua = []
    _thu_thap_tat_ca(cay.goc, noi_dung, loai_task, yeu_to, ket_qua)

    # Sắp xếp theo điểm giảm dần
    ket_qua.sort(key=lambda x: x[1], reverse=True)
    return [node for node, _ in ket_qua]


def _thu_thap_tat_ca(node, noi_dung, loai_task, yeu_to, ket_qua):
    """Thu thập tất cả node khớp vào ket_qua."""
    if not node or node.blacklist:
        return

    khop, diem_dieu_kien = _kiem_tra_dieu_kien(node, noi_dung, yeu_to)
    if khop:
        diem_4_tang = _diem_4_tang(node, loai_task)
        diem_ten = _diem_ten(node, noi_dung)
        diem_score = node.score * 2.0
        tong = diem_dieu_kien + diem_4_tang + diem_ten + diem_score
        ket_qua.append((node, tong))

    for con in node.nhanh_con:
        _thu_thap_tat_ca(con, noi_dung, loai_task, yeu_to, ket_qua)
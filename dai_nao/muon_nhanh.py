"""
muon_nhanh.py - Cơ chế mượn nhánh Rồng Thần.

Nhiệm vụ:
    - tim_nhanh_gan_giong(noi_dung, loai_task, cay): tìm nhánh gần giống.
    - muon_nhanh(node_goc, noi_dung, loai_task, yeu_to): tạo nhánh mới
      dựa trên nhánh gốc, có thích nghi.
    - kiem_tra_dieu_kien_muon(node_goc): kiểm tra score có đủ để mượn không.

Quy tắc (theo Phần 4):
    - Score < 0.5 → không mượn.
    - Score ≥ 0.5 → mượn cấu trúc và thích nghi.
    - Luôn tạo nhánh MỚI, không sửa nhánh cũ.
    - Ghi lại muon_tu = id_node_gốc.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

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
NGUONG_SCORE_MUON = 0.5       # score ≥ 0.5 mới mượn (đúng Phần 4)
SO_NODE_TOI_DA_XET = 200      # tránh duyệt quá nhiều node


# ================================================================
# TIỆN ÍCH
# ================================================================
def _lay(node, ten_truong, mac_dinh=None):
    """Lấy thuộc tính — hỗ trợ cả Nut object và dict."""
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
    """
    Kiểm tra node gốc có đủ điều kiện để mượn không.

    Trả về: (True/False, lý_do)
    """
    if node_goc is None:
        return False, "Node gốc không tồn tại."

    # Kiểm tra blacklist
    if bool(_lay(node_goc, "blacklist", False)):
        return False, "Node gốc đang bị blacklist."

    # Kiểm tra score
    score = float(_lay(node_goc, "score", 0.0) or 0.0)
    if score < NGUONG_SCORE_MUON:
        return False, f"Score node gốc quá thấp ({score} < {NGUONG_SCORE_MUON})."

    # Phải có ít nhất 1 trong: cach_giai, quy_tac, hanh_dong
    co_cach_giai = bool(_lay(node_goc, "cach_giai"))
    co_quy_tac = bool(_lay(node_goc, "quy_tac"))
    co_hanh_dong = bool(_lay(node_goc, "hanh_dong"))

    if not (co_cach_giai or co_quy_tac or co_hanh_dong):
        return False, "Node gốc không có cách giải / quy tắc / hành động."

    return True, "Đủ điều kiện."


# ================================================================
# TÌM NHÁNH GẦN GIỐNG NHẤT
# ================================================================
def _diem_giong(node, noi_dung, loai_task):
    """
    Tính điểm giống giữa node và task.
    Dựa trên:
        - Cùng lĩnh vực: +5.
        - Cùng loại vấn đề: +8.
        - Tên node xuất hiện trong nội dung: +len(ten) * 0.5 (tối đa 10).
        - Cùng ngôn ngữ: +3.
    """
    if node is None:
        return 0.0

    diem = 0.0
    noi_dung_lower = (noi_dung or "").lower()

    # Lĩnh vực
    lv_node = (_lay(node, "linh_vuc", "") or "").lower()
    lv_task = (loai_task.get("linh_vuc", "") or "").lower()
    if lv_node and lv_task and lv_node == lv_task:
        diem += 5.0

    # Loại vấn đề
    lvd_node = (_lay(node, "loai_van_de", "") or "").lower()
    nhom_task = (loai_task.get("nhom", "") or "").lower()
    if lvd_node and nhom_task and (lvd_node == nhom_task or lvd_node in nhom_task or nhom_task in lvd_node):
        diem += 8.0

    # Tên node xuất hiện trong nội dung
    ten = (_lay(node, "ten", "") or "").lower()
    if ten and ten in noi_dung_lower:
        diem += min(10.0, len(ten) * 0.5)
    else:
        # Khớp từng từ
        for tu in ten.split():
            if len(tu) >= 3 and tu in noi_dung_lower:
                diem += 0.8

    # Ngôn ngữ
    nn_node = (_lay(node, "hanh_dong", {}) or {}).get("ngon_ngu", "")
    if nn_node and nn_node.lower() in noi_dung_lower:
        diem += 3.0

    # Cộng score nhỏ (khuyến khích node tốt)
    score = float(_lay(node, "score", 0.0) or 0.0)
    diem += score

    return diem


def tim_nhanh_gan_giong(noi_dung, loai_task, cay):
    """
    Tìm nhánh gần giống nhất trong cây.

    noi_dung: chuỗi đã chuẩn hóa.
    loai_task: dict phân loại từ phan_loai.py.
    cay: object Cay.

    Trả về: Nut object hoặc None.
    """
    if not cay or not cay.goc or not noi_dung:
        return None

    # Thu thập tất cả node (giới hạn để tránh duyệt quá lâu)
    tat_ca = cay.duyet_tat_ca()[:SO_NODE_TOI_DA_XET]

    tot_nhat = None
    diem_tot_nhat = 0.0

    for node in tat_ca:
        # Bỏ qua chính node gốc ROOT
        if _lay(node, "id") == "root":
            continue

        # Bỏ qua node blacklist
        if bool(_lay(node, "blacklist", False)):
            continue

        # Phải có nội dung thực để mượn
        co_noi_dung = bool(
            _lay(node, "cach_giai") or _lay(node, "quy_tac") or _lay(node, "hanh_dong")
        )
        if not co_noi_dung:
            continue

        diem = _diem_giong(node, noi_dung, loai_task)
        if diem > diem_tot_nhat:
            diem_tot_nhat = diem
            tot_nhat = node

    # Yêu cầu điểm giống tối thiểu (tránh mượn bừa)
    if tot_nhat and diem_tot_nhat < 3.0:
        return None

    return tot_nhat


# ================================================================
# THÍCH NGHI CÁCH GIẢI
# ================================================================
def _thich_nghi_cach_giai(node_goc, noi_dung, loai_task, yeu_to):
    """
    Thích nghi cách giải của node gốc cho task mới.
    Không sửa node gốc — chỉ tạo bản sao đã điều chỉnh.
    """
    cach_giai_goc = _lay(node_goc, "cach_giai", {}) or {}
    if not isinstance(cach_giai_goc, dict):
        cach_giai_goc = {"mo_ta": str(cach_giai_goc)}

    cach_giai_moi = dict(cach_giai_goc)

    # Cập nhật mô tả nếu có thông tin mới
    if "mo_ta" in cach_giai_moi:
        mo_ta_goc = cach_giai_moi["mo_ta"]
        linh_vuc_moi = loai_task.get("linh_vuc", "")
        loai_moi = loai_task.get("loai", "")
        if linh_vuc_moi and loai_moi:
            cach_giai_moi["mo_ta"] = f"[Mượn từ '{_lay(node_goc, 'ten', '')}'] {mo_ta_goc}"
    else:
        cach_giai_moi["mo_ta"] = cach_giai_goc.get("mo_ta", "")

    # Ghi rõ nguồn mượn
    cach_giai_moi["muon_tu_ten"] = _lay(node_goc, "ten", "")
    cach_giai_moi["muon_tu_id"] = _lay(node_goc, "id", "")

    return cach_giai_moi


def _thich_nghi_hanh_dong(node_goc, noi_dung, loai_task, yeu_to):
    """
    Thích nghi hành động của node gốc cho task mới.
    """
    hanh_dong_goc = _lay(node_goc, "hanh_dong", {}) or {}
    if not isinstance(hanh_dong_goc, dict):
        hanh_dong_goc = {"loai": str(hanh_dong_goc)}

    hanh_dong_moi = dict(hanh_dong_goc)

    # Ghi rõ nguồn mượn
    hanh_dong_moi["muon_tu_ten"] = _lay(node_goc, "ten", "")
    hanh_dong_moi["muon_tu_id"] = _lay(node_goc, "id", "")

    return hanh_dong_moi


# ================================================================
# TẠO NHÁNH MỚI TỪ NHÁNH GỐC
# ================================================================
def muon_nhanh(node_goc, noi_dung, loai_task, yeu_to=None):
    """
    Mượn nhánh từ node_goc để tạo node mới.

    node_goc: Nut object (nhánh gần giống).
    noi_dung: chuỗi đã chuẩn hóa.
    loai_task: dict phân loại.
    yeu_to: dict 5 yếu tố (tùy chọn).

    Trả về: Nut object (node mới) hoặc None nếu không mượn được.
    """
    if not node_goc:
        return None

    # Kiểm tra điều kiện mượn
    du_dieu_kien, ly_do = kiem_tra_dieu_kien_muon(node_goc)
    if not du_dieu_kien:
        _ghi_log("dai-nao", f"Không mượn được: {ly_do}")
        return None

    yeu_to = yeu_to or {}

    # Tạo node mới — KHÔNG sửa node gốc
    try:
        from dai_nao.cay_quyet_dinh import Nut
    except ImportError:
        _ghi_log("loi", "cay_quyet_dinh.py chưa có — không tạo được Nut.")
        return None

    # Xây dựng dữ liệu node mới
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
        "score": 0.7,               # bắt đầu ở mức khá
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
        f"(score={_lay(node_goc, 'score')}) → tạo node mới {id_moi}",
    )

    return node_moi


# ================================================================
# HÀM PHỤ: TRÍCH TỪ KHÓA TỪ NỘI DUNG
# ================================================================
def _trich_tu_khoa(noi_dung, so_tu=5):
    """Trích tối đa `so_tu` từ khóa (từ dài ≥ 3 ký tự) từ nội dung."""
    if not noi_dung:
        return []
    cac_tu = [t.strip(".,!?;:") for t in noi_dung.split()]
    loc = [t for t in cac_tu if len(t) >= 3]
    return loc[:so_tu]


# ================================================================
# HÀM PHỤ: LƯU NHÁNH MỚI VÀO CÂY + KHO 2
# ================================================================
def luu_nhanh_muon(node_moi, cay, id_cha=None):
    """
    Lưu node mới (vừa mượn) vào cây + kho 2.

    node_moi: Nut object.
    cay: object Cay.
    id_cha: id node cha (mặc định vào gốc).

    Trả về: True nếu thành công.
    """
    if not node_moi or not cay:
        return False

    # Thêm vào cây
    if not cay.them_node(node_moi, id_cha):
        return False

    # Lưu vào kho 2
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
# HÀM CHÍNH GỘP — TÌM VÀ MƯỢN 1 LẦN
# ================================================================
def tim_va_muon(noi_dung, loai_task, yeu_to=None, cay=None):
    """
    Tìm nhánh gần giống + mượn + trả về node mới (chưa lưu vào cây).

    Trả về: (node_moi, node_goc) hoặc (None, None).
    """
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
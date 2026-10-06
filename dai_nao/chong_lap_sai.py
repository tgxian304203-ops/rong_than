"""
chong_lap_sai.py - Chống lặp sai Rồng Thần.

Nhiệm vụ:
    - kiem_tra_failed_path(node, noi_dung): kiểm tra node có nằm trong
      failed_paths không.
    - ghi_failed_path(node, noi_dung, ly_do): ghi 1 vết sai vào node.
    - cap_nhat_blacklist(node): kiểm tra + cập nhật blacklist.
    - giam_score_neu_fail_nhieu(node): giảm score nếu fail > 50%.

Quy tắc (theo Phần 4):
    - Mỗi node lưu failed_paths — danh sách vết sai.
    - Task mới giống failed_path > 80% → bỏ qua node.
    - Node fail 3 lần → blacklist.
    - Node fail > 50% → giảm score.

Tầng dữ liệu: dai_nao/ghi_nho.py
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
TY_LE_GIONG_FAILED_PATH = 0.8   # > 80% → bỏ qua node
SO_LAN_FAIL_BLACKLIST = 3       # fail 3 lần → blacklist
TY_LE_FAIL_GIAM_SCORE = 0.5     # fail > 50% → giảm score
MUC_GIAM_SCORE = 0.2            # giảm 20%


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


def _dat(node, ten_truong, gia_tri):
    """Đặt thuộc tính — hỗ trợ cả Nut object và dict."""
    if node is None:
        return
    if isinstance(node, dict):
        node[ten_truong] = gia_tri
    else:
        setattr(node, ten_truong, gia_tri)


# ================================================================
# SO KHỚP CHUỖI — TÍNH TỶ LỆ GIỐNG
# ================================================================
def _tach_tu(chuoi):
    """Tách chuỗi thành set các từ (lowercase, bỏ dấu câu, bỏ từ ngắn)."""
    if not chuoi:
        return set()
    cac_tu = chuoi.lower().replace(",", " ").replace(".", " ").replace("!", " ") \
                    .replace("?", " ").replace(";", " ").replace(":", " ").split()
    return {t for t in cac_tu if len(t) >= 2}


def _ty_le_giong(chuoi_a, chuoi_b):
    """
    Tính tỷ lệ giống giữa 2 chuỗi dựa trên tập từ (Jaccard).
    Trả về: 0.0 – 1.0
    """
    if not chuoi_a or not chuoi_b:
        return 0.0

    tu_a = _tach_tu(chuoi_a)
    tu_b = _tach_tu(chuoi_b)

    if not tu_a or not tu_b:
        return 0.0

    giao = tu_a & tu_b
    hop = tu_a | tu_b

    if not hop:
        return 0.0

    return len(giao) / len(hop)


# ================================================================
# KIỂM TRA FAILED_PATH
# ================================================================
def kiem_tra_failed_path(node, noi_dung):
    """
    Kiểm tra node có nằm trong failed_paths với task mới không.

    node: Nut object hoặc dict.
    noi_dung: chuỗi task mới.

    Trả về: True nếu task giống failed_path > 80% (nên bỏ qua node).
    """
    if node is None or not noi_dung:
        return False

    failed_paths = list(_lay(node, "failed_paths", []) or [])
    if not failed_paths:
        return False

    for vet_sai in failed_paths:
        # Bỏ qua nếu vết sai không phải chuỗi
        if not isinstance(vet_sai, str):
            continue

        ty_le = _ty_le_giong(noi_dung, vet_sai)
        if ty_le > TY_LE_GIONG_FAILED_PATH:
            _ghi_log(
                "dai-nao",
                f"Task giống failed_path ({round(ty_le * 100)}%) — bỏ qua node "
                f"'{_lay(node, 'ten', _lay(node, 'id', ''))}'.",
            )
            return True

    return False


# ================================================================
# GHI FAILED_PATH
# ================================================================
def ghi_failed_path(node, noi_dung, ly_do=None):
    """
    Ghi 1 vết sai vào node.

    node: Nut object hoặc dict.
    noi_dung: chuỗi task bị sai.
    ly_do: mô tả lý do (tùy chọn).

    Trả về: True nếu ghi thành công.
    """
    if node is None or not noi_dung:
        return False

    failed_paths = list(_lay(node, "failed_paths", []) or [])

    # Cắt ngắn nội dung để tránh lưu quá dài
    vet_sai = noi_dung.strip()[:200]
    if ly_do:
        vet_sai = f"{vet_sai} || {ly_do[:100]}"

    # Kiểm tra trùng
    if vet_sai in failed_paths:
        return False

    # Giới hạn số lượng failed_paths mỗi node (tránh phình to)
    SO_FAILED_PATH_TOI_DA = 20
    if len(failed_paths) >= SO_FAILED_PATH_TOI_DA:
        failed_paths.pop(0)  # xóa cũ nhất

    failed_paths.append(vet_sai)
    _dat(node, "failed_paths", failed_paths)

    # Cập nhật số lần thất bại
    that_bai = int(_lay(node, "that_bai", 0) or 0) + 1
    so_lan_thu = int(_lay(node, "so_lan_thu", 0) or 0) + 1
    _dat(node, "that_bai", that_bai)
    _dat(node, "so_lan_thu", so_lan_thu)
    _dat(node, "lan_dung_cuoi", int(time.time()))

    # Cập nhật blacklist nếu cần
    cap_nhat_blacklist(node)

    # Giảm score nếu fail nhiều
    giam_score_neu_fail_nhieu(node)

    _ghi_log(
        "dai-nao",
        f"Ghi failed_path cho node '{_lay(node, 'ten', _lay(node, 'id', ''))}': "
        f"{vet_sai[:60]}",
    )

    return True


# ================================================================
# CẬP NHẬT BLACKLIST
# ================================================================
def cap_nhat_blacklist(node):
    """
    Kiểm tra + cập nhật blacklist cho node.
    Node fail ≥ 3 lần → blacklist.

    Trả về: True nếu node vừa bị blacklist.
    """
    if node is None:
        return False

    that_bai = int(_lay(node, "that_bai", 0) or 0)

    if that_bai >= SO_LAN_FAIL_BLACKLIST:
        if not bool(_lay(node, "blacklist", False)):
            _dat(node, "blacklist", True)
            _ghi_log(
                "dai-nao",
                f"Blacklist node '{_lay(node, 'ten', _lay(node, 'id', ''))}' "
                f"(fail {that_bai} lần).",
            )
            return True

    return False


# ================================================================
# GIẢM SCORE NẾU FAIL NHIỀU
# ================================================================
def giam_score_neu_fail_nhieu(node):
    """
    Giảm score 20% nếu tỷ lệ fail > 50%.

    Trả về: score mới (hoặc score cũ nếu không giảm).
    """
    if node is None:
        return 0.0

    so_lan_thu = int(_lay(node, "so_lan_thu", 0) or 0)
    that_bai = int(_lay(node, "that_bai", 0) or 0)

    if so_lan_thu <= 0:
        return float(_lay(node, "score", 0.0) or 0.0)

    ty_le_that_bai = that_bai / so_lan_thu
    score_hien_tai = float(_lay(node, "score", 0.0) or 0.0)

    if ty_le_that_bai > TY_LE_FAIL_GIAM_SCORE:
        score_moi = max(0.0, score_hien_tai - MUC_GIAM_SCORE)
        _dat(node, "score", round(score_moi, 3))
        return score_moi

    return score_hien_tai


# ================================================================
# XÓA FAILED_PATH (nếu sau này node sửa được)
# ================================================================
def xoa_failed_path(node, noi_dung=None):
    """
    Xóa 1 failed_path cụ thể (hoặc toàn bộ nếu noi_dung=None).
    Dùng khi node đã sửa được lỗi.
    """
    if node is None:
        return False

    if noi_dung is None:
        # Xóa toàn bộ
        _dat(node, "failed_paths", [])
        return True

    failed_paths = list(_lay(node, "failed_paths", []) or [])
    noi_dung = noi_dung.strip()[:200]

    danh_sach_moi = [fp for fp in failed_paths if not fp.startswith(noi_dung)]
    if len(danh_sach_moi) < len(failed_paths):
        _dat(node, "failed_paths", danh_sach_moi)
        return True

    return False


# ================================================================
# XÓA BLACKLIST (thủ công, khi node đã cải thiện)
# ================================================================
def xoa_blacklist(node):
    """
    Xóa blacklist + reset số lần thất bại.
    Chỉ dùng khi chắc chắn node đã sửa được.
    """
    if node is None:
        return False

    _dat(node, "blacklist", False)
    _dat(node, "that_bai", 0)
    _dat(node, "failed_paths", [])

    _ghi_log(
        "dai-nao",
        f"Xóa blacklist cho node '{_lay(node, 'ten', _lay(node, 'id', ''))}'.",
    )
    return True


# ================================================================
# THỐNG KÊ LỖI CỦA NODE
# ================================================================
def thong_ke_loi(node):
    """
    Thống kê lỗi của node.

    Trả về: dict
        {
            so_lan_thu: int,
            thanh_cong: int,
            that_bai: int,
            ty_le_that_bai: float,
            so_failed_paths: int,
            blacklist: bool,
            score: float,
        }
    """
    if node is None:
        return {}

    so_lan_thu = int(_lay(node, "so_lan_thu", 0) or 0)
    thanh_cong = int(_lay(node, "thanh_cong", 0) or 0)
    that_bai = int(_lay(node, "that_bai", 0) or 0)
    failed_paths = list(_lay(node, "failed_paths", []) or [])

    return {
        "so_lan_thu": so_lan_thu,
        "thanh_cong": thanh_cong,
        "that_bai": that_bai,
        "ty_le_that_bai": round(that_bai / so_lan_thu, 3) if so_lan_thu > 0 else 0.0,
        "so_failed_paths": len(failed_paths),
        "blacklist": bool(_lay(node, "blacklist", False)),
        "score": float(_lay(node, "score", 0.0) or 0.0),
    }


# ================================================================
# LƯU NODE SAU KHI CẬP NHẬT
# ================================================================
def luu_node_sau_cap_nhat(node):
    """Lưu node vào kho 2 sau khi cập nhật failed_paths/blacklist/score."""
    if node is None:
        return False

    try:
        from dai_nao.ghi_nho import luu_node

        if isinstance(node, dict):
            du_lieu = dict(node)
        elif hasattr(node, "sang_dict_phang"):
            du_lieu = node.sang_dict_phang()
        else:
            return False

        luu_node(du_lieu)
        return True
    except Exception as e:
        _ghi_log("loi", f"Không lưu được node sau cập nhật: {e}")
        return False


# ================================================================
# HÀM GỘP — XỬ LÝ 1 LẦN FAIL
# ================================================================
def xu_ly_that_bai(node, noi_dung, ly_do=None):
    """
    Xử lý 1 lần thất bại: ghi failed_path + cập nhật blacklist + giảm score.
    Tự lưu node vào kho 2.

    Trả về: dict thống kê sau khi cập nhật.
    """
    if node is None:
        return {}

    ghi_failed_path(node, noi_dung, ly_do)
    luu_node_sau_cap_nhat(node)
    return thong_ke_loi(node)
"""
chia_se_nhanh.py - Cơ chế chia sẻ nhánh Rồng Thần.

Nhiệm vụ:
    - dang_ky_chia_se(node_a, node_b): đăng ký 2 node chia sẻ cho nhau.
    - tim_node_chia_se(node): tìm node chia sẻ có cách giải.
    - lay_cach_giai_chia_se(node): lấy cách giải từ node chia sẻ.
    - tu_dong_chia_se(node_moi, cay): tự động tìm node cũ để chia sẻ.

Quy tắc (theo Phần 4):
    - Node cùng quy tắc chia sẻ cho nhau.
    - Ví dụ: cộng ↔ nhân, chia ↔ trừ, lũy thừa ↔ nhân, giai thừa ↔ nhân.
    - Không copy dữ liệu — chỉ ghi nhận quan hệ "chia_se_voi".
    - Không sửa node chia sẻ.
    - Chỉ chia sẻ khi 2 node cùng loại hành động / cùng lĩnh vực.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""


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
# BẢNG CHIA SẺ MẶC ĐỊNH
# (cặp node cùng quy tắc — theo Phần 4)
# ================================================================
BANG_CHIA_SE_MAC_DINH = [
    # Toán — số học
    ("cộng", "nhân"),
    ("trừ", "chia"),
    ("nhân", "lũy thừa"),
    ("nhân", "giai thừa"),
    ("cộng", "trung bình"),

    # Toán — đại số
    ("lũy thừa", "logarit"),
    ("lũy thừa", "căn bậc 2"),

    # Code
    ("tạo mới web", "tạo mới form"),
    ("viết hàm", "viết class"),
    ("tạo mới API", "tạo mới database"),

    # Văn
    ("viết đoạn văn", "viết email"),
    ("tóm tắt", "phân tích"),
    ("dịch", "chuyển đổi"),

    # Bug
    ("syntax", "logic"),
    ("runtime", "logic"),
]


# ================================================================
# TÌM CẶP CHIA SẺ THEO TÊN
# ================================================================
def _tim_cap_chia_se(ten_a, ten_b):
    """
    Kiểm tra 2 tên có nằm trong bảng chia sẻ không.
    Trả về True nếu có cặp khớp.
    """
    if not ten_a or not ten_b:
        return False
    a = ten_a.lower()
    b = ten_b.lower()
    for x, y in BANG_CHIA_SE_MAC_DINH:
        if (x in a and y in b) or (y in a and x in b):
            return True
    return False


# ================================================================
# LẤY THUỘC TÍNH NODE AN TOÀN
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
# ĐĂNG KÝ CHIA SẺ
# ================================================================
def dang_ky_chia_se(node_a, node_b):
    """
    Đăng ký 2 node chia sẻ cho nhau (quan hệ 2 chiều).

    node_a, node_b: Nut object hoặc dict.
    Trả về: True nếu đăng ký thành công.
    """
    id_a = _lay(node_a, "id")
    id_b = _lay(node_b, "id")
    if not id_a or not id_b or id_a == id_b:
        return False

    # Lấy danh sách chia_se_voi hiện tại
    cs_a = list(_lay(node_a, "chia_se_voi", []) or [])
    cs_b = list(_lay(node_b, "chia_se_voi", []) or [])

    # Thêm quan hệ 2 chiều
    if id_b not in cs_a:
        cs_a.append(id_b)
    if id_a not in cs_b:
        cs_b.append(id_a)

    _dat(node_a, "chia_se_voi", cs_a)
    _dat(node_b, "chia_se_voi", cs_b)

    _ghi_log(
        "dai-nao",
        f"Đăng ký chia sẻ: {id_a} ↔ {id_b}",
    )
    return True


# ================================================================
# HỦY CHIA SẺ
# ================================================================
def huy_chia_se(node_a, node_b):
    """Hủy quan hệ chia sẻ giữa 2 node."""
    id_a = _lay(node_a, "id")
    id_b = _lay(node_b, "id")
    if not id_a or not id_b:
        return False

    cs_a = list(_lay(node_a, "chia_se_voi", []) or [])
    cs_b = list(_lay(node_b, "chia_se_voi", []) or [])

    if id_b in cs_a:
        cs_a.remove(id_b)
    if id_a in cs_b:
        cs_b.remove(id_a)

    _dat(node_a, "chia_se_voi", cs_a)
    _dat(node_b, "chia_se_voi", cs_b)
    return True


# ================================================================
# TÌM NODE CHIA SẺ CÓ CÁCH GIẢI
# ================================================================
def tim_node_chia_se(node, cay=None):
    """
    Tìm 1 node chia sẻ của node hiện tại (ưu tiên node có cách giải).

    node: node hiện tại (Nut hoặc dict).
    cay: object Cay (để tra cứu node theo id) — có thể None.

    Trả về: Nut object hoặc None.
    """
    if node is None:
        return None

    danh_sach_id = _lay(node, "chia_se_voi", []) or []
    if not danh_sach_id:
        return None

    # Nếu không có cây → không tra cứu được
    if cay is None:
        return None

    ban_do = getattr(cay, "ban_do", {}) or {}

    tot_nhat = None
    diem_tot_nhat = -1

    for id_chia_se in danh_sach_id:
        node_chia_se = ban_do.get(id_chia_se)
        if not node_chia_se:
            continue

        # Ưu tiên node có cách giải
        co_cach_giai = bool(_lay(node_chia_se, "cach_giai"))
        co_hanh_dong = bool(_lay(node_chia_se, "hanh_dong"))
        score = float(_lay(node_chia_se, "score", 0.0) or 0.0)

        diem = (1 if co_cach_giai else 0) * 5 \
             + (1 if co_hanh_dong else 0) * 3 \
             + score

        if diem > diem_tot_nhat:
            diem_tot_nhat = diem
            tot_nhat = node_chia_se

    return tot_nhat


# ================================================================
# LẤY CÁCH GIẢI TỪ NODE CHIA SẺ
# ================================================================
def lay_cach_giai_chia_se(node, cay=None):
    """
    Lấy cách giải từ node chia sẻ (nếu node chính không có).

    Trả về: dict cach_giai hoặc {} nếu không có.
    """
    # Nếu node chính đã có cách giải → dùng luôn
    cach_giai_chinh = _lay(node, "cach_giai")
    if cach_giai_chinh:
        return cach_giai_chinh

    # Tìm node chia sẻ
    node_chia_se = tim_node_chia_se(node, cay)
    if not node_chia_se:
        return {}

    return _lay(node_chia_se, "cach_giai", {}) or {}


# ================================================================
# TỰ ĐỘNG CHIA SẺ KHI TẠO NODE MỚI
# ================================================================
def tu_dong_chia_se(node_moi, cay):
    """
    Tự động tìm node cũ để chia sẻ với node mới.
    Dựa vào tên node + lĩnh vực.

    node_moi: Nut object (node vừa sinh).
    cay: object Cay (toàn bộ cây).

    Trả về: danh sách id node đã chia sẻ.
    """
    if not node_moi or not cay:
        return []

    ten_moi = (_lay(node_moi, "ten") or "").lower()
    linh_vuc_moi = (_lay(node_moi, "linh_vuc") or "").lower()

    if not ten_moi or not linh_vuc_moi:
        return []

    da_chia_se = []

    # Duyệt tất cả node cùng lĩnh vực
    for node_cu in cay.duyet_theo_linh_vuc(linh_vuc_moi):
        if node_cu.id == node_moi.id:
            continue

        ten_cu = (_lay(node_cu, "ten") or "").lower()
        if not ten_cu:
            continue

        # Kiểm tra cặp chia sẻ mặc định
        if _tim_cap_chia_se(ten_moi, ten_cu):
            if dang_ky_chia_se(node_moi, node_cu):
                da_chia_se.append(node_cu.id)

    if da_chia_se:
        _ghi_log(
            "dai-nao",
            f"Tự động chia sẻ '{ten_moi}' với {len(da_chia_se)} node.",
        )

    return da_chia_se


# ================================================================
# LIỆT KÊ CHIA SẺ
# ================================================================
def liet_ke_chia_se(node, cay=None):
    """
    Liệt kê các node chia sẻ của 1 node (kèm tên).

    Trả về: list dict { id, ten, co_cach_giai, score }.
    """
    if node is None:
        return []

    danh_sach_id = _lay(node, "chia_se_voi", []) or []
    if not danh_sach_id:
        return []

    ket_qua = []
    ban_do = getattr(cay, "ban_do", {}) if cay else {}

    for id_chia_se in danh_sach_id:
        node_chia_se = ban_do.get(id_chia_se)
        if not node_chia_se:
            ket_qua.append({
                "id": id_chia_se,
                "ten": "(không tìm thấy)",
                "co_cach_giai": False,
                "score": 0.0,
            })
            continue

        ket_qua.append({
            "id": id_chia_se,
            "ten": _lay(node_chia_se, "ten", ""),
            "co_cach_giai": bool(_lay(node_chia_se, "cach_giai")),
            "score": float(_lay(node_chia_se, "score", 0.0) or 0.0),
        })

    return ket_qua


# ================================================================
# LƯU CHIA SẺ VÀO KHO 2
# ================================================================
def luu_chia_se_vao_kho(node_a, node_b):
    """
    Lưu quan hệ chia sẻ vào kho 2.
    Gọi luu_node cho cả 2 node sau khi cập nhật.
    """
    if not dang_ky_chia_se(node_a, node_b):
        return False

    try:
        from dai_nao.ghi_nho import luu_node
        luu_node(_sang_dict(node_a))
        luu_node(_sang_dict(node_b))
        return True
    except Exception as e:
        _ghi_log("loi", f"Không lưu được chia sẻ vào kho 2: {e}")
        return False


def _sang_dict(node):
    """Chuyển node thành dict (không gồm nhánh con)."""
    if isinstance(node, dict):
        return dict(node)
    if hasattr(node, "sang_dict_phang"):
        return node.sang_dict_phang()
    return {}
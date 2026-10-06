"""
schema_node.py - Schema các trường bắt buộc của node Rồng Thần.

Nhiệm vụ:
    - lay_schema(): trả về schema đầy đủ của node.
    - lay_schema_rut_gon(): schema rút gọn cho prompt.
    - validate_node(node): validate node theo schema.
    - tao_node_mac_dinh(): tạo node rỗng với giá trị mặc định.
    - sap_xep_truong(node): sắp xếp lại trường theo thứ tự schema.
    - chuan_hoa_node(node): chuẩn hóa node về đúng schema.

Schema đầy đủ (25 trường, theo Phần 4):
    - Định danh: id, ten, phien_ban.
    - Điều kiện: dieu_kien, quy_tac, thuat_toan, cach_giai, hanh_dong.
    - Đánh giá: score, so_lan_thu, thanh_cong, that_bai, do_kho,
                thoi_gian_uoc_tinh.
    - Phụ thuộc: phu_thuoc, uu_tien.
    - Nhánh con: nhanh_con.
    - Chia sẻ: chia_se_voi, muon_tu.
    - Chống sai: failed_paths, blacklist.
    - 4 tầng cây: linh_vuc, loai_van_de, cach_giai_phap, ngu_canh_node.
    - Metadata: ngay_tao, lan_dung_cuoi.

Tầng dữ liệu: Không.
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
# SCHEMA ĐẦY ĐỦ (25 TRƯỜNG)
# ================================================================
SCHEMA_DAY_DU = {
    # Nhóm định danh
    "id": {"kieu": str, "bat_buoc": True, "mac_dinh": None,
           "mo_ta": "Định danh duy nhất, dạng nut-xxxxxxxx"},
    "ten": {"kieu": str, "bat_buoc": True, "mac_dinh": "",
            "mo_ta": "Tên node ngắn gọn"},
    "phien_ban": {"kieu": int, "bat_buoc": False, "mac_dinh": 1,
                  "mo_ta": "Phiên bản node"},

    # Nhóm điều kiện / quy tắc
    "dieu_kien": {"kieu": dict, "bat_buoc": True,
                  "mac_dinh": {"chua": [], "yeu_to_can": ["hanh_dong", "doi_tuong"]},
                  "mo_ta": "Điều kiện khớp"},
    "quy_tac": {"kieu": str, "bat_buoc": False, "mac_dinh": "",
                "mo_ta": "Quy tắc xử lý"},
    "thuat_toan": {"kieu": dict, "bat_buoc": False,
                   "mac_dinh": {"ten": "", "mo_ta": "", "do_phuc_tap": ""},
                   "mo_ta": "Thuật toán áp dụng"},
    "cach_giai": {"kieu": dict, "bat_buoc": True,
                  "mac_dinh": {"mo_ta": "", "cac_buoc": [], "vi_du": ""},
                  "mo_ta": "Cách giải cụ thể"},
    "hanh_dong": {"kieu": dict, "bat_buoc": True,
                  "mac_dinh": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
                  "mo_ta": "Hành động (code mẫu, loại)"},

    # Nhóm đánh giá
    "score": {"kieu": float, "bat_buoc": False, "mac_dinh": 0.7,
              "mo_ta": "Điểm tổng hợp (0.0-1.0)"},
    "so_lan_thu": {"kieu": int, "bat_buoc": False, "mac_dinh": 0,
                   "mo_ta": "Số lần thử"},
    "thanh_cong": {"kieu": int, "bat_buoc": False, "mac_dinh": 0,
                   "mo_ta": "Số lần thành công"},
    "that_bai": {"kieu": int, "bat_buoc": False, "mac_dinh": 0,
                 "mo_ta": "Số lần thất bại"},
    "do_kho": {"kieu": float, "bat_buoc": False, "mac_dinh": 0.5,
               "mo_ta": "Độ khó (0.0-1.0)"},
    "thoi_gian_uoc_tinh": {"kieu": int, "bat_buoc": False, "mac_dinh": 0,
                            "mo_ta": "Thời gian ước tính (giây)"},

    # Nhóm phụ thuộc / ưu tiên
    "phu_thuoc": {"kieu": list, "bat_buoc": False, "mac_dinh": [],
                  "mo_ta": "Danh sách id node phụ thuộc"},
    "uu_tien": {"kieu": int, "bat_buoc": False, "mac_dinh": 50,
                "mo_ta": "Mức ưu tiên (0-100)"},

    # Nhóm nhánh con
    "nhanh_con": {"kieu": list, "bat_buoc": False, "mac_dinh": [],
                  "mo_ta": "Danh sách node con"},

    # Nhóm chia sẻ / mượn
    "chia_se_voi": {"kieu": list, "bat_buoc": False, "mac_dinh": [],
                    "mo_ta": "Danh sách id node chia sẻ"},
    "muon_tu": {"kieu": str, "bat_buoc": False, "mac_dinh": "",
                "mo_ta": "Id node đã mượn"},

    # Nhóm chống lặp sai
    "failed_paths": {"kieu": list, "bat_buoc": False, "mac_dinh": [],
                     "mo_ta": "Danh sách vết sai"},
    "blacklist": {"kieu": bool, "bat_buoc": False, "mac_dinh": False,
                  "mo_ta": "Có bị blacklist không"},

    # Nhóm 4 tầng cây
    "linh_vuc": {"kieu": str, "bat_buoc": True, "mac_dinh": "",
                 "mo_ta": "Tầng 1: lĩnh vực"},
    "loai_van_de": {"kieu": str, "bat_buoc": True, "mac_dinh": "",
                    "mo_ta": "Tầng 2: loại vấn đề"},
    "cach_giai_phap": {"kieu": str, "bat_buoc": True, "mac_dinh": "",
                       "mo_ta": "Tầng 3: cách giải"},
    "ngu_canh_node": {"kieu": str, "bat_buoc": False, "mac_dinh": "",
                      "mo_ta": "Tầng 4: ngữ cảnh"},

    # Nhóm metadata
    "ngay_tao": {"kieu": int, "bat_buoc": False, "mac_dinh": 0,
                 "mo_ta": "Thời gian tạo (unix timestamp)"},
    "lan_dung_cuoi": {"kieu": int, "bat_buoc": False, "mac_dinh": 0,
                      "mo_ta": "Lần dùng cuối (unix timestamp)"},
}


# ================================================================
# TRƯỜNG BẮT BUỘC (8 trường)
# ================================================================
TRUONG_BAT_BUOC = [
    "id", "ten", "linh_vuc", "loai_van_de",
    "cach_giai_phap", "dieu_kien", "cach_giai", "hanh_dong",
]


# ================================================================
# LẤY SCHEMA
# ================================================================
def lay_schema():
    """Trả về schema đầy đủ."""
    return dict(SCHEMA_DAY_DU)


def lay_schema_rut_gon():
    """
    Schema rút gọn cho prompt (chỉ 8 trường bắt buộc).
    Dùng khi gọi model — tiết kiệm token.
    """
    rut_gon = {}
    for truong in TRUONG_BAT_BUOC:
        if truong in SCHEMA_DAY_DU:
            rut_gon[truong] = SCHEMA_DAY_DU[truong]
    return rut_gon


def lay_mo_ta_truong(truong):
    """Lấy mô tả của 1 trường."""
    if truong in SCHEMA_DAY_DU:
        return SCHEMA_DAY_DU[truong].get("mo_ta", "")
    return ""


def lay_truong_bat_buoc():
    """Trả về danh sách 8 trường bắt buộc."""
    return list(TRUONG_BAT_BUOC)


# ================================================================
# TẠO NODE MẶC ĐỊNH
# ================================================================
def tao_node_mac_dinh():
    """Tạo node rỗng với giá trị mặc định cho mọi trường."""
    node = {}
    for truong, thong_tin in SCHEMA_DAY_DU.items():
        mac_dinh = thong_tin.get("mac_dinh")

        # Copy giá trị mutable
        if isinstance(mac_dinh, (dict, list)):
            import copy
            node[truong] = copy.deepcopy(mac_dinh)
        else:
            node[truong] = mac_dinh

    # Sinh id mới
    node["id"] = "nut-" + secrets.token_hex(8)
    node["ngay_tao"] = int(time.time())

    return node


# ================================================================
# VALIDATE NODE
# ================================================================
def validate_node(node):
    """
    Validate node theo schema.

    Trả về: (True, []) nếu OK, hoặc (False, [danh_sách_lỗi]).
    """
    if not node or not isinstance(node, dict):
        return False, ["Node không phải dict."]

    loi = []

    # 1. Kiểm tra trường bắt buộc
    for truong in TRUONG_BAT_BUOC:
        if truong not in node:
            loi.append(f"Thiếu trường bắt buộc: {truong}")
        elif node[truong] in (None, "", [], {}):
            loi.append(f"Trường bắt buộc rỗng: {truong}")

    # 2. Kiểm tra kiểu dữ liệu
    for truong, gia_tri in node.items():
        if truong not in SCHEMA_DAY_DU:
            continue  # Trường lạ, bỏ qua

        kieu_mong = SCHEMA_DAY_DU[truong].get("kieu")
        if kieu_mong and gia_tri is not None and not isinstance(gia_tri, kieu_mong):
            # Cho phép int khi yêu cầu float
            if kieu_mong is float and isinstance(gia_tri, int):
                continue
            loi.append(
                f"Sai kiểu trường '{truong}': cần {kieu_mong.__name__}, "
                f"có {type(gia_tri).__name__}"
            )

    # 3. Validate dieu_kien
    if isinstance(node.get("dieu_kien"), dict):
        dk = node["dieu_kien"]
        if "chua" in dk and not isinstance(dk["chua"], list):
            loi.append("dieu_kien.chua phải là list.")
    else:
        if "dieu_kien" in node:
            loi.append("dieu_kien phải là dict.")

    # 4. Validate cach_giai
    if isinstance(node.get("cach_giai"), dict):
        if not node["cach_giai"].get("mo_ta"):
            loi.append("cach_giai.mo_ta rỗng.")
    else:
        if "cach_giai" in node:
            loi.append("cach_giai phải là dict.")

    # 5. Validate score (0.0 - 1.0)
    if "score" in node:
        try:
            s = float(node["score"])
            if not 0.0 <= s <= 1.0:
                loi.append(f"score phải trong [0.0, 1.0], có {s}")
        except (ValueError, TypeError):
            loi.append("score không phải số.")

    # 6. Validate uu_tien (0 - 100)
    if "uu_tien" in node:
        try:
            u = int(node["uu_tien"])
            if not 0 <= u <= 100:
                loi.append(f"uu_tien phải trong [0, 100], có {u}")
        except (ValueError, TypeError):
            loi.append("uu_tien không phải số nguyên.")

    return len(loi) == 0, loi


# ================================================================
# CHUẨN HÓA NODE
# ================================================================
def chuan_hoa_node(node):
    """
    Chuẩn hóa node về đúng schema:
        - Bổ sung trường thiếu bằng giá trị mặc định.
        - Sửa kiểu dữ liệu nếu sai.
        - Sinh id nếu thiếu.
    """
    if not isinstance(node, dict):
        return tao_node_mac_dinh()

    ket_qua = {}

    for truong, thong_tin in SCHEMA_DAY_DU.items():
        mac_dinh = thong_tin.get("mac_dinh")
        kieu_mong = thong_tin.get("kieu")

        if truong not in node or node[truong] is None:
            # Bổ sung mặc định
            if isinstance(mac_dinh, (dict, list)):
                import copy
                ket_qua[truong] = copy.deepcopy(mac_dinh)
            else:
                ket_qua[truong] = mac_dinh
            continue

        gia_tri = node[truong]

        # Sửa kiểu nếu sai
        if kieu_mong and not isinstance(gia_tri, kieu_mong):
            try:
                if kieu_mong is str:
                    gia_tri = str(gia_tri)
                elif kieu_mong is int:
                    gia_tri = int(float(gia_tri)) if gia_tri else 0
                elif kieu_mong is float:
                    gia_tri = float(gia_tri)
                elif kieu_mong is bool:
                    gia_tri = bool(gia_tri)
                elif kieu_mong is list and not isinstance(gia_tri, list):
                    gia_tri = [gia_tri] if gia_tri else []
                elif kieu_mong is dict and not isinstance(gia_tri, dict):
                    gia_tri = {"gia_tri": gia_tri}
            except (ValueError, TypeError):
                if isinstance(mac_dinh, (dict, list)):
                    import copy
                    gia_tri = copy.deepcopy(mac_dinh)
                else:
                    gia_tri = mac_dinh

        ket_qua[truong] = gia_tri

    # Sinh id nếu thiếu
    if not ket_qua.get("id"):
        ket_qua["id"] = "nut-" + secrets.token_hex(8)
    elif not ket_qua["id"].startswith("nut-"):
        ket_qua["id"] = "nut-" + str(ket_qua["id"])[:16]

    # Ngày tạo
    if not ket_qua.get("ngay_tao"):
        ket_qua["ngay_tao"] = int(time.time())

    # Giới hạn score
    try:
        ket_qua["score"] = max(0.0, min(1.0, float(ket_qua.get("score", 0.7))))
    except (ValueError, TypeError):
        ket_qua["score"] = 0.7

    # Giới hạn uu_tien
    try:
        ket_qua["uu_tien"] = max(0, min(100, int(ket_qua.get("uu_tien", 50))))
    except (ValueError, TypeError):
        ket_qua["uu_tien"] = 50

    # Giới hạn do_kho
    try:
        ket_qua["do_kho"] = max(0.0, min(1.0, float(ket_qua.get("do_kho", 0.5))))
    except (ValueError, TypeError):
        ket_qua["do_kho"] = 0.5

    return ket_qua


# ================================================================
# SẮP XẾP TRƯỜNG
# ================================================================
def sap_xep_truong(node):
    """
    Sắp xếp trường theo thứ tự schema.
    Hữu ích khi lưu MongoDB hoặc hiển thị.
    """
    if not isinstance(node, dict):
        return node

    ket_qua = {}
    for truong in SCHEMA_DAY_DU.keys():
        if truong in node:
            ket_qua[truong] = node[truong]

    # Thêm trường lạ ở cuối (nếu có)
    for truong, gia_tri in node.items():
        if truong not in ket_qua:
            ket_qua[truong] = gia_tri

    return ket_qua


# ================================================================
# HÀM PHỤ
# ================================================================
def lay_so_truong():
    """Đếm tổng số trường trong schema."""
    return len(SCHEMA_DAY_DU)


def lay_so_truong_bat_buoc():
    """Đếm số trường bắt buộc."""
    return len(TRUONG_BAT_BUOC)


def la_node_hop_le(node):
    """Kiểm tra nhanh node có hợp lệ không."""
    hop_le, _ = validate_node(node)
    return hop_le


def trich_loi_validate(node):
    """Trả về danh sách lỗi validate (rỗng nếu hợp lệ)."""
    _, loi = validate_node(node)
    return loi


def tom_tat_schema():
    """Tạo chuỗi tóm tắt schema."""
    phan = []
    phan.append(f"📋 Schema node: {lay_so_truong()} trường "
                f"({lay_so_truong_bat_buoc()} bắt buộc)")

    phan.append("\nTrường bắt buộc:")
    for truong in TRUONG_BAT_BUOC:
        mo_ta = lay_mo_ta_truong(truong)
        phan.append(f"  - {truong}: {mo_ta}")

    return "\n".join(phan)


# ================================================================
# SO SÁNH 2 NODE
# ================================================================
def so_sanh_node(node_a, node_b):
    """
    So sánh 2 node theo schema.

    Trả về dict:
        {
            truong_giong: [str],
            truong_khac: [{truong, a, b}],
        }
    """
    if not isinstance(node_a, dict) or not isinstance(node_b, dict):
        return {"truong_giong": [], "truong_khac": []}

    giong = []
    khac = []

    for truong in SCHEMA_DAY_DU.keys():
        a = node_a.get(truong)
        b = node_b.get(truong)

        if a == b:
            giong.append(truong)
        else:
            khac.append({"truong": truong, "a": a, "b": b})

    return {"truong_giong": giong, "truong_khac": khac}


# ================================================================
# TẠO NODE TỪ DICT RÚT GỌN
# ================================================================
def tao_node_tu_rut_gon(dict_rut_gon):
    """
    Tạo node đầy đủ từ dict rút gọn (chỉ 8 trường).
    Bổ sung trường thiếu bằng giá trị mặc định.
    """
    if not isinstance(dict_rut_gon, dict):
        return tao_node_mac_dinh()

    node = tao_node_mac_dinh()
    for truong, gia_tri in dict_rut_gon.items():
        if truong in SCHEMA_DAY_DU:
            node[truong] = gia_tri

    return chuan_hoa_node(node)


# ================================================================
# HÀM PHỤ: ĐẾM TRƯỜNG CÓ DỮ LIỆU
# ================================================================
def dem_truong_co_du_lieu(node):
    """Đếm số trường có dữ liệu (không rỗng)."""
    if not isinstance(node, dict):
        return 0

    dem = 0
    for truong in SCHEMA_DAY_DU.keys():
        gia_tri = node.get(truong)
        if gia_tri not in (None, "", [], {}, 0, 0.0, False):
            dem += 1

    return dem


# ================================================================
# HÀM PHỤ: ĐỘ ĐẦY ĐỦ CỦA NODE
# ================================================================
def do_day_du_node(node):
    """
    Tính độ đầy đủ của node (0.0 - 1.0).
    Node càng nhiều trường có dữ liệu → càng đầy đủ.
    """
    tong = lay_so_truong()
    if tong == 0:
        return 0.0

    dem = dem_truong_co_du_lieu(node)
    return round(dem / tong, 3)
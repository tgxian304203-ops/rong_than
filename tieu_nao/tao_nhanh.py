"""
tao_nhanh.py - Sinh nhánh mới cho cây quyết định Rồng Thần.

Nhiệm vụ:
    - tao_nhanh(task, ngu_canh, chu_so_huu): sinh nhánh mới từ task.
    - tao_nhieu_nhanh(task, so_luong, chu_so_huu): sinh nhiều nhánh cùng lúc.
    - _tim_vi_tri_gan(task, loai_task): tìm vị trí gắn node vào cây.
    - luu_nhanh_vao_kho(node, chu_so_huu): lưu node vào kho 2.

Quy tắc (theo Phần 4):
    - Sinh node mới khi Đại não bí.
    - Dùng ep_viet_truong.py (bước 3) để ép model viết JSON.
    - Validate node theo schema_node.py.
    - Gắn node vào cây đúng vị trí (4 tầng).
    - Lưu node vào kho 2.

Trả về:
    - Nut object (từ cay_quyet_dinh.py) hoặc None.

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
# HÀM CHÍNH: TẠO NHÁNH MỚI
# ================================================================
def tao_nhanh(task, ngu_canh=None, chu_so_huu=""):
    """
    Sinh nhánh mới cho cây quyết định.

    task: dict { noi_dung, yeu_to, loai_task }.
    ngu_canh: dict 10 loại ngữ cảnh.
    chu_so_huu: tên đăng nhập.

    Trả về: Nut object (cay_quyet_dinh.py) hoặc None.
    """
    if not task or not chu_so_huu:
        _ghi_log("loi", "tao_nhanh: thiếu task hoặc chu_so_huu.")
        return None

    _ghi_log(
        "tieu-nao",
        f"Bắt đầu sinh nhánh cho: {str(task.get('noi_dung', ''))[:80]}",
    )

    # 1. Ép model viết JSON (bước 3)
    try:
        from tieu_nao.ep_viet_truong import ep_viet_truong
        node_dict = ep_viet_truong(task, ngu_canh, chu_so_huu)
    except ImportError:
        _ghi_log("loi", "ep_viet_truong.py chưa có.")
        return None

    if not node_dict:
        _ghi_log("loi", "Ép viết trường thất bại.")
        return None

    # 2. Validate + chuẩn hóa node
    try:
        from tieu_nao.schema_node import (
            validate_node, chuan_hoa_node, sap_xep_truong,
        )
        node_dict = chuan_hoa_node(node_dict)
        hop_le, loi = validate_node(node_dict)
        if not hop_le:
            _ghi_log("loi", f"Node không hợp lệ: {', '.join(loi[:3])}")
            return None

        node_dict = sap_xep_truong(node_dict)
    except ImportError:
        _ghi_log("loi", "schema_node.py chưa có.")
        return None

    # 3. Thêm metadata
    node_dict["ngay_tao"] = int(time.time())
    node_dict["lan_dung_cuoi"] = 0

    # 4. Chuyển dict → Nut object
    try:
        from dai_nao.cay_quyet_dinh import Nut
        node_obj = Nut(node_dict)
    except ImportError:
        _ghi_log("loi", "cay_quyet_dinh.py chưa có — trả dict thay Nut.")
        return node_dict
    except Exception as e:
        _ghi_log("loi", f"Không tạo được Nut: {e}")
        return node_dict

    # 5. Lưu node vào kho 2
    luu_nhanh_vao_kho(node_dict, chu_so_huu)

    _ghi_log(
        "tieu-nao",
        f"Sinh nhánh thành công: {node_dict.get('ten', '')[:60]}",
    )

    return node_obj


# ================================================================
# TẠO NHIỀU NHÁNH
# ================================================================
def tao_nhieu_nhanh(task, so_luong=3, chu_so_huu="", ngu_canh=None):
    """
    Sinh nhiều nhánh cùng lúc cho 1 task.

    Trả về: list node (Nut object hoặc dict).
    """
    if not task or not chu_so_huu:
        return []

    try:
        from tieu_nao.ep_viet_truong import ep_viet_nhieu_node
        danh_sach_dict = ep_viet_nhieu_node(task, so_luong, ngu_canh, chu_so_huu)
    except ImportError:
        _ghi_log("loi", "ep_viet_truong.py chưa có.")
        return []

    if not danh_sach_dict:
        return []

    try:
        from tieu_nao.schema_node import (
            validate_node, chuan_hoa_node, sap_xep_truong,
        )
        from dai_nao.cay_quyet_dinh import Nut
    except ImportError:
        return danh_sach_dict

    ket_qua = []
    for node_dict in danh_sach_dict:
        try:
            node_dict = chuan_hoa_node(node_dict)
            hop_le, _ = validate_node(node_dict)
            if not hop_le:
                continue

            node_dict = sap_xep_truong(node_dict)
            node_dict["ngay_tao"] = int(time.time())

            luu_nhanh_vao_kho(node_dict, chu_so_huu)

            try:
                ket_qua.append(Nut(node_dict))
            except Exception:
                ket_qua.append(node_dict)
        except Exception:
            continue

    _ghi_log(
        "tieu-nao",
        f"Sinh {len(ket_qua)}/{so_luong} nhánh cho task.",
    )
    return ket_qua


# ================================================================
# LƯU NHÁNH VÀO KHO 2
# ================================================================
def luu_nhanh_vao_kho(node, chu_so_huu=""):
    """
    Lưu node vào kho 2.

    node: Nut object hoặc dict.
    chu_so_huu: tên đăng nhập.
    """
    if not node:
        return False

    # Chuyển Nut → dict
    if hasattr(node, "sang_dict_phang"):
        du_lieu = node.sang_dict_phang()
    elif isinstance(node, dict):
        du_lieu = dict(node)
    else:
        return False

    # Thêm chủ sở hữu
    du_lieu["chu_so_huu"] = chu_so_huu
    du_lieu["thoi_gian_luu"] = int(time.time())

    try:
        from dai_nao.ghi_nho import luu_node
        ket_qua = luu_node(du_lieu)
        if ket_qua:
            _ghi_log(
                "tieu-nao",
                f"Lưu node {du_lieu.get('id', '')[:12]} vào kho 2.",
            )
        return ket_qua
    except Exception as e:
        _ghi_log("loi", f"Lưu node lỗi: {e}")
        return False


# ================================================================
# TÌM VỊ TRÍ GẮN NODE VÀO CÂY
# ================================================================
def _tim_vi_tri_gan(task, loai_task):
    """
    Tìm node cha để gắn node mới vào cây.

    Ưu tiên:
        1. Node cùng lĩnh vực + cùng loại vấn đề.
        2. Node cùng lĩnh vực.
        3. Node gốc ROOT.

    Trả về: id node cha hoặc "root".
    """
    if not loai_task:
        return "root"

    linh_vuc = (loai_task.get("linh_vuc") or "").lower()
    loai_van_de = (loai_task.get("nhom") or loai_task.get("loai_van_de") or "").lower()

    if not linh_vuc:
        return "root"

    try:
        from dai_nao.cay_quyet_dinh import cay_tu_mongo
        cay = cay_tu_mongo()
    except ImportError:
        return "root"
    except Exception:
        return "root"

    if not cay or not cay.goc:
        return "root"

    # Duyệt tìm node phù hợp
    node_linh_vuc = None
    node_loai_van_de = None

    for node in cay.duyet_tat_ca():
        if node.id == "root":
            continue

        node_linh_vuc_val = (getattr(node, "linh_vuc", "") or "").lower()
        node_loai_vd_val = (getattr(node, "loai_van_de", "") or "").lower()

        # Ưu tiên 1: cùng lĩnh vực + cùng loại vấn đề
        if node_linh_vuc_val == linh_vuc and node_loai_vd_val == loai_van_de:
            return node.id

        # Ưu tiên 2: cùng lĩnh vực
        if node_linh_vuc_val == linh_vuc and not node_linh_vuc:
            node_linh_vuc = node.id

    if node_linh_vuc:
        return node_linh_vuc

    # Không tìm thấy → về root
    return "root"


def lay_vi_tri_gan(task, loai_task):
    """Public API cho _tim_vi_tri_gan."""
    return _tim_vi_tri_gan(task, loai_task)


# ================================================================
# GẮN NHÁNH VÀO CÂY
# ================================================================
def gan_vao_cay(node, task=None, loai_task=None):
    """
    Gắn node vào cây quyết định.

    node: Nut object hoặc dict.
    task: dict task gốc.
    loai_task: dict phân loại.

    Trả về: True nếu gắn thành công.
    """
    if not node:
        return False

    try:
        from dai_nao.cay_quyet_dinh import cay_tu_mongo, luu_cay_vao_mongo, Nut

        cay = cay_tu_mongo()
        if not cay:
            _ghi_log("loi", "Không đọc được cây từ kho 2.")
            return False

        # Chuyển node thành Nut nếu cần
        if isinstance(node, dict):
            try:
                node = Nut(node)
            except Exception:
                return False

        # Tìm vị trí gắn
        id_cha = _tim_vi_tri_gan(task, loai_task)

        # Gắn vào cây
        if not cay.them_node(node, id_cha):
            _ghi_log("loi", f"Không gắn được node vào cha {id_cha}.")
            return False

        # Lưu cây vào kho 2
        if luu_cay_vao_mongo(cay):
            _ghi_log(
                "tieu-nao",
                f"Đã gắn node {node.id[:12]} vào cha {id_cha}.",
            )
            return True

        return False

    except ImportError:
        _ghi_log("loi", "cay_quyet_dinh.py chưa có.")
        return False
    except Exception as e:
        _ghi_log("loi", f"Gắn nhánh lỗi: {e}")
        return False


# ================================================================
# SINH NHÁNH + GẮN VÀO CÂY (API gộp)
# ================================================================
def tao_va_gan_nhanh(task, ngu_canh=None, chu_so_huu="", loai_task=None):
    """
    Sinh nhánh mới + gắn vào cây.

    Trả về: Nut object hoặc None.
    """
    node = tao_nhanh(task, ngu_canh, chu_so_huu)
    if not node:
        return None

    if loai_task is None:
        loai_task = task.get("loai_task") if isinstance(task, dict) else None

    gan_vao_cay(node, task, loai_task)
    return node


# ================================================================
# HÀM PHỤ: TÓM TẮT NHÁNH MỚI
# ================================================================
def tom_tat_nhanh(node):
    """Tạo chuỗi tóm tắt nhánh mới."""
    if not node:
        return ""

    if hasattr(node, "sang_dict_phang"):
        node = node.sang_dict_phang()

    if not isinstance(node, dict):
        return ""

    return (
        f"🌿 Nhánh mới:\n"
        f"  - ID: {node.get('id', '?')}\n"
        f"  - Tên: {node.get('ten', '?')}\n"
        f"  - Lĩnh vực: {node.get('linh_vuc', '?')}\n"
        f"  - Nhóm: {node.get('loai_van_de', '?')}\n"
        f"  - Cách giải: {node.get('cach_giai_phap', '?')}\n"
        f"  - Score: {node.get('score', 0.7)}"
    )


# ================================================================
# HÀM PHỤ: ĐẾM NHÁNH ĐÃ SINH
# ================================================================
def dem_nhanh_da_sinh(chu_so_huu, ngay=1):
    """
    Đếm số nhánh đã sinh trong N ngày gần nhất.
    """
    nguong = int(time.time()) - ngay * 24 * 3600

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        dem = db["node"].count_documents({
            "chu_so_huu": chu_so_huu,
            "thoi_gian_luu": {"$gte": nguong},
        })
        return dem
    except Exception:
        return 0


# ================================================================
# HÀM PHỤ: KIỂM TRA ĐÃ CÓ NODE TƯƠNG TỰ CHƯA
# ================================================================
def da_co_node_tuong_tu(task, nguong=0.7):
    """
    Kiểm tra đã có node tương tự trong cây chưa.
    Tránh sinh trùng.

    Trả về: node tương tự hoặc None.
    """
    if not task:
        return None

    noi_dung = task.get("noi_dung", "")
    if not noi_dung:
        return None

    try:
        from dai_nao.duyet_cay import duyet_cay
        loai_task = task.get("loai_task", {})
        yeu_to = task.get("yeu_to", {})
        node = duyet_cay(noi_dung, loai_task, yeu_to)
        if node:
            return node
    except ImportError:
        pass
    except Exception:
        pass

    return None


# ================================================================
# HÀM PHỤ: GHI LỊCH SỬ SINH NHÁNH
# ================================================================
def ghi_lich_su_sinh(node, chu_so_huu, task_goc=""):
    """Ghi lịch sử sinh nhánh vào kho 2."""
    if not node:
        return False

    if hasattr(node, "sang_dict_phang"):
        node_dict = node.sang_dict_phang()
    elif isinstance(node, dict):
        node_dict = node
    else:
        return False

    try:
        from dai_nao.ghi_nho import luu_lich_su_hoc
        luu_lich_su_hoc({
            "loai": "tao_nhanh",
            "chu_so_huu": chu_so_huu,
            "id_node": node_dict.get("id"),
            "ten_node": node_dict.get("ten"),
            "linh_vuc": node_dict.get("linh_vuc"),
            "task_goc": task_goc[:200],
            "thoi_gian": int(time.time()),
        })
        return True
    except Exception as e:
        _ghi_log("loi", f"Ghi lịch sử sinh lỗi: {e}")
        return False
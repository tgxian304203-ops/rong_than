"""
cap_nhat_tu_dien_loi.py - Cập nhật từ điển lỗi Rồng Thần.

Nhiệm vụ:
    - cap_nhat_tu_dien(loai_loi, du_lieu): lưu/cập nhật 1 mục.
    - hoc_tu_loi_moi(loai_loi, stderr, cach_sua): học từ lỗi mới.
    - dong_bo_tu_doc_loi(): đồng bộ từ bảng LOAI_LOI của doc_loi.py.
    - xoa_muc_tu_dien(loai_loi): xóa 1 mục.
    - lay_tat_ca(): lấy toàn bộ từ điển.
    - tim_kiem_tu_dien(tu_khoa): tìm kiếm mục.
    - thong_ke_tu_dien(): thống kê.

Quy tắc:
    - Từ điển lưu vào kho 2, collection tu_dien_loi.
    - Không ghi đè nếu mục đã tồn tại và giống.
    - Có trường "phien_ban" để đếm số lần cập nhật.
    - Có trường "nguon" để biết học từ đâu (tinh / tu_dong / nguoi_dung).
    - Tự tăng "so_lan_gap" mỗi lần gặp lại lỗi.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import re
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
# ĐỌC / GHI TỪ ĐIỂN (qua kho 2)
# ================================================================
def _doc_tu_dien():
    """Đọc toàn bộ từ điển từ kho 2."""
    try:
        from dai_nao.ghi_nho import lay_tu_dien_loi
        return lay_tu_dien_loi() or []
    except Exception as e:
        _ghi_log("loi", f"Không đọc được từ điển lỗi: {e}")
        return []


def _ghi_tu_dien(loai_loi, du_lieu):
    """Ghi 1 mục vào từ điển kho 2."""
    try:
        from dai_nao.ghi_nho import luu_tu_dien_loi
        return luu_tu_dien_loi(loai_loi, du_lieu)
    except Exception as e:
        _ghi_log("loi", f"Không ghi được từ điển lỗi: {e}")
        return False


# ================================================================
# CẬP NHẬT 1 MỤC
# ================================================================
def cap_nhat_tu_dien(loai_loi, du_lieu):
    """
    Lưu/cập nhật 1 mục trong từ điển lỗi.

    loai_loi: tên loại lỗi (NameError, TypeError, ...).
    du_lieu: dict mô tả:
        - mo_ta: str
        - vi_du: str
        - goi_y: list[str]
        - code_sua_mau: str
        - cach_sua_regex: dict { regex, thay_the }
        - nguon: "tinh" | "tu_dong" | "nguoi_dung"
        - ngon_ngu: str

    Trả về: True nếu thành công.
    """
    if not loai_loi:
        return False

    du_lieu = du_lieu or {}

    # Đọc mục cũ (nếu có)
    cu = _tim_muc(loai_loi)
    phien_ban = (cu.get("phien_ban", 0) + 1) if cu else 1
    so_lan_gap = cu.get("so_lan_gap", 0) if cu else 0

    # Gộp dữ liệu mới với cũ — ưu tiên mới
    muc_moi = {
        "loai_loi": loai_loi,
        "mo_ta": du_lieu.get("mo_ta") or (cu.get("mo_ta", "") if cu else ""),
        "vi_du": du_lieu.get("vi_du") or (cu.get("vi_du", "") if cu else ""),
        "goi_y": du_lieu.get("goi_y") or (cu.get("goi_y", []) if cu else []),
        "code_sua_mau": du_lieu.get("code_sua_mau") or (cu.get("code_sua_mau", "") if cu else ""),
        "cach_sua_regex": du_lieu.get("cach_sua_regex") or (cu.get("cach_sua_regex") if cu else None),
        "ngon_ngu": du_lieu.get("ngon_ngu") or (cu.get("ngon_ngu", "") if cu else ""),
        "nguon": du_lieu.get("nguon") or (cu.get("nguon", "tinh") if cu else "tinh"),
        "phien_ban": phien_ban,
        "so_lan_gap": so_lan_gap,
        "thoi_gian_tao": (cu.get("thoi_gian_tao") if cu else int(time.time())),
        "thoi_gian_cap_nhat": int(time.time()),
    }

    thanh_cong = _ghi_tu_dien(loai_loi, muc_moi)

    if thanh_cong:
        _ghi_log(
            "dai-nao",
            f"Cập nhật từ điển lỗi '{loai_loi}' (v{phien_ban}, nguồn={muc_moi['nguon']})",
        )

    return thanh_cong


# ================================================================
# TÌM 1 MỤC
# ================================================================
def _tim_muc(loai_loi):
    """Tìm 1 mục trong từ điển theo loại lỗi."""
    if not loai_loi:
        return None
    for muc in _doc_tu_dien():
        if muc.get("loai_loi") == loai_loi:
            return muc
    return None


def tim_kiem_tu_dien(tu_khoa):
    """
    Tìm kiếm mục trong từ điển theo từ khóa.

    tu_khoa: chuỗi tìm (khớp trong loai_loi, mo_ta, vi_du).

    Trả về: list mục khớp.
    """
    if not tu_khoa:
        return []

    tu_khoa = tu_khoa.lower()
    ket_qua = []

    for muc in _doc_tu_dien():
        loai = (muc.get("loai_loi") or "").lower()
        mo_ta = (muc.get("mo_ta") or "").lower()
        vi_du = (muc.get("vi_du") or "").lower()

        if tu_khoa in loai or tu_khoa in mo_ta or tu_khoa in vi_du:
            ket_qua.append(muc)

    return ket_qua


# ================================================================
# HỌC TỪ LỖI MỚI
# ================================================================
def hoc_tu_loi_moi(loai_loi, stderr, cach_sua, code_sua_mau=""):
    """
    Học từ 1 lỗi mới gặp + cách sửa thành công.

    loai_loi: tên loại lỗi.
    stderr: chuỗi lỗi gốc.
    cach_sua: mô tả cách sửa (str) hoặc dict { regex, thay_the }.
    code_sua_mau: code mẫu đã sửa (tùy chọn).

    Trả về: True nếu học thành công.
    """
    if not loai_loi:
        return False

    # Nếu mục đã tồn tại → chỉ tăng so_lan_gap
    cu = _tim_muc(loai_loi)
    if cu:
        so_lan_gap = cu.get("so_lan_gap", 0) + 1
        _ghi_tu_dien(loai_loi, {**cu, "so_lan_gap": so_lan_gap,
                                "thoi_gian_cap_nhat": int(time.time())})
        return True

    # Mục mới → tạo
    du_lieu = {
        "loai_loi": loai_loi,
        "mo_ta": stderr[:200] if stderr else "",
        "vi_du": stderr[:100] if stderr else "",
        "goi_y": [],
        "code_sua_mau": code_sua_mau,
        "cach_sua_regex": cach_sua if isinstance(cach_sua, dict) else None,
        "nguon": "tu_dong",
        "so_lan_gap": 1,
        "phien_ban": 1,
    }

    # Nếu cach_sua là str → thêm vào goi_y
    if isinstance(cach_sua, str) and cach_sua:
        du_lieu["goi_y"] = [cach_sua]

    thanh_cong = _ghi_tu_dien(loai_loi, du_lieu)

    if thanh_cong:
        _ghi_log("dai-nao", f"Học lỗi mới: {loai_loi}")

    return thanh_cong


# ================================================================
# ĐỒNG BỘ TỪ doc_loi.py
# ================================================================
def dong_bo_tu_doc_loi():
    """
    Đồng bộ toàn bộ bảng LOAI_LOI từ doc_loi.py vào từ điển kho 2.
    Chỉ thêm mục chưa có — không ghi đè mục đã có.

    Trả về: dict { them_moi: int, da_co: int, loi: int }
    """
    try:
        from dai_nao.doc_loi import LOAI_LOI
    except ImportError:
        _ghi_log("loi", "doc_loi.py chưa có — không đồng bộ được.")
        return {"them_moi": 0, "da_co": 0, "loi": 0}

    da_co = 0
    them_moi = 0
    loi = 0

    for loai_loi, thong_tin in LOAI_LOI.items():
        cu = _tim_muc(loai_loi)
        if cu:
            da_co += 1
            continue

        du_lieu = {
            "loai_loi": loai_loi,
            "mo_ta": thong_tin.get("mo_ta", ""),
            "vi_du": thong_tin.get("vi_du", ""),
            "goi_y": thong_tin.get("goi_y", []),
            "code_sua_mau": thong_tin.get("code_sua_mau", ""),
            "cach_sua_regex": None,
            "ngon_ngu": thong_tin.get("ngon_ngu", ""),
            "nguon": "tinh",
            "phien_ban": 1,
            "so_lan_gap": 0,
            "thoi_gian_tao": int(time.time()),
            "thoi_gian_cap_nhat": int(time.time()),
        }

        if _ghi_tu_dien(loai_loi, du_lieu):
            them_moi += 1
        else:
            loi += 1

    _ghi_log(
        "dai-nao",
        f"Đồng bộ từ điển: +{them_moi} mới, {da_co} đã có, {loi} lỗi",
    )

    return {"them_moi": them_moi, "da_co": da_co, "loi": loi}


# ================================================================
# XÓA 1 MỤC
# ================================================================
def xoa_muc_tu_dien(loai_loi):
    """Xóa 1 mục khỏi từ điển."""
    if not loai_loi:
        return False

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        ket_qua = db["tu_dien_loi"].delete_one({"loai_loi": loai_loi})
        if ket_qua.deleted_count > 0:
            _ghi_log("dai-nao", f"Xóa mục từ điển: {loai_loi}")
            return True
    except Exception as e:
        _ghi_log("loi", f"Không xóa được mục từ điển: {e}")

    return False


# ================================================================
# LẤY TẤT CẢ
# ================================================================
def lay_tat_ca():
    """Lấy toàn bộ từ điển lỗi."""
    return _doc_tu_dien()


# ================================================================
# THỐNG KÊ
# ================================================================
def thong_ke_tu_dien():
    """
    Thống kê từ điển lỗi.

    Trả về: dict
        {
            tong: int,
            theo_nguon: dict,
            theo_ngon_ngu: dict,
            top_gap_nhieu: list,
            moi_cap_nhat: list,
        }
    """
    danh_sach = _doc_tu_dien()
    tong = len(danh_sach)

    theo_nguon = {}
    theo_ngon_ngu = {}

    for muc in danh_sach:
        nguon = muc.get("nguon", "khong_ro")
        theo_nguon[nguon] = theo_nguon.get(nguon, 0) + 1

        nn = muc.get("ngon_ngu", "khong_ro") or "khong_ro"
        theo_ngon_ngu[nn] = theo_ngon_ngu.get(nn, 0) + 1

    # Top gặp nhiều
    sap_xep_gap = sorted(
        danh_sach,
        key=lambda m: m.get("so_lan_gap", 0),
        reverse=True,
    )[:10]

    top_gap = [
        {"loai_loi": m.get("loai_loi"), "so_lan_gap": m.get("so_lan_gap", 0)}
        for m in sap_xep_gap if m.get("so_lan_gap", 0) > 0
    ]

    # Mới cập nhật
    sap_xep_moi = sorted(
        danh_sach,
        key=lambda m: m.get("thoi_gian_cap_nhat", 0),
        reverse=True,
    )[:10]

    moi_cap_nhat = [
        {"loai_loi": m.get("loai_loi"),
         "thoi_gian_cap_nhat": m.get("thoi_gian_cap_nhat")}
        for m in sap_xep_moi
    ]

    return {
        "tong": tong,
        "theo_nguon": theo_nguon,
        "theo_ngon_ngu": theo_ngon_ngu,
        "top_gap_nhieu": top_gap,
        "moi_cap_nhat": moi_cap_nhat,
    }


# ================================================================
# TĂNG SỐ LẦN GẶP
# ================================================================
def tang_so_lan_gap(loai_loi):
    """Tăng số lần gặp của 1 mục."""
    if not loai_loi:
        return False

    cu = _tim_muc(loai_loi)
    if not cu:
        return False

    so_lan_gap = cu.get("so_lan_gap", 0) + 1
    return _ghi_tu_dien(loai_loi, {**cu, "so_lan_gap": so_lan_gap})


# ================================================================
# GỢI Ý TỪ ĐIỂN
# ================================================================
def goi_y_tu_dien(loai_loi):
    """
    Lấy gợi ý sửa từ từ điển (dùng cho phan_tich_loi).

    Trả về: list[str] hoặc [].
    """
    muc = _tim_muc(loai_loi)
    if not muc:
        return []

    ket_qua = []
    goi_y = muc.get("goi_y", [])
    if isinstance(goi_y, list):
        ket_qua.extend(goi_y)

    code_mau = muc.get("code_sua_mau", "")
    if code_mau:
        ket_qua.append(f"Code mẫu:\n{code_mau}")

    return ket_qua


# ================================================================
# XUẤT / NHẬP JSON (backup)
# ================================================================
def xuat_json():
    """Xuất từ điển thành JSON (dùng backup)."""
    import json
    try:
        return json.dumps(_doc_tu_dien(), ensure_ascii=False, indent=2)
    except Exception as e:
        _ghi_log("loi", f"Không xuất JSON được: {e}")
        return ""


def nhap_tu_json(chuoi_json):
    """
    Nhập từ điển từ JSON (dùng restore).

    Trả về: dict { them_moi, da_co, loi }
    """
    import json
    try:
        danh_sach = json.loads(chuoi_json)
    except (json.JSONDecodeError, TypeError):
        return {"them_moi": 0, "da_co": 0, "loi": 0}

    if not isinstance(danh_sach, list):
        return {"them_moi": 0, "da_co": 0, "loi": 0}

    them_moi = da_co = loi = 0
    for muc in danh_sach:
        loai = muc.get("loai_loi")
        if not loai:
            loi += 1
            continue

        if _tim_muc(loai):
            da_co += 1
            continue

        if _ghi_tu_dien(loai, muc):
            them_moi += 1
        else:
            loi += 1

    return {"them_moi": them_moi, "da_co": da_co, "loi": loi}


# ================================================================
# XÓA TOÀN BỘ (cẩn thận)
# ================================================================
def xoa_tat_ca():
    """Xóa toàn bộ từ điển lỗi (cẩn thận — không phục hồi được)."""
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        ket_qua = db["tu_dien_loi"].delete_many({})
        _ghi_log("dai-nao", f"Xóa toàn bộ từ điển: {ket_qua.deleted_count} mục")
        return ket_qua.deleted_count
    except Exception as e:
        _ghi_log("loi", f"Không xóa được từ điển: {e}")
        return 0
"""
luu_ket_qua.py - Lưu kết quả chạy vào Cây linh hồn.

Nhiệm vụ:
    - Lưu kết quả sau khi Model chạy xong.
    - Lưu stdout / stderr / returncode.
    - Lưu vào collection code_da_viet (gộp với code).

Kết quả gồm:
    - stdout: nội dung in ra.
    - stderr: lỗi (nếu có).
    - returncode: mã trả về.
    - thanh_cong: True/False.
    - thoi_gian_chay: thời gian chạy (giây).

Nguyên tắc:
    - Lưu vào kho 2, collection code_da_viet.
    - Cập nhật liên tục.
"""

import time

from luu_tru.ghi_nho import (
    luu_code_da_viet as _luu_code,
    lay_code_da_viet as _lay_code,
)


# ================================================================
# LƯU KẾT QUẢ CHẠY
# ================================================================
def luu_ket_qua(chu_so_huu, id_chat, buoc, ket_qua):
    """
    Lưu kết quả chạy cho 1 bước.

    ket_qua: {
        stdout, stderr, returncode, thanh_cong, thoi_gian_chay
    }

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat or not ket_qua:
        return False

    code_cu = _lay_code(chu_so_huu, id_chat, buoc)
    if not code_cu:
        return False

    du_lieu_ket_qua = {
        "stdout": ket_qua.get("stdout", ""),
        "stderr": ket_qua.get("stderr", ""),
        "returncode": ket_qua.get("returncode", -1),
        "thanh_cong": ket_qua.get("thanh_cong", False),
        "thoi_gian_chay": ket_qua.get("thoi_gian_chay", 0),
        "thoi_gian_luu_ket_qua": int(time.time()),
    }

    return _luu_code({
        "chu_so_huu": chu_so_huu,
        "id_chat": id_chat,
        "buoc": buoc,
        "file": code_cu.get("file", ""),
        "code": code_cu.get("code", ""),
        "phien_ban": (code_cu.get("phien_ban", 0) or 0) + 1,
        "ket_qua": du_lieu_ket_qua,
        "thoi_gian": int(time.time()),
    })


# ================================================================
# LƯU KẾT QUẢ THÀNH CÔNG
# ================================================================
def luu_thanh_cong(chu_so_huu, id_chat, buoc, stdout="", returncode=0):
    """Lưu kết quả thành công."""
    return luu_ket_qua(chu_so_huu, id_chat, buoc, {
        "stdout": stdout,
        "stderr": "",
        "returncode": returncode,
        "thanh_cong": True,
        "thoi_gian_chay": 0,
    })


# ================================================================
# LƯU KẾT QUẢ THẤT BẠI
# ================================================================
def luu_that_bai(chu_so_huu, id_chat, buoc, stderr="", returncode=-1):
    """Lưu kết quả thất bại."""
    return luu_ket_qua(chu_so_huu, id_chat, buoc, {
        "stdout": "",
        "stderr": stderr,
        "returncode": returncode,
        "thanh_cong": False,
        "thoi_gian_chay": 0,
    })


# ================================================================
# ĐỌC KẾT QUẢ
# ================================================================
def doc_ket_qua(chu_so_huu, id_chat, buoc):
    """Đọc kết quả của 1 bước."""
    du_lieu = _lay_code(chu_so_huu, id_chat, buoc)
    if not du_lieu:
        return None
    return du_lieu.get("ket_qua")


# ================================================================
# ĐẾM SỐ BƯỚC THÀNH CÔNG
# ================================================================
def dem_thanh_cong(chu_so_huu, id_chat):
    """Đếm số bước chạy thành công."""
    from luu_tru.ghi_nho import lay_tat_ca_code
    tat_ca = lay_tat_ca_code(chu_so_huu, id_chat)

    dem = 0
    for item in tat_ca:
        kq = item.get("ket_qua") or {}
        if kq.get("thanh_cong"):
            dem += 1

    return dem


# ================================================================
# TÓM TẮT KẾT QUẢ
# ================================================================
def tom_tat_ket_qua(chu_so_huu, id_chat, buoc):
    """Tạo chuỗi tóm tắt kết quả."""
    kq = doc_ket_qua(chu_so_huu, id_chat, buoc)
    if not kq:
        return ""

    if kq.get("thanh_cong"):
        stdout = kq.get("stdout", "")
        return f"✅ Thành công\n{stdout[:500]}"

    stderr = kq.get("stderr", "")
    return f"❌ Thất bại\n{stderr[:500]}"
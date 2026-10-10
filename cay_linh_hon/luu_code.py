"""
luu_code.py - Lưu code đã viết vào Cây linh hồn.

Nhiệm vụ:
    - Lưu code sau khi Model viết xong.
    - Mỗi bước lưu 1 bản (có phien_ban).
    - Code đã viết GIỮ MÃI MÃI, không xóa.
    - Dùng khi Boss Thế cần gửi lại code cũ.

Code gồm:
    - buoc: bước số mấy.
    - file: tên file (VD: toan.py).
    - code: nội dung code.
    - phien_ban: phiên bản (1, 2, 3...).
    - thoi_gian: timestamp.

Nguyên tắc:
    - Lưu vào kho 2, collection code_da_viet.
    - Gắn chu_so_huu + id_chat.
"""

import time

from luu_tru.ghi_nho import (
    luu_code_da_viet as _luu_code,
    lay_code_da_viet as _lay_code,
    lay_tat_ca_code as _lay_tat_ca,
    xoa_code_da_viet as _xoa_code,
)


# ================================================================
# LƯU CODE
# ================================================================
def luu_code(chu_so_huu, id_chat, buoc, file, code,
             phien_ban=1):
    """
    Lưu code đã viết cho 1 bước.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat or not code:
        return False

    du_lieu = {
        "chu_so_huu": chu_so_huu,
        "id_chat": id_chat,
        "buoc": buoc,
        "file": file or "",
        "code": code,
        "phien_ban": phien_ban,
        "thoi_gian": int(time.time()),
    }

    return _luu_code(du_lieu)


# ================================================================
# LƯU CODE (TỰ ĐỘNG TĂNG PHIÊN BẢN)
# ================================================================
def luu_code_moi(chu_so_huu, id_chat, buoc, file, code):
    """
    Lưu code mới — tự động tăng phien_ban nếu bước đã có code.

    Trả về: True/False.
    """
    cu = _lay_code(chu_so_huu, id_chat, buoc)
    if cu:
        phien_ban_moi = (cu.get("phien_ban", 0) or 0) + 1
    else:
        phien_ban_moi = 1

    return luu_code(chu_so_huu, id_chat, buoc, file, code, phien_ban_moi)


# ================================================================
# ĐỌC CODE THEO BƯỚC
# ================================================================
def doc_code(chu_so_huu, id_chat, buoc):
    """
    Đọc code của 1 bước (bản mới nhất).

    Trả về: dict hoặc None.
    """
    return _lay_code(chu_so_huu, id_chat, buoc)


# ================================================================
# ĐỌC TẤT CẢ CODE
# ================================================================
def doc_tat_ca_code(chu_so_huu, id_chat):
    """
    Đọc tất cả code của 1 chat (sắp xếp theo bước).

    Trả về: list.
    """
    return _lay_tat_ca(chu_so_huu, id_chat)


# ================================================================
# LẤY CODE ĐÃ VIẾT THEO FILE
# ================================================================
def lay_code_theo_file(chu_so_huu, id_chat, ten_file):
    """
    Lấy code theo tên file (bản mới nhất).

    Trả về: dict hoặc None.
    """
    tat_ca = doc_tat_ca_code(chu_so_huu, id_chat)

    ket_qua = None
    for item in tat_ca:
        if item.get("file") == ten_file:
            if ket_qua is None:
                ket_qua = item
            else:
                if item.get("phien_ban", 0) > ket_qua.get("phien_ban", 0):
                    ket_qua = item

    return ket_qua


# ================================================================
# GỬI LẠI CODE CŨ (CHO BOSS THẾ)
# ================================================================
def lay_code_de_gui_lai(chu_so_huu, id_chat, buoc=None):
    """
    Lấy code để gửi lại cho user khi họ yêu cầu.

    buoc: nếu None → lấy tất cả.

    Trả về: dict hoặc list.
    """
    if buoc is not None:
        return doc_code(chu_so_huu, id_chat, buoc)
    return doc_tat_ca_code(chu_so_huu, id_chat)


# ================================================================
# ĐẾM SỐ FILE ĐÃ VIẾT
# ================================================================
def dem_file_da_viet(chu_so_huu, id_chat):
    """Đếm số file đã viết."""
    tat_ca = doc_tat_ca_code(chu_so_huu, id_chat)
    return len(set(item.get("file", "") for item in tat_ca if item.get("file")))


# ================================================================
# XÓA CODE (CHỈ DÙNG KHI XÓA CHAT)
# ================================================================
def xoa_code(chu_so_huu, id_chat):
    """Xóa tất cả code của 1 chat. CHỈ DÙNG KHI XÓA CHAT."""
    return _xoa_code(chu_so_huu, id_chat)
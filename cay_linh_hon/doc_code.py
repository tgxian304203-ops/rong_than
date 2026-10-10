"""
doc_code.py - Đọc code đã viết từ Cây linh hồn.

Nhiệm vụ:
    - Đọc code của 1 bước.
    - Đọc code theo file.
    - Đọc tất cả code của 1 chat.
    - Format code để gửi lại user.

Nguyên tắc:
    - Chỉ đọc — không sửa.
    - Code đã lưu GIỮ MÃI MÃI.
"""

from luu_tru.ghi_nho import (
    lay_code_da_viet as _lay_code,
    lay_tat_ca_code as _lay_tat_ca,
)


# ================================================================
# ĐỌC CODE 1 BƯỚC
# ================================================================
def doc_code_buoc(chu_so_huu, id_chat, buoc):
    """
    Đọc code của bước (bản mới nhất).

    Trả về: dict hoặc None.
    """
    return _lay_code(chu_so_huu, id_chat, buoc)


# ================================================================
# ĐỌC TẤT CẢ CODE
# ================================================================
def doc_tat_ca(chu_so_huu, id_chat):
    """Đọc tất cả code (sắp xếp theo bước)."""
    return _lay_tat_ca(chu_so_huu, id_chat)


# ================================================================
# ĐỌC CODE THEO FILE
# ================================================================
def doc_code_file(chu_so_huu, id_chat, ten_file):
    """Đọc code của 1 file (bản mới nhất)."""
    tat_ca = doc_tat_ca(chu_so_huu, id_chat)

    ket_qua = None
    for item in tat_ca:
        if item.get("file") == ten_file:
            if ket_qua is None or item.get("phien_ban", 0) > ket_qua.get("phien_ban", 0):
                ket_qua = item

    return ket_qua


# ================================================================
# ĐỌC CODE MỚI NHẤT
# ================================================================
def doc_code_moi_nhat(chu_so_huu, id_chat):
    """Đọc code mới nhất của chat."""
    tat_ca = doc_tat_ca(chu_so_huu, id_chat)
    if not tat_ca:
        return None

    tat_ca.sort(key=lambda x: (x.get("buoc", 0), x.get("phien_ban", 0)), reverse=True)
    return tat_ca[0] if tat_ca else None


# ================================================================
# ĐỌC CODE THEO KHOẢNG BƯỚC
# ================================================================
def doc_code_tu_buoc(chu_so_huu, id_chat, tu_buoc, den_buoc=None):
    """
    Đọc code trong khoảng bước.

    Trả về: list.
    """
    tat_ca = doc_tat_ca(chu_so_huu, id_chat)
    if den_buoc is None:
        den_buoc = tu_buoc

    return [
        item for item in tat_ca
        if tu_buoc <= item.get("buoc", 0) <= den_buoc
    ]


# ================================================================
# FORMAT CODE ĐỂ GỬI USER
# ================================================================
def format_gui_user(chu_so_huu, id_chat, buoc=None):
    """
    Format code để gửi user (dạng markdown với ```).

    buoc: nếu None → gửi tất cả.

    Trả về: chuỗi.
    """
    if buoc is not None:
        du_lieu = doc_code_buoc(chu_so_huu, id_chat, buoc)
        if not du_lieu:
            return ""
        return _format_mot_file(du_lieu)

    tat_ca = doc_tat_ca(chu_so_huu, id_chat)
    if not tat_ca:
        return ""

    phan = []
    for item in tat_ca:
        phan.append(_format_mot_file(item))

    return "\n\n".join(phan)


def _format_mot_file(du_lieu):
    """Format 1 file code."""
    if not du_lieu:
        return ""

    ten_file = du_lieu.get("file", "code")
    code = du_lieu.get("code", "")
    ngon_ngu = _doan_ngon_ngu(ten_file)

    return f"**{ten_file}**\n```{ngon_ngu}\n{code}\n```"


def _doan_ngon_ngu(ten_file):
    """Đoán ngôn ngữ từ tên file."""
    if not ten_file or "." not in ten_file:
        return ""

    duoi = ten_file.rsplit(".", 1)[-1].lower()
    bang = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "html": "html",
        "css": "css",
        "json": "json",
        "md": "markdown",
        "sql": "sql",
        "sh": "bash",
    }
    return bang.get(duoi, "")


# ================================================================
# ĐẾM SỐ BƯỚC CÓ CODE
# ================================================================
def dem_buoc_co_code(chu_so_huu, id_chat):
    """Đếm số bước có code."""
    tat_ca = doc_tat_ca(chu_so_huu, id_chat)
    return len(set(item.get("buoc", 0) for item in tat_ca))


# ================================================================
# KIỂM TRA CÓ CODE KHÔNG
# ================================================================
def co_code(chu_so_huu, id_chat):
    """Kiểm tra chat đã có code chưa."""
    return len(doc_tat_ca(chu_so_huu, id_chat)) > 0
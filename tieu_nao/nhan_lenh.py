"""
nhan_lenh.py - Nhận lệnh từ Cây linh hồn.

Nhiệm vụ:
    - Nhận lệnh từ dieu_phoi (Đại não) hoặc ket_noi (Cây linh hồn).
    - Chuẩn bị dữ liệu cho ep_model.
    - Trả kết quả về cho Đại não.

Nguyên tắc:
    - Đây là entry point của Tiểu não.
    - Không chứa logic — chỉ nhận + chuyển.
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
# NHẬN LỆNH
# ================================================================
def nhan_lenh(du_lieu):
    """
    Nhận lệnh từ Đại não / Cây linh hồn và chuyển cho ep_model.

    du_lieu: {
        noi_dung: str,
        chu_so_huu: str,
        id_chat: str,
        id_du_an: str,
        lich_su: list,
        buoc: int?,
        loai_task: str?,   # "sinh_code" | "tra_loi" | "sua_code"
    }

    Trả về: {
        thanh_cong: bool,
        tra_loi: str,
        code: str?,
        ngon_ngu: str?,
        ket_qua_chay: dict?,
        loi: str?,
    }
    """
    if not du_lieu or not isinstance(du_lieu, dict):
        return {
            "thanh_cong": False,
            "loi": "Dữ liệu đầu vào không hợp lệ.",
        }

    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    if not noi_dung:
        return {
            "thanh_cong": False,
            "loi": "Không có nội dung để xử lý.",
        }

    chu_so_huu = du_lieu.get("chu_so_huu") or "khach"
    id_chat = du_lieu.get("id_chat") or ""
    loai_task = du_lieu.get("loai_task") or "tra_loi"

    _ghi_log("tieu-nao", f"Nhận lệnh: {loai_task} | {noi_dung[:80]}")

    # Chuyển cho ep_model
    try:
        from tieu_nao.ep_model import ep_model
        ket_qua = ep_model({
            "noi_dung": noi_dung,
            "chu_so_huu": chu_so_huu,
            "id_chat": id_chat,
            "id_du_an": du_lieu.get("id_du_an") or "",
            "lich_su": du_lieu.get("lich_su") or [],
            "buoc": du_lieu.get("buoc", 0),
            "loai_task": loai_task,
            "thoi_gian": int(time.time()),
        })
        return ket_qua
    except Exception as e:
        _ghi_log("loi", f"Tiểu não xử lý lỗi: {e}")
        return {
            "thanh_cong": False,
            "loi": f"Tiểu não xử lý lỗi: {e}",
        }


# ================================================================
# NHẬN LỆNH SINH CODE
# ================================================================
def nhan_lenh_sinh_code(du_lieu):
    """Shortcut cho loai_task = sinh_code."""
    du_lieu_moi = dict(du_lieu)
    du_lieu_moi["loai_task"] = "sinh_code"
    return nhan_lenh(du_lieu_moi)


# ================================================================
# NHẬN LỆNH SỬA CODE
# ================================================================
def nhan_lenh_sua_code(du_lieu):
    """Shortcut cho loai_task = sua_code."""
    du_lieu_moi = dict(du_lieu)
    du_lieu_moi["loai_task"] = "sua_code"
    return nhan_lenh(du_lieu_moi)


# ================================================================
# NHẬN LỆNH TRẢ LỜI
# ================================================================
def nhan_lenh_tra_loi(du_lieu):
    """Shortcut cho loai_task = tra_loi."""
    du_lieu_moi = dict(du_lieu)
    du_lieu_moi["loai_task"] = "tra_loi"
    return nhan_lenh(du_lieu_moi)
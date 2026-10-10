"""
nhan_yeu_cau.py - Nhận yêu cầu từ giao diện.

Nhiệm vụ:
    - Nhận tin nhắn + metadata từ giao diện.
    - Kiểm tra dữ liệu đầu vào.
    - Chuyển cho dieu_phoi xử lý.
    - Trả kết quả về giao diện.

Nguyên tắc:
    - Đây là entry point của Đại não.
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
# NHẬN YÊU CẦU
# ================================================================
def nhan_yeu_cau(du_lieu):
    """
    Nhận yêu cầu từ giao diện và chuyển cho dieu_phoi.

    du_lieu: {
        noi_dung: str,
        anh: [str],
        file: [str],
        lich_su: [dict],
        id_chat: str,
        id_du_an: str,
        chu_so_huu: str,
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
    danh_sach_anh = du_lieu.get("anh") or []
    danh_sach_file = du_lieu.get("file") or []
    id_chat = du_lieu.get("id_chat") or ""
    chu_so_huu = du_lieu.get("chu_so_huu") or "khach"

    if not noi_dung and not danh_sach_anh and not danh_sach_file:
        return {
            "thanh_cong": False,
            "loi": "Không có nội dung để xử lý.",
        }

    _ghi_log("dai-nao", f"Nhận yêu cầu: {noi_dung[:100]}")

    # Chuyển cho điều phối
    try:
        from dai_nao.dieu_phoi import dieu_phoi
        ket_qua = dieu_phoi({
            "noi_dung": noi_dung,
            "anh": danh_sach_anh,
            "file": danh_sach_file,
            "lich_su": du_lieu.get("lich_su") or [],
            "id_chat": id_chat,
            "id_du_an": du_lieu.get("id_du_an") or "",
            "chu_so_huu": chu_so_huu,
            "thoi_gian": int(time.time()),
        })
        return ket_qua
    except Exception as e:
        _ghi_log("loi", f"Đại não xử lý lỗi: {e}")
        return {
            "thanh_cong": False,
            "loi": f"Đại não xử lý lỗi: {e}",
        }


# ================================================================
# HÀM TƯƠNG THÍCH (tên cũ)
# ================================================================
def nhan_task(du_lieu):
    """
    Alias tương thích với code cũ.
    Gọi nhan_yeu_cau.
    """
    return nhan_yeu_cau(du_lieu)
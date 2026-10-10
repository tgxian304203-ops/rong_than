"""
nhan_yeu_cau.py - Nhận yêu cầu từ giao diện.

Sửa: log "Đại não thất bại" → "Luồng xử lý thất bại".
"""

import time


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _in_debug(noi_dung):
    try:
        print(f"[DEBUG-NHAN-YEU-CAU] {noi_dung}", flush=True)
    except Exception:
        pass


def nhan_yeu_cau(du_lieu):
    """
    Nhận yêu cầu từ giao diện và chuyển cho dieu_phoi.
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

        # Ghi log lỗi rõ nguồn
        if ket_qua and not ket_qua.get("thanh_cong"):
            nguon_loi = ket_qua.get("nguon_loi", "")
            loi = ket_qua.get("loi", "không rõ")

            if nguon_loi == "tieu_nao":
                _ghi_log("loi", f"Tiểu não thất bại: {loi}")
            elif nguon_loi == "boss_model":
                _ghi_log("loi", f"Boss model thất bại: {loi}")
            elif nguon_loi == "sandbox":
                _ghi_log("loi", f"Sandbox thất bại: {loi}")
            elif nguon_loi == "tra_web":
                _ghi_log("loi", f"Tra web thất bại: {loi}")
            else:
                _ghi_log("loi", f"Luồng xử lý thất bại: {loi}")

        return ket_qua
    except Exception as e:
        _ghi_log("loi", f"Đại não xử lý lỗi: {e}")
        return {
            "thanh_cong": False,
            "loi": f"Đại não xử lý lỗi: {e}",
            "nguon_loi": "dai_nao",
        }


def nhan_task(du_lieu):
    """Alias tương thích."""
    return nhan_yeu_cau(du_lieu)
"""
nhan_lenh.py - Nhận lệnh từ Cây linh hồn.

CÓ DEBUG để kiểm tra luồng.
"""

import time


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _in_debug(noi_dung):
    """In ra console Render."""
    try:
        print(f"[DEBUG-NHAN-LENH] {noi_dung}", flush=True)
    except Exception:
        pass


def nhan_lenh(du_lieu):
    """
    Nhận lệnh từ Đại não / Cây linh hồn.
    """
    _in_debug("=== TIỂU NÃO NHẬN LỆNH ===")

    if not du_lieu or not isinstance(du_lieu, dict):
        _in_debug("du_lieu không hợp lệ")
        return {
            "thanh_cong": False,
            "loi": "Dữ liệu đầu vào không hợp lệ.",
        }

    _in_debug(f"du_lieu keys: {list(du_lieu.keys())}")
    _in_debug(f"noi_dung = {du_lieu.get('noi_dung', '')[:80]}")
    _in_debug(f"chu_so_huu = '{du_lieu.get('chu_so_huu')}'")
    _in_debug(f"id_chat = '{du_lieu.get('id_chat')}'")
    _in_debug(f"id_du_an = '{du_lieu.get('id_du_an')}'")
    _in_debug(f"loai_task = '{du_lieu.get('loai_task')}'")

    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    if not noi_dung:
        _in_debug("noi_dung RỖNG")
        return {
            "thanh_cong": False,
            "loi": "Không có nội dung để xử lý.",
        }

    chu_so_huu = du_lieu.get("chu_so_huu") or "khach"
    id_chat = du_lieu.get("id_chat") or ""
    loai_task = du_lieu.get("loai_task") or "tra_loi"

    _in_debug(f"→ Gọi ep_model với chu_so_huu='{chu_so_huu}', loai_task='{loai_task}'")

    _ghi_log("tieu-nao", f"Nhận lệnh: {loai_task} | {noi_dung[:80]}")

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

        _in_debug(f"← ep_model trả về: thanh_cong={ket_qua.get('thanh_cong')}")
        _in_debug(f"← ep_model trả về: loi={ket_qua.get('loi', '')}")

        return ket_qua
    except Exception as e:
        _in_debug(f"❌ ep_model exception: {e}")
        _ghi_log("loi", f"Tiểu não xử lý lỗi: {e}")
        return {
            "thanh_cong": False,
            "loi": f"Tiểu não xử lý lỗi: {e}",
        }


def nhan_lenh_sinh_code(du_lieu):
    du_lieu_moi = dict(du_lieu)
    du_lieu_moi["loai_task"] = "sinh_code"
    return nhan_lenh(du_lieu_moi)


def nhan_lenh_sua_code(du_lieu):
    du_lieu_moi = dict(du_lieu)
    du_lieu_moi["loai_task"] = "sua_code"
    return nhan_lenh(du_lieu_moi)


def nhan_lenh_tra_loi(du_lieu):
    du_lieu_moi = dict(du_lieu)
    du_lieu_moi["loai_task"] = "tra_loi"
    return nhan_lenh(du_lieu_moi)
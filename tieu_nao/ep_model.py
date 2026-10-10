"""
ep_model.py - ÉP Model làm việc.

Nhiệm vụ:
    - Nhận lệnh đã chuẩn hóa từ nhan_lenh.
    - ÉP Model làm đúng hợp đồng (dùng model/do_model + goi_model).
    - Phân loại task: sinh_code / tra_loi / sua_code.
    - Trả kết quả về.

Nguyên tắc:
    - Tiểu não ÉP Model, không tự suy luận.
    - Model là công cụ thuần — không giữ ngữ cảnh.
    - Nếu Model lỗi → xoay key Model.
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
# LOẠI TASK
# ================================================================
TASK_SINH_CODE = "sinh_code"
TASK_SUA_CODE = "sua_code"
TASK_TRA_LOI = "tra_loi"


# ================================================================
# ÉP MODEL (CHÍNH)
# ================================================================
def ep_model(du_lieu):
    """
    ÉP Model làm việc theo loại task.

    du_lieu: {
        noi_dung, chu_so_huu, id_chat, id_du_an,
        lich_su, buoc, loai_task, thoi_gian
    }

    Trả về: {
        thanh_cong, tra_loi, code?, ngon_ngu?,
        ket_qua_chay?, loi?
    }
    """
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    loai_task = du_lieu.get("loai_task", TASK_TRA_LOI)

    # Điều phối theo loại task
    if loai_task == TASK_SINH_CODE:
        return _ep_sinh_code(du_lieu)
    if loai_task == TASK_SUA_CODE:
        return _ep_sua_code(du_lieu)
    return _ep_tra_loi(du_lieu)


# ================================================================
# ÉP MODEL — SINH CODE
# ================================================================
def _ep_sinh_code(du_lieu):
    """ÉP Model sinh code mới."""
    try:
        from tieu_nao.sinh_code import sinh_code
        ket_qua = sinh_code(du_lieu)
    except Exception as e:
        _ghi_log("loi", f"sinh_code lỗi: {e}")
        return {"thanh_cong": False, "loi": f"sinh_code lỗi: {e}"}

    # Kiểm tra cứng (syntax, format)
    if ket_qua.get("thanh_cong") and ket_qua.get("code"):
        try:
            from tieu_nao.kiem_tra_cung import kiem_tra_cung
            kiem_tra = kiem_tra_cung(
                ket_qua["code"],
                ket_qua.get("ngon_ngu", "python"),
            )
            if not kiem_tra.get("thanh_cong"):
                ket_qua["canh_bao_cung"] = kiem_tra.get("loi", "")
        except Exception:
            pass

    return ket_qua


# ================================================================
# ÉP MODEL — SỬA CODE
# ================================================================
def _ep_sua_code(du_lieu):
    """ÉP Model sửa code lỗi."""
    try:
        from tieu_nao.sua_code import sua_code
        return sua_code(du_lieu)
    except Exception as e:
        _ghi_log("loi", f"sua_code lỗi: {e}")
        return {"thanh_cong": False, "loi": f"sua_code lỗi: {e}"}


# ================================================================
# ÉP MODEL — TRẢ LỜI
# ================================================================
def _ep_tra_loi(du_lieu):
    """ÉP Model trả lời câu hỏi (không sinh code)."""
    try:
        from tieu_nao.model.goi_model import goi_model
        ket_qua = goi_model(du_lieu)
    except Exception as e:
        _ghi_log("loi", f"goi_model lỗi: {e}")
        return {"thanh_cong": False, "loi": f"goi_model lỗi: {e}"}

    return ket_qua


# ================================================================
# ÉP MODEL VỚI HỢP ĐỒNG (dùng cho Boss Thế)
# ================================================================
def ep_model_theo_hop_dong(du_lieu, hop_dong):
    """
    ÉP Model làm việc theo hợp đồng cụ thể.

    hop_dong: {
        dang_lam_gi, dang_lam_toi_dau, tiep_theo_lam_gi
    }

    Trả về: dict kết quả.
    """
    if not hop_dong:
        return ep_model(du_lieu)

    # Tạo prompt theo hợp đồng
    prompt = _tao_prompt_theo_hop_dong(du_lieu.get("noi_dung", ""), hop_dong)

    du_lieu_moi = dict(du_lieu)
    du_lieu_moi["noi_dung"] = prompt

    return ep_model(du_lieu_moi)


def _tao_prompt_theo_hop_dong(noi_dung, hop_dong):
    """Tạo prompt cho Model theo hợp đồng."""
    phan = []
    if hop_dong.get("dang_lam_gi"):
        phan.append(f"Đang làm: {hop_dong['dang_lam_gi']}")
    if hop_dong.get("dang_lam_toi_dau"):
        phan.append(f"Tới đâu: {hop_dong['dang_lam_toi_dau']}")
    if hop_dong.get("tiep_theo_lam_gi"):
        phan.append(f"Tiếp theo: {hop_dong['tiep_theo_lam_gi']}")

    return f"""Hợp đồng:
{chr(10).join(phan)}

Yêu cầu: {noi_dung}"""


# ================================================================
# ÉP MODEL VỚI HƯỚNG DẪN
# ================================================================
def ep_model_theo_huong_dan(du_lieu, huong_dan):
    """
    ÉP Model làm việc theo hướng dẫn cụ thể.

    huong_dan: {
        nen_lam_gi, blacklist
    }

    Trả về: dict kết quả.
    """
    if not huong_dan:
        return ep_model(du_lieu)

    prompt = _tao_prompt_theo_huong_dan(du_lieu.get("noi_dung", ""), huong_dan)

    du_lieu_moi = dict(du_lieu)
    du_lieu_moi["noi_dung"] = prompt

    return ep_model(du_lieu_moi)


def _tao_prompt_theo_huong_dan(noi_dung, huong_dan):
    """Tạo prompt cho Model theo hướng dẫn."""
    phan = []

    if huong_dan.get("nen_lam_gi"):
        phan.append(f"NÊN LÀM: {huong_dan['nen_lam_gi']}")

    blacklist = huong_dan.get("blacklist", [])
    if blacklist:
        muc = [str(x) for x in blacklist[:5]]
        phan.append(f"TRÁNH: {', '.join(muc)}")

    if not phan:
        return noi_dung

    return f"""Hướng dẫn:
{chr(10).join(phan)}

Yêu cầu: {noi_dung}"""
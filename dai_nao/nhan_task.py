"""
nhan_task.py - Cửa ngõ của Đại não Rồng Thần.

Nhiệm vụ:
    - nhan_task(du_lieu): nhận task từ giao diện.
    - Kiểm tra dữ liệu đầu vào cơ bản.
    - Chuyển cho xu_ly_task.py điều phối chính.
    - Nhận kết quả, chuẩn hóa, trả về.

Quy tắc:
    - Đây là CỬA NGÕ — không chứa logic nghiệp vụ.
    - Mọi xử lý thật nằm ở xu_ly_task.py.
    - Ghi log khi nhận task và khi trả kết quả.
    - Xử lý lỗi rõ ràng — không sập khi xu_ly_task.py lỗi.

Tầng dữ liệu: dai_nao/ghi_nho.py
Điều phối: dai_nao/xu_ly_task.py
"""

import time


# ----------------------------------------------------------------
# GHI LOG
# ----------------------------------------------------------------
def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ----------------------------------------------------------------
# KIỂM TRA DỮ LIỆU ĐẦU VÀO
# ----------------------------------------------------------------
def _kiem_tra_du_lieu(du_lieu):
    """
    Kiểm tra du_lieu có hợp lệ không.
    Trả về (True, None) nếu OK, hoặc (False, "lỗi") nếu sai.
    """
    if not du_lieu or not isinstance(du_lieu, dict):
        return False, "Dữ liệu task không hợp lệ."

    noi_dung = du_lieu.get("noi_dung", "")
    danh_sach_anh = du_lieu.get("anh", [])
    danh_sach_file = du_lieu.get("file", [])

    # Kiểm tra kiểu dữ liệu
    if not isinstance(noi_dung, str):
        return False, "Nội dung task phải là chuỗi."
    if not isinstance(danh_sach_anh, list):
        return False, "Danh sách ảnh phải là mảng."
    if not isinstance(danh_sach_file, list):
        return False, "Danh sách file phải là mảng."

    # Phải có ít nhất 1 trong 3: chữ, ảnh, file
    if not noi_dung.strip() and not danh_sach_anh and not danh_sach_file:
        return False, "Task rỗng — cần ít nhất nội dung, ảnh hoặc file."

    return True, None


# ----------------------------------------------------------------
# CHUẨN HÓA KẾT QUẢ TRẢ VỀ
# ----------------------------------------------------------------
def _chuan_hoa_ket_qua(ket_qua):
    """
    Chuẩn hóa kết quả từ xu_ly_task.py về dạng thống nhất.
    Đảm bảo luôn có: thanh_cong, tra_loi, và tùy chọn code/ngon_ngu.
    """
    if not ket_qua or not isinstance(ket_qua, dict):
        return {
            "thanh_cong": False,
            "loi": "Đại não không trả về kết quả hợp lệ.",
        }

    ket_qua_chuan = {
        "thanh_cong": bool(ket_qua.get("thanh_cong", False)),
        "tra_loi": ket_qua.get("tra_loi") or "",
    }

    # Code + ngôn ngữ (nếu có)
    if ket_qua.get("code"):
        ket_qua_chuan["code"] = ket_qua["code"]
        ket_qua_chuan["ngon_ngu"] = ket_qua.get("ngon_ngu", "python")

    # Lỗi (nếu có)
    if ket_qua.get("loi"):
        ket_qua_chuan["loi"] = ket_qua["loi"]

    # Các trường mở rộng (nếu có)
    for truong in ("id_node", "score", "nguon", "do_tin_cay"):
        if truong in ket_qua:
            ket_qua_chuan[truong] = ket_qua[truong]

    return ket_qua_chuan


# ----------------------------------------------------------------
# HÀM CHÍNH: NHẬN TASK
# ----------------------------------------------------------------
def nhan_task(du_lieu):
    """
    Nhận task từ giao diện, chuyển cho xu_ly_task.py, trả kết quả.

    du_lieu: {
        noi_dung: str,
        anh: [str],
        file: [str],
        lich_su: [dict],
        id_chat: str?,
        id_du_an: str?,
        chu_so_huu: str,  # tên đăng nhập hoặc "khach"
    }

    Trả về: {
        thanh_cong: bool,
        tra_loi: str,
        code: str?,
        ngon_ngu: str?,
        loi: str?,
        ...
    }
    """
    thoi_gian_bat_dau = time.time()

    # ------------------------------------------------------------
    # 1. Kiểm tra dữ liệu đầu vào
    # ------------------------------------------------------------
    hop_le, loi = _kiem_tra_du_lieu(du_lieu)
    if not hop_le:
        _ghi_log("loi", f"Task không hợp lệ: {loi}")
        return {
            "thanh_cong": False,
            "loi": loi,
        }

    noi_dung = du_lieu.get("noi_dung", "").strip()
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")

    # Ghi log nhận task (rút gọn nội dung để log không quá dài)
    noi_dung_rut_gon = noi_dung[:100] + ("..." if len(noi_dung) > 100 else "")
    _ghi_log(
        "dai-nao",
        f"Nhận task từ {chu_so_huu}: {noi_dung_rut_gon or '(chỉ có ảnh/file)'}",
    )

    # ------------------------------------------------------------
    # 2. Chuyển cho xu_ly_task.py điều phối
    # ------------------------------------------------------------
    try:
        from dai_nao.xu_ly_task import xu_ly_task
    except ImportError:
        _ghi_log("loi", "xu_ly_task.py chưa có hoặc import lỗi.")
        return {
            "thanh_cong": False,
            "loi": "Đại não chưa sẵn sàng (dai_nao/xu_ly_task.py chưa có).",
        }

    try:
        ket_qua_tho = xu_ly_task(du_lieu)
    except Exception as e:
        _ghi_log("loi", f"xu_ly_task lỗi: {e}")
        return {
            "thanh_cong": False,
            "loi": f"Đại não xử lý lỗi: {e}",
        }

    # ------------------------------------------------------------
    # 3. Chuẩn hóa kết quả
    # ------------------------------------------------------------
    ket_qua = _chuan_hoa_ket_qua(ket_qua_tho)

    # ------------------------------------------------------------
    # 4. Ghi log kết quả
    # ------------------------------------------------------------
    thoi_gian_xu_ly = round(time.time() - thoi_gian_bat_dau, 3)
    if ket_qua.get("thanh_cong"):
        _ghi_log(
            "dai-nao",
            f"Trả lời {chu_so_huu} trong {thoi_gian_xu_ly}s",
        )
    else:
        _ghi_log(
            "loi",
            f"Xử lý thất bại cho {chu_so_huu} sau {thoi_gian_xu_ly}s: "
            f"{ket_qua.get('loi', 'không rõ')}",
        )

    ket_qua["thoi_gian_xu_ly"] = thoi_gian_xu_ly
    return ket_qua
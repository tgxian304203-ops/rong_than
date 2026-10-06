"""
doi_mat_khau.py - Xử lý đổi mật khẩu Rồng Thần.

Nhiệm vụ:
    - doi_mat_khau(du_lieu): kiểm tra mật khẩu cũ, cập nhật mật khẩu mới.

Quy tắc:
    - Yêu cầu đã đăng nhập (đọc ten_dang_nhap từ Flask session).
    - Kiểm tra mật khẩu cũ khớp với mật khẩu đã băm trong kho 1.
    - Băm mật khẩu mới bằng hashlib.sha256 + salt (dùng lại hàm từ xac_thuc.py).
    - Cập nhật vào kho 1 (collection tai_khoan).
    - Sau khi đổi thành công, có thể xóa các phiên khác (tùy chọn).

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

from flask import session as phien_flask

# ----------------------------------------------------------------
# IMPORT TẦNG DỮ LIỆU
# ----------------------------------------------------------------
from dai_nao.ghi_nho import (
    lay_tai_khoan,
    cap_nhat_mat_khau,
)

# ----------------------------------------------------------------
# IMPORT HÀM BĂM MẬT KHẨU TỪ xac_thuc.py
# ----------------------------------------------------------------
from giao_dien.xac_thuc import (
    _bam_mat_khau,
    _kiem_tra_mat_khau,
)


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
# TIỆN ÍCH
# ----------------------------------------------------------------
def _lay_ten_dang_nhap():
    """Lấy tên đăng nhập hiện tại từ Flask session."""
    return phien_flask.get("ten_dang_nhap")


# ----------------------------------------------------------------
# ĐỔI MẬT KHẨU
# ----------------------------------------------------------------
def doi_mat_khau(du_lieu):
    """
    Đổi mật khẩu cho tài khoản đang đăng nhập.
    du_lieu: { mat_khau_cu, mat_khau_moi }
    Trả về: { thanh_cong, loi? }
    """
    # Kiểm tra đăng nhập
    ten = _lay_ten_dang_nhap()
    if not ten:
        return {"thanh_cong": False, "loi": "Chưa đăng nhập."}

    mat_khau_cu = du_lieu.get("mat_khau_cu") or ""
    mat_khau_moi = du_lieu.get("mat_khau_moi") or ""

    # Kiểm tra dữ liệu đầu vào
    if not mat_khau_cu:
        return {"thanh_cong": False, "loi": "Thiếu mật khẩu cũ."}
    if not mat_khau_moi:
        return {"thanh_cong": False, "loi": "Thiếu mật khẩu mới."}
    if len(mat_khau_moi) < 3:
        return {"thanh_cong": False, "loi": "Mật khẩu mới phải có ít nhất 3 ký tự."}
    if mat_khau_cu == mat_khau_moi:
        return {"thanh_cong": False, "loi": "Mật khẩu mới phải khác mật khẩu cũ."}

    # Lấy tài khoản từ kho 1
    tk = lay_tai_khoan(ten)
    if not tk:
        return {"thanh_cong": False, "loi": "Không tìm thấy tài khoản."}

    # Kiểm tra mật khẩu cũ
    chuoi_bam_cu = tk.get("mat_khau_bam", "")
    if not _kiem_tra_mat_khau(mat_khau_cu, chuoi_bam_cu):
        return {"thanh_cong": False, "loi": "Mật khẩu cũ không đúng."}

    # Băm mật khẩu mới + cập nhật
    chuoi_bam_moi = _bam_mat_khau(mat_khau_moi)
    if not cap_nhat_mat_khau(ten, chuoi_bam_moi):
        return {"thanh_cong": False, "loi": "Không cập nhật được mật khẩu."}

    _ghi_log("dai-nao", f"Đổi mật khẩu thành công: {ten}")

    return {"thanh_cong": True}
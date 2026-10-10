"""
doi_mat_khau.py - Xử lý đổi mật khẩu.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho.
"""

from flask import session as phien_flask

from luu_tru.ghi_nho import (
    lay_tai_khoan,
    cap_nhat_mat_khau,
)

from giao_dien.xac_thuc import (
    _bam_mat_khau,
    _kiem_tra_mat_khau,
)


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _lay_ten_dang_nhap():
    return phien_flask.get("ten_dang_nhap")


def doi_mat_khau(du_lieu):
    ten = _lay_ten_dang_nhap()
    if not ten:
        return {"thanh_cong": False, "loi": "Chưa đăng nhập."}

    mat_khau_cu = du_lieu.get("mat_khau_cu") or ""
    mat_khau_moi = du_lieu.get("mat_khau_moi") or ""

    if not mat_khau_cu:
        return {"thanh_cong": False, "loi": "Thiếu mật khẩu cũ."}
    if not mat_khau_moi:
        return {"thanh_cong": False, "loi": "Thiếu mật khẩu mới."}
    if len(mat_khau_moi) < 3:
        return {"thanh_cong": False, "loi": "Mật khẩu mới phải có ít nhất 3 ký tự."}
    if mat_khau_cu == mat_khau_moi:
        return {"thanh_cong": False, "loi": "Mật khẩu mới phải khác mật khẩu cũ."}

    tk = lay_tai_khoan(ten)
    if not tk:
        return {"thanh_cong": False, "loi": "Không tìm thấy tài khoản."}

    chuoi_bam_cu = tk.get("mat_khau_bam", "")
    if not _kiem_tra_mat_khau(mat_khau_cu, chuoi_bam_cu):
        return {"thanh_cong": False, "loi": "Mật khẩu cũ không đúng."}

    chuoi_bam_moi = _bam_mat_khau(mat_khau_moi)
    if not cap_nhat_mat_khau(ten, chuoi_bam_moi):
        return {"thanh_cong": False, "loi": "Không cập nhật được mật khẩu."}

    _ghi_log("dai-nao", f"Đổi mật khẩu thành công: {ten}")

    return {"thanh_cong": True}
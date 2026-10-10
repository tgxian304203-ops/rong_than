"""
xac_thuc.py - Xác thực đăng ký / đăng nhập Rồng Thần.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho.
"""

import hashlib
import secrets
import time

from luu_tru.ghi_nho import (
    dem_tai_khoan,
    lay_tai_khoan,
    luu_tai_khoan,
    lay_tai_khoan_cu_nhat,
    xoa_tai_khoan_va_du_lieu,
)


MAX_TAI_KHOAN = 50


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _bam_mat_khau(mat_khau, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    bam = hashlib.sha256((salt + mat_khau).encode("utf-8")).hexdigest()
    return salt + "$" + bam


def _kiem_tra_mat_khau(mat_khau, chuoi_da_bam):
    if not chuoi_da_bam or "$" not in chuoi_da_bam:
        return False
    try:
        salt, _ = chuoi_da_bam.split("$", 1)
    except ValueError:
        return False
    return _bam_mat_khau(mat_khau, salt) == chuoi_da_bam


def dang_ky(du_lieu):
    ten = (du_lieu.get("ten_dang_nhap") or "").strip()
    mat_khau = du_lieu.get("mat_khau") or ""

    if not ten:
        return {"thanh_cong": False, "loi": "Thiếu tên đăng nhập."}
    if len(ten) < 3:
        return {"thanh_cong": False, "loi": "Tên đăng nhập phải có ít nhất 3 ký tự."}
    if not mat_khau:
        return {"thanh_cong": False, "loi": "Thiếu mật khẩu."}

    if lay_tai_khoan(ten) is not None:
        return {"thanh_cong": False, "loi": "Tên đăng nhập đã tồn tại."}

    so_luong = dem_tai_khoan()
    if so_luong >= MAX_TAI_KHOAN:
        cu_nhat = lay_tai_khoan_cu_nhat()
        if cu_nhat:
            xoa_tai_khoan_va_du_lieu(cu_nhat.get("ten_dang_nhap"))
            _ghi_log(
                "dai-nao",
                f"Vượt giới hạn {MAX_TAI_KHOAN} tài khoản. "
                f"Đã xóa: {cu_nhat.get('ten_dang_nhap')}",
            )

    tai_khoan_moi = {
        "ten_dang_nhap": ten,
        "mat_khau_bam": _bam_mat_khau(mat_khau),
        "ngay_tao": int(time.time()),
        "lan_dang_nhap_cuoi": 0,
    }

    if not luu_tai_khoan(tai_khoan_moi):
        return {"thanh_cong": False, "loi": "Không lưu được tài khoản."}

    _ghi_log("dai-nao", f"Đăng ký tài khoản mới: {ten}")
    return {"thanh_cong": True, "ten_dang_nhap": ten}


def dang_nhap(du_lieu):
    ten = (du_lieu.get("ten_dang_nhap") or "").strip()
    mat_khau = du_lieu.get("mat_khau") or ""

    if not ten or not mat_khau:
        return {"thanh_cong": False, "loi": "Thiếu tên đăng nhập hoặc mật khẩu."}

    tk = lay_tai_khoan(ten)
    if tk is None:
        return {"thanh_cong": False, "loi": "Tên đăng nhập hoặc mật khẩu không đúng."}

    if not _kiem_tra_mat_khau(mat_khau, tk.get("mat_khau_bam", "")):
        return {"thanh_cong": False, "loi": "Tên đăng nhập hoặc mật khẩu không đúng."}

    _ghi_log("dai-nao", f"Đăng nhập thành công: {ten}")
    return {"thanh_cong": True, "ten_dang_nhap": ten}
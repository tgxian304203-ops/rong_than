"""
xac_thuc.py - Xác thực đăng ký / đăng nhập Rồng Thần.

Nhiệm vụ:
    - dang_ky(du_lieu): tạo tài khoản mới.
    - dang_nhap(du_lieu): kiểm tra tài khoản, trả kết quả.

Quy tắc:
    - Mật khẩu băm bằng hashlib.sha256 + salt (không lưu mật khẩu gốc).
    - Lưu tài khoản vào kho 1 (collection tai_khoan).
    - Giới hạn tối đa 50 tài khoản (MAX_TAI_KHOAN).
    - Khi vượt 50: xóa tài khoản cũ nhất + mọi dữ liệu liên quan trong kho 1.
    - Kho 2 KHÔNG bị ảnh hưởng.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import hashlib
import secrets
import time

# ----------------------------------------------------------------
# IMPORT TẦNG DỮ LIỆU
# ----------------------------------------------------------------
from dai_nao.ghi_nho import (
    dem_tai_khoan,
    lay_tai_khoan,
    luu_tai_khoan,
    lay_tai_khoan_cu_nhat,
    xoa_tai_khoan_va_du_lieu,
)


# ----------------------------------------------------------------
# HẰNG SỐ
# ----------------------------------------------------------------
MAX_TAI_KHOAN = 50


# ----------------------------------------------------------------
# GHI LOG
# ----------------------------------------------------------------
def _ghi_log(loai, noi_dung):
    """Ghi log vào kho 1. Bọc try/except để không sập luồng chính."""
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ----------------------------------------------------------------
# BĂM MẬT KHẨU
# ----------------------------------------------------------------
def _bam_mat_khau(mat_khau, salt=None):
    """
    Băm mật khẩu bằng sha256 + salt.
    Trả về chuỗi 'salt$hash'.
    Nếu salt=None, tự sinh salt mới.
    """
    if salt is None:
        salt = secrets.token_hex(16)
    bam = hashlib.sha256((salt + mat_khau).encode("utf-8")).hexdigest()
    return salt + "$" + bam


def _kiem_tra_mat_khau(mat_khau, chuoi_da_bam):
    """Kiểm tra mật khẩu khớp với chuỗi đã băm."""
    if not chuoi_da_bam or "$" not in chuoi_da_bam:
        return False
    try:
        salt, _ = chuoi_da_bam.split("$", 1)
    except ValueError:
        return False
    return _bam_mat_khau(mat_khau, salt) == chuoi_da_bam


# ----------------------------------------------------------------
# ĐĂNG KÝ
# ----------------------------------------------------------------
def dang_ky(du_lieu):
    """
    Tạo tài khoản mới.
    du_lieu: { ten_dang_nhap, mat_khau }
    Trả về: { thanh_cong, ten_dang_nhap, loi? }
    """
    ten = (du_lieu.get("ten_dang_nhap") or "").strip()
    mat_khau = du_lieu.get("mat_khau") or ""

    # Kiểm tra dữ liệu đầu vào
    if not ten:
        return {"thanh_cong": False, "loi": "Thiếu tên đăng nhập."}
    if len(ten) < 3:
        return {"thanh_cong": False, "loi": "Tên đăng nhập phải có ít nhất 3 ký tự."}
    if not mat_khau:
        return {"thanh_cong": False, "loi": "Thiếu mật khẩu."}

    # Kiểm tra trùng tên đăng nhập
    if lay_tai_khoan(ten) is not None:
        return {"thanh_cong": False, "loi": "Tên đăng nhập đã tồn tại."}

    # Kiểm tra giới hạn 50 tài khoản
    so_luong = dem_tai_khoan()
    if so_luong >= MAX_TAI_KHOAN:
        # Xóa tài khoản cũ nhất + mọi dữ liệu liên quan trong kho 1
        cu_nhat = lay_tai_khoan_cu_nhat()
        if cu_nhat:
            xoa_tai_khoan_va_du_lieu(cu_nhat.get("ten_dang_nhap"))
            _ghi_log(
                "dai-nao",
                f"Vượt giới hạn {MAX_TAI_KHOAN} tài khoản. "
                f"Đã xóa tài khoản cũ nhất: {cu_nhat.get('ten_dang_nhap')}",
            )

    # Tạo tài khoản mới
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


# ----------------------------------------------------------------
# ĐĂNG NHẬP
# ----------------------------------------------------------------
def dang_nhap(du_lieu):
    """
    Kiểm tra đăng nhập.
    du_lieu: { ten_dang_nhap, mat_khau }
    Trả về: { thanh_cong, ten_dang_nhap, loi? }
    """
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
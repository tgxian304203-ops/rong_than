"""
luu_uri_kho.py - Lưu URI 2 kho MongoDB Rồng Thần.

Nhiệm vụ:
    - luu_uri_kho(du_lieu): nhận { kho: 1|2, uri }, kiểm tra kết nối, lưu vào kho 1.
    - lay_uri_kho(): trả URI đã lưu (che mật khẩu).

Quy tắc:
    - Mỗi tài khoản có URI 2 kho riêng.
    - URI kho 1 và kho 2 là cấu hình của tài khoản.
    - Trước khi lưu, THỬ KẾT NỐI để xác nhận URI đúng.
    - Lưu vào collection cau_hinh_kho trong kho 1.
    - Khi trả về client, che mật khẩu bằng ***.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import re
import time

from flask import session as phien_flask

# ----------------------------------------------------------------
# IMPORT TẦNG DỮ LIỆU
# ----------------------------------------------------------------
from dai_nao.ghi_nho import (
    luu_uri_kho_cua,
    lay_uri_kho_cua,
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


def _kiem_tra_dinh_dang_uri(uri):
    """
    Kiểm tra URI có đúng định dạng MongoDB không.
    Trả về True nếu hợp lệ.
    """
    if not uri or not isinstance(uri, str):
        return False
    return uri.startswith("mongodb://") or uri.startswith("mongodb+srv://")


def _thu_ket_noi(uri):
    """
    Thử kết nối tới URI bằng pymongo.
    Trả về True nếu kết nối OK, False nếu lỗi.
    Timeout ngắn để không treo server.
    """
    try:
        from pymongo import MongoClient
        from pymongo.errors import (
            ServerSelectionTimeoutError,
            ConfigurationError,
            OperationFailure,
        )
    except ImportError:
        # Chưa cài pymongo — coi như không kiểm tra được, cho phép lưu.
        return True

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Ping để xác nhận kết nối
        client.admin.command("ping")
        client.close()
        return True
    except (ServerSelectionTimeoutError, ConfigurationError, OperationFailure):
        return False
    except Exception:
        return False


def _che_mat_khau(uri):
    """
    Che mật khẩu trong URI MongoDB.
    Ví dụ:
        mongodb+srv://user:pass@cluster.mongodb.net/db
        → mongodb+srv://user:***@cluster.mongodb.net/db
    """
    if not uri:
        return ""
    # Định dạng: scheme://user:password@host
    mau = r"^(mongodb(?:\+srv)?://[^:]+:)([^@]+)(@.+)$"
    khop = re.match(mau, uri)
    if khop:
        return khop.group(1) + "***" + khop.group(3)
    return uri


# ----------------------------------------------------------------
# LƯU URI KHO
# ----------------------------------------------------------------
def luu_uri_kho(du_lieu):
    """
    Lưu URI kho MongoDB.
    du_lieu: { kho: 1|2, uri: "mongodb+srv://..." }
    Trả về: { thanh_cong, kho, uri_da_che?, loi? }
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {"thanh_cong": False, "loi": "Chưa đăng nhập."}

    so_kho = du_lieu.get("kho")
    uri = (du_lieu.get("uri") or "").strip()

    # Kiểm tra số kho
    if so_kho not in (1, 2):
        return {"thanh_cong": False, "loi": "Số kho phải là 1 hoặc 2."}

    # Kiểm tra URI không rỗng
    if not uri:
        return {"thanh_cong": False, "loi": "Thiếu URI."}

    # Kiểm tra định dạng URI
    if not _kiem_tra_dinh_dang_uri(uri):
        return {
            "thanh_cong": False,
            "loi": "URI không đúng định dạng MongoDB. Phải bắt đầu bằng "
                   "'mongodb://' hoặc 'mongodb+srv://'.",
        }

    # Thử kết nối (chỉ thử với kho 1 vì kho 1 là kho lưu cấu hình)
    if so_kho == 1:
        if not _thu_ket_noi(uri):
            return {
                "thanh_cong": False,
                "loi": "Không kết nối được tới URI kho 1. "
                       "Kiểm tra lại URI, mật khẩu, IP whitelist.",
            }

    # Lưu vào kho 1
    if not luu_uri_kho_cua(ten_tk, so_kho, uri):
        return {"thanh_cong": False, "loi": "Không lưu được URI."}

    _ghi_log("dai-nao", f"Lưu URI kho {so_kho} cho tài khoản {ten_tk}")

    return {
        "thanh_cong": True,
        "kho": so_kho,
        "uri_da_che": _che_mat_khau(uri),
        "thoi_gian": int(time.time()),
    }


# ----------------------------------------------------------------
# LẤY URI KHO
# ----------------------------------------------------------------
def lay_uri_kho():
    """
    Trả URI 2 kho đã lưu của tài khoản hiện tại (đã che mật khẩu).
    """
    ten_tk = _lay_ten_dang_nhap()
    if not ten_tk:
        return {
            "thanh_cong": True,
            "kho_1": "",
            "kho_2": "",
        }

    uri_kho_1 = lay_uri_kho_cua(ten_tk, 1) or ""
    uri_kho_2 = lay_uri_kho_cua(ten_tk, 2) or ""

    return {
        "thanh_cong": True,
        "kho_1": _che_mat_khau(uri_kho_1),
        "kho_2": _che_mat_khau(uri_kho_2),
    }
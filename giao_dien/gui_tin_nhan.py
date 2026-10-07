"""
gui_tin_nhan.py - Xử lý nút gửi tin nhắn Rồng Thần.

Nhiệm vụ:
    - xu_ly_gui_tin_nhan(du_lieu): nhận tin nhắn từ client, chuyển
      cho Đại não xử lý, trả kết quả về client.

Quy tắc:
    - Đây là CẦU NỐI giữa giao diện và Đại não.
    - Đại não xử lý chính — file này KHÔNG chứa logic nghiệp vụ.
    - Lưu lịch sử chat vào kho 1 (collection lich_su_chat).
    - Nhận diện tài khoản đang đăng nhập hoặc chế độ khách.
    - Nếu Đại não lỗi, trả lỗi rõ ràng cho client.
    - Nhận cả trường "urls_anh"/"urls_file" (từ chat.js mới)
      và "anh"/"file" (tương thích ngược).

Tầng dữ liệu: dai_nao/ghi_nho.py
Đại não: dai_nao/nhan_task.py
"""

import time
import secrets

from flask import session as phien_flask

# ----------------------------------------------------------------
# IMPORT TẦNG DỮ LIỆU
# ----------------------------------------------------------------
from dai_nao.ghi_nho import (
    luu_tin_nhan_chat,
    lay_lich_su_chat,
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
    """Lấy tên đăng nhập hiện tại (None nếu là khách)."""
    return phien_flask.get("ten_dang_nhap")


def _tao_id():
    return "msg-" + secrets.token_hex(8)


def _lay_danh_sach(du_lieu, ten_moi, ten_cu):
    """Lấy danh sách từ trường mới (urls_anh) hoặc trường cũ (anh)."""
    ds = du_lieu.get(ten_moi)
    if ds is None:
        ds = du_lieu.get(ten_cu)
    if not isinstance(ds, list):
        return []
    return ds


# ----------------------------------------------------------------
# HÀM XỬ LÝ CHÍNH
# ----------------------------------------------------------------
def xu_ly_gui_tin_nhan(du_lieu):
    """
    Nhận tin nhắn từ client, chuyển cho Đại não, trả kết quả.

    du_lieu: {
        noi_dung: str,
        urls_anh: [str]?,       # từ chat.js mới
        urls_file: [str]?,      # từ chat.js mới
        anh: [str]?,            # tương thích ngược
        file: [str]?,           # tương thích ngược
        id_chat: str?,
        id_du_an: str?,
    }

    Trả về: {
        thanh_cong: bool,
        tra_loi: str,
        code: str?,
        ngon_ngu: str?,
        id_tin_nhan: str,
        loi: str?,
    }
    """
    # ------------------------------------------------------------
    # 1. Kiểm tra dữ liệu đầu vào
    # ------------------------------------------------------------
    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    danh_sach_anh = _lay_danh_sach(du_lieu, "urls_anh", "anh")
    danh_sach_file = _lay_danh_sach(du_lieu, "urls_file", "file")

    # Nếu không có chữ, không có ảnh, không có file → lỗi
    if not noi_dung and not danh_sach_anh and not danh_sach_file:
        return {
            "thanh_cong": False,
            "loi": "Không có nội dung để gửi.",
        }

    ten_tk = _lay_ten_dang_nhap()
    id_chat = du_lieu.get("id_chat") or ""
    id_du_an = du_lieu.get("id_du_an") or ""
    id_tin_nhan = _tao_id()
    thoi_gian = int(time.time())

    # ------------------------------------------------------------
    # 2. Lưu tin nhắn của người dùng vào kho 1
    # ------------------------------------------------------------
    tin_nhan_nguoi = {
        "id_tin_nhan": id_tin_nhan,
        "chu_so_huu": ten_tk or "khach",
        "id_chat": id_chat,
        "id_du_an": id_du_an,
        "vai_tro": "nguoi_dung",
        "noi_dung": noi_dung,
        "anh": danh_sach_anh,
        "file": danh_sach_file,
        "thoi_gian": thoi_gian,
    }

    if ten_tk:
        try:
            luu_tin_nhan_chat(tin_nhan_nguoi)
        except Exception as e:
            _ghi_log("dai-nao", f"Lỗi lưu tin nhắn người dùng: {e}")

    # ------------------------------------------------------------
    # 3. Lấy lịch sử chat gần đây
    # ------------------------------------------------------------
    lich_su = []
    if ten_tk and id_chat:
        try:
            lich_su = lay_lich_su_chat(ten_tk, id_chat, gioi_han=20) or []
        except Exception:
            lich_su = []

    # ------------------------------------------------------------
    # 4. Chuyển cho Đại não xử lý
    # ------------------------------------------------------------
    try:
        from dai_nao.nhan_task import nhan_task
    except ImportError:
        return {
            "thanh_cong": False,
            "loi": "Đại não chưa sẵn sàng (dai_nao/nhan_task.py chưa có).",
        }

    du_lieu_dai_nao = {
        "noi_dung": noi_dung,
        "anh": danh_sach_anh,
        "file": danh_sach_file,
        "lich_su": lich_su,
        "id_chat": id_chat,
        "id_du_an": id_du_an,
        "chu_so_huu": ten_tk or "khach",
    }

    try:
        ket_qua = nhan_task(du_lieu_dai_nao)
    except Exception as e:
        _ghi_log("loi", f"Đại não lỗi: {e}")
        return {
            "thanh_cong": False,
            "loi": f"Đại não xử lý lỗi: {e}",
        }

    if not ket_qua or not isinstance(ket_qua, dict):
        return {
            "thanh_cong": False,
            "loi": "Đại não không trả về kết quả hợp lệ.",
        }

    # ------------------------------------------------------------
    # 5. Chuẩn bị câu trả lời
    # ------------------------------------------------------------
    tra_loi = ket_qua.get("tra_loi") or ""
    code = ket_qua.get("code")
    ngon_ngu = ket_qua.get("ngon_ngu")

    # ------------------------------------------------------------
    # 6. Lưu tin nhắn trả lời của Rồng Thần
    # ------------------------------------------------------------
    tin_nhan_rong = {
        "id_tin_nhan": _tao_id(),
        "chu_so_huu": ten_tk or "khach",
        "id_chat": id_chat,
        "id_du_an": id_du_an,
        "vai_tro": "rong_than",
        "noi_dung": tra_loi,
        "code": code,
        "ngon_ngu": ngon_ngu,
        "thoi_gian": int(time.time()),
    }

    if ten_tk:
        try:
            luu_tin_nhan_chat(tin_nhan_rong)
        except Exception as e:
            _ghi_log("dai-nao", f"Lỗi lưu tin nhắn Rồng Thần: {e}")

    # ------------------------------------------------------------
    # 7. Trả kết quả về client
    # ------------------------------------------------------------
    return {
        "thanh_cong": True,
        "tra_loi": tra_loi,
        "code": code,
        "ngon_ngu": ngon_ngu,
        "id_tin_nhan": id_tin_nhan,
    }
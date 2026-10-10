"""
gui_tin_nhan.py - Xử lý nút gửi tin nhắn.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho
      dai_nao.nhan_task → dai_nao.nhan_yeu_cau.
"""

import time
import secrets

from flask import session as phien_flask

from luu_tru.ghi_nho import (
    luu_tin_nhan_chat,
    lay_lich_su_chat,
)


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _lay_ten_dang_nhap():
    return phien_flask.get("ten_dang_nhap")


def _tao_id():
    return "msg-" + secrets.token_hex(8)


def _lay_danh_sach(du_lieu, ten_moi, ten_cu):
    ds = du_lieu.get(ten_moi)
    if ds is None:
        ds = du_lieu.get(ten_cu)
    if not isinstance(ds, list):
        return []
    return ds


def xu_ly_gui_tin_nhan(du_lieu):
    """
    Nhận tin nhắn từ client, chuyển cho Đại não, trả kết quả.
    """
    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    danh_sach_anh = _lay_danh_sach(du_lieu, "urls_anh", "anh")
    danh_sach_file = _lay_danh_sach(du_lieu, "urls_file", "file")

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

    lich_su = []
    if ten_tk and id_chat:
        try:
            lich_su = lay_lich_su_chat(ten_tk, id_chat, gioi_han=20) or []
        except Exception:
            lich_su = []

    # Chuyển cho Đại não
    try:
        from dai_nao.nhan_yeu_cau import nhan_yeu_cau
    except ImportError:
        _ghi_log("loi", "nhan_yeu_cau.py chưa có.")
        return {
            "thanh_cong": False,
            "loi": "Đại não chưa sẵn sàng (dai_nao/nhan_yeu_cau.py chưa có).",
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
        ket_qua = nhan_yeu_cau(du_lieu_dai_nao)
    except Exception as e:
        _ghi_log("loi", f"Đại não lỗi: {e}")
        return {
            "thanh_cong": False,
            "loi": f"Đại não xử lý lỗi: {e}",
        }

    if not ket_qua or not isinstance(ket_qua, dict):
        _ghi_log("loi", "Đại não không trả về kết quả hợp lệ.")
        return {
            "thanh_cong": False,
            "loi": "Đại não không trả về kết quả hợp lệ.",
        }

    thanh_cong_dai_nao = bool(ket_qua.get("thanh_cong", False))
    tra_loi = ket_qua.get("tra_loi") or ""
    code = ket_qua.get("code")
    ngon_ngu = ket_qua.get("ngon_ngu")
    sandbox = ket_qua.get("sandbox")
    ket_qua_chay = ket_qua.get("ket_qua_chay")
    loi_dai_nao = ket_qua.get("loi") or ""

    if not thanh_cong_dai_nao:
        _ghi_log("loi", f"Đại não thất bại: {loi_dai_nao or 'không rõ'}")
        return {
            "thanh_cong": False,
            "loi": loi_dai_nao or "Đại não không xử lý được task này.",
            "id_tin_nhan": id_tin_nhan,
        }

    if not tra_loi and not code:
        _ghi_log("loi", "Đại não thành công nhưng không có nội dung trả lời.")
        return {
            "thanh_cong": False,
            "loi": "Đại não không tạo ra câu trả lời. Bạn thử lại giúp ta nhé.",
            "id_tin_nhan": id_tin_nhan,
        }

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

    ket_qua_tra = {
        "thanh_cong": True,
        "tra_loi": tra_loi,
        "id_tin_nhan": id_tin_nhan,
    }

    if code:
        ket_qua_tra["code"] = code
    if ngon_ngu:
        ket_qua_tra["ngon_ngu"] = ngon_ngu
    if sandbox:
        ket_qua_tra["sandbox"] = sandbox
    if ket_qua_chay:
        ket_qua_tra["ket_qua_chay"] = ket_qua_chay

    return ket_qua_tra
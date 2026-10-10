"""
het_quota_model.py - Xử lý khi Model hết quota.

Nhiệm vụ:
    - Đánh dấu key hết quota.
    - Xoay key khác.
    - Nếu hết tất cả → báo Đại não.

Nguyên tắc:
    - Model chỉ có 1 loại (không có "Model Thế" như Boss).
    - Hết quota → thử key khác của provider khác.
    - Hết hết → báo Đại não.
"""


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
# HẰNG SỐ
# ================================================================
LOAI_NAO_MODEL = "tieu_boss"


# ================================================================
# XỬ LÝ HẾT QUOTA
# ================================================================
def xu_ly_het_quota(chu_so_huu, provider="", key_id=""):
    """
    Xử lý khi Model hết quota.

    Trả về: {
        thanh_cong, hanh_dong, model_info?, loi?
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "hanh_dong": "",
        "model_info": None,
        "loi": "",
    }

    if not chu_so_huu:
        ket_qua["loi"] = "Thiếu chu_so_huu."
        return ket_qua

    # 1. Đánh dấu key hiện tại hết quota
    if provider and key_id:
        _danh_dau_het_quota(provider, key_id)

    # 2. Thử xoay key khác
    model_moi = _thu_xoay_key(chu_so_huu, key_id)

    if model_moi and model_moi.get("thanh_cong"):
        ket_qua["thanh_cong"] = True
        ket_qua["hanh_dong"] = "xoay_key"
        ket_qua["model_info"] = model_moi
        return ket_qua

    # 3. Hết tất cả
    _ghi_log("tieu-nao", "Hết tất cả Model.")
    ket_qua["hanh_dong"] = "het_tat_ca"
    ket_qua["loi"] = "Tất cả Model đều hết quota."
    return ket_qua


# ================================================================
# ĐÁNH DẤU HẾT QUOTA
# ================================================================
def _danh_dau_het_quota(provider, key_id):
    """Đánh dấu key hết quota vào kho 2."""
    try:
        from luu_tru.trang_thai_key import danh_dau_het_quota
        danh_dau_het_quota(LOAI_NAO_MODEL, provider, key_id)
        _ghi_log("tieu-nao", f"Đánh dấu {provider} hết quota.")
    except Exception as e:
        _ghi_log("loi", f"Đánh dấu hết quota lỗi: {e}")


# ================================================================
# THỬ XOAY KEY
# ================================================================
def _thu_xoay_key(chu_so_huu, key_hien_tai=""):
    """Thử xoay sang key khác."""
    try:
        from tieu_nao.model.xoay_key_model import xoay_key_model
        return xoay_key_model(chu_so_huu, key_hien_tai)
    except Exception as e:
        _ghi_log("loi", f"Xoay key Model lỗi: {e}")
        return None


# ================================================================
# KIỂM TRA HẾT TẤT CẢ
# ================================================================
def kiem_tra_het_tat_ca(chu_so_huu):
    """Kiểm tra tất cả Model đều hết quota không."""
    if not chu_so_huu:
        return True

    try:
        from tieu_nao.model.xoay_key_model import dem_key_con_dung
        return dem_key_con_dung(chu_so_huu) == 0
    except Exception:
        return True


# ================================================================
# THỜI GIAN HỒI GẦN NHẤT
# ================================================================
def thoi_gian_hoi_gan_nhat(chu_so_huu):
    """Tính thời gian chờ đến khi Model gần nhất hồi quota."""
    try:
        from luu_tru.trang_thai_key import thoi_gian_hoi_gan_nhat as _tg
        return _tg(LOAI_NAO_MODEL)
    except Exception:
        return 0


# ================================================================
# THÔNG BÁO
# ================================================================
def tao_thong_bao_het_quota(chu_so_huu):
    """Tạo thông báo khi hết Model."""
    tg = thoi_gian_hoi_gan_nhat(chu_so_huu)

    if tg <= 0:
        return "⚠️ Tất cả Model đều hết quota."

    if tg < 60:
        return f"⚠️ Hết Model. Thử lại sau {tg} giây."
    if tg < 3600:
        return f"⚠️ Hết Model. Thử lại sau {tg // 60} phút."
    if tg < 86400:
        return f"⚠️ Hết Model. Thử lại sau {tg // 3600} giờ."

    return f"⚠️ Hết Model. Thử lại sau {tg // 86400} ngày."


# ================================================================
# RESET
# ================================================================
def reset_tat_ca(chu_so_huu):
    """Reset trạng thái hết quota của tất cả key Model."""
    try:
        from luu_tru.trang_thai_key import reset_tat_ca as _reset
        _reset(LOAI_NAO_MODEL)
        _ghi_log("tieu-nao", f"Reset Model cho {chu_so_huu}")
        return True
    except Exception as e:
        _ghi_log("loi", f"Reset Model lỗi: {e}")
        return False
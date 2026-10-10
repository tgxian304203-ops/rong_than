"""
het_quota_boss.py - Xử lý khi Boss hết quota.

Nhiệm vụ:
    - Đánh dấu key Boss hết quota.
    - Tìm key Boss khác (xoay key).
    - Nếu hết tất cả → chuyển Boss Thế (tieu_boss).
    - Nếu hết cả 2 → báo Đại não.

Nguyên tắc:
    - Boss Đầu hết quota → thử Boss Thế.
    - Boss Thế hết quota → báo Đại não.
    - Không tự sập nếu không có key.
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
# HẰNG SỐ
# ================================================================
LOAI_BOSS_DAU = "boss"
LOAI_BOSS_THE = "tieu_boss"


# ================================================================
# XỬ LÝ HẾT QUOTA
# ================================================================
def xu_ly_het_quota(chu_so_huu, loai_nao="boss", provider="", key_id=""):
    """
    Xử lý khi Boss hết quota.

    Bước:
        1. Đánh dấu key hết quota.
        2. Thử xoay key khác (cùng loại Boss).
        3. Nếu hết → thử Boss Thế.
        4. Nếu hết cả 2 → báo Đại não.

    Trả về: {
        thanh_cong: bool,
        hanh_dong: "xoay_key" | "chuyen_boss_the" | "het_tat_ca",
        boss_info: dict?,
        loi: str?,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "hanh_dong": "",
        "boss_info": None,
        "loi": "",
    }

    if not chu_so_huu:
        ket_qua["loi"] = "Thiếu chu_so_huu."
        return ket_qua

    # 1. Đánh dấu key hiện tại hết quota
    if provider and key_id:
        _danh_dau_het_quota(loai_nao, provider, key_id)

    # 2. Thử xoay key khác (cùng loại Boss)
    boss_moi = _thu_xoay_key(chu_so_huu, loai_nao, key_id)

    if boss_moi and boss_moi.get("thanh_cong"):
        ket_qua["thanh_cong"] = True
        ket_qua["hanh_dong"] = "xoay_key"
        ket_qua["boss_info"] = boss_moi
        return ket_qua

    # 3. Nếu đang là Boss Đầu → thử Boss Thế
    if loai_nao == LOAI_BOSS_DAU:
        boss_the = _thu_xoay_key(chu_so_huu, LOAI_BOSS_THE, "")

        if boss_the and boss_the.get("thanh_cong"):
            _ghi_log("dai-nao", "Chuyển sang Boss Thế.")
            ket_qua["thanh_cong"] = True
            ket_qua["hanh_dong"] = "chuyen_boss_the"
            ket_qua["boss_info"] = boss_the
            return ket_qua

    # 4. Hết cả 2
    _ghi_log("dai-nao", f"Hết tất cả Boss ({loai_nao}).")
    ket_qua["hanh_dong"] = "het_tat_ca"
    ket_qua["loi"] = "Tất cả Boss đều hết quota."
    return ket_qua


# ================================================================
# ĐÁNH DẤU HẾT QUOTA
# ================================================================
def _danh_dau_het_quota(loai_nao, provider, key_id):
    """Đánh dấu key hết quota vào kho 2."""
    try:
        from luu_tru.trang_thai_key import danh_dau_het_quota
        danh_dau_het_quota(loai_nao, provider, key_id)
        _ghi_log("dai-nao", f"Đánh dấu {provider} ({loai_nao}) hết quota.")
    except Exception as e:
        _ghi_log("loi", f"Đánh dấu hết quota lỗi: {e}")


# ================================================================
# THỬ XOAY KEY
# ================================================================
def _thu_xoay_key(chu_so_huu, loai_nao, key_hien_tai=""):
    """Thử xoay sang key khác cùng loại."""
    try:
        from dai_nao.boss_model.xoay_key_boss import xoay_key_boss
        return xoay_key_boss(chu_so_huu, loai_nao, key_hien_tai)
    except Exception as e:
        _ghi_log("loi", f"Xoay key Boss lỗi: {e}")
        return None


# ================================================================
# KIỂM TRA HẾT TẤT CẢ
# ================================================================
def kiem_tra_het_tat_ca(chu_so_huu):
    """
    Kiểm tra cả 2 loại Boss đều hết quota không.

    Trả về: True/False.
    """
    if not chu_so_huu:
        return True

    try:
        from dai_nao.boss_model.xoay_key_boss import dem_key_con_dung

        con_boss = dem_key_con_dung(chu_so_huu, LOAI_BOSS_DAU)
        con_boss_the = dem_key_con_dung(chu_so_huu, LOAI_BOSS_THE)

        return (con_boss + con_boss_the) == 0
    except Exception:
        return True


# ================================================================
# THỜI GIAN HỒI GẦN NHẤT
# ================================================================
def thoi_gian_hoi_gan_nhat(chu_so_huu):
    """
    Tính thời gian chờ đến khi Boss gần nhất hồi quota.

    Trả về: số giây (int) hoặc 0 nếu có key dùng được ngay.
    """
    try:
        from luu_tru.trang_thai_key import thoi_gian_hoi_gan_nhat as _tg

        tg_boss = _tg(LOAI_BOSS_DAU)
        tg_boss_the = _tg(LOAI_BOSS_THE)

        if tg_boss == 0 or tg_boss_the == 0:
            return 0

        return min(tg_boss, tg_boss_the)
    except Exception:
        return 0


# ================================================================
# THÔNG BÁO CHO ĐẠI NÃO
# ================================================================
def tao_thong_bao_het_quota(chu_so_huu):
    """
    Tạo thông báo khi hết tất cả Boss.

    Trả về: chuỗi thông báo.
    """
    tg = thoi_gian_hoi_gan_nhat(chu_so_huu)

    if tg <= 0:
        return "⚠️ Tất cả Boss đều hết quota."

    if tg < 60:
        return f"⚠️ Hết Boss. Thử lại sau {tg} giây."
    if tg < 3600:
        return f"⚠️ Hết Boss. Thử lại sau {tg // 60} phút."
    if tg < 86400:
        return f"⚠️ Hết Boss. Thử lại sau {tg // 3600} giờ."

    return f"⚠️ Hết Boss. Thử lại sau {tg // 86400} ngày."


# ================================================================
# RESET TẤT CẢ
# ================================================================
def reset_tat_ca(chu_so_huu):
    """
    Reset trạng thái hết quota của tất cả key Boss.

    Trả về: True/False.
    """
    try:
        from luu_tru.trang_thai_key import reset_tat_ca as _reset

        _reset(LOAI_BOSS_DAU)
        _reset(LOAI_BOSS_THE)
        _ghi_log("dai-nao", f"Reset Boss cho {chu_so_huu}")
        return True
    except Exception as e:
        _ghi_log("loi", f"Reset Boss lỗi: {e}")
        return False


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(chu_so_huu):
    """Tạo chuỗi tóm tắt trạng thái Boss."""
    try:
        from dai_nao.boss_model.xoay_key_boss import dem_key_con_dung

        con_boss = dem_key_con_dung(chu_so_huu, LOAI_BOSS_DAU)
        con_boss_the = dem_key_con_dung(chu_so_huu, LOAI_BOSS_THE)

        return f"Boss Đầu: {con_boss} key dùng được | Boss Thế: {con_boss_the} key dùng được"
    except Exception:
        return ""
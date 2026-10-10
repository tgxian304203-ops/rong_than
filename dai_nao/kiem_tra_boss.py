"""
kiem_tra_boss.py - Kiểm tra Boss có hợp lệ không.

Nhiệm vụ:
    - Kiểm tra Boss còn quota không.
    - Kiểm tra Boss có đọc hợp đồng chưa (nếu là Boss THẾ).
    - Kiểm tra Boss trả kết quả đúng format không.
    - Kiểm tra Boss có trả code / kết quả không.

Nguyên tắc:
    - Đại não gọi hàm này trước khi tin Boss.
    - Nếu Boss không hợp lệ → đổi Boss khác / báo lỗi.
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
# KIỂM TRA BOSS CÒN QUOTA
# ================================================================
def kiem_tra_boss_con_quota(loai_nao="boss"):
    """
    Kiểm tra Boss còn key + quota không.

    Trả về: True/False.
    """
    try:
        from dai_nao.boss_model.kiem_ke_key_boss import kiem_ke_key_boss

        if loai_nao == "boss":
            return kiem_ke_key_boss("boss")
        if loai_nao == "tieu_boss":
            return kiem_ke_key_boss("tieu_boss")

        return False
    except ImportError:
        # Chưa có boss_model → coi như không có quota
        return False
    except Exception:
        return False


# ================================================================
# KIỂM TRA KẾT QUẢ BOSS
# ================================================================
def kiem_tra_ket_qua_boss(ket_qua):
    """
    Kiểm tra kết quả Boss trả về có hợp lệ không.

    ket_qua: dict.

    Trả về: (ok, loi).
    """
    if not ket_qua:
        return False, "Boss không trả kết quả."

    if not isinstance(ket_qua, dict):
        return False, "Kết quả Boss không phải dict."

    # Boss phải có ít nhất 1 trong 3:
    # - tra_loi (câu trả lời)
    # - code (code sinh ra)
    # - ket_qua_chay (kết quả chạy)
    co_tra_loi = bool(ket_qua.get("tra_loi"))
    co_code = bool(ket_qua.get("code"))
    co_ket_qua_chay = bool(ket_qua.get("ket_qua_chay"))

    if not (co_tra_loi or co_code or co_ket_qua_chay):
        return False, "Boss không trả về nội dung (tra_loi/code/ket_qua_chay)."

    return True, ""


# ================================================================
# KIỂM TRA BOSS THẾ ĐÃ ĐỌC
# ================================================================
def kiem_tra_boss_the_da_doc(chu_so_huu, id_chat):
    """
    Kiểm tra Boss THẾ đã đọc hợp đồng chưa (dùng tracking).

    Trả về: True/False.
    """
    try:
        from cay_linh_hon.hop_dong import doc_hop_dong
        hop_dong = doc_hop_dong(chu_so_huu, id_chat)
        if not hop_dong:
            return False
        return bool(hop_dong.get("boss_da_doc", False))
    except Exception:
        return False


# ================================================================
# KIỂM TRA TỔNG HỢP
# ================================================================
def kiem_tra_tong_hop(chu_so_huu, id_chat, ket_qua_boss,
                      la_boss_the=False):
    """
    Kiểm tra tổng hợp: quota + kết quả + đã đọc (nếu Boss thế).

    Trả về: {
        thanh_cong: bool,
        loi: str,
        can_doi_boss: bool,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "loi": "",
        "can_doi_boss": False,
    }

    # 1. Kiểm tra kết quả Boss
    ok, loi = kiem_tra_ket_qua_boss(ket_qua_boss)
    if not ok:
        ket_qua["loi"] = loi
        ket_qua["can_doi_boss"] = True
        return ket_qua

    # 2. Nếu là Boss THẾ → phải đã đọc
    if la_boss_the:
        if not kiem_tra_boss_the_da_doc(chu_so_huu, id_chat):
            ket_qua["loi"] = "Boss THẾ chưa đọc hợp đồng."
            ket_qua["can_doi_boss"] = True
            return ket_qua

    ket_qua["thanh_cong"] = True
    return ket_qua


# ================================================================
# ĐẾM SỐ LẦN BOSS LỖI
# ================================================================
def dem_so_lan_boss_loi(chu_so_huu, id_chat):
    """
    Đếm số lần Boss lỗi ở chat này (để biết có nên đổi Boss không).

    Trả về: int.
    """
    try:
        from cay_linh_hon.luu_loi import dem_loi
        return dem_loi(chu_so_huu, id_chat)
    except Exception:
        return 0


# ================================================================
# NÊN ĐỔI BOSS KHÔNG
# ================================================================
def nen_doi_boss(chu_so_huu, id_chat, nguong=3):
    """
    Kiểm tra có nên đổi Boss không (khi Boss lỗi quá nhiều).

    Trả về: True/False.
    """
    so_lan_loi = dem_so_lan_boss_loi(chu_so_huu, id_chat)
    return so_lan_loi >= nguong


# ================================================================
# TÓM TẮT KIỂM TRA
# ================================================================
def tom_tat_kiem_tra(ket_qua):
    """Tạo chuỗi tóm tắt kiểm tra Boss."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return "✅ Boss hợp lệ."
    return f"❌ Boss lỗi: {ket_qua.get('loi', '')[:150]}"
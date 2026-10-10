"""
do_boss.py - Dò tìm Boss khả dụng.

Nhiệm vụ:
    - Dò danh sách key Boss (2 loại: boss, tieu_boss).
    - Chọn key còn quota.
    - Trả về thông tin key để gọi.

Nguyên tắc:
    - Dùng chung quy tắc với Model (không dùng chung key).
    - Dò tuần tự: Groq → OpenRouter → Gemini.
    - Key hết quota → nhảy key kế.
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
THU_TU_PROVIDER = ["Groq", "OpenRouter", "Gemini"]


# ================================================================
# DÒ BOSS KHẢ DỤNG
# ================================================================
def do_boss(chu_so_huu, loai_nao="boss"):
    """
    Dò tìm Boss khả dụng (còn quota).

    chu_so_huu: tên đăng nhập.
    loai_nao: "boss" (Boss Đầu) hoặc "tieu_boss" (Boss Thế).

    Trả về: {
        thanh_cong: bool,
        key: str,
        key_id: str,
        provider: str,
        loai_nao: str,
        loi: str?,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "key": "",
        "key_id": "",
        "provider": "",
        "loai_nao": loai_nao,
        "loi": "",
    }

    if not chu_so_huu:
        ket_qua["loi"] = "Thiếu chu_so_huu."
        return ket_qua

    if loai_nao not in ("boss", "tieu_boss"):
        ket_qua["loi"] = f"Loại Boss không hợp lệ: {loai_nao}"
        return ket_qua

    # 1. Lấy danh sách key Boss
    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_cua
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    except Exception as e:
        ket_qua["loi"] = f"Không lấy được danh sách key: {e}"
        return ket_qua

    # 2. Lọc key theo loại Boss + còn quota
    danh_sach_loc = []
    for key in danh_sach:
        if key.get("loai_key") == "tra_web":
            continue
        if key.get("loai_nao") != loai_nao:
            continue
        danh_sach_loc.append(key)

    if not danh_sach_loc:
        ket_qua["loi"] = f"Chưa có key Boss loại '{loai_nao}'."
        return ket_qua

    # 3. Sắp xếp theo provider (Groq → OpenRouter → Gemini)
    danh_sach_loc.sort(key=lambda k: _thu_tu_provider(k.get("provider", "")))

    # 4. Chọn key còn quota
    for key in danh_sach_loc:
        key_id = key.get("id", "")
        provider = key.get("provider", "")
        phan_tram = key.get("phan_tram", 100)

        if phan_tram <= 0:
            continue

        # Kiểm tra trạng thái hết quota (nếu có)
        try:
            from luu_tru.trang_thai_key import kiem_tra_hoi_quota
            if not kiem_tra_hoi_quota(loai_nao, provider, key_id):
                continue
        except Exception:
            pass

        ket_qua["thanh_cong"] = True
        ket_qua["key"] = key.get("key", "")
        ket_qua["key_id"] = key_id
        ket_qua["provider"] = provider

        _ghi_log("dai-nao", f"Dò Boss: {provider} ({loai_nao})")
        return ket_qua

    ket_qua["loi"] = f"Tất cả key Boss loại '{loai_nao}' đều hết quota."
    return ket_qua


# ================================================================
# DÒ BOSS THEO PROVIDER
# ================================================================
def do_boss_theo_provider(chu_so_huu, loai_nao, provider):
    """Dò Boss theo provider cụ thể."""
    ket_qua = do_boss(chu_so_huu, loai_nao)
    if ket_qua.get("thanh_cong") and ket_qua.get("provider") == provider:
        return ket_qua
    ket_qua["thanh_cong"] = False
    ket_qua["loi"] = f"Không có key {provider} cho {loai_nao}."
    return ket_qua


# ================================================================
# ĐẾM KEY KHẢ DỤNG
# ================================================================
def dem_key_kha_dung(chu_so_huu, loai_nao="boss"):
    """Đếm số key Boss còn dùng được."""
    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_cua
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    except Exception:
        return 0

    dem = 0
    for key in danh_sach:
        if key.get("loai_key") == "tra_web":
            continue
        if key.get("loai_nao") != loai_nao:
            continue
        if key.get("phan_tram", 100) > 0:
            dem += 1

    return dem


# ================================================================
# THỨ TỰ PROVIDER
# ================================================================
def _thu_tu_provider(provider):
    """Trả thứ tự ưu tiên provider."""
    try:
        return THU_TU_PROVIDER.index(provider)
    except (ValueError, TypeError):
        return 999


# ================================================================
# DÒ CẢ 2 LOẠI BOSS
# ================================================================
def do_ca_2_loai_boss(chu_so_huu):
    """
    Dò cả Boss Đầu và Boss Thế.

    Trả về: {boss, tieu_boss}.
    """
    return {
        "boss": do_boss(chu_so_huu, "boss"),
        "tieu_boss": do_boss(chu_so_huu, "tieu_boss"),
    }


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt dò Boss."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ Boss: {ket_qua.get('provider')} ({ket_qua.get('loai_nao')})"
    return f"❌ Dò Boss lỗi: {ket_qua.get('loi', '')[:100]}"
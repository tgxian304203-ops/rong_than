"""
do_model.py - Dò Model khả dụng.

Nhiệm vụ:
    - Dò danh sách key Model.
    - Chọn key còn quota.
    - Trả về thông tin key để gọi Model.

Nguyên tắc:
    - Dùng chung quy tắc với Boss (không dùng chung key).
    - Dò tuần tự: Groq → OpenRouter → Gemini.
    - Key hết quota → nhảy key kế.
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
THU_TU_PROVIDER = ["Groq", "OpenRouter", "Gemini"]
LOAI_NAO_MODEL = "tieu_boss"   # Key Model gắn loai_nao = tieu_boss


# ================================================================
# DÒ MODEL KHẢ DỤNG
# ================================================================
def do_model(chu_so_huu):
    """
    Dò tìm Model khả dụng (còn quota).

    chu_so_huu: tên đăng nhập.

    Trả về: {
        thanh_cong: bool,
        key, key_id, provider,
        loi?
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "key": "",
        "key_id": "",
        "provider": "",
        "loi": "",
    }

    if not chu_so_huu:
        ket_qua["loi"] = "Thiếu chu_so_huu."
        return ket_qua

    # 1. Lấy danh sách key
    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_cua
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    except Exception as e:
        ket_qua["loi"] = f"Không lấy được danh sách key: {e}"
        return ket_qua

    # 2. Lọc key model (loai_nao = tieu_boss)
    danh_sach_loc = []
    for key in danh_sach:
        if key.get("loai_key") == "tra_web":
            continue
        if key.get("loai_nao") != LOAI_NAO_MODEL:
            continue
        danh_sach_loc.append(key)

    if not danh_sach_loc:
        ket_qua["loi"] = "Chưa có key Model."
        return ket_qua

    # 3. Sắp xếp theo provider ưu tiên
    danh_sach_loc.sort(key=lambda k: _thu_tu_provider(k.get("provider", "")))

    # 4. Chọn key còn quota
    for key in danh_sach_loc:
        key_id = key.get("id", "")
        provider = key.get("provider", "")
        phan_tram = key.get("phan_tram", 100)

        if phan_tram <= 0:
            continue

        try:
            from luu_tru.trang_thai_key import kiem_tra_hoi_quota
            if not kiem_tra_hoi_quota(LOAI_NAO_MODEL, provider, key_id):
                continue
        except Exception:
            pass

        ket_qua["thanh_cong"] = True
        ket_qua["key"] = key.get("key", "")
        ket_qua["key_id"] = key_id
        ket_qua["provider"] = provider

        _ghi_log("tieu-nao", f"Dò Model: {provider}")
        return ket_qua

    ket_qua["loi"] = "Tất cả key Model đều hết quota."
    return ket_qua


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
# ĐẾM KEY KHẢ DỤNG
# ================================================================
def dem_key_kha_dung(chu_so_huu):
    """Đếm số key Model còn dùng được."""
    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_cua
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    except Exception:
        return 0

    dem = 0
    for key in danh_sach:
        if key.get("loai_key") == "tra_web":
            continue
        if key.get("loai_nao") != LOAI_NAO_MODEL:
            continue
        if key.get("phan_tram", 100) > 0:
            dem += 1

    return dem


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt dò Model."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ Model: {ket_qua.get('provider')}"
    return f"❌ Dò Model lỗi: {ket_qua.get('loi', '')[:100]}"
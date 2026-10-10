"""
xoay_key_boss.py - Xoay key Boss khi hết quota.

Nhiệm vụ:
    - Tìm key Boss kế tiếp khi key hiện tại hết quota.
    - Xoay vòng theo thứ tự: Groq → OpenRouter → Gemini.
    - Đánh dấu key hết quota.
    - Kiểm tra key đã hồi quota chưa.

Nguyên tắc:
    - 1 key = 1 tài khoản.
    - Cùng 1 provider → cùng 1 model.
    - Hết key → provider kế.
    - Hết provider → quay lại key #1 nếu hồi quota.
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


# ================================================================
# XOAY KEY BOSS
# ================================================================
def xoay_key_boss(chu_so_huu, loai_nao="boss", key_hien_tai=""):
    """
    Tìm key Boss kế tiếp khi key hiện tại hết quota.

    Trả về: {
        thanh_cong, key, key_id, provider, loai_nao, loi?
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

    # 1. Lấy danh sách key Boss
    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_cua
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    except Exception as e:
        ket_qua["loi"] = f"Không lấy được danh sách key: {e}"
        return ket_qua

    # 2. Lọc theo loại Boss
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

    # 3. Sắp xếp theo provider ưu tiên
    danh_sach_loc.sort(key=lambda k: _thu_tu_provider(k.get("provider", "")))

    # 4. Tìm vị trí key hiện tại
    vi_tri_hien_tai = -1
    for i, key in enumerate(danh_sach_loc):
        if key.get("id") == key_hien_tai:
            vi_tri_hien_tai = i
            break

    # 5. Duyệt từ vị trí kế tiếp
    bat_dau = vi_tri_hien_tai + 1 if vi_tri_hien_tai >= 0 else 0

    for i in range(bat_dau, len(danh_sach_loc)):
        key = danh_sach_loc[i]
        if _key_con_dung_duoc(key):
            return _tao_ket_qua(key, loai_nao)

    # 6. Hết danh sách → quay lại từ đầu
    for i in range(0, bat_dau):
        key = danh_sach_loc[i]
        if _key_con_dung_duoc(key):
            _ghi_log("dai-nao", f"Xoay Boss quay lại từ đầu ({loai_nao})")
            return _tao_ket_qua(key, loai_nao)

    ket_qua["loi"] = f"Tất cả key Boss loại '{loai_nao}' đều hết quota."
    return ket_qua


# ================================================================
# KIỂM TRA KEY CÒN DÙNG ĐƯỢC
# ================================================================
def _key_con_dung_duoc(key):
    """Kiểm tra key còn quota + chưa hết hạn."""
    if not key:
        return False

    if key.get("phan_tram", 100) <= 0:
        return False

    try:
        from luu_tru.trang_thai_key import kiem_tra_hoi_quota
        loai_nao = key.get("loai_nao", "boss")
        provider = key.get("provider", "")
        key_id = key.get("id", "")
        return kiem_tra_hoi_quota(loai_nao, provider, key_id)
    except Exception:
        return True


# ================================================================
# TẠO KẾT QUẢ
# ================================================================
def _tao_ket_qua(key, loai_nao):
    """Tạo dict kết quả từ key."""
    _ghi_log("dai-nao", f"Xoay Boss: {key.get('provider')} ({loai_nao})")
    return {
        "thanh_cong": True,
        "key": key.get("key", ""),
        "key_id": key.get("id", ""),
        "provider": key.get("provider", ""),
        "loai_nao": loai_nao,
    }


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
# ĐÁNH DẤU KEY HẾT QUOTA
# ================================================================
def danh_dau_key_het_quota(chu_so_huu, loai_nao, provider, key_id):
    """Đánh dấu key Boss hết quota."""
    try:
        from luu_tru.trang_thai_key import danh_dau_het_quota
        return danh_dau_het_quota(loai_nao, provider, key_id)
    except Exception as e:
        _ghi_log("loi", f"Đánh dấu hết quota lỗi: {e}")
        return False


# ================================================================
# ĐẾM KEY CÒN DÙNG
# ================================================================
def dem_key_con_dung(chu_so_huu, loai_nao="boss"):
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
        if _key_con_dung_duoc(key):
            dem += 1

    return dem


# ================================================================
# LẤY KEY ĐẦU TIÊN CÒN DÙNG
# ================================================================
def lay_key_dau_tien(chu_so_huu, loai_nao="boss"):
    """Lấy key Boss đầu tiên còn dùng được."""
    return xoay_key_boss(chu_so_huu, loai_nao, "")


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt xoay key Boss."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ Xoay Boss: {ket_qua.get('provider')} ({ket_qua.get('loai_nao')})"
    return f"❌ Xoay Boss lỗi: {ket_qua.get('loi', '')[:100]}"
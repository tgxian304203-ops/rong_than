"""
xoay_key_model.py - Xoay key Model khi hết quota.

Nhiệm vụ:
    - Tìm key Model kế tiếp khi key hiện tại hết quota.
    - Xoay vòng theo thứ tự: Groq → OpenRouter → Gemini.
    - Đánh dấu key hết quota.

Nguyên tắc:
    - Dùng key loai_nao = "tieu_boss".
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
LOAI_NAO_MODEL = "tieu_boss"


# ================================================================
# XOAY KEY MODEL
# ================================================================
def xoay_key_model(chu_so_huu, key_hien_tai=""):
    """
    Tìm key Model kế tiếp khi key hiện tại hết quota.

    Trả về: {
        thanh_cong, key, key_id, provider, loi?
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

    # 1. Lấy danh sách key Model
    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_cua
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    except Exception as e:
        ket_qua["loi"] = f"Không lấy được danh sách key: {e}"
        return ket_qua

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

    # 2. Sắp xếp theo provider
    danh_sach_loc.sort(key=lambda k: _thu_tu_provider(k.get("provider", "")))

    # 3. Tìm vị trí key hiện tại
    vi_tri = -1
    for i, key in enumerate(danh_sach_loc):
        if key.get("id") == key_hien_tai:
            vi_tri = i
            break

    bat_dau = vi_tri + 1 if vi_tri >= 0 else 0

    # 4. Duyệt từ vị trí kế tiếp
    for i in range(bat_dau, len(danh_sach_loc)):
        key = danh_sach_loc[i]
        if _key_con_dung_duoc(key):
            return _tao_ket_qua(key)

    # 5. Hết danh sách → quay lại từ đầu
    for i in range(0, bat_dau):
        key = danh_sach_loc[i]
        if _key_con_dung_duoc(key):
            _ghi_log("tieu-nao", "Xoay Model quay lại từ đầu.")
            return _tao_ket_qua(key)

    ket_qua["loi"] = "Tất cả key Model đều hết quota."
    return ket_qua


# ================================================================
# KIỂM TRA KEY CÒN DÙNG
# ================================================================
def _key_con_dung_duoc(key):
    """Kiểm tra key còn quota + chưa hết hạn."""
    if not key:
        return False

    if key.get("phan_tram", 100) <= 0:
        return False

    try:
        from luu_tru.trang_thai_key import kiem_tra_hoi_quota
        provider = key.get("provider", "")
        key_id = key.get("id", "")
        return kiem_tra_hoi_quota(LOAI_NAO_MODEL, provider, key_id)
    except Exception:
        return True


# ================================================================
# TẠO KẾT QUẢ
# ================================================================
def _tao_ket_qua(key):
    """Tạo dict kết quả từ key."""
    _ghi_log("tieu-nao", f"Xoay Model: {key.get('provider')}")
    return {
        "thanh_cong": True,
        "key": key.get("key", ""),
        "key_id": key.get("id", ""),
        "provider": key.get("provider", ""),
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
def danh_dau_het_quota(provider, key_id):
    """Đánh dấu key Model hết quota."""
    try:
        from luu_tru.trang_thai_key import danh_dau_het_quota as _danh_dau
        return _danh_dau(LOAI_NAO_MODEL, provider, key_id)
    except Exception as e:
        _ghi_log("loi", f"Đánh dấu hết quota lỗi: {e}")
        return False


# ================================================================
# ĐẾM KEY CÒN DÙNG
# ================================================================
def dem_key_con_dung(chu_so_huu):
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
        if _key_con_dung_duoc(key):
            dem += 1

    return dem


# ================================================================
# LẤY KEY ĐẦU TIÊN CÒN DÙNG
# ================================================================
def lay_key_dau_tien(chu_so_huu):
    """Lấy key Model đầu tiên còn dùng được."""
    return xoay_key_model(chu_so_huu, "")


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt xoay key Model."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ Xoay Model: {ket_qua.get('provider')}"
    return f"❌ Xoay Model lỗi: {ket_qua.get('loi', '')[:100]}"
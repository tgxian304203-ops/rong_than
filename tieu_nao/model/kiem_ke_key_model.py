"""
kiem_ke_key_model.py - Kiểm kê key Model.

Nhiệm vụ:
    - Đếm số key Model theo provider.
    - Đếm số key còn dùng / hết quota.
    - Trả danh sách key cho giao diện.

Nguyên tắc:
    - Chỉ key loai_nao = tieu_boss.
    - Kiểm kê nhanh — không gọi API.
"""


# ================================================================
# HẰNG SỐ
# ================================================================
LOAI_NAO_MODEL = "tieu_boss"
THU_TU_PROVIDER = ["Groq", "OpenRouter", "Gemini"]


# ================================================================
# LẤY DANH SÁCH KEY MODEL
# ================================================================
def lay_danh_sach_key_model(chu_so_huu):
    """Lấy danh sách key Model."""
    if not chu_so_huu:
        return []

    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_cua
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    except Exception:
        return []

    ket_qua = []
    for key in danh_sach:
        if key.get("loai_key") == "tra_web":
            continue
        if key.get("loai_nao") != LOAI_NAO_MODEL:
            continue
        ket_qua.append(key)

    return ket_qua


# ================================================================
# ĐẾM KEY THEO PROVIDER
# ================================================================
def dem_key_theo_provider(chu_so_huu):
    """Đếm số key Model theo từng provider."""
    ket_qua = {p: 0 for p in THU_TU_PROVIDER}

    danh_sach = lay_danh_sach_key_model(chu_so_huu)

    for key in danh_sach:
        provider = key.get("provider", "")
        if provider in ket_qua:
            ket_qua[provider] += 1

    return ket_qua


# ================================================================
# ĐẾM KEY CÒN DÙNG / HẾT QUOTA
# ================================================================
def dem_key_con_dung(chu_so_huu):
    """Đếm số key Model còn dùng được."""
    danh_sach = lay_danh_sach_key_model(chu_so_huu)

    dem = 0
    for key in danh_sach:
        if _key_con_dung(key):
            dem += 1

    return dem


def dem_key_het_quota(chu_so_huu):
    """Đếm số key Model đang hết quota."""
    danh_sach = lay_danh_sach_key_model(chu_so_huu)

    dem = 0
    for key in danh_sach:
        if not _key_con_dung(key):
            dem += 1

    return dem


def _key_con_dung(key):
    """Kiểm tra key còn dùng được không."""
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
# KIỂM TRA CÓ KEY KHẢ DỤNG
# ================================================================
def co_key_kha_dung(chu_so_huu):
    """Kiểm tra có key Model nào khả dụng không."""
    return dem_key_con_dung(chu_so_huu) > 0


def kiem_ke_key_model(chu_so_huu=""):
    """Kiểm tra có key Model khả dụng không."""
    if not chu_so_huu:
        return False
    return co_key_kha_dung(chu_so_huu)


# ================================================================
# KIỂM KÊ TỔNG HỢP
# ================================================================
def kiem_ke_tong_hop(chu_so_huu):
    """Kiểm kê tổng hợp key Model."""
    danh_sach = lay_danh_sach_key_model(chu_so_huu)

    return {
        "tong": len(danh_sach),
        "con_dung": dem_key_con_dung(chu_so_huu),
        "het_quota": dem_key_het_quota(chu_so_huu),
        "theo_provider": dem_key_theo_provider(chu_so_huu),
    }


# ================================================================
# DANH SÁCH KEY ĐẦY ĐỦ
# ================================================================
def lay_danh_sach_key_day_du(chu_so_huu):
    """Lấy danh sách key Model đầy đủ (đã che key gốc)."""
    danh_sach = lay_danh_sach_key_model(chu_so_huu)

    ket_qua = []
    for key in danh_sach:
        ket_qua.append({
            "id": key.get("id"),
            "provider": key.get("provider"),
            "ten": key.get("provider"),
            "loai_nao": key.get("loai_nao"),
            "phan_tram": key.get("phan_tram", 100),
            "con_dung": _key_con_dung(key),
            "ngay_tao": key.get("ngay_tao", 0),
        })

    return ket_qua


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat_kiem_ke(chu_so_huu):
    """Tạo chuỗi tóm tắt kiểm kê key Model."""
    kk = kiem_ke_tong_hop(chu_so_huu)

    if kk["tong"] == 0:
        return "❌ Chưa có key Model."

    return f"Model: {kk['con_dung']}/{kk['tong']} key dùng được"
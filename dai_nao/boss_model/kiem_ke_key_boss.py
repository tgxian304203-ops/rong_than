"""
kiem_ke_key_boss.py - Kiểm kê key Boss.

Nhiệm vụ:
    - Đếm số key Boss theo từng provider.
    - Đếm số key còn dùng được / hết quota.
    - Trả danh sách key theo loại Boss.
    - Kiểm tra có key nào khả dụng không.

Nguyên tắc:
    - Kiểm kê nhanh — không gọi API (chỉ đọc kho 1 + kho 2).
    - Dùng cho do_boss + giao diện.
"""


# ================================================================
# HẰNG SỐ
# ================================================================
LOAI_BOSS_DAU = "boss"
LOAI_BOSS_THE = "tieu_boss"
THU_TU_PROVIDER = ["Groq", "OpenRouter", "Gemini"]


# ================================================================
# LẤY DANH SÁCH KEY BOSS
# ================================================================
def lay_danh_sach_key_boss(chu_so_huu, loai_nao="boss"):
    """
    Lấy danh sách key Boss theo loại.

    Trả về: list.
    """
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
        if key.get("loai_nao") != loai_nao:
            continue
        ket_qua.append(key)

    return ket_qua


# ================================================================
# ĐẾM KEY THEO PROVIDER
# ================================================================
def dem_key_theo_provider(chu_so_huu, loai_nao="boss"):
    """
    Đếm số key Boss theo từng provider.

    Trả về: dict {Groq: N, OpenRouter: N, Gemini: N}.
    """
    ket_qua = {p: 0 for p in THU_TU_PROVIDER}

    danh_sach = lay_danh_sach_key_boss(chu_so_huu, loai_nao)

    for key in danh_sach:
        provider = key.get("provider", "")
        if provider in ket_qua:
            ket_qua[provider] += 1

    return ket_qua


# ================================================================
# ĐẾM KEY CÒN DÙNG / HẾT QUOTA
# ================================================================
def dem_key_con_dung(chu_so_huu, loai_nao="boss"):
    """Đếm số key Boss còn dùng được."""
    danh_sach = lay_danh_sach_key_boss(chu_so_huu, loai_nao)

    dem = 0
    for key in danh_sach:
        if _key_con_dung(key):
            dem += 1

    return dem


def dem_key_het_quota(chu_so_huu, loai_nao="boss"):
    """Đếm số key Boss đang hết quota."""
    danh_sach = lay_danh_sach_key_boss(chu_so_huu, loai_nao)

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
        loai_nao = key.get("loai_nao", "boss")
        provider = key.get("provider", "")
        key_id = key.get("id", "")
        return kiem_tra_hoi_quota(loai_nao, provider, key_id)
    except Exception:
        return True


# ================================================================
# KIỂM TRA CÓ KEY KHẢ DỤNG
# ================================================================
def co_key_kha_dung(chu_so_huu, loai_nao="boss"):
    """
    Kiểm tra có key Boss nào khả dụng không.

    Trả về: True/False.
    """
    return dem_key_con_dung(chu_so_huu, loai_nao) > 0


def kiem_ke_key_boss(loai_nao="boss", chu_so_huu=""):
    """
    Kiểm tra có key Boss khả dụng không (dùng cho kiem_tra_boss).

    Trả về: True/False.
    """
    if not chu_so_huu:
        return False
    return co_key_kha_dung(chu_so_huu, loai_nao)


# ================================================================
# KIỂM KÊ TỔNG HỢP
# ================================================================
def kiem_ke_tong_hop(chu_so_huu):
    """
    Kiểm kê tổng hợp cả 2 loại Boss.

    Trả về: dict.
    """
    ket_qua = {}

    for loai in (LOAI_BOSS_DAU, LOAI_BOSS_THE):
        danh_sach = lay_danh_sach_key_boss(chu_so_huu, loai)

        ket_qua[loai] = {
            "tong": len(danh_sach),
            "con_dung": dem_key_con_dung(chu_so_huu, loai),
            "het_quota": dem_key_het_quota(chu_so_huu, loai),
            "theo_provider": dem_key_theo_provider(chu_so_huu, loai),
        }

    return ket_qua


# ================================================================
# DANH SÁCH KEY ĐẦY ĐỦ (cho giao diện)
# ================================================================
def lay_danh_sach_key_day_du(chu_so_huu, loai_nao="boss"):
    """
    Lấy danh sách key Boss đầy đủ (đã che key gốc).

    Trả về: list dict.
    """
    danh_sach = lay_danh_sach_key_boss(chu_so_huu, loai_nao)

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
    """Tạo chuỗi tóm tắt kiểm kê key Boss."""
    kk = kiem_ke_tong_hop(chu_so_huu)
    phan = []

    for loai, du_lieu in kk.items():
        if du_lieu["tong"] == 0:
            continue

        phan.append(
            f"{loai}: {du_lieu['con_dung']}/{du_lieu['tong']} key dùng được"
        )

    return "\n".join(phan) if phan else "❌ Chưa có key Boss."
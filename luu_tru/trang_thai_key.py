"""
trang_thai_key.py - Quản lý trạng thái key Rồng Thần (kho 2).

Nhiệm vụ:
    - Theo dõi trạng thái hết quota của key (Boss / Model / Tra web).
    - Đánh dấu key hết quota + thời gian hồi.
    - Kiểm tra key đã hồi quota chưa.
    - Quota hồi đầu tháng (SERPJET/Tavily/Bright Data) hoặc RPM/RPD (Groq).

Nguyên tắc:
    - Trạng thái lưu ở KHO 2, collection trang_thai_key.
    - Mỗi key gắn: loai_key (boss/tieu_boss/tra_web), provider, key_id.
    - Không xóa key — chỉ đánh dấu.
"""

import time

from luu_tru.ghi_nho import _ket_noi_kho_2


# ================================================================
# LOẠI KEY HỢP LỆ
# ================================================================
LOAI_BOSS = "boss"
LOAI_TIEU_BOSS = "tieu_boss"
LOAI_TRA_WEB = "tra_web"
LOAI_HOP_LE = [LOAI_BOSS, LOAI_TIEU_BOSS, LOAI_TRA_WEB]


# ================================================================
# LẤY COLLECTION
# ================================================================
def _collection():
    """Collection trang_thai_key ở kho 2."""
    db, _ = _ket_noi_kho_2()
    if db is None:
        return None
    return db["trang_thai_key"]


# ================================================================
# TÍNH THỜI GIAN HỒI QUOTA
# ================================================================
def _tinh_thoi_gian_hoi(loai_key, provider):
    """
    Tính thời gian hồi quota theo loại key + provider.

    - Boss / Tiểu Boss (Groq/OpenRouter/Gemini): hồi theo RPM (1 phút) hoặc RPD (hôm sau).
    - Tra web (SERPJET/Tavily/Bright Data): hồi đầu tháng sau.

    Trả về: timestamp (int) thời điểm hồi.
    """
    now = time.time()

    if loai_key in (LOAI_BOSS, LOAI_TIEU_BOSS):
        # Key model hồi nhanh — 1 phút
        return int(now + 60)

    if loai_key == LOAI_TRA_WEB:
        # Tra web — hồi đầu tháng sau
        tg = time.localtime()
        thang_sau = tg.tm_mon + 1
        nam_sau = tg.tm_year
        if thang_sau > 12:
            thang_sau = 1
            nam_sau += 1
        return int(time.mktime((
            nam_sau, thang_sau, 1, 0, 0, 0, 0, 0, -1
        )))

    # Mặc định: hồi sau 1 giờ
    return int(now + 3600)


# ================================================================
# ĐÁNH DẤU HẾT QUOTA
# ================================================================
def danh_dau_het_quota(loai_key, provider, key_id):
    """
    Đánh dấu key hết quota.

    Trả về: True/False.
    """
    if not loai_key or not provider or not key_id:
        return False

    if loai_key not in LOAI_HOP_LE:
        return False

    col = _collection()
    if col is None:
        return False

    thoi_gian_hoi = _tinh_thoi_gian_hoi(loai_key, provider)

    try:
        col.update_one(
            {
                "loai_key": loai_key,
                "provider": provider,
                "key_id": key_id,
            },
            {
                "$set": {
                    "loai_key": loai_key,
                    "provider": provider,
                    "key_id": key_id,
                    "het_quota": True,
                    "thoi_gian_het": int(time.time()),
                    "thoi_gian_hoi": thoi_gian_hoi,
                }
            },
            upsert=True,
        )
        return True
    except Exception:
        return False


# ================================================================
# KIỂM TRA HỒI QUOTA
# ================================================================
def kiem_tra_hoi_quota(loai_key, provider, key_id):
    """
    Kiểm tra key đã hồi quota chưa.

    Trả về: True (dùng được) / False (còn hết quota).
    """
    if not loai_key or not provider or not key_id:
        return True

    col = _collection()
    if col is None:
        return True

    try:
        trang_thai = col.find_one({
            "loai_key": loai_key,
            "provider": provider,
            "key_id": key_id,
        })
        if not trang_thai:
            return True

        if not trang_thai.get("het_quota"):
            return True

        thoi_gian_hoi = trang_thai.get("thoi_gian_hoi", 0)
        if not thoi_gian_hoi:
            return True

        if int(time.time()) >= thoi_gian_hoi:
            col.update_one(
                {
                    "loai_key": loai_key,
                    "provider": provider,
                    "key_id": key_id,
                },
                {"$set": {
                    "het_quota": False,
                    "thoi_gian_hoi_phuc": int(time.time()),
                }},
            )
            return True

        return False
    except Exception:
        return True


# ================================================================
# LẤY TRẠNG THÁI CHI TIẾT
# ================================================================
def lay_trang_thai(loai_key, provider, key_id):
    """
    Lấy trạng thái chi tiết của 1 key.

    Trả về: dict.
    """
    if not loai_key or not provider or not key_id:
        return {}

    col = _collection()
    if col is None:
        return {}

    try:
        trang_thai = col.find_one({
            "loai_key": loai_key,
            "provider": provider,
            "key_id": key_id,
        })
        if not trang_thai:
            return {
                "het_quota": False,
                "thoi_gian_hoi": 0,
            }

        return {
            "het_quota": trang_thai.get("het_quota", False),
            "thoi_gian_het": trang_thai.get("thoi_gian_het", 0),
            "thoi_gian_hoi": trang_thai.get("thoi_gian_hoi", 0),
            "thoi_gian_hoi_phuc": trang_thai.get("thoi_gian_hoi_phuc", 0),
        }
    except Exception:
        return {}


# ================================================================
# XÓA TRẠNG THÁI
# ================================================================
def xoa_trang_thai(loai_key, provider, key_id):
    """Xóa trạng thái hết quota của 1 key."""
    if not loai_key or not provider or not key_id:
        return False

    col = _collection()
    if col is None:
        return False

    try:
        kq = col.delete_one({
            "loai_key": loai_key,
            "provider": provider,
            "key_id": key_id,
        })
        return kq.deleted_count > 0
    except Exception:
        return False


def xoa_tat_ca_cua_user(chu_so_huu):
    """Xóa tất cả trạng thái key của 1 user (khi xóa tài khoản)."""
    col = _collection()
    if col is None or not chu_so_huu:
        return False

    try:
        col.delete_many({"chu_so_huu": chu_so_huu})
        return True
    except Exception:
        return False


# ================================================================
# LẤY DANH SÁCH KEY HẾT QUOTA
# ================================================================
def lay_danh_sach_het_quota(loai_key=""):
    """
    Lấy danh sách các key đang hết quota.

    loai_key: nếu rỗng → lấy tất cả.
    """
    col = _collection()
    if col is None:
        return []

    try:
        dieu_kien = {"het_quota": True}
        if loai_key:
            dieu_kien["loai_key"] = loai_key
        return list(col.find(dieu_kien))
    except Exception:
        return []


# ================================================================
# ĐẾM KEY CÒN DÙNG ĐƯỢC
# ================================================================
def dem_key_con_dung(loai_key=""):
    """Đếm số key còn dùng được (không hết quota)."""
    col = _collection()
    if col is None:
        return 0

    try:
        dieu_kien = {"het_quota": {"$ne": True}}
        if loai_key:
            dieu_kien["loai_key"] = loai_key
        return col.count_documents(dieu_kien)
    except Exception:
        return 0


# ================================================================
# ĐẾM KEY HẾT QUOTA
# ================================================================
def dem_key_het_quota(loai_key=""):
    """Đếm số key đang hết quota."""
    col = _collection()
    if col is None:
        return 0

    try:
        dieu_kien = {"het_quota": True}
        if loai_key:
            dieu_kien["loai_key"] = loai_key
        return col.count_documents(dieu_kien)
    except Exception:
        return 0


# ================================================================
# TÓM TẮT TRẠNG THÁI
# ================================================================
def tom_tat_trang_thai():
    """Tạo chuỗi tóm tắt trạng thái key."""
    phan = []

    for loai in LOAI_HOP_LE:
        con = dem_key_con_dung(loai)
        het = dem_key_het_quota(loai)
        if con + het == 0:
            continue
        phan.append(f"{loai}: {con} dùng được, {het} hết quota")

    return "\n".join(phan) if phan else "Chưa có key nào."


# ================================================================
# THỜI GIAN HỒI GẦN NHẤT
# ================================================================
def thoi_gian_hoi_gan_nhat(loai_key=""):
    """
    Tính thời gian chờ đến khi key gần nhất hồi quota.

    Trả về: số giây (int) hoặc 0 nếu có key dùng được ngay.
    """
    col = _collection()
    if col is None:
        return 0

    try:
        dieu_kien = {"het_quota": True}
        if loai_key:
            dieu_kien["loai_key"] = loai_key

        danh_sach = list(col.find(dieu_kien))
        if not danh_sach:
            return 0

        now = int(time.time())
        thoi_gian_min = None

        for tt in danh_sach:
            thoi_gian_hoi = tt.get("thoi_gian_hoi", 0)
            if thoi_gian_hoi:
                con_lai = max(0, thoi_gian_hoi - now)
                if thoi_gian_min is None or con_lai < thoi_gian_min:
                    thoi_gian_min = con_lai

        return thoi_gian_min if thoi_gian_min is not None else 0
    except Exception:
        return 0


# ================================================================
# RESET TOÀN BỘ
# ================================================================
def reset_tat_ca(loai_key=""):
    """Reset trạng thái tất cả key (bỏ đánh dấu hết quota)."""
    col = _collection()
    if col is None:
        return False

    try:
        dieu_kien = {}
        if loai_key:
            dieu_kien["loai_key"] = loai_key
        col.update_many(dieu_kien, {"$set": {"het_quota": False}})
        return True
    except Exception:
        return False


def danh_sach_loai_key():
    """Trả danh sách loại key hợp lệ."""
    return list(LOAI_HOP_LE)


def la_loai_key_hop_le(loai):
    """Kiểm tra loại key có hợp lệ không."""
    return loai in LOAI_HOP_LE
"""
xoay_key.py - Quản lý xoay vòng key Rồng Thần.

Nhiệm vụ:
    - xoay_key(chu_so_huu): chuyển sang key tiếp theo trong thứ tự gọi.
    - key_tiep_theo(danh_sach_key, key_hien_tai): tìm key kế tiếp.
    - danh_dau_het_quota(key_id, chu_so_huu): đánh dấu key hết quota.
    - kiem_tra_hoi_quota(key_id, chu_so_huu): kiểm tra key đã hồi quota chưa.
    - xoay_vong(danh_sach_key): xoay vòng danh sách key.

Quy tắc (theo Phần 4):
    - Khi key hết quota → nhảy sang key tiếp theo.
    - Hết tất cả → quay lại key #1 nếu hồi quota.
    - Quota hồi sau 1 phút (RPM) hoặc 1 ngày (RPD).
    - Key bị đánh dấu het_quota sẽ bị bỏ qua cho đến khi hồi.

Trả về:
    - key_tiep_theo() → dict key_info hoặc None.
    - kiem_tra_hoi_quota() → True/False.

Tầng dữ liệu: dai_nao/ghi_nho.py
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
THOI_GIAN_HOI_QUOTA_RPM = 60          # 1 phút
THOI_GIAN_HOI_QUOTA_RPD = 24 * 3600   # 24 giờ


# ================================================================
# LẤY DANH SÁCH KEY
# ================================================================
def _lay_danh_sach_key(chu_so_huu):
    """Lấy danh sách key theo thứ tự gọi từ kiem_ke_key."""
    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        ket_qua = kiem_ke_key(chu_so_huu)
        if ket_qua.get("thanh_cong"):
            return ket_qua.get("thu_tu_goi", [])
    except ImportError:
        pass
    return []


# ================================================================
# LẤY TRẠNG THÁI KEY TỪ KHO 2
# ================================================================
def _lay_trang_thai_key(key_id):
    """
    Lấy trạng thái key từ kho 2.
    Trả về dict hoặc {} nếu chưa có.
    """
    if not key_id:
        return {}

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        ket_qua = db["trang_thai_key"].find_one({"key_id": key_id})
        return ket_qua or {}
    except Exception:
        return {}


def _luu_trang_thai_key(key_id, du_lieu):
    """Lưu trạng thái key vào kho 2."""
    if not key_id or not du_lieu:
        return False

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        db["trang_thai_key"].update_one(
            {"key_id": key_id},
            {"$set": dict(du_lieu, key_id=key_id)},
            upsert=True,
        )
        return True
    except Exception:
        return False


# ================================================================
# ĐÁNH DẤU HẾT QUOTA
# ================================================================
def danh_dau_het_quota(key_id, chu_so_huu="", loai_quota="rpm"):
    """
    Đánh dấu key hết quota.

    loai_quota: "rpm" (hồi sau 1 phút) | "rpd" (hồi sau 24 giờ).
    """
    if not key_id:
        return False

    thoi_gian_hoi = int(time.time())
    if loai_quota == "rpd":
        thoi_gian_hoi += THOI_GIAN_HOI_QUOTA_RPD
    else:
        thoi_gian_hoi += THOI_GIAN_HOI_QUOTA_RPM

    _luu_trang_thai_key(key_id, {
        "het_quota": True,
        "loai_quota": loai_quota,
        "thoi_gian_het": int(time.time()),
        "thoi_gian_hoi": thoi_gian_hoi,
        "chu_so_huu": chu_so_huu,
    })

    _ghi_log("tieu-nao", f"Đánh dấu key {key_id[:8]} hết quota ({loai_quota}).")
    return True


# ================================================================
# KIỂM TRA HỒI QUOTA
# ================================================================
def kiem_tra_hoi_quota(key_id, chu_so_huu=""):
    """
    Kiểm tra key đã hồi quota chưa.

    Trả về:
        - True: key đã hồi quota → có thể dùng lại.
        - False: key vẫn hết quota.
    """
    if not key_id:
        return True

    trang_thai = _lay_trang_thai_key(key_id)
    if not trang_thai:
        return True  # chưa có trạng thái → coi như bình thường

    if not trang_thai.get("het_quota"):
        return True

    thoi_gian_hoi = trang_thai.get("thoi_gian_hoi", 0)
    if not thoi_gian_hoi:
        return True

    # Đã hồi
    if int(time.time()) >= thoi_gian_hoi:
        # Xóa trạng thái hết quota
        _luu_trang_thai_key(key_id, {
            "het_quota": False,
            "thoi_gian_hoi_phuc": int(time.time()),
        })
        _ghi_log("tieu-nao", f"Key {key_id[:8]} đã hồi quota.")
        return True

    return False


# ================================================================
# TÌM KEY KẾ TIẾP
# ================================================================
def key_tiep_theo(danh_sach_key, key_hien_tai_id=""):
    """
    Tìm key kế tiếp trong danh sách.

    danh_sach_key: list key_info theo thứ tự gọi.
    key_hien_tai_id: id key hiện tại (nếu None → lấy key đầu).

    Trả về: dict key_info hoặc None.
    """
    if not danh_sach_key:
        return None

    # Bỏ qua key hiện tại
    if not key_hien_tai_id:
        # Lấy key đầu tiên còn dùng được
        for key in danh_sach_key:
            if kiem_tra_hoi_quota(key.get("id", "")):
                return key
        return None

    # Tìm vị trí key hiện tại
    vi_tri = -1
    for i, key in enumerate(danh_sach_key):
        if key.get("id") == key_hien_tai_id:
            vi_tri = i
            break

    # Duyệt từ vị trí kế tiếp
    if vi_tri >= 0:
        for i in range(vi_tri + 1, len(danh_sach_key)):
            if kiem_tra_hoi_quota(danh_sach_key[i].get("id", "")):
                return danh_sach_key[i]

    # Hết danh sách → quay lại từ đầu
    for i in range(0, vi_tri if vi_tri >= 0 else len(danh_sach_key)):
        if kiem_tra_hoi_quota(danh_sach_key[i].get("id", "")):
            _ghi_log("tieu-nao", "Hết key → quay lại từ đầu.")
            return danh_sach_key[i]

    return None


# ================================================================
# XOAY VÒNG DANH SÁCH
# ================================================================
def xoay_vong(danh_sach_key):
    """
    Xoay vòng danh sách key: đưa key hết quota xuống cuối,
    key còn dùng lên đầu.

    Trả về: danh sách đã sắp xếp lại.
    """
    if not danh_sach_key:
        return []

    con_dung = []
    het_quota = []

    for key in danh_sach_key:
        key_id = key.get("id", "")
        if kiem_tra_hoi_quota(key_id):
            con_dung.append(key)
        else:
            het_quota.append(key)

    return con_dung + het_quota


# ================================================================
# HÀM CHÍNH
# ================================================================
def xoay_key(chu_so_huu, key_hien_tai_id=""):
    """
    Chuyển sang key tiếp theo trong thứ tự gọi.

    chu_so_huu: tên đăng nhập.
    key_hien_tai_id: id key hiện tại (nếu có).

    Trả về dict key_info hoặc None nếu không có key nào dùng được.
    """
    danh_sach = _lay_danh_sach_key(chu_so_huu)
    if not danh_sach:
        _ghi_log("tieu-nao", f"Không có key nào cho {chu_so_huu}.")
        return None

    # Xoay vòng: key còn dùng lên đầu
    danh_sach_moi = xoay_vong(danh_sach)

    # Tìm key kế tiếp
    key_tiep = key_tiep_theo(danh_sach_moi, key_hien_tai_id)

    if key_tiep:
        _ghi_log(
            "tieu-nao",
            f"Xoay sang key {key_tiep.get('id', '')[:8]} "
            f"({key_tiep.get('provider', '')})",
        )
    else:
        _ghi_log("tieu-nao", "Không còn key nào dùng được.")

    return key_tiep


# ================================================================
# HÀM PHỤ: XOAY KEY THEO PROVIDER
# ================================================================
def xoay_key_theo_provider(chu_so_huu, provider, key_hien_tai_id=""):
    """Xoay key trong cùng 1 provider."""
    danh_sach = _lay_danh_sach_key(chu_so_huu)
    if not danh_sach:
        return None

    # Lọc theo provider
    ds_provider = [
        k for k in danh_sach
        if k.get("provider", "").lower() == provider.lower()
    ]
    if not ds_provider:
        return None

    ds_xoay = xoay_vong(ds_provider)
    return key_tiep_theo(ds_xoay, key_hien_tai_id)


# ================================================================
# HÀM PHỤ: ĐẾM KEY CÒN DÙNG
# ================================================================
def dem_key_con_dung(chu_so_huu):
    """Đếm số key còn dùng được (chưa hết quota)."""
    danh_sach = _lay_danh_sach_key(chu_so_huu)
    if not danh_sach:
        return 0

    dem = 0
    for key in danh_sach:
        if kiem_tra_hoi_quota(key.get("id", "")):
            dem += 1
    return dem


# ================================================================
# HÀM PHỤ: ĐẾM KEY HẾT QUOTA
# ================================================================
def dem_key_het_quota(chu_so_huu):
    """Đếm số key đang hết quota."""
    danh_sach = _lay_danh_sach_key(chu_so_huu)
    if not danh_sach:
        return 0

    dem = 0
    for key in danh_sach:
        if not kiem_tra_hoi_quota(key.get("id", "")):
            dem += 1
    return dem


# ================================================================
# HÀM PHỤ: XÓA TRẠNG THÁI KEY
# ================================================================
def xoa_trang_thai_key(key_id):
    """Xóa trạng thái hết quota của key."""
    if not key_id:
        return False

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        db["trang_thai_key"].delete_one({"key_id": key_id})
        return True
    except Exception:
        return False


def reset_tat_ca_trang_thai(chu_so_huu):
    """Reset toàn bộ trạng thái key của tài khoản."""
    danh_sach = _lay_danh_sach_key(chu_so_huu)
    if not danh_sach:
        return False

    for key in danh_sach:
        xoa_trang_thai_key(key.get("id", ""))

    _ghi_log("tieu-nao", f"Đã reset trạng thái key cho {chu_so_huu}")
    return True


# ================================================================
# HÀM PHỤ: TÓM TẮT TRẠNG THÁI
# ================================================================
def tom_tat_trang_thai(chu_so_huu):
    """Tạo chuỗi tóm tắt trạng thái key."""
    danh_sach = _lay_danh_sach_key(chu_so_huu)
    if not danh_sach:
        return "❌ Không có key."

    phan = []
    for key in danh_sach:
        key_id = key.get("id", "")
        provider = key.get("provider", "")
        con_dung = kiem_tra_hoi_quota(key_id)
        trang_thai = "✅" if con_dung else "⏸️"
        phan.append(f"{trang_thai} {provider} / {key_id[:8]}")

    return "\n".join(phan)


# ================================================================
# HÀM PHỤ: LẤY TRẠNG THÁI CHI TIẾT
# ================================================================
def lay_trang_thai_chi_tiet(chu_so_huu):
    """Lấy trạng thái chi tiết của tất cả key."""
    danh_sach = _lay_danh_sach_key(chu_so_huu)
    if not danh_sach:
        return []

    ket_qua = []
    for key in danh_sach:
        key_id = key.get("id", "")
        trang_thai = _lay_trang_thai_key(key_id)

        ket_qua.append({
            "key_id": key_id,
            "provider": key.get("provider", ""),
            "con_dung": kiem_tra_hoi_quota(key_id),
            "het_quota": trang_thai.get("het_quota", False),
            "thoi_gian_hoi": trang_thai.get("thoi_gian_hoi", 0),
            "loai_quota": trang_thai.get("loai_quota", ""),
        })

    return ket_qua


# ================================================================
# HÀM PHỤ: KIỂM TRA CÒN KEY NÀO KHÔNG
# ================================================================
def con_key_dung_duoc(chu_so_huu):
    """Kiểm tra còn key nào dùng được không."""
    return dem_key_con_dung(chu_so_huu) > 0


# ================================================================
# HÀM PHỤ: ĐỢI HỒI QUOTA GẦN NHẤT
# ================================================================
def thoi_gian_hoi_gan_nhat(chu_so_huu):
    """
    Tính thời gian chờ đến khi key gần nhất hồi quota.
    Trả về số giây hoặc None nếu tất cả đã hồi.
    """
    danh_sach = _lay_danh_sach_key(chu_so_huu)
    if not danh_sach:
        return None

    thoi_gian_min = None
    now = int(time.time())

    for key in danh_sach:
        key_id = key.get("id", "")
        trang_thai = _lay_trang_thai_key(key_id)

        if not trang_thai.get("het_quota"):
            return 0  # có key dùng được ngay

        thoi_gian_hoi = trang_thai.get("thoi_gian_hoi", 0)
        if thoi_gian_hoi:
            con_lai = max(0, thoi_gian_hoi - now)
            if thoi_gian_min is None or con_lai < thoi_gian_min:
                thoi_gian_min = con_lai

    return thoi_gian_min
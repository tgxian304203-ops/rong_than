"""
xoay_api.py - Quản lý xoay API Tra web Rồng Thần.

Nhiệm vụ:
    - xoay_api(chu_so_huu): chuyển sang API tra web tiếp theo.
    - api_tiep_theo(danh_sach_api, api_hien_tai): tìm API kế tiếp.
    - danh_dau_het_quota(provider, key_id): đánh dấu API hết quota.
    - kiem_tra_hoi_quota(provider, key_id): kiểm tra API đã hồi quota chưa.
    - xoay_vong(danh_sach_api): xoay vòng danh sách API.

Quy tắc (theo Phần 4):
    - Khi API hết quota → nhảy sang API tiếp theo.
    - Thứ tự: SERPJET → Tavily → Bright Data.
    - Hết tất cả → quay lại API #1 nếu hồi quota.
    - Quota hồi đầu tháng (reset ngày 1).
    - Không lưu kết quả vào cây.

Trả về:
    - api_tiep_theo() → dict api_info hoặc None.
    - kiem_tra_hoi_quota() → True/False.

Tầng dữ liệu: dai_nao/ghi_nho.py (kho 2)
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
THU_TU_API = ["SERPJET", "Tavily", "Bright Data"]

# Quota mặc định mỗi API (reset ngày 1 hàng tháng)
QUOTA_MAC_DINH = {
    "SERPJET": 1000,
    "Tavily": 1000,
    "Bright Data": 5000,
}


# ================================================================
# ĐỌC / GHI KHO 2
# ================================================================
def _collection_trang_thai():
    """Collection lưu trạng thái API tra web."""
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        return db["trang_thai_api_tra_web"]
    except Exception:
        return None


# ================================================================
# LẤY DANH SÁCH API
# ================================================================
def _lay_danh_sach_api(chu_so_huu):
    """Lấy danh sách API tra web của tài khoản."""
    if not chu_so_huu:
        return []

    try:
        from dai_nao.ghi_nho import lay_danh_sach_key_web_cua
        danh_sach_key = lay_danh_sach_key_web_cua(chu_so_huu) or []
    except ImportError:
        return []
    except Exception:
        return []

    ket_qua = []
    for key in danh_sach_key:
        provider = (key.get("provider") or "").strip()
        if provider in THU_TU_API:
            ket_qua.append(key)

    return ket_qua


# ================================================================
# ĐÁNH DẤU HẾT QUOTA
# ================================================================
def danh_dau_het_quota(provider, key_id=""):
    """
    Đánh dấu API hết quota.
    Quota reset đầu tháng → thời gian hồi = đầu tháng sau.
    """
    if not provider:
        return False

    col = _collection_trang_thai()
    if col is None:
        return False

    # Tính thời gian hồi = đầu tháng sau
    now = time.localtime()
    thang_sau = now.tm_mon + 1
    nam_sau = now.tm_year
    if thang_sau > 12:
        thang_sau = 1
        nam_sau += 1

    # Ngày 1 tháng sau, 00:00
    thoi_gian_hoi = int(time.mktime((
        nam_sau, thang_sau, 1, 0, 0, 0, 0, 0, -1
    )))

    try:
        col.update_one(
            {"provider": provider, "key_id": key_id},
            {
                "$set": {
                    "provider": provider,
                    "key_id": key_id,
                    "het_quota": True,
                    "thoi_gian_het": int(time.time()),
                    "thoi_gian_hoi": thoi_gian_hoi,
                }
            },
            upsert=True,
        )
        _ghi_log("tra-web", f"Đánh dấu {provider} hết quota.")
        return True
    except Exception:
        return False


# ================================================================
# KIỂM TRA HỒI QUOTA
# ================================================================
def kiem_tra_hoi_quota(provider, key_id=""):
    """
    Kiểm tra API đã hồi quota chưa.

    Trả về: True nếu đã hồi (dùng được), False nếu còn hết quota.
    """
    if not provider:
        return True

    col = _collection_trang_thai()
    if col is None:
        return True

    try:
        trang_thai = col.find_one({"provider": provider, "key_id": key_id})
        if not trang_thai:
            return True

        if not trang_thai.get("het_quota"):
            return True

        thoi_gian_hoi = trang_thai.get("thoi_gian_hoi", 0)
        if not thoi_gian_hoi:
            return True

        # Đã hồi
        if int(time.time()) >= thoi_gian_hoi:
            col.update_one(
                {"provider": provider, "key_id": key_id},
                {"$set": {"het_quota": False, "thoi_gian_hoi_phuc": int(time.time())}},
            )
            _ghi_log("tra-web", f"{provider} đã hồi quota.")
            return True

        return False
    except Exception:
        return True


# ================================================================
# TÌM API KẾ TIẾP
# ================================================================
def api_tiep_theo(danh_sach_api, api_hien_tai=""):
    """
    Tìm API kế tiếp trong danh sách.

    danh_sach_api: list api_info.
    api_hien_tai: tên provider hiện tại.

    Trả về: dict api_info hoặc None.
    """
    if not danh_sach_api:
        return None

    # Chuẩn hóa danh sách theo thứ tự ưu tiên
    danh_sach_sap_xep = []
    for provider in THU_TU_API:
        for api in danh_sach_api:
            if api.get("provider") == provider:
                danh_sach_sap_xep.append(api)

    # Không có api hiện tại → lấy api đầu còn dùng
    if not api_hien_tai:
        for api in danh_sach_sap_xep:
            if kiem_tra_hoi_quota(api.get("provider"), api.get("id", "")):
                return api
        return None

    # Tìm vị trí hiện tại
    vi_tri = -1
    for i, api in enumerate(danh_sach_sap_xep):
        if api.get("provider") == api_hien_tai:
            vi_tri = i
            break

    # Duyệt từ vị trí kế tiếp
    if vi_tri >= 0:
        for i in range(vi_tri + 1, len(danh_sach_sap_xep)):
            if kiem_tra_hoi_quota(danh_sach_sap_xep[i].get("provider"),
                                  danh_sach_sap_xep[i].get("id", "")):
                return danh_sach_sap_xep[i]

    # Hết danh sách → quay lại từ đầu
    for i in range(0, vi_tri if vi_tri >= 0 else len(danh_sach_sap_xep)):
        if kiem_tra_hoi_quota(danh_sach_sap_xep[i].get("provider"),
                              danh_sach_sap_xep[i].get("id", "")):
            _ghi_log("tra-web", "Hết API → quay lại từ đầu.")
            return danh_sach_sap_xep[i]

    return None


# ================================================================
# XOAY VÒNG DANH SÁCH
# ================================================================
def xoay_vong(danh_sach_api):
    """
    Xoay vòng danh sách API: API còn dùng lên đầu, API hết quota xuống cuối.
    """
    if not danh_sach_api:
        return []

    con_dung = []
    het_quota = []

    for api in danh_sach_api:
        provider = api.get("provider", "")
        key_id = api.get("id", "")
        if kiem_tra_hoi_quota(provider, key_id):
            con_dung.append(api)
        else:
            het_quota.append(api)

    return con_dung + het_quota


# ================================================================
# HÀM CHÍNH
# ================================================================
def xoay_api(chu_so_huu, api_hien_tai=""):
    """
    Chuyển sang API tra web tiếp theo.

    chu_so_huu: tên đăng nhập.
    api_hien_tai: tên provider hiện tại.

    Trả về: dict api_info hoặc None nếu không còn API nào.
    """
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        _ghi_log("tra-web", f"Không có API tra web cho {chu_so_huu}.")
        return None

    # Xoay vòng
    danh_sach_moi = xoay_vong(danh_sach)

    # Tìm API kế tiếp
    api_tiep = api_tiep_theo(danh_sach_moi, api_hien_tai)

    if api_tiep:
        _ghi_log(
            "tra-web",
            f"Xoay sang API: {api_tiep.get('provider')}",
        )

    return api_tiep


# ================================================================
# HÀM PHỤ: ĐẾM API CÒN DÙNG
# ================================================================
def dem_api_con_dung(chu_so_huu):
    """Đếm số API tra web còn dùng được."""
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return 0

    dem = 0
    for api in danh_sach:
        if kiem_tra_hoi_quota(api.get("provider"), api.get("id", "")):
            dem += 1
    return dem


# ================================================================
# HÀM PHỤ: ĐẾM API HẾT QUOTA
# ================================================================
def dem_api_het_quota(chu_so_huu):
    """Đếm số API đang hết quota."""
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return 0

    dem = 0
    for api in danh_sach:
        if not kiem_tra_hoi_quota(api.get("provider"), api.get("id", "")):
            dem += 1
    return dem


# ================================================================
# HÀM PHỤ: XÓA TRẠNG THÁI
# ================================================================
def xoa_trang_thai(provider, key_id=""):
    """Xóa trạng thái hết quota của API."""
    col = _collection_trang_thai()
    if col is None:
        return False

    try:
        col.delete_one({"provider": provider, "key_id": key_id})
        return True
    except Exception:
        return False


def reset_tat_ca(chu_so_huu):
    """Reset trạng thái tất cả API tra web của tài khoản."""
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return False

    for api in danh_sach:
        xoa_trang_thai(api.get("provider"), api.get("id", ""))

    _ghi_log("tra-web", f"Reset trạng thái API tra web cho {chu_so_huu}")
    return True


# ================================================================
# HÀM PHỤ: TÓM TẮT TRẠNG THÁI
# ================================================================
def tom_tat_trang_thai(chu_so_huu):
    """Tạo chuỗi tóm tắt trạng thái API."""
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return "❌ Không có API tra web."

    phan = []
    for api in danh_sach:
        provider = api.get("provider", "")
        key_id = api.get("id", "")[:8]
        con_dung = kiem_tra_hoi_quota(provider, api.get("id", ""))
        bieu_tuong = "✅" if con_dung else "⏸️"
        phan.append(f"{bieu_tuong} {provider} / {key_id}")

    return "\n".join(phan)


# ================================================================
# HÀM PHỤ: THỜI GIAN HỒI GẦN NHẤT
# ================================================================
def thoi_gian_hoi_gan_nhat(chu_so_huu):
    """
    Tính thời gian chờ đến khi API gần nhất hồi quota.

    Trả về: số giây hoặc None.
    """
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return None

    col = _collection_trang_thai()
    if col is None:
        return None

    thoi_gian_min = None
    now = int(time.time())

    for api in danh_sach:
        provider = api.get("provider")
        key_id = api.get("id", "")

        if kiem_tra_hoi_quota(provider, key_id):
            return 0  # có API dùng được ngay

        try:
            trang_thai = col.find_one({"provider": provider, "key_id": key_id})
            if not trang_thai:
                continue
            thoi_gian_hoi = trang_thai.get("thoi_gian_hoi", 0)
            if thoi_gian_hoi:
                con_lai = max(0, thoi_gian_hoi - now)
                if thoi_gian_min is None or con_lai < thoi_gian_min:
                    thoi_gian_min = con_lai
        except Exception:
            continue

    return thoi_gian_min


# ================================================================
# HÀM PHỤ: LẤY TRẠNG THÁI CHI TIẾT
# ================================================================
def lay_trang_thai_chi_tiet(chu_so_huu):
    """Lấy trạng thái chi tiết các API tra web."""
    danh_sach = _lay_danh_sach_api(chu_so_huu)
    if not danh_sach:
        return []

    col = _collection_trang_thai()

    ket_qua = []
    for api in danh_sach:
        provider = api.get("provider", "")
        key_id = api.get("id", "")

        trang_thai = {}
        if col is not None:
            try:
                trang_thai = col.find_one({"provider": provider, "key_id": key_id}) or {}
            except Exception:
                trang_thai = {}

        ket_qua.append({
            "provider": provider,
            "key_id": key_id,
            "con_dung": kiem_tra_hoi_quota(provider, key_id),
            "het_quota": trang_thai.get("het_quota", False),
            "thoi_gian_hoi": trang_thai.get("thoi_gian_hoi", 0),
        })

    return ket_qua


# ================================================================
# HÀM PHỤ: DANH SÁCH API HỖ TRỢ
# ================================================================
def danh_sach_api_ho_tro():
    """Trả danh sách 3 API tra web."""
    return list(THU_TU_API)


def quota_mac_dinh(provider):
    """Trả quota mặc định của API."""
    return QUOTA_MAC_DINH.get(provider, 0)
"""
het_quota.py - Xử lý khi hết quota Rồng Thần.

Nhiệm vụ:
    - xu_ly_het_quota(chu_so_huu): xử lý khi tất cả key hết quota.
    - kiem_tra_con_quota(chu_so_huu): kiểm tra còn key nào dùng được không.
    - doi_hoi_quota(chu_so_huu, toi_da_giay=60): đợi key hồi quota.
    - thong_bao_het_quota(chu_so_huu): tạo thông báo cho user.
    - de_xuat_giai_phap(chu_so_huu): đề xuất giải pháp khi hết quota.

Quy tắc (theo Phần 4):
    - Khi tất cả key hết quota → không gọi được model.
    - Đợi key hồi quota (RPM: 1 phút, RPD: 24 giờ).
    - Nếu chờ quá lâu → thông báo user.
    - Gợi ý thêm key hoặc chờ.

Trả về:
    - xu_ly_het_quota() → dict { hanh_dong, thoi_gian_cho, thong_bao }.
    - kiem_tra_con_quota() → True/False.

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
THOI_GIAN_CHO_TOI_DA = 60       # giây — tối đa đợi trong 1 lần
THOI_GIAN_CHO_NGAN = 5          # giây — chờ ngắn giữa các lần thử


# ================================================================
# KIỂM TRA CÒN QUOTA
# ================================================================
def kiem_tra_con_quota(chu_so_huu):
    """
    Kiểm tra còn key nào dùng được không.

    Trả về: True nếu còn ít nhất 1 key chưa hết quota.
    """
    try:
        from tieu_nao.xoay_key import dem_key_con_dung
        return dem_key_con_dung(chu_so_huu) > 0
    except ImportError:
        return False


def dem_key_con_dung(chu_so_huu):
    """Đếm số key còn dùng được."""
    try:
        from tieu_nao.xoay_key import dem_key_con_dung as dem
        return dem(chu_so_huu)
    except ImportError:
        return 0


# ================================================================
# ĐỢI HỒI QUOTA
# ================================================================
def doi_hoi_quota(chu_so_huu, toi_da_giay=THOI_GIAN_CHO_TOI_DA):
    """
    Đợi key hồi quota.

    chu_so_huu: tên đăng nhập.
    toi_da_giay: thời gian chờ tối đa (giây).

    Trả về: True nếu có key hồi trong thời gian chờ.
    """
    if not chu_so_huu:
        return False

    thoi_gian_bat_dau = time.time()

    while time.time() - thoi_gian_bat_dau < toi_da_giay:
        # Kiểm tra còn key không
        if kiem_tra_con_quota(chu_so_huu):
            _ghi_log("tieu-nao", "Đã có key hồi quota.")
            return True

        # Đợi 1 chút
        time.sleep(THOI_GIAN_CHO_NGAN)

    _ghi_log("tieu-nao", f"Chờ {toi_da_giay}s nhưng chưa có key hồi.")
    return False


# ================================================================
# TÍNH THỜI GIAN CHỜ GẦN NHẤT
# ================================================================
def tinh_thoi_gian_cho(chu_so_huu):
    """
    Tính thời gian chờ đến khi key gần nhất hồi quota.

    Trả về: số giây hoặc None.
    """
    try:
        from tieu_nao.xoay_key import thoi_gian_hoi_gan_nhat
        return thoi_gian_hoi_gan_nhat(chu_so_huu)
    except ImportError:
        return None


# ================================================================
# TẠO THÔNG BÁO
# ================================================================
def thong_bao_het_quota(chu_so_huu):
    """
    Tạo thông báo hết quota cho user.

    Trả về: chuỗi thông báo.
    """
    phan = []
    phan.append("⏸️ **Tất cả key đã hết quota.**")

    # Thời gian chờ gần nhất
    thoi_gian_cho = tinh_thoi_gian_cho(chu_so_huu)
    if thoi_gian_cho is not None:
        if thoi_gian_cho <= 0:
            phan.append("→ Đã có key hồi, thử lại ngay.")
        elif thoi_gian_cho < 60:
            phan.append(f"→ Còn khoảng {thoi_gian_cho} giây nữa.")
        elif thoi_gian_cho < 3600:
            phut = thoi_gian_cho // 60
            phan.append(f"→ Còn khoảng {phut} phút nữa.")
        else:
            gio = thoi_gian_cho // 3600
            phan.append(f"→ Còn khoảng {gio} giờ nữa.")

    # Đếm key
    so_con_dung = dem_key_con_dung(chu_so_huu)
    phan.append(f"\n📊 Key còn dùng được: {so_con_dung}")

    return "\n".join(phan)


# ================================================================
# ĐỀ XUẤT GIẢI PHÁP
# ================================================================
def de_xuat_giai_phap(chu_so_huu):
    """
    Đề xuất giải pháp khi hết quota.

    Trả về: list gợi ý.
    """
    goi_y = []

    # Đếm key hiện có
    so_key = 0
    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        kiem_ke = kiem_ke_key(chu_so_huu)
        if kiem_ke.get("thanh_cong"):
            so_key = kiem_ke.get("tong_key", 0)
    except ImportError:
        pass

    # Nếu ít key → gợi ý thêm key
    if so_key == 0:
        goi_y.append("📌 Bạn chưa dán key nào. Vào Cài đặt → Key để dán.")
    elif so_key < 3:
        goi_y.append(f"📌 Bạn chỉ có {so_key} key. Nên thêm key từ "
                     "Groq/OpenRouter/Gemini để tăng quota.")
    else:
        goi_y.append("📌 Bạn đã có nhiều key. Chờ key hồi quota.")

    # Gợi ý theo provider
    goi_y.append("💡 Groq: 30 request/phút, 1.000 request/ngày.")
    goi_y.append("💡 OpenRouter: 20 request/phút (chưa nạp $10).")
    goi_y.append("💡 Gemini: Quota khá rộng, dùng model flash.")

    # Gợi ý chờ
    thoi_gian_cho = tinh_thoi_gian_cho(chu_so_huu)
    if thoi_gian_cho and thoi_gian_cho > 0:
        if thoi_gian_cho < 60:
            goi_y.append(f"⏳ Chờ {thoi_gian_cho} giây rồi thử lại.")
        elif thoi_gian_cho < 3600:
            goi_y.append(f"⏳ Chờ {thoi_gian_cho // 60} phút rồi thử lại.")
        else:
            goi_y.append(f"⏳ Chờ {thoi_gian_cho // 3600} giờ rồi thử lại.")

    return goi_y


# ================================================================
# HÀM CHÍNH
# ================================================================
def xu_ly_het_quota(chu_so_huu, cho_phep_doi=True):
    """
    Xử lý khi hết quota.

    chu_so_huu: tên đăng nhập.
    cho_phep_doi: có được đợi key hồi không.

    Trả về dict:
        {
            thanh_cong: bool,
            hanh_dong: "co_key" | "cho_duoc" | "bao_user" | "loi",
            thoi_gian_cho: int,
            thong_bao: str,
            goi_y: list,
        }
    """
    ket_qua = {
        "thanh_cong": False,
        "hanh_dong": "",
        "thoi_gian_cho": 0,
        "thong_bao": "",
        "goi_y": [],
    }

    if not chu_so_huu:
        ket_qua["hanh_dong"] = "loi"
        ket_qua["thong_bao"] = "Thiếu tên tài khoản."
        return ket_qua

    # 1. Kiểm tra còn key không
    if kiem_tra_con_quota(chu_so_huu):
        ket_qua["thanh_cong"] = True
        ket_qua["hanh_dong"] = "co_key"
        ket_qua["thong_bao"] = "Còn key dùng được."
        return ket_qua

    # 2. Thử đợi nếu cho phép
    if cho_phep_doi:
        thoi_gian_cho = tinh_thoi_gian_cho(chu_so_huu)
        if thoi_gian_cho is not None and thoi_gian_cho <= THOI_GIAN_CHO_TOI_DA:
            _ghi_log(
                "tieu-nao",
                f"Đợi {thoi_gian_cho}s để key hồi quota.",
            )
            if doi_hoi_quota(chu_so_huu, min(thoi_gian_cho + 5, THOI_GIAN_CHO_TOI_DA)):
                ket_qua["thanh_cong"] = True
                ket_qua["hanh_dong"] = "cho_duoc"
                ket_qua["thoi_gian_cho"] = thoi_gian_cho
                ket_qua["thong_bao"] = "Đã hồi quota."
                return ket_qua

    # 3. Không đợi được → báo user
    ket_qua["hanh_dong"] = "bao_user"
    ket_qua["thong_bao"] = thong_bao_het_quota(chu_so_huu)
    ket_qua["goi_y"] = de_xuat_giai_phap(chu_so_huu)
    ket_qua["thoi_gian_cho"] = tinh_thoi_gian_cho(chu_so_huu) or 0

    _ghi_log("tieu-nao", f"Hết quota cho {chu_so_huu} → báo user.")
    return ket_qua


# ================================================================
# HÀM PHỤ: TÓM TẮT
# ================================================================
def tom_tat(chu_so_huu):
    """Tạo chuỗi tóm tắt tình trạng quota."""
    so_key = 0
    so_con_dung = 0
    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        kiem_ke = kiem_ke_key(chu_so_huu)
        if kiem_ke.get("thanh_cong"):
            so_key = kiem_ke.get("tong_key", 0)
            so_con_dung = dem_key_con_dung(chu_so_huu)
    except ImportError:
        pass

    phan = [f"📊 Tổng key: {so_key}, còn dùng: {so_con_dung}"]

    thoi_gian_cho = tinh_thoi_gian_cho(chu_so_huu)
    if thoi_gian_cho is not None and thoi_gian_cho > 0:
        phan.append(f"⏳ Chờ gần nhất: {thoi_gian_cho}s")

    return "\n".join(phan)


# ================================================================
# HÀM PHỤ: ĐẾM KEY THEO TRẠNG THÁI
# ================================================================
def dem_key_theo_trang_thai(chu_so_huu):
    """Đếm key theo trạng thái."""
    ket_qua = {"con_dung": 0, "het_quota": 0, "tong": 0}

    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        from tieu_nao.xoay_key import kiem_tra_hoi_quota

        kiem_ke = kiem_ke_key(chu_so_huu)
        if not kiem_ke.get("thanh_cong"):
            return ket_qua

        for key in kiem_ke.get("thu_tu_goi", []):
            ket_qua["tong"] += 1
            key_id = key.get("id", "")
            if kiem_tra_hoi_quota(key_id):
                ket_qua["con_dung"] += 1
            else:
                ket_qua["het_quota"] += 1

    except ImportError:
        pass

    return ket_qua


# ================================================================
# HÀM PHỤ: KIỂM TRA SẮP HẾT QUOTA
# ================================================================
def sap_het_quota(chu_so_huu, nguong=20):
    """
    Kiểm tra có key nào sắp hết quota không (< nguong%).

    Trả về: list key sắp hết.
    """
    ket_qua = []

    try:
        from tieu_nao.quan_ly_quota import lay_quota_chi_tiet
        chi_tiet = lay_quota_chi_tiet(chu_so_huu)

        for provider, danh_sach in chi_tiet.items():
            for kq in danh_sach:
                phan_tram = kq.get("phan_tram")
                if phan_tram is not None and phan_tram < nguong:
                    ket_qua.append(kq)

    except ImportError:
        pass

    return ket_qua


# ================================================================
# HÀM PHỤ: CẢNH BÁO SẮP HẾT QUOTA
# ================================================================
def canh_bao_sap_het(chu_so_huu):
    """Tạo cảnh báo nếu có key sắp hết quota."""
    ds_sap_het = sap_het_quota(chu_so_huu)
    if not ds_sap_het:
        return ""

    phan = ["⚠️ Key sắp hết quota:"]
    for kq in ds_sap_het:
        phan.append(
            f"  - {kq.get('provider')} / {kq.get('key_id', '')[:8]}: "
            f"{kq.get('phan_tram')}%"
        )

    return "\n".join(phan)
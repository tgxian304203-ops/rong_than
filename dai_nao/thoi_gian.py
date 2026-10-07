"""
thoi_gian.py - Xử lý câu hỏi thời gian Rồng Thần.

Nhiệm vụ:
    - Nhan dien cau hoi thoi gian.
    - Nhom 1: gio Viet Nam -> tra loi ngay bang Python (UTC+7).
    - Nhom 2: gio khu vuc khac -> goi Tra web.

ĐÃ SỬA:
    - LỖI A: Truyền chu_so_huu vào goi_tra_web để lấy đúng key.
    - LỖI A: Lấy tom_tat (chuỗi) từ dict goi_tra_web, không in dict thô.

Quy tắc:
    - Chỉ xử lý khi câu hỏi THUẦN về thời gian.
    - Câu hỏi thời gian tương lai/quá khứ → không xử lý (trả None).
    - Mọi hàm đều có try/except, không sập luồng chính.

Trả về:
    - dict { thanh_cong, tra_loi, nguon } hoặc None nếu không xử lý.
"""

import re
from datetime import datetime, timedelta, timezone


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
MUI_GIO_VN = timezone(timedelta(hours=7))

THU_TRONG_TUAN = {
    0: "Thứ Hai",
    1: "Thứ Ba",
    2: "Thứ Tư",
    3: "Thứ Năm",
    4: "Thứ Sáu",
    5: "Thứ Bảy",
    6: "Chủ Nhật",
}

# Các từ khóa nhận diện câu hỏi thời gian VN
TU_KHOA_VN = [
    "hom nay", "hom qua", "ngay mai", "ngay kia", "ngay mot",
    "bay gio", "hien tai", "may gio", "gio hien tai",
    "ngay may", "thu may", "thang may", "nam may",
    "ngay bao nhieu", "thang bao nhieu", "nam bao nhieu",
    "thoi gian hien tai", "ngay gio hien tai",
    "cho toi biet ngay", "cho minh biet ngay", "cho tôi biết ngày",
    "bay gio la", "hom nay la",
]

# Các từ khóa nhận diện câu hỏi thời gian khu vực khác
TU_KHOA_KHU_VUC = [
    "o nhat", "ở nhật", "o my", "ở mỹ", "o anh", "ở anh",
    "o trung quoc", "ở trung quốc", "o han quoc", "ở hàn quốc",
    "o phap", "ở pháp", "o duc", "ở đức", "o uc", "ở úc",
    "o nga", "ở nga", "o thai lan", "ở thái lan",
    "o singapore", "ở singapore", "o malaysia", "ở malaysia",
    "o indonesia", "ở indonesia", "o philippines", "ở philippines",
    "o an do", "ở ấn độ", "o brazil", "ở brazil",
    "o canada", "ở canada", "o mexico", "ở mexico",
    "o y", "ở ý", "o tay ban nha", "ở tây ban nha",
    "o hoa ky", "ở hoa kỳ", "o uae", "ở uae",
    "o ai cap", "ở ai cập", "o nam phi", "ở nam phi",
]

# Các từ khóa loại trừ (không phải hỏi thời gian thực tế)
TU_KHOA_LOAI_TRU = [
    "thoi tiet", "thời tiết", "mua", "mưa", "nang", "nắng",
    "bao", "bão", "nhiet do", "nhiệt độ",
    "gia", "giá", "lich su", "lịch sử",
    "nam 20", "nam 19", "năm 20", "năm 19",
    "tuong lai", "tương lai", "qua khu", "quá khứ",
]


# ================================================================
# TIỆN ÍCH
# ================================================================
def _bo_dau(s):
    """Bỏ dấu tiếng Việt đơn giản."""
    if not s:
        return ""
    bang = {
        "a": "a", "á": "a", "à": "a", "ả": "a", "ã": "a", "ạ": "a",
        "ă": "a", "ắ": "a", "ằ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
        "â": "a", "ấ": "a", "ầ": "a", "ẩ": "a", "ẫ": "a", "ậ": "a",
        "e": "e", "é": "e", "è": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
        "ê": "e", "ế": "e", "ề": "e", "ể": "e", "ễ": "e", "ệ": "e",
        "i": "i", "í": "i", "ì": "i", "ỉ": "i", "ĩ": "i", "ị": "i",
        "o": "o", "ó": "o", "ò": "o", "ỏ": "o", "õ": "o", "ọ": "o",
        "ô": "o", "ố": "o", "ồ": "o", "ổ": "o", "ỗ": "o", "ộ": "o",
        "ơ": "o", "ớ": "o", "ờ": "o", "ở": "o", "ỡ": "o", "ợ": "o",
        "u": "u", "ú": "u", "ù": "u", "ủ": "u", "ũ": "u", "ụ": "u",
        "ư": "u", "ứ": "u", "ừ": "u", "ử": "u", "ữ": "u", "ự": "u",
        "y": "y", "ý": "y", "ỳ": "y", "ỷ": "y", "ỹ": "y", "ỵ": "y",
        "d": "d", "đ": "d",
    }
    ket_qua = []
    for c in s.lower():
        ket_qua.append(bang.get(c, c))
    return "".join(ket_qua)


def _co_tu_khoa(noi_dung, danh_sach):
    """Kiểm tra noi_dung có chứa bất kỳ từ khóa nào trong danh sách."""
    t = _bo_dau(noi_dung)
    for tk in danh_sach:
        tk_kd = _bo_dau(tk)
        if tk_kd in t:
            return True, tk
    return False, ""


# ================================================================
# NHẬN DIỆN
# ================================================================
def la_cau_hoi_thoi_gian(noi_dung):
    """
    Kiểm tra câu có phải câu hỏi thời gian không.

    Trả về: (True, "vn" | "khuvuc") hoặc (False, "")
    """
    if not noi_dung:
        return False, ""

    t = noi_dung.lower().strip()

    # Loại trừ trước
    co_loai_tru, _ = _co_tu_khoa(t, TU_KHOA_LOAI_TRU)
    if co_loai_tru:
        co_kv, _ = _co_tu_khoa(t, TU_KHOA_KHU_VUC)
        if co_kv:
            return True, "khuvuc"
        return False, ""

    # Kiểm tra khu vực khác trước
    co_kv, _ = _co_tu_khoa(t, TU_KHOA_KHU_VUC)
    if co_kv:
        return True, "khuvuc"

    # Kiểm tra VN
    co_vn, _ = _co_tu_khoa(t, TU_KHOA_VN)
    if co_vn:
        return True, "vn"

    # Kiểm tra mẫu câu đặc biệt
    if re.search(r"\b\d{1,2}\s*(gio|h)\b", t) and ("bay gio" in _bo_dau(t) or "hien tai" in _bo_dau(t)):
        return True, "vn"

    return False, ""


# ================================================================
# TRẢ LỜI THỜI GIAN VIỆT NAM
# ================================================================
def _lay_thoi_gian_vn():
    """Lấy thời gian hiện tại theo giờ VN (UTC+7)."""
    return datetime.now(MUI_GIO_VN)


def _dinh_dang_gio(now):
    """Định dạng: 'HH:MM'."""
    return now.strftime("%H:%M")


def _dinh_dang_ngay(now):
    """Định dạng: 'Thứ X, ngày DD/MM/YYYY'."""
    thu = THU_TRONG_TUAN.get(now.weekday(), "")
    return f"{thu}, ngày {now.strftime('%d/%m/%Y')}"


def _dinh_dang_day_du(now):
    """Định dạng: 'HH:MM, Thứ X ngày DD/MM/YYYY (giờ Việt Nam)'."""
    gio = _dinh_dang_gio(now)
    ngay = _dinh_dang_ngay(now)
    return f"{gio}, {ngay} (giờ Việt Nam)"


def tra_loi_thoi_gian_vn(noi_dung):
    """Trả lời câu hỏi thời gian VN bằng Python."""
    now = _lay_thoi_gian_vn()
    t = _bo_dau(noi_dung.lower())

    gio = _dinh_dang_gio(now)
    ngay = _dinh_dang_ngay(now)

    chi_gio = any(kw in t for kw in ["may gio", "gio may", "bay gio", "gio hien tai", "gio la"])
    chi_ngay = any(kw in t for kw in ["ngay may", "thu may", "hom nay", "hom qua", "ngay mai", "ngay kia"])
    chi_thang = "thang may" in t or "thang bao nhieu" in t
    chi_nam = "nam may" in t or "nam bao nhieu" in t
    chi_thang_nam = chi_thang and chi_nam

    if chi_gio and not chi_ngay:
        tra_loi = f"🕐 Bây giờ là {gio}, {ngay} (giờ Việt Nam)."
    elif chi_nam and not chi_thang:
        tra_loi = f"🗓️ Năm nay là năm {now.year}."
    elif chi_thang_nam:
        tra_loi = f"🗓️ Tháng này là tháng {now.month}, năm {now.year}."
    elif "hom qua" in t:
        hom_qua = now - timedelta(days=1)
        thu = THU_TRONG_TUAN.get(hom_qua.weekday(), "")
        tra_loi = f"Hôm qua là {thu}, ngày {hom_qua.strftime('%d/%m/%Y')}."
    elif "ngay mai" in t:
        ngay_mai = now + timedelta(days=1)
        thu = THU_TRONG_TUAN.get(ngay_mai.weekday(), "")
        tra_loi = f"Ngày mai là {thu}, ngày {ngay_mai.strftime('%d/%m/%Y')}."
    elif "ngay kia" in t:
        ngay_kia = now + timedelta(days=2)
        thu = THU_TRONG_TUAN.get(ngay_kia.weekday(), "")
        tra_loi = f"Ngày kia là {thu}, ngày {ngay_kia.strftime('%d/%m/%Y')}."
    else:
        tra_loi = f"🕐 Bây giờ là {gio}, {ngay} (giờ Việt Nam)."

    _ghi_log("dai-nao", f"Trả lời thời gian VN: {tra_loi}")

    return {
        "thanh_cong": True,
        "tra_loi": tra_loi,
        "nguon": "thoi_gian_vn",
    }


# ================================================================
# TRẢ LỜI THỜI GIAN KHU VỰC KHÁC (QUA TRA WEB)
# ================================================================
def _goi_tra_web(cau_hoi, chu_so_huu=""):
    """
    Gọi Tra web — SỬA LỖI A:
        - Truyền chu_so_huu để lấy đúng key tra web.
        - Lấy tom_tat (chuỗi) từ dict, không in dict thô.
    """
    try:
        from dai_nao.goi_tra_web import goi_tra_web
        ket_qua = goi_tra_web(cau_hoi, chu_so_huu)

        if not ket_qua or not ket_qua.get("thanh_cong"):
            _ghi_log("tra-web", f"Tra web thất bại: {ket_qua.get('loi', '') if ket_qua else 'rỗng'}")
            return ""

        # Lấy chuỗi tổng hợp
        tom_tat = ket_qua.get("tom_tat") or ""
        if tom_tat:
            return tom_tat

        # Fallback: tổng hợp từ danh sách
        danh_sach = ket_qua.get("ket_qua", [])
        return _tong_hop_don_gian(danh_sach)

    except ImportError:
        _ghi_log("loi", "goi_tra_web.py chưa có.")
        return ""
    except Exception as e:
        _ghi_log("loi", f"Tra web lỗi: {e}")
        return ""


def _tong_hop_don_gian(danh_sach):
    """Fallback tổng hợp nếu goi_tra_web không trả tom_tat."""
    if not danh_sach:
        return ""
    phan = []
    for i, item in enumerate(danh_sach[:5], 1):
        if not isinstance(item, dict):
            continue
        tieu_de = (item.get("tieu_de") or "").strip()
        mo_ta = (item.get("mo_ta") or "").strip()
        url = (item.get("url") or "").strip()
        dong = f"{i}. {tieu_de}" if tieu_de else f"{i}."
        if mo_ta:
            dong += f"\n   {mo_ta[:300]}"
        if url:
            dong += f"\n   🔗 {url}"
        phan.append(dong)
    return "\n\n".join(phan)


def tra_loi_thoi_gian_khu_vuc(noi_dung, chu_so_huu=""):
    """
    Trả lời câu hỏi thời gian khu vực khác qua Tra web.
    Kèm giờ VN để so sánh.

    SỬA LỖI A: Nhận chu_so_huu, truyền xuống _goi_tra_web.
    """
    now_vn = _lay_thoi_gian_vn()
    gio_vn = _dinh_dang_gio(now_vn)

    # Gọi tra web (truyền chu_so_huu)
    ket_qua_web = _goi_tra_web(noi_dung, chu_so_huu)

    if not ket_qua_web:
        # Không tra được → trả lời giờ VN + xin lỗi
        _ghi_log("tra-web", f"Tra web thất bại cho câu hỏi: {noi_dung[:80]}")
        return {
            "thanh_cong": True,
            "tra_loi": f"🕐 Ta chưa tra cứu được giờ khu vực bạn hỏi. "
                       f"Bây giờ ở Việt Nam là {gio_vn}.",
            "nguon": "thoi_gian_khuvuc_fallback",
        }

    # Tra web thành công → thêm giờ VN
    tra_loi = f"{ket_qua_web}\n\n🕐 Để so sánh, bây giờ ở Việt Nam là {gio_vn}."

    _ghi_log("tra-web", f"Trả lời thời gian khu vực: {tra_loi[:100]}")

    return {
        "thanh_cong": True,
        "tra_loi": tra_loi,
        "nguon": "thoi_gian_khuvuc",
    }


# ================================================================
# HÀM CHÍNH — ĐIỂM VÀO
# ================================================================
def xu_ly_cau_hoi_thoi_gian(noi_dung, chu_so_huu=""):
    """
    Điểm vào chính — xử lý câu hỏi thời gian.

    SỬA LỖI A: Nhận chu_so_huu, truyền xuống nhánh khu vực.

    Trả về:
        - dict { thanh_cong, tra_loi, nguon } nếu xử lý được.
        - None nếu không phải câu hỏi thời gian.
    """
    if not noi_dung:
        return None

    la_thoi_gian, loai = la_cau_hoi_thoi_gian(noi_dung)

    if not la_thoi_gian:
        return None

    if loai == "vn":
        return tra_loi_thoi_gian_vn(noi_dung)
    elif loai == "khuvuc":
        return tra_loi_thoi_gian_khu_vuc(noi_dung, chu_so_huu)

    return None


# ================================================================
# TIỆN ÍCH XUẤT
# ================================================================
def lay_gio_vn():
    """Trả về chuỗi giờ VN hiện tại."""
    return _dinh_dang_gio(_lay_thoi_gian_vn())


def lay_ngay_vn():
    """Trả về chuỗi ngày VN hiện tại."""
    return _dinh_dang_ngay(_lay_thoi_gian_vn())


def lay_day_du_vn():
    """Trả về chuỗi đầy đủ (giờ + ngày) VN."""
    return _dinh_dang_day_du(_lay_thoi_gian_vn())
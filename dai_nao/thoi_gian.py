"""
thoi_gian.py - Xử lý câu hỏi thời gian Rồng Thần.

Nhiệm vụ:
    - Nhan dien cau hoi thoi gian.
    - Nhom 1: gio Viet Nam -> tra loi ngay bang Python (UTC+7).
    - Nhom 2: gio khu vuc khac -> goi Tra web.

Quy tac:
    - Chi xu ly khi cau hoi THUAN ve thoi gian.
    - Cau hoi thoi gian tuong lai/qua khu -> khong xu ly (tra None).
    - Moi ham deu co try/except, khong sap luong chinh.

Tra ve:
    - dict { thanh_cong, tra_loi, nguon } hoac None neu khong xu ly.
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
# HANG SO
# ================================================================
MUI_GIO_VN = timezone(timedelta(hours=7))

THU_TRONG_TUAN = {
    0: "Thu Hai",
    1: "Thu Ba",
    2: "Thu Tu",
    3: "Thu Nam",
    4: "Thu Sau",
    5: "Thu Bay",
    6: "Chu Nhat",
}

# Cac tu khoa nhan dien cau hoi thoi gian VN
TU_KHOA_VN = [
    "hom nay", "hom qua", "ngay mai", "ngay kia", "ngay mot",
    "bay gio", "hien tai", "may gio", "gio hien tai",
    "ngay may", "thu may", "thang may", "nam may",
    "ngay bao nhieu", "thang bao nhieu", "nam bao nhieu",
    "thoi gian hien tai", "ngay gio hien tai",
    "cho toi biet ngay", "cho minh biet ngay", "cho tôi biết ngày",
    "bay gio la", "hom nay la",
]

# Cac tu khoa nhan dien cau hoi thoi gian khu vuc khac
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

# Cac tu khoa loai tru (khong phai hoi thoi gian thuc te)
TU_KHOA_LOAI_TRU = [
    "thoi tiet", "thời tiết", "mua", "mưa", "nang", "nắng",
    "bao", "bão", "nhiet do", "nhiệt độ",
    "gia", "giá", "lich su", "lịch sử",
    "nam 20", "nam 19", "năm 20", "năm 19",
    "tuong lai", "tương lai", "qua khu", "quá khứ",
]


# ================================================================
# TIEN ICH
# ================================================================
def _bo_dau(s):
    """Bo dau tieng Viet don gian."""
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
    """Kiem tra noi_dung co chua bat ky tu khoa nao trong danh sach."""
    t = _bo_dau(noi_dung)
    for tk in danh_sach:
        tk_kd = _bo_dau(tk)
        if tk_kd in t:
            return True, tk
    return False, ""


# ================================================================
# NHAN DIEN
# ================================================================
def la_cau_hoi_thoi_gian(noi_dung):
    """
    Kiem tra cau co phai cau hoi thoi gian khong.

    Tra ve: (True, "vn" | "khuvuc") hoac (False, "")
    """
    if not noi_dung:
        return False, ""

    t = noi_dung.lower().strip()

    # Loai tru truoc
    co_loai_tru, _ = _co_tu_khoa(t, TU_KHOA_LOAI_TRU)
    if co_loai_tru:
        # Van co the la cau hoi gio khu vuc
        co_kv, _ = _co_tu_khoa(t, TU_KHOA_KHU_VUC)
        if co_kv:
            return True, "khuvuc"
        return False, ""

    # Kiem tra khu vuc khac truoc
    co_kv, _ = _co_tu_khoa(t, TU_KHOA_KHU_VUC)
    if co_kv:
        return True, "khuvuc"

    # Kiem tra VN
    co_vn, _ = _co_tu_khoa(t, TU_KHOA_VN)
    if co_vn:
        return True, "vn"

    # Kiem tra mau cau dac biet
    if re.search(r"\b\d{1,2}\s*(gio|h)\b", t) and ("bay gio" in _bo_dau(t) or "hien tai" in _bo_dau(t)):
        return True, "vn"

    return False, ""


# ================================================================
# TRA LOI THOI GIAN VIET NAM
# ================================================================
def _lay_thoi_gian_vn():
    """Lay thoi gian hien tai theo gio VN (UTC+7)."""
    now = datetime.now(MUI_GIO_VN)
    return now


def _dinh_dang_gio(now):
    """Dinh dang: 'HH:MM'."""
    return now.strftime("%H:%M")


def _dinh_dang_ngay(now):
    """Dinh dang: 'Thu X, ngay DD/MM/YYYY'."""
    thu = THU_TRONG_TUAN.get(now.weekday(), "")
    return f"{thu}, ngay {now.strftime('%d/%m/%Y')}"


def _dinh_dang_day_du(now):
    """Dinh dang: 'HH:MM, Thu X ngay DD/MM/YYYY (gio Viet Nam)'."""
    gio = _dinh_dang_gio(now)
    ngay = _dinh_dang_ngay(now)
    return f"{gio}, {ngay} (gio Viet Nam)"


def tra_loi_thoi_gian_vn(noi_dung):
    """
    Tra loi cau hoi thoi gian VN bang Python.

    Tra ve dict { thanh_cong, tra_loi, nguon }.
    """
    now = _lay_thoi_gian_vn()
    t = _bo_dau(noi_dung.lower())

    gio = _dinh_dang_gio(now)
    ngay = _dinh_dang_ngay(now)

    # Xac dinh dang cau hoi
    chi_gio = any(kw in t for kw in ["may gio", "gio may", "bay gio", "gio hien tai", "gio la"])
    chi_ngay = any(kw in t for kw in ["ngay may", "thu may", "hom nay", "hom qua", "ngay mai", "ngay kia"])
    chi_thang = "thang may" in t or "thang bao nhieu" in t
    chi_nam = "nam may" in t or "nam bao nhieu" in t
    chi_thang_nam = chi_thang and chi_nam

    if chi_gio and not chi_ngay:
        tra_loi = f"🕐 Bay gio la {gio}, {ngay} (gio Viet Nam)."
    elif chi_nam and not chi_thang:
        tra_loi = f"🗓️ Nam nay la nam {now.year}."
    elif chi_thang_nam:
        tra_loi = f"🗓️ Thang nay la thang {now.month}, nam {now.year}."
    elif "hom qua" in t:
        hom_qua = now - timedelta(days=1)
        thu = THU_TRONG_TUAN.get(hom_qua.weekday(), "")
        tra_loi = f"Hom qua la {thu}, ngay {hom_qua.strftime('%d/%m/%Y')}."
    elif "ngay mai" in t:
        ngay_mai = now + timedelta(days=1)
        thu = THU_TRONG_TUAN.get(ngay_mai.weekday(), "")
        tra_loi = f"Ngay mai la {thu}, ngay {ngay_mai.strftime('%d/%m/%Y')}."
    elif "ngay kia" in t:
        ngay_kia = now + timedelta(days=2)
        thu = THU_TRONG_TUAN.get(ngay_kia.weekday(), "")
        tra_loi = f"Ngay kia la {thu}, ngay {ngay_kia.strftime('%d/%m/%Y')}."
    else:
        # Mac dinh: tra loi day du
        tra_loi = f"🕐 Bay gio la {gio}, {ngay} (gio Viet Nam)."

    _ghi_log("dai-nao", f"Tra loi thoi gian VN: {tra_loi}")

    return {
        "thanh_cong": True,
        "tra_loi": tra_loi,
        "nguon": "thoi_gian_vn",
    }


# ================================================================
# TRA LOI THOI GIAN KHU VUC KHAC (QUA TRA WEB)
# ================================================================
def _goi_tra_web(cau_hoi):
    """Goi Tra web — import dong."""
    try:
        from dai_nao.goi_tra_web import goi_tra_web
        return goi_tra_web(cau_hoi) or ""
    except ImportError:
        return ""
    except Exception:
        return ""


def tra_loi_thoi_gian_khu_vuc(noi_dung):
    """
    Tra loi cau hoi thoi gian khu vuc khac qua Tra web.
    Kem gio VN de so sanh.

    Tra ve dict { thanh_cong, tra_loi, nguon }.
    """
    now_vn = _lay_thoi_gian_vn()
    gio_vn = _dinh_dang_gio(now_vn)

    # Goi tra web
    ket_qua_web = _goi_tra_web(noi_dung)

    if not ket_qua_web:
        # Khong tra duoc -> tra loi gio VN + xin loi
        _ghi_log("tra-web", f"Tra web that bai cho cau hoi: {noi_dung[:80]}")
        return {
            "thanh_cong": True,
            "tra_loi": f"🕐 Ta chua tra cuu duoc gio khu vuc ban hoi. "
                       f"Bay gio o Viet Nam la {gio_vn}.",
            "nguon": "thoi_gian_khuvuc_fallback",
        }

    # Tra web thanh cong -> them gio VN
    tra_loi = f"{ket_qua_web}\n\n🕐 De so sanh, bay gio o Viet Nam la {gio_vn}."

    _ghi_log("tra-web", f"Tra loi thoi gian khu vuc: {tra_loi[:100]}")

    return {
        "thanh_cong": True,
        "tra_loi": tra_loi,
        "nguon": "thoi_gian_khuvuc",
    }


# ================================================================
# HAM CHINH — DIEM VAO
# ================================================================
def xu_ly_cau_hoi_thoi_gian(noi_dung):
    """
    Diem vao chinh — xu ly cau hoi thoi gian.

    Tra ve:
        - dict { thanh_cong, tra_loi, nguon } neu xu ly duoc.
        - None neu khong phai cau hoi thoi gian.
    """
    if not noi_dung:
        return None

    la_thoi_gian, loai = la_cau_hoi_thoi_gian(noi_dung)

    if not la_thoi_gian:
        return None

    if loai == "vn":
        return tra_loi_thoi_gian_vn(noi_dung)
    elif loai == "khuvuc":
        return tra_loi_thoi_gian_khu_vuc(noi_dung)

    return None


# ================================================================
# TIEN ICH XUAT
# ================================================================
def lay_gio_vn():
    """Tra ve chuoi gio VN hien tai — tien cho module khac dung."""
    return _dinh_dang_gio(_lay_thoi_gian_vn())


def lay_ngay_vn():
    """Tra ve chuoi ngay VN hien tai."""
    return _dinh_dang_ngay(_lay_thoi_gian_vn())


def lay_day_du_vn():
    """Tra ve chuoi day du (gio + ngay) VN."""
    return _dinh_dang_day_du(_lay_thoi_gian_vn())
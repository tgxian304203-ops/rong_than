"""
chuan_hoa.py - Chuẩn hóa input Rồng Thần (10 bước, ký hiệu mạnh).

Nhiệm vụ:
    - chuan_hoa(noi_dung): chuẩn hóa câu người dùng theo 10 bước.

10 bước (theo Phần 4):
    1. Tách câu.
    2. Sửa viết tắt.
    3. Sửa chính tả (so khớp gần đúng > 90%).
    4. Sửa dấu tiếng Việt (dùng ngữ cảnh).
    5. Bỏ từ đệm (giữ "thì" trong "nếu... thì...").
    6. Sửa dấu câu + CHUẨN HÓA KÝ HIỆU MẠNH.
    7. Chuẩn hóa viết hoa.
    8. Kiểm tra lại (ý không đổi).
    9. Ghi log.
    10. Chuyển sang trích xuất 5 yếu tố (không làm ở file này).

CHUẨN HÓA KÝ HIỆU MẠNH (bổ sung):
    - Toán tử: × → *, : → /, ÷ → /, − → -, toàn giác → nửa giác.
    - Số mũ: ² → ^2, ³ → ^3, ⁿ → ^n.
    - Căn: √ → sqrt, ∛ → cbrt.
    - So sánh: ≠ → !=, ≤ → <=, ≥ → >=.
    - Ký hiệu toán: π → pi, ∞ → infinity, ∑ → sum, ∏ → product, ∫ → integral.
    - Đơn vị m² → m^2, m³ → m^3.
    - Tiền tệ: 50k → 50000, 2tr → 2000000, 2m → 2000000,
      50000đ → 50000 VND, $ → USD, € → EUR, ¥ → JPY, £ → GBP, ₫ → VND.
    - Ký tự lặp: ...,,,, !!!, ???, đượcccc, hayyyyy.
    - Dấu câu ngoại: 。 → ., 、 → ,, ！ → !, ？ → ?, ： → :, ； → ;.
    - Ngoặc cong: " " → ", ' ' → '.
    - Unicode điều khiển (zero-width, BOM) → bỏ.
    - Xuống dòng: \r\n → \n, tab → space.

KHÔNG xử lý:
    - && → and, || → or (giữ nguyên).
    - #1 → số 1 (giữ nguyên).
"""

import re
import unicodedata


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
# BƯỚC 2: BẢNG VIẾT TẮT (MỞ RỘNG)
# ================================================================
VIET_TAT = {
    # Viết tắt phổ biến
    "lm": "làm",
    "ko": "không", "k": "không", "hk": "không", "hok": "không",
    "dc": "được", "đc": "được", "đk": "được",
    "vs": "với",
    "wep": "web", "wed": "web",
    "j": "gì", "z": "gì",
    "ntn": "như thế nào", "nt": "như thế",
    "bn": "bao nhiêu", "bnhiu": "bao nhiêu",
    "mk": "mình", "mik": "mình",
    "nx": "nữa", "nua": "nữa",
    "cx": "cũng", "cg": "cũng",
    "bth": "bình thường", "bt": "biết",
    "tl": "trả lời", "trloi": "trả lời",
    "ib": "inbox", "inb": "inbox",
    "rep": "reply",
    "ng": "người",
    "nc": "nước",
    "qá": "quá", "wá": "quá", "wa": "quá",
    "r": "rồi", "rui": "rồi",
    "đg": "đang", "đag": "đang",
    "hj": "hình",
    "sp": "sản phẩm",
    "tk": "tài khoản",
    "nv": "nhân viên",
    "kh": "khách hàng",
    "ck": "chuyển khoản",
    "iu": "yêu",
    "a": "anh", "e": "em", "c": "chị",
    "n": "nó",
    "thik": "thích",
    "mún": "muốn",
    "bik": "biết",
    "zay": "vậy", "zậy": "vậy", "v": "vậy",
    "h": "giờ",
    "tks": "cảm ơn",
    "sr": "xin lỗi", "sorry": "xin lỗi",
    "oke": "ok", "okay": "ok",
    "nhìu": "nhiều", "nhiu": "nhiều",
    "khum": "không", "hum": "không",
    "hoy": "thôi", "thui": "thôi",
    "r đó": "rồi đó",
    "bùn": "buồn",
    "đượcccc": "được",
    # Viết tắt chat
    "stt": "status",
    "cmt": "comment",
    "zl": "zalo",
    "fb": "facebook",
    "ig": "instagram",
    "yt": "youtube",
    "tt": "tiktok",
    "nv2": "nhân viên",
    # Viết tắt tiếng Anh
    "pls": "please", "plz": "please",
    "thx": "thanks", "tks": "thanks",
    "btw": "by the way",
    "imo": "in my opinion",
    "idk": "i don't know",
    "omg": "oh my god",
    "lol": "laugh out loud",
    "wanna": "want to",
    "gonna": "going to",
    "gotta": "got to",
    "asap": "as soon as possible",
    "fyi": "for your information",
}


# ================================================================
# BƯỚC 4: BẢNG SỬA DẤU TIẾNG VIỆT (MỞ RỘNG)
# ================================================================
KHONG_DAU_SANG_CO_DAU = {
    # Động từ thông dụng
    "khong": "không",
    "duoc": "được",
    "lam": "làm",
    "muon": "muốn",
    "biet": "biết",
    "thich": "thích",
    "hoc": "học",
    "day": "dạy",
    "noi": "nói",
    "nghe": "nghe",
    "doc": "đọc",
    "viet": "viết",
    "gui": "gửi",
    "nhan": "nhận",
    "xem": "xem",
    "tim": "tìm",
    "giup": "giúp",
    "hoi": "hỏi",
    "tra_loi": "trả lời",
    "sua": "sửa",
    "tao": "tạo",
    "xoa": "xóa",
    "them": "thêm",
    "bo": "bỏ",
    "chay": "chạy",
    "dung": "dùng",  # có thể là "đúng" — dùng ngữ cảnh
    "mo": "mở",
    "dong": "đóng",
    "luu": "lưu",
    "nap": "nạp",
    "xuat": "xuất",
    "nhap": "nhập",
    "cai": "cài",
    "dat": "đặt",
    "lay": "lấy",
    "cho": "cho",
    "tra": "trả",
    "mua": "mua",
    "ban": "bán",
    "thanh_toan": "thanh toán",
    "mua_ban": "mua bán",

    # Danh từ thông dụng
    "nguoi": "người",
    "nuoc": "nước",
    "nha": "nhà",
    "duong": "đường",
    "xe": "xe",
    "may": "máy",
    "sach": "sách",
    "but": "bút",
    "vo": "vở",
    "bang": "bảng",
    "ghe": "ghế",
    "ban_ghe": "bàn ghế",
    "cua": "cửa",
    "cua_so": "cửa sổ",
    "tuong": "tường",
    "tran": "trần",
    "san": "sàn",
    "gac": "gác",
    "tang": "tầng",

    # Tính từ thông dụng
    "dep": "đẹp",
    "xau": "xấu",
    "tot": "tốt",
    "cao": "cao",
    "thap": "thấp",
    "dai": "dài",
    "ngan": "ngắn",
    "nong": "nóng",
    "lanh": "lạnh",
    "moi": "mới",
    "cu": "cũ",
    "tre": "trẻ",
    "gia": "già",
    "nhanh": "nhanh",
    "cham": "chậm",
    "manh": "mạnh",
    "yeu": "yếu",
    "khoe": "khỏe",
    "sai": "sai",
    "that": "thật",
    "gia_tao": "giả tạo",

    # Chuyên ngành toán
    "toan": "toán",
    "tinh": "tính",
    "tong": "tổng",
    "hieu": "hiệu",
    "tich": "tích",
    "thuong": "thương",
    "phan_so": "phân số",
    "tu_so": "tử số",
    "mau_so": "mẫu số",
    "luy_thua": "lũy thừa",
    "can_bac": "căn bậc",
    "phuong_trinh": "phương trình",
    "bat_phuong_trinh": "bất phương trình",
    "he_phuong_trinh": "hệ phương trình",
    "dao_ham": "đạo hàm",
    "tich_phan": "tích phân",
    "gioi_han": "giới hạn",
    "xac_suat": "xác suất",
    "trung_binh": "trung bình",

    # Chuyên ngành văn
    "doan_van": "đoạn văn",
    "bai_van": "bài văn",
    "tieu_luan": "tiểu luận",
    "phan_tich": "phân tích",
    "nghi_luan": "nghị luận",
    "tom_tat": "tóm tắt",
    "dich": "dịch",

    # Chuyên ngành code
    "lap_trinh": "lập trình",
    "ngon_ngu": "ngôn ngữ",
    "ham": "hàm",
    "thuat_toan": "thuật toán",
    "du_lieu": "dữ liệu",
    "loi": "lỗi",
    "sua_loi": "sửa lỗi",
    "toi_uu": "tối ưu",

    # Chuyên ngành khác
    "suc_khoe": "sức khỏe",
    "benh": "bệnh",
    "thuoc": "thuốc",
    "luat": "luật",
    "hop_dong": "hợp đồng",
    "thu_tuc": "thủ tục",
    "thue": "thuế",
}


# ================================================================
# BƯỚC 5: TỪ ĐỆM CẦN BỎ
# ================================================================
TU_DEM = [
    "ạ", "nhé", "nha", "nè", "nà", "đấy", "ấy", "đó", "hén", "hí",
    "hihi", "haha", "hehe", "kk", "kaka",
    "um", "uh", "uhm", "à", "ừ", "ờ", "ơ",
    "đi mà", "mà thôi",
]


# ================================================================
# BƯỚC 5: TỪ ĐỆM CẦN GIỮ
# ================================================================
TU_GIU = [
    "thì", "mà", "là", "và", "hoặc", "nhưng", "nếu", "vì", "nên",
    "của", "cho", "với", "bằng", "để", "khi", "sau", "trước",
]


# ================================================================
# CHUẨN HÓA KÝ HIỆU — BẢNG THAY THẾ
# ================================================================

# Toán tử cơ bản
TOAN_TU = {
    "×": "*",
    "✕": "*",
    "✖": "*",
    "⨯": "*",
    "⋅": "*",
    "·": "*",
    "÷": "/",
    "∕": "/",
    "⁄": "/",
    "−": "-",
    "–": "-",
    "—": "-",
    "﹣": "-",
    "＋": "+",
    "－": "-",
    "＊": "*",
    "／": "/",
    "％": "%",
    "＾": "^",
}

# Số mũ
SO_MU = {
    "⁰": "^0", "¹": "^1", "²": "^2", "³": "^3", "⁴": "^4",
    "⁵": "^5", "⁶": "^6", "⁷": "^7", "⁸": "^8", "⁹": "^9",
    "ⁿ": "^n",
    "₀": "_0", "₁": "_1", "₂": "_2", "₃": "_3", "₄": "_4",
    "₅": "_5", "₆": "_6", "₇": "_7", "₈": "_8", "₉": "_9",
    "ₙ": "_n",
}

# Căn
CAN = {
    "√": " sqrt ",
    "∛": " cbrt ",
    "∜": " root4 ",
}

# So sánh + ký hiệu toán
KY_HIEU_TOAN = {
    "≠": "!=",
    "≤": "<=",
    "≥": ">=",
    "≈": "~=",
    "≃": "~=",
    "≅": "~=",
    "±": "+-",
    "∓": "-+",
    "∞": "infinity",
    "π": "pi",
    "Π": "pi",
    "∑": "sum",
    "∏": "product",
    "∫": "integral",
    "∬": "double_integral",
    "∂": "partial",
    "∇": "nabla",
    "∈": "in",
    "∉": "not in",
    "⊂": "subset",
    "⊃": "superset",
    "∪": "union",
    "∩": "intersection",
    "∅": "empty",
    "∀": "for all",
    "∃": "exists",
    "¬": "not",
    "∧": "and",
    "∨": "or",
    "→": "->",
    "←": "<-",
    "↔": "<->",
    "⇒": "=>",
    "⇔": "<=>",
    "∴": "therefore",
    "∵": "because",
}

# Tiền tệ
TIEN_TE = {
    "$": " USD ",
    "€": " EUR ",
    "¥": " JPY ",
    "£": " GBP ",
    "₫": " VND ",
    "₩": " KRW ",
    "₽": " RUB ",
    "₹": " INR ",
    "₺": " TRY ",
    "฿": " THB ",
    "₱": " PHP ",
    "₪": " ILS ",
}

# Dấu câu ngoại (Trung, Nhật, Hàn)
DAU_CAU_NGOAI = {
    "。": ".",
    "、": ",",
    "！": "!",
    "？": "?",
    "：": ":",
    "；": ";",
    "（": "(",
    "）": ")",
    "【": "[",
    "】": "]",
    "「": "\"",
    "」": "\"",
    "『": "\"",
    "』": "\"",
    "《": "\"",
    "》": "\"",
    "，": ",",
}

# Ngoặc cong
NGOAC_CONG = {
    """: "\"",
    """: "\"",
    "'": "'",
    "'": "'",
    "‚": ",",
    "„": "\"",
    "‹": "<",
    "›": ">",
    "«": "<<",
    "»": ">>",
}


# ================================================================
# BƯỚC 1: TÁCH CÂU
# ================================================================
def _tach_cau(noi_dung):
    """Tách câu theo . ! ? và xuống dòng."""
    if not noi_dung:
        return []
    cac_cau = re.split(r"(?<=[.!?])\s+|\n+", noi_dung)
    return [c.strip() for c in cac_cau if c.strip()]


# ================================================================
# BƯỚC 2: SỬA VIẾT TẮT
# ================================================================
def _sua_viet_tat(noi_dung):
    """Sửa viết tắt — chỉ sửa khi từ đứng riêng."""
    if not noi_dung:
        return noi_dung
    cac_tu = noi_dung.split()
    ket_qua = []
    for tu in cac_tu:
        # Giữ dấu câu 2 đầu
        dau_dau, dau_cuoi = "", ""
        while tu and tu[0] in "\"'([{":
            dau_dau += tu[0]
            tu = tu[1:]
        while tu and tu[-1] in ".,!?;:)\"']}":
            dau_cuoi = tu[-1] + dau_cuoi
            tu = tu[:-1]

        tu_lower = tu.lower()
        if tu_lower in VIET_TAT:
            tu = VIET_TAT[tu_lower]
        ket_qua.append(dau_dau + tu + dau_cuoi)
    return " ".join(ket_qua)


# ================================================================
# BƯỚC 3: SỬA CHÍNH TẢ (LEVENSHTEIN)
# ================================================================
def _khoang_cach_levenshtein(a, b):
    """Tính khoảng cách Levenshtein giữa 2 chuỗi."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    hang_truoc = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        hang_hien_tai = [i]
        for j, cb in enumerate(b, 1):
            chen = hang_hien_tai[j - 1] + 1
            xoa = hang_truoc[j] + 1
            thay = hang_truoc[j - 1] + (0 if ca == cb else 1)
            hang_hien_tai.append(min(chen, xoa, thay))
        hang_truoc = hang_hien_tai
    return hang_truoc[-1]


def _sua_chinh_ta(noi_dung):
    """Sửa chính tả — chỉ sửa khi giống > 90%."""
    if not noi_dung:
        return noi_dung

    tu_dung = set(KHONG_DAU_SANG_CO_DAU.values()) | {
        "làm", "không", "được", "với", "web", "hàng", "gì",
        "như thế nào", "bao nhiêu", "mình", "nữa", "cũng",
        "bình thường", "biết", "trả lời", "người", "nước",
        "quá", "rồi", "đang", "sẽ", "sản phẩm", "tài khoản",
        "mật khẩu", "nhân viên", "khách hàng", "chuyển khoản",
        "tiền", "yêu", "anh", "em", "chị", "nó", "thích",
        "sao", "muốn", "vậy", "giờ", "nay", "mai", "cảm ơn",
        "xin lỗi", "ok", "văn bản", "code", "file", "liên kết",
        "toán", "văn", "tiếng việt", "tiếng anh",
        "viết", "đọc", "nghe", "nói", "hỏi", "đáp",
    }

    cac_tu = noi_dung.split()
    ket_qua = []
    for tu in cac_tu:
        dau_dau, dau_cuoi = "", ""
        while tu and tu[0] in "\"'([{":
            dau_dau += tu[0]
            tu = tu[1:]
        while tu and tu[-1] in ".,!?;:)\"']}":
            dau_cuoi = tu[-1] + dau_cuoi
            tu = tu[:-1]

        tu_lower = tu.lower()

        if len(tu_lower) >= 3 and not tu_lower.isdigit() and tu_lower not in tu_dung:
            tot_nhat = None
            kc_tot_nhat = 999
            for tu_chuan in tu_dung:
                if abs(len(tu_chuan) - len(tu_lower)) > 3:
                    continue
                kc = _khoang_cach_levenshtein(tu_lower, tu_chuan)
                if kc < kc_tot_nhat:
                    kc_tot_nhat = kc
                    tot_nhat = tu_chuan

            if tot_nhat and kc_tot_nhat <= max(1, len(tu_lower) // 10):
                ty_le = 1 - (kc_tot_nhat / len(tu_lower))
                if ty_le > 0.9:
                    tu = tot_nhat

        ket_qua.append(dau_dau + tu + dau_cuoi)
    return " ".join(ket_qua)


# ================================================================
# BƯỚC 4: SỬA DẤU TIẾNG VIỆT
# ================================================================
def _co_dau_tieng_viet(noi_dung):
    """Kiểm tra chuỗi có dấu tiếng Việt không."""
    if not noi_dung:
        return False
    for c in noi_dung:
        if unicodedata.combining(c):
            return True
        if c in "ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ":
            return True
    return False


def _sua_dau_tieng_viet(noi_dung):
    """Sửa dấu — chỉ sửa từ có trong bảng."""
    if not noi_dung:
        return noi_dung
    cac_tu = noi_dung.split()
    ket_qua = []
    for tu in cac_tu:
        dau_dau, dau_cuoi = "", ""
        while tu and tu[0] in "\"'([{":
            dau_dau += tu[0]
            tu = tu[1:]
        while tu and tu[-1] in ".,!?;:)\"']}":
            dau_cuoi = tu[-1] + dau_cuoi
            tu = tu[:-1]

        tu_lower = tu.lower()
        if tu_lower in KHONG_DAU_SANG_CO_DAU:
            tu = KHONG_DAU_SANG_CO_DAU[tu_lower]
        ket_qua.append(dau_dau + tu + dau_cuoi)
    return " ".join(ket_qua)


# ================================================================
# BƯỚC 5: BỎ TỪ ĐỆM
# ================================================================
def _bo_tu_dem(noi_dung):
    """Bỏ từ đệm — giữ 'thì' trong 'nếu... thì...'."""
    if not noi_dung:
        return noi_dung

    co_neu = "nếu" in noi_dung.lower()
    co_thi = "thì" in noi_dung.lower()
    giu_thi = co_neu and co_thi

    cac_tu = noi_dung.split()
    ket_qua = []
    for tu in cac_tu:
        dau_dau, dau_cuoi = "", ""
        while tu and tu[0] in "\"'([{":
            dau_dau += tu[0]
            tu = tu[1:]
        while tu and tu[-1] in ".,!?;:)\"']}":
            dau_cuoi = tu[-1] + dau_cuoi
            tu = tu[:-1]

        tu_lower = tu.lower()

        if tu_lower == "thì" and giu_thi:
            ket_qua.append(dau_dau + tu + dau_cuoi)
            continue

        if tu_lower in TU_DEM:
            continue

        ket_qua.append(dau_dau + tu + dau_cuoi)

    return " ".join(ket_qua)


# ================================================================
# BƯỚC 6a: SỬA DẤU CÂU
# ================================================================
def _sua_dau_cau(noi_dung):
    """Sửa dấu câu — khoảng trắng, dấu lặp."""
    if not noi_dung:
        return noi_dung

    noi_dung = re.sub(r"\s+", " ", noi_dung).strip()
    noi_dung = re.sub(r"\s+([.,!?;:])", r"\1", noi_dung)
    noi_dung = re.sub(r"([.!?])\1+", r"\1", noi_dung)
    noi_dung = re.sub(r"(,)\1+", r"\1", noi_dung)

    if noi_dung and len(noi_dung) > 10 and noi_dung[-1] not in ".!?":
        noi_dung += "."

    return noi_dung


# ================================================================
# BƯỚC 6b: CHUẨN HÓA KÝ HIỆU (MẠNH)
# ================================================================
def _chuan_hoa_ky_hieu(noi_dung):
    """
    Chuẩn hóa ký hiệu mạnh:
        - Toán tử, số mũ, căn, so sánh, ký hiệu toán.
        - Đơn vị m², m³.
        - Tiền tệ k, tr, m, $, €, ¥, £, ₫.
        - Ký tự lặp vô nghĩa.
        - Dấu câu ngoại, ngoặc cong.
        - Unicode điều khiển.
        - Xuống dòng, tab.
    """
    if not noi_dung:
        return noi_dung

    s = noi_dung

    # 1. Chuẩn hóa Unicode (NFC) — gộp dấu tổ hợp
    s = unicodedata.normalize("NFC", s)

    # 2. Bỏ ký tự điều khiển Unicode (zero-width, BOM, ...)
    s = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "", s)

    # 3. Xuống dòng, tab
    s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")

    # 4. Dấu câu ngoại (Trung, Nhật, Hàn)
    for k, v in DAU_CAU_NGOAI.items():
        s = s.replace(k, v)

    # 5. Ngoặc cong
    for k, v in NGOAC_CONG.items():
        s = s.replace(k, v)

    # 6. Toán tử cơ bản
    for k, v in TOAN_TU.items():
        s = s.replace(k, v)

    # 7. Số mũ (² → ^2)
    for k, v in SO_MU.items():
        s = s.replace(k, v)

    # 8. Căn (√ → sqrt)
    for k, v in CAN.items():
        s = s.replace(k, v)

    # 9. Ký hiệu toán (≠ ≤ ≥ ...)
    for k, v in KY_HIEU_TOAN.items():
        s = s.replace(k, v)

    # 10. Tiền tệ ký hiệu ($ € ¥ £ ₫)
    for k, v in TIEN_TE.items():
        s = s.replace(k, v)

    # 11. Đơn vị m², m³, cm², cm³, km², km³ → m^2, m^3, ...
    s = re.sub(r"([a-zA-Z])([²³])", lambda m: m.group(1) + ("^2" if m.group(2) == "²" else "^3"), s)

    # 12. x giữa 2 số → *
    s = re.sub(r"(?<=\d)\s*[xX]\s*(?=\d)", "*", s)

    # 13. : giữa 2 số → /
    s = re.sub(r"(?<=\d)\s*:\s*(?=\d)", "/", s)

    # 14. Tiền tệ k, tr, m sau số
    # 50k → 50000
    s = re.sub(r"(\d+(?:\.\d+)?)\s*[kK]\b", lambda m: str(int(float(m.group(1)) * 1000)), s)
    # 2tr → 2000000
    s = re.sub(r"(\d+(?:\.\d+)?)\s*(?:tr|TR|Tr)\b", lambda m: str(int(float(m.group(1)) * 1000000)), s)
    # 2m → 2000000 (chỉ khi m đứng riêng, không phải đơn vị mét)
    s = re.sub(r"(\d+(?:\.\d+)?)\s*[mM]\b(?!\d)", lambda m: str(int(float(m.group(1)) * 1000000)), s)
    # 50000đ → 50000 VND
    s = re.sub(r"(\d+(?:\.\d+)?)\s*[đĐ]\b", lambda m: m.group(1) + " VND", s)

    # 15. Ký tự lặp vô nghĩa (3 lần trở lên)
    # ... → .
    s = re.sub(r"\.{3,}", ".", s)
    # ~~~ → bỏ
    s = re.sub(r"~{2,}", "", s)
    # *** → bỏ (không phải markdown)
    s = re.sub(r"\*{3,}", "", s)
    # !!! → !
    s = re.sub(r"!{2,}", "!", s)
    # ??? → ?
    s = re.sub(r"\?{2,}", "?", s)
    # ,,, → ,
    s = re.sub(r",{2,}", ",", s)
    # ;;; → ;
    s = re.sub(r";{2,}", ";", s)
    # ::: → :
    s = re.sub(r":{2,}", ":", s)

    # 16. Ký tự lặp trong từ (đượcccc → được, hayyyyy → hay)
    # Chỉ giảm khi cùng ký tự lặp ≥ 3 lần
    s = re.sub(r"(\w)\1{2,}", r"\1", s)

    # 17. Khoảng trắng thừa quanh dấu câu
    s = re.sub(r"\s+([.,!?;:)}\]])", r"\1", s)
    s = re.sub(r"([(\[{])\s+", r"\1", s)

    # 18. Gộp nhiều khoảng trắng
    s = re.sub(r"\s+", " ", s).strip()

    return s


# ================================================================
# BƯỚC 7: CHUẨN HÓA VIẾT HOA
# ================================================================
def _chuan_hoa_viet_hoa(noi_dung):
    """Chữ đầu câu viết hoa."""
    if not noi_dung:
        return noi_dung

    ket_qua = noi_dung[0].upper() + noi_dung[1:]

    ket_qua = re.sub(
        r"([.!?]\s+)([a-zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ])",
        lambda m: m.group(1) + m.group(2).upper(),
        ket_qua,
    )

    return ket_qua


# ================================================================
# BƯỚC 8: KIỂM TRA Ý KHÔNG ĐỔI
# ================================================================
def _kiem_tra_y_khong_doi(goc, moi):
    """Cảnh báo nếu chuẩn hóa làm mất từ khóa quan trọng."""
    if not goc or not moi:
        return True
    tu_quan_trong = ["không", "được", "làm", "web", "code", "toán", "văn"]
    for tu in tu_quan_trong:
        if tu in goc.lower() and tu not in moi.lower():
            _ghi_log("dai-nao", f"Cảnh báo: chuẩn hóa mất từ khóa '{tu}'")
            return False
    return True


# ================================================================
# HÀM CHÍNH: CHUẨN HÓA 10 BƯỚC
# ================================================================
def chuan_hoa(noi_dung):
    """
    Chuẩn hóa input theo 10 bước (ký hiệu mạnh).

    noi_dung: chuỗi gốc.
    Trả về: chuỗi đã chuẩn hóa.
    """
    if not noi_dung or not isinstance(noi_dung, str):
        return ""

    goc = noi_dung.strip()
    if not goc:
        return ""

    # Bước 1: Tách câu
    cac_cau = _tach_cau(goc)
    if not cac_cau:
        return goc

    ket_qua_cac_cau = []
    for cau in cac_cau:
        # Bước 2: Sửa viết tắt
        cau = _sua_viet_tat(cau)

        # Bước 3: Sửa chính tả
        cau = _sua_chinh_ta(cau)

        # Bước 4: Sửa dấu tiếng Việt (chỉ khi chưa có dấu)
        if not _co_dau_tieng_viet(cau):
            cau = _sua_dau_tieng_viet(cau)

        # Bước 5: Bỏ từ đệm
        cau = _bo_tu_dem(cau)

        # Bước 6a: Sửa dấu câu
        cau = _sua_dau_cau(cau)

        # Bước 6b: CHUẨN HÓA KÝ HIỆU MẠNH
        cau = _chuan_hoa_ky_hieu(cau)

        # Bước 7: Chuẩn hóa viết hoa
        cau = _chuan_hoa_viet_hoa(cau)

        ket_qua_cac_cau.append(cau)

    ket_qua = " ".join(ket_qua_cac_cau)

    # Bước 8: Kiểm tra ý không đổi
    _kiem_tra_y_khong_doi(goc, ket_qua)

    # Bước 9: Ghi log
    if ket_qua != goc:
        _ghi_log("dai-nao", f"Chuẩn hóa: '{goc[:60]}' → '{ket_qua[:60]}'")

    # Bước 10: Trả kết quả
    return ket_qua


# ================================================================
# TIỆN ÍCH
# ================================================================
def chuan_hoa_nhanh(noi_dung):
    """Chuẩn hóa nhanh — chỉ 4 bước đầu."""
    if not noi_dung:
        return ""
    cau = _sua_viet_tat(noi_dung)
    cau = _sua_dau_tieng_viet(cau)
    cau = _bo_tu_dem(cau)
    cau = _sua_dau_cau(cau)
    return cau


def chuan_hoa_ky_hieu(noi_dung):
    """Chỉ chuẩn hóa ký hiệu — dùng riêng khi cần."""
    return _chuan_hoa_ky_hieu(noi_dung or "")
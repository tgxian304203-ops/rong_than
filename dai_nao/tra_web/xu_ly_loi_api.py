"""
xu_ly_loi_api.py - Phân tích + xử lý lỗi API Tra web Rồng Thần.
"""


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


BANG_LOI_HTTP = {
    400: ("Yêu cầu sai (Bad Request).", "khac"),
    401: ("Key sai hoặc hết hạn (Unauthorized).", "key_sai"),
    402: ("Cần nạp tiền (Payment Required).", "het_quota"),
    403: ("Không có quyền truy cập (Forbidden).", "key_sai"),
    404: ("Endpoint hoặc model không tồn tại (Not Found).", "khong_tim_thay"),
    405: ("Phương thức không được phép (Method Not Allowed).", "khac"),
    408: ("Hết thời gian chờ (Request Timeout).", "loi_mang"),
    409: ("Xung đột dữ liệu (Conflict).", "khac"),
    413: ("Dữ liệu quá lớn (Payload Too Large).", "khac"),
    415: ("Định dạng không hỗ trợ (Unsupported Media Type).", "khac"),
    422: ("Dữ liệu không hợp lệ (Unprocessable Entity).", "khac"),
    429: ("Hết quota hoặc vượt rate limit (Too Many Requests).", "het_quota"),
    500: ("Lỗi server (Internal Server Error).", "loi_server"),
    501: ("Chức năng chưa triển khai (Not Implemented).", "loi_server"),
    502: ("Bad Gateway — server trung gian lỗi.", "loi_server"),
    503: ("Service Unavailable — server quá tải.", "loi_server"),
    504: ("Gateway Timeout — server trung gian chậm.", "loi_server"),
    505: ("HTTP Version Not Supported.", "khac"),
    507: ("Hết dung lượng (Insufficient Storage).", "het_quota"),
    509: ("Vượt băng thông (Bandwidth Limit Exceeded).", "het_quota"),
}


def phan_tich_loi(status_code, response_text="", provider=""):
    if not status_code:
        return "Không có mã lỗi.", "khac"

    try:
        status_code = int(status_code)
    except (ValueError, TypeError):
        return f"Mã lỗi không hợp lệ: {status_code}", "khac"

    if status_code in BANG_LOI_HTTP:
        mo_ta, loai_loi = BANG_LOI_HTTP[status_code]
    elif 500 <= status_code < 600:
        mo_ta = f"Lỗi server ({status_code})."
        loai_loi = "loi_server"
    elif 400 <= status_code < 500:
        mo_ta = f"Lỗi client ({status_code})."
        loai_loi = "khac"
    else:
        mo_ta = f"Lỗi không xác định ({status_code})."
        loai_loi = "khac"

    if provider:
        mo_ta = f"[{provider}] {mo_ta}"

    if response_text:
        t = str(response_text)[:500].lower()

        if "quota" in t or "rate limit" in t or "too many" in t:
            loai_loi = "het_quota"
            mo_ta += " (phát hiện từ khóa quota/rate limit)."
        elif "invalid" in t and "key" in t:
            loai_loi = "key_sai"
            mo_ta += " (phát hiện key không hợp lệ)."
        elif "not found" in t:
            loai_loi = "khong_tim_thay"
            mo_ta += " (phát hiện not found)."

    return mo_ta, loai_loi


def xu_ly_exception(exception, provider=""):
    if not exception:
        return {"loi": "Exception rỗng.", "loai_loi": "khac"}

    ten_loi = type(exception).__name__
    thong_diep = str(exception)[:500]

    loai_loi = "khac"
    if ten_loi in ("Timeout", "TimeoutError", "ReadTimeout", "ConnectTimeout"):
        loai_loi = "loi_mang"
    elif ten_loi in ("ConnectionError", "ConnectTimeoutError"):
        loai_loi = "loi_mang"
    elif ten_loi in ("SSLError", "CertificateError"):
        loai_loi = "loi_ssl"
    elif ten_loi in ("JSONDecodeError", "ValueError"):
        loai_loi = "loi_parse"
    elif "quota" in thong_diep.lower() or "rate" in thong_diep.lower():
        loai_loi = "het_quota"
    elif "unauthorized" in thong_diep.lower() or "forbidden" in thong_diep.lower():
        loai_loi = "key_sai"

    if provider:
        mo_ta = f"[{provider}] {ten_loi}: {thong_diep}"
    else:
        mo_ta = f"{ten_loi}: {thong_diep}"

    _ghi_log("tra-web", f"Exception: {mo_ta[:200]}")

    return {
        "loi": mo_ta,
        "loai_loi": loai_loi,
    }


def goi_y_khac_phuc(loai_loi, provider=""):
    goi_y = []

    if loai_loi == "key_sai":
        goi_y.append("Kiểm tra lại API key đã dán.")
        goi_y.append("Đăng nhập dashboard provider để tạo key mới.")
        if provider:
            goi_y.append(f"Đảm bảo key thuộc tài khoản {provider}.")

    elif loai_loi == "het_quota":
        goi_y.append("Chờ quota reset (đầu tháng hoặc đầu ngày).")
        goi_y.append("Xoay sang API khác (SERPJET → Tavily → Bright Data).")
        goi_y.append("Thêm key mới từ tài khoản khác.")

    elif loai_loi == "khong_tim_thay":
        goi_y.append("Kiểm tra lại endpoint / tên model.")
        goi_y.append("Provider có thể đã đổi endpoint — cần cập nhật code.")

    elif loai_loi == "loi_mang":
        goi_y.append("Kiểm tra kết nối mạng.")
        goi_y.append("Tăng timeout cho request.")
        goi_y.append("Thử lại sau vài giây.")

    elif loai_loi == "loi_ssl":
        goi_y.append("Cập nhật chứng chỉ SSL.")
        goi_y.append("Kiểm tra proxy/firewall.")

    elif loai_loi == "loi_parse":
        goi_y.append("Provider trả về JSON sai format.")
        goi_y.append("Kiểm tra version API — có thể provider đã đổi schema.")

    elif loai_loi == "loi_server":
        goi_y.append("Server provider gặp lỗi — chờ và thử lại.")
        goi_y.append("Xoay sang API khác nếu lỗi kéo dài.")

    else:
        goi_y.append("Xem log chi tiết để biết nguyên nhân.")

    return goi_y


def nen_xoay_api(loai_loi):
    if not loai_loi:
        return False
    return loai_loi in ("het_quota", "key_sai", "loi_server")


def tom_tat_loi(ket_qua_loi):
    if not ket_qua_loi:
        return ""
    return f"[{ket_qua_loi.get('loai_loi', 'khac')}] {ket_qua_loi.get('loi', '')[:150]}"


def lay_ma_loi(loai_loi):
    ket_qua = []
    for ma, (_, loai) in BANG_LOI_HTTP.items():
        if loai == loai_loi:
            ket_qua.append(ma)
    return ket_qua


def lay_loai_tu_ma(ma):
    if ma in BANG_LOI_HTTP:
        return BANG_LOI_HTTP[ma][1]
    if 500 <= ma < 600:
        return "loi_server"
    if 400 <= ma < 500:
        return "khac"
    return "khac"


def danh_sach_loai_loi():
    return [
        "key_sai",
        "het_quota",
        "khong_tim_thay",
        "loi_mang",
        "loi_ssl",
        "loi_parse",
        "loi_server",
        "khac",
    ]
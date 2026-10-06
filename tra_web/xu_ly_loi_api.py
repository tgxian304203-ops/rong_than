"""
xu_ly_loi_api.py - Xử lý lỗi API Tra web Rồng Thần.

Nhiệm vụ:
    - phan_tich_loi(status_code, text, provider): phân tích lỗi từ response.
    - xu_ly_loi(key_info, ket_qua_loi): xử lý lỗi (đánh dấu quota, xoay API).
    - lay_hanh_dong(loai_loi): trả hành động tiếp theo.
    - ghi_loi_api(provider, key_id, loi, loai_loi): ghi lỗi vào kho 2.

Quy tắc (theo Phần 4):
    - Phân loại lỗi: het_quota, key_sai, timeout, mạng, rate_limit, khac.
    - het_quota → xoay API.
    - key_sai → xoay key.
    - timeout/mạng → thử lại.
    - rate_limit → chờ.

Trả về:
    - phan_tich_loi() → (mô_tả, loại_lỗi).
    - xu_ly_loi() → hành_động (str).

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
SO_LAN_LOI_TOI_DA = 3


# ================================================================
# PHÂN TÍCH LỖI
# ================================================================
def phan_tich_loi(status_code, text, provider=""):
    """
    Phân tích lỗi từ response API.

    status_code: mã HTTP.
    text: nội dung response.
    provider: tên API (SERPJET / Tavily / Bright Data).

    Trả về: (mô_tả, loại_lỗi).
    Loại lỗi: "het_quota" | "key_sai" | "timeout" | "mang" | "rate_limit" | "khac".
    """
    text_lower = (text or "").lower()

    # Xử lý theo mã HTTP
    if status_code == 200:
        return "", ""

    if status_code == 400:
        # Có thể do query sai hoặc API sai format
        if "invalid" in text_lower or "bad request" in text_lower:
            return f"Request sai (400): {text[:200]}", "khac"
        return f"Bad Request (400): {text[:200]}", "khac"

    if status_code == 401:
        return "Key sai hoặc hết hạn (401).", "key_sai"

    if status_code == 402:
        return "Hết credit / cần nạp tiền (402).", "het_quota"

    if status_code == 403:
        return "Không có quyền (403).", "key_sai"

    if status_code == 404:
        return "Endpoint không tồn tại (404).", "khac"

    if status_code == 408:
        return "Request timeout (408).", "timeout"

    if status_code == 429:
        # Phân biệt rate limit ngắn và hết quota tháng
        if "month" in text_lower or "monthly" in text_lower or "quota" in text_lower:
            return "Hết quota tháng (429).", "het_quota"
        if "day" in text_lower or "daily" in text_lower:
            return "Hết quota ngày (429).", "het_quota"
        return "Vượt rate limit (429).", "rate_limit"

    if 500 <= status_code < 600:
        return f"Server {provider or 'API'} lỗi ({status_code}).", "khac"

    # Phân tích theo text
    if "quota" in text_lower or "exceeded" in text_lower:
        return f"Hết quota: {text[:200]}", "het_quota"
    if "unauthorized" in text_lower or "invalid key" in text_lower or "authentication" in text_lower:
        return f"Key sai: {text[:200]}", "key_sai"
    if "rate limit" in text_lower or "too many" in text_lower:
        return f"Vượt rate limit: {text[:200]}", "rate_limit"
    if "timeout" in text_lower or "timed out" in text_lower:
        return f"Timeout: {text[:200]}", "timeout"

    return f"Lỗi không xác định ({status_code}): {text[:200]}", "khac"


# ================================================================
# LẤY HÀNH ĐỘNG TIẾP THEO
# ================================================================
def lay_hanh_dong(loai_loi):
    """
    Trả hành động tiếp theo dựa trên loại lỗi.

    Trả về:
        - "xoay_api": hết quota → xoay API.
        - "xoay_key": key sai → xoay key.
        - "thu_lai": timeout/mạng → thử lại.
        - "cho": rate_limit → chờ.
        - "bo_qua": lỗi khác → bỏ qua.
    """
    bang = {
        "het_quota": "xoay_api",
        "key_sai": "xoay_key",
        "timeout": "thu_lai",
        "mang": "thu_lai",
        "rate_limit": "cho",
        "khac": "bo_qua",
    }
    return bang.get(loai_loi, "bo_qua")


# ================================================================
# XỬ LÝ LỖI
# ================================================================
def xu_ly_loi(key_info, ket_qua_loi):
    """
    Xử lý lỗi từ kết quả gọi API.

    key_info: dict { id, key, provider }.
    ket_qua_loi: dict { loi, loai_loi }.

    Trả về: hành động (str): "xoay_api" | "xoay_key" | "thu_lai" | "cho" | "bo_qua".
    """
    if not ket_qua_loi:
        return "bo_qua"

    provider = (key_info or {}).get("provider", "")
    key_id = (key_info or {}).get("id", "")
    loai_loi = ket_qua_loi.get("loai_loi", "khac")
    loi = ket_qua_loi.get("loi", "")

    # Ghi lỗi vào kho 2
    if provider and loai_loi:
        ghi_loi_api(provider, key_id, loi, loai_loi)

    # Hết quota → đánh dấu + xoay API
    if loai_loi == "het_quota":
        try:
            from tra_web.xoay_api import danh_dau_het_quota
            danh_dau_het_quota(provider, key_id)
        except ImportError:
            pass
        _ghi_log("tra-web", f"{provider} hết quota → xoay API.")
        return "xoay_api"

    # Key sai → đánh dấu + xoay key
    if loai_loi == "key_sai":
        _ghi_log("tra-web", f"{provider} key sai → xoay key.")
        return "xoay_key"

    # Rate limit → chờ
    if loai_loi == "rate_limit":
        _ghi_log("tra-web", f"{provider} rate limit → chờ.")
        return "cho"

    # Timeout / mạng → thử lại
    if loai_loi in ("timeout", "mang"):
        _ghi_log("tra-web", f"{provider} {loai_loi} → thử lại.")
        return "thu_lai"

    return "bo_qua"


# ================================================================
# GHI LỖI VÀO KHO 2
# ================================================================
def ghi_loi_api(provider, key_id, loi="", loai_loi="khac"):
    """
    Ghi lỗi API tra web vào kho 2.

    Trả về: True nếu ghi thành công.
    """
    if not provider:
        return False

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        col = db["loi_api_tra_web"]

        col.update_one(
            {"provider": provider, "key_id": key_id},
            {
                "$inc": {"so_lan_loi": 1},
                "$set": {
                    "provider": provider,
                    "key_id": key_id,
                    "loi_cuoi": loi[:500],
                    "loai_loi_cuoi": loai_loi,
                    "thoi_gian_cuoi": int(time.time()),
                },
            },
            upsert=True,
        )
        return True
    except Exception as e:
        _ghi_log("loi", f"Ghi lỗi API lỗi: {e}")
        return False


# ================================================================
# LẤY LỊCH SỬ LỖI
# ================================================================
def lay_lich_su_loi(provider="", key_id=""):
    """
    Lấy lịch sử lỗi của API.

    Trả về: list lỗi.
    """
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        col = db["loi_api_tra_web"]

        dieu_kien = {}
        if provider:
            dieu_kien["provider"] = provider
        if key_id:
            dieu_kien["key_id"] = key_id

        return list(col.find(dieu_kien))
    except Exception:
        return []


# ================================================================
# XÓA LỊCH SỬ LỖI
# ================================================================
def xoa_lich_su_loi(provider="", key_id=""):
    """Xóa lịch sử lỗi của API."""
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        col = db["loi_api_tra_web"]

        dieu_kien = {}
        if provider:
            dieu_kien["provider"] = provider
        if key_id:
            dieu_kien["key_id"] = key_id

        ket_qua = col.delete_many(dieu_kien)
        return ket_qua.deleted_count
    except Exception:
        return 0


# ================================================================
# ĐẾM LỖI
# ================================================================
def dem_loi(provider=""):
    """Đếm số lỗi của API."""
    return len(lay_lich_su_loi(provider))


# ================================================================
# KIỂM TRA CÓ NÊN BLACKLIST KEY KHÔNG
# ================================================================
def nen_blacklist_key(provider, key_id):
    """
    Kiểm tra có nên blacklist key không (lỗi >= 3 lần).

    Trả về: True nếu nên blacklist.
    """
    lich_su = lay_lich_su_loi(provider, key_id)
    for item in lich_su:
        if item.get("so_lan_loi", 0) >= SO_LAN_LOI_TOI_DA:
            return True
    return False


# ================================================================
# XỬ LÝ LỖI HTTP TỪ REQUEST
# ================================================================
def xu_ly_http_error(response, provider=""):
    """
    Xử lý lỗi từ đối tượng response của requests.

    response: requests.Response.
    provider: tên API.

    Trả về dict { thanh_cong, loi, loai_loi }.
    """
    if not response:
        return {
            "thanh_cong": False,
            "loi": "Response rỗng.",
            "loai_loi": "khac",
        }

    if response.status_code == 200:
        return {"thanh_cong": True, "loi": "", "loai_loi": ""}

    try:
        text = response.text[:500]
    except Exception:
        text = ""

    mo_ta, loai_loi = phan_tich_loi(response.status_code, text, provider)

    return {
        "thanh_cong": False,
        "loi": mo_ta,
        "loai_loi": loai_loi,
    }


# ================================================================
# XỬ LÝ EXCEPTION
# ================================================================
def xu_ly_exception(exception, provider=""):
    """
    Xử lý exception khi gọi API.

    Trả về dict { thanh_cong, loi, loai_loi }.
    """
    if not exception:
        return {
            "thanh_cong": False,
            "loi": "Exception rỗng.",
            "loai_loi": "khac",
        }

    ten_loai = type(exception).__name__
    mo_ta = str(exception)[:300]

    # Phân loại exception
    if "Timeout" in ten_loai or "timeout" in mo_ta.lower():
        loai_loi = "timeout"
    elif "Connection" in ten_loai or "connection" in mo_ta.lower():
        loai_loi = "mang"
    elif "SSLError" in ten_loai:
        loai_loi = "mang"
    elif "HTTPError" in ten_loai:
        loai_loi = "khac"
    else:
        loai_loi = "khac"

    return {
        "thanh_cong": False,
        "loi": f"{ten_loai}: {mo_ta}",
        "loai_loi": loai_loi,
    }


# ================================================================
# TÓM TẮT LỖI
# ================================================================
def tom_tat_loi(ket_qua_loi):
    """Tạo chuỗi tóm tắt lỗi API."""
    if not ket_qua_loi:
        return ""

    if ket_qua_loi.get("thanh_cong"):
        return "✅ OK"

    return (
        f"❌ [{ket_qua_loi.get('loai_loi', '')}] "
        f"{ket_qua_loi.get('loi', '')[:100]}"
    )


# ================================================================
# HÀM PHỤ: XỬ LÝ CHUỖI LỖI THỦ CÔNG
# ================================================================
def phan_tich_loi_tu_chuoi(chuoi_loi):
    """
    Phân tích lỗi từ chuỗi (không có status code).
    Dùng khi nhận lỗi từ nơi khác.

    Trả về: (mô_tả, loại_lỗi).
    """
    if not chuoi_loi:
        return "", ""

    t = chuoi_loi.lower()

    if "quota" in t or "exceeded" in t:
        return chuoi_loi[:200], "het_quota"
    if "unauthorized" in t or "invalid" in t or "authentication" in t:
        return chuoi_loi[:200], "key_sai"
    if "rate limit" in t or "too many" in t:
        return chuoi_loi[:200], "rate_limit"
    if "timeout" in t or "timed out" in t:
        return chuoi_loi[:200], "timeout"
    if "connection" in t or "network" in t:
        return chuoi_loi[:200], "mang"

    return chuoi_loi[:200], "khac"


# ================================================================
# HÀM PHỤ: ĐẾM LỖI THEO LOẠI
# ================================================================
def dem_loi_theo_loai(provider=""):
    """Đếm lỗi theo loại (het_quota, key_sai, timeout...)."""
    lich_su = lay_lich_su_loi(provider)
    ket_qua = {}

    for item in lich_su:
        loai = item.get("loai_loi_cuoi", "khac")
        ket_qua[loai] = ket_qua.get(loai, 0) + item.get("so_lan_loi", 0)

    return ket_qua
"""
kiem_ke_key.py - Bước 1 Tiểu não: Kiểm kê key THỰC TẾ Rồng Thần.

Nhiệm vụ:
    - kiem_ke_key(chu_so_huu): kiểm kê key THỰC TẾ đã dán.
    - Xác định provider nào CÓ key (bỏ provider không có key).
    - Sắp xếp thứ tự gọi chỉ trong các provider có key.
    - Mỗi key chỉ dùng model của provider đó.

Quy tắc (theo Phần 4, bước 1):
    - Chỉ gọi provider có key được dán.
    - Không dán Gemini → không gọi Gemini.
    - Không dán OpenRouter → không gọi OpenRouter.
    - Thứ tự provider: Groq → OpenRouter → Gemini (chỉ provider có key).
    - Trong mỗi provider: key #1 → key #2 → key #3.
    - Bỏ key đã bị blacklist.

Trả về:
    {
        thanh_cong: bool,
        tong_key: int,
        provider_co_key: [str],       # chỉ provider CÓ key
        theo_provider: {provider: [key_info]},   # chỉ provider có key
        thu_tu_goi: [key_info],       # thứ tự gọi thực tế
        loi: str?,
    }

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
# Thứ tự ưu tiên provider (chỉ áp dụng cho provider CÓ key)
THU_TU_PROVIDER = ["Groq", "OpenRouter", "Gemini"]

# Model mặc định cho từng provider (dùng khi không lấy được từ API)
MODEL_MAC_DINH = {
    "Groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ],
    "OpenRouter": [
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
        "mistralai/mistral-7b-instruct:free",
        "qwen/qwen-2.5-72b-instruct:free",
    ],
    "Gemini": [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ],
}


# ================================================================
# CHUẨN HÓA TÊN PROVIDER
# ================================================================
def _chuan_hoa_provider(provider):
    """Chuẩn hóa tên provider về 3 tên chính."""
    if not provider:
        return ""
    p = provider.strip().lower()
    if p == "groq":
        return "Groq"
    if p in ("openrouter", "open router", "or"):
        return "OpenRouter"
    if p in ("gemini", "google"):
        return "Gemini"
    return ""


# ================================================================
# ĐỌC KEY TỪ KHO 1
# ================================================================
def _lay_key_tu_kho(chu_so_huu):
    """Đọc toàn bộ key model của 1 tài khoản từ kho 1."""
    if not chu_so_huu:
        return []

    try:
        from dai_nao.ghi_nho import lay_danh_sach_key_cua
        return lay_danh_sach_key_cua(chu_so_huu) or []
    except ImportError:
        _ghi_log("loi", "ghi_nho.py chưa có — không đọc được key.")
        return []
    except Exception as e:
        _ghi_log("loi", f"Đọc key lỗi: {e}")
        return []


# ================================================================
# NHÓM THEO PROVIDER (CHỈ PROVIDER CÓ KEY)
# ================================================================
def _nhom_theo_provider(danh_sach_key):
    """
    Nhóm key theo provider.
    CHỈ trả về provider CÓ key — không thêm provider rỗng.

    Trả về: dict { provider_co_key: [key_info] }.
    """
    ket_qua = {}

    for key in danh_sach_key:
        if not isinstance(key, dict):
            continue

        provider = _chuan_hoa_provider(key.get("provider", ""))
        if not provider:
            continue

        # Bỏ key blacklist
        if key.get("blacklist", False):
            continue

        if provider not in ket_qua:
            ket_qua[provider] = []
        ket_qua[provider].append(key)

    return ket_qua


# ================================================================
# LIỆT KÊ MODEL CHO 1 KEY
# ================================================================
def _liet_ke_model(provider, key):
    """
    Liệt kê model có thể dùng cho 1 key.
    Chỉ gọi provider của key đó.
    """
    if not provider or not key:
        return list(MODEL_MAC_DINH.get(provider, []))

    # Thử gọi API thật
    try:
        from tieu_nao.lay_danh_sach_model import lay_danh_sach_model
        danh_sach = lay_danh_sach_model(provider, key)
        if danh_sach and isinstance(danh_sach, list):
            return danh_sach
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Lấy model lỗi ({provider}): {e}")

    return list(MODEL_MAC_DINH.get(provider, []))


# ================================================================
# SẮP XẾP KEY TRONG TỪNG PROVIDER
# ================================================================
def _sap_xep_key_trong_provider(danh_sach_key):
    """
    Sắp xếp key trong 1 provider:
        - Phần trăm còn lại cao đứng trước.
        - Cũ hơn (ngay_tao nhỏ) đứng trước.
    """
    if not danh_sach_key:
        return []

    def khoa(key):
        phan_tram = float(key.get("phan_tram", 100) or 100)
        ngay_tao = key.get("ngay_tao", 0) or 0
        return (-phan_tram, ngay_tao)

    return sorted(danh_sach_key, key=khoa)


# ================================================================
# XÂY THỨ TỰ GỌI THỰC TẾ
# ================================================================
def _xay_thu_tu_goi(nhom_theo_provider):
    """
    Xây thứ tự gọi key thực tế:
        - Chỉ gồm provider CÓ key.
        - Provider theo thứ tự: Groq → OpenRouter → Gemini.
        - Trong mỗi provider: key đã sắp xếp.

    Trả về: list key_info theo thứ tự gọi.
    """
    ket_qua = []

    for provider in THU_TU_PROVIDER:
        if provider not in nhom_theo_provider:
            continue  # Bỏ qua provider không có key

        danh_sach = _sap_xep_key_trong_provider(nhom_theo_provider[provider])
        ket_qua.extend(danh_sach)

    return ket_qua


# ================================================================
# HÀM CHÍNH
# ================================================================
def kiem_ke_key(chu_so_huu):
    """
    Bước 1: Kiểm kê key THỰC TẾ đã dán của tài khoản.

    chưa dán Gemini → không có Gemini trong danh sách.
    chưa dán OpenRouter → không có OpenRouter.

    Trả về dict đầy đủ.
    """
    ket_qua = {
        "thanh_cong": False,
        "tong_key": 0,
        "provider_co_key": [],       # CHỈ provider có key
        "theo_provider": {},
        "thu_tu_goi": [],
        "loi": "",
    }

    if not chu_so_huu:
        ket_qua["loi"] = "Thiếu tên tài khoản."
        return ket_qua

    # 1. Đọc key từ kho 1
    danh_sach_key = _lay_key_tu_kho(chu_so_huu)

    if not danh_sach_key:
        ket_qua["loi"] = "Tài khoản chưa có key nào."
        return ket_qua

    # 2. Nhóm theo provider (chỉ provider có key)
    nhom = _nhom_theo_provider(danh_sach_key)

    if not nhom:
        ket_qua["loi"] = "Không có key nào hợp lệ (có thể bị blacklist)."
        return ket_qua

    # 3. Xác định danh sách provider CÓ key (theo thứ tự ưu tiên)
    provider_co_key = [p for p in THU_TU_PROVIDER if p in nhom]
    ket_qua["provider_co_key"] = provider_co_key

    # 4. Với mỗi key, liệt kê model
    for provider in provider_co_key:
        ket_qua["theo_provider"][provider] = []
        for key in nhom[provider]:
            key["model_co_the_dung"] = _liet_ke_model(provider, key.get("key", ""))
            ket_qua["theo_provider"][provider].append(key)

    # 5. Xây thứ tự gọi thực tế
    ket_qua["thu_tu_goi"] = _xay_thu_tu_goi(nhom)

    ket_qua["tong_key"] = sum(len(v) for v in nhom.values())
    ket_qua["thanh_cong"] = True

    _ghi_log(
        "tieu-nao",
        f"Kiểm kê key cho {chu_so_huu}: {ket_qua['tong_key']} key, "
        f"provider có key: {', '.join(provider_co_key)}",
    )

    return ket_qua


# ================================================================
# HÀM PHỤ
# ================================================================
def dem_theo_provider(chu_so_huu):
    """Đếm số key theo từng provider có key."""
    ket_qua = kiem_ke_key(chu_so_huu)
    if not ket_qua.get("thanh_cong"):
        return {}

    return {
        p: len(ket_qua["theo_provider"].get(p, []))
        for p in ket_qua["provider_co_key"]
    }


def lay_key_dau_tien(chu_so_huu):
    """Lấy key đầu tiên trong thứ tự gọi."""
    ket_qua = kiem_ke_key(chu_so_huu)
    if not ket_qua.get("thanh_cong"):
        return None

    thu_tu = ket_qua.get("thu_tu_goi", [])
    return thu_tu[0] if thu_tu else None


def lay_key_theo_provider(chu_so_huu, provider):
    """Lấy tất cả key của 1 provider (chỉ khi provider có key)."""
    ket_qua = kiem_ke_key(chu_so_huu)
    if not ket_qua.get("thanh_cong"):
        return []

    provider_chuan = _chuan_hoa_provider(provider)
    return ket_qua["theo_provider"].get(provider_chuan, [])


def tom_tat_kiem_ke(ket_qua):
    """Tạo chuỗi tóm tắt kiểm kê."""
    if not ket_qua or not ket_qua.get("thanh_cong"):
        return f"❌ Không kiểm kê được: {ket_qua.get('loi', 'không rõ')}"

    phan = [f"📊 Tổng key: {ket_qua['tong_key']}"]
    phan.append(f"🔑 Provider có key: {', '.join(ket_qua['provider_co_key'])}")

    for provider in ket_qua["provider_co_key"]:
        so = len(ket_qua["theo_provider"].get(provider, []))
        phan.append(f"  - {provider}: {so} key")

    phan.append(f"📞 Thứ tự gọi: {len(ket_qua['thu_tu_goi'])} bước")
    return "\n".join(phan)


def co_key(chu_so_huu):
    """Kiểm tra tài khoản có key nào không."""
    ket_qua = kiem_ke_key(chu_so_huu)
    return ket_qua.get("thanh_cong") and ket_qua.get("tong_key", 0) > 0


def lay_danh_sach_provider_co_key(chu_so_huu):
    """Trả về danh sách provider CÓ key (đã sắp xếp theo thứ tự ưu tiên)."""
    ket_qua = kiem_ke_key(chu_so_huu)
    if not ket_qua.get("thanh_cong"):
        return []
    return ket_qua.get("provider_co_key", [])


def co_provider(chu_so_huu, provider):
    """Kiểm tra provider có key không."""
    provider_chuan = _chuan_hoa_provider(provider)
    if not provider_chuan:
        return False
    ds = lay_danh_sach_provider_co_key(chu_so_huu)
    return provider_chuan in ds


def liet_ke_model_theo_key(chu_so_huu):
    """
    Liệt kê toàn bộ model có thể dùng, gắn với key tương ứng.

    Trả về: list [{ provider, key_id, phan_tram, model: [str] }].
    """
    ket_qua = kiem_ke_key(chu_so_huu)
    if not ket_qua.get("thanh_cong"):
        return []

    ket_qua_list = []
    for key in ket_qua["thu_tu_goi"]:
        ket_qua_list.append({
            "provider": key.get("provider", ""),
            "key_id": key.get("id", ""),
            "phan_tram": key.get("phan_tram", 100),
            "model": key.get("model_co_the_dung", []),
        })
    return ket_qua_list
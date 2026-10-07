"""
kiem_ke_key.py - Bước 1 Tiểu não: Kiểm kê key THỰC TẾ Rồng Thần.

Nhiệm vụ:
    - kiem_ke_key(chu_so_huu): kiểm kê key THỰC TẾ đã dán.
    - Xác định provider nào CÓ key (bỏ provider không có key).
    - Sắp xếp thứ tự gọi chỉ trong các provider có key.
    - Mỗi key chỉ dùng model của provider đó.

ĐÃ SỬA:
    - L6: MODEL_MAC_DINH cập nhật mới (10/2026), đồng bộ với
      lay_danh_sach_model.py.
    - L14: Lọc model bị blacklist trước khi trả về.

Quy tắc:
    - Chỉ gọi provider có key được dán.
    - Thứ tự provider: Groq → OpenRouter → Gemini.
    - Trong mỗi provider: key #1 → key #2 → key #3.
    - Bỏ key đã bị blacklist.

Trả về:
    {
        thanh_cong: bool,
        tong_key: int,
        provider_co_key: [str],
        theo_provider: {provider: [key_info]},
        thu_tu_goi: [key_info],
        loi: str?,
    }
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
THU_TU_PROVIDER = ["Groq", "OpenRouter", "Gemini"]

# MODEL MẶC ĐỊNH (cập nhật 10/2026) — đồng bộ với lay_danh_sach_model.py
MODEL_MAC_DINH = {
    "Groq": [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
    ],
    "OpenRouter": [
        "space-bunny-alpha",
        "nvidia/nemotron-3-ultra:free",
        "poolside/laguna-s-2.1:free",
        "nvidia/nemotron-3.5-lightning:free",
        "dots-studio/dots3-note-preview:free",
        "openai/gpt-oss-120b:free",
        "openai/gpt-oss-20b:free",
        "qwen/qwen3-coder:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "arcee-ai/trinity-large-preview:free",
        "z-ai/glm-4.5-air:free",
        "deepseek/deepseek-r1:free",
    ],
    "Gemini": [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ],
}


# ================================================================
# CHUẨN HÓA TÊN PROVIDER
# ================================================================
def _chuan_hoa_provider(provider):
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
    if not chu_so_huu:
        return []
    try:
        from dai_nao.ghi_nho import lay_danh_sach_key_cua
        return lay_danh_sach_key_cua(chu_so_huu) or []
    except ImportError:
        _ghi_log("loi", "ghi_nho.py chưa có.")
        return []
    except Exception as e:
        _ghi_log("loi", f"Đọc key lỗi: {e}")
        return []


# ================================================================
# NHÓM KEY THEO PROVIDER
# ================================================================
def _nhom_theo_provider(danh_sach_key):
    ket_qua = {}
    for key in danh_sach_key:
        if not isinstance(key, dict):
            continue
        provider = _chuan_hoa_provider(key.get("provider", ""))
        if not provider:
            continue
        if key.get("blacklist", False):
            continue
        if provider not in ket_qua:
            ket_qua[provider] = []
        ket_qua[provider].append(key)
    return ket_qua


# ================================================================
# LỌC MODEL BỊ BLACKLIST (L14)
# ================================================================
def _loc_blacklist(danh_sach_model, provider):
    """
    Lọc bỏ model bị blacklist.

    L14: Trước đây không lọc → model chết được gọi lại mãi.
    """
    if not danh_sach_model or not provider:
        return list(danh_sach_model) if danh_sach_model else []

    try:
        from tieu_nao.quan_ly_loi import loc_model_bi_blacklist
        return loc_model_bi_blacklist(danh_sach_model, provider)
    except ImportError:
        return list(danh_sach_model)
    except Exception as e:
        _ghi_log("loi", f"Lọc blacklist lỗi ({provider}): {e}")
        return list(danh_sach_model)


# ================================================================
# LIỆT KÊ MODEL CHO 1 KEY
# ================================================================
def _liet_ke_model(provider, key):
    """Liệt kê model có thể dùng cho 1 key (đã lọc blacklist)."""
    if not provider or not key:
        return list(MODEL_MAC_DINH.get(provider, []))

    danh_sach = []
    # Thử gọi API thật
    try:
        from tieu_nao.lay_danh_sach_model import lay_danh_sach_model
        danh_sach_api = lay_danh_sach_model(provider, key)
        if danh_sach_api and isinstance(danh_sach_api, list):
            danh_sach = danh_sach_api
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Lấy model lỗi ({provider}): {e}")

    # Fallback: model mặc định
    if not danh_sach:
        danh_sach = list(MODEL_MAC_DINH.get(provider, []))

    # L14: Lọc blacklist
    danh_sach = _loc_blacklist(danh_sach, provider)

    return danh_sach


# ================================================================
# SẮP XẾP KEY TRONG TỪNG PROVIDER
# ================================================================
def _sap_xep_key_trong_provider(danh_sach_key):
    if not danh_sach_key:
        return []

    def khoa(key):
        phan_tram = float(key.get("phan_tram", 100) or 100)
        ngay_tao = key.get("ngay_tao", 0) or 0
        return (-phan_tram, ngay_tao)

    return sorted(danh_sach_key, key=khoa)


# ================================================================
# XÂY THỨ TỰ GỌI
# ================================================================
def _xay_thu_tu_goi(nhom_theo_provider):
    ket_qua = []
    for provider in THU_TU_PROVIDER:
        if provider not in nhom_theo_provider:
            continue
        danh_sach = _sap_xep_key_trong_provider(nhom_theo_provider[provider])
        ket_qua.extend(danh_sach)
    return ket_qua


# ================================================================
# HÀM CHÍNH
# ================================================================
def kiem_ke_key(chu_so_huu):
    """
    Bước 1: Kiểm kê key THỰC TẾ đã dán của tài khoản.

    ĐÃ SỬA:
        - L6: MODEL_MAC_DINH cập nhật mới.
        - L14: Lọc model bị blacklist.
    """
    ket_qua = {
        "thanh_cong": False,
        "tong_key": 0,
        "provider_co_key": [],
        "theo_provider": {},
        "thu_tu_goi": [],
        "loi": "",
    }

    if not chu_so_huu:
        ket_qua["loi"] = "Thiếu tên tài khoản."
        return ket_qua

    danh_sach_key = _lay_key_tu_kho(chu_so_huu)

    if not danh_sach_key:
        ket_qua["loi"] = "Tài khoản chưa có key nào."
        return ket_qua

    nhom = _nhom_theo_provider(danh_sach_key)

    if not nhom:
        ket_qua["loi"] = "Không có key nào hợp lệ (có thể bị blacklist)."
        return ket_qua

    provider_co_key = [p for p in THU_TU_PROVIDER if p in nhom]
    ket_qua["provider_co_key"] = provider_co_key

    for provider in provider_co_key:
        ket_qua["theo_provider"][provider] = []
        for key in nhom[provider]:
            key["model_co_the_dung"] = _liet_ke_model(provider, key.get("key", ""))
            ket_qua["theo_provider"][provider].append(key)

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
    ket_qua = kiem_ke_key(chu_so_huu)
    if not ket_qua.get("thanh_cong"):
        return {}
    return {
        p: len(ket_qua["theo_provider"].get(p, []))
        for p in ket_qua["provider_co_key"]
    }


def lay_key_dau_tien(chu_so_huu):
    ket_qua = kiem_ke_key(chu_so_huu)
    if not ket_qua.get("thanh_cong"):
        return None
    thu_tu = ket_qua.get("thu_tu_goi", [])
    return thu_tu[0] if thu_tu else None


def lay_key_theo_provider(chu_so_huu, provider):
    ket_qua = kiem_ke_key(chu_so_huu)
    if not ket_qua.get("thanh_cong"):
        return []
    provider_chuan = _chuan_hoa_provider(provider)
    return ket_qua["theo_provider"].get(provider_chuan, [])


def tom_tat_kiem_ke(ket_qua):
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
    ket_qua = kiem_ke_key(chu_so_huu)
    return ket_qua.get("thanh_cong") and ket_qua.get("tong_key", 0) > 0


def lay_danh_sach_provider_co_key(chu_so_huu):
    ket_qua = kiem_ke_key(chu_so_huu)
    if not ket_qua.get("thanh_cong"):
        return []
    return ket_qua.get("provider_co_key", [])


def co_provider(chu_so_huu, provider):
    provider_chuan = _chuan_hoa_provider(provider)
    if not provider_chuan:
        return False
    ds = lay_danh_sach_provider_co_key(chu_so_huu)
    return provider_chuan in ds


def liet_ke_model_theo_key(chu_so_huu):
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
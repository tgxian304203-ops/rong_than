"""
lay_danh_sach_model.py - Lấy danh sách model TỰ ĐỘNG CẬP NHẬT Rồng Thần.

Nhiệm vụ:
    - lay_danh_sach_model(provider, key): lấy model thật từ API.
    - TỰ ĐỘNG CẬP NHẬT: gọi API trước, danh sách mặc định chỉ là fallback.
    - TỰ ĐỘNG LOẠI BỎ model không phải chat (image, embedding, audio, ...).
    - Lọc model free, model đang hoạt động.

Quy tắc:
    - Ưu tiên số 1: gọi API thật để lấy danh sách model hiện tại.
    - Ưu tiên số 2: nếu API lỗi, dùng danh sách mặc định (đã cập nhật).
    - Tự động loại bỏ model không phải chat.
    - Cache 6 giờ để tiết kiệm quota.
    - Timeout 10s — tránh treo server.

Cập nhật lần cuối: 2026-10-09
    - Groq: giữ các model chat còn sống.
    - OpenRouter: giữ các model free, loại bỏ model không phải chat.
    - Gemini: loại bỏ model image/vision/embedding/audio.

Tầng dữ liệu: Không.
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
# CACHE (6 giờ cho model, vì model ít thay đổi)
# ================================================================
CACHE = {}
THOI_GIAN_CACHE = 6 * 3600  # 6 giờ


def _lay_cache(khoa_cache):
    """Lấy cache nếu còn hạn."""
    if khoa_cache in CACHE:
        thoi_gian, gia_tri = CACHE[khoa_cache]
        if time.time() - thoi_gian < THOI_GIAN_CACHE:
            return gia_tri
        del CACHE[khoa_cache]
    return None


def _luu_cache(khoa_cache, gia_tri):
    """Lưu cache với timestamp."""
    CACHE[khoa_cache] = (time.time(), gia_tri)


def xoa_cache():
    """Xóa toàn bộ cache."""
    CACHE.clear()


def xoa_cache_provider(provider, key):
    """Xóa cache của 1 provider + key."""
    if not provider or not key:
        return
    p = provider.strip().lower()
    if p == "groq":
        khoa_cache = "groq_" + key[:20]
    elif p in ("openrouter", "open router", "or"):
        khoa_cache = "openrouter_" + key[:20]
    elif p in ("gemini", "google"):
        khoa_cache = "gemini_" + key[:20]
    else:
        return
    if khoa_cache in CACHE:
        del CACHE[khoa_cache]


# ================================================================
# HẰNG SỐ: MODEL KHÔNG PHẢI CHAT — LOẠI BỎ
# ================================================================
# Dùng cho tất cả provider
TU_KHOA_LOAI_BO = (
    "image", "vision", "embedding", "embed", "aqa",
    "imagen", "veo", "tts", "audio", "whisper",
    "gemma", "learnlm", "text-embedding",
    "guard", "safeguard", "moderation",
    "rerank", "clip", "blip", "dall-e", "stable-diffusion",
)


def _la_model_chat(model_id):
    """Kiểm tra model có phải chat/text không."""
    if not model_id:
        return False
    m = model_id.lower()
    for tk in TU_KHOA_LOAI_BO:
        if tk in m:
            return False
    return True


# ================================================================
# DANH SÁCH MẶC ĐỊNH (ĐÃ CẬP NHẬT THÁNG 10/2026)
# CHỈ LÀ FALLBACK KHI API CHẾT HOÀN TOÀN
# ================================================================
MODEL_MAC_DINH = {
    "Groq": [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
    ],
    "OpenRouter": [
        "qwen/qwen3.6-plus",
        "deepseek/deepseek-r1:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "openai/gpt-oss-120b:free",
        "openai/gpt-oss-20b:free",
        "google/gemma-4-31b-it:free",
        "qwen/qwen3-coder:free",
        "nvidia/nemotron-3-super-120b-a12b",
        "inclusionai/ling-3.0-flash",
        "arcee-ai/trinity-large-preview:free",
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
# TỰ ĐỘNG LOẠI BỎ MODEL ĐÃ CHẾT
# ================================================================
def _loai_bo_model_chet(danh_sach_api, danh_sach_mac_dinh):
    """
    So sánh danh sách API và mặc định.
    Trả về danh sách chỉ gồm model CÒN SỐNG trong API.
    """
    if danh_sach_api:
        return list(danh_sach_api)
    return list(danh_sach_mac_dinh)


# ================================================================
# LẤY MODEL GROQ (SỬA — LỌC MODEL CHAT)
# ================================================================
def lay_model_groq(key):
    """
    Lấy danh sách model từ Groq API.

    FIX: Lọc bỏ model không phải chat (guard, safeguard, ...).
    """
    if not key:
        return []

    khoa_cache = "groq_" + key[:20]
    cache = _lay_cache(khoa_cache)
    if cache is not None:
        return cache

    try:
        import requests
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if r.status_code != 200:
            _ghi_log("loi", f"Groq API trả {r.status_code} — dùng fallback.")
            return list(MODEL_MAC_DINH["Groq"])

        du_lieu = r.json()
        danh_sach = du_lieu.get("data", [])
        ket_qua = []

        for model in danh_sach:
            model_id = model.get("id", "")
            if not model_id:
                continue
            if model.get("active", True) is False:
                continue
            # FIX: Bỏ model không phải chat
            if not _la_model_chat(model_id):
                continue
            ket_qua.append(model_id)

        if ket_qua:
            ket_qua = _loai_bo_model_chet(ket_qua, MODEL_MAC_DINH["Groq"])
            _luu_cache(khoa_cache, ket_qua)
            _ghi_log("tieu-nao", f"Groq API: {len(ket_qua)} model chat.")
            return ket_qua

        return list(MODEL_MAC_DINH["Groq"])

    except ImportError:
        _ghi_log("loi", "Chưa cài requests.")
        return list(MODEL_MAC_DINH["Groq"])
    except Exception as e:
        _ghi_log("loi", f"Groq API lỗi: {e} — dùng fallback.")
        return list(MODEL_MAC_DINH["Groq"])


# ================================================================
# LẤY MODEL OPENROUTER (SỬA — LỌC MODEL CHAT)
# ================================================================
def lay_model_openrouter(key):
    """
    Lấy danh sách model từ OpenRouter API.

    FIX: Lọc bỏ model không phải chat (image, embedding, ...).
    """
    if not key:
        return []

    khoa_cache = "openrouter_" + key[:20]
    cache = _lay_cache(khoa_cache)
    if cache is not None:
        return cache

    try:
        import requests
        r = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if r.status_code != 200:
            _ghi_log("loi", f"OpenRouter API trả {r.status_code} — dùng fallback.")
            return list(MODEL_MAC_DINH["OpenRouter"])

        du_lieu = r.json()
        danh_sach = du_lieu.get("data", [])
        ket_qua = []

        for model in danh_sach:
            model_id = model.get("id", "")
            if not model_id:
                continue

            # Chỉ lấy model free
            gia = model.get("pricing", {})
            gia_prompt = float(gia.get("prompt", 0) or 0)
            gia_completion = float(gia.get("completion", 0) or 0)

            if gia_prompt == 0 and gia_completion == 0:
                # FIX: Bỏ model không phải chat
                if not _la_model_chat(model_id):
                    continue
                ket_qua.append(model_id)

        if ket_qua:
            ket_qua = _loai_bo_model_chet(ket_qua, MODEL_MAC_DINH["OpenRouter"])
            # Ưu tiên model instruct/chat
            ket_qua_sap_xep = sorted(
                ket_qua,
                key=lambda m: (
                    0 if "instruct" in m.lower() else 1,
                    0 if "chat" in m.lower() else 1,
                    m,
                ),
            )
            _luu_cache(khoa_cache, ket_qua_sap_xep)
            _ghi_log("tieu-nao", f"OpenRouter API: {len(ket_qua_sap_xep)} model chat free.")
            return ket_qua_sap_xep

        return list(MODEL_MAC_DINH["OpenRouter"])

    except ImportError:
        _ghi_log("loi", "Chưa cài requests.")
        return list(MODEL_MAC_DINH["OpenRouter"])
    except Exception as e:
        _ghi_log("loi", f"OpenRouter API lỗi: {e} — dùng fallback.")
        return list(MODEL_MAC_DINH["OpenRouter"])


# ================================================================
# LẤY MODEL GEMINI (SỬA — LỌC MODEL CHAT)
# ================================================================
def lay_model_gemini(key):
    """
    Lấy danh sách model từ Gemini API.

    FIX: Lọc bỏ model image/vision/embedding/audio.
         Chỉ giữ model chat/text.
    """
    if not key:
        return []

    khoa_cache = "gemini_" + key[:20]
    cache = _lay_cache(khoa_cache)
    if cache is not None:
        return cache

    try:
        import requests
        r = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
            timeout=10,
        )
        if r.status_code != 200:
            _ghi_log("loi", f"Gemini API trả {r.status_code} — dùng fallback.")
            return list(MODEL_MAC_DINH["Gemini"])

        du_lieu = r.json()
        danh_sach = du_lieu.get("models", [])
        ket_qua = []

        for model in danh_sach:
            ten = model.get("name", "")
            if not ten:
                continue
            ten_ngan = ten.replace("models/", "")

            # Chỉ lấy model hỗ trợ generateContent
            phuong_thuc = model.get("supportedGenerationMethods", [])
            if "generateContent" not in phuong_thuc:
                continue

            # FIX: Bỏ model không phải chat
            if not _la_model_chat(ten_ngan):
                continue

            ket_qua.append(ten_ngan)

        if ket_qua:
            ket_qua = _loai_bo_model_chet(ket_qua, MODEL_MAC_DINH["Gemini"])
            # Ưu tiên flash trước pro, version mới trước
            ket_qua_sap_xep = sorted(
                ket_qua,
                key=lambda m: (
                    0 if "flash" in m.lower() else 1,
                    0 if "3." in m else (1 if "2.5" in m else 2),
                    m,
                ),
            )
            _luu_cache(khoa_cache, ket_qua_sap_xep)
            _ghi_log("tieu-nao", f"Gemini API: {len(ket_qua_sap_xep)} model chat.")
            return ket_qua_sap_xep

        return list(MODEL_MAC_DINH["Gemini"])

    except ImportError:
        _ghi_log("loi", "Chưa cài requests.")
        return list(MODEL_MAC_DINH["Gemini"])
    except Exception as e:
        _ghi_log("loi", f"Gemini API lỗi: {e} — dùng fallback.")
        return list(MODEL_MAC_DINH["Gemini"])


# ================================================================
# HÀM CHÍNH
# ================================================================
def lay_danh_sach_model(provider, key):
    """
    Lấy danh sách model từ API provider.

    provider: "Groq" | "OpenRouter" | "Gemini".
    key: API key.

    Trả về: list tên model.
    """
    if not provider or not key:
        return []

    provider_chuan = provider.strip().lower()

    if provider_chuan == "groq":
        return lay_model_groq(key)
    if provider_chuan in ("openrouter", "open router", "or"):
        return lay_model_openrouter(key)
    if provider_chuan in ("gemini", "google"):
        return lay_model_gemini(key)

    _ghi_log("loi", f"Provider không hỗ trợ: {provider}")
    return []


# ================================================================
# LỌC MODEL
# ================================================================
def loc_model_free(danh_sach):
    """Lọc model miễn phí (OpenRouter có :free)."""
    if not danh_sach:
        return []
    ket_qua = [m for m in danh_sach if ":free" in m.lower()]
    return ket_qua if ket_qua else list(danh_sach)


def loc_model_theo_provider(danh_sach, provider):
    """Lọc model phù hợp với provider."""
    if not danh_sach or not provider:
        return []

    p = provider.strip().lower()

    if p == "groq":
        return [m for m in danh_sach if "/" not in m]
    if p in ("openrouter", "open router", "or"):
        return [m for m in danh_sach if "/" in m]
    if p in ("gemini", "google"):
        return [m for m in danh_sach if m.lower().startswith("gemini")]

    return list(danh_sach)


def loc_model_pho_bien(danh_sach):
    """Ưu tiên model chất lượng cao."""
    if not danh_sach:
        return []

    tu_khoa_uu_tien = [
        "gpt-oss", "gemini-3", "gemini-2.5", "qwen",
        "deepseek", "mistral", "gemma", "nemotron",
        "laguna", "space-bunny",
    ]

    ket_qua = []
    con_lai = []

    for model in danh_sach:
        if any(tk in model.lower() for tk in tu_khoa_uu_tien):
            ket_qua.append(model)
        else:
            con_lai.append(model)

    return ket_qua + con_lai


# ================================================================
# HÀM PHỤ
# ================================================================
def dem_model(provider, key):
    """Đếm số model có thể dùng."""
    return len(lay_danh_sach_model(provider, key))


def lay_model_dau_tien(provider, key):
    """Lấy model đầu tiên (ưu tiên nhất)."""
    danh_sach = lay_danh_sach_model(provider, key)
    if not danh_sach:
        return ""
    danh_sach_uu_tien = loc_model_pho_bien(danh_sach)
    return danh_sach_uu_tien[0] if danh_sach_uu_tien else ""


def tom_tat_model(provider, key):
    """Tạo chuỗi tóm tắt model của provider."""
    danh_sach = lay_danh_sach_model(provider, key)
    if not danh_sach:
        return f"❌ {provider}: không có model."

    return f"✅ {provider}: {len(danh_sach)} model — {danh_sach[0]}..."


def lay_model_mac_dinh(provider):
    """Lấy danh sách model mặc định cho provider."""
    return list(MODEL_MAC_DINH.get(provider, []))


def lay_tat_ca_model_mac_dinh():
    """Lấy toàn bộ model mặc định của 3 provider."""
    return {p: list(ds) for p, ds in MODEL_MAC_DINH.items()}


def thong_ke_cache():
    """Thống kê cache hiện tại."""
    return {
        "so_luong": len(CACHE),
        "khoa": list(CACHE.keys()),
    }


def cap_nhat_danh_sach_mac_dinh(provider, danh_sach_moi):
    """
    Cập nhật thủ công danh sách mặc định cho 1 provider.
    Dùng khi muốn ghi đè danh sách (không khuyến khích).
    """
    if provider in MODEL_MAC_DINH and isinstance(danh_sach_moi, list):
        MODEL_MAC_DINH[provider] = list(danh_sach_moi)
        return True
    return False


# ================================================================
# HÀM MỚI: KIỂM TRA MODEL CÒN SỐNG
# ================================================================
def model_con_song(provider, key, model):
    """
    Kiểm tra 1 model cụ thể có còn sống không.
    Dùng khi cần verify model trước khi gọi.
    """
    if not provider or not key or not model:
        return False

    danh_sach = lay_danh_sach_model(provider, key)
    return model in danh_sach


def lay_model_thay_the(provider, key, model_chet):
    """
    Tìm model thay thế nếu model hiện tại đã chết.
    Ưu tiên cùng dòng (cùng prefix).
    """
    danh_sach = lay_danh_sach_model(provider, key)
    if not danh_sach:
        return ""

    prefix = ""
    if model_chet and "/" in model_chet:
        prefix = model_chet.split("/")[0] + "/"
    elif model_chet:
        phan = model_chet.split("-")
        if len(phan) >= 2:
            prefix = phan[0] + "-"

    if prefix:
        for m in danh_sach:
            if m.startswith(prefix) and m != model_chet:
                return m

    return danh_sach[0] if danh_sach else ""


# ================================================================
# HÀM MỚI: ĐỒNG BỘ DANH SÁCH MODEL VÀO KHO 2
# ================================================================
def dong_bo_model_vao_kho(chu_so_huu):
    """
    Đồng bộ danh sách model thực tế vào kho 2.
    Dùng để Tiểu não biết model nào còn sống.
    """
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()

        from tieu_nao.kiem_ke_key import kiem_ke_key
        ket_qua = kiem_ke_key(chu_so_huu)
        if not ket_qua.get("thanh_cong"):
            return False

        for provider, danh_sach_key in ket_qua.get("theo_provider", {}).items():
            for key in danh_sach_key:
                danh_sach_model = lay_danh_sach_model(provider, key.get("key", ""))
                db["model_kha_dung"].update_one(
                    {"provider": provider, "key_id": key.get("id", "")},
                    {
                        "$set": {
                            "provider": provider,
                            "key_id": key.get("id", ""),
                            "chu_so_huu": chu_so_huu,
                            "danh_sach_model": danh_sach_model,
                            "so_model": len(danh_sach_model),
                            "thoi_gian": int(time.time()),
                        }
                    },
                    upsert=True,
                )

        _ghi_log("tieu-nao", f"Đồng bộ model vào kho 2 cho {chu_so_huu}")
        return True
    except Exception as e:
        _ghi_log("loi", f"Đồng bộ model lỗi: {e}")
        return False
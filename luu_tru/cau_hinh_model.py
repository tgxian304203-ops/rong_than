"""
cau_hinh_model.py - Cấu hình model TRUNG TÂM cho Rồng Thần.

NƠI DUY NHẤT chứa tên model trong toàn dự án.
Đổi model → chỉ sửa file này.

SỬA:
    - OpenRouter: đổi deepseek/deepseek-v4-flash:free
      → nvidia/nemotron-3-super-120b-a12b:free
      (deepseek v4 flash free đã bị OpenRouter xóa)
"""


VAI_TRO_BOSS = "boss"
VAI_TRO_MODEL = "model"


PROVIDER_GROQ = "Groq"
PROVIDER_OPENROUTER = "OpenRouter"
PROVIDER_GEMINI = "Gemini"

DANH_SACH_PROVIDER = [PROVIDER_GROQ, PROVIDER_OPENROUTER, PROVIDER_GEMINI]


# ================================================================
# MODEL CHO BOSS
# ================================================================
MODEL_BOSS = {
    PROVIDER_GROQ: [
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
    ],
    PROVIDER_OPENROUTER: [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "google/gemma-4-31b-it:free",
        "qwen/qwen3.8-27b:free",
        "openai/gpt-oss-120b:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
    ],
    PROVIDER_GEMINI: [
        "gemini-3.1-flash-lite",
    ],
}


# ================================================================
# MODEL CHO MODEL (TIỂU NÃO)
# ================================================================
MODEL_MODEL = {
    PROVIDER_GROQ: [
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
    ],
    PROVIDER_OPENROUTER: [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "nvidia/nemotron-nano-12b-v2-vl:free",
        "google/gemma-4-26b-a4b-it:free",
        "qwen/qwen3.8-27b:free",
    ],
    PROVIDER_GEMINI: [
        "gemini-3.1-flash-lite",
    ],
}


def lay_model(provider, vai_tro=VAI_TRO_BOSS):
    bang = MODEL_MODEL if vai_tro == VAI_TRO_MODEL else MODEL_BOSS
    danh_sach = bang.get(provider, [])
    return danh_sach[0] if danh_sach else ""


def lay_model_boss(provider):
    return lay_model(provider, VAI_TRO_BOSS)


def lay_model_model(provider):
    return lay_model(provider, VAI_TRO_MODEL)


def lay_model_theo_thu_tu(provider, thu_tu=0, vai_tro=VAI_TRO_BOSS):
    bang = MODEL_MODEL if vai_tro == VAI_TRO_MODEL else MODEL_BOSS
    danh_sach = bang.get(provider, [])
    if 0 <= thu_tu < len(danh_sach):
        return danh_sach[thu_tu]
    return ""


def lay_model_du_phong(provider, index, vai_tro=VAI_TRO_BOSS):
    return lay_model_theo_thu_tu(provider, index, vai_tro)


def lay_danh_sach_model(provider, vai_tro=VAI_TRO_BOSS):
    bang = MODEL_MODEL if vai_tro == VAI_TRO_MODEL else MODEL_BOSS
    return list(bang.get(provider, []))


def dem_model(provider, vai_tro=VAI_TRO_BOSS):
    return len(lay_danh_sach_model(provider, vai_tro))


def danh_sach_model_boss():
    return dict(MODEL_BOSS)


def danh_sach_model_model():
    return dict(MODEL_MODEL)


def danh_sach_provider():
    return list(DANH_SACH_PROVIDER)


def la_provider_hop_le(provider):
    return provider in DANH_SACH_PROVIDER


def la_vai_tro_hop_le(vai_tro):
    return vai_tro in (VAI_TRO_BOSS, VAI_TRO_MODEL)


def tom_tat():
    phan = ["=== MODEL BOSS ==="]
    for p in DANH_SACH_PROVIDER:
        ds = MODEL_BOSS.get(p, [])
        phan.append(f"  {p}: {len(ds)} model")
        for i, m in enumerate(ds):
            ghi_chu = " (chính)" if i == 0 else f" (dự phòng {i})"
            phan.append(f"    - {m}{ghi_chu}")

    phan.append("")
    phan.append("=== MODEL MODEL (Tiểu não) ===")
    for p in DANH_SACH_PROVIDER:
        ds = MODEL_MODEL.get(p, [])
        phan.append(f"  {p}: {len(ds)} model")
        for i, m in enumerate(ds):
            ghi_chu = " (chính)" if i == 0 else f" (dự phòng {i})"
            phan.append(f"    - {m}{ghi_chu}")

    return "\n".join(phan)
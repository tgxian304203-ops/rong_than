"""
cau_hinh_model.py - Cấu hình model TRUNG TÂM cho Rồng Thần.

NƠI DUY NHẤT chứa tên model trong toàn dự án.
Đổi model → chỉ sửa file này.

Mỗi provider có DANH SÁCH model (mạnh nhất trước).
Hàm lay_model() lấy model đầu tiên.
Hàm lay_model_du_phong() lấy model tiếp theo khi cần.

CHỈ CHỨA MODEL DÙNG ĐƯỢC VỚI KEY FREE.
"""


# ================================================================
# VAI TRÒ
# ================================================================
VAI_TRO_BOSS = "boss"
VAI_TRO_MODEL = "model"


# ================================================================
# PROVIDER
# ================================================================
PROVIDER_GROQ = "Groq"
PROVIDER_OPENROUTER = "OpenRouter"
PROVIDER_GEMINI = "Gemini"

DANH_SACH_PROVIDER = [PROVIDER_GROQ, PROVIDER_OPENROUTER, PROVIDER_GEMINI]


# ================================================================
# MODEL CHO BOSS (mạnh nhất trước)
# ================================================================
MODEL_BOSS = {
    PROVIDER_GROQ: [
        "qwen/qwen3.8-27b",                # #1 - mạnh nhất (Preview)
        "openai/gpt-oss-120b",             # #2
        "openai/gpt-oss-20b",              # #3
    ],
    PROVIDER_OPENROUTER: [
        "deepseek/deepseek-v4-flash:free", # #1 - mạnh nhất free
        "qwen/qwen3.8-27b:free",           # #2
        "qwen/qwen3-coder:free",           # #3
        "nvidia/nemotron-3-super-120b-a12b:free",  # #4
        "openai/gpt-oss-120b:free",        # #5
    ],
    PROVIDER_GEMINI: [
        "gemini-3.1-flash-lite",           # #1 - duy nhất còn free
    ],
}


# ================================================================
# MODEL CHO MODEL (TIỂU NÃO)
# ================================================================
MODEL_MODEL = {
    PROVIDER_GROQ: [
        "qwen/qwen3.8-27b",                # #1
        "openai/gpt-oss-20b",              # #2 - nhẹ
        "openai/gpt-oss-120b",             # #3
    ],
    PROVIDER_OPENROUTER: [
        "deepseek/deepseek-v4-flash:free", # #1
        "qwen/qwen3-coder:free",           # #2 - code
        "qwen/qwen3.8-27b:free",           # #3
        "openai/gpt-oss-20b:free",         # #4 - nhẹ
    ],
    PROVIDER_GEMINI: [
        "gemini-3.1-flash-lite",           # #1
    ],
}


# ================================================================
# HÀM LẤY MODEL (đầu tiên - mạnh nhất)
# ================================================================
def lay_model(provider, vai_tro=VAI_TRO_BOSS):
    """Lấy model đầu tiên (mạnh nhất)."""
    bang = MODEL_MODEL if vai_tro == VAI_TRO_MODEL else MODEL_BOSS
    danh_sach = bang.get(provider, [])
    return danh_sach[0] if danh_sach else ""


def lay_model_boss(provider):
    """Lấy model Boss đầu tiên."""
    return lay_model(provider, VAI_TRO_BOSS)


def lay_model_model(provider):
    """Lấy model Model đầu tiên."""
    return lay_model(provider, VAI_TRO_MODEL)


# ================================================================
# HÀM LẤY MODEL THEO THỨ TỰ (0 = mạnh nhất)
# ================================================================
def lay_model_theo_thu_tu(provider, thu_tu=0, vai_tro=VAI_TRO_BOSS):
    """
    Lấy model theo thứ tự ưu tiên.

    thu_tu=0 → mạnh nhất.
    thu_tu=1 → mạnh nhì.
    thu_tu=2 → mạnh ba.
    ...
    """
    bang = MODEL_MODEL if vai_tro == VAI_TRO_MODEL else MODEL_BOSS
    danh_sach = bang.get(provider, [])
    if 0 <= thu_tu < len(danh_sach):
        return danh_sach[thu_tu]
    return ""


def lay_model_du_phong(provider, index, vai_tro=VAI_TRO_BOSS):
    """Lấy model dự phòng theo index (giống lay_model_theo_thu_tu)."""
    return lay_model_theo_thu_tu(provider, index, vai_tro)


# ================================================================
# LẤY DANH SÁCH
# ================================================================
def lay_danh_sach_model(provider, vai_tro=VAI_TRO_BOSS):
    """Lấy tất cả model của provider."""
    bang = MODEL_MODEL if vai_tro == VAI_TRO_MODEL else MODEL_BOSS
    return list(bang.get(provider, []))


def dem_model(provider, vai_tro=VAI_TRO_BOSS):
    """Đếm số model của provider."""
    return len(lay_danh_sach_model(provider, vai_tro))


def danh_sach_model_boss():
    return dict(MODEL_BOSS)


def danh_sach_model_model():
    return dict(MODEL_MODEL)


def danh_sach_provider():
    return list(DANH_SACH_PROVIDER)


# ================================================================
# KIỂM TRA
# ================================================================
def la_provider_hop_le(provider):
    return provider in DANH_SACH_PROVIDER


def la_vai_tro_hop_le(vai_tro):
    return vai_tro in (VAI_TRO_BOSS, VAI_TRO_MODEL)


# ================================================================
# TÓM TẮT
# ================================================================
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
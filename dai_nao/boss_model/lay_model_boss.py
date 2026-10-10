"""
lay_model_boss.py - Alias gọi về luu_tru/cau_hinh_model.py.

Không khai báo model ở đây.
Mọi khai báo model nằm ở luu_tru/cau_hinh_model.py.
"""

from luu_tru.cau_hinh_model import (
    lay_model_boss,
    lay_model,
    MODEL_BOSS,
    MODEL_MODEL,
    VAI_TRO_BOSS,
    VAI_TRO_MODEL,
)


# ================================================================
# TƯƠNG THÍCH CODE CŨ
# ================================================================
MODEL_GROQ = MODEL_BOSS.get("Groq", "")
MODEL_OPENROUTER = MODEL_BOSS.get("OpenRouter", "")
MODEL_GEMINI = MODEL_BOSS.get("Gemini", "")


def lay_model_theo_task(provider, loai_task="suy_luan"):
    """Tương thích code cũ."""
    return lay_model_boss(provider)


def danh_sach_model_ho_tro():
    """Tương thích code cũ."""
    return {
        "Groq": [MODEL_GROQ],
        "OpenRouter": [MODEL_OPENROUTER],
        "Gemini": [MODEL_GEMINI],
    }


def la_model_hop_le(provider, model):
    """Kiểm tra model có hợp lệ cho provider không."""
    return model in danh_sach_model_ho_tro().get(provider, [])


def lay_model_mac_dinh():
    """Trả model mặc định (Groq)."""
    return MODEL_GROQ
"""
lay_model_kha_dung.py - Alias gọi về luu_tru/cau_hinh_model.py.

Không khai báo model ở đây.
Mọi khai báo model nằm ở luu_tru/cau_hinh_model.py.
"""

from luu_tru.cau_hinh_model import (
    lay_model as _lay_model,
    lay_model_model as _lay_model_model,
    lay_model_theo_thu_tu as _lay_model_theo_thu_tu,
    lay_danh_sach_model as _lay_danh_sach_model,
    MODEL_MODEL,
    VAI_TRO_MODEL,
)


# ================================================================
# HÀM CHÍNH
# ================================================================
def lay_model_kha_dung(provider):
    """Lấy model Model (Tiểu não) đầu tiên cho provider."""
    return _lay_model_model(provider)


def lay_model_model(provider):
    """Alias rõ nghĩa."""
    return _lay_model_model(provider)


def lay_model_theo_thu_tu(provider, thu_tu=0):
    """Lấy model theo thứ tự ưu tiên (0 = mạnh nhất)."""
    return _lay_model_theo_thu_tu(provider, thu_tu, VAI_TRO_MODEL)


def lay_danh_sach_model(provider):
    """Lấy tất cả model Model của provider."""
    return _lay_danh_sach_model(provider, VAI_TRO_MODEL)


# ================================================================
# TƯƠNG THÍCH CODE CŨ
# ================================================================
MODEL_GROQ = MODEL_MODEL.get("Groq", [""])[0]
MODEL_OPENROUTER = MODEL_MODEL.get("OpenRouter", [""])[0]
MODEL_GEMINI = MODEL_MODEL.get("Gemini", [""])[0]


def lay_model_mac_dinh():
    """Trả model mặc định (Groq)."""
    return MODEL_GROQ


def danh_sach_model_ho_tro():
    """Trả dict model Model."""
    return {
        "Groq": [MODEL_GROQ],
        "OpenRouter": [MODEL_OPENROUTER],
        "Gemini": [MODEL_GEMINI],
    }


def la_model_hop_le(provider, model):
    """Kiểm tra model có hợp lệ cho provider không."""
    return model in lay_danh_sach_model(provider)
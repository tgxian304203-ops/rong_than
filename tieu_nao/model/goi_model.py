"""
goi_model.py - Gọi Model suy luận.

Nhiệm vụ:
    - goi_model(du_lieu): gọi Model trả lời / sinh code.
    - Dò Model khả dụng qua do_model.
    - Gọi API tương ứng (Groq/OpenRouter/Gemini).
    - Nếu lỗi hết quota → xoay key.

Nguyên tắc:
    - Model là công cụ thuần — không giữ ngữ cảnh.
    - Dùng key Model (không dùng key Boss).
    - Không tự suy luận — chỉ gọi API.
"""


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
# GỌI MODEL
# ================================================================
def goi_model(du_lieu):
    """
    Gọi Model trả lời / sinh code.

    du_lieu: {
        noi_dung, lich_su, chu_so_huu,
        id_chat, buoc
    }

    Trả về: {
        thanh_cong, tra_loi, code?, ngon_ngu?, loi?
    }
    """
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    noi_dung = du_lieu.get("noi_dung", "")

    if not noi_dung:
        return {"thanh_cong": False, "loi": "Thiếu nội dung."}

    # 1. Dò Model
    try:
        from tieu_nao.model.do_model import do_model
        model_info = do_model(chu_so_huu)
    except Exception as e:
        return {"thanh_cong": False, "loi": f"Dò Model lỗi: {e}"}

    if not model_info.get("thanh_cong"):
        return {
            "thanh_cong": False,
            "loi": model_info.get("loi", "Không có Model khả dụng."),
        }

    # 2. Gọi API tương ứng
    provider = model_info.get("provider", "")
    key = model_info.get("key", "")
    key_id = model_info.get("key_id", "")

    if provider == "Groq":
        from tieu_nao.model.api.groq_model import goi_groq_model
        ket_qua = goi_groq_model(key, du_lieu)
    elif provider == "OpenRouter":
        from tieu_nao.model.api.openrouter_model import goi_openrouter_model
        ket_qua = goi_openrouter_model(key, du_lieu)
    elif provider == "Gemini":
        from tieu_nao.model.api.gemini_model import goi_gemini_model
        ket_qua = goi_gemini_model(key, du_lieu)
    else:
        return {"thanh_cong": False, "loi": f"Provider không hỗ trợ: {provider}"}

    # 3. Xử lý nếu hết quota
    if not ket_qua.get("thanh_cong"):
        loai_loi = ket_qua.get("loai_loi", "")
        if loai_loi == "het_quota":
            _xu_ly_het_quota(provider, key_id)
            return goi_model(du_lieu)

    return ket_qua


# ================================================================
# GỌI MODEL THEO PROMPT CỤ THỂ
# ================================================================
def goi_model_voi_prompt(prompt, chu_so_huu="khach", lich_su=None):
    """
    Gọi Model với prompt cụ thể.

    Trả về: dict kết quả.
    """
    return goi_model({
        "noi_dung": prompt,
        "chu_so_huu": chu_so_huu,
        "lich_su": lich_su or [],
    })


# ================================================================
# GỌI MODEL SINH CODE
# ================================================================
def goi_model_sinh_code(prompt, chu_so_huu="khach"):
    """Gọi Model sinh code."""
    return goi_model_voi_prompt(prompt, chu_so_huu)


# ================================================================
# GỌI MODEL TRẢ LỜI
# ================================================================
def goi_model_tra_loi(prompt, chu_so_huu="khach", lich_su=None):
    """Gọi Model trả lời câu hỏi."""
    return goi_model_voi_prompt(prompt, chu_so_huu, lich_su)


# ================================================================
# XỬ LÝ HẾT QUOTA
# ================================================================
def _xu_ly_het_quota(provider, key_id):
    """Đánh dấu key hết quota."""
    try:
        from luu_tru.trang_thai_key import danh_dau_het_quota
        danh_dau_het_quota("tieu_boss", provider, key_id)
        _ghi_log("tieu-nao", f"Đánh dấu {provider} hết quota.")
    except Exception:
        pass


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả gọi Model."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        tra_loi = ket_qua.get("tra_loi", "")
        return f"✅ Model OK: {len(tra_loi)} ký tự"
    return f"❌ Model lỗi: {ket_qua.get('loi', '')[:100]}"
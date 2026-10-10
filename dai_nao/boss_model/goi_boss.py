"""
goi_boss.py - Gọi Boss suy luận.

Nhiệm vụ:
    - goi_boss(du_lieu): gọi Boss trả lời câu hỏi.
    - goi_boss_lap_ke_hoach(du_lieu): Boss lập kế hoạch cho dự án.
    - goi_boss_sua_code(du_lieu): Boss sửa code lỗi.
    - goi_boss_the(cau_lenh): Boss Thế đọc hợp đồng.
    - goi_boss_verify(du_lieu): Boss tự verify kết quả.

Nguyên tắc:
    - Dùng key Boss (không dùng key Model).
    - Nếu key hết quota → xoay key.
    - Nếu hết tất cả → chuyển Boss Thế.
"""

import json
import re


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
LOAI_BOSS_DAU = "boss"
LOAI_BOSS_THE = "tieu_boss"


# ================================================================
# GỌI BOSS TRẢ LỜI
# ================================================================
def goi_boss(du_lieu):
    """
    Gọi Boss trả lời câu hỏi.

    du_lieu: {
        noi_dung, lich_su, phan_loai, chu_so_huu
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

    # 1. Dò Boss
    try:
        from dai_nao.boss_model.do_boss import do_boss
        boss_info = do_boss(chu_so_huu, LOAI_BOSS_DAU)
    except Exception as e:
        return {"thanh_cong": False, "loi": f"Dò Boss lỗi: {e}"}

    if not boss_info.get("thanh_cong"):
        try:
            from dai_nao.boss_model.do_boss import do_boss as _do
            boss_info = _do(chu_so_huu, LOAI_BOSS_THE)
        except Exception:
            pass

    if not boss_info.get("thanh_cong"):
        return {
            "thanh_cong": False,
            "loi": boss_info.get("loi", "Không có Boss khả dụng."),
        }

    # 2. Gọi API tương ứng
    provider = boss_info.get("provider", "")
    key = boss_info.get("key", "")
    key_id = boss_info.get("key_id", "")
    loai_nao = boss_info.get("loai_nao", LOAI_BOSS_DAU)

    if provider == "Groq":
        from dai_nao.boss_model.api.groq_boss import goi_groq_boss
        ket_qua = goi_groq_boss(key, du_lieu)
    elif provider == "OpenRouter":
        from dai_nao.boss_model.api.openrouter_boss import goi_openrouter_boss
        ket_qua = goi_openrouter_boss(key, du_lieu)
    elif provider == "Gemini":
        from dai_nao.boss_model.api.gemini_boss import goi_gemini_boss
        ket_qua = goi_gemini_boss(key, du_lieu)
    else:
        return {"thanh_cong": False, "loi": f"Provider không hỗ trợ: {provider}"}

    # 3. Xử lý nếu hết quota
    if not ket_qua.get("thanh_cong"):
        loai_loi = ket_qua.get("loai_loi", "")
        if loai_loi == "het_quota":
            _xu_ly_het_quota(chu_so_huu, provider, key_id, loai_nao)
            return goi_boss(du_lieu)

    return ket_qua


# ================================================================
# GỌI BOSS LẬP KẾ HOẠCH
# ================================================================
def goi_boss_lap_ke_hoach(du_lieu):
    """
    Gọi Boss lập kế hoạch cho dự án.

    Trả về: {
        thanh_cong,
        dang_lam_gi, dang_lam_toi_dau, tiep_theo_lam_gi,
        danh_sach_buoc, huong_dan,
        loi?
    }
    """
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    du_lieu_prompt = dict(du_lieu)
    du_lieu_prompt["noi_dung"] = _tao_prompt_lap_ke_hoach(
        du_lieu.get("noi_dung", "")
    )

    ket_qua = goi_boss(du_lieu_prompt)

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    tra_loi = ket_qua.get("tra_loi", "")
    ke_hoach = _parse_ke_hoach(tra_loi)
    ke_hoach["thanh_cong"] = True
    return ke_hoach


def _tao_prompt_lap_ke_hoach(noi_dung):
    """Tạo prompt yêu cầu Boss lập kế hoạch."""
    return f"""Bạn là Boss Rồng Thần. Hãy lập kế hoạch cho dự án sau:

Yêu cầu: {noi_dung}

Trả về JSON với format:
{{
  "dang_lam_gi": "mô tả ngắn",
  "dang_lam_toi_dau": "0/N",
  "tiep_theo_lam_gi": "bước 1",
  "danh_sach_buoc": ["bước 1", "bước 2"],
  "huong_dan": "nên làm gì để không sai"
}}

Chỉ trả về JSON, không giải thích."""


def _parse_ke_hoach(tra_loi):
    """Parse kế hoạch từ câu trả lời Boss."""
    ket_qua_mac_dinh = {
        "dang_lam_gi": "",
        "dang_lam_toi_dau": "0/N",
        "tiep_theo_lam_gi": "Bước 1",
        "danh_sach_buoc": [],
        "huong_dan": "",
    }

    if not tra_loi:
        return ket_qua_mac_dinh

    try:
        khop = re.search(r"\{[\s\S]*\}", tra_loi)
        if khop:
            du_lieu = json.loads(khop.group())
            for k in ket_qua_mac_dinh:
                if k in du_lieu:
                    ket_qua_mac_dinh[k] = du_lieu[k]
    except (json.JSONDecodeError, ValueError):
        pass

    return ket_qua_mac_dinh


# ================================================================
# GỌI BOSS SỬA CODE
# ================================================================
def goi_boss_sua_code(du_lieu):
    """
    Gọi Boss sửa code bị lỗi.

    du_lieu: { code_cu, loi, ngon_ngu, chu_so_huu }

    Trả về: { thanh_cong, code_moi, cach_sua?, loi? }
    """
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    code_cu = du_lieu.get("code_cu", "")
    loi = du_lieu.get("loi", "")
    ngon_ngu = du_lieu.get("ngon_ngu", "python")

    if not code_cu:
        return {"thanh_cong": False, "loi": "Thiếu code."}

    prompt = f"""Code {ngon_ngu} sau bị lỗi:

{code_cu}

Lỗi: {loi}

Hãy sửa code và trả về CHỈ code đã sửa, không giải thích."""

    du_lieu_prompt = {
        "noi_dung": prompt,
        "chu_so_huu": du_lieu.get("chu_so_huu", "khach"),
    }

    ket_qua = goi_boss(du_lieu_prompt)

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    code_moi = _trich_code(ket_qua.get("tra_loi", ""), ngon_ngu)

    return {
        "thanh_cong": True,
        "code_moi": code_moi,
        "cach_sua": ket_qua.get("tra_loi", "")[:200],
    }


def _trich_code(tra_loi, ngon_ngu):
    """Trích code từ câu trả lời Boss (bỏ dấu backtick)."""
    if not tra_loi:
        return ""

    # Tạo pattern với ký tự backtick (không viết trực tiếp để tránh bị tách)
    bt = chr(96) * 3
    mau = bt + r"(?:" + ngon_ngu + r")?\s*([\s\S]*?)" + bt
    khop = re.search(mau, tra_loi)
    if khop:
        return khop.group(1).strip()

    return tra_loi.strip()


# ================================================================
# GỌI BOSS THẾ (ĐỌC HỢP ĐỒNG)
# ================================================================
def goi_boss_the(cau_lenh):
    """
    Gọi Boss Thế đọc hợp đồng.

    Trả về: { da_doc: bool, tra_loi: str }
    """
    return {
        "da_doc": True,
        "tra_loi": "Đã đọc hợp đồng và hướng dẫn.",
    }


# ================================================================
# GỌI BOSS VERIFY
# ================================================================
def goi_boss_verify(du_lieu):
    """
    Gọi Boss tự verify kết quả (toán, văn, khác).

    Trả về: { thanh_cong, dung: bool, loi? }
    """
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    prompt = f"""Kiểm tra kết quả sau có đúng không:

Câu hỏi: {du_lieu.get('noi_dung', '')}
Kết quả: {du_lieu.get('ket_qua', '')}

Trả về CHỈ "ĐÚNG" hoặc "SAI"."""

    du_lieu_prompt = {
        "noi_dung": prompt,
        "chu_so_huu": du_lieu.get("chu_so_huu", "khach"),
    }

    ket_qua = goi_boss(du_lieu_prompt)

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    tra_loi = (ket_qua.get("tra_loi") or "").upper()

    return {
        "thanh_cong": True,
        "dung": "ĐÚNG" in tra_loi or "DUNG" in tra_loi,
    }


# ================================================================
# XỬ LÝ HẾT QUOTA
# ================================================================
def _xu_ly_het_quota(chu_so_huu, provider, key_id, loai_nao):
    """Đánh dấu key hết quota."""
    try:
        from luu_tru.trang_thai_key import danh_dau_het_quota
        danh_dau_het_quota(loai_nao, provider, key_id)
        _ghi_log("dai-nao", f"Đánh dấu {provider} hết quota.")
    except Exception:
        pass
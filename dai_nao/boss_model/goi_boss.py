"""
goi_boss.py - Gọi Boss suy luận.

SỬA:
    - Thêm hàm goi_boss_nhan_yeu_cau() — Boss nhận yêu cầu trực tiếp.
    - Boss phân loại: đơn giản / dự án.
    - Nếu dự án → lập kế hoạch + hợp đồng + hướng dẫn.
"""

import json
import re


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _in_debug(noi_dung):
    try:
        print(f"[DEBUG-GOI-BOSS] {noi_dung}", flush=True)
    except Exception:
        pass


LOAI_BOSS_DAU = "boss"
LOAI_BOSS_THE = "tieu_boss"


def _lay_boss_kha_dung(chu_so_huu):
    from dai_nao.boss_model.do_boss import do_boss

    _in_debug("--- Thử Boss Đầu (boss) ---")
    boss_info = do_boss(chu_so_huu, LOAI_BOSS_DAU)
    _in_debug(f"Kết quả: thanh_cong={boss_info.get('thanh_cong')}, "
              f"loai_loi={boss_info.get('loai_loi')}")

    if boss_info.get("thanh_cong"):
        return boss_info

    loai_loi = boss_info.get("loai_loi", "")

    if loai_loi == "het_quota":
        _in_debug("Boss Đầu hết quota → thử Boss Thế")
        boss_the = do_boss(chu_so_huu, LOAI_BOSS_THE)
        if boss_the.get("thanh_cong"):
            return boss_the
        return boss_the

    _in_debug(f"Boss Đầu lỗi loai_loi='{loai_loi}' → KHÔNG chuyển Boss Thế")
    return boss_info


def goi_boss_nhan_yeu_cau(du_lieu):
    """
    BOSS NHẬN YÊU CẦU:
        - Đọc yêu cầu.
        - Phân loại: đơn giản / dự án.
        - Nếu dự án → lập kế hoạch + hợp đồng + hướng dẫn.
        - Nếu đơn giản → trả lời.
    """
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    noi_dung = du_lieu.get("noi_dung", "")

    if not noi_dung:
        return {"thanh_cong": False, "loi": "Thiếu nội dung."}

    _in_debug(f"=== BOSS NHẬN YÊU CẦU ===")
    _in_debug(f"chu_so_huu = '{chu_so_huu}'")
    _in_debug(f"noi_dung = {noi_dung[:80]}")

    # 1. Dò Boss
    boss_info = _lay_boss_kha_dung(chu_so_huu)

    if not boss_info.get("thanh_cong"):
        return {
            "thanh_cong": False,
            "loi": boss_info.get("loi", "Không có Boss khả dụng."),
        }

    provider = boss_info.get("provider", "")
    key = boss_info.get("key", "")

    # 2. Gọi Boss phân loại + xử lý
    prompt = _tao_prompt_nhan_yeu_cau(noi_dung)

    du_lieu_prompt = {
        "noi_dung": prompt,
        "chu_so_huu": chu_so_huu,
        "lich_su": du_lieu.get("lich_su", []),
    }

    _in_debug(f"→ Gọi API {provider}")

    if provider == "Groq":
        from dai_nao.boss_model.api.groq_boss import goi_groq_boss
        ket_qua = goi_groq_boss(key, du_lieu_prompt)
    elif provider == "OpenRouter":
        from dai_nao.boss_model.api.openrouter_boss import goi_openrouter_boss
        ket_qua = goi_openrouter_boss(key, du_lieu_prompt)
    elif provider == "Gemini":
        from dai_nao.boss_model.api.gemini_boss import goi_gemini_boss
        ket_qua = goi_gemini_boss(key, du_lieu_prompt)
    else:
        return {"thanh_cong": False, "loi": f"Provider lạ: {provider}"}

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    # 3. Parse kết quả Boss
    tra_loi = ket_qua.get("tra_loi", "")
    _in_debug(f"Boss trả lời: {tra_loi[:200]}")

    ket_qua_parse = _parse_ket_qua_boss(tra_loi)
    ket_qua_parse["thanh_cong"] = True
    return ket_qua_parse


def _tao_prompt_nhan_yeu_cau(noi_dung):
    """Tạo prompt cho Boss nhận yêu cầu."""
    return f"""Bạn là Boss Rồng Thần — bộ não suy luận.

Yêu cầu user: {noi_dung}

Hãy:
1. Phân loại: "don_gian" (toán, văn, hỏi đáp) hay "du_an" (web, app, AI, game).
2. Nếu ĐƠN GIẢN → trả lời trực tiếp.
3. Nếu DỰ ÁN → lập kế hoạch.

Trả về JSON:
{{
  "loai": "don_gian" | "du_an",
  "tra_loi": "câu trả lời (nếu đơn giản)",
  "danh_sach_buoc": ["bước 1", "bước 2"],
  "huong_dan": "nên làm gì để không sai",
  "dang_lam_gi": "mô tả ngắn (nếu dự án)",
  "tiep_theo_lam_gi": "bước 1 (nếu dự án)"
}}

Chỉ trả về JSON, không giải thích."""


def _parse_ket_qua_boss(tra_loi):
    """Parse kết quả Boss."""
    ket_qua = {
        "loai": "don_gian",
        "tra_loi": "",
        "danh_sach_buoc": [],
        "huong_dan": "",
        "dang_lam_gi": "",
        "dang_lam_toi_dau": "0/N",
        "tiep_theo_lam_gi": "",
    }

    if not tra_loi:
        return ket_qua

    try:
        khop = re.search(r"\{[\s\S]*\}", tra_loi)
        if khop:
            du_lieu = json.loads(khop.group())
            for k in ket_qua:
                if k in du_lieu:
                    ket_qua[k] = du_lieu[k]
    except (json.JSONDecodeError, ValueError):
        # Nếu không phải JSON → coi như trả lời đơn giản
        ket_qua["tra_loi"] = tra_loi

    return ket_qua


def goi_boss(du_lieu):
    """Gọi Boss trả lời đơn giản."""
    return goi_boss_nhan_yeu_cau(du_lieu)


def goi_boss_lap_ke_hoach(du_lieu):
    """Gọi Boss lập kế hoạch."""
    return goi_boss_nhan_yeu_cau(du_lieu)


def goi_boss_sua_code(du_lieu):
    """Gọi Boss sửa code."""
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

    ket_qua = goi_boss_nhan_yeu_cau({
        "noi_dung": prompt,
        "chu_so_huu": du_lieu.get("chu_so_huu", "khach"),
    })

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    tra_loi = ket_qua.get("tra_loi", "")
    return {
        "thanh_cong": True,
        "code_moi": _trich_code(tra_loi, ngon_ngu),
        "cach_sua": tra_loi[:200],
    }


def _trich_code(tra_loi, ngon_ngu):
    if not tra_loi:
        return ""

    bt = chr(96) * 3
    mau = bt + r"(?:" + ngon_ngu + r")?\s*([\s\S]*?)" + bt
    khop = re.search(mau, tra_loi)
    if khop:
        return khop.group(1).strip()

    return tra_loi.strip()


def goi_boss_the(cau_lenh):
    return {
        "da_doc": True,
        "tra_loi": "Đã đọc hợp đồng và hướng dẫn.",
    }


def goi_boss_verify(du_lieu):
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    prompt = f"""Kiểm tra kết quả sau có đúng không:

Câu hỏi: {du_lieu.get('noi_dung', '')}
Kết quả: {du_lieu.get('ket_qua', '')}

Trả về CHỈ "ĐÚNG" hoặc "SAI"."""

    ket_qua = goi_boss_nhan_yeu_cau({
        "noi_dung": prompt,
        "chu_so_huu": du_lieu.get("chu_so_huu", "khach"),
    })

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    tra_loi = (ket_qua.get("tra_loi") or "").upper()
    return {
        "thanh_cong": True,
        "dung": "ĐÚNG" in tra_loi or "DUNG" in tra_loi,
    }


def _xu_ly_het_quota(chu_so_huu, provider, key_id, loai_nao):
    try:
        from luu_tru.trang_thai_key import danh_dau_het_quota
        danh_dau_het_quota(loai_nao, provider, key_id)
    except Exception:
        pass
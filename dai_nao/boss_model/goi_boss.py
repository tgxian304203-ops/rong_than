"""
goi_boss.py - Gọi Boss suy luận.

SỬA:
    - Thêm hàm _la_code_that() kiểm tra code hợp lệ.
    - goi_boss_sua_code() không trả câu tiếng Việt làm code.
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


def _la_code_that(code, ngon_ngu):
    """
    Kiểm tra code có phải code thật không.

    - Python → phải parse được bằng ast.
    - HTML → phải có thẻ HTML.
    - CSS → phải có { }.
    - JS → phải có function/const/let/var.
    """
    if not code:
        return False

    code = code.strip()
    if not code:
        return False

    ngon_ngu = (ngon_ngu or "").lower().strip()

    # Python
    if ngon_ngu == "python":
        try:
            import ast
            ast.parse(code)
            return True
        except SyntaxError:
            return False
        except Exception:
            return False

    # HTML
    if ngon_ngu == "html":
        return bool(re.search(r"<[a-z]", code, re.I))

    # CSS
    if ngon_ngu == "css":
        return "{" in code and "}" in code

    # JavaScript / TypeScript
    if ngon_ngu in ("javascript", "js", "typescript", "ts"):
        return bool(re.search(r"\b(function|const|let|var|=>|class|import|export)\b", code))

    # Khác → chấp nhận
    return True


def goi_boss_nhan_yeu_cau(du_lieu):
    """BOSS NHẬN YÊU CẦU: phân loại + lập kế hoạch."""
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    noi_dung = du_lieu.get("noi_dung", "")

    if not noi_dung:
        return {"thanh_cong": False, "loi": "Thiếu nội dung."}

    _in_debug(f"=== BOSS NHẬN YÊU CẦU ===")
    _in_debug(f"chu_so_huu = '{chu_so_huu}'")

    boss_info = _lay_boss_kha_dung(chu_so_huu)

    if not boss_info.get("thanh_cong"):
        return {
            "thanh_cong": False,
            "loi": boss_info.get("loi", "Không có Boss khả dụng."),
        }

    provider = boss_info.get("provider", "")
    key = boss_info.get("key", "")

    prompt = _tao_prompt_nhan_yeu_cau(noi_dung)

    du_lieu_prompt = {
        "noi_dung": prompt,
        "chu_so_huu": chu_so_huu,
        "lich_su": du_lieu.get("lich_su", []),
    }

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

    tra_loi = ket_qua.get("tra_loi", "")
    ket_qua_parse = _parse_ket_qua_boss(tra_loi)
    ket_qua_parse["thanh_cong"] = True
    return ket_qua_parse


def _tao_prompt_nhan_yeu_cau(noi_dung):
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
        ket_qua["tra_loi"] = tra_loi

    return ket_qua


def goi_boss(du_lieu):
    return goi_boss_nhan_yeu_cau(du_lieu)


def goi_boss_lap_ke_hoach(du_lieu):
    return goi_boss_nhan_yeu_cau(du_lieu)


def goi_boss_sua_code(du_lieu):
    """
    Gọi Boss sửa code.

    SỬA: kiểm tra code_moi có phải code thật không.
    """
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    code_cu = du_lieu.get("code_cu", "")
    loi = du_lieu.get("loi", "")
    ngon_ngu = du_lieu.get("ngon_ngu", "python")

    if not code_cu:
        return {"thanh_cong": False, "loi": "Thiếu code."}

    _in_debug(f"=== SỬA CODE ({ngon_ngu}) ===")

    prompt = f"""Code {ngon_ngu} sau bị lỗi:

```{ngon_ngu}
{code_cu}
```

Lỗi: {loi}

Hãy sửa code và trả về CHỈ code đã sửa trong khối markdown ```{ngon_ngu} ... ```.
KHÔNG giải thích, KHÔNG trả lời bằng văn bản."""

    ket_qua = goi_boss_nhan_yeu_cau({
        "noi_dung": prompt,
        "chu_so_huu": du_lieu.get("chu_so_huu", "khach"),
    })

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    tra_loi = ket_qua.get("tra_loi", "")
    code_moi = _trich_code(tra_loi, ngon_ngu)

    _in_debug(f"code_moi (100 ký tự) = {code_moi[:100] if code_moi else 'RỖNG'}")

    # Kiểm tra code_moi có phải code thật không
    if not code_moi:
        _in_debug("❌ code_moi RỖNG")
        return {
            "thanh_cong": False,
            "loi": "Boss không trả về code.",
            "tra_loi": tra_loi,
        }

    if not _la_code_that(code_moi, ngon_ngu):
        _in_debug(f"❌ code_moi KHÔNG phải code hợp lệ")
        return {
            "thanh_cong": False,
            "loi": "Boss trả về nội dung không phải code.",
            "tra_loi": tra_loi,
        }

    _in_debug(f"✅ code_moi OK ({len(code_moi)} ký tự)")

    return {
        "thanh_cong": True,
        "code_moi": code_moi,
        "cach_sua": tra_loi[:200],
    }


def _trich_code(tra_loi, ngon_ngu):
    """
    Trích code từ câu trả lời Boss.

    SỬA: kiểm tra code tìm được có hợp lệ không.
    """
    if not tra_loi:
        return ""

    bt = chr(96) * 3

    # Thử tìm code có ghi ngôn ngữ
    mau = bt + ngon_ngu + r"\s*([\s\S]*?)" + bt
    khop = re.search(mau, tra_loi, re.IGNORECASE)
    if khop:
        code = khop.group(1).strip()
        if _la_code_that(code, ngon_ngu):
            return code

    # Thử tìm code không ghi ngôn ngữ
    mau = bt + r"(?:\w+)?\s*([\s\S]*?)" + bt
    khop = re.search(mau, tra_loi)
    if khop:
        code = khop.group(1).strip()
        if _la_code_that(code, ngon_ngu):
            return code

    # Không có code block → kiểm tra toàn bộ tra_loi
    # (chỉ khi toàn bộ là code hợp lệ)
    if _la_code_that(tra_loi, ngon_ngu):
        return tra_loi.strip()

    return ""


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
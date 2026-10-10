"""
goi_boss.py - Gọi Boss suy luận.

SỬA:
    - Chỉ chuyển Boss Đầu → Boss Thế khi HẾT QUOTA.
    - Nếu lỗi khác (không có key, sai key...) → trả lỗi luôn.
    - Thêm DEBUG.
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
    """
    Lấy Boss khả dụng.

    Logic:
        1. Thử Boss Đầu.
        2. Nếu Boss Đầu lỗi → kiểm tra loai_loi:
           - "het_quota" → thử Boss Thế.
           - Lỗi khác → trả lỗi luôn.
    """
    from dai_nao.boss_model.do_boss import do_boss

    _in_debug("--- Thử Boss Đầu (boss) ---")
    boss_info = do_boss(chu_so_huu, LOAI_BOSS_DAU)
    _in_debug(f"Kết quả: thanh_cong={boss_info.get('thanh_cong')}, "
              f"loai_loi={boss_info.get('loai_loi')}, "
              f"loi={boss_info.get('loi', '')[:100]}")

    if boss_info.get("thanh_cong"):
        return boss_info

    loai_loi = boss_info.get("loai_loi", "")

    # Chỉ chuyển sang Boss Thế khi HẾT QUOTA
    if loai_loi == "het_quota":
        _in_debug("Boss Đầu hết quota → thử Boss Thế")
        boss_the = do_boss(chu_so_huu, LOAI_BOSS_THE)
        _in_debug(f"Kết quả Boss Thế: thanh_cong={boss_the.get('thanh_cong')}, "
                  f"loai_loi={boss_the.get('loai_loi')}, "
                  f"loi={boss_the.get('loi', '')[:100]}")

        if boss_the.get("thanh_cong"):
            return boss_the

        return boss_the

    # Lỗi khác (không có key, sai loai...) → trả lỗi luôn
    _in_debug(f"Boss Đầu lỗi loai_loi='{loai_loi}' → KHÔNG chuyển Boss Thế")
    return boss_info


def goi_boss(du_lieu):
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    noi_dung = du_lieu.get("noi_dung", "")

    if not noi_dung:
        return {"thanh_cong": False, "loi": "Thiếu nội dung."}

    _in_debug("=== GỌI BOSS ===")
    _in_debug(f"chu_so_huu = '{chu_so_huu}'")
    _in_debug(f"noi_dung = {noi_dung[:80]}")

    boss_info = _lay_boss_kha_dung(chu_so_huu)

    if not boss_info.get("thanh_cong"):
        _in_debug(f"❌ Không có Boss khả dụng: {boss_info.get('loi', '')}")
        return {
            "thanh_cong": False,
            "loi": boss_info.get("loi", "Không có Boss khả dụng."),
        }

    provider = boss_info.get("provider", "")
    key = boss_info.get("key", "")
    key_id = boss_info.get("key_id", "")
    loai_nao = boss_info.get("loai_nao", LOAI_BOSS_DAU)

    _in_debug(f"→ Gọi API {provider} với loai_nao={loai_nao}")

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

    # Nếu hết quota → đánh dấu + thử key khác
    if not ket_qua.get("thanh_cong"):
        if ket_qua.get("loai_loi") == "het_quota":
            _in_debug(f"Key {provider} hết quota → thử key khác")
            _xu_ly_het_quota(chu_so_huu, provider, key_id, loai_nao)
            return goi_boss(du_lieu)

    return ket_qua


def goi_boss_lap_ke_hoach(du_lieu):
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


def goi_boss_sua_code(du_lieu):
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    code_cu = du_lieu.get("code_cu", "")
    loi = du_lieu.get("loi", "")
    ngon_ngu = du_lieu.get("ngon_ngu", "python")

    if not code_cu:
        return {"thanh_cong": False, "loi": "Thiếu code."}

    prompt = f"""Code {ngon_ngu} sau bị lỗi:
```{ngon_ngu}
{code_cu}
```

Lỗi: {loi}

Hãy sửa code và trả về CHỈ code đã sửa, không giải thích."""

    ket_qua = goi_boss({
        "noi_dung": prompt,
        "chu_so_huu": du_lieu.get("chu_so_huu", "khach"),
    })

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    return {
        "thanh_cong": True,
        "code_moi": _trich_code(ket_qua.get("tra_loi", ""), ngon_ngu),
        "cach_sua": ket_qua.get("tra_loi", "")[:200],
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

    ket_qua = goi_boss({
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
        _ghi_log("dai-nao", f"Đánh dấu {provider} hết quota.")
    except Exception:
        pass
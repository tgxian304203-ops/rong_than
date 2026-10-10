"""
gemini_boss.py - Kết nối Gemini API cho Boss.

Nhiệm vụ:
    - goi_gemini_boss(key, du_lieu): gọi Gemini API.
    - kiem_tra_key_gemini_boss(key): kiểm tra key.

Quy tắc:
    - Endpoint: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
    - Auth: key dạng query param.
    - Key format: AIza... hoặc AQ.Ab...

Nguyên tắc:
    - KHÔNG hardcode model — gọi lay_model_boss("Gemini").
    - Đổi model chỉ cần sửa lay_model_boss.py.
"""

import requests

from dai_nao.boss_model.lay_model_boss import lay_model_boss


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
URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/models"
TIMEOUT = 60


# ================================================================
# GỌI GEMINI BOSS
# ================================================================
def goi_gemini_boss(key, du_lieu):
    """
    Gọi Gemini API cho Boss.

    Trả về: { thanh_cong, tra_loi, loai_loi?, loi? }
    """
    ket_qua = {
        "thanh_cong": False,
        "tra_loi": "",
        "loai_loi": "",
        "loi": "",
    }

    if not key:
        ket_qua["loi"] = "Thiếu key Gemini."
        ket_qua["loai_loi"] = "key_sai"
        return ket_qua

    noi_dung = du_lieu.get("noi_dung", "")
    if not noi_dung:
        ket_qua["loi"] = "Thiếu nội dung."
        return ket_qua

    # Lấy model từ lay_model_boss
    model = du_lieu.get("model") or lay_model_boss("Gemini")
    url = f"{URL_GEMINI}/{model}:generateContent?key={key}"

    body = {
        "contents": _tao_contents(du_lieu),
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 4096,
        },
    }

    try:
        r = requests.post(url, json=body, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        ket_qua["loi"] = "Gemini timeout."
        ket_qua["loai_loi"] = "timeout"
        return ket_qua
    except requests.exceptions.ConnectionError:
        ket_qua["loi"] = "Không kết nối được Gemini."
        ket_qua["loai_loi"] = "loi_mang"
        return ket_qua
    except Exception as e:
        ket_qua["loi"] = f"Lỗi gọi Gemini: {e}"
        ket_qua["loai_loi"] = "khac"
        return ket_qua

    if r.status_code == 429:
        ket_qua["loi"] = "Gemini hết quota (429)."
        ket_qua["loai_loi"] = "het_quota"
        return ket_qua
    if r.status_code in (401, 403):
        ket_qua["loi"] = "Key Gemini sai hoặc hết hạn."
        ket_qua["loai_loi"] = "key_sai"
        return ket_qua
    if r.status_code == 404:
        ket_qua["loi"] = f"Model Gemini không tồn tại: {model}"
        ket_qua["loai_loi"] = "khong_tim_thay"
        return ket_qua
    if r.status_code != 200:
        ket_qua["loi"] = f"Gemini trả {r.status_code}: {r.text[:200]}"
        ket_qua["loai_loi"] = "loi_server"
        return ket_qua

    try:
        du_lieu_tra = r.json()
        tra_loi = du_lieu_tra["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, ValueError) as e:
        ket_qua["loi"] = f"Parse Gemini lỗi: {e}"
        ket_qua["loai_loi"] = "loi_parse"
        return ket_qua

    ket_qua["thanh_cong"] = True
    ket_qua["tra_loi"] = tra_loi

    _ghi_log("dai-nao", f"Gemini Boss OK: {len(tra_loi)} ký tự")
    return ket_qua


def _tao_contents(du_lieu):
    """Tạo mảng contents cho Gemini API."""
    contents = []

    phan = [_tao_system_prompt()]

    lich_su = du_lieu.get("lich_su") or []
    for tin in lich_su[-10:]:
        vai_tro = tin.get("vai_tro", "user")
        noi_dung = tin.get("noi_dung", "")
        if not noi_dung:
            continue

        if vai_tro in ("rong_than", "rong"):
            vai_tro_gemini = "model"
        elif vai_tro in ("nguoi_dung", "nguoi"):
            vai_tro_gemini = "user"
        else:
            continue

        contents.append({
            "role": vai_tro_gemini,
            "parts": [{"text": noi_dung}],
        })

    contents.append({
        "role": "user",
        "parts": [{"text": du_lieu.get("noi_dung", "")}],
    })

    if phan and phan[0]:
        contents.insert(0, {
            "role": "user",
            "parts": [{"text": phan[0]}],
        })

    return contents


def _tao_system_prompt():
    """Tạo system prompt cho Boss."""
    return (
        "[HỆ THỐNG] Bạn là Rồng Thần — AI Agent tự trị thông minh. "
        "Trả lời ngắn gọn, đúng trọng tâm. "
        "Nếu cần code, viết code trong dấu 3 backtick kèm ngôn ngữ. "
        "Không lan man, không dài dòng."
    )


def kiem_tra_key_gemini_boss(key):
    """Kiểm tra key Gemini còn hiệu lực không."""
    if not key:
        return False, "Thiếu key."

    if not (key.startswith("AIza") or key.startswith("AQ.Ab")):
        return False, "Key không đúng format."

    try:
        r = requests.get(
            f"{URL_GEMINI}?key={key}",
            timeout=10,
        )

        if r.status_code == 200:
            return True, ""
        if r.status_code in (401, 403):
            return False, "Key sai hoặc hết hạn."
        if r.status_code == 429:
            return False, "Hết quota."

        return False, f"Gemini trả {r.status_code}."
    except Exception as e:
        return False, f"Lỗi kiểm tra key: {e}"


def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả Gemini Boss."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ Gemini Boss: {len(ket_qua.get('tra_loi', ''))} ký tự"
    return f"❌ Gemini Boss [{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')[:100]}"
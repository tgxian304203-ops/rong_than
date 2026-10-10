"""
groq_boss.py - Kết nối Groq API cho Boss.

Nhiệm vụ:
    - goi_groq_boss(key, du_lieu): gọi Groq API.
    - kiem_tra_key_groq_boss(key): kiểm tra key.

Quy tắc:
    - Endpoint: https://api.groq.com/openai/v1/chat/completions
    - Auth: Bearer <key>.
    - Key format: gsk_xxx.

Nguyên tắc:
    - KHÔNG hardcode model — gọi lay_model_boss("Groq").
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
URL_GROQ = "https://api.groq.com/openai/v1/chat/completions"
TIMEOUT = 60


# ================================================================
# GỌI GROQ BOSS
# ================================================================
def goi_groq_boss(key, du_lieu):
    """
    Gọi Groq API cho Boss.

    Trả về: { thanh_cong, tra_loi, loai_loi?, loi? }
    """
    ket_qua = {
        "thanh_cong": False,
        "tra_loi": "",
        "loai_loi": "",
        "loi": "",
    }

    if not key:
        ket_qua["loi"] = "Thiếu key Groq."
        ket_qua["loai_loi"] = "key_sai"
        return ket_qua

    noi_dung = du_lieu.get("noi_dung", "")
    if not noi_dung:
        ket_qua["loi"] = "Thiếu nội dung."
        return ket_qua

    # Lấy model từ lay_model_boss
    model = du_lieu.get("model") or lay_model_boss("Groq")
    tin_nhan = _tao_tin_nhan(du_lieu)

    body = {
        "model": model,
        "messages": tin_nhan,
        "temperature": 0.7,
        "max_tokens": 4096,
    }

    try:
        r = requests.post(
            URL_GROQ,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=TIMEOUT,
        )
    except requests.exceptions.Timeout:
        ket_qua["loi"] = "Groq timeout."
        ket_qua["loai_loi"] = "timeout"
        return ket_qua
    except requests.exceptions.ConnectionError:
        ket_qua["loi"] = "Không kết nối được Groq."
        ket_qua["loai_loi"] = "loi_mang"
        return ket_qua
    except Exception as e:
        ket_qua["loi"] = f"Lỗi gọi Groq: {e}"
        ket_qua["loai_loi"] = "khac"
        return ket_qua

    if r.status_code == 429:
        ket_qua["loi"] = "Groq hết quota (429)."
        ket_qua["loai_loi"] = "het_quota"
        return ket_qua
    if r.status_code in (401, 403):
        ket_qua["loi"] = "Key Groq sai hoặc hết hạn."
        ket_qua["loai_loi"] = "key_sai"
        return ket_qua
    if r.status_code == 404:
        ket_qua["loi"] = f"Model Groq không tồn tại: {model}"
        ket_qua["loai_loi"] = "khong_tim_thay"
        return ket_qua
    if r.status_code != 200:
        ket_qua["loi"] = f"Groq trả {r.status_code}: {r.text[:200]}"
        ket_qua["loai_loi"] = "loi_server"
        return ket_qua

    try:
        du_lieu_tra = r.json()
        tra_loi = du_lieu_tra["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as e:
        ket_qua["loi"] = f"Parse Groq lỗi: {e}"
        ket_qua["loai_loi"] = "loi_parse"
        return ket_qua

    ket_qua["thanh_cong"] = True
    ket_qua["tra_loi"] = tra_loi

    _ghi_log("dai-nao", f"Groq Boss OK: {len(tra_loi)} ký tự")
    return ket_qua


# ================================================================
# TẠO TIN NHẮN
# ================================================================
def _tao_tin_nhan(du_lieu):
    """Tạo mảng tin nhắn cho Groq API."""
    tin_nhan = []

    tin_nhan.append({
        "role": "system",
        "content": _tao_system_prompt(),
    })

    lich_su = du_lieu.get("lich_su") or []
    for tin in lich_su[-10:]:
        vai_tro = tin.get("vai_tro", "user")
        if vai_tro in ("rong_than", "rong"):
            vai_tro = "assistant"
        elif vai_tro in ("nguoi_dung", "nguoi"):
            vai_tro = "user"
        else:
            continue

        noi_dung = tin.get("noi_dung", "")
        if noi_dung:
            tin_nhan.append({"role": vai_tro, "content": noi_dung})

    tin_nhan.append({
        "role": "user",
        "content": du_lieu.get("noi_dung", ""),
    })

    return tin_nhan


def _tao_system_prompt():
    """Tạo system prompt cho Boss."""
    return (
        "Bạn là Rồng Thần — AI Agent tự trị thông minh. "
        "Trả lời ngắn gọn, đúng trọng tâm. "
        "Nếu cần code, viết code trong dấu 3 backtick kèm ngôn ngữ. "
        "Không lan man, không dài dòng."
    )


# ================================================================
# KIỂM TRA KEY
# ================================================================
def kiem_tra_key_groq_boss(key):
    """Kiểm tra key Groq còn hiệu lực không."""
    if not key:
        return False, "Thiếu key."

    if not key.startswith("gsk_"):
        return False, "Key không đúng format (phải bắt đầu bằng gsk_)."

    try:
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )

        if r.status_code == 200:
            return True, ""
        if r.status_code == 401:
            return False, "Key sai hoặc hết hạn."
        if r.status_code == 429:
            return False, "Hết quota."

        return False, f"Groq trả {r.status_code}."
    except Exception as e:
        return False, f"Lỗi kiểm tra key: {e}"


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả Groq Boss."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ Groq Boss: {len(ket_qua.get('tra_loi', ''))} ký tự"
    return f"❌ Groq Boss [{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')[:100]}"
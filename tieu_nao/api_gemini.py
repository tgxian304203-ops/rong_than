"""
api_gemini.py - Kết nối Gemini API Rồng Thần.

Nhiệm vụ:
    - goi_gemini(key, model, prompt, ...): gọi Gemini API.
    - lay_model_gemini(key): lấy danh sách model.
    - kiem_tra_key_gemini(key): kiểm tra key.
    - _xu_ly_loi_gemini(status_code, text): phân tích lỗi.

Quy tắc:
    - Endpoint: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
    - Auth: x-goog-api-key header HOẶC ?key= query param.
    - Timeout: 30 giây.
    - Hỗ trợ generateContent + streamGenerateContent (SSE).

Trả về:
    {
        thanh_cong: bool,
        ket_qua: str,
        loi: str,
        loai_loi: str,      # "het_quota" | "key_sai" | "model_chet" | "khac"
        thoi_gian: float,
    }

Tầng dữ liệu: Không.
"""

import time


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
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
TIMEOUT = 30


# ================================================================
# GỌI GEMINI API
# ================================================================
def goi_gemini(key, model, prompt, temperature=0.7, max_tokens=None,
               he_thong=None, streaming=False):
    """
    Gọi Gemini API.

    key: API key.
    model: tên model (gemini-3.8-flash, gemini-2.5-flash-lite, ...).
    prompt: câu hỏi.
    temperature: 0.0-2.0.
    max_tokens: giới hạn output.
    he_thong: system instruction.
    streaming: True → streamGenerateContent (SSE).

    Trả về: dict kết quả (không streaming) hoặc generator.
    """
    ket_qua = {
        "thanh_cong": False,
        "ket_qua": "",
        "loi": "",
        "loai_loi": "",
        "thoi_gian": 0.0,
    }

    if not key or not model or not prompt:
        ket_qua["loi"] = "Thiếu key, model hoặc prompt."
        return ket_qua

    thoi_gian_bat_dau = time.time()

    try:
        import requests
    except ImportError:
        ket_qua["loi"] = "Chưa cài requests."
        return ket_qua

    # Endpoint
    method = "streamGenerateContent" if streaming else "generateContent"
    url = f"{BASE_URL}/{model}:{method}?alt=sse" if streaming else f"{BASE_URL}/{model}:{method}"

    # Headers
    headers = {
        "x-goog-api-key": key,
        "Content-Type": "application/json",
    }

    # Body
    contents = [{
        "parts": [{"text": prompt}],
    }]

    body = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
        },
    }
    if max_tokens:
        body["generationConfig"]["maxOutputTokens"] = max_tokens
    if he_thong:
        body["systemInstruction"] = {
            "parts": [{"text": he_thong}],
        }

    try:
        r = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=TIMEOUT,
            stream=streaming,
        )

        # Streaming
        if streaming and r.status_code == 200:
            ket_qua["thanh_cong"] = True
            ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
            return _xu_ly_stream(r, ket_qua)

        # Không streaming
        if r.status_code == 200:
            try:
                du_lieu = r.json()
                noi_dung = du_lieu["candidates"][0]["content"]["parts"][0]["text"]
                ket_qua["thanh_cong"] = True
                ket_qua["ket_qua"] = noi_dung
            except (KeyError, IndexError, ValueError):
                ket_qua["loi"] = "Gemini trả về không đúng format."
            ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
            return ket_qua

        # Lỗi
        ket_qua["loi"], ket_qua["loai_loi"] = _xu_ly_loi_gemini(
            r.status_code, r.text[:500]
        )
        ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
        return ket_qua

    except Exception as e:
        ket_qua["loi"] = f"Lỗi gọi Gemini: {e}"
        ket_qua["loai_loi"] = "khac"
        ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
        return ket_qua


# ================================================================
# XỬ LÝ STREAM
# ================================================================
def _xu_ly_stream(response, ket_qua):
    """Xử lý response streaming của Gemini (SSE)."""
    def _gen():
        try:
            import json
            for dong in response.iter_lines():
                if not dong:
                    continue
                dong = dong.decode("utf-8").strip()
                if dong.startswith("data: "):
                    du_lieu = dong[6:]
                    try:
                        obj = json.loads(du_lieu)
                        candidates = obj.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                text = parts[0].get("text", "")
                                if text:
                                    yield text
                    except (ValueError, KeyError, IndexError):
                        continue
        except Exception as e:
            _ghi_log("loi", f"Gemini stream lỗi: {e}")

    return _gen()


# ================================================================
# XỬ LÝ LỖI
# ================================================================
def _xu_ly_loi_gemini(status_code, text):
    """
    Phân tích lỗi Gemini.

    Trả về: (mô_tả, loai_loi).
    """
    text_lower = (text or "").lower()

    if status_code == 400:
        # Có thể do model không hợp lệ hoặc request sai
        if "model" in text_lower and ("not found" in text_lower or "invalid" in text_lower):
            return f"Model không hợp lệ (400).", "model_chet"
        return f"Request sai (400): {text[:200]}", "khac"
    if status_code == 401:
        return "Key sai hoặc hết hạn (401).", "key_sai"
    if status_code == 403:
        return "Không có quyền (403).", "key_sai"
    if status_code == 404:
        return f"Model không tồn tại (404).", "model_chet"
    if status_code == 429:
        # RESOURCE_EXHAUSTED
        if "quota" in text_lower or "resource" in text_lower:
            return "Hết quota (429).", "het_quota"
        return "Vượt rate limit (429).", "het_quota"
    if 500 <= status_code < 600:
        return f"Server Gemini lỗi ({status_code}).", "khac"

    return f"Gemini trả {status_code}: {text[:200]}", "khac"


# ================================================================
# LẤY DANH SÁCH MODEL
# ================================================================
def lay_model_gemini(key):
    """
    Lấy danh sách model từ Gemini API.

    Chỉ lấy model hỗ trợ generateContent.

    Trả về: list tên model.
    """
    if not key:
        return []

    try:
        import requests
        r = requests.get(
            f"{BASE_URL}?key={key}",
            timeout=10,
        )
        if r.status_code != 200:
            return []

        du_lieu = r.json()
        danh_sach = du_lieu.get("models", [])
        ket_qua = []

        for model in danh_sach:
            ten = model.get("name", "")
            if not ten:
                continue
            ten_ngan = ten.replace("models/", "")

            # Chỉ lấy model hỗ trợ generateContent
            phuong_thuc = model.get("supportedGenerationMethods", [])
            if "generateContent" not in phuong_thuc:
                continue

            ket_qua.append(ten_ngan)

        # Sắp xếp: flash trước, version mới trước
        ket_qua_sap_xep = sorted(
            ket_qua,
            key=lambda m: (
                0 if "flash" in m.lower() else 1,
                0 if "3." in m else (1 if "2.5" in m else 2),
                m,
            ),
        )
        return ket_qua_sap_xep

    except ImportError:
        return []
    except Exception:
        return []


# ================================================================
# KIỂM TRA KEY
# ================================================================
def kiem_tra_key_gemini(key):
    """
    Kiểm tra key Gemini còn hiệu lực không.

    Trả về: (True, "") nếu OK.
    """
    if not key:
        return False, "Thiếu key."

    try:
        import requests
        r = requests.get(
            f"{BASE_URL}?key={key}",
            timeout=10,
        )
        if r.status_code == 200:
            return True, ""
        if r.status_code in (401, 403):
            return False, "Key sai hoặc hết hạn."
        return False, f"Gemini trả {r.status_code}."
    except ImportError:
        return False, "Chưa cài requests."
    except Exception as e:
        return False, f"Lỗi kiểm tra key: {e}"


# ================================================================
# HÀM PHỤ: GỌI NHANH
# ================================================================
def goi_nhanh(key, model, prompt):
    """Gọi nhanh temperature 0.7."""
    return goi_gemini(key, model, prompt, temperature=0.7)


def goi_chinh_xac(key, model, prompt):
    """Gọi chính xác temperature thấp."""
    return goi_gemini(key, model, prompt, temperature=0.2)


def goi_sang_tao(key, model, prompt):
    """Gọi sáng tạo temperature cao."""
    return goi_gemini(key, model, prompt, temperature=1.2)


# ================================================================
# HÀM PHỤ: LẤY MODEL MẶC ĐỊNH
# ================================================================
def lay_model_mac_dinh():
    """
    Trả về danh sách model Gemini mặc định (tháng 10/2026).

    Lưu ý: Từ 9/10/2026, free tier chỉ còn dòng Flash-Lite.
    """
    return [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]


def lay_model_free_sau_9_10():
    """
    Model free SAU ngày 9/10/2026 (chỉ còn Flash-Lite).
    """
    return [
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash-lite",
    ]


# ================================================================
# HÀM PHỤ: KIỂM TRA MODEL CÒN SỐNG
# ================================================================
def model_con_song(key, model):
    """Kiểm tra model có trong danh sách API không."""
    danh_sach = lay_model_gemini(key)
    return model in danh_sach


# ================================================================
# HÀM PHỤ: TÓM TẮT KẾT QUẢ
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả gọi Gemini."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return (
            f"✅ Gemini OK ({ket_qua.get('thoi_gian', 0)}s): "
            f"{ket_qua.get('ket_qua', '')[:60]}..."
        )

    return f"❌ Gemini lỗi [{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')}"


# ================================================================
# HÀM PHỤ: ĐẾM MODEL
# ================================================================
def dem_model(key):
    """Đếm số model có thể dùng."""
    return len(lay_model_gemini(key))
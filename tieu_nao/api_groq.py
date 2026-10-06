"""
api_groq.py - Kết nối Groq API Rồng Thần.

Nhiệm vụ:
    - goi_groq(key, model, prompt, ...): gọi Groq API.
    - lay_model_groq(key): lấy danh sách model.
    - kiem_tra_key_groq(key): kiểm tra key còn hiệu lực.
    - _xu_ly_loi_groq(status_code, text): phân tích lỗi.

Quy tắc:
    - Endpoint: https://api.groq.com/openai/v1/chat/completions
    - Auth: Bearer <key>
    - Timeout: 30 giây
    - Xử lý 6 mã lỗi: 200, 400, 401, 403, 404, 429, 5xx
    - Hỗ trợ streaming (tùy chọn)

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
URL_GROQ = "https://api.groq.com/openai/v1/chat/completions"
URL_GROQ_MODELS = "https://api.groq.com/openai/v1/models"
TIMEOUT = 30


# ================================================================
# GỌI GROQ API
# ================================================================
def goi_groq(key, model, prompt, temperature=0.7, max_tokens=None,
             he_thong=None, streaming=False):
    """
    Gọi Groq API.

    key: API key.
    model: tên model.
    prompt: câu hỏi.
    temperature: 0.0-2.0.
    max_tokens: giới hạn output.
    he_thong: system prompt (nếu có).
    streaming: True → trả generator.

    Trả về: dict kết quả (không streaming) hoặc generator (streaming).
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

    # Chuẩn bị messages
    messages = []
    if he_thong:
        messages.append({"role": "system", "content": he_thong})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens:
        body["max_tokens"] = max_tokens
    if streaming:
        body["stream"] = True

    try:
        r = requests.post(
            URL_GROQ,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
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
                noi_dung = du_lieu["choices"][0]["message"]["content"]
                ket_qua["thanh_cong"] = True
                ket_qua["ket_qua"] = noi_dung
            except (KeyError, IndexError, ValueError):
                ket_qua["loi"] = "Groq trả về không đúng format."
            ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
            return ket_qua

        # Xử lý lỗi
        ket_qua["loi"], ket_qua["loai_loi"] = _xu_ly_loi_groq(
            r.status_code, r.text[:500]
        )
        ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
        return ket_qua

    except Exception as e:
        ket_qua["loi"] = f"Lỗi gọi Groq: {e}"
        ket_qua["loai_loi"] = "khac"
        ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
        return ket_qua


# ================================================================
# XỬ LÝ STREAM
# ================================================================
def _xu_ly_stream(response, ket_qua):
    """Xử lý response streaming của Groq."""
    def _gen():
        try:
            for dong in response.iter_lines():
                if not dong:
                    continue
                dong = dong.decode("utf-8").strip()
                if dong.startswith("data: "):
                    du_lieu = dong[6:]
                    if du_lieu == "[DONE]":
                        break
                    try:
                        import json
                        obj = json.loads(du_lieu)
                        delta = obj["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except (ValueError, KeyError, IndexError):
                        continue
        except Exception as e:
            _ghi_log("loi", f"Stream lỗi: {e}")

    return _gen()


# ================================================================
# XỬ LÝ LỖI
# ================================================================
def _xu_ly_loi_groq(status_code, text):
    """
    Phân tích lỗi Groq.

    Trả về: (mô_tả, loai_loi).
    """
    text_lower = (text or "").lower()

    if status_code == 400:
        return f"Request sai (400): {text[:200]}", "khac"
    if status_code == 401:
        return "Key sai hoặc hết hạn (401).", "key_sai"
    if status_code == 403:
        return "Không có quyền (403).", "key_sai"
    if status_code == 404:
        return f"Model không tồn tại (404).", "model_chet"
    if status_code == 429:
        # Phân biệt rate limit ngắn (RPM) và dài (RPD/TPD)
        if "per day" in text_lower or "daily" in text_lower:
            return "Hết quota ngày (429).", "het_quota"
        if "token" in text_lower and "per day" in text_lower:
            return "Hết quota token ngày (429).", "het_quota"
        return "Vượt rate limit (429).", "het_quota"
    if 500 <= status_code < 600:
        return f"Server Groq lỗi ({status_code}).", "khac"

    return f"Groq trả {status_code}: {text[:200]}", "khac"


# ================================================================
# LẤY DANH SÁCH MODEL
# ================================================================
def lay_model_groq(key):
    """
    Lấy danh sách model từ Groq API.

    Trả về: list tên model.
    """
    if not key:
        return []

    try:
        import requests
        r = requests.get(
            URL_GROQ_MODELS,
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if r.status_code != 200:
            return []

        du_lieu = r.json()
        danh_sach = du_lieu.get("data", [])
        ket_qua = []

        for model in danh_sach:
            model_id = model.get("id", "")
            if not model_id:
                continue
            if model.get("active", True) is False:
                continue
            ket_qua.append(model_id)

        return ket_qua

    except ImportError:
        return []
    except Exception:
        return []


# ================================================================
# KIỂM TRA KEY
# ================================================================
def kiem_tra_key_groq(key):
    """
    Kiểm tra key Groq còn hiệu lực không.

    Trả về: (True, "") nếu OK, hoặc (False, "lỗi").
    """
    if not key:
        return False, "Thiếu key."

    try:
        import requests
        r = requests.get(
            URL_GROQ_MODELS,
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if r.status_code == 200:
            return True, ""
        if r.status_code in (401, 403):
            return False, "Key sai hoặc hết hạn."
        return False, f"Groq trả {r.status_code}."
    except ImportError:
        return False, "Chưa cài requests."
    except Exception as e:
        return False, f"Lỗi kiểm tra key: {e}"


# ================================================================
# LẤY QUOTA TỪ HEADER
# ================================================================
def lay_quota_groq(key):
    """
    Lấy quota Groq từ header response.

    Trả về dict:
        { remaining_requests, limit_requests, remaining_tokens,
          limit_tokens, phan_tram }
    """
    ket_qua = {
        "remaining_requests": None,
        "limit_requests": None,
        "remaining_tokens": None,
        "limit_tokens": None,
        "phan_tram": None,
    }

    if not key:
        return ket_qua

    try:
        import requests
        r = requests.get(
            URL_GROQ_MODELS,
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )

        if r.status_code != 200:
            return ket_qua

        con_lai = r.headers.get("x-ratelimit-remaining-requests")
        tong = r.headers.get("x-ratelimit-limit-requests")
        con_token = r.headers.get("x-ratelimit-remaining-tokens")
        tong_token = r.headers.get("x-ratelimit-limit-tokens")

        ket_qua["remaining_requests"] = int(con_lai) if con_lai else None
        ket_qua["limit_requests"] = int(tong) if tong else None
        ket_qua["remaining_tokens"] = int(con_token) if con_token else None
        ket_qua["limit_tokens"] = int(tong_token) if tong_token else None

        if ket_qua["remaining_requests"] is not None and ket_qua["limit_requests"]:
            if ket_qua["limit_requests"] > 0:
                ket_qua["phan_tram"] = int(
                    ket_qua["remaining_requests"] / ket_qua["limit_requests"] * 100
                )

        return ket_qua

    except ImportError:
        return ket_qua
    except Exception:
        return ket_qua


# ================================================================
# HÀM PHỤ: GỌI NHANH
# ================================================================
def goi_nhanh(key, model, prompt):
    """Gọi nhanh với temperature mặc định 0.7."""
    return goi_groq(key, model, prompt, temperature=0.7)


def goi_chinh_xac(key, model, prompt):
    """Gọi với temperature thấp (chính xác cao)."""
    return goi_groq(key, model, prompt, temperature=0.2)


def goi_sang_tao(key, model, prompt):
    """Gọi với temperature cao (sáng tạo)."""
    return goi_groq(key, model, prompt, temperature=1.2)


# ================================================================
# HÀM PHỤ: ĐẾM TOKEN (ước lượng)
# ================================================================
def uoc_luong_token(chuoi):
    """
    Ước lượng số token (thô).
    Quy tắc: ~4 ký tự = 1 token (tiếng Anh), ~1.5 ký tự = 1 token (tiếng Việt).
    """
    if not chuoi:
        return 0

    # Ước lượng dựa trên tỉ lệ ký tự có dấu
    co_dau = sum(1 for c in chuoi if ord(c) > 127)
    if co_dau > len(chuoi) * 0.1:
        # Có nhiều dấu → tiếng Việt → 1.5 ký tự/token
        return int(len(chuoi) / 1.5)
    return int(len(chuoi) / 4)


# ================================================================
# HÀM PHỤ: TÓM TẮT KẾT QUẢ
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả gọi Groq."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return (
            f"✅ Groq OK ({ket_qua.get('thoi_gian', 0)}s): "
            f"{ket_qua.get('ket_qua', '')[:60]}..."
        )

    return f"❌ Groq lỗi [{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')}"


# ================================================================
# HÀM PHỤ: LẤY MODEL MẶC ĐỊNH
# ================================================================
def lay_model_mac_dinh():
    """Trả về danh sách model Groq mặc định (tháng 10/2026)."""
    return [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
    ]


# ================================================================
# HÀM PHỤ: KIỂM TRA MODEL CÒN SỐNG
# ================================================================
def model_con_song(key, model):
    """Kiểm tra model có trong danh sách API không."""
    danh_sach = lay_model_groq(key)
    return model in danh_sach
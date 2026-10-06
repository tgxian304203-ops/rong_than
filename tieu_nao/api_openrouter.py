"""
api_openrouter.py - Kết nối OpenRouter API Rồng Thần.

Nhiệm vụ:
    - goi_openrouter(key, model, prompt, ...): gọi OpenRouter API.
    - lay_model_openrouter(key): lấy danh sách model free.
    - kiem_tra_key_openrouter(key): kiểm tra key + đọc quota.
    - lay_quota_openrouter(key): lấy quota (limit + usage).
    - _xu_ly_loi_openrouter(status_code, text): phân tích lỗi.

Quy tắc:
    - Endpoint: https://openrouter.ai/api/v1/chat/completions
    - Models: https://openrouter.ai/api/v1/models
    - Key info: https://openrouter.ai/api/v1/key
    - Auth: Bearer <key>
    - Timeout: 30 giây
    - Headers bắt buộc: HTTP-Referer, X-Title

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
URL_OR = "https://openrouter.ai/api/v1/chat/completions"
URL_OR_MODELS = "https://openrouter.ai/api/v1/models"
URL_OR_KEY = "https://openrouter.ai/api/v1/key"
TIMEOUT = 30
HTTP_REFERER = "https://rong-than.app"
X_TITLE = "Rong Than"


# ================================================================
# HEADERS
# ================================================================
def _tao_headers(key):
    """Tạo headers chuẩn cho OpenRouter."""
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": HTTP_REFERER,
        "X-Title": X_TITLE,
    }


# ================================================================
# GỌI OPENROUTER API
# ================================================================
def goi_openrouter(key, model, prompt, temperature=0.7, max_tokens=None,
                   he_thong=None, streaming=False):
    """
    Gọi OpenRouter API.

    key: API key.
    model: tên model (dạng "provider/model" hoặc "provider/model:free").
    prompt: câu hỏi.
    temperature: 0.0-2.0.
    max_tokens: giới hạn output.
    he_thong: system prompt.
    streaming: True → trả generator.

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

    # Messages
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
            URL_OR,
            headers=_tao_headers(key),
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
                ket_qua["loi"] = "OpenRouter trả về không đúng format."
            ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
            return ket_qua

        # Lỗi
        ket_qua["loi"], ket_qua["loai_loi"] = _xu_ly_loi_openrouter(
            r.status_code, r.text[:500]
        )
        ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
        return ket_qua

    except Exception as e:
        ket_qua["loi"] = f"Lỗi gọi OpenRouter: {e}"
        ket_qua["loai_loi"] = "khac"
        ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
        return ket_qua


# ================================================================
# XỬ LÝ STREAM
# ================================================================
def _xu_ly_stream(response, ket_qua):
    """Xử lý response streaming của OpenRouter."""
    def _gen():
        try:
            import json
            for dong in response.iter_lines():
                if not dong:
                    continue
                dong = dong.decode("utf-8").strip()
                if dong.startswith("data: "):
                    du_lieu = dong[6:]
                    if du_lieu == "[DONE]":
                        break
                    try:
                        obj = json.loads(du_lieu)
                        choices = obj.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {}).get("content", "")
                            if delta:
                                yield delta
                    except (ValueError, KeyError, IndexError):
                        continue
        except Exception as e:
            _ghi_log("loi", f"OpenRouter stream lỗi: {e}")

    return _gen()


# ================================================================
# XỬ LÝ LỖI
# ================================================================
def _xu_ly_loi_openrouter(status_code, text):
    """
    Phân tích lỗi OpenRouter.

    Trả về: (mô_tả, loai_loi).
    """
    text_lower = (text or "").lower()

    if status_code == 400:
        return f"Request sai (400): {text[:200]}", "khac"
    if status_code == 401:
        return "Key sai hoặc hết hạn (401).", "key_sai"
    if status_code == 402:
        return "Hết credit / cần nạp tiền (402).", "het_quota"
    if status_code == 403:
        return "Không có quyền (403).", "key_sai"
    if status_code == 404:
        return "Model không tồn tại (404).", "model_chet"
    if status_code == 408:
        return "Request timeout (408).", "khac"
    if status_code == 429:
        return "Vượt rate limit (429).", "het_quota"
    if status_code == 502 or status_code == 503:
        return f"Provider model lỗi ({status_code}).", "khac"
    if 500 <= status_code < 600:
        return f"OpenRouter lỗi ({status_code}).", "khac"

    # Kiểm tra text có chứa "no endpoints" → model chết
    if "no endpoints" in text_lower or "not found" in text_lower:
        return f"Model không có endpoint ({text[:150]}).", "model_chet"

    return f"OpenRouter trả {status_code}: {text[:200]}", "khac"


# ================================================================
# LẤY DANH SÁCH MODEL
# ================================================================
def lay_model_openrouter(key, chi_free=True):
    """
    Lấy danh sách model từ OpenRouter.

    key: API key.
    chi_free: True → chỉ lấy model free (:free hoặc pricing = 0).

    Trả về: list tên model.
    """
    if not key:
        return []

    try:
        import requests
        r = requests.get(
            URL_OR_MODELS,
            headers=_tao_headers(key),
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

            if chi_free:
                # Kiểm tra pricing
                gia = model.get("pricing", {})
                gia_prompt = float(gia.get("prompt", 0) or 0)
                gia_completion = float(gia.get("completion", 0) or 0)

                # Free nếu pricing = 0 hoặc có :free trong tên
                if gia_prompt == 0 and gia_completion == 0:
                    ket_qua.append(model_id)
            else:
                ket_qua.append(model_id)

        # Ưu tiên instruct/chat
        ket_qua_sap_xep = sorted(
            ket_qua,
            key=lambda m: (
                0 if "instruct" in m.lower() else 1,
                0 if "chat" in m.lower() else 1,
                m,
            ),
        )
        return ket_qua_sap_xep

    except ImportError:
        return []
    except Exception:
        return []


# ================================================================
# KIỂM TRA KEY + QUOTA
# ================================================================
def kiem_tra_key_openrouter(key):
    """
    Kiểm tra key OpenRouter và lấy thông tin quota.

    Trả về: (thanh_cong, thong_tin).
        thong_tin = {
            con_lai, tong, da_dung, phan_tram, ten, gioi_han,
        }
    """
    if not key:
        return False, {"loi": "Thiếu key."}

    try:
        import requests
        r = requests.get(
            URL_OR_KEY,
            headers=_tao_headers(key),
            timeout=10,
        )

        if r.status_code != 200:
            return False, {"loi": f"OpenRouter trả {r.status_code}."}

        du_lieu = r.json().get("data", {})

        gioi_han = du_lieu.get("limit")
        da_dung = du_lieu.get("usage", 0) or 0
        ten = du_lieu.get("label") or du_lieu.get("name") or ""
        is_free_tier = du_lieu.get("is_free_tier", True)

        con_lai = None
        phan_tram = 100

        if gioi_han and gioi_han > 0:
            con_lai = max(0, gioi_han - da_dung)
            phan_tram = int(con_lai / gioi_han * 100)

        return True, {
            "con_lai": con_lai,
            "tong": gioi_han,
            "da_dung": da_dung,
            "phan_tram": phan_tram,
            "ten": ten,
            "is_free_tier": is_free_tier,
        }

    except ImportError:
        return False, {"loi": "Chưa cài requests."}
    except Exception as e:
        return False, {"loi": f"Lỗi: {e}"}


def lay_quota_openrouter(key):
    """Lấy quota OpenRouter (dùng cho quan_ly_quota)."""
    _, thong_tin = kiem_tra_key_openrouter(key)
    return {
        "phan_tram": thong_tin.get("phan_tram", 100),
        "con_lai": thong_tin.get("con_lai"),
        "tong": thong_tin.get("tong"),
        "loai_quota": "credit",
    }


# ================================================================
# HÀM PHỤ: GỌI NHANH
# ================================================================
def goi_nhanh(key, model, prompt):
    """Gọi nhanh với temperature 0.7."""
    return goi_openrouter(key, model, prompt, temperature=0.7)


def goi_chinh_xac(key, model, prompt):
    """Gọi chính xác với temperature thấp."""
    return goi_openrouter(key, model, prompt, temperature=0.2)


def goi_sang_tao(key, model, prompt):
    """Gọi sáng tạo với temperature cao."""
    return goi_openrouter(key, model, prompt, temperature=1.2)


# ================================================================
# HÀM PHỤ: LẤY MODEL FREE TOP
# ================================================================
def lay_model_free_top(key, so_luong=10):
    """
    Lấy top N model free phổ biến.
    """
    danh_sach = lay_model_openrouter(key, chi_free=True)
    return danh_sach[:so_luong]


# ================================================================
# HÀM PHỤ: KIỂM TRA MODEL CÒN SỐNG
# ================================================================
def model_con_song(key, model):
    """Kiểm tra model có trong danh sách API không."""
    danh_sach = lay_model_openrouter(key, chi_free=False)
    return model in danh_sach


# ================================================================
# HÀM PHỤ: LẤY MODEL MẶC ĐỊNH
# ================================================================
def lay_model_mac_dinh():
    """Trả về danh sách model OpenRouter free mặc định (tháng 10/2026)."""
    return [
        "space-bunny-alpha",
        "nvidia/nemotron-3-ultra:free",
        "poolside/laguna-s-2.1:free",
        "openai/gpt-oss-120b:free",
        "openai/gpt-oss-20b:free",
        "qwen/qwen3-coder:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1:free",
        "z-ai/glm-4.5-air:free",
    ]


# ================================================================
# HÀM PHỤ: TÓM TẮT KẾT QUẢ
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả gọi OpenRouter."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return (
            f"✅ OpenRouter OK ({ket_qua.get('thoi_gian', 0)}s): "
            f"{ket_qua.get('ket_qua', '')[:60]}..."
        )

    return f"❌ OpenRouter lỗi [{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')}"


# ================================================================
# HÀM PHỤ: ĐẾM MODEL FREE
# ================================================================
def dem_model_free(key):
    """Đếm số model free hiện có."""
    return len(lay_model_openrouter(key, chi_free=True))
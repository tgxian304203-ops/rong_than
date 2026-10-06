"""
api_chung.py - Interface chung cho 3 provider API Rồng Thần.

Nhiệm vụ:
    - goi_api(provider, key, model, prompt, ...): điều phối gọi API.
    - lay_model(provider, key): lấy danh sách model.
    - kiem_tra_key(provider, key): kiểm tra key.
    - lay_quota(provider, key): lấy quota.

Quy tắc:
    - Đây là CỬA NGÕ CHUNG cho 3 provider: Groq, OpenRouter, Gemini.
    - Không tự gọi API — gọi qua api_groq/api_openrouter/api_gemini.
    - Chuẩn hóa tên provider.
    - Chuẩn hóa kết quả trả về.

Trả về:
    {
        thanh_cong: bool,
        ket_qua: str,
        loi: str,
        loai_loi: str,
        thoi_gian: float,
        provider: str,
        model: str,
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
# CHUẨN HÓA TÊN PROVIDER
# ================================================================
def chuan_hoa_provider(provider):
    """
    Chuẩn hóa tên provider về 3 tên chính: Groq, OpenRouter, Gemini.
    """
    if not provider:
        return ""

    p = provider.strip().lower()
    if p == "groq":
        return "Groq"
    if p in ("openrouter", "open router", "or"):
        return "OpenRouter"
    if p in ("gemini", "google"):
        return "Gemini"
    return ""


def danh_sach_provider():
    """Trả danh sách 3 provider."""
    return ["Groq", "OpenRouter", "Gemini"]


# ================================================================
# GỌI API
# ================================================================
def goi_api(provider, key, model, prompt, temperature=0.7,
            max_tokens=None, he_thong=None, streaming=False):
    """
    Điều phối gọi API theo provider.

    provider: "Groq" | "OpenRouter" | "Gemini".
    key: API key.
    model: tên model.
    prompt: câu hỏi.
    temperature, max_tokens, he_thong, streaming: như các api_*.py.

    Trả về: dict kết quả chuẩn hóa.
    """
    ket_qua = {
        "thanh_cong": False,
        "ket_qua": "",
        "loi": "",
        "loai_loi": "",
        "thoi_gian": 0.0,
        "provider": "",
        "model": model or "",
    }

    if not provider or not key or not model or not prompt:
        ket_qua["loi"] = "Thiếu tham số."
        return ket_qua

    p = chuan_hoa_provider(provider)
    if not p:
        ket_qua["loi"] = f"Provider không hỗ trợ: {provider}"
        return ket_qua

    ket_qua["provider"] = p
    thoi_gian_bat_dau = time.time()

    # Điều phối theo provider
    try:
        if p == "Groq":
            from tieu_nao.api_groq import goi_groq
            ket_qua_tho = goi_groq(
                key, model, prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                he_thong=he_thong,
                streaming=streaming,
            )
        elif p == "OpenRouter":
            from tieu_nao.api_openrouter import goi_openrouter
            ket_qua_tho = goi_openrouter(
                key, model, prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                he_thong=he_thong,
                streaming=streaming,
            )
        elif p == "Gemini":
            from tieu_nao.api_gemini import goi_gemini
            ket_qua_tho = goi_gemini(
                key, model, prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                he_thong=he_thong,
                streaming=streaming,
            )
        else:
            ket_qua["loi"] = f"Provider không hỗ trợ: {p}"
            return ket_qua
    except ImportError as e:
        ket_qua["loi"] = f"Không import được api_{p.lower()}: {e}"
        return ket_qua

    # Streaming → trả generator luôn
    if streaming and ket_qua_tho and not isinstance(ket_qua_tho, dict):
        ket_qua["thanh_cong"] = True
        ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
        return {
            "thanh_cong": True,
            "stream": ket_qua_tho,
            "provider": p,
            "model": model,
        }

    # Không streaming
    if not ket_qua_tho or not isinstance(ket_qua_tho, dict):
        ket_qua["loi"] = "API trả về không hợp lệ."
        return ket_qua

    ket_qua.update({
        "thanh_cong": ket_qua_tho.get("thanh_cong", False),
        "ket_qua": ket_qua_tho.get("ket_qua", ""),
        "loi": ket_qua_tho.get("loi", ""),
        "loai_loi": ket_qua_tho.get("loai_loi", ""),
        "thoi_gian": ket_qua_tho.get("thoi_gian", 0.0),
    })

    return ket_qua


# ================================================================
# LẤY DANH SÁCH MODEL
# ================================================================
def lay_model(provider, key):
    """
    Lấy danh sách model theo provider.
    """
    p = chuan_hoa_provider(provider)
    if not p or not key:
        return []

    try:
        if p == "Groq":
            from tieu_nao.api_groq import lay_model_groq
            return lay_model_groq(key) or []
        if p == "OpenRouter":
            from tieu_nao.api_openrouter import lay_model_openrouter
            return lay_model_openrouter(key) or []
        if p == "Gemini":
            from tieu_nao.api_gemini import lay_model_gemini
            return lay_model_gemini(key) or []
    except ImportError:
        pass

    return []


# ================================================================
# KIỂM TRA KEY
# ================================================================
def kiem_tra_key(provider, key):
    """
    Kiểm tra key theo provider.

    Trả về: (True, "") hoặc (False, "lỗi").
    """
    p = chuan_hoa_provider(provider)
    if not p or not key:
        return False, "Thiếu provider hoặc key."

    try:
        if p == "Groq":
            from tieu_nao.api_groq import kiem_tra_key_groq
            return kiem_tra_key_groq(key)
        if p == "OpenRouter":
            from tieu_nao.api_openrouter import kiem_tra_key_openrouter
            thanh_cong, thong_tin = kiem_tra_key_openrouter(key)
            if thanh_cong:
                return True, ""
            return False, thong_tin.get("loi", "Lỗi không xác định.")
        if p == "Gemini":
            from tieu_nao.api_gemini import kiem_tra_key_gemini
            return kiem_tra_key_gemini(key)
    except ImportError:
        pass

    return False, "Provider không hỗ trợ."


# ================================================================
# LẤY QUOTA
# ================================================================
def lay_quota(provider, key):
    """
    Lấy quota theo provider.

    Trả về: dict { phan_tram, con_lai, tong, loai_quota }.
    """
    p = chuan_hoa_provider(provider)
    ket_qua = {
        "phan_tram": 100,
        "con_lai": None,
        "tong": None,
        "loai_quota": "",
    }

    if not p or not key:
        return ket_qua

    try:
        if p == "Groq":
            from tieu_nao.api_groq import lay_quota_groq
            return lay_quota_groq(key)
        if p == "OpenRouter":
            from tieu_nao.api_openrouter import lay_quota_openrouter
            return lay_quota_openrouter(key)
        if p == "Gemini":
            # Gemini không có quota API — trả mặc định
            return ket_qua
    except ImportError:
        pass

    return ket_qua


# ================================================================
# HÀM PHỤ: GỌI NÉU KEY CÒN DÙNG
# ================================================================
def goi_nen_key_con_dung(provider, key, model, prompt, **kwargs):
    """
    Chỉ gọi nếu key còn dùng được.
    Kiểm tra key trước khi gọi.
    """
    hop_le, loi = kiem_tra_key(provider, key)
    if not hop_le:
        return {
            "thanh_cong": False,
            "loi": loi,
            "loai_loi": "key_sai",
            "provider": provider,
            "model": model,
        }

    return goi_api(provider, key, model, prompt, **kwargs)


# ================================================================
# HÀM PHỤ: GỌI VỚI DANH SÁCH MODEL
# ================================================================
def goi_voi_ds_model(provider, key, danh_sach_model, prompt, **kwargs):
    """
    Gọi lần lượt qua danh sách model đến khi thành công.
    """
    if not danh_sach_model:
        return {
            "thanh_cong": False,
            "loi": "Danh sách model rỗng.",
            "provider": provider,
        }

    lich_su = []

    for model in danh_sach_model:
        ket_qua = goi_api(provider, key, model, prompt, **kwargs)
        lich_su.append({
            "model": model,
            "thanh_cong": ket_qua.get("thanh_cong"),
            "loai_loi": ket_qua.get("loai_loi", ""),
        })

        if ket_qua.get("thanh_cong"):
            ket_qua["lich_su"] = lich_su
            return ket_qua

    # Thất bại tất cả
    return {
        "thanh_cong": False,
        "loi": f"Đã thử {len(danh_sach_model)} model nhưng thất bại.",
        "loai_loi": "het_quota",
        "provider": provider,
        "lich_su": lich_su,
    }


# ================================================================
# HÀM PHỤ: TÓM TẮT KẾT QUẢ
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả gọi API."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        return (
            f"✅ {ket_qua.get('provider', '')} / {ket_qua.get('model', '')} "
            f"({ket_qua.get('thoi_gian', 0)}s)"
        )

    return (
        f"❌ {ket_qua.get('provider', '')} / {ket_qua.get('model', '')} "
        f"[{ket_qua.get('loai_loi', '')}]: {ket_qua.get('loi', '')[:100]}"
    )


# ================================================================
# HÀM PHỤ: KIỂM TRA PROVIDER
# ================================================================
def la_provider_hop_le(provider):
    """Kiểm tra tên provider có hợp lệ không."""
    return chuan_hoa_provider(provider) != ""


def lay_tat_ca_model_mac_dinh():
    """Lấy model mặc định của cả 3 provider."""
    ket_qua = {}
    try:
        from tieu_nao.api_groq import lay_model_mac_dinh as groq
        ket_qua["Groq"] = groq()
    except ImportError:
        ket_qua["Groq"] = []

    try:
        from tieu_nao.api_openrouter import lay_model_mac_dinh as or_
        ket_qua["OpenRouter"] = or_()
    except ImportError:
        ket_qua["OpenRouter"] = []

    try:
        from tieu_nao.api_gemini import lay_model_mac_dinh as gem
        ket_qua["Gemini"] = gem()
    except ImportError:
        ket_qua["Gemini"] = []

    return ket_qua


# ================================================================
# HÀM PHỤ: KIỂM TRA TẤT CẢ KEY
# ================================================================
def kiem_tra_tat_ca_key(danh_sach_key):
    """
    Kiểm tra tất cả key.

    danh_sach_key: list [{provider, key, id}].

    Trả về: list [{provider, key_id, thanh_cong, loi}].
    """
    ket_qua = []

    for key_info in danh_sach_key or []:
        provider = key_info.get("provider", "")
        key = key_info.get("key", "")
        key_id = key_info.get("id", "")

        thanh_cong, loi = kiem_tra_key(provider, key)
        ket_qua.append({
            "provider": provider,
            "key_id": key_id,
            "thanh_cong": thanh_cong,
            "loi": loi,
        })

    return ket_qua


# ================================================================
# HÀM PHỤ: TÓM TẮT TẤT CẢ PROVIDER
# ================================================================
def tom_tat_tat_ca_provider():
    """Tạo chuỗi tóm tắt 3 provider + model mặc định."""
    tat_ca = lay_tat_ca_model_mac_dinh()
    phan = []

    for p in danh_sach_provider():
        ds = tat_ca.get(p, [])
        phan.append(f"📡 {p}: {len(ds)} model mặc định")
        for m in ds[:3]:
            phan.append(f"  - {m}")

    return "\n".join(phan)
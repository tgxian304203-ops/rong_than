"""
do_model.py - Bước 2 Tiểu não: Dò model, xoay quota Rồng Thần.

Nhiệm vụ:
    - do_model(chu_so_huu, prompt): dò model theo thứ tự gọi.
    - _goi_model(key_info, prompt, model): gọi 1 model cụ thể.
    - _xu_ly_loi(key_info, ket_qua): xử lý lỗi (hết quota, model lỗi).
    - _chuyen_key_tiep(danh_sach_key, vi_tri): chuyển sang key tiếp.

ĐÃ SỬA:
    - L7: Thêm timeout tổng (25 giây). Nếu vượt → dừng, trả lỗi.
    - L14: Check blacklist trước khi gọi model. Set blacklist đúng
      qua quan_ly_loi.ghi_loi_model.

Quy tắc:
    - Gọi lần lượt: Groq#1 → Groq#2 → OpenRouter#1 → Gemini#1.
    - Key nào hết quota → nhảy key tiếp.
    - Model nào bị blacklist → bỏ qua.
    - Model lỗi 3 lần → blacklist.
    - Không gọi cùng lúc — gọi tuần tự.

Trả về:
    {
        thanh_cong: bool,
        ket_qua: str,
        provider: str,
        key_id: str,
        model: str,
        so_lan_thu: int,
        lich_su: list,
        loi: str?,
        het_thoi_gian: bool?,
    }
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
SO_LAN_THU_TOI_DA = 3      # mỗi model thử tối đa 3 lần
SO_LAN_BLACKLIST = 3       # lỗi 3 lần → blacklist
TIMEOUT_GOI = 30           # giây — timeout mỗi lần gọi API
TIMEOUT_TONG = 25          # giây — timeout tổng toàn bộ do_model (L7)


# ================================================================
# KIỂM TRA BLACKLIST (L14)
# ================================================================
def _bi_blacklist(provider, model):
    """Kiểm tra model có bị blacklist không."""
    if not provider or not model:
        return False
    try:
        from tieu_nao.quan_ly_loi import kiem_tra_blacklist
        return bool(kiem_tra_blacklist(provider, model))
    except ImportError:
        return False
    except Exception:
        return False


# ================================================================
# GHI LỖI MODEL (L14)
# ================================================================
def _ghi_loi(provider, model, loi, loai_loi="khac"):
    """Ghi lỗi vào từ điển blacklist qua quan_ly_loi."""
    if not provider or not model:
        return
    try:
        from tieu_nao.quan_ly_loi import ghi_loi_model
        ghi_loi_model(provider, model, loi, loai_loi)
    except ImportError:
        pass
    except Exception:
        pass


# ================================================================
# GỌI MODEL QUA API
# ================================================================
def _goi_model(key_info, prompt, model=None):
    """Gọi 1 model cụ thể qua API tương ứng provider."""
    ket_qua = {"thanh_cong": False, "ket_qua": "", "loi": "", "loai_loi": ""}

    if not key_info or not prompt:
        ket_qua["loi"] = "Thiếu key_info hoặc prompt."
        return ket_qua

    provider = (key_info.get("provider") or "").strip()
    key = key_info.get("key") or ""

    if not provider or not key:
        ket_qua["loi"] = "Thiếu provider hoặc key."
        return ket_qua

    if not model:
        ds_model = key_info.get("model_co_the_dung") or []
        if ds_model:
            model = ds_model[0]
        else:
            ket_qua["loi"] = "Không có model khả dụng."
            return ket_qua

    provider_chuan = provider.lower()

    if provider_chuan == "groq":
        return _goi_groq(key, model, prompt)
    if provider_chuan in ("openrouter", "open router", "or"):
        return _goi_openrouter(key, model, prompt)
    if provider_chuan in ("gemini", "google"):
        return _goi_gemini(key, model, prompt)

    ket_qua["loi"] = f"Provider không hỗ trợ: {provider}"
    return ket_qua


# ================================================================
# GỌI GROQ
# ================================================================
def _goi_groq(key, model, prompt):
    ket_qua = {"thanh_cong": False, "ket_qua": "", "loi": "", "loai_loi": ""}

    try:
        import requests
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            },
            timeout=TIMEOUT_GOI,
        )

        if r.status_code == 200:
            du_lieu = r.json()
            try:
                noi_dung = du_lieu["choices"][0]["message"]["content"]
                ket_qua["thanh_cong"] = True
                ket_qua["ket_qua"] = noi_dung
            except (KeyError, IndexError):
                ket_qua["loi"] = "Groq trả về không đúng format."
            return ket_qua

        if r.status_code == 429:
            ket_qua["loi"] = "Hết quota (429)."
            ket_qua["loai_loi"] = "het_quota"
        elif r.status_code == 401:
            ket_qua["loi"] = "Key sai hoặc hết hạn (401)."
            ket_qua["loai_loi"] = "key_sai"
        elif r.status_code == 404:
            ket_qua["loi"] = f"Model không tồn tại (404): {model}"
            ket_qua["loai_loi"] = "model_chet"
        else:
            ket_qua["loi"] = f"Groq trả {r.status_code}: {r.text[:200]}"
            ket_qua["loai_loi"] = "khac"

        return ket_qua

    except ImportError:
        ket_qua["loi"] = "Chưa cài requests."
        return ket_qua
    except Exception as e:
        ket_qua["loi"] = f"Lỗi gọi Groq: {e}"
        ket_qua["loai_loi"] = "khac"
        return ket_qua


# ================================================================
# GỌI OPENROUTER
# ================================================================
def _goi_openrouter(key, model, prompt):
    ket_qua = {"thanh_cong": False, "ket_qua": "", "loi": "", "loai_loi": ""}

    try:
        import requests
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://rong-than.app",
                "X-Title": "Rong Than",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=TIMEOUT_GOI,
        )

        if r.status_code == 200:
            du_lieu = r.json()
            try:
                noi_dung = du_lieu["choices"][0]["message"]["content"]
                ket_qua["thanh_cong"] = True
                ket_qua["ket_qua"] = noi_dung
            except (KeyError, IndexError):
                ket_qua["loi"] = "OpenRouter trả về không đúng format."
            return ket_qua

        if r.status_code == 429:
            ket_qua["loi"] = "Hết quota (429)."
            ket_qua["loai_loi"] = "het_quota"
        elif r.status_code == 401:
            ket_qua["loi"] = "Key sai hoặc hết hạn (401)."
            ket_qua["loai_loi"] = "key_sai"
        elif r.status_code == 404:
            ket_qua["loi"] = f"Model không tồn tại (404): {model}"
            ket_qua["loai_loi"] = "model_chet"
        elif r.status_code == 402:
            ket_qua["loi"] = "Cần nạp tiền (402)."
            ket_qua["loai_loi"] = "het_quota"
        else:
            ket_qua["loi"] = f"OpenRouter trả {r.status_code}: {r.text[:200]}"
            ket_qua["loai_loi"] = "khac"

        return ket_qua

    except ImportError:
        ket_qua["loi"] = "Chưa cài requests."
        return ket_qua
    except Exception as e:
        ket_qua["loi"] = f"Lỗi gọi OpenRouter: {e}"
        ket_qua["loai_loi"] = "khac"
        return ket_qua


# ================================================================
# GỌI GEMINI
# ================================================================
def _goi_gemini(key, model, prompt):
    ket_qua = {"thanh_cong": False, "ket_qua": "", "loi": "", "loai_loi": ""}

    try:
        import requests
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={key}"
        )
        r = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{"text": prompt}],
                }]
            },
            timeout=TIMEOUT_GOI,
        )

        if r.status_code == 200:
            du_lieu = r.json()
            try:
                noi_dung = du_lieu["candidates"][0]["content"]["parts"][0]["text"]
                ket_qua["thanh_cong"] = True
                ket_qua["ket_qua"] = noi_dung
            except (KeyError, IndexError):
                ket_qua["loi"] = "Gemini trả về không đúng format."
            return ket_qua

        if r.status_code == 429:
            ket_qua["loi"] = "Hết quota (429)."
            ket_qua["loai_loi"] = "het_quota"
        elif r.status_code in (401, 403):
            ket_qua["loi"] = f"Key sai hoặc hết hạn ({r.status_code})."
            ket_qua["loai_loi"] = "key_sai"
        elif r.status_code == 404:
            ket_qua["loi"] = f"Model không tồn tại (404): {model}"
            ket_qua["loai_loi"] = "model_chet"
        else:
            ket_qua["loi"] = f"Gemini trả {r.status_code}: {r.text[:200]}"
            ket_qua["loai_loi"] = "khac"

        return ket_qua

    except ImportError:
        ket_qua["loi"] = "Chưa cài requests."
        return ket_qua
    except Exception as e:
        ket_qua["loi"] = f"Lỗi gọi Gemini: {e}"
        ket_qua["loai_loi"] = "khac"
        return ket_qua


# ================================================================
# XỬ LÝ LỖI
# ================================================================
def _xu_ly_loi(key_info, ket_qua_loi, model=""):
    """
    Xử lý lỗi: cập nhật quota, blacklist model.

    Trả về hành động: "chuyen_key" | "chuyen_model" | "thu_lai" | "bo_qua".
    """
    if not key_info or not ket_qua_loi:
        return "bo_qua"

    loai_loi = ket_qua_loi.get("loai_loi", "")
    key_id = key_info.get("id", "")
    provider = key_info.get("provider", "")

    # Hết quota → chuyển key
    if loai_loi == "het_quota":
        try:
            from dai_nao.ghi_nho import cap_nhat_quota_key
            cap_nhat_quota_key(key_id, 0)
        except Exception:
            pass
        _ghi_log("tieu-nao", f"Key {key_id[:8]} hết quota → chuyển key.")
        return "chuyen_key"

    # Key sai → chuyển key
    if loai_loi == "key_sai":
        _ghi_log("tieu-nao", f"Key {key_id[:8]} sai → bỏ qua.")
        return "chuyen_key"

    # Model chết → blacklist + chuyển model
    if loai_loi == "model_chet":
        _ghi_loi(provider, model, ket_qua_loi.get("loi", ""), "model_chet")
        _ghi_log("tieu-nao", f"Model {model} chết → blacklist.")
        return "chuyen_model"

    # Lỗi khác → thử lại
    return "thu_lai"


# ================================================================
# BLACKLIST MODEL (qua quan_ly_loi — L14)
# ================================================================
def _blacklist_model(provider, model, loi="", loai_loi="khac"):
    """Blacklist model qua quan_ly_loi (set blacklist đúng)."""
    if not provider or not model:
        return
    _ghi_loi(provider, model, loi, loai_loi)


# ================================================================
# HÀM CHÍNH
# ================================================================
def do_model(chu_so_huu, prompt):
    """
    Bước 2: Dò model theo thứ tự gọi.

    ĐÃ SỬA:
        - L7: Timeout tổng 25 giây. Vượt → dừng.
        - L14: Check blacklist trước khi gọi.

    chu_so_huu: tên đăng nhập.
    prompt: câu hỏi gửi model.

    Trả về dict đầy đủ.
    """
    thoi_gian_bat_dau = time.time()

    ket_qua = {
        "thanh_cong": False,
        "ket_qua": "",
        "provider": "",
        "key_id": "",
        "model": "",
        "so_lan_thu": 0,
        "lich_su": [],
        "loi": "",
        "het_thoi_gian": False,
    }

    if not chu_so_huu or not prompt:
        ket_qua["loi"] = "Thiếu tài khoản hoặc prompt."
        return ket_qua

    # 1. Kiểm kê key
    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        kiem_ke = kiem_ke_key(chu_so_huu)
    except ImportError:
        ket_qua["loi"] = "kiem_ke_key.py chưa có."
        return ket_qua

    if not kiem_ke.get("thanh_cong"):
        ket_qua["loi"] = kiem_ke.get("loi", "Không có key.")
        return ket_qua

    thu_tu_goi = kiem_ke.get("thu_tu_goi", [])
    if not thu_tu_goi:
        ket_qua["loi"] = "Không có key nào để gọi."
        return ket_qua

    # 2. Duyệt từng key
    for key_info in thu_tu_goi:
        # L7: Kiểm tra timeout tổng
        if time.time() - thoi_gian_bat_dau >= TIMEOUT_TONG:
            ket_qua["loi"] = f"Hết thời gian tổng ({TIMEOUT_TONG}s)."
            ket_qua["het_thoi_gian"] = True
            _ghi_log("tieu-nao", f"Hết timeout tổng sau {TIMEOUT_TONG}s.")
            break

        provider = key_info.get("provider", "")
        key_id = key_info.get("id", "")
        ds_model = key_info.get("model_co_the_dung") or []

        # L14: Lọc model bị blacklist (đã làm ở kiem_ke_key, nhưng check lại)
        ds_model_sach = []
        for m in ds_model:
            if _bi_blacklist(provider, m):
                continue
            ds_model_sach.append(m)

        if not ds_model_sach:
            _ghi_log(
                "tieu-nao",
                f"Key {key_id[:8]} ({provider}) không có model khả dụng "
                f"(tất cả bị blacklist).",
            )
            continue

        # Thử từng model trong key này
        for model in ds_model_sach:
            # L7: Kiểm tra timeout trước mỗi lần gọi
            if time.time() - thoi_gian_bat_dau >= TIMEOUT_TONG:
                ket_qua["loi"] = f"Hết thời gian tổng ({TIMEOUT_TONG}s)."
                ket_qua["het_thoi_gian"] = True
                break

            hanh_dong = ""  # reset trước mỗi vòng

            for lan_thu in range(1, SO_LAN_THU_TOI_DA + 1):
                # L7: Kiểm tra timeout trước mỗi lần gọi
                if time.time() - thoi_gian_bat_dau >= TIMEOUT_TONG:
                    ket_qua["loi"] = f"Hết thời gian tổng ({TIMEOUT_TONG}s)."
                    ket_qua["het_thoi_gian"] = True
                    break

                ket_qua["so_lan_thu"] += 1

                _ghi_log(
                    "tieu-nao",
                    f"Gọi {provider} key={key_id[:8]} model={model} lần {lan_thu}",
                )

                kq_goi = _goi_model(key_info, prompt, model)

                lich_su_item = {
                    "provider": provider,
                    "key_id": key_id,
                    "model": model,
                    "lan_thu": lan_thu,
                    "thanh_cong": kq_goi.get("thanh_cong"),
                    "loi": (kq_goi.get("loi") or "")[:200],
                }
                ket_qua["lich_su"].append(lich_su_item)

                # Thành công → trả về
                if kq_goi.get("thanh_cong"):
                    ket_qua.update({
                        "thanh_cong": True,
                        "ket_qua": kq_goi.get("ket_qua", ""),
                        "provider": provider,
                        "key_id": key_id,
                        "model": model,
                    })
                    _ghi_log("tieu-nao", f"Thành công: {provider} / {model}")
                    return ket_qua

                # Xử lý lỗi
                hanh_dong = _xu_ly_loi(key_info, kq_goi, model)

                if hanh_dong == "chuyen_key":
                    break

                if hanh_dong == "chuyen_model":
                    _blacklist_model(provider, model,
                                     kq_goi.get("loi", ""),
                                     kq_goi.get("loai_loi", "khac"))
                    break

                # Lỗi khác → thử lại (vòng lặp tiếp tục)

            # Kết thúc vòng lần thử
            if hanh_dong == "chuyen_key":
                break

            # Nếu hết thời gian tổng → thoát luôn
            if ket_qua.get("het_thoi_gian"):
                break

        # Kết thúc vòng model
        if hanh_dong == "chuyen_key":
            continue

        if ket_qua.get("het_thoi_gian"):
            break

    # 3. Hết tất cả
    if not ket_qua["loi"]:
        ket_qua["loi"] = "Đã thử tất cả key và model nhưng không thành công."

    _ghi_log("tieu-nao", f"Dò model thất bại: {ket_qua['loi']}")
    return ket_qua


# ================================================================
# HÀM PHỤ: GỌI 1 KEY CỤ THỂ
# ================================================================
def goi_voi_key(chu_so_huu, key_id, prompt):
    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        kiem_ke = kiem_ke_key(chu_so_huu)
    except ImportError:
        return {"thanh_cong": False, "loi": "kiem_ke_key.py chưa có."}

    if not kiem_ke.get("thanh_cong"):
        return {"thanh_cong": False, "loi": "Không có key."}

    for key_info in kiem_ke.get("thu_tu_goi", []):
        if key_info.get("id") == key_id:
            return _goi_model(key_info, prompt)

    return {"thanh_cong": False, "loi": f"Không tìm thấy key id={key_id}."}


# ================================================================
# HÀM PHỤ: GỌI 1 PROVIDER CỤ THỂ
# ================================================================
def goi_voi_provider(chu_so_huu, provider, prompt):
    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        kiem_ke = kiem_ke_key(chu_so_huu)
    except ImportError:
        return {"thanh_cong": False, "loi": "kiem_ke_key.py chưa có."}

    if not kiem_ke.get("thanh_cong"):
        return {"thanh_cong": False, "loi": "Không có key."}

    for key_info in kiem_ke.get("thu_tu_goi", []):
        if key_info.get("provider", "").lower() == provider.lower():
            return _goi_model(key_info, prompt)

    return {"thanh_cong": False, "loi": f"Không có key cho {provider}."}


# ================================================================
# HÀM PHỤ: TÓM TẮT
# ================================================================
def tom_tat_lich_su(ket_qua):
    if not ket_qua:
        return ""
    phan = []
    lich_su = ket_qua.get("lich_su", [])
    for item in lich_su[-10:]:
        ok = "✅" if item.get("thanh_cong") else "❌"
        phan.append(
            f"{ok} {item.get('provider')} / {item.get('model')} "
            f"(lần {item.get('lan_thu')})"
        )
    return "\n".join(phan)


def dem_so_lan_thu(ket_qua):
    if not ket_qua:
        return 0
    return ket_qua.get("so_lan_thu", 0)
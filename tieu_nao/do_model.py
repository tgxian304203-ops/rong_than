"""
do_model.py - Bước 2 Tiểu não: Dò model, xoay quota Rồng Thần.

ĐÃ SỬA (fix Boss timeout):
    - FIX: Timeout tổng khác nhau cho Boss và Tiểu não.
      + Boss: 20 giây (đủ cho 1 lần gọi model).
      + Tiểu não: 25 giây (giữ nguyên).
    - Boss gọi 2 lần (hiểu yêu cầu + chia task) → tổng 40s < Render timeout 100s.
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
SO_LAN_THU_TOI_DA = 3
SO_LAN_BLACKLIST = 3
TIMEOUT_GOI = 30

# FIX: Timeout tổng theo loại não
TIMEOUT_TONG_BOSS = 20      # Boss: 20s / lần gọi
TIMEOUT_TONG_TIEU_BOSS = 25  # Tiểu não: 25s / lần gọi


def _lay_timeout_tong(loai_nao):
    """Lấy timeout tổng theo loại não."""
    if loai_nao == "boss":
        return TIMEOUT_TONG_BOSS
    return TIMEOUT_TONG_TIEU_BOSS


# ================================================================
# KIỂM TRA BLACKLIST
# ================================================================
def _bi_blacklist(provider, model):
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
# GHI LỖI MODEL
# ================================================================
def _ghi_loi(provider, model, loi, loai_loi="khac"):
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
    if not key_info or not ket_qua_loi:
        return "bo_qua"

    loai_loi = ket_qua_loi.get("loai_loi", "")
    key_id = key_info.get("id", "")
    provider = key_info.get("provider", "")

    if loai_loi == "het_quota":
        try:
            from dai_nao.ghi_nho import cap_nhat_quota_key
            cap_nhat_quota_key(key_id, 0)
        except Exception:
            pass
        _ghi_log("tieu-nao", f"Key {key_id[:8]} hết quota → chuyển key.")
        return "chuyen_key"

    if loai_loi == "key_sai":
        _ghi_log("tieu-nao", f"Key {key_id[:8]} sai → bỏ qua.")
        return "chuyen_key"

    if loai_loi == "model_chet":
        _ghi_loi(provider, model, ket_qua_loi.get("loi", ""), "model_chet")
        _ghi_log("tieu-nao", f"Model {model} chết → blacklist.")
        return "chuyen_model"

    return "thu_lai"


def _blacklist_model(provider, model, loi="", loai_loi="khac"):
    if not provider or not model:
        return
    _ghi_loi(provider, model, loi, loai_loi)


# ================================================================
# HÀM CHÍNH
# ================================================================
def do_model(chu_so_huu, prompt, loai_nao=None):
    """
    Bước 2: Dò model theo thứ tự gọi.

    FIX: Timeout tổng khác nhau cho Boss (20s) và Tiểu não (25s).
    """
    thoi_gian_bat_dau = time.time()
    timeout_tong = _lay_timeout_tong(loai_nao)

    ket_qua = {
        "thanh_cong": False,
        "ket_qua": "",
        "provider": "",
        "key_id": "",
        "model": "",
        "loai_nao": loai_nao or "tieu_boss",
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
        kiem_ke = kiem_ke_key(chu_so_huu, loai_nao)
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
        if time.time() - thoi_gian_bat_dau >= timeout_tong:
            ket_qua["loi"] = f"Hết thời gian tổng ({timeout_tong}s)."
            ket_qua["het_thoi_gian"] = True
            _ghi_log("tieu-nao", f"Hết timeout tổng sau {timeout_tong}s.")
            break

        provider = key_info.get("provider", "")
        key_id = key_info.get("id", "")
        ds_model = key_info.get("model_co_the_dung") or []

        ds_model_sach = []
        for m in ds_model:
            if _bi_blacklist(provider, m):
                continue
            ds_model_sach.append(m)

        if not ds_model_sach:
            _ghi_log("tieu-nao", f"Key {key_id[:8]} ({provider}) không có model khả dụng.")
            continue

        for model in ds_model_sach:
            if time.time() - thoi_gian_bat_dau >= timeout_tong:
                ket_qua["loi"] = f"Hết thời gian tổng ({timeout_tong}s)."
                ket_qua["het_thoi_gian"] = True
                break

            hanh_dong = ""

            for lan_thu in range(1, SO_LAN_THU_TOI_DA + 1):
                if time.time() - thoi_gian_bat_dau >= timeout_tong:
                    ket_qua["loi"] = f"Hết thời gian tổng ({timeout_tong}s)."
                    ket_qua["het_thoi_gian"] = True
                    break

                ket_qua["so_lan_thu"] += 1

                _ghi_log(
                    "tieu-nao",
                    f"[{loai_nao or 'tieu_boss'}] Gọi {provider} "
                    f"key={key_id[:8]} model={model} lần {lan_thu}",
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

                if kq_goi.get("thanh_cong"):
                    ket_qua.update({
                        "thanh_cong": True,
                        "ket_qua": kq_goi.get("ket_qua", ""),
                        "provider": provider,
                        "key_id": key_id,
                        "model": model,
                    })
                    _ghi_log(
                        "tieu-nao",
                        f"[{loai_nao or 'tieu_boss'}] Thành công: {provider} / {model}",
                    )
                    return ket_qua

                hanh_dong = _xu_ly_loi(key_info, kq_goi, model)

                if hanh_dong == "chuyen_key":
                    break

                if hanh_dong == "chuyen_model":
                    _blacklist_model(
                        provider, model,
                        kq_goi.get("loi", ""),
                        kq_goi.get("loai_loi", "khac"),
                    )
                    break

            if hanh_dong == "chuyen_key":
                break

            if ket_qua.get("het_thoi_gian"):
                break

        if hanh_dong == "chuyen_key":
            continue

        if ket_qua.get("het_thoi_gian"):
            break

    if not ket_qua["loi"]:
        ket_qua["loi"] = "Đã thử tất cả key và model nhưng không thành công."

    _ghi_log(
        "tieu-nao",
        f"[{loai_nao or 'tieu_boss'}] Dò model thất bại: {ket_qua['loi']}",
    )
    return ket_qua


# ================================================================
# HÀM PHỤ
# ================================================================
def goi_voi_key(chu_so_huu, key_id, prompt, loai_nao=None):
    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        kiem_ke = kiem_ke_key(chu_so_huu, loai_nao)
    except ImportError:
        return {"thanh_cong": False, "loi": "kiem_ke_key.py chưa có."}

    if not kiem_ke.get("thanh_cong"):
        return {"thanh_cong": False, "loi": "Không có key."}

    for key_info in kiem_ke.get("thu_tu_goi", []):
        if key_info.get("id") == key_id:
            return _goi_model(key_info, prompt)

    return {"thanh_cong": False, "loi": f"Không tìm thấy key id={key_id}."}


def goi_voi_provider(chu_so_huu, provider, prompt, loai_nao=None):
    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        kiem_ke = kiem_ke_key(chu_so_huu, loai_nao)
    except ImportError:
        return {"thanh_cong": False, "loi": "kiem_ke_key.py chưa có."}

    if not kiem_ke.get("thanh_cong"):
        return {"thanh_cong": False, "loi": "Không có key."}

    for key_info in kiem_ke.get("thu_tu_goi", []):
        if key_info.get("provider", "").lower() == provider.lower():
            return _goi_model(key_info, prompt)

    return {"thanh_cong": False, "loi": f"Không có key cho {provider}."}


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
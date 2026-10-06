"""
quan_ly_quota.py - Theo dõi quota từng key Rồng Thần.

Nhiệm vụ:
    - lay_quota(key_info): lấy quota hiện tại từ API provider.
    - cap_nhat_quota(key_id, phan_tram): cập nhật quota vào kho 1.
    - lay_quota_tu_kho(key_id): đọc quota từ kho 1.
    - cap_nhat_tat_ca(chu_so_huu): cập nhật quota toàn bộ key.
    - lay_quota_chi_tiet(chu_so_huu): lấy quota chi tiết 3 provider.

Quy tắc (theo Phần 4):
    - Quota Groq: đọc header x-ratelimit-remaining-requests.
    - Quota OpenRouter: gọi /api/v1/key.
    - Quota Gemini: đếm RPM/RPD.
    - Cập nhật mỗi 60 giây.
    - Phần trăm: xanh (>50%), vàng (20-50%), đỏ (<20%), đen (0%).

Trả về:
    {
        provider, key_id, phan_tram, con_lai, tong,
        loai_quota, thoi_gian,
    }

Tầng dữ liệu: dai_nao/ghi_nho.py
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
# LẤY QUOTA GROQ
# ================================================================
def _lay_quota_groq(key):
    """
    Lấy quota Groq từ API.

    Groq trả header:
        x-ratelimit-remaining-requests
        x-ratelimit-limit-requests
        x-ratelimit-remaining-tokens
        x-ratelimit-limit-tokens
    """
    ket_qua = {
        "phan_tram": None,
        "con_lai": None,
        "tong": None,
        "loai_quota": "",
    }

    if not key:
        return ket_qua

    try:
        import requests
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )

        if r.status_code != 200:
            if r.status_code in (401, 403):
                ket_qua["phan_tram"] = 0
                ket_qua["loai_quota"] = "key_sai"
            return ket_qua

        con_lai = r.headers.get("x-ratelimit-remaining-requests")
        tong = r.headers.get("x-ratelimit-limit-requests")

        if con_lai is not None and tong is not None:
            try:
                con_lai = int(con_lai)
                tong = int(tong)
                if tong > 0:
                    phan_tram = int(con_lai / tong * 100)
                else:
                    phan_tram = 100
                return {
                    "phan_tram": phan_tram,
                    "con_lai": con_lai,
                    "tong": tong,
                    "loai_quota": "rpm",
                }
            except (ValueError, TypeError):
                pass

        # Không đọc được header → giả định còn 100%
        return {
            "phan_tram": 100,
            "con_lai": None,
            "tong": None,
            "loai_quota": "",
        }

    except ImportError:
        return ket_qua
    except Exception:
        return ket_qua


# ================================================================
# LẤY QUOTA OPENROUTER
# ================================================================
def _lay_quota_openrouter(key):
    """
    Lấy quota OpenRouter từ API.

    Endpoint: GET https://openrouter.ai/api/v1/key
    """
    ket_qua = {
        "phan_tram": None,
        "con_lai": None,
        "tong": None,
        "loai_quota": "",
    }

    if not key:
        return ket_qua

    try:
        import requests
        r = requests.get(
            "https://openrouter.ai/api/v1/key",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )

        if r.status_code != 200:
            if r.status_code in (401, 403):
                ket_qua["phan_tram"] = 0
                ket_qua["loai_quota"] = "key_sai"
            return ket_qua

        du_lieu = r.json().get("data", {})
        gioi_han = du_lieu.get("limit")
        da_dung = du_lieu.get("usage", 0)

        if gioi_han and gioi_han > 0:
            con_lai = max(0, gioi_han - da_dung)
            phan_tram = int(con_lai / gioi_han * 100)
            return {
                "phan_tram": phan_tram,
                "con_lai": con_lai,
                "tong": gioi_han,
                "loai_quota": "credit",
            }

        # Không có giới hạn → 100%
        return {
            "phan_tram": 100,
            "con_lai": None,
            "tong": None,
            "loai_quota": "",
        }

    except ImportError:
        return ket_qua
    except Exception:
        return ket_qua


# ================================================================
# LẤY QUOTA GEMINI
# ================================================================
def _lay_quota_gemini(key):
    """
    Lấy quota Gemini từ API.

    Endpoint: GET https://generativelanguage.googleapis.com/v1beta/models?key=<key>
    Gemini không trả header quota chính thức.
    """
    ket_qua = {
        "phan_tram": None,
        "con_lai": None,
        "tong": None,
        "loai_quota": "",
    }

    if not key:
        return ket_qua

    try:
        import requests
        r = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
            timeout=10,
        )

        if r.status_code != 200:
            if r.status_code in (401, 403):
                ket_qua["phan_tram"] = 0
                ket_qua["loai_quota"] = "key_sai"
            return ket_qua

        # Gemini không trả header quota → giả định 100% khi key hoạt động
        return {
            "phan_tram": 100,
            "con_lai": None,
            "tong": None,
            "loai_quota": "",
        }

    except ImportError:
        return ket_qua
    except Exception:
        return ket_qua


# ================================================================
# LẤY QUOTA THEO PROVIDER
# ================================================================
def lay_quota(key_info):
    """
    Lấy quota hiện tại từ API provider.

    key_info: dict { id, key, provider, ... }.

    Trả về dict quota.
    """
    ket_qua = {
        "provider": "",
        "key_id": "",
        "phan_tram": None,
        "con_lai": None,
        "tong": None,
        "loai_quota": "",
        "thoi_gian": int(time.time()),
    }

    if not key_info:
        return ket_qua

    provider = (key_info.get("provider") or "").strip()
    key = key_info.get("key") or ""
    key_id = key_info.get("id") or ""

    ket_qua["provider"] = provider
    ket_qua["key_id"] = key_id

    if not provider or not key:
        return ket_qua

    p = provider.lower()
    if p == "groq":
        kq = _lay_quota_groq(key)
    elif p in ("openrouter", "open router", "or"):
        kq = _lay_quota_openrouter(key)
    elif p in ("gemini", "google"):
        kq = _lay_quota_gemini(key)
    else:
        return ket_qua

    ket_qua.update(kq)
    return ket_qua


# ================================================================
# CẬP NHẬT QUOTA VÀO KHO 1
# ================================================================
def cap_nhat_quota(key_id, phan_tram):
    """Cập nhật quota vào kho 1 qua ghi_nho."""
    if not key_id:
        return False

    try:
        from dai_nao.ghi_nho import cap_nhat_quota_key
        return cap_nhat_quota_key(key_id, phan_tram)
    except Exception as e:
        _ghi_log("loi", f"Cập nhật quota lỗi: {e}")
        return False


def lay_quota_tu_kho(key_id):
    """Đọc quota từ kho 1."""
    if not key_id:
        return {}

    try:
        from dai_nao.ghi_nho import lay_key_da_luu
        key = lay_key_da_luu(key_id)
        if not key:
            return {}
        return {
            "phan_tram": key.get("phan_tram", 100),
            "lan_kiem_tra_cuoi": key.get("lan_kiem_tra_cuoi", 0),
        }
    except Exception:
        return {}


# ================================================================
# CẬP NHẬT TẤT CẢ KEY
# ================================================================
def cap_nhat_tat_ca(chu_so_huu):
    """
    Cập nhật quota cho toàn bộ key của tài khoản.

    Trả về: list kết quả cập nhật.
    """
    ket_qua = []

    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        kiem_ke = kiem_ke_key(chu_so_huu)
    except ImportError:
        return ket_qua

    if not kiem_ke.get("thanh_cong"):
        return ket_qua

    for key_info in kiem_ke.get("thu_tu_goi", []):
        kq = lay_quota(key_info)
        key_id = key_info.get("id", "")

        # Cập nhật vào kho 1
        if kq.get("phan_tram") is not None:
            cap_nhat_quota(key_id, kq["phan_tram"])

        ket_qua.append(kq)

    _ghi_log(
        "tieu-nao",
        f"Cập nhật quota {len(ket_qua)} key cho {chu_so_huu}",
    )
    return ket_qua


# ================================================================
# LẤY QUOTA CHI TIẾT
# ================================================================
def lay_quota_chi_tiet(chu_so_huu):
    """
    Lấy quota chi tiết 3 provider.

    Trả về dict:
        {
            "Groq": [{key_id, phan_tram, ...}],
            "OpenRouter": [...],
            "Gemini": [...],
        }
    """
    ket_qua = {"Groq": [], "OpenRouter": [], "Gemini": []}

    try:
        from tieu_nao.kiem_ke_key import kiem_ke_key
        kiem_ke = kiem_ke_key(chu_so_huu)
    except ImportError:
        return ket_qua

    if not kiem_ke.get("thanh_cong"):
        return ket_qua

    for key_info in kiem_ke.get("thu_tu_goi", []):
        provider = key_info.get("provider", "")
        kq = lay_quota(key_info)

        if provider in ket_qua:
            ket_qua[provider].append(kq)

    return ket_qua


# ================================================================
# HÀM PHỤ: XÁC ĐỊNH MÀU QUOTA
# ================================================================
def lay_mau_quota(phan_tram):
    """
    Xác định màu dựa trên phần trăm (theo Phần 6).

    Trả về: "xanh" | "vang" | "do" | "den".
    """
    if phan_tram is None:
        return "khong_ro"
    if phan_tram >= 50:
        return "xanh"
    if phan_tram >= 20:
        return "vang"
    if phan_tram > 0:
        return "do"
    return "den"


def lay_class_quota(phan_tram):
    """Trả class CSS tương ứng."""
    mau = lay_mau_quota(phan_tram)
    bang = {
        "xanh": "quota-xanh",
        "vang": "quota-vang",
        "do": "quota-do",
        "den": "quota-den",
        "khong_ro": "",
    }
    return bang.get(mau, "")


# ================================================================
# HÀM PHỤ: TỔNG HỢP QUOTA
# ================================================================
def tong_hop_quota(chu_so_huu):
    """
    Tổng hợp quota: phần trăm trung bình của tất cả key.
    """
    chi_tiet = lay_quota_chi_tiet(chu_so_huu)
    tat_ca = []
    for ds in chi_tiet.values():
        tat_ca.extend([k.get("phan_tram") for k in ds if k.get("phan_tram") is not None])

    if not tat_ca:
        return {
            "phan_tram_tb": 100,
            "so_key": 0,
            "mau": "khong_ro",
        }

    phan_tram_tb = int(sum(tat_ca) / len(tat_ca))
    return {
        "phan_tram_tb": phan_tram_tb,
        "so_key": len(tat_ca),
        "mau": lay_mau_quota(phan_tram_tb),
    }


# ================================================================
# HÀM PHỤ: TÓM TẮT QUOTA
# ================================================================
def tom_tat_quota(chu_so_huu):
    """Tạo chuỗi tóm tắt quota."""
    chi_tiet = lay_quota_chi_tiet(chu_so_huu)
    phan = []

    for provider, danh_sach in chi_tiet.items():
        if not danh_sach:
            continue
        phan.append(f"📊 {provider}:")
        for kq in danh_sach:
            key_id = kq.get("key_id", "")[:8]
            phan_tram = kq.get("phan_tram")
            mau = lay_mau_quota(phan_tram)

            bieu_tuong = {
                "xanh": "🟢",
                "vang": "🟡",
                "do": "🔴",
                "den": "⚫",
                "khong_ro": "⚪",
            }.get(mau, "⚪")

            phan.append(f"  {bieu_tuong} {key_id}: {phan_tram}%")

    return "\n".join(phan) if phan else "❌ Không có key."


# ================================================================
# HÀM PHỤ: CẦN CẬP NHẬT LẠI KHÔNG
# ================================================================
def can_cap_nhat_lai(key_id, nguong_giay=60):
    """
    Kiểm tra có cần cập nhật lại quota không.
    Nếu lần cập nhật cuối > nguong_giay → cần cập nhật.
    """
    if not key_id:
        return True

    kq = lay_quota_tu_kho(key_id)
    lan_cuoi = kq.get("lan_kiem_tra_cuoi", 0)
    if not lan_cuoi:
        return True

    if int(time.time()) - lan_cuoi > nguong_giay:
        return True

    return False


# ================================================================
# HÀM PHỤ: QUOTA THẤP NHẤT
# ================================================================
def quota_thap_nhat(chu_so_huu):
    """Tìm key có quota thấp nhất."""
    chi_tiet = lay_quota_chi_tiet(chu_so_huu)
    tat_ca = []
    for ds in chi_tiet.values():
        tat_ca.extend([k for k in ds if k.get("phan_tram") is not None])

    if not tat_ca:
        return None

    tat_ca.sort(key=lambda k: k.get("phan_tram", 100))
    return tat_ca[0]


# ================================================================
# HÀM PHỤ: ĐẾM KEY THEO MÀU
# ================================================================
def dem_key_theo_mau(chu_so_huu):
    """Đếm số key theo từng màu quota."""
    chi_tiet = lay_quota_chi_tiet(chu_so_huu)

    dem = {"xanh": 0, "vang": 0, "do": 0, "den": 0, "khong_ro": 0}

    for ds in chi_tiet.values():
        for kq in ds:
            mau = lay_mau_quota(kq.get("phan_tram"))
            dem[mau] = dem.get(mau, 0) + 1

    return dem


# ================================================================
# HÀM PHỤ: DANH SÁCH KEY CÒN DÙNG ĐƯỢC (>= 20%)
# ================================================================
def key_con_dung_duoc(chu_so_huu, nguong=20):
    """Trả danh sách key có quota >= ngưỡng."""
    chi_tiet = lay_quota_chi_tiet(chu_so_huu)
    ket_qua = []

    for ds in chi_tiet.values():
        for kq in ds:
            if kq.get("phan_tram") is not None and kq["phan_tram"] >= nguong:
                ket_qua.append(kq)

    return ket_qua
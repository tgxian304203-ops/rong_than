"""
tim_kiem.py - Gọi API tìm kiếm Tra web Rồng Thần.

Nhiệm vụ:
    - tim_kiem(cau_hoi): tìm kiếm qua SERPJET → Tavily → Bright Data.
    - _goi_serpjet(cau_hoi, so_ket_qua): gọi SERPJET.
    - _goi_tavily(cau_hoi, so_ket_qua): gọi Tavily.
    - _goi_brightdata(cau_hoi, so_ket_qua): gọi Bright Data.
    - _chuan_hoa_ket_qua(danh_sach): chuẩn hóa về format thống nhất.

Quy tắc (theo Phần 4):
    - Tra web gọi SERPJET trước.
    - Nếu hết quota → gọi Tavily.
    - Nếu hết quota → gọi Bright Data.
    - Nếu tất cả hết quota → báo Đại não.
    - Không lưu kết quả vào cây.

Trả về:
    {
        thanh_cong: bool,
        ket_qua: [{tieu_de, mo_ta, url}],
        nguon: [str],       # Tên API đã dùng
        so_ket_qua: int,
        loi: str?,
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
SO_KET_QUA_MAC_DINH = 5
THU_TU_API = ["SERPJET", "Tavily", "Bright Data"]


# ================================================================
# LẤY KEY TRA WEB
# ================================================================
def _lay_key_tra_web(chu_so_huu):
    """
    Lấy danh sách key tra web của tài khoản.

    Trả về: dict { provider: [key_info] }.
    """
    if not chu_so_huu:
        return {}

    try:
        from dai_nao.ghi_nho import lay_danh_sach_key_web_cua
        danh_sach = lay_danh_sach_key_web_cua(chu_so_huu) or []
    except ImportError:
        return {}
    except Exception:
        return {}

    ket_qua = {p: [] for p in THU_TU_API}

    for key in danh_sach:
        provider = (key.get("provider") or "").strip()
        if provider in ket_qua:
            ket_qua[provider].append(key)

    return ket_qua


# ================================================================
# GỌI SERPJET
# ================================================================
def _goi_serpjet(cau_hoi, key, so_ket_qua=SO_KET_QUA_MAC_DINH):
    """Gọi SERPJET API."""
    ket_qua = {"thanh_cong": False, "ket_qua": [], "loi": "", "loai_loi": ""}

    try:
        from tra_web.api.serpjet import tim_kiem_serpjet
        ket_qua_tho = tim_kiem_serpjet(key, cau_hoi, so_ket_qua)
        if ket_qua_tho and ket_qua_tho.get("thanh_cong"):
            ket_qua["thanh_cong"] = True
            ket_qua["ket_qua"] = _chuan_hoa_ket_qua(ket_qua_tho.get("ket_qua", []))
        else:
            ket_qua["loi"] = (ket_qua_tho or {}).get("loi", "SERPJET lỗi.")
            ket_qua["loai_loi"] = (ket_qua_tho or {}).get("loai_loi", "khac")
    except ImportError:
        ket_qua["loi"] = "api/serpjet.py chưa có."
    except Exception as e:
        ket_qua["loi"] = f"Lỗi SERPJET: {e}"

    return ket_qua


# ================================================================
# GỌI TAVILY
# ================================================================
def _goi_tavily(cau_hoi, key, so_ket_qua=SO_KET_QUA_MAC_DINH):
    """Gọi Tavily API."""
    ket_qua = {"thanh_cong": False, "ket_qua": [], "loi": "", "loai_loi": ""}

    try:
        from tra_web.api.tavily import tim_kiem_tavily
        ket_qua_tho = tim_kiem_tavily(key, cau_hoi, so_ket_qua)
        if ket_qua_tho and ket_qua_tho.get("thanh_cong"):
            ket_qua["thanh_cong"] = True
            ket_qua["ket_qua"] = _chuan_hoa_ket_qua(ket_qua_tho.get("ket_qua", []))
        else:
            ket_qua["loi"] = (ket_qua_tho or {}).get("loi", "Tavily lỗi.")
            ket_qua["loai_loi"] = (ket_qua_tho or {}).get("loai_loi", "khac")
    except ImportError:
        ket_qua["loi"] = "api/tavily.py chưa có."
    except Exception as e:
        ket_qua["loi"] = f"Lỗi Tavily: {e}"

    return ket_qua


# ================================================================
# GỌI BRIGHT DATA
# ================================================================
def _goi_brightdata(cau_hoi, key, so_ket_qua=SO_KET_QUA_MAC_DINH):
    """Gọi Bright Data API."""
    ket_qua = {"thanh_cong": False, "ket_qua": [], "loi": "", "loai_loi": ""}

    try:
        from tra_web.api.brightdata import tim_kiem_brightdata
        ket_qua_tho = tim_kiem_brightdata(key, cau_hoi, so_ket_qua)
        if ket_qua_tho and ket_qua_tho.get("thanh_cong"):
            ket_qua["thanh_cong"] = True
            ket_qua["ket_qua"] = _chuan_hoa_ket_qua(ket_qua_tho.get("ket_qua", []))
        else:
            ket_qua["loi"] = (ket_qua_tho or {}).get("loi", "Bright Data lỗi.")
            ket_qua["loai_loi"] = (ket_qua_tho or {}).get("loai_loi", "khac")
    except ImportError:
        ket_qua["loi"] = "api/brightdata.py chưa có."
    except Exception as e:
        ket_qua["loi"] = f"Lỗi Bright Data: {e}"

    return ket_qua


# ================================================================
# CHUẨN HÓA KẾT QUẢ
# ================================================================
def _chuan_hoa_ket_qua(danh_sach):
    """
    Chuẩn hóa kết quả về format thống nhất.
    Mỗi item: { tieu_de, mo_ta, url }.
    """
    if not danh_sach or not isinstance(danh_sach, list):
        return []

    ket_qua = []
    for item in danh_sach:
        if isinstance(item, str):
            ket_qua.append({"tieu_de": "", "mo_ta": item, "url": ""})
        elif isinstance(item, dict):
            ket_qua.append({
                "tieu_de": item.get("tieu_de") or item.get("title") or item.get("name") or "",
                "mo_ta": item.get("mo_ta") or item.get("description") or item.get("snippet") or "",
                "url": item.get("url") or item.get("link") or item.get("href") or "",
            })

    return ket_qua


# ================================================================
# HÀM CHÍNH
# ================================================================
def tim_kiem(cau_hoi, chu_so_huu="", so_ket_qua=SO_KET_QUA_MAC_DINH):
    """
    Tìm kiếm qua 3 API theo thứ tự.

    cau_hoi: chuỗi câu hỏi.
    chu_so_huu: tên đăng nhập (để lấy key tra web).
    so_ket_qua: số kết quả cần lấy.

    Trả về: dict đầy đủ.
    """
    ket_qua = {
        "thanh_cong": False,
        "ket_qua": [],
        "nguon": [],
        "so_ket_qua": 0,
        "loi": "",
    }

    if not cau_hoi:
        ket_qua["loi"] = "Câu hỏi rỗng."
        return ket_qua

    _ghi_log("tra-web", f"Tìm kiếm: {cau_hoi[:80]}")

    # Lấy key tra web
    key_theo_provider = _lay_key_tra_web(chu_so_huu)

    if not any(key_theo_provider.values()):
        ket_qua["loi"] = "Chưa có key tra web."
        return ket_qua

    lich_su = []

    # Thử lần lượt 3 API
    for provider in THU_TU_API:
        danh_sach_key = key_theo_provider.get(provider, [])
        if not danh_sach_key:
            continue

        for key_info in danh_sach_key:
            key = key_info.get("key", "")
            if not key:
                continue

            _ghi_log("tra-web", f"Thử {provider}...")

            if provider == "SERPJET":
                ket_qua_tho = _goi_serpjet(cau_hoi, key, so_ket_qua)
            elif provider == "Tavily":
                ket_qua_tho = _goi_tavily(cau_hoi, key, so_ket_qua)
            elif provider == "Bright Data":
                ket_qua_tho = _goi_brightdata(cau_hoi, key, so_ket_qua)
            else:
                continue

            lich_su.append({
                "provider": provider,
                "thanh_cong": ket_qua_tho.get("thanh_cong"),
                "loai_loi": ket_qua_tho.get("loai_loi", ""),
            })

            # Thành công → trả về
            if ket_qua_tho.get("thanh_cong"):
                ket_qua["thanh_cong"] = True
                ket_qua["ket_qua"] = ket_qua_tho.get("ket_qua", [])
                ket_qua["nguon"] = [provider]
                ket_qua["so_ket_qua"] = len(ket_qua["ket_qua"])

                _ghi_log(
                    "tra-web",
                    f"{provider}: {ket_qua['so_ket_qua']} kết quả.",
                )
                return ket_qua

            # Hết quota → chuyển API tiếp theo
            if ket_qua_tho.get("loai_loi") == "het_quota":
                _ghi_log("tra-web", f"{provider} hết quota → chuyển API.")
                continue

    # Hết tất cả API
    ket_qua["loi"] = "Tất cả API tra web đều thất bại."
    ket_qua["lich_su"] = lich_su

    _ghi_log("tra-web", "Tất cả API tra web thất bại.")
    return ket_qua


# ================================================================
# HÀM PHỤ: TÌM KIẾM NHANH (không cần tài khoản)
# ================================================================
def tim_kiem_nhanh(cau_hoi, key_dict=None, so_ket_qua=SO_KET_QUA_MAC_DINH):
    """
    Tìm kiếm nhanh với key truyền trực tiếp.

    key_dict: { "SERPJET": key1, "Tavily": key2, "Bright Data": key3 }.
    """
    if not cau_hoi or not key_dict:
        return {"thanh_cong": False, "loi": "Thiếu tham số."}

    lich_su = []

    for provider in THU_TU_API:
        key = key_dict.get(provider)
        if not key:
            continue

        if provider == "SERPJET":
            ket_qua_tho = _goi_serpjet(cau_hoi, key, so_ket_qua)
        elif provider == "Tavily":
            ket_qua_tho = _goi_tavily(cau_hoi, key, so_ket_qua)
        elif provider == "Bright Data":
            ket_qua_tho = _goi_brightdata(cau_hoi, key, so_ket_qua)
        else:
            continue

        lich_su.append({
            "provider": provider,
            "thanh_cong": ket_qua_tho.get("thanh_cong"),
        })

        if ket_qua_tho.get("thanh_cong"):
            return {
                "thanh_cong": True,
                "ket_qua": ket_qua_tho.get("ket_qua", []),
                "nguon": [provider],
                "so_ket_qua": len(ket_qua_tho.get("ket_qua", [])),
            }

    return {
        "thanh_cong": False,
        "loi": "Tất cả API thất bại.",
        "lich_su": lich_su,
    }


# ================================================================
# HÀM PHỤ: TÌM KIẾM 1 PROVIDER CỤ THỂ
# ================================================================
def tim_kiem_provider(provider, cau_hoi, key, so_ket_qua=SO_KET_QUA_MAC_DINH):
    """Tìm kiếm qua 1 provider cụ thể."""
    if provider == "SERPJET":
        return _goi_serpjet(cau_hoi, key, so_ket_qua)
    if provider == "Tavily":
        return _goi_tavily(cau_hoi, key, so_ket_qua)
    if provider == "Bright Data":
        return _goi_brightdata(cau_hoi, key, so_ket_qua)

    return {"thanh_cong": False, "loi": f"Provider không hỗ trợ: {provider}"}


# ================================================================
# HÀM PHỤ: TÓM TẮT KẾT QUẢ
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả tìm kiếm."""
    if not ket_qua:
        return ""

    if not ket_qua.get("thanh_cong"):
        return f"❌ Tra web thất bại: {ket_qua.get('loi', '')}"

    nguon = ", ".join(ket_qua.get("nguon", []))
    so = ket_qua.get("so_ket_qua", 0)
    return f"✅ {so} kết quả từ {nguon}"


# ================================================================
# HÀM PHỤ: LẤY URL
# ================================================================
def lay_url(ket_qua):
    """Trích danh sách URL từ kết quả."""
    if not ket_qua or not ket_qua.get("thanh_cong"):
        return []
    return [item.get("url") for item in ket_qua.get("ket_qua", []) if item.get("url")]


def lay_tieu_de(ket_qua):
    """Trích danh sách tiêu đề."""
    if not ket_qua or not ket_qua.get("thanh_cong"):
        return []
    return [item.get("tieu_de") for item in ket_qua.get("ket_qua", []) if item.get("tieu_de")]


# ================================================================
# HÀM PHỤ: DANH SÁCH API HỖ TRỢ
# ================================================================
def danh_sach_api_ho_tro():
    """Trả danh sách 3 API tra web."""
    return list(THU_TU_API)
"""
tim_kiem.py - Gọi API tìm kiếm Tra web Rồng Thần.

Sửa: dai_nao.ghi_nho → luu_tru.ghi_nho.
Thêm DEBUG để kiểm tra key.
"""


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _in_debug(noi_dung):
    """In ra console Render."""
    try:
        print(f"[DEBUG-TRA-WEB] {noi_dung}", flush=True)
    except Exception:
        pass


SO_KET_QUA_MAC_DINH = 5
THU_TU_API = ["SERPJET", "Tavily", "Bright Data"]


def _lay_key_tra_web(chu_so_huu):
    if not chu_so_huu:
        _in_debug("chu_so_huu RỖNG → không có key")
        return {}

    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_web_cua
        danh_sach = lay_danh_sach_key_web_cua(chu_so_huu) or []

        _in_debug(f"chu_so_huu = '{chu_so_huu}'")
        _in_debug(f"Số key tra web tìm được: {len(danh_sach)}")

        for i, k in enumerate(danh_sach):
            _in_debug(
                f"  Key #{i+1}: "
                f"provider={k.get('provider')}, "
                f"loai_key={k.get('loai_key')}, "
                f"chu_so_huu={k.get('chu_so_huu')}, "
                f"id={k.get('id')}"
            )

    except ImportError as e:
        _in_debug(f"ImportError: {e}")
        return {}
    except Exception as e:
        _in_debug(f"Exception: {e}")
        return {}

    ket_qua = {p: [] for p in THU_TU_API}

    for key in danh_sach:
        provider = (key.get("provider") or "").strip()
        if provider in ket_qua:
            ket_qua[provider].append(key)

    _in_debug(f"Phân loại: {[(p, len(ks)) for p, ks in ket_qua.items()]}")

    return ket_qua


def _goi_serpjet(cau_hoi, key, so_ket_qua=SO_KET_QUA_MAC_DINH):
    ket_qua = {"thanh_cong": False, "ket_qua": [], "loi": "", "loai_loi": ""}

    try:
        from dai_nao.tra_web.api.serpjet import tim_kiem_serpjet
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


def _goi_tavily(cau_hoi, key, so_ket_qua=SO_KET_QUA_MAC_DINH):
    ket_qua = {"thanh_cong": False, "ket_qua": [], "loi": "", "loai_loi": ""}

    try:
        from dai_nao.tra_web.api.tavily import tim_kiem_tavily
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


def _goi_brightdata(cau_hoi, key, so_ket_qua=SO_KET_QUA_MAC_DINH):
    ket_qua = {"thanh_cong": False, "ket_qua": [], "loi": "", "loai_loi": ""}

    try:
        from dai_nao.tra_web.api.brightdata import tim_kiem_brightdata
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


def _chuan_hoa_ket_qua(danh_sach):
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


def tim_kiem(cau_hoi, chu_so_huu="", so_ket_qua=SO_KET_QUA_MAC_DINH):
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

    _in_debug(f"=== BẮT ĐẦU TÌM KIẾM ===")
    _in_debug(f"cau_hoi = {cau_hoi[:80]}")
    _in_debug(f"chu_so_huu = '{chu_so_huu}'")

    key_theo_provider = _lay_key_tra_web(chu_so_huu)

    if not any(key_theo_provider.values()):
        _in_debug("KHÔNG CÓ KEY NÀO → trả lỗi")
        ket_qua["loi"] = "Chưa có key tra web."
        return ket_qua

    lich_su = []

    for provider in THU_TU_API:
        danh_sach_key = key_theo_provider.get(provider, [])
        if not danh_sach_key:
            _in_debug(f"Provider {provider}: KHÔNG có key → bỏ qua")
            continue

        _in_debug(f"Provider {provider}: có {len(danh_sach_key)} key")

        for key_info in danh_sach_key:
            key = key_info.get("key", "")
            if not key:
                _in_debug(f"  Key rỗng → bỏ qua")
                continue

            _in_debug(f"  Thử gọi {provider} với key... {key[:10]}...")

            if provider == "SERPJET":
                ket_qua_tho = _goi_serpjet(cau_hoi, key, so_ket_qua)
            elif provider == "Tavily":
                ket_qua_tho = _goi_tavily(cau_hoi, key, so_ket_qua)
            elif provider == "Bright Data":
                ket_qua_tho = _goi_brightdata(cau_hoi, key, so_ket_qua)
            else:
                continue

            _in_debug(
                f"  Kết quả {provider}: "
                f"thanh_cong={ket_qua_tho.get('thanh_cong')}, "
                f"loai_loi={ket_qua_tho.get('loai_loi')}, "
                f"loi={(ket_qua_tho.get('loi') or '')[:100]}"
            )

            lich_su.append({
                "provider": provider,
                "thanh_cong": ket_qua_tho.get("thanh_cong"),
                "loai_loi": ket_qua_tho.get("loai_loi", ""),
            })

            if ket_qua_tho.get("thanh_cong"):
                ket_qua["thanh_cong"] = True
                ket_qua["ket_qua"] = ket_qua_tho.get("ket_qua", [])
                ket_qua["nguon"] = [provider]
                ket_qua["so_ket_qua"] = len(ket_qua["ket_qua"])

                _in_debug(f"  ✅ {provider} THÀNH CÔNG: {ket_qua['so_ket_qua']} kết quả")
                _ghi_log("tra-web", f"{provider}: {ket_qua['so_ket_qua']} kết quả.")
                return ket_qua

            if ket_qua_tho.get("loai_loi") == "het_quota":
                _in_debug(f"  ⏸️ {provider} hết quota → chuyển API.")
                continue

    _in_debug("❌ TẤT CẢ API ĐỀU THẤT BẠI")
    ket_qua["loi"] = "Tất cả API tra web đều thất bại."
    ket_qua["lich_su"] = lich_su

    _ghi_log("tra-web", "Tất cả API tra web thất bại.")
    return ket_qua


def tim_kiem_nhanh(cau_hoi, key_dict=None, so_ket_qua=SO_KET_QUA_MAC_DINH):
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


def tim_kiem_provider(provider, cau_hoi, key, so_ket_qua=SO_KET_QUA_MAC_DINH):
    if provider == "SERPJET":
        return _goi_serpjet(cau_hoi, key, so_ket_qua)
    if provider == "Tavily":
        return _goi_tavily(cau_hoi, key, so_ket_qua)
    if provider == "Bright Data":
        return _goi_brightdata(cau_hoi, key, so_ket_qua)

    return {"thanh_cong": False, "loi": f"Provider không hỗ trợ: {provider}"}


def tom_tat(ket_qua):
    if not ket_qua:
        return ""
    if not ket_qua.get("thanh_cong"):
        return f"❌ Tra web thất bại: {ket_qua.get('loi', '')}"
    nguon = ", ".join(ket_qua.get("nguon", []))
    so = ket_qua.get("so_ket_qua", 0)
    return f"✅ {so} kết quả từ {nguon}"


def lay_url(ket_qua):
    if not ket_qua or not ket_qua.get("thanh_cong"):
        return []
    return [item.get("url") for item in ket_qua.get("ket_qua", []) if item.get("url")]


def lay_tieu_de(ket_qua):
    if not ket_qua or not ket_qua.get("thanh_cong"):
        return []
    return [item.get("tieu_de") for item in ket_qua.get("ket_qua", []) if item.get("tieu_de")]


def danh_sach_api_ho_tro():
    return list(THU_TU_API)
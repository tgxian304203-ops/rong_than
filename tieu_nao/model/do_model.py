"""
do_model.py - Dò Model khả dụng.

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
        print(f"[DEBUG-DO-MODEL] {noi_dung}", flush=True)
    except Exception:
        pass


THU_TU_PROVIDER = ["Groq", "OpenRouter", "Gemini"]
LOAI_NAO_MODEL = "tieu_boss"


def do_model(chu_so_huu):
    """
    Dò tìm Model khả dụng (còn quota).

    Trả về: {
        thanh_cong: bool,
        key, key_id, provider,
        loi?
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "key": "",
        "key_id": "",
        "provider": "",
        "loi": "",
    }

    _in_debug("=== BẮT ĐẦU DÒ MODEL ===")
    _in_debug(f"chu_so_huu = '{chu_so_huu}'")

    if not chu_so_huu:
        _in_debug("chu_so_huu RỖNG → lỗi")
        ket_qua["loi"] = "Thiếu chu_so_huu."
        return ket_qua

    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_cua
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []

        _in_debug(f"Tổng số key tìm được: {len(danh_sach)}")

        for i, k in enumerate(danh_sach):
            _in_debug(
                f"  Key #{i+1}: "
                f"id={k.get('id')}, "
                f"provider={k.get('provider')}, "
                f"loai_key={k.get('loai_key')}, "
                f"loai_nao={k.get('loai_nao')}, "
                f"chu_so_huu={k.get('chu_so_huu')}, "
                f"phan_tram={k.get('phan_tram')}"
            )

    except Exception as e:
        _in_debug(f"Lỗi lấy danh sách key: {e}")
        ket_qua["loi"] = f"Không lấy được danh sách key: {e}"
        return ket_qua

    danh_sach_loc = []
    for key in danh_sach:
        if key.get("loai_key") == "tra_web":
            _in_debug(f"  Bỏ qua key tra_web: id={key.get('id')}")
            continue
        if key.get("loai_nao") != LOAI_NAO_MODEL:
            _in_debug(
                f"  Bỏ qua key loai_nao={key.get('loai_nao')} "
                f"(cần {LOAI_NAO_MODEL}): id={key.get('id')}"
            )
            continue
        danh_sach_loc.append(key)

    _in_debug(f"Sau khi lọc loai_nao='{LOAI_NAO_MODEL}': {len(danh_sach_loc)} key")

    if not danh_sach_loc:
        _in_debug(f"❌ KHÔNG CÓ KEY MODEL (loai_nao='{LOAI_NAO_MODEL}')")
        ket_qua["loi"] = "Chưa có key Model."
        return ket_qua

    danh_sach_loc.sort(key=lambda k: _thu_tu_provider(k.get("provider", "")))

    for key in danh_sach_loc:
        key_id = key.get("id", "")
        provider = key.get("provider", "")
        phan_tram = key.get("phan_tram", 100)

        _in_debug(
            f"Xét key: id={key_id}, provider={provider}, phan_tram={phan_tram}"
        )

        if phan_tram <= 0:
            _in_debug(f"  → phan_tram <= 0 → bỏ qua")
            continue

        try:
            from luu_tru.trang_thai_key import kiem_tra_hoi_quota
            con_dung = kiem_tra_hoi_quota(LOAI_NAO_MODEL, provider, key_id)
            _in_debug(f"  → kiem_tra_hoi_quota = {con_dung}")

            if not con_dung:
                _in_debug(f"  → hết quota → bỏ qua")
                continue
        except Exception as e:
            _in_debug(f"  → lỗi kiem_tra_hoi_quota: {e}")

        ket_qua["thanh_cong"] = True
        ket_qua["key"] = key.get("key", "")
        ket_qua["key_id"] = key_id
        ket_qua["provider"] = provider

        _in_debug(f"  ✅ CHỌN KEY: {provider} (id={key_id})")
        _ghi_log("tieu-nao", f"Dò Model: {provider}")
        return ket_qua

    _in_debug("❌ Tất cả key Model đều hết quota")
    ket_qua["loi"] = "Tất cả key Model đều hết quota."
    return ket_qua


def _thu_tu_provider(provider):
    """Trả thứ tự ưu tiên provider."""
    try:
        return THU_TU_PROVIDER.index(provider)
    except (ValueError, TypeError):
        return 999


def dem_key_kha_dung(chu_so_huu):
    """Đếm số key Model còn dùng được."""
    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_cua
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    except Exception:
        return 0

    dem = 0
    for key in danh_sach:
        if key.get("loai_key") == "tra_web":
            continue
        if key.get("loai_nao") != LOAI_NAO_MODEL:
            continue
        if key.get("phan_tram", 100) > 0:
            dem += 1

    return dem


def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt dò Model."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ Model: {ket_qua.get('provider')}"
    return f"❌ Dò Model lỗi: {ket_qua.get('loi', '')[:100]}"
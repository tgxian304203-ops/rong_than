"""
do_boss.py - Dò tìm Boss khả dụng.

Sửa: chấp nhận key cũ (không có loai_nao) + key mới.
Thêm DEBUG + set loai_loi.
"""


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _in_debug(noi_dung):
    try:
        print(f"[DEBUG-DO-BOSS] {noi_dung}", flush=True)
    except Exception:
        pass


THU_TU_PROVIDER = ["Groq", "OpenRouter", "Gemini"]

LOAI_BOSS_DAU = "boss"
LOAI_BOSS_THE = "tieu_boss"


def do_boss(chu_so_huu, loai_nao=LOAI_BOSS_DAU):
    """
    Dò tìm Boss khả dụng (còn quota).

    Chấp nhận:
        - Key có loai_nao khớp (key mới).
        - Key KHÔNG có loai_nao (key cũ).
    """
    ket_qua = {
        "thanh_cong": False,
        "key": "",
        "key_id": "",
        "provider": "",
        "loai_nao": loai_nao,
        "loai_loi": "",
        "loi": "",
    }

    _in_debug("=== DÒ BOSS ===")
    _in_debug(f"chu_so_huu = '{chu_so_huu}'")
    _in_debug(f"loai_nao cần tìm = '{loai_nao}'")

    if not chu_so_huu:
        _in_debug("chu_so_huu RỖNG")
        ket_qua["loi"] = "Thiếu chu_so_huu."
        ket_qua["loai_loi"] = "thieu_tham_so"
        return ket_qua

    if loai_nao not in (LOAI_BOSS_DAU, LOAI_BOSS_THE):
        _in_debug(f"loai_nao không hợp lệ: {loai_nao}")
        ket_qua["loi"] = f"Loại Boss không hợp lệ: {loai_nao}"
        ket_qua["loai_loi"] = "sai_loai"
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
        ket_qua["loai_loi"] = "loi_db"
        return ket_qua

    danh_sach_loc = []
    for key in danh_sach:
        if key.get("loai_key") == "tra_web":
            _in_debug(f"  Bỏ qua key tra_web: id={key.get('id')}")
            continue

        ln = key.get("loai_nao")
        if ln is None:
            ln_str = ""
        else:
            ln_str = str(ln).strip().lower()

        # Chấp nhận: rỗng (key cũ) HOẶC khớp loai_nao cần tìm
        if ln_str and ln_str != loai_nao:
            _in_debug(
                f"  Bỏ qua key loai_nao='{ln_str}' "
                f"(cần rỗng hoặc '{loai_nao}'): id={key.get('id')}"
            )
            continue

        danh_sach_loc.append(key)

    _in_debug(f"Sau khi lọc: {len(danh_sach_loc)} key")

    if not danh_sach_loc:
        _in_debug(f"❌ KHÔNG CÓ KEY BOSS (loai_nao='{loai_nao}')")
        ket_qua["loi"] = f"Chưa có key Boss loại '{loai_nao}'."
        ket_qua["loai_loi"] = "khong_co_key"
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
            _in_debug(f"  → phan_tram <= 0 → bỏ qua (hết quota)")
            continue

        try:
            from luu_tru.trang_thai_key import kiem_tra_hoi_quota
            con_dung = kiem_tra_hoi_quota(loai_nao, provider, key_id)
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

        _in_debug(f"  ✅ CHỌN BOSS: {provider} (id={key_id}, loai_nao={loai_nao})")
        _ghi_log("dai-nao", f"Dò Boss: {provider} ({loai_nao})")
        return ket_qua

    _in_debug(f"❌ Tất cả key Boss loại '{loai_nao}' đều hết quota")
    ket_qua["loi"] = f"Tất cả key Boss loại '{loai_nao}' đều hết quota."
    ket_qua["loai_loi"] = "het_quota"
    return ket_qua


def _thu_tu_provider(provider):
    try:
        return THU_TU_PROVIDER.index(provider)
    except (ValueError, TypeError):
        return 999


def dem_key_kha_dung(chu_so_huu, loai_nao=LOAI_BOSS_DAU):
    try:
        from luu_tru.ghi_nho import lay_danh_sach_key_cua
        danh_sach = lay_danh_sach_key_cua(chu_so_huu) or []
    except Exception:
        return 0

    dem = 0
    for key in danh_sach:
        if key.get("loai_key") == "tra_web":
            continue
        ln = key.get("loai_nao")
        if ln is None:
            ln_str = ""
        else:
            ln_str = str(ln).strip().lower()
        if ln_str and ln_str != loai_nao:
            continue
        if key.get("phan_tram", 100) > 0:
            dem += 1

    return dem


def do_ca_2_loai_boss(chu_so_huu):
    return {
        "boss": do_boss(chu_so_huu, LOAI_BOSS_DAU),
        "tieu_boss": do_boss(chu_so_huu, LOAI_BOSS_THE),
    }


def tom_tat(ket_qua):
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ Boss: {ket_qua.get('provider')} ({ket_qua.get('loai_nao')})"
    return f"❌ Dò Boss lỗi: {ket_qua.get('loi', '')[:100]}"
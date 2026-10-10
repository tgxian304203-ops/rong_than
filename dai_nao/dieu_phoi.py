"""
dieu_phoi.py - Điều phối toàn bộ luồng Đại não.

SỬA:
    - BOSS là bên nhận yêu cầu trực tiếp (suy luận + phân loại + lập kế hoạch).
    - Đại não chỉ ghi hợp đồng + điều phối Model.
    - Luồng đúng: Boss nhận → Boss xử lý → Đại não ghi Cây → Đại não gọi Model.
"""

import time


THOI_GIAN_VERIFY_TOI_DA = 99
SO_LAN_SUA_TOI_DA = 5


TU_KHOA_TRA_WEB = [
    "giá", "tỷ giá", "vàng", "bạc", "usd", "đô la", "euro",
    "chứng khoán", "cổ phiếu", "bitcoin", "crypto", "tiền ảo",
    "lãi suất", "lạm phát", "giá xăng", "giá điện", "giá nhà",
    "giá đất", "giá vàng", "bảng giá", "niêm yết",
    "hôm nay", "hôm qua", "ngày mai", "hiện tại", "bây giờ",
    "mới nhất", "gần đây", "tuần này", "tháng này", "năm nay",
    "thời tiết", "dự báo", "nhiệt độ", "mưa", "nắng",
    "tin tức", "thời sự", "sự kiện", "diễn biến", "kết quả",
    "tra cứu", "tìm hiểu về", "thông tin về",
]


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _in_debug(noi_dung):
    try:
        print(f"[DEBUG-DIEU-PHOI] {noi_dung}", flush=True)
    except Exception:
        pass


def _tao_loi(loi, nguon_loi):
    return {
        "thanh_cong": False,
        "loi": loi,
        "nguon_loi": nguon_loi,
    }


def _can_tra_web(noi_dung):
    if not noi_dung:
        return False
    t = noi_dung.lower()
    for tu_khoa in TU_KHOA_TRA_WEB:
        if tu_khoa in t:
            return True
    return False


def _ghep_ket_qua_web(noi_dung, ket_qua_web):
    tong_hop = ket_qua_web.get("tong_hop", "")
    nguon = ket_qua_web.get("nguon", [])

    if not tong_hop:
        return noi_dung

    phan = [
        f"Câu hỏi của user: {noi_dung}",
        "",
        "Thông tin tra web mới nhất:",
        tong_hop,
        "",
    ]

    if nguon:
        phan.append(f"(Nguồn: {', '.join(nguon)})")
        phan.append("")

    phan.append(
        "Hãy trả lời câu hỏi dựa trên thông tin tra web ở trên."
    )

    return "\n".join(phan)


def _tra_web_neu_can(noi_dung, chu_so_huu):
    if not _can_tra_web(noi_dung):
        return noi_dung

    _in_debug(f"Cần tra web: {noi_dung[:80]}")
    _ghi_log("dai-nao", f"Đại não tra web cho: {noi_dung[:80]}")

    try:
        from dai_nao.tra_web.dieu_phoi_tra_web import dieu_phoi_tra_web

        ket_qua_web = dieu_phoi_tra_web(
            noi_dung, chu_so_huu,
            so_ket_qua=5,
            lay_noi_dung=False,
        )

        if ket_qua_web.get("thanh_cong"):
            _in_debug(f"Tra web OK: {ket_qua_web.get('so_ket_qua', 0)} kết quả")
            _ghi_log("dai-nao", f"Tra web OK: {ket_qua_web.get('so_ket_qua', 0)} kết quả")
            return _ghep_ket_qua_web(noi_dung, ket_qua_web)

        _in_debug(f"Tra web lỗi: {ket_qua_web.get('loi', '')}")

    except Exception as e:
        _in_debug(f"Tra web exception: {e}")

    return noi_dung


def dieu_phoi(du_lieu):
    """
    Điều phối luồng chính.

    Luồng đúng:
        1. Boss NHẬN yêu cầu + suy luận + phân loại + lập kế hoạch.
        2. Đại não đọc kết quả Boss.
        3. Đại não ghi hợp đồng vào Cây (nếu dự án).
        4. Đại não gọi Model (nếu cần).
        5. Verify + trả user.
    """
    if not du_lieu:
        return _tao_loi("Thiếu dữ liệu.", "dai_nao")

    noi_dung = du_lieu.get("noi_dung", "")
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    id_chat = du_lieu.get("id_chat", "")

    if not noi_dung:
        return _tao_loi("Không có nội dung.", "dai_nao")

    _in_debug("=== ĐẠI NÃO ĐIỀU PHỐI ===")
    _in_debug(f"noi_dung = {noi_dung[:80]}")
    _in_debug(f"chu_so_huu = '{chu_so_huu}'")

    _ghi_log("dai-nao", f"Đại não điều phối: {noi_dung[:80]}")

    # 1. Tra web trước nếu cần (Đại não làm)
    noi_dung_moi = _tra_web_neu_can(noi_dung, chu_so_huu)

    if noi_dung_moi != noi_dung:
        du_lieu = dict(du_lieu)
        du_lieu["noi_dung"] = noi_dung_moi

    # 2. BOSS NHẬN YÊU CẦU + XỬ LÝ (phân loại + lập kế hoạch + viết HĐ)
    _in_debug("→ Gọi Boss nhận yêu cầu + xử lý")
    ket_qua_boss = _goi_boss_nhan_yeu_cau(du_lieu)

    if not ket_qua_boss or not ket_qua_boss.get("thanh_cong"):
        _in_debug(f"Boss lỗi: {(ket_qua_boss or {}).get('loi', '')}")
        return _tao_loi(
            (ket_qua_boss or {}).get("loi", "Boss không xử lý được."),
            "boss_model",
        )

    # 3. Lấy phân loại từ Boss
    loai = ket_qua_boss.get("loai", "don_gian")
    _in_debug(f"Boss phân loại: {loai}")

    # 4. Nếu là DỰ ÁN → ghi hợp đồng + gọi Model
    if loai == "du_an":
        return _xu_ly_du_an(du_lieu, ket_qua_boss, chu_so_huu, id_chat)

    # 5. Nếu ĐƠN GIẢN → trả lời trực tiếp từ Boss
    return _xu_ly_don_gian(du_lieu, ket_qua_boss, chu_so_huu, id_chat)


def _goi_boss_nhan_yeu_cau(du_lieu):
    """
    BOSS NHẬN YÊU CẦU:
        - Đọc yêu cầu.
        - Phân loại (đơn giản / dự án).
        - Nếu dự án → lập kế hoạch + viết hợp đồng + viết hướng dẫn.
        - Nếu đơn giản → trả lời.
    """
    _in_debug("=== BOSS NHẬN YÊU CẦU ===")

    try:
        from dai_nao.boss_model.goi_boss import goi_boss_nhan_yeu_cau
        ket_qua = goi_boss_nhan_yeu_cau({
            "noi_dung": du_lieu.get("noi_dung", ""),
            "lich_su": du_lieu.get("lich_su", []),
            "chu_so_huu": du_lieu.get("chu_so_huu", "khach"),
        })
        _in_debug(f"← Boss trả về: {ket_qua}")
        return ket_qua
    except ImportError as e:
        _in_debug(f"ImportError: {e}")
        return _tao_loi(f"Boss chưa sẵn sàng: {e}", "boss_model")
    except Exception as e:
        _in_debug(f"Exception: {e}")
        return _tao_loi(f"Boss lỗi: {e}", "boss_model")


def _xu_ly_don_gian(du_lieu, ket_qua_boss, chu_so_huu, id_chat):
    """Xử lý luồng đơn giản — chỉ Boss trả lời."""
    _in_debug("--- LUỒNG ĐƠN GIẢN ---")

    tra_loi = ket_qua_boss.get("tra_loi", "")

    if chu_so_huu and id_chat:
        try:
            from dai_nao.ghi_hop_dong import ghi_hop_dong_moi
            ghi_hop_dong_moi(
                chu_so_huu, id_chat,
                dang_lam_gi=du_lieu.get("noi_dung", "")[:200],
                dang_lam_toi_dau="1/1",
                tiep_theo_lam_gi="Trả lời",
            )
        except Exception:
            pass

    return {
        "thanh_cong": True,
        "tra_loi": tra_loi,
        "code": ket_qua_boss.get("code"),
        "ngon_ngu": ket_qua_boss.get("ngon_ngu"),
    }


def _xu_ly_du_an(du_lieu, ket_qua_boss, chu_so_huu, id_chat):
    """Xử lý luồng dự án."""
    _in_debug("--- LUỒNG DỰ ÁN ---")

    # 1. Đại não GHI hợp đồng vào Cây
    if chu_so_huu and id_chat:
        try:
            from dai_nao.ghi_hop_dong import ghi_tu_ke_hoach
            ghi_tu_ke_hoach(chu_so_huu, id_chat, ket_qua_boss)
            _in_debug("Đã ghi hợp đồng vào Cây")
        except Exception as e:
            _in_debug(f"Ghi hợp đồng lỗi: {e}")

    # 2. Lấy bước hiện tại
    danh_sach_buoc = ket_qua_boss.get("danh_sach_buoc", [])
    if not danh_sach_buoc:
        return _tao_loi("Boss không lập được danh sách bước.", "boss_model")

    buoc_hien_tai = danh_sach_buoc[0]
    _in_debug(f"Bước hiện tại: {buoc_hien_tai}")

    # 3. Tạo prompt CỤ THỂ cho Model
    prompt_model = _tao_prompt_cho_model(
        du_lieu.get("noi_dung", ""),
        buoc_hien_tai,
        ket_qua_boss.get("huong_dan", ""),
    )

    _in_debug(f"Prompt cho Model: {prompt_model[:200]}")

    # 4. Gọi Tiểu não → Model sinh code
    du_lieu_model = dict(du_lieu)
    du_lieu_model["noi_dung"] = prompt_model
    du_lieu_model["loai_task"] = "sinh_code"

    ket_qua_buoc = _chi_huy_model(du_lieu_model)

    if not ket_qua_buoc or not ket_qua_buoc.get("thanh_cong"):
        return _tao_loi(
            (ket_qua_buoc or {}).get("loi", "Model không sinh được code."),
            "tieu_nao",
        )

    # 5. Verify code
    ket_qua_cuoi = _verify_va_cap_nhat(ket_qua_buoc, chu_so_huu, id_chat)

    # 6. Lưu kết quả
    if chu_so_huu and id_chat:
        try:
            from dai_nao.luu_ket_qua import luu_ket_qua
            luu_ket_qua(chu_so_huu, id_chat, ket_qua_cuoi)
        except Exception:
            pass

    return ket_qua_cuoi


def _tao_prompt_cho_model(noi_dung_goc, buoc, huong_dan):
    """Tạo prompt CỤ THỂ cho Model sinh code."""
    phan = [
        f"Yêu cầu dự án: {noi_dung_goc}",
        "",
        f"Bước hiện tại: {buoc}",
        "",
    ]

    if huong_dan:
        phan.append(f"Hướng dẫn: {huong_dan}")
        phan.append("")

    phan.append(
        "Hãy viết code cho bước này. "
        "Chỉ trả về code trong khối markdown, không giải thích."
    )

    return "\n".join(phan)


def _chi_huy_model(du_lieu):
    _in_debug("=== ĐẠI NÃO GỌI TIỂU NÃO ===")
    _in_debug(f"chu_so_huu = '{du_lieu.get('chu_so_huu')}'")
    _in_debug(f"loai_task = '{du_lieu.get('loai_task')}'")

    try:
        from tieu_nao.nhan_lenh import nhan_lenh
        ket_qua = nhan_lenh(du_lieu)
        _in_debug(f"← nhan_lenh trả về: {ket_qua}")
        return ket_qua
    except ImportError as e:
        _in_debug(f"ImportError: {e}")
        return _tao_loi(f"Tiểu não chưa sẵn sàng: {e}", "tieu_nao")
    except Exception as e:
        _in_debug(f"Exception: {e}")
        return _tao_loi(f"Tiểu não lỗi: {e}", "tieu_nao")


def _verify_va_cap_nhat(ket_qua, chu_so_huu, id_chat):
    if ket_qua.get("code"):
        ket_qua = _verify_code(ket_qua, chu_so_huu, id_chat)

    if chu_so_huu and id_chat:
        try:
            from dai_nao.ghi_hop_dong import cap_nhat_hop_dong
            cap_nhat_hop_dong(
                chu_so_huu, id_chat,
                dang_lam_toi_dau=_dem_buoc_hien_tai(chu_so_huu, id_chat),
            )
        except Exception:
            pass

    return ket_qua


def _verify_code(ket_qua, chu_so_huu, id_chat):
    code = ket_qua.get("code")
    ngon_ngu = ket_qua.get("ngon_ngu", "python")

    if not code:
        return ket_qua

    bat_dau = time.time()
    so_lan_sua = 0
    ket_qua_hien_tai = ket_qua
    ket_qua_chay = {}

    while so_lan_sua < SO_LAN_SUA_TOI_DA:
        if time.time() - bat_dau > THOI_GIAN_VERIFY_TOI_DA:
            _ghi_log("dai-nao", "Hết 99s verify — dừng.")
            ket_qua_hien_tai["het_thoi_gian"] = True
            return ket_qua_hien_tai

        try:
            if ngon_ngu == "html":
                from tieu_nao.sanbox.chay_html import chay_html
                ket_qua_chay = chay_html({"code": code})
            else:
                from tieu_nao.sanbox.chay_python import chay_python
                ket_qua_chay = chay_python({"code": code})
        except Exception as e:
            _ghi_log("loi", f"Sandbox lỗi: {e}")
            ket_qua_hien_tai["ket_qua_chay"] = {
                "thanh_cong": False,
                "loi": str(e),
            }
            return ket_qua_hien_tai

        if ket_qua_chay.get("thanh_cong"):
            ket_qua_hien_tai["ket_qua_chay"] = ket_qua_chay
            _ghi_log("dai-nao", f"Code OK sau {so_lan_sua} lần sửa.")
            return ket_qua_hien_tai

        so_lan_sua += 1
        _ghi_log("dai-nao", f"Code lỗi — sửa lần {so_lan_sua}")

        try:
            from dai_nao.boss_model.goi_boss import goi_boss_sua_code
            ket_qua_sua = goi_boss_sua_code({
                "code_cu": code,
                "loi": ket_qua_chay.get("stderr") or ket_qua_chay.get("loi", ""),
                "ngon_ngu": ngon_ngu,
                "chu_so_huu": chu_so_huu,
            })

            if ket_qua_sua and ket_qua_sua.get("code_moi"):
                code = ket_qua_sua["code_moi"]
                ket_qua_hien_tai["code"] = code
            else:
                break
        except ImportError:
            break
        except Exception as e:
            _ghi_log("loi", f"Boss sửa code lỗi: {e}")
            break

    ket_qua_hien_tai["so_lan_sua"] = so_lan_sua
    ket_qua_hien_tai["ket_qua_chay"] = ket_qua_chay

    if not ket_qua_chay.get("thanh_cong"):
        ket_qua_hien_tai["can_chay_lai"] = True

    return ket_qua_hien_tai


def _dem_buoc_hien_tai(chu_so_huu, id_chat):
    try:
        from cay_linh_hon.tien_do import doc_tien_do
        tien_do = doc_tien_do(chu_so_huu, id_chat)
        if tien_do:
            return f"{tien_do.get('buoc_hien_tai', 0)}/{tien_do.get('tong_buoc', 0)}"
    except Exception:
        pass
    return "0/0"
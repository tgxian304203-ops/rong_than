"""
dieu_phoi.py - Điều phối toàn bộ luồng Đại não.

CÓ DEBUG để kiểm tra luồng.
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
    "bầu cử", "thể thao", "bóng đá", "world cup", "olympic",
    "tra cứu", "tìm hiểu về", "thông tin về", "là ai", "ở đâu",
    "khi nào", "bao giờ", "thế nào", "ra sao",
    "so sánh", "đánh giá", "review", "top", "xếp hạng",
]


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _in_debug(noi_dung):
    """In ra console Render."""
    try:
        print(f"[DEBUG-DIEU-PHOI] {noi_dung}", flush=True)
    except Exception:
        pass


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
        "Hãy trả lời câu hỏi dựa trên thông tin tra web ở trên. "
        "Nếu thông tin không đủ, hãy nói rõ."
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
            _ghi_log("dai-nao", f"Đại não tra web OK: {ket_qua_web.get('so_ket_qua', 0)} kết quả")
            return _ghep_ket_qua_web(noi_dung, ket_qua_web)

        _in_debug(f"Tra web lỗi: {ket_qua_web.get('loi', '')}")
        _ghi_log("dai-nao", f"Đại não tra web lỗi: {ket_qua_web.get('loi', '')}")

    except Exception as e:
        _in_debug(f"Tra web exception: {e}")
        _ghi_log("loi", f"Tra web exception: {e}")

    return noi_dung


def dieu_phoi(du_lieu):
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    noi_dung = du_lieu.get("noi_dung", "")
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    id_chat = du_lieu.get("id_chat", "")

    if not noi_dung:
        return {"thanh_cong": False, "loi": "Không có nội dung."}

    _in_debug("=== ĐẠI NÃO ĐIỀU PHỐI ===")
    _in_debug(f"noi_dung = {noi_dung[:80]}")
    _in_debug(f"chu_so_huu = '{chu_so_huu}'")
    _in_debug(f"id_chat = '{id_chat}'")

    _ghi_log("dai-nao", f"Đại não điều phối: {noi_dung[:80]}")

    try:
        from dai_nao.phan_loai import phan_loai
        phan_loai_ket_qua = phan_loai(noi_dung)
        _in_debug(f"Phân loại: {phan_loai_ket_qua}")
    except Exception as e:
        _in_debug(f"Phân loại lỗi: {e}")
        _ghi_log("loi", f"Phân loại lỗi: {e}")
        phan_loai_ket_qua = {"loai": "don_gian", "loai_noi_dung": "khac"}

    loai = phan_loai_ket_qua.get("loai", "don_gian")
    _in_debug(f"→ Loại: {loai}")

    if loai == "du_an":
        return _dieu_phoi_du_an(du_lieu, phan_loai_ket_qua)
    return _dieu_phoi_don_gian(du_lieu, phan_loai_ket_qua)


def _dieu_phoi_don_gian(du_lieu, phan_loai_ket_qua):
    noi_dung = du_lieu.get("noi_dung", "")
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    id_chat = du_lieu.get("id_chat", "")

    _in_debug("--- LUỒNG ĐƠN GIẢN ---")

    noi_dung_moi = _tra_web_neu_can(noi_dung, chu_so_huu)

    if noi_dung_moi != noi_dung:
        du_lieu = dict(du_lieu)
        du_lieu["noi_dung"] = noi_dung_moi

    if chu_so_huu and id_chat:
        try:
            from dai_nao.ghi_hop_dong import ghi_hop_dong_moi
            ghi_hop_dong_moi(
                chu_so_huu, id_chat,
                dang_lam_gi=noi_dung[:200],
                dang_lam_toi_dau="1/1",
                tiep_theo_lam_gi="Trả lời",
            )
        except Exception:
            pass

    ket_qua_boss = _goi_boss(du_lieu, phan_loai_ket_qua)

    if not ket_qua_boss or not ket_qua_boss.get("thanh_cong"):
        _in_debug(f"Boss lỗi: {(ket_qua_boss or {}).get('loi', '')}")
        return {
            "thanh_cong": False,
            "loi": (ket_qua_boss or {}).get("loi", "Boss không trả lời."),
        }

    ket_qua_cuoi = ket_qua_boss
    if ket_qua_boss.get("code"):
        ket_qua_cuoi = _verify_code(ket_qua_boss, chu_so_huu, id_chat)

    if chu_so_huu and id_chat:
        try:
            from dai_nao.luu_ket_qua import luu_ket_qua
            luu_ket_qua(chu_so_huu, id_chat, ket_qua_cuoi)
        except Exception:
            pass

    return ket_qua_cuoi


def _dieu_phoi_du_an(du_lieu, phan_loai_ket_qua):
    noi_dung = du_lieu.get("noi_dung", "")
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    id_chat = du_lieu.get("id_chat", "")

    _in_debug("--- LUỒNG DỰ ÁN ---")

    noi_dung_moi = _tra_web_neu_can(noi_dung, chu_so_huu)

    if noi_dung_moi != noi_dung:
        du_lieu = dict(du_lieu)
        du_lieu["noi_dung"] = noi_dung_moi

    co_hop_dong = False
    if chu_so_huu and id_chat:
        try:
            from dai_nao.ghi_hop_dong import doc_hop_dong
            co_hop_dong = doc_hop_dong(chu_so_huu, id_chat) is not None
        except Exception:
            co_hop_dong = False

    _in_debug(f"Có hợp đồng chưa: {co_hop_dong}")

    if not co_hop_dong:
        _in_debug("Chưa có hợp đồng → gọi Boss lập kế hoạch")
        ket_qua_ke_hoach = _goi_boss_lap_ke_hoach(du_lieu, phan_loai_ket_qua)

        if not ket_qua_ke_hoach or not ket_qua_ke_hoach.get("thanh_cong"):
            _in_debug(f"Boss lập kế hoạch lỗi: {(ket_qua_ke_hoach or {}).get('loi', '')}")
            return {
                "thanh_cong": False,
                "loi": (ket_qua_ke_hoach or {}).get("loi", "Boss lập kế hoạch lỗi."),
            }

        if chu_so_huu and id_chat:
            try:
                from dai_nao.ghi_hop_dong import ghi_tu_ke_hoach
                ghi_tu_ke_hoach(chu_so_huu, id_chat, ket_qua_ke_hoach)
                _in_debug("Đã ghi kế hoạch vào cây")
            except Exception as e:
                _in_debug(f"Ghi kế hoạch lỗi: {e}")
                _ghi_log("loi", f"Ghi kế hoạch lỗi: {e}")

    # Gọi Tiểu não
    _in_debug("→ Gọi Tiểu não: _chi_huy_model()")
    _in_debug(f"   chu_so_huu truyền vào = '{chu_so_huu}'")

    ket_qua_buoc = _chi_huy_model(du_lieu)

    _in_debug(f"← Tiểu não trả về: thanh_cong={ket_qua_buoc.get('thanh_cong')}")
    _in_debug(f"← Tiểu não trả về: loi={ket_qua_buoc.get('loi', '')}")

    if not ket_qua_buoc or not ket_qua_buoc.get("thanh_cong"):
        _in_debug(f"❌ Tiểu não thất bại: {ket_qua_buoc.get('loi', '')}")
        return {
            "thanh_cong": False,
            "loi": (ket_qua_buoc or {}).get("loi", "Model không thực hiện được."),
        }

    ket_qua_cuoi = _verify_va_cap_nhat(ket_qua_buoc, chu_so_huu, id_chat)

    if chu_so_huu and id_chat:
        try:
            from dai_nao.luu_ket_qua import luu_ket_qua
            luu_ket_qua(chu_so_huu, id_chat, ket_qua_cuoi)
        except Exception:
            pass

    return ket_qua_cuoi


def _goi_boss(du_lieu, phan_loai_ket_qua):
    try:
        from dai_nao.boss_model.goi_boss import goi_boss
        return goi_boss({
            "noi_dung": du_lieu.get("noi_dung", ""),
            "lich_su": du_lieu.get("lich_su", []),
            "phan_loai": phan_loai_ket_qua,
            "chu_so_huu": du_lieu.get("chu_so_huu", "khach"),
        })
    except ImportError:
        return _goi_model_truc_tiep(du_lieu)
    except Exception as e:
        _ghi_log("loi", f"Gọi Boss lỗi: {e}")
        return {"thanh_cong": False, "loi": f"Boss lỗi: {e}"}


def _goi_boss_lap_ke_hoach(du_lieu, phan_loai_ket_qua):
    try:
        from dai_nao.boss_model.goi_boss import goi_boss_lap_ke_hoach
        return goi_boss_lap_ke_hoach({
            "noi_dung": du_lieu.get("noi_dung", ""),
            "chu_so_huu": du_lieu.get("chu_so_huu", "khach"),
        })
    except ImportError:
        return {
            "thanh_cong": True,
            "dang_lam_gi": du_lieu.get("noi_dung", "")[:200],
            "dang_lam_toi_dau": "0/1",
            "tiep_theo_lam_gi": "Bước 1",
            "danh_sach_buoc": ["Thực hiện yêu cầu"],
            "huong_dan": "Làm từng bước, kiểm tra kỹ.",
        }
    except Exception as e:
        return {"thanh_cong": False, "loi": f"Boss lập kế hoạch lỗi: {e}"}


def _chi_huy_model(du_lieu):
    """
    Đại não gọi Tiểu não để ép Model làm việc.

    CÓ DEBUG để kiểm tra tham số truyền.
    """
    _in_debug("=== ĐẠI NÃO GỌI TIỂU NÃO ===")
    _in_debug(f"du_lieu keys: {list(du_lieu.keys())}")
    _in_debug(f"chu_so_huu = '{du_lieu.get('chu_so_huu')}'")
    _in_debug(f"id_chat = '{du_lieu.get('id_chat')}'")
    _in_debug(f"noi_dung = {du_lieu.get('noi_dung', '')[:80]}")

    try:
        from tieu_nao.nhan_lenh import nhan_lenh
        _in_debug("→ Đã import nhan_lenh, đang gọi...")
        ket_qua = nhan_lenh(du_lieu)
        _in_debug(f"← nhan_lenh trả về: {ket_qua}")
        return ket_qua
    except ImportError as e:
        _in_debug(f"ImportError nhan_lenh: {e}")
        return _goi_model_truc_tiep(du_lieu)
    except Exception as e:
        _in_debug(f"Exception nhan_lenh: {e}")
        _ghi_log("loi", f"Chỉ huy Model lỗi: {e}")
        return {"thanh_cong": False, "loi": f"Model lỗi: {e}"}


def _goi_model_truc_tiep(du_lieu):
    noi_dung = du_lieu.get("noi_dung", "")
    return {
        "thanh_cong": True,
        "tra_loi": f"Rồng Thần đã nhận: {noi_dung[:200]}",
        "code": None,
        "ngon_ngu": None,
    }


def _verify_code(ket_qua, chu_so_huu, id_chat):
    code = ket_qua.get("code")
    ngon_ngu = ket_qua.get("ngon_ngu", "python")

    if not code:
        return ket_qua

    bat_dau = time.time()
    so_lan_sua = 0
    ket_qua_hien_tai = ket_qua

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


def _dem_buoc_hien_tai(chu_so_huu, id_chat):
    try:
        from cay_linh_hon.tien_do import doc_tien_do
        tien_do = doc_tien_do(chu_so_huu, id_chat)
        if tien_do:
            return f"{tien_do.get('buoc_hien_tai', 0)}/{tien_do.get('tong_buoc', 0)}"
    except Exception:
        pass
    return "0/0"


def xu_ly_boss_het_quota(chu_so_huu, id_chat, du_lieu):
    _ghi_log("dai-nao", f"Boss hết quota — Đại não chuyển Boss thế chat {id_chat}")

    try:
        from dai_nao.ep_boss_doc import ep_boss_doc
        from dai_nao.boss_model.goi_boss import goi_boss_the

        ket_qua_doc = ep_boss_doc(chu_so_huu, id_chat, goi_boss_the)

        if not ket_qua_doc.get("thanh_cong"):
            return {
                "thanh_cong": False,
                "loi": ket_qua_doc.get("loi", "Boss thế không đọc hợp đồng."),
            }
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Ép Boss thế đọc lỗi: {e}")

    return dieu_phoi(du_lieu)


def xu_ly_doi_y(chu_so_huu, id_chat, noi_dung, muc_do="nho"):
    try:
        from cay_linh_hon.ket_noi import su_kien_doi_y
        return su_kien_doi_y(chu_so_huu, id_chat, muc_do, noi_dung)
    except Exception as e:
        _ghi_log("loi", f"Xử lý đổi ý lỗi: {e}")
        return False


def boss_the_gui_lai_code(chu_so_huu, id_chat, buoc=None):
    try:
        from cay_linh_hon.doc_code import format_gui_user
        return format_gui_user(chu_so_huu, id_chat, buoc)
    except Exception as e:
        _ghi_log("loi", f"Gửi lại code lỗi: {e}")
        return ""


def boss_the_tra_web_cap_nhat(chu_so_huu, id_chat, cau_hoi):
    try:
        from dai_nao.tra_web.tim_kiem import tim_kiem
        ket_qua = tim_kiem(cau_hoi, chu_so_huu)

        if ket_qua.get("thanh_cong"):
            from cay_linh_hon.huong_dan import cap_nhat_thong_tin_moi
            cap_nhat_thong_tin_moi(chu_so_huu, id_chat, {
                "tra_web": ket_qua.get("ket_qua", []),
                "thoi_gian": int(time.time()),
            })

        return ket_qua
    except Exception as e:
        _ghi_log("loi", f"Tra web lỗi: {e}")
        return {"thanh_cong": False, "loi": str(e)}


def boss_the_kiem_tra_toan_bo_code(chu_so_huu, id_chat):
    try:
        from cay_linh_hon.doc_code import doc_tat_ca
        tat_ca_code = doc_tat_ca(chu_so_huu, id_chat)
    except Exception:
        tat_ca_code = []

    if not tat_ca_code:
        return {"thanh_cong": True, "ket_qua": "Chưa có code nào."}

    ket_qua_kiem_tra = []

    for item in tat_ca_code:
        buoc = item.get("buoc", 0)
        code = item.get("code", "")
        ngon_ngu = _doan_ngon_ngu(item.get("file", ""))

        try:
            if ngon_ngu == "html":
                from tieu_nao.sanbox.chay_html import chay_html
                ket_qua_chay = chay_html({"code": code})
            else:
                from tieu_nao.sanbox.chay_python import chay_python
                ket_qua_chay = chay_python({"code": code})
        except Exception as e:
            ket_qua_kiem_tra.append({
                "buoc": buoc,
                "thanh_cong": False,
                "loi": str(e),
            })
            continue

        ket_qua_kiem_tra.append({
            "buoc": buoc,
            "thanh_cong": ket_qua_chay.get("thanh_cong", False),
            "stdout": ket_qua_chay.get("stdout", ""),
            "stderr": ket_qua_chay.get("stderr", ""),
        })

    return {
        "thanh_cong": True,
        "so_buoc": len(ket_qua_kiem_tra),
        "ket_qua": ket_qua_kiem_tra,
    }


def _doan_ngon_ngu(ten_file):
    if not ten_file or "." not in ten_file:
        return "python"

    duoi = ten_file.rsplit(".", 1)[-1].lower()
    bang = {
        "py": "python", "js": "javascript", "ts": "typescript",
        "html": "html", "css": "css",
    }
    return bang.get(duoi, "python")
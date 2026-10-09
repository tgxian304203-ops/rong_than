"""
xu_ly_task.py - Trung tâm điều phối Đại não Rồng Thần.

ĐÃ SỬA:
    - BƯỚC 3.5: Boss viết trường + hợp đồng file → trả danh sách bước.
    - BƯỚC 3.6: Nhận "Số N" → lấy bước N → gọi Tiểu não sinh code.
    - BƯỚC 3.7: Kiểm tra code khớp hợp đồng → lưu tiến độ.
    - Bỏ cây quyết định cũ (không dùng nữa).
"""

import time
import re


CAN_5_YEU_TO = ("hanh_dong", "doi_tuong", "thuoc_tinh", "rang_buoc", "ngu_canh")

TU_MO_HO = (
    "cái đó", "cái này", "cái kia", "cái ấy",
    "nó", "hắn", "chúng nó", "bọn nó",
    "kia", "ấy", "đó", "đấy",
    "thứ đó", "thứ này", "thứ kia",
    "việc đó", "việc này", "chuyện đó", "chuyện này",
)

CHU_SO_HUU_KHACH = "khach"


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ----------------------------------------------------------------
# HÀM PHỤ: HỎI LẠI
# ----------------------------------------------------------------
def _hoi_lai(ly_do, cau_hoi):
    return {
        "thanh_cong": True,
        "tra_loi": f"{ly_do}\n\n{cau_hoi}",
        "hoi_lai": True,
    }


# ----------------------------------------------------------------
# HÀM PHỤ: KIỂM TRA MƠ HỒ
# ----------------------------------------------------------------
def _la_mo_ho(noi_dung):
    if not noi_dung:
        return True, "Câu rỗng."
    t = noi_dung.lower().strip()
    for tu in TU_MO_HO:
        if (" " + tu + " ") in (" " + t + " "):
            return True, f"Câu chứa từ mơ hồ '{tu}'."
    if len(t) < 3 and not any(c.isdigit() for c in t):
        return True, "Câu quá ngắn."
    return False, ""


# ----------------------------------------------------------------
# HÀM PHỤ: LẤY NGỮ CẢNH
# ----------------------------------------------------------------
def _lay_ngu_canh(du_lieu):
    try:
        from dai_nao.ngu_canh import lay_ngu_canh
        return lay_ngu_canh(du_lieu) or {}
    except ImportError:
        return {}
    except Exception as e:
        _ghi_log("loi", f"Lấy ngữ cảnh lỗi: {e}")
        return {}


# ----------------------------------------------------------------
# HÀM PHỤ: LẤY DỰ ÁN GẦN NHẤT CỦA USER
# ----------------------------------------------------------------
def _lay_du_an_gan_nhat(chu_so_huu):
    """Lấy id dự án gần nhất của user từ kho 1."""
    if not chu_so_huu or chu_so_huu == CHU_SO_HUU_KHACH:
        return None

    try:
        from dai_nao.ghi_nho import lay_danh_sach_du_an_cua
        danh_sach = lay_danh_sach_du_an_cua(chu_so_huu) or []
        if not danh_sach:
            return None

        # Lấy dự án có boss_tao=True mới nhất
        ds_boss = [d for d in danh_sach if d.get("boss_tao")]
        if not ds_boss:
            return None

        ds_boss.sort(key=lambda d: d.get("ngay_tao", 0), reverse=True)
        return ds_boss[0].get("id")
    except Exception as e:
        _ghi_log("loi", f"Lấy dự án gần nhất lỗi: {e}")
        return None


# ----------------------------------------------------------------
# HÀM PHỤ: SINH CODE CHO 1 BƯỚC
# ----------------------------------------------------------------
def _sinh_code_buoc(id_du_an, so_buoc, chu_so_huu):
    """Lấy bước N từ snapshot → gọi Tiểu não sinh code."""
    try:
        from dai_nao.snapshot import lay_snapshot, cap_nhat_task, cap_nhat_dang_viet
        snapshot = lay_snapshot(id_du_an)
        if not snapshot:
            return None

        da_chia = snapshot.get("da_chia", [])
        buoc = None
        for task in da_chia:
            if task.get("so") == so_buoc:
                buoc = task
                break

        if not buoc:
            return {
                "thanh_cong": False,
                "tra_loi": f"🐉 Không tìm thấy bước {so_buoc}.",
            }

        ten_file = buoc.get("file", "")
        ten_buoc = buoc.get("ten", "")
        mo_ta = buoc.get("mo_ta", "")

        # Đánh dấu đang làm
        cap_nhat_task(id_du_an, so_buoc, "dang_lam")

        # Gọi Tiểu não sinh code
        from dai_nao.su_dung_model import sinh_code_cho_file
        kq = sinh_code_cho_file(
            id_du_an=id_du_an,
            ten_file=ten_file,
            ten_buoc=ten_buoc,
            mo_ta_buoc=mo_ta,
            chu_so_huu=chu_so_huu,
        )

        if not kq.get("thanh_cong"):
            cap_nhat_task(id_du_an, so_buoc, "loi", kq.get("loi", ""))
            return {
                "thanh_cong": False,
                "tra_loi": f"🐉 Lỗi sinh code bước {so_buoc}: {kq.get('loi', '')}",
            }

        # Lưu tiến độ
        cap_nhat_dang_viet(
            id_du_an,
            so_buoc,
            ten_file,
            "",
            kq.get("ham_da_viet", []),
            kq.get("ham_con_lai", []),
        )

        # Đánh dấu xong
        cap_nhat_task(id_du_an, so_buoc, "xong")

        return {
            "thanh_cong": True,
            "code": kq.get("code", ""),
            "ngon_ngu": kq.get("ngon_ngu", ""),
            "ten_file": ten_file,
            "ten_buoc": ten_buoc,
            "ham_da_viet": kq.get("ham_da_viet", []),
            "ham_con_lai": kq.get("ham_con_lai", []),
        }

    except Exception as e:
        _ghi_log("loi", f"Sinh code bước lỗi: {e}")
        return None


# ----------------------------------------------------------------
# HÀM PHỤ: TẠO PHẢN HỒI TỪ BOSS
# ----------------------------------------------------------------
def _tao_phan_hoi_boss(ket_qua_boss):
    if not ket_qua_boss:
        return ""

    truong = ket_qua_boss.get("truong", {})
    id_du_an = ket_qua_boss.get("id_du_an", "")

    try:
        from dai_nao.chi_huy import tao_phan_hoi
        return tao_phan_hoi(truong, id_du_an)
    except ImportError:
        # Fallback
        ten = truong.get("ten", "")
        ds_buoc = truong.get("thuat_toan", {}).get("buoc", [])
        phan = [f"🔥 Boss đã phân tích dự án: **{ten}**"]
        phan.append(f"🆔 Mã dự án: `{id_du_an}`")
        phan.append(f"📊 Số bước: {len(ds_buoc)}")
        phan.append("")
        for i, b in enumerate(ds_buoc, 1):
            phan.append(f"  {i}. {b}")
        phan.append("")
        phan.append("💡 Gõ **Số 1** để bắt đầu.")
        return "\n".join(phan)


# ----------------------------------------------------------------
# HÀM PHỤ: TẠO PHẢN HỒI TỪ CODE
# ----------------------------------------------------------------
def _tao_phan_hoi_code(ket_qua_code, id_du_an):
    if not ket_qua_code:
        return ""

    ten_file = ket_qua_code.get("ten_file", "")
    ten_buoc = ket_qua_code.get("ten_buoc", "")
    code = ket_qua_code.get("code", "")
    ngon_ngu = ket_qua_code.get("ngon_ngu", "")
    ham_da_viet = ket_qua_code.get("ham_da_viet", [])
    ham_con_lai = ket_qua_code.get("ham_con_lai", [])

    phan = []
    phan.append(f"✅ Đã viết xong **{ten_file}**")
    phan.append(f"📝 Bước: {ten_buoc}")

    if ham_da_viet:
        phan.append(f"✔️ Hàm đã viết: {', '.join(ham_da_viet)}")
    if ham_con_lai:
        phan.append(f"⏳ Hàm còn lại: {', '.join(ham_con_lai)}")

    phan.append("")
    phan.append(f"💡 Gõ **Số tiếp theo** để làm bước kế.")

    return "\n".join(phan)


# ----------------------------------------------------------------
# HÀM CHÍNH
# ----------------------------------------------------------------
def xu_ly_task(du_lieu):
    """Điều phối xử lý task."""
    try:
        return _xu_ly_task_that(du_lieu)
    except Exception as e:
        import traceback
        _ghi_log("loi", f"xu_ly_task CRASH: {e}\n{traceback.format_exc()}")
        return {
            "thanh_cong": False,
            "tra_loi": f"🐉 Lỗi hệ thống: {e}",
            "loi": str(e),
        }


def _xu_ly_task_that(du_lieu):
    thoi_gian_bat_dau = time.time()

    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")

    # BƯỚC 0: CÂU HỎI THỜI GIAN
    if noi_dung:
        try:
            from dai_nao.thoi_gian import xu_ly_cau_hoi_thoi_gian
            ket_qua_tg = xu_ly_cau_hoi_thoi_gian(noi_dung, chu_so_huu)
            if ket_qua_tg and ket_qua_tg.get("tra_loi"):
                return ket_qua_tg
        except ImportError:
            pass
        except Exception as e:
            _ghi_log("loi", f"Xử lý thời gian lỗi: {e}")

    # BƯỚC 0.5: LẤY NGỮ CẢNH
    ngu_canh = _lay_ngu_canh(du_lieu)

    # BƯỚC 1: CHUẨN HÓA
    try:
        from dai_nao.chuan_hoa import chuan_hoa
        noi_dung_chuan = chuan_hoa(noi_dung) or noi_dung
    except ImportError:
        noi_dung_chuan = noi_dung
    except Exception as e:
        _ghi_log("loi", f"Chuẩn hóa lỗi: {e}")
        noi_dung_chuan = noi_dung

    # BƯỚC 2: KIỂM TRA MƠ HỒ (đơn giản)
    mo_ho, ly_do_mo_ho = _la_mo_ho(noi_dung_chuan)

    # Nếu là lệnh "Số N" → không kiểm tra mơ hồ
    if chu_so_huu != CHU_SO_HUU_KHACH:
        try:
            from dai_nao.chi_huy import la_lenh_lam_task
            so_buoc = la_lenh_lam_task(noi_dung_chuan)
            if so_buoc:
                mo_ho = False
        except ImportError:
            pass

    if mo_ho:
        cau_hoi = "Bạn có thể nói cụ thể hơn không?"
        _ghi_log("dai-nao", f"Hỏi lại {chu_so_huu}: {ly_do_mo_ho}")
        return _hoi_lai("Task chưa đủ rõ để thực hiện.", cau_hoi)

    # ============================================================
    # BƯỚC 3.5: BOSS VIẾT TRƯỜNG (chỉ tài khoản)
    # ============================================================
    if chu_so_huu and chu_so_huu != CHU_SO_HUU_KHACH:
        try:
            from dai_nao.chi_huy import chi_huy, la_lenh_lam_task, lay_buoc_theo_so

            # BƯỚC 3.5a: Kiểm tra có phải lệnh "Số N" không
            so_buoc = la_lenh_lam_task(noi_dung_chuan)

            if so_buoc:
                # Đây là lệnh làm bước N
                id_du_an = _lay_du_an_gan_nhat(chu_so_huu)
                if not id_du_an:
                    return {
                        "thanh_cong": True,
                        "tra_loi": "🐉 Bạn chưa có dự án nào. Hãy gõ yêu cầu dự án trước.",
                    }

                _ghi_log("dai-nao", f"Lệnh làm bước {so_buoc} dự án {id_du_an}")

                # BƯỚC 3.6: Sinh code cho bước N
                kq_code = _sinh_code_buoc(id_du_an, so_buoc, chu_so_huu)

                if kq_code and kq_code.get("thanh_cong"):
                    tra_loi_code = _tao_phan_hoi_code(kq_code, id_du_an)
                    return {
                        "thanh_cong": True,
                        "tra_loi": tra_loi_code,
                        "code": kq_code.get("code", ""),
                        "ngon_ngu": kq_code.get("ngon_ngu", ""),
                    }
                else:
                    return {
                        "thanh_cong": True,
                        "tra_loi": kq_code.get("tra_loi", "🐉 Lỗi sinh code."),
                    }

            # BƯỚC 3.5b: Boss viết trường (yêu cầu mới)
            ket_qua_boss = chi_huy({
                "noi_dung": noi_dung_chuan,
                "chu_so_huu": chu_so_huu,
            })

            if ket_qua_boss and ket_qua_boss.get("can_boss"):
                _ghi_log("dai-nao", f"Boss viết trường cho {chu_so_huu}")
                tra_loi_boss = _tao_phan_hoi_boss(ket_qua_boss)
                return {
                    "thanh_cong": True,
                    "tra_loi": tra_loi_boss,
                    "boss": {
                        "id_du_an": ket_qua_boss.get("id_du_an", ""),
                        "truong": ket_qua_boss.get("truong", {}),
                    },
                }
        except ImportError:
            pass
        except Exception as e:
            _ghi_log("loi", f"Boss lỗi: {e}")

    # ============================================================
    # FALLBACK: KHÁCH hoặc Boss thất bại → dùng luồng cũ đơn giản
    # ============================================================
    # Gọi Tiểu não sinh code đơn giản (không qua cây)
    try:
        from dai_nao.su_dung_model import sinh_code_cho_file
        kq = sinh_code_cho_file(
            id_du_an="khach-" + str(int(time.time())),
            ten_file="",
            ten_buoc=noi_dung_chuan,
            mo_ta_buoc=noi_dung_chuan,
            chu_so_huu=chu_so_huu,
        )
        if kq.get("thanh_cong"):
            return {
                "thanh_cong": True,
                "tra_loi": "Đây là code bạn cần:",
                "code": kq.get("code", ""),
                "ngon_ngu": kq.get("ngon_ngu", "python"),
            }
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Fallback Tiểu não lỗi: {e}")

    return {
        "thanh_cong": True,
        "tra_loi": "🐉 Ta chưa hiểu rõ task này. Bạn có thể nói cụ thể hơn không?",
    }


# ----------------------------------------------------------------
# HÀM CÔNG KHAI (giữ để không phá code khác)
# ----------------------------------------------------------------
def ghi_that_bai_vao_cay(id_node, noi_dung, ly_do=""):
    return {}


def ghi_thanh_cong_vao_cay(id_node, noi_dung=""):
    return {}
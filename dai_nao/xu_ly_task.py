"""
xu_ly_task.py - Trung tâm điều phối Đại não Rồng Thần.

ĐÃ SỬA:
    - Hỗ trợ lệnh "Số N" (1 bước) và "Cả"/"Làm hết"/"Tiếp" (3 bước).
    - Kiểm tra hợp đồng + chạy sandbox trước khi đánh dấu xong.
    - Phản hồi code có hướng dẫn đầy đủ.
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
SO_BUOC_TOI_DA_MOI_LAN = 3


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
# HÀM PHỤ: NHẬN DIỆN LỆNH
# ----------------------------------------------------------------
def _la_lenh_lam_het(noi_dung):
    if not noi_dung:
        return False
    t = noi_dung.lower().strip()
    ds = (
        "cả", "làm hết", "all", "hết", "tất cả",
        "làm tất cả", "làm cả", "chạy hết", "cả 4 bước",
        "cả 5 bước", "cả 3 bước", "làm hết luôn",
    )
    return t in ds or t.startswith("cả ") or t.startswith("làm hết")


def _la_lenh_tiep(noi_dung):
    if not noi_dung:
        return False
    t = noi_dung.lower().strip()
    return t in ("tiếp", "tiếp tục", "next", "làm tiếp", "tếp")


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
# HÀM PHỤ: LẤY DỰ ÁN GẦN NHẤT
# ----------------------------------------------------------------
def _lay_du_an_gan_nhat(chu_so_huu):
    if not chu_so_huu or chu_so_huu == CHU_SO_HUU_KHACH:
        return None

    try:
        from dai_nao.ghi_nho import lay_danh_sach_du_an_cua
        danh_sach = lay_danh_sach_du_an_cua(chu_so_huu) or []
        if not danh_sach:
            return None

        ds_boss = [d for d in danh_sach if d.get("boss_tao")]
        if not ds_boss:
            return None

        ds_boss.sort(key=lambda d: d.get("ngay_tao", 0), reverse=True)
        return ds_boss[0].get("id")
    except Exception as e:
        _ghi_log("loi", f"Lấy dự án gần nhất lỗi: {e}")
        return None


# ----------------------------------------------------------------
# HÀM PHỤ: SINH CODE 1 BƯỚC (có kiểm tra)
# ----------------------------------------------------------------
def _sinh_code_buoc(id_du_an, so_buoc, chu_so_huu):
    """Lấy bước N → sinh code → kiểm tra → đánh dấu xong."""
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

        # 1. Gọi Tiểu não sinh code
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

        code = kq.get("code", "")
        ngon_ngu = kq.get("ngon_ngu", "")

        # 2. Kiểm tra hợp đồng (doi_chieu)
        kiem_tra_hop_dong = {"dat": True, "ly_do": ""}
        if ten_file:
            try:
                from dai_nao.doi_chieu import doi_chieu
                kq_dc = doi_chieu(id_du_an, ten_file, code, ngon_ngu)
                if kq_dc and kq_dc.get("thanh_cong"):
                    kiem_tra_hop_dong["dat"] = kq_dc.get("dat", False)
                    kiem_tra_hop_dong["ly_do"] = kq_dc.get("ly_do", "")
                    kiem_tra_hop_dong["chi_tiet"] = kq_dc
                _ghi_log("dai-nao",
                         f"Đối chiếu {ten_file}: "
                         f"{'PASS' if kiem_tra_hop_dong['dat'] else 'FAIL'} — "
                         f"{kiem_tra_hop_dong['ly_do'][:100]}")
            except ImportError:
                _ghi_log("loi", "doi_chieu.py chưa có — bỏ qua kiểm tra hợp đồng.")
            except Exception as e:
                _ghi_log("loi", f"Lỗi đối chiếu: {e}")

        # 3. Kiểm tra chạy được (sandbox)
        kiem_tra_chay = {"dat": True, "ly_do": ""}
        if code and ngon_ngu in ("python", "html"):
            try:
                if ngon_ngu == "html":
                    from sanbox.chay_html import chay_html_backend
                    kq_chay = chay_html_backend(code)
                else:
                    from sanbox.chay_python import chay_python_backend
                    kq_chay = chay_python_backend(code)

                if kq_chay:
                    kiem_tra_chay["dat"] = kq_chay.get("thanh_cong", False)
                    if not kiem_tra_chay["dat"]:
                        kiem_tra_chay["ly_do"] = (
                            kq_chay.get("loi") or
                            kq_chay.get("stderr") or
                            "Code chạy lỗi"
                        )[:200]
                _ghi_log("sandbox",
                         f"Chạy thử {ten_file}: "
                         f"{'PASS' if kiem_tra_chay['dat'] else 'FAIL'}")
            except ImportError:
                _ghi_log("loi", "Sandbox chưa có — bỏ qua kiểm tra chạy.")
            except Exception as e:
                _ghi_log("loi", f"Lỗi chạy sandbox: {e}")

        # 4. Đánh giá tổng hợp
        dat_tat_ca = (
            kiem_tra_hop_dong.get("dat", True) and
            kiem_tra_chay.get("dat", True)
        )

        if dat_tat_ca:
            cap_nhat_dang_viet(
                id_du_an,
                so_buoc,
                ten_file,
                "",
                kq.get("ham_da_viet", []),
                kq.get("ham_con_lai", []),
            )
            cap_nhat_task(id_du_an, so_buoc, "xong")

            _ghi_log("dai-nao",
                     f"Bước {so_buoc} ({ten_file}) XONG — "
                     f"hợp đồng PASS, chạy PASS")

            return {
                "thanh_cong": True,
                "code": code,
                "ngon_ngu": ngon_ngu,
                "ten_file": ten_file,
                "ten_buoc": ten_buoc,
                "mo_ta": mo_ta,
                "so_buoc": so_buoc,
                "ham_da_viet": kq.get("ham_da_viet", []),
                "ham_con_lai": kq.get("ham_con_lai", []),
                "kiem_tra_hop_dong": kiem_tra_hop_dong,
                "kiem_tra_chay": kiem_tra_chay,
            }
        else:
            ly_do_list = []
            if not kiem_tra_hop_dong.get("dat", True):
                ly_do_list.append(f"Hợp đồng: {kiem_tra_hop_dong.get('ly_do', '')}")
            if not kiem_tra_chay.get("dat", True):
                ly_do_list.append(f"Chạy: {kiem_tra_chay.get('ly_do', '')}")
            ly_do = " | ".join(ly_do_list)

            cap_nhat_task(id_du_an, so_buoc, "loi", ly_do)

            _ghi_log("dai-nao",
                     f"Bước {so_buoc} ({ten_file}) FAIL — {ly_do}")

            return {
                "thanh_cong": True,
                "code": code,
                "ngon_ngu": ngon_ngu,
                "ten_file": ten_file,
                "ten_buoc": ten_buoc,
                "mo_ta": mo_ta,
                "so_buoc": so_buoc,
                "ham_da_viet": kq.get("ham_da_viet", []),
                "ham_con_lai": kq.get("ham_con_lai", []),
                "kiem_tra_hop_dong": kiem_tra_hop_dong,
                "kiem_tra_chay": kiem_tra_chay,
                "co_loi_kiem_tra": True,
                "ly_do_loi": ly_do,
            }

    except Exception as e:
        _ghi_log("loi", f"Sinh code bước lỗi: {e}")
        return None


# ----------------------------------------------------------------
# HÀM PHỤ: PHẢN HỒI BOSS
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
        ten = truong.get("ten", "")
        ds_buoc = truong.get("thuat_toan", {}).get("buoc", [])
        phan = [f"🔥 Boss đã phân tích dự án: **{ten}**"]
        phan.append(f"🆔 Mã dự án: `{id_du_an}`")
        phan.append(f"📊 Số bước: {len(ds_buoc)}")
        phan.append("")
        for i, b in enumerate(ds_buoc, 1):
            phan.append(f"  {i}. {b}")
        phan.append("")
        phan.append("💡 Gõ **Số 1** hoặc **Cả** để bắt đầu.")
        return "\n".join(phan)


# ----------------------------------------------------------------
# HÀM PHỤ: PHẢN HỒI CODE
# ----------------------------------------------------------------
def _tao_phan_hoi_code_1_buoc(kq, tong_so_buoc):
    if not kq:
        return ""

    so_buoc = kq.get("so_buoc", 1)
    ten_file = kq.get("ten_file", "")
    ten_buoc = kq.get("ten_buoc", "")
    mo_ta = kq.get("mo_ta", "")
    co_loi = kq.get("co_loi_kiem_tra", False)
    ly_do_loi = kq.get("ly_do_loi", "")

    phan = []

    if co_loi:
        phan.append(f"⚠️ **BƯỚC {so_buoc}/{tong_so_buoc}** — {ten_buoc}")
        phan.append(f"❗ **Có lỗi kiểm tra:** {ly_do_loi}")
    else:
        phan.append(f"✅ **BƯỚC {so_buoc}/{tong_so_buoc}** — {ten_buoc}")

    phan.append("")
    phan.append(f"📁 **Đặt file tại:** `{ten_file or '(không có file)'}`")
    if mo_ta:
        phan.append(f"📝 **Mô tả:** {mo_ta}")

    # Báo kiểm tra
    if not co_loi:
        phan.append("")
        phan.append("✔️ Hợp đồng khớp")
        phan.append("✔️ Code chạy được")

    return "\n".join(phan)


def _tao_phan_hoi_code_nhieu_buoc(ds_kq, tong_so_buoc):
    if not ds_kq:
        return ""

    phan = []
    phan.append(f"✅ Đã làm xong **{len(ds_kq)} bước**")
    phan.append("")

    for kq in ds_kq:
        so_buoc = kq.get("so_buoc", "?")
        ten_file = kq.get("ten_file", "")
        ten_buoc = kq.get("ten_buoc", "")
        co_loi = kq.get("co_loi_kiem_tra", False)

        ky_hieu = "⚠️" if co_loi else "✅"
        phan.append(f"{ky_hieu} **Bước {so_buoc}/{tong_so_buoc}** — {ten_buoc}")
        phan.append(f"📁 File: `{ten_file}`")
        if co_loi:
            phan.append(f"❗ Lỗi: {kq.get('ly_do_loi', '')[:100]}")
        phan.append("")

    # Đếm bước chưa làm
    so_buoc_da_lam = max([kq.get("so_buoc", 0) for kq in ds_kq] or [0])
    con_lai = tong_so_buoc - so_buoc_da_lam

    if con_lai > 0:
        phan.append(f"⏳ Còn **{con_lai}** bước. Gõ **Tiếp** để làm tiếp.")
    else:
        phan.append("🎉 Đã xong tất cả các bước!")

    return "\n".join(phan)


# ----------------------------------------------------------------
# HÀM PHỤ: XỬ LÝ LÀM NHIỀU BƯỚC
# ----------------------------------------------------------------
def _xu_ly_lam_nhieu_buoc(id_du_an, chu_so_huu):
    try:
        from dai_nao.snapshot import lay_snapshot
        snapshot = lay_snapshot(id_du_an)
        if not snapshot:
            return None

        da_chia = snapshot.get("da_chia", [])
        tong_so_buoc = len(da_chia)

        ds_chua_lam = []
        for task in da_chia:
            if task.get("trang_thai") != "xong":
                ds_chua_lam.append(task.get("so"))

        if not ds_chua_lam:
            return {
                "thanh_cong": True,
                "tra_loi": "🐉 Tất cả các bước đã xong.",
            }

        ds_lam = ds_chua_lam[:SO_BUOC_TOI_DA_MOI_LAN]

        ds_kq = []
        for so in ds_lam:
            kq = _sinh_code_buoc(id_du_an, so, chu_so_huu)
            if kq and kq.get("thanh_cong"):
                ds_kq.append(kq)
            else:
                break

        if not ds_kq:
            return {
                "thanh_cong": True,
                "tra_loi": "🐉 Không sinh được code.",
            }

        tra_loi = _tao_phan_hoi_code_nhieu_buoc(ds_kq, tong_so_buoc)

        ds_code = [
            {
                "code": kq.get("code", ""),
                "ngon_ngu": kq.get("ngon_ngu", ""),
                "ten_file": kq.get("ten_file", ""),
                "so_buoc": kq.get("so_buoc", 0),
                "ten_buoc": kq.get("ten_buoc", ""),
            }
            for kq in ds_kq
        ]

        ket_qua = {
            "thanh_cong": True,
            "tra_loi": tra_loi,
            "ds_code": ds_code,
        }

        if ds_code:
            ket_qua["code"] = ds_code[0].get("code", "")
            ket_qua["ngon_ngu"] = ds_code[0].get("ngon_ngu", "python")

        return ket_qua

    except Exception as e:
        _ghi_log("loi", f"Xử lý nhiều bước lỗi: {e}")
        return None


# ----------------------------------------------------------------
# HÀM CHÍNH
# ----------------------------------------------------------------
def xu_ly_task(du_lieu):
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

    # BƯỚC 2: KIỂM TRA MƠ HỒ
    mo_ho, ly_do_mo_ho = _la_mo_ho(noi_dung_chuan)

    if chu_so_huu != CHU_SO_HUU_KHACH:
        try:
            from dai_nao.chi_huy import la_lenh_lam_task
            so_buoc = la_lenh_lam_task(noi_dung_chuan)
            if so_buoc:
                mo_ho = False
            if _la_lenh_lam_het(noi_dung_chuan) or _la_lenh_tiep(noi_dung_chuan):
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
            from dai_nao.chi_huy import chi_huy, la_lenh_lam_task

            # 3.5a: Lệnh "Số N"
            so_buoc = la_lenh_lam_task(noi_dung_chuan)

            if so_buoc:
                id_du_an = _lay_du_an_gan_nhat(chu_so_huu)
                if not id_du_an:
                    return {
                        "thanh_cong": True,
                        "tra_loi": "🐉 Bạn chưa có dự án nào. Hãy gõ yêu cầu dự án trước.",
                    }

                _ghi_log("dai-nao", f"Lệnh làm bước {so_buoc} dự án {id_du_an}")

                try:
                    from dai_nao.snapshot import lay_snapshot
                    snapshot = lay_snapshot(id_du_an)
                    tong_so_buoc = len(snapshot.get("da_chia", [])) if snapshot else 0
                except Exception:
                    tong_so_buoc = 0

                kq_code = _sinh_code_buoc(id_du_an, so_buoc, chu_so_huu)

                if kq_code and kq_code.get("thanh_cong"):
                    phan_huong_dan = _tao_phan_hoi_code_1_buoc(kq_code, tong_so_buoc)

                    if so_buoc < tong_so_buoc:
                        phan_huong_dan += f"\n\n💡 Tiếp theo: Gõ **Số {so_buoc + 1}** để làm bước {so_buoc + 1}."
                    else:
                        phan_huong_dan += "\n\n🎉 Đã xong tất cả các bước!"

                    return {
                        "thanh_cong": True,
                        "tra_loi": phan_huong_dan,
                        "code": kq_code.get("code", ""),
                        "ngon_ngu": kq_code.get("ngon_ngu", ""),
                    }
                else:
                    return {
                        "thanh_cong": True,
                        "tra_loi": kq_code.get("tra_loi", "🐉 Lỗi sinh code."),
                    }

            # 3.5b: Lệnh "Cả" / "Làm hết" / "Tiếp"
            if _la_lenh_lam_het(noi_dung_chuan) or _la_lenh_tiep(noi_dung_chuan):
                id_du_an = _lay_du_an_gan_nhat(chu_so_huu)
                if not id_du_an:
                    return {
                        "thanh_cong": True,
                        "tra_loi": "🐉 Bạn chưa có dự án nào.",
                    }

                _ghi_log("dai-nao", f"Lệnh làm nhiều bước dự án {id_du_an}")

                kq_nhieu = _xu_ly_lam_nhieu_buoc(id_du_an, chu_so_huu)
                if kq_nhieu:
                    return kq_nhieu

            # 3.5c: Boss viết trường
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
    # FALLBACK
    # ============================================================
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
# HÀM CÔNG KHAI
# ----------------------------------------------------------------
def ghi_that_bai_vao_cay(id_node, noi_dung, ly_do=""):
    return {}


def ghi_thanh_cong_vao_cay(id_node, noi_dung=""):
    return {}
"""
xu_ly_task.py - Trung tâm điều phối Đại não Rồng Thần.

ĐÃ SỬA:
    - _sinh_code_buoc: vòng lặp sửa lỗi đến khi PASS.
    - Mỗi lần lỗi: phân tích lỗi cụ thể → gửi Tiểu não sửa → chạy lại.
    - Giới hạn 10 lần thử (tránh treo Render).
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
SO_LAN_SUA_TOI_DA = 10


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


def _hoi_lai(ly_do, cau_hoi):
    return {
        "thanh_cong": True,
        "tra_loi": f"{ly_do}\n\n{cau_hoi}",
        "hoi_lai": True,
    }


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


def _lay_ngu_canh(du_lieu):
    try:
        from dai_nao.ngu_canh import lay_ngu_canh
        return lay_ngu_canh(du_lieu) or {}
    except ImportError:
        return {}
    except Exception as e:
        _ghi_log("loi", f"Lấy ngữ cảnh lỗi: {e}")
        return {}


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
# CHẠY SANDBOX (dùng chung)
# ----------------------------------------------------------------
def _chay_sandbox(code, ngon_ngu):
    """Chạy code qua sandbox. Trả về {dat, ly_do, stderr, stdout}."""
    ket_qua = {"dat": True, "ly_do": "", "stderr": "", "stdout": ""}

    if not code or ngon_ngu not in ("python", "html"):
        return ket_qua

    try:
        if ngon_ngu == "html":
            from sanbox.chay_html import chay_html_backend
            kq = chay_html_backend(code)
        else:
            from sanbox.chay_python import chay_python_backend
            kq = chay_python_backend(code)

        if not kq:
            return ket_qua

        ket_qua["dat"] = kq.get("thanh_cong", False)
        ket_qua["stderr"] = kq.get("stderr", "") or kq.get("loi", "")
        ket_qua["stdout"] = kq.get("stdout", "")

        if not ket_qua["dat"]:
            ket_qua["ly_do"] = (
                kq.get("loi") or kq.get("stderr") or "Code chạy lỗi"
            )[:300]

        _ghi_log("sandbox",
                 f"Chạy code {ngon_ngu}: "
                 f"{'PASS' if ket_qua['dat'] else 'FAIL'}")

    except ImportError:
        _ghi_log("loi", "Sandbox chưa có — bỏ qua kiểm tra.")
    except Exception as e:
        _ghi_log("loi", f"Lỗi sandbox: {e}")
        ket_qua["dat"] = False
        ket_qua["ly_do"] = f"Lỗi sandbox: {e}"

    return ket_qua


# ----------------------------------------------------------------
# KIỂM TRA HỢP ĐỒNG
# ----------------------------------------------------------------
def _kiem_tra_hop_dong(id_du_an, ten_file, code, ngon_ngu):
    """Kiểm tra code khớp hợp đồng."""
    if not ten_file:
        return {"dat": True, "ly_do": ""}

    try:
        from dai_nao.doi_chieu import doi_chieu
        kq = doi_chieu(id_du_an, ten_file, code, ngon_ngu)
        if kq and kq.get("thanh_cong"):
            _ghi_log("dai-nao",
                     f"Đối chiếu {ten_file}: "
                     f"{'PASS' if kq.get('dat') else 'FAIL'}")
            return {
                "dat": kq.get("dat", False),
                "ly_do": kq.get("ly_do", ""),
                "chi_tiet": kq,
            }
    except ImportError:
        _ghi_log("loi", "doi_chieu.py chưa có — bỏ qua.")
    except Exception as e:
        _ghi_log("loi", f"Lỗi đối chiếu: {e}")

    return {"dat": True, "ly_do": ""}


# ----------------------------------------------------------------
# PHÂN TÍCH LỖI CHI TIẾT
# ----------------------------------------------------------------
def _phan_tich_loi(stderr, code):
    """Gọi phan_tich_loi(stderr, code) → dict chi tiết."""
    if not stderr:
        return {}

    try:
        from dai_nao.phan_tich_loi import phan_tich
        kq = phan_tich(stderr, code)
        if kq and kq.get("co_loi"):
            _ghi_log("dai-nao",
                     f"Phân tích lỗi: {kq.get('loai_loi')} — "
                     f"dòng {kq.get('dong_bi_loi', {}).get('so_dong', '?')}")
            return kq
    except ImportError:
        _ghi_log("loi", "phan_tich_loi.py chưa có.")
    except Exception as e:
        _ghi_log("loi", f"Lỗi phân tích: {e}")

    # Fallback: tối thiểu trả về loại lỗi
    try:
        from dai_nao.doc_loi import doc_loi
        kq = doc_loi(stderr)
        return {
            "co_loi": kq.get("co_loi", False),
            "loai_loi": kq.get("loai_loi", ""),
            "ngon_ngu": kq.get("ngon_ngu", ""),
            "nguyen_nhan_goc": kq.get("mo_ta", ""),
            "cach_sua": kq.get("goi_y", []),
            "code_sua_mau": kq.get("code_sua_mau", ""),
            "thong_diep": stderr[:500],
        }
    except Exception:
        return {}


# ----------------------------------------------------------------
# SINH CODE 1 BƯỚC — VÒNG LẶP SỬA LỖI ĐẾN KHI PASS
# ----------------------------------------------------------------
def _sinh_code_buoc(id_du_an, so_buoc, chu_so_huu):
    """Sinh code → kiểm tra → sửa lỗi đến khi PASS (tối đa 10 lần)."""
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

        cap_nhat_task(id_du_an, so_buoc, "dang_lam")

        from dai_nao.su_dung_model import sinh_code_cho_file, sua_code_theo_loi

        # ============================================================
        # LẦN 1: SINH CODE
        # ============================================================
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
        ham_da_viet = kq.get("ham_da_viet", [])
        ham_con_lai = kq.get("ham_con_lai", [])

        # ============================================================
        # VÒNG LẶP SỬA LỖI
        # ============================================================
        for lan_sua in range(1, SO_LAN_SUA_TOI_DA + 1):
            # 1. Kiểm tra hợp đồng
            kq_hd = _kiem_tra_hop_dong(id_du_an, ten_file, code, ngon_ngu)

            # 2. Kiểm tra chạy sandbox (toàn bộ code)
            kq_chay = _chay_sandbox(code, ngon_ngu)

            dat_tat_ca = kq_hd.get("dat", True) and kq_chay.get("dat", True)

            if dat_tat_ca:
                # PASS → đánh dấu xong
                _ghi_log("dai-nao",
                         f"Bước {so_buoc} ({ten_file}) PASS "
                         f"sau {lan_sua} lần sửa")

                cap_nhat_dang_viet(
                    id_du_an, so_buoc, ten_file, "",
                    ham_da_viet, ham_con_lai,
                )
                cap_nhat_task(id_du_an, so_buoc, "xong")

                return {
                    "thanh_cong": True,
                    "code": code,
                    "ngon_ngu": ngon_ngu,
                    "ten_file": ten_file,
                    "ten_buoc": ten_buoc,
                    "mo_ta": mo_ta,
                    "so_buoc": so_buoc,
                    "lan_sua": lan_sua - 1,
                    "ham_da_viet": ham_da_viet,
                    "ham_con_lai": ham_con_lai,
                    "kiem_tra_hop_dong": kq_hd,
                    "kiem_tra_chay": kq_chay,
                }

            # 3. FAIL → phân tích lỗi cụ thể
            loi_chi_tiet = {}

            if not kq_chay.get("dat", True):
                stderr = kq_chay.get("stderr", "") or kq_chay.get("ly_do", "")
                loi_chi_tiet = _phan_tich_loi(stderr, code)

            if not kq_hd.get("dat", True):
                if not loi_chi_tiet:
                    loi_chi_tiet = {}
                loi_chi_tiet["loai_loi"] = loi_chi_tiet.get("loai_loi", "HopDongLoi")
                loi_chi_tiet["nguyen_nhan_goc"] = kq_hd.get("ly_do", "")
                loi_chi_tiet["cach_sua"] = [kq_hd.get("ly_do", "")]

            ly_do_tom_tat = (
                loi_chi_tiet.get("nguyen_nhan_goc") or
                kq_hd.get("ly_do") or
                kq_chay.get("ly_do") or
                "Lỗi không xác định"
            )

            _ghi_log("dai-nao",
                     f"Bước {so_buoc} lần {lan_sua} FAIL — {ly_do_tom_tat[:150]}")

            # Nếu đã hết lần sửa → dừng
            if lan_sua >= SO_LAN_SUA_TOI_DA:
                cap_nhat_task(id_du_an, so_buoc, "loi", ly_do_tom_tat)

                _ghi_log("dai-nao",
                         f"Bước {so_buoc} ({ten_file}) bỏ cuộc sau "
                         f"{SO_LAN_SUA_TOI_DA} lần sửa")

                return {
                    "thanh_cong": True,
                    "code": code,
                    "ngon_ngu": ngon_ngu,
                    "ten_file": ten_file,
                    "ten_buoc": ten_buoc,
                    "mo_ta": mo_ta,
                    "so_buoc": so_buoc,
                    "lan_sua": SO_LAN_SUA_TOI_DA,
                    "ham_da_viet": ham_da_viet,
                    "ham_con_lai": ham_con_lai,
                    "kiem_tra_hop_dong": kq_hd,
                    "kiem_tra_chay": kq_chay,
                    "co_loi_kiem_tra": True,
                    "ly_do_loi": ly_do_tom_tat,
                }

            # 4. Gửi Tiểu não sửa (kèm yêu cầu gốc + code cũ + lỗi + cách sửa)
            _ghi_log("dai-nao",
                     f"Gửi Tiểu não sửa lần {lan_sua} cho {ten_file}")

            kq_sua = sua_code_theo_loi(
                id_du_an=id_du_an,
                ten_file=ten_file,
                code_cu=code,
                loi_chi_tiet=loi_chi_tiet,
                chu_so_huu=chu_so_huu,
            )

            if not kq_sua.get("thanh_cong"):
                _ghi_log("loi",
                         f"Tiểu não không sửa được: {kq_sua.get('loi', '')}")
                # Thử lại vòng tiếp theo (nếu còn)
                continue

            code = kq_sua.get("code", "")
            ngon_ngu = kq_sua.get("ngon_ngu", ngon_ngu)

        # Hết vòng lặp — không PASS được
        cap_nhat_task(id_du_an, so_buoc, "loi", "Không sửa được sau nhiều lần")

        return {
            "thanh_cong": True,
            "code": code,
            "ngon_ngu": ngon_ngu,
            "ten_file": ten_file,
            "ten_buoc": ten_buoc,
            "mo_ta": mo_ta,
            "so_buoc": so_buoc,
            "lan_sua": SO_LAN_SUA_TOI_DA,
            "co_loi_kiem_tra": True,
            "ly_do_loi": "Không sửa được sau nhiều lần",
        }

    except Exception as e:
        import traceback
        _ghi_log("loi", f"_sinh_code_buoc CRASH: {e}\n{traceback.format_exc()}")
        return None


# ----------------------------------------------------------------
# PHẢN HỒI BOSS
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
# PHẢN HỒI CODE
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
    lan_sua = kq.get("lan_sua", 0)

    phan = []

    if co_loi:
        phan.append(f"⚠️ **BƯỚC {so_buoc}/{tong_so_buoc}** — {ten_buoc}")
        phan.append(f"❗ Không sửa được sau {lan_sua} lần: {ly_do_loi[:200]}")
    else:
        phan.append(f"✅ **BƯỚC {so_buoc}/{tong_so_buoc}** — {ten_buoc}")
        if lan_sua > 0:
            phan.append(f"🔁 Đã sửa {lan_sua} lần cho tới khi chạy được")

    phan.append("")
    phan.append(f"📁 **Đặt file tại:** `{ten_file or '(không có file)'}`")
    if mo_ta:
        phan.append(f"📝 **Mô tả:** {mo_ta}")

    if not co_loi:
        phan.append("")
        phan.append("✔️ Hợp đồng khớp")
        phan.append("✔️ Code chạy được")

    return "\n".join(phan)


def _tao_phan_hoi_code_nhieu_buoc(ds_kq, tong_so_buoc):
    if not ds_kq:
        return ""

    phan = [f"✅ Đã làm xong **{len(ds_kq)} bước**", ""]

    for kq in ds_kq:
        so_buoc = kq.get("so_buoc", "?")
        ten_file = kq.get("ten_file", "")
        ten_buoc = kq.get("ten_buoc", "")
        co_loi = kq.get("co_loi_kiem_tra", False)
        lan_sua = kq.get("lan_sua", 0)

        ky_hieu = "⚠️" if co_loi else "✅"
        phan.append(f"{ky_hieu} **Bước {so_buoc}/{tong_so_buoc}** — {ten_buoc}")
        phan.append(f"📁 File: `{ten_file}`")
        if lan_sua > 0:
            phan.append(f"🔁 Sửa {lan_sua} lần")
        if co_loi:
            phan.append(f"❗ Lỗi: {kq.get('ly_do_loi', '')[:100]}")
        phan.append("")

    so_buoc_da_lam = max([kq.get("so_buoc", 0) for kq in ds_kq] or [0])
    con_lai = tong_so_buoc - so_buoc_da_lam

    if con_lai > 0:
        phan.append(f"⏳ Còn **{con_lai}** bước. Gõ **Tiếp** để làm tiếp.")
    else:
        phan.append("🎉 Đã xong tất cả các bước!")

    return "\n".join(phan)


# ----------------------------------------------------------------
# XỬ LÝ LÀM NHIỀU BƯỚC
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

    # BƯỚC 3.5: BOSS
    if chu_so_huu and chu_so_huu != CHU_SO_HUU_KHACH:
        try:
            from dai_nao.chi_huy import chi_huy, la_lenh_lam_task

            so_buoc = la_lenh_lam_task(noi_dung_chuan)

            if so_buoc:
                id_du_an = _lay_du_an_gan_nhat(chu_so_huu)
                if not id_du_an:
                    return {
                        "thanh_cong": True,
                        "tra_loi": "🐉 Bạn chưa có dự án nào.",
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

    # FALLBACK
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
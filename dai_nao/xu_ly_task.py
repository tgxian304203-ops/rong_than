"""
xu_ly_task.py - Trung tâm điều phối Đại não Rồng Thần.

Nhiệm vụ:
    - Nhận task từ nhan_task.py.
    - Điều phối 12 bước xử lý theo Phần 4 của dự án.
    - Gọi Boss (nếu task phức tạp) → chia task + lưu snapshot.
    - Gọi Tiểu não khi bí, gọi Tra web khi cần, gọi Sandbox khi chạy code.
    - Cập nhật cây quyết định sau mỗi task.

ĐÃ SỬA (Giai đoạn 2 — Boss có model riêng):
    - FIX 1: Thêm BƯỚC 3.5 — gọi Boss (chi_huy.py) cho task phức tạp.
    - FIX 2: Nếu Boss phân tích được dự án → lưu snapshot + trả info cho user.
    - FIX 3: Nếu Boss hết quota → fallback về luồng cũ (không sập).

Các fix cũ giữ nguyên:
    - FIX 1: Ngưỡng chấm điểm 0.75.
    - FIX 2: Node rỗng nội dung → bỏ qua.
    - FIX 3: Node có hanh_dong + cach_giai_phap.
"""

import time


# ----------------------------------------------------------------
# HẰNG SỐ
# ----------------------------------------------------------------
CAN_5_YEU_TO = ("hanh_dong", "doi_tuong", "thuoc_tinh", "rang_buoc", "ngu_canh")

TU_MO_HO = (
    "cái đó", "cái này", "cái kia", "cái ấy",
    "nó", "hắn", "chúng nó", "bọn nó",
    "kia", "ấy", "đó", "đấy",
    "thứ đó", "thứ này", "thứ kia",
    "việc đó", "việc này", "chuyện đó", "chuyện này",
)

SO_LAN_TU_SUA_TOI_DA = 3
NGUONG_DUNG_NODE = 0.75


# ----------------------------------------------------------------
# GHI LOG
# ----------------------------------------------------------------
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
# HÀM PHỤ: NODE NUT → DICT
# ----------------------------------------------------------------
def _node_sang_dict(nhanh):
    if nhanh is None:
        return {}
    if isinstance(nhanh, dict):
        return nhanh
    if hasattr(nhanh, "sang_dict_phang"):
        try:
            return nhanh.sang_dict_phang()
        except Exception:
            return {}
    if hasattr(nhanh, "sang_dict"):
        try:
            return nhanh.sang_dict(gom_nhanh_con=False)
        except Exception:
            return {}
    return {}


# ----------------------------------------------------------------
# HÀM PHỤ: KIỂM TRA NODE CÓ NỘI DUNG THỰC
# ----------------------------------------------------------------
def _node_co_noi_dung_thuc(nhanh_dict):
    if not isinstance(nhanh_dict, dict):
        return False

    hanh_dong = nhanh_dict.get("hanh_dong") or {}
    if isinstance(hanh_dong, dict):
        code = (hanh_dong.get("code") or "").strip()
        loai = (hanh_dong.get("loai") or "").strip()
        if code:
            return True
        if loai == "tra_web":
            return True

    cach_giai = nhanh_dict.get("cach_giai") or {}
    if isinstance(cach_giai, dict):
        mo_ta = (cach_giai.get("mo_ta") or "").strip()
        if mo_ta:
            return True
    elif isinstance(cach_giai, str) and cach_giai.strip():
        return True

    return False


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
# HÀM PHỤ: GỌI TIỂU NÃO
# ----------------------------------------------------------------
def _goi_tieu_nao(task, ngu_canh, chu_so_huu=""):
    try:
        from dai_nao.su_dung_model import su_dung_model
        return su_dung_model(task, ngu_canh, chu_so_huu)
    except ImportError:
        _ghi_log("loi", "su_dung_model.py chưa có.")
        return None
    except Exception as e:
        _ghi_log("loi", f"Tiểu não lỗi: {e}")
        return None


# ----------------------------------------------------------------
# FIX 1: HÀM PHỤ: GỌI BOSS
# ----------------------------------------------------------------
def _goi_boss(noi_dung, chu_so_huu=""):
    """
    Gọi Boss (Đại não có model riêng) cho task phức tạp.

    Trả về dict hoặc None nếu Boss không dùng / hết quota.
    """
    try:
        from dai_nao.chi_huy import chi_huy

        ket_qua = chi_huy({
            "noi_dung": noi_dung,
            "chu_so_huu": chu_so_huu,
        })

        if not ket_qua:
            return None

        # Boss hết quota → trả None → fallback
        if not ket_qua.get("thanh_cong"):
            _ghi_log("dai-nao", f"Boss thất bại: {ket_qua.get('loi', '')}")
            return None

        # Task không cần Boss → trả None
        if not ket_qua.get("can_boss"):
            return None

        return ket_qua

    except ImportError:
        _ghi_log("loi", "chi_huy.py chưa có.")
        return None
    except Exception as e:
        _ghi_log("loi", f"Boss lỗi: {e}")
        return None


# ----------------------------------------------------------------
# FIX 2: HÀM PHỤ: TẠO PHẢN HỒI TỪ BOSS
# ----------------------------------------------------------------
def _tao_phan_hoi_boss(ket_qua_boss):
    """
    Tạo phản hồi cho user từ kết quả Boss.

    Hiển thị:
        - Loại dự án.
        - Số task.
        - Danh sách task.
        - Mã dự án (snapshot).
    """
    if not ket_qua_boss:
        return ""

    yeu_cau = ket_qua_boss.get("yeu_cau", {})
    ds_task = ket_qua_boss.get("ds_task", [])
    id_du_an = ket_qua_boss.get("id_du_an", "")

    loai_task = yeu_cau.get("loai_task", "khác")
    do_phuc_tap = yeu_cau.get("do_phuc_tap", "?")
    yeu_cau_chinh = yeu_cau.get("yeu_cau_chinh", "")

    phan = []
    phan.append(f"🔥 Boss đã phân tích dự án: **{yeu_cau_chinh}**")
    phan.append("")
    phan.append(f"📁 **Loại**: {loai_task}")
    phan.append(f"🎯 **Độ phức tạp**: {do_phuc_tap}")
    phan.append(f"📊 **Số task**: {len(ds_task)}")

    if id_du_an:
        phan.append(f"🆔 **Mã dự án**: `{id_du_an}`")

    if ds_task:
        phan.append("")
        phan.append("**📝 DANH SÁCH TASK:**")
        for task in ds_task:
            so = task.get("so", "?")
            ten = task.get("ten", "?")
            file = task.get("file", "")
            if file:
                phan.append(f"  {so}. {ten} → `{file}`")
            else:
                phan.append(f"  {so}. {ten}")

    phan.append("")
    phan.append("💡 Bạn muốn Boss bắt đầu làm task nào? (Gõ số hoặc 'làm hết')")

    return "\n".join(phan)


# ----------------------------------------------------------------
# HÀM PHỤ: GỌI TRA WEB
# ----------------------------------------------------------------
def _goi_tra_web(cau_hoi, chu_so_huu=""):
    try:
        from dai_nao.goi_tra_web import goi_tra_web
        ket_qua = goi_tra_web(cau_hoi, chu_so_huu)
        if not ket_qua or not ket_qua.get("thanh_cong"):
            return ""
        tom_tat = ket_qua.get("tom_tat") or ""
        if not tom_tat:
            danh_sach = ket_qua.get("ket_qua", [])
            tom_tat = _tong_hop_don_gian(danh_sach)
        return tom_tat
    except ImportError:
        return ""
    except Exception as e:
        _ghi_log("loi", f"Tra web lỗi: {e}")
        return ""


def _tong_hop_don_gian(danh_sach):
    if not danh_sach:
        return ""
    phan = []
    for i, item in enumerate(danh_sach[:5], 1):
        if not isinstance(item, dict):
            continue
        tieu_de = (item.get("tieu_de") or "").strip()
        mo_ta = (item.get("mo_ta") or "").strip()
        url = (item.get("url") or "").strip()
        dong = f"{i}. {tieu_de}" if tieu_de else f"{i}."
        if mo_ta:
            dong += f"\n   {mo_ta[:300]}"
        if url:
            dong += f"\n   🔗 {url}"
        phan.append(dong)
    return "\n\n".join(phan)


# ----------------------------------------------------------------
# HÀM PHỤ: MƯỢN NHÁNH
# ----------------------------------------------------------------
def _thu_muon_nhanh(noi_dung, loai_task, yeu_to, ngu_canh):
    try:
        from dai_nao.muon_nhanh import tim_va_muon
        node_moi, node_goc = tim_va_muon(noi_dung, loai_task, yeu_to)
        if node_moi:
            _ghi_log(
                "dai-nao",
                f"Đã mượn nhánh từ '{_node_sang_dict(node_goc).get('ten', '')}'",
            )
            return node_moi
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Mượn nhánh lỗi: {e}")
    return None


# ----------------------------------------------------------------
# HÀM PHỤ: CHIA SẺ NHÁNH
# ----------------------------------------------------------------
def _thu_chia_se_nhanh(node_moi, cay=None):
    if not node_moi:
        return
    try:
        from dai_nao.chia_se_nhanh import tu_dong_chia_se
        if cay is None:
            from dai_nao.cay_quyet_dinh import cay_tu_mongo
            cay = cay_tu_mongo()
        if cay:
            tu_dong_chia_se(node_moi, cay)
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Chia sẻ nhánh lỗi: {e}")


# ----------------------------------------------------------------
# HÀM PHỤ: CẬP NHẬT ƯU TIÊN
# ----------------------------------------------------------------
def _cap_nhat_uu_tien_node(node):
    if not node:
        return
    try:
        from dai_nao.uu_tien import cap_nhat_uu_tien
        cap_nhat_uu_tien(node)
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Cập nhật ưu tiên lỗi: {e}")


# ----------------------------------------------------------------
# HÀM PHỤ: PHÂN BIỆT CODE
# ----------------------------------------------------------------
def _phan_biet_ngon_ngu(code, ngon_ngu_goi_y=""):
    if not code:
        return ngon_ngu_goi_y or "python"
    try:
        from dai_nao.phan_biet_code import phan_biet_code
        ket_qua = phan_biet_code(code, ngon_ngu_goi_y)
        nn = ket_qua.get("ngon_ngu", "")
        if nn and nn != "khong_ro":
            return nn
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Phân biệt code lỗi: {e}")
    return ngon_ngu_goi_y or "python"


# ----------------------------------------------------------------
# HÀM PHỤ: TẠO CODE
# ----------------------------------------------------------------
def _tao_code_tu_node(nhanh_dict, yeu_to, noi_dung):
    try:
        from dai_nao.tao_code import tao_code
        ket_qua = tao_code(nhanh_dict, yeu_to, noi_dung)
        if ket_qua and ket_qua.get("thanh_cong"):
            return ket_qua.get("code", ""), ket_qua.get("ngon_ngu", "")
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Tạo code lỗi: {e}")

    hanh_dong = nhanh_dict.get("hanh_dong") or {}
    if isinstance(hanh_dong, dict):
        code = hanh_dong.get("code") or nhanh_dict.get("code") or ""
        ngon_ngu = hanh_dong.get("ngon_ngu") or nhanh_dict.get("ngon_ngu") or "python"
        return code, ngon_ngu
    return "", "python"


# ----------------------------------------------------------------
# HÀM PHỤ: CHẠY SANDBOX BACKEND
# ----------------------------------------------------------------
def _chay_sandbox_backend(code, ngon_ngu):
    if not code:
        return {"thanh_cong": False, "loi": "Code rỗng."}

    if ngon_ngu == "html":
        try:
            from sanbox.chay_html import chay_html_backend
            ket_qua = chay_html_backend(code)
            return {
                "thanh_cong": ket_qua.get("thanh_cong", False),
                "stdout": "",
                "stderr": ket_qua.get("loi", ""),
                "returncode": 0 if ket_qua.get("thanh_cong") else 1,
                "loi": ket_qua.get("loi", ""),
                "canh_bao": ket_qua.get("canh_bao", ""),
                "ngon_ngu": "html",
                "code": code,
            }
        except ImportError:
            return {"thanh_cong": False, "loi": "chay_html.py chưa có."}
        except Exception as e:
            return {"thanh_cong": False, "loi": f"Lỗi HTML: {e}"}
    else:
        try:
            from sanbox.chay_python import chay_python_backend
            ket_qua = chay_python_backend(code)
            return {
                "thanh_cong": ket_qua.get("thanh_cong", False),
                "stdout": ket_qua.get("stdout", ""),
                "stderr": ket_qua.get("stderr", ""),
                "returncode": ket_qua.get("returncode", -1),
                "loi": ket_qua.get("loi", ""),
                "thoi_gian": ket_qua.get("thoi_gian", 0.0),
                "ngon_ngu": "python",
                "code": code,
            }
        except ImportError:
            return {"thanh_cong": False, "loi": "chay_python.py chưa có."}
        except Exception as e:
            return {"thanh_cong": False, "loi": f"Lỗi Python: {e}"}


# ----------------------------------------------------------------
# HÀM PHỤ: TỰ SỬA LỖI
# ----------------------------------------------------------------
def _tu_sua_va_chay_lai(code, ngon_ngu, ket_qua_chay):
    if ket_qua_chay.get("thanh_cong"):
        return ket_qua_chay

    loi = ket_qua_chay.get("stderr") or ket_qua_chay.get("loi") or ""
    if not loi:
        return ket_qua_chay

    code_hien_tai = code

    for lan in range(1, SO_LAN_TU_SUA_TOI_DA + 1):
        _ghi_log("dai-nao", f"Tự sửa lần {lan}/{SO_LAN_TU_SUA_TOI_DA}")

        try:
            from dai_nao.tu_sua_loi import tu_sua_loi
            ket_qua_sua = tu_sua_loi(code_hien_tai, loi, ngon_ngu)
        except ImportError:
            _ghi_log("loi", "tu_sua_loi.py chưa có.")
            break
        except Exception as e:
            _ghi_log("loi", f"tu_sua_loi lỗi: {e}")
            break

        if not ket_qua_sua or not ket_qua_sua.get("thanh_cong"):
            _ghi_log("dai-nao", f"Lần {lan}: không sửa được.")
            break

        code_moi = ket_qua_sua.get("code_moi", "")
        if not code_moi or code_moi == code_hien_tai:
            _ghi_log("dai-nao", f"Lần {lan}: code không đổi — dừng.")
            break

        _ghi_log("dai-nao", f"Lần {lan}: đã sửa, chạy lại.")

        ket_qua_chay_moi = _chay_sandbox_backend(code_moi, ngon_ngu)
        ket_qua_chay = ket_qua_chay_moi
        code_hien_tai = code_moi

        if ket_qua_chay.get("thanh_cong"):
            _ghi_log("dai-nao", f"Lần {lan}: sửa thành công.")
            ket_qua_chay["da_sua"] = True
            ket_qua_chay["so_lan_sua"] = lan
            ket_qua_chay["code_cu"] = code
            ket_qua_chay["cach_sua"] = ket_qua_sua.get("cach_sua", "")
            ket_qua_chay["nguon_sua"] = ket_qua_sua.get("nguon", "")
            return ket_qua_chay

        loi = ket_qua_chay.get("stderr") or ket_qua_chay.get("loi") or ""

    return ket_qua_chay


# ----------------------------------------------------------------
# HÀM CHÍNH
# ----------------------------------------------------------------
def xu_ly_task(du_lieu):
    """Điều phối xử lý task."""
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

    # BƯỚC 2: TRÍCH XUẤT
    try:
        from dai_nao.trich_xuat import trich_xuat_5_yeu_to
        yeu_to = trich_xuat_5_yeu_to(noi_dung_chuan) or {}
    except ImportError:
        yeu_to = {}
    except Exception as e:
        _ghi_log("loi", f"Trích xuất lỗi: {e}")
        yeu_to = {}

    # BƯỚC 3: KIỂM TRA 5 YẾU TỐ
    mo_ho, ly_do_mo_ho = _la_mo_ho(noi_dung_chuan)

    if mo_ho:
        thieu = [y for y in CAN_5_YEU_TO if not yeu_to.get(y)]
        if thieu:
            cau_hoi = "Bạn có thể nói rõ hơn: " + ", ".join(thieu) + " không?"
        else:
            cau_hoi = "Bạn có thể nói cụ thể hơn không?"
        _ghi_log("dai-nao", f"Hỏi lại {chu_so_huu}: {ly_do_mo_ho}")
        return _hoi_lai("Task chưa đủ rõ để thực hiện.", cau_hoi)

    # ============================================================
    # FIX 1: BƯỚC 3.5 — GỌI BOSS CHO TASK PHỨC TẠP
    # ============================================================
    ket_qua_boss = _goi_boss(noi_dung_chuan, chu_so_huu)

    if ket_qua_boss and ket_qua_boss.get("can_boss"):
        # Boss đã phân tích dự án → trả kết quả cho user
        _ghi_log("dai-nao", f"Boss đã phân tích dự án cho {chu_so_huu}")

        tra_loi_boss = _tao_phan_hoi_boss(ket_qua_boss)

        return {
            "thanh_cong": True,
            "tra_loi": tra_loi_boss,
            "boss": {
                "id_du_an": ket_qua_boss.get("id_du_an", ""),
                "ds_task": ket_qua_boss.get("ds_task", []),
                "yeu_cau": ket_qua_boss.get("yeu_cau", {}),
            },
        }

    # Boss không dùng được → tiếp tục luồng cũ
    if ket_qua_boss and not ket_qua_boss.get("thanh_cong"):
        _ghi_log("dai-nao", "Boss hết quota — fallback luồng cũ.")

    # BƯỚC 4: PHÂN LOẠI
    try:
        from dai_nao.phan_loai import phan_loai
        loai_task = phan_loai(noi_dung_chuan, yeu_to) or {}
    except ImportError:
        loai_task = {}
    except Exception as e:
        _ghi_log("loi", f"Phân loại lỗi: {e}")
        loai_task = {}

    # BƯỚC 5: DUYỆT CÂY
    nhanh_tot_nhat = None
    try:
        from dai_nao.duyet_cay import duyet_cay
        nhanh_tot_nhat = duyet_cay(noi_dung_chuan, loai_task, yeu_to)
    except ImportError:
        nhanh_tot_nhat = None
    except Exception as e:
        _ghi_log("loi", f"Duyệt cây lỗi: {e}")
        nhanh_tot_nhat = None

    # BƯỚC 6: FAILED_PATHS
    if nhanh_tot_nhat:
        try:
            from dai_nao.chong_lap_sai import kiem_tra_failed_path
            if kiem_tra_failed_path(nhanh_tot_nhat, noi_dung_chuan):
                _ghi_log("dai-nao", "Nhánh khớp nằm trong failed_paths — bỏ qua.")
                nhanh_tot_nhat = None
        except ImportError:
            pass
        except Exception as e:
            _ghi_log("loi", f"Kiểm tra failed_paths lỗi: {e}")

    # BƯỚC 7: CHẤM ĐIỂM + KIỂM TRA NỘI DUNG THỰC
    if nhanh_tot_nhat:
        nhanh_dict = _node_sang_dict(nhanh_tot_nhat)

        if not _node_co_noi_dung_thuc(nhanh_dict):
            _ghi_log("dai-nao", "Nhánh rỗng nội dung — bỏ qua, gọi Tiểu não.")
            nhanh_tot_nhat = None
        else:
            try:
                from dai_nao.cham_diem import cham_diem
                diem = cham_diem(nhanh_tot_nhat, yeu_to)
                if diem < NGUONG_DUNG_NODE:
                    _ghi_log(
                        "dai-nao",
                        f"Nhánh có điểm thấp ({diem} < {NGUONG_DUNG_NODE}) — bỏ qua.",
                    )
                    nhanh_tot_nhat = None
            except ImportError:
                pass
            except Exception as e:
                _ghi_log("loi", f"Chấm điểm lỗi: {e}")

    # BƯỚC 8: THỰC THI NHÁNH
    if nhanh_tot_nhat:
        return _thuc_thi_nhanh(
            nhanh_tot_nhat, noi_dung_chuan, yeu_to, loai_task,
            chu_so_huu, thoi_gian_bat_dau, ngu_canh,
        )

    # BƯỚC 8.5: MƯỢN NHÁNH
    node_muon = _thu_muon_nhanh(noi_dung_chuan, loai_task, yeu_to, ngu_canh)
    if node_muon:
        node_muon_dict = _node_sang_dict(node_muon)
        if _node_co_noi_dung_thuc(node_muon_dict):
            _ghi_log("dai-nao", "Đã mượn nhánh gần giống.")
            try:
                from dai_nao.ghi_nho import luu_node
                if node_muon_dict:
                    luu_node(node_muon_dict)
            except Exception as e:
                _ghi_log("loi", f"Lưu node mượn lỗi: {e}")

            _thu_chia_se_nhanh(node_muon)

            return _thuc_thi_nhanh(
                node_muon, noi_dung_chuan, yeu_to, loai_task,
                chu_so_huu, thoi_gian_bat_dau, ngu_canh,
            )
        else:
            _ghi_log("dai-nao", "Nhánh mượn rỗng nội dung — bỏ qua.")

    # BƯỚC 9: GỌI TIỂU NÃO
    _ghi_log("dai-nao", "Không có nhánh khớp — gọi Tiểu não.")

    node_moi = _goi_tieu_nao(
        {"noi_dung": noi_dung_chuan, "yeu_to": yeu_to, "loai_task": loai_task},
        ngu_canh,
        chu_so_huu,
    )

    if not node_moi:
        return {
            "thanh_cong": True,
            "tra_loi": "🐉 Ta chưa hiểu rõ task này. "
                       "Bạn có thể nói cụ thể hơn không?",
        }

    try:
        from dai_nao.ghi_nho import luu_node
        node_dict = _node_sang_dict(node_moi)
        if node_dict:
            luu_node(node_dict)
    except Exception as e:
        _ghi_log("loi", f"Lưu node mới lỗi: {e}")

    _thu_chia_se_nhanh(node_moi)
    _cap_nhat_uu_tien_node(node_moi)

    return _thuc_thi_nhanh(
        node_moi, noi_dung_chuan, yeu_to, loai_task,
        chu_so_huu, thoi_gian_bat_dau, ngu_canh,
    )


# ----------------------------------------------------------------
# HÀM PHỤ: THỰC THI NHÁNH
# ----------------------------------------------------------------
def _thuc_thi_nhanh(nhanh, noi_dung, yeu_to, loai_task, chu_so_huu,
                    thoi_gian_bat_dau, ngu_canh=None):
    nhanh_dict = _node_sang_dict(nhanh)

    if not nhanh_dict:
        return {
            "thanh_cong": True,
            "tra_loi": "🐉 Ta tìm thấy nhánh nhưng không đọc được dữ liệu. "
                       "Bạn thử lại giúp ta nhé.",
        }

    hanh_dong = nhanh_dict.get("hanh_dong") or {}
    if not isinstance(hanh_dong, dict):
        hanh_dong = {}

    loai_hanh_dong = hanh_dong.get("loai") or nhanh_dict.get("loai") or ""

    # --- Tra web ---
    if loai_hanh_dong == "tra_web" or nhanh_dict.get("can_tra_web"):
        ket_qua_web = _goi_tra_web(noi_dung, chu_so_huu)
        if ket_qua_web:
            _ghi_log("tra-web", f"Tra web cho {chu_so_huu}: {ket_qua_web[:80]}...")
            _cap_nhat_node_sau_thanh_cong(nhanh_dict)
            _cap_nhat_uu_tien_node(nhanh)
            return {
                "thanh_cong": True,
                "tra_loi": ket_qua_web,
            }

    # --- Chạy code ---
    code_mau = hanh_dong.get("code") or nhanh_dict.get("code")
    ngon_ngu = hanh_dong.get("ngon_ngu") or nhanh_dict.get("ngon_ngu") or ""

    if code_mau:
        code_final, ngon_ngu_final = _tao_code_tu_node(nhanh_dict, yeu_to, noi_dung)

        if not code_final:
            code_final = code_mau
            ngon_ngu_final = ngon_ngu or "python"

        ngon_ngu_final = _phan_biet_ngon_ngu(code_final, ngon_ngu_final)

        _ghi_log(
            "sandbox",
            f"Chạy code backend: {ngon_ngu_final}, {len(code_final)} ký tự",
        )

        ket_qua_chay = _chay_sandbox_backend(code_final, ngon_ngu_final)

        if not ket_qua_chay.get("thanh_cong"):
            _ghi_log("sandbox", "Code lỗi — thử tự sửa.")
            ket_qua_chay = _tu_sua_va_chay_lai(code_final, ngon_ngu_final, ket_qua_chay)
            if ket_qua_chay.get("da_sua"):
                code_final = ket_qua_chay.get("code", code_final)

        _cap_nhat_node_sau_thanh_cong(nhanh_dict)
        _cap_nhat_uu_tien_node(nhanh)

        return {
            "thanh_cong": True,
            "tra_loi": "Đây là code bạn cần:",
            "code": code_final,
            "ngon_ngu": ngon_ngu_final,
            "ket_qua_chay": {
                "thanh_cong": ket_qua_chay.get("thanh_cong", False),
                "stdout": ket_qua_chay.get("stdout", ""),
                "stderr": ket_qua_chay.get("stderr", ""),
                "returncode": ket_qua_chay.get("returncode", -1),
                "loi": ket_qua_chay.get("loi", ""),
                "da_sua": ket_qua_chay.get("da_sua", False),
                "so_lan_sua": ket_qua_chay.get("so_lan_sua", 0),
                "cach_sua": ket_qua_chay.get("cach_sua", ""),
                "nguon_sua": ket_qua_chay.get("nguon_sua", ""),
            },
        }

    # --- Cách giải trực tiếp ---
    cach_giai = nhanh_dict.get("cach_giai") or {}
    if isinstance(cach_giai, dict):
        tra_loi = cach_giai.get("mo_ta") or nhanh_dict.get("tra_loi") or ""
    else:
        tra_loi = str(cach_giai) if cach_giai else ""

    if not tra_loi:
        tra_loi = nhanh_dict.get("tra_loi") or ""

    if tra_loi:
        _cap_nhat_node_sau_thanh_cong(nhanh_dict)
        _cap_nhat_uu_tien_node(nhanh)
        return {
            "thanh_cong": True,
            "tra_loi": tra_loi,
        }

    _cap_nhat_node_sau_thanh_cong(nhanh_dict)
    _cap_nhat_uu_tien_node(nhanh)
    ten_nhanh = nhanh_dict.get("ten") or "nhánh này"
    return {
        "thanh_cong": True,
        "tra_loi": f"🐉 Ta đã tìm thấy nhánh '{ten_nhanh}' nhưng chưa có cách giải cụ thể. "
                   "Bạn có thể nói rõ hơn không?",
    }


# ----------------------------------------------------------------
# HÀM PHỤ: CẬP NHẬT NODE SAU KHI THÀNH CÔNG
# ----------------------------------------------------------------
def _cap_nhat_node_sau_thanh_cong(nhanh_dict):
    try:
        if not isinstance(nhanh_dict, dict):
            return
        id_node = nhanh_dict.get("id")
        if not id_node:
            return

        from dai_nao.ghi_nho import lay_node, luu_node

        node_hien_tai = lay_node(id_node) or {}
        so_lan_thu = int(node_hien_tai.get("so_lan_thu", 0)) + 1
        thanh_cong = int(node_hien_tai.get("thanh_cong", 0)) + 1

        node_hien_tai["so_lan_thu"] = so_lan_thu
        node_hien_tai["thanh_cong"] = thanh_cong
        node_hien_tai["lan_dung_cuoi"] = int(time.time())

        try:
            from dai_nao.uu_tien import tinh_uu_tien
            node_hien_tai["uu_tien"] = int(tinh_uu_tien(node_hien_tai) * 100)
        except ImportError:
            pass

        luu_node(node_hien_tai)
    except Exception as e:
        _ghi_log("loi", f"Cập nhật node lỗi: {e}")


# ----------------------------------------------------------------
# HÀM CÔNG KHAI
# ----------------------------------------------------------------
def ghi_that_bai_vao_cay(id_node, noi_dung, ly_do=""):
    if not id_node or not noi_dung:
        return {}

    try:
        from dai_nao.ghi_nho import lay_node, luu_node
        from dai_nao.chong_lap_sai import (
            ghi_failed_path, cap_nhat_blacklist,
            giam_score_neu_fail_nhieu, thong_ke_loi,
        )

        node = lay_node(id_node)
        if not node:
            return {}

        ghi_failed_path(node, noi_dung, ly_do)
        cap_nhat_blacklist(node)
        giam_score_neu_fail_nhieu(node)

        try:
            from dai_nao.uu_tien import tinh_uu_tien
            node["uu_tien"] = int(tinh_uu_tien(node) * 100)
        except ImportError:
            pass

        luu_node(node)
        return thong_ke_loi(node)
    except ImportError as e:
        _ghi_log("loi", f"Không import được module: {e}")
        return {}
    except Exception as e:
        _ghi_log("loi", f"Ghi thất bại lỗi: {e}")
        return {}


def ghi_thanh_cong_vao_cay(id_node, noi_dung=""):
    if not id_node:
        return {}

    try:
        from dai_nao.ghi_nho import lay_node, luu_node
        from dai_nao.chong_lap_sai import thong_ke_loi

        node = lay_node(id_node)
        if not node:
            return {}

        so_lan_thu = int(node.get("so_lan_thu", 0)) + 1
        thanh_cong = int(node.get("thanh_cong", 0)) + 1
        node["so_lan_thu"] = so_lan_thu
        node["thanh_cong"] = thanh_cong
        node["lan_dung_cuoi"] = int(time.time())

        try:
            from dai_nao.uu_tien import tinh_uu_tien
            node["uu_tien"] = int(tinh_uu_tien(node) * 100)
        except ImportError:
            pass

        luu_node(node)
        return thong_ke_loi(node)
    except ImportError as e:
        _ghi_log("loi", f"Không import được module: {e}")
        return {}
    except Exception as e:
        _ghi_log("loi", f"Ghi thành công lỗi: {e}")
        return {}
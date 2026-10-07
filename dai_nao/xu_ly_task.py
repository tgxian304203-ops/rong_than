"""
xu_ly_task.py - Trung tâm điều phối Đại não Rồng Thần.

Nhiệm vụ:
    - Nhận task từ nhan_task.py.
    - Điều phối 12 bước xử lý theo Phần 4 của dự án.
    - Gọi Tiểu não khi bí, gọi Tra web khi cần, gọi Sandbox khi chạy code.
    - Cập nhật cây quyết định sau mỗi task.

ĐÃ SỬA (Nhóm 1 + Nhóm 2):
    L1: Bước 3 chỉ hỏi lại khi THỰC SỰ mơ hồ.
    L2a: _thuc_thi_nhanh chuyển Nut → dict.
    L18: Không chạy sandbox backend.
    L24: _goi_tra_web không slice dict.
    L34: Thêm _ghi_that_bai_vao_cay (cho route /api/sandbox/ket-qua).
    L35: Gọi tu_dong_chia_se sau khi sinh node mới.
    L36: Gọi tim_va_muon trước khi gọi Tiểu não.
    L38: Gọi cap_nhat_uu_tien sau khi node thay đổi.
    L39: Gọi lay_ngu_canh ở BƯỚC 1 (đầu vào).
    L42: Gọi tao_code thay vì lấy code thô.
    L43: Gọi phan_biet_code để nhận diện ngôn ngữ.
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
# HÀM PHỤ: LẤY NGỮ CẢNH (L39)
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
def _goi_tieu_nao(task, ngu_canh):
    try:
        from dai_nao.su_dung_model import su_dung_model
        return su_dung_model(task, ngu_canh)
    except ImportError:
        _ghi_log("loi", "su_dung_model.py chưa có.")
        return None
    except Exception as e:
        _ghi_log("loi", f"Tiểu não lỗi: {e}")
        return None


# ----------------------------------------------------------------
# HÀM PHỤ: GỌI TRA WEB (L24)
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
# HÀM PHỤ: MƯỢN NHÁNH (L36)
# ----------------------------------------------------------------
def _thu_muon_nhanh(noi_dung, loai_task, yeu_to, ngu_canh):
    """
    Thử mượn nhánh gần giống. Trả về node mới hoặc None.
    """
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
# HÀM PHỤ: CHIA SẺ NHÁNH (L35)
# ----------------------------------------------------------------
def _thu_chia_se_nhanh(node_moi, cay=None):
    """Tự động chia sẻ nhánh cho node mới."""
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
# HÀM PHỤ: CẬP NHẬT ƯU TIÊN (L38)
# ----------------------------------------------------------------
def _cap_nhat_uu_tien_node(node):
    """Cập nhật uu_tien cho node."""
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
# HÀM PHỤ: PHÂN BIỆT CODE (L43)
# ----------------------------------------------------------------
def _phan_biet_ngon_ngu(code, ngon_ngu_goi_y=""):
    """Nhận diện ngôn ngữ của code."""
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
# HÀM PHỤ: TẠO CODE (L42)
# ----------------------------------------------------------------
def _tao_code_tu_node(nhanh_dict, yeu_to, noi_dung):
    """
    Tạo code từ node. Nếu node có placeholder {{x}} → thay bằng giá trị.
    """
    try:
        from dai_nao.tao_code import tao_code
        ket_qua = tao_code(nhanh_dict, yeu_to, noi_dung)
        if ket_qua and ket_qua.get("thanh_cong"):
            return ket_qua.get("code", ""), ket_qua.get("ngon_ngu", "")
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Tạo code lỗi: {e}")

    # Fallback: lấy code thô từ node
    hanh_dong = nhanh_dict.get("hanh_dong") or {}
    if isinstance(hanh_dong, dict):
        code = hanh_dong.get("code") or nhanh_dict.get("code") or ""
        ngon_ngu = hanh_dong.get("ngon_ngu") or nhanh_dict.get("ngon_ngu") or "python"
        return code, ngon_ngu
    return "", "python"


# ----------------------------------------------------------------
# HÀM PHỤ: TẠO HƯỚNG DẪN SANDBOX
# ----------------------------------------------------------------
def _tao_huong_dan_sandbox(code, ngon_ngu):
    return {
        "che_do": "client_side",
        "ngon_ngu": ngon_ngu,
        "code": code,
        "huong_dan": (
            "Code sẽ chạy trên trình duyệt của bạn qua LiveCodes. "
            "Kết quả và lỗi (nếu có) sẽ được gửi tự động về "
            "Rồng Thần để sửa nếu cần."
        ),
    }


# ----------------------------------------------------------------
# HÀM CHÍNH: XỬ LÝ TASK
# ----------------------------------------------------------------
def xu_ly_task(du_lieu):
    """Điều phối xử lý task."""
    thoi_gian_bat_dau = time.time()

    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")

    # ============================================================
    # BƯỚC 0: CÂU HỎI THỜI GIAN
    # ============================================================
    if noi_dung:
        try:
            from dai_nao.thoi_gian import xu_ly_cau_hoi_thoi_gian
            ket_qua_tg = xu_ly_cau_hoi_thoi_gian(noi_dung)
            if ket_qua_tg and ket_qua_tg.get("tra_loi"):
                return ket_qua_tg
        except ImportError:
            pass
        except Exception as e:
            _ghi_log("loi", f"Xử lý thời gian lỗi: {e}")

    # ============================================================
    # BƯỚC 0.5: LẤY NGỮ CẢNH (L39 — gọi ở đầu vào)
    # ============================================================
    ngu_canh = _lay_ngu_canh(du_lieu)

    # ============================================================
    # BƯỚC 1: CHUẨN HÓA INPUT
    # ============================================================
    try:
        from dai_nao.chuan_hoa import chuan_hoa
        noi_dung_chuan = chuan_hoa(noi_dung) or noi_dung
    except ImportError:
        noi_dung_chuan = noi_dung
    except Exception as e:
        _ghi_log("loi", f"Chuẩn hóa lỗi: {e}")
        noi_dung_chuan = noi_dung

    # ============================================================
    # BƯỚC 2: TRÍCH XUẤT 5 YẾU TỐ
    # ============================================================
    try:
        from dai_nao.trich_xuat import trich_xuat_5_yeu_to
        yeu_to = trich_xuat_5_yeu_to(noi_dung_chuan) or {}
    except ImportError:
        yeu_to = {}
    except Exception as e:
        _ghi_log("loi", f"Trích xuất lỗi: {e}")
        yeu_to = {}

    # ============================================================
    # BƯỚC 3: KIỂM TRA 5 YẾU TỐ — CHỈ HỎI LẠI KHI MƠ HỒ
    # ============================================================
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
    # BƯỚC 4: PHÂN LOẠI TASK (truyền ngữ cảnh)
    # ============================================================
    try:
        from dai_nao.phan_loai import phan_loai
        loai_task = phan_loai(noi_dung_chuan, yeu_to) or {}
    except ImportError:
        loai_task = {}
    except Exception as e:
        _ghi_log("loi", f"Phân loại lỗi: {e}")
        loai_task = {}

    # ============================================================
    # BƯỚC 5: DUYỆT CÂY QUYẾT ĐỊNH
    # ============================================================
    nhanh_tot_nhat = None
    try:
        from dai_nao.duyet_cay import duyet_cay
        nhanh_tot_nhat = duyet_cay(noi_dung_chuan, loai_task, yeu_to)
    except ImportError:
        nhanh_tot_nhat = None
    except Exception as e:
        _ghi_log("loi", f"Duyệt cây lỗi: {e}")
        nhanh_tot_nhat = None

    # ============================================================
    # BƯỚC 6: KIỂM TRA FAILED_PATHS
    # ============================================================
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

    # ============================================================
    # BƯỚC 7: CHẤM ĐIỂM
    # ============================================================
    if nhanh_tot_nhat:
        try:
            from dai_nao.cham_diem import cham_diem
            diem = cham_diem(nhanh_tot_nhat, yeu_to)
            if diem < 0.7:
                _ghi_log("dai-nao", f"Nhánh có điểm thấp ({diem}) — bỏ qua.")
                nhanh_tot_nhat = None
        except ImportError:
            pass
        except Exception as e:
            _ghi_log("loi", f"Chấm điểm lỗi: {e}")

    # ============================================================
    # BƯỚC 8: THỰC THI NHÁNH
    # ============================================================
    if nhanh_tot_nhat:
        return _thuc_thi_nhanh(
            nhanh_tot_nhat, noi_dung_chuan, yeu_to, loai_task,
            chu_so_huu, thoi_gian_bat_dau, ngu_canh,
        )

    # ============================================================
    # BƯỚC 8.5: THỬ MƯỢN NHÁNH GẦN GIỐNG (L36)
    # ============================================================
    node_muon = _thu_muon_nhanh(noi_dung_chuan, loai_task, yeu_to, ngu_canh)
    if node_muon:
        _ghi_log("dai-nao", "Đã mượn nhánh gần giống — không cần gọi Tiểu não.")
        # Lưu node mượn vào cây
        try:
            from dai_nao.ghi_nho import luu_node
            node_dict = _node_sang_dict(node_muon)
            if node_dict:
                luu_node(node_dict)
        except Exception as e:
            _ghi_log("loi", f"Lưu node mượn lỗi: {e}")

        # Chia sẻ nhánh
        _thu_chia_se_nhanh(node_muon)

        return _thuc_thi_nhanh(
            node_muon, noi_dung_chuan, yeu_to, loai_task,
            chu_so_huu, thoi_gian_bat_dau, ngu_canh,
        )

    # ============================================================
    # BƯỚC 9: KHÔNG CÓ NHÁNH — GỌI TIỂU NÃO
    # ============================================================
    _ghi_log("dai-nao", "Không có nhánh khớp — gọi Tiểu não.")

    node_moi = _goi_tieu_nao(
        {"noi_dung": noi_dung_chuan, "yeu_to": yeu_to, "loai_task": loai_task},
        ngu_canh,
    )

    if not node_moi:
        return {
            "thanh_cong": True,
            "tra_loi": "🐉 Ta chưa hiểu rõ task này. "
                       "Bạn có thể nói cụ thể hơn không?",
        }

    # Lưu node mới vào cây
    try:
        from dai_nao.ghi_nho import luu_node
        node_dict = _node_sang_dict(node_moi)
        if node_dict:
            luu_node(node_dict)
    except Exception as e:
        _ghi_log("loi", f"Lưu node mới lỗi: {e}")

    # Chia sẻ nhánh tự động (L35)
    _thu_chia_se_nhanh(node_moi)

    # Cập nhật ưu tiên (L38)
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
    """Thực thi nhánh đã chọn."""
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

    # --- Nhánh cần tra web ---
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

    # --- Nhánh cần chạy code ---
    code_mau = hanh_dong.get("code") or nhanh_dict.get("code")
    ngon_ngu = hanh_dong.get("ngon_ngu") or nhanh_dict.get("ngon_ngu") or ""

    if code_mau:
        # L42: Tạo code (thay placeholder nếu có)
        code_final, ngon_ngu_final = _tao_code_tu_node(nhanh_dict, yeu_to, noi_dung)

        if not code_final:
            code_final = code_mau
            ngon_ngu_final = ngon_ngu or "python"

        # L43: Phân biệt ngôn ngữ
        ngon_ngu_final = _phan_biet_ngon_ngu(code_final, ngon_ngu_final)

        _cap_nhat_node_sau_thanh_cong(nhanh_dict)
        _cap_nhat_uu_tien_node(nhanh)

        huong_dan = _tao_huong_dan_sandbox(code_final, ngon_ngu_final)
        return {
            "thanh_cong": True,
            "tra_loi": "Đây là code bạn cần:",
            "code": code_final,
            "ngon_ngu": ngon_ngu_final,
            "sandbox": huong_dan,
        }

    # --- Nhánh có cách giải trực tiếp ---
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

    # --- Nhánh không có gì để trả ---
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
    """Tăng số_lần_thử + thành_công."""
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

        # Cập nhật uu_tien
        try:
            from dai_nao.uu_tien import tinh_uu_tien
            node_hien_tai["uu_tien"] = int(tinh_uu_tien(node_hien_tai) * 100)
        except ImportError:
            pass

        luu_node(node_hien_tai)
    except Exception as e:
        _ghi_log("loi", f"Cập nhật node lỗi: {e}")


# ----------------------------------------------------------------
# HÀM CÔNG KHAI: GHI THẤT BẠI VÀO CÂY (L34)
# ----------------------------------------------------------------
def ghi_that_bai_vao_cay(id_node, noi_dung, ly_do=""):
    """
    Ghi 1 vết sai vào node. Được gọi từ route /api/sandbox/ket-qua.

    id_node: id node đã dùng.
    noi_dung: task gốc.
    ly_do: mô tả lỗi.

    Trả về: dict thống kê hoặc {} nếu lỗi.
    """
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

        # Cập nhật ưu tiên
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
    """
    Ghi 1 lần thành công vào node. Được gọi từ route /api/sandbox/ket-qua
    khi client báo code chạy thành công.

    Trả về: dict thống kê hoặc {} nếu lỗi.
    """
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

        # Cập nhật ưu tiên
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
"""
xu_ly_task.py - Trung tâm điều phối Đại não Rồng Thần.

Nhiệm vụ:
    - Nhận task từ nhan_task.py.
    - Điều phối 12 bước xử lý theo Phần 4 của dự án.
    - Gọi Tiểu não khi bí, gọi Tra web khi cần, gọi Sandbox khi chạy code.
    - Cập nhật cây quyết định sau mỗi task.

Luồng 12 bước:
    1. Chuẩn hóa input (chuan_hoa.py).
    2. Trích xuất 5 yếu tố (trich_xuat.py).
    3. Kiểm tra đủ 5 yếu tố chưa → nếu thiếu, hỏi lại.
    4. Phân loại task (phan_loai.py).
    5. Duyệt cây quyết định (duyet_cay.py).
    6. Kiểm tra failed_paths (chong_lap_sai.py).
    7. Chấm điểm nhánh (cham_diem.py).
    8. Thực thi nhánh:
        - Nếu có code → gọi Sandbox.
        - Nếu cần tra web → gọi Tra web.
        - Nếu bí hoàn toàn → gọi Tiểu não.
    9. Nhận kết quả, cập nhật cây (ghi_nho.py).
    10. Trả kết quả cho nhan_task.py.

Quy tắc:
    - Không đoán bừa. Độ tin cậy < 95% → hỏi lại.
    - Đây là TRUNG TÂM — chỉ điều phối, không chứa logic nghiệp vụ.
    - Mọi nhánh xử lý đều có try/except — không sập luồng chính.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import time


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
# HÀM PHỤ: HỎI LẠI NGƯỜI DÙNG
# ----------------------------------------------------------------
def _hoi_lai(ly_do, cau_hoi):
    """Trả kết quả hỏi lại người dùng."""
    return {
        "thanh_cong": True,
        "tra_loi": f"{ly_do}\n\n{cau_hoi}",
        "hoi_lai": True,
    }


# ----------------------------------------------------------------
# HÀM PHỤ: LẤY NGỮ CẢNH
# ----------------------------------------------------------------
def _lay_ngu_canh(du_lieu):
    """
    Gọi ngu_canh.py để lấy 10 loại ngữ cảnh từ lịch sử + dữ liệu hiện tại.
    Trả về dict ngữ cảnh, hoặc {} nếu chưa có file.
    """
    try:
        from dai_nao.ngu_canh import lay_ngu_canh
        return lay_ngu_canh(du_lieu) or {}
    except ImportError:
        return {}


# ----------------------------------------------------------------
# HÀM PHỤ: XỬ LÝ KHI BÍ — GỌI TIỂU NÃO
# ----------------------------------------------------------------
def _goi_tieu_nao(task, ngu_canh):
    """
    Gọi Tiểu não khi Đại não bí.
    Trả về node mới (dict) hoặc None nếu Tiểu não không sinh được.
    """
    try:
        from dai_nao.su_dung_model import su_dung_model
        return su_dung_model(task, ngu_canh)
    except ImportError:
        _ghi_log("loi", "su_dung_model.py chưa có — không gọi được Tiểu não.")
        return None
    except Exception as e:
        _ghi_log("loi", f"Tiểu não lỗi: {e}")
        return None


# ----------------------------------------------------------------
# HÀM PHỤ: CHẠY CODE QUA SANDBOX
# ----------------------------------------------------------------
def _chay_sandbox(code, ngon_ngu):
    """
    Chạy code qua sandbox.
    Trả về dict { thanh_cong, stdout, stderr } hoặc None.
    """
    try:
        if ngon_ngu == "html":
            from sanbox.chay_html import chay_html
            return chay_html({"code": code})
        else:
            from sanbox.chay_python import chay_python
            return chay_python({"code": code})
    except ImportError:
        return None
    except Exception as e:
        return {"thanh_cong": False, "stderr": str(e)}


# ----------------------------------------------------------------
# HÀM PHỤ: GỌI TRA WEB
# ----------------------------------------------------------------
def _goi_tra_web(cau_hoi):
    """
    Gọi tra web để tìm thông tin.
    Trả về chuỗi kết quả tổng hợp, hoặc "" nếu không có.
    """
    try:
        from dai_nao.goi_tra_web import goi_tra_web
        return goi_tra_web(cau_hoi) or ""
    except ImportError:
        return ""
    except Exception as e:
        _ghi_log("loi", f"Tra web lỗi: {e}")
        return ""


# ----------------------------------------------------------------
# HÀM CHÍNH: XỬ LÝ TASK
# ----------------------------------------------------------------
def xu_ly_task(du_lieu):
    """
    Điều phối xử lý task theo 12 bước.

    du_lieu: {
        noi_dung: str,
        anh: [str],
        file: [str],
        lich_su: [dict],
        id_chat: str?,
        id_du_an: str?,
        chu_so_huu: str,
    }

    Trả về: {
        thanh_cong: bool,
        tra_loi: str,
        code: str?,
        ngon_ngu: str?,
        hoi_lai: bool?,
        loi: str?,
    }
    """
    thoi_gian_bat_dau = time.time()

    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")

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
    # BƯỚC 3: KIỂM TRA 5 YẾU TỐ — NẾU THIẾU, HỎI LẠI
    # ============================================================
    CAN_5_YEU_TO = ("hanh_dong", "doi_tuong", "thuoc_tinh", "rang_buoc", "ngu_canh")
    thieu = [y for y in CAN_5_YEU_TO if not yeu_to.get(y)]

    # Nếu thiếu yếu tố nhưng task rõ ràng ngắn (chào hỏi, cảm ơn...) → bỏ qua
    if thieu and len(noi_dung_chuan) > 10:
        ly_do = "Task chưa đủ rõ để thực hiện."
        cau_hoi = "Bạn có thể nói rõ hơn: " + ", ".join(thieu) + " không?"
        _ghi_log("dai-nao", f"Hỏi lại {chu_so_huu}: thiếu {thieu}")
        return _hoi_lai(ly_do, cau_hoi)

    # ============================================================
    # BƯỚC 4: PHÂN LOẠI TASK
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
    # BƯỚC 7: CHẤM ĐIỂM — CHỌN NHÁNH TỐT NHẤT
    # ============================================================
    if nhanh_tot_nhat:
        try:
            from dai_nao.cham_diem import cham_diem
            diem = cham_diem(nhanh_tot_nhat)
            if diem < 0.7:
                _ghi_log("dai-nao", f"Nhánh có điểm thấp ({diem}) — bỏ qua.")
                nhanh_tot_nhat = None
        except ImportError:
            pass
        except Exception:
            pass

    # ============================================================
    # BƯỚC 8: THỰC THI NHÁNH
    # ============================================================
    if nhanh_tot_nhat:
        return _thuc_thi_nhanh(
            nhanh_tot_nhat, noi_dung_chuan, yeu_to, loai_task,
            chu_so_huu, thoi_gian_bat_dau,
        )

    # ============================================================
    # BƯỚC 9: KHÔNG CÓ NHÁNH — GỌI TIỂU NÃO
    # ============================================================
    _ghi_log("dai-nao", "Không có nhánh khớp — gọi Tiểu não.")

    ngu_canh = _lay_ngu_canh(du_lieu)
    node_moi = _goi_tieu_nao(
        {"noi_dung": noi_dung_chuan, "yeu_to": yeu_to, "loai_task": loai_task},
        ngu_canh,
    )

    if not node_moi:
        # Tiểu não không sinh được — trả lời xin lỗi
        return {
            "thanh_cong": True,
            "tra_loi": "🐉 Ta chưa hiểu rõ task này. "
                       "Bạn có thể nói cụ thể hơn không?",
        }

    # Lưu node mới vào cây kho 2
    try:
        from dai_nao.ghi_nho import luu_node
        luu_node(node_moi)
    except Exception as e:
        _ghi_log("loi", f"Lưu node mới lỗi: {e}")

    # Thực thi node vừa sinh
    return _thuc_thi_nhanh(
        node_moi, noi_dung_chuan, yeu_to, loai_task,
        chu_so_huu, thoi_gian_bat_dau,
    )


# ----------------------------------------------------------------
# HÀM PHỤ: THỰC THI NHÁNH
# ----------------------------------------------------------------
def _thuc_thi_nhanh(nhanh, noi_dung, yeu_to, loai_task, chu_so_huu, thoi_gian_bat_dau):
    """
    Thực thi nhánh đã chọn.
    - Nếu nhánh cần code → chạy sandbox.
    - Nếu nhánh cần tra web → gọi tra web.
    - Nếu nhánh có cách giải trực tiếp → trả về.
    """
    hanh_dong = nhanh.get("hanh_dong") or {}
    loai_hanh_dong = hanh_dong.get("loai") or nhanh.get("loai") or ""

    # --- Nhánh cần tra web ---
    if loai_hanh_dong == "tra_web" or nhanh.get("can_tra_web"):
        ket_qua_web = _goi_tra_web(noi_dung)
        if ket_qua_web:
            _ghi_log("tra-web", f"Tra web cho {chu_so_huu}: {ket_qua_web[:80]}...")
            return {
                "thanh_cong": True,
                "tra_loi": ket_qua_web,
            }

    # --- Nhánh cần chạy code ---
    code_mau = hanh_dong.get("code") or nhanh.get("code")
    ngon_ngu = hanh_dong.get("ngon_ngu") or nhanh.get("ngon_ngu") or "python"

    if code_mau:
        ket_qua_sandbox = _chay_sandbox(code_mau, ngon_ngu)
        if ket_qua_sandbox and ket_qua_sandbox.get("thanh_cong"):
            # Thành công — trả code + kết quả
            _cap_nhat_node_sau_thanh_cong(nhanh)
            return {
                "thanh_cong": True,
                "tra_loi": "Đây là code bạn cần:",
                "code": code_mau,
                "ngon_ngu": ngon_ngu,
            }
        else:
            # Sandbox lỗi — ghi log, trả code kèm cảnh báo
            loi_sandbox = (ket_qua_sandbox or {}).get("stderr", "không rõ")
            _ghi_log("sandbox", f"Sandbox lỗi: {loi_sandbox}")

            # Thử tự sửa lỗi
            try:
                from dai_nao.tu_sua_loi import tu_sua_loi
                code_moi = tu_sua_loi(code_mau, loi_sandbox, ngon_ngu)
                if code_moi and code_moi != code_mau:
                    _cap_nhat_node_sau_thanh_cong(nhanh)
                    return {
                        "thanh_cong": True,
                        "tra_loi": "Đây là code đã sửa lỗi cho bạn:",
                        "code": code_moi,
                        "ngon_ngu": ngon_ngu,
                    }
            except ImportError:
                pass

            return {
                "thanh_cong": True,
                "tra_loi": f"Code gặp lỗi khi chạy:\n{loi_sandbox}\n\nĐây là code gốc:",
                "code": code_mau,
                "ngon_ngu": ngon_ngu,
            }

    # --- Nhánh có cách giải trực tiếp (không cần code) ---
    cach_giai = nhanh.get("cach_giai") or {}
    tra_loi = cach_giai.get("mo_ta") or nhanh.get("tra_loi") or ""

    if tra_loi:
        _cap_nhat_node_sau_thanh_cong(nhanh)
        return {
            "thanh_cong": True,
            "tra_loi": tra_loi,
        }

    # --- Nhánh không có gì để trả ---
    return {
        "thanh_cong": True,
        "tra_loi": "🐉 Ta đã tìm thấy nhánh phù hợp nhưng chưa có cách giải. "
                   "Bạn có thể nói rõ hơn không?",
    }


# ----------------------------------------------------------------
# HÀM PHỤ: CẬP NHẬT NODE SAU KHI THÀNH CÔNG
# ----------------------------------------------------------------
def _cap_nhat_node_sau_thanh_cong(nhanh):
    """
    Tăng số_lần_thử + thành_công + cập nhật score cho node.
    Ghi lại vào kho 2.
    """
    try:
        id_node = nhanh.get("id")
        if not id_node:
            return

        from dai_nao.ghi_nho import lay_node, luu_node

        node_hien_tai = lay_node(id_node) or {}
        so_lan_thu = int(node_hien_tai.get("so_lan_thu", 0)) + 1
        thanh_cong = int(node_hien_tai.get("thanh_cong", 0)) + 1
        ty_le = thanh_cong / so_lan_thu if so_lan_thu > 0 else 1.0

        node_hien_tai["so_lan_thu"] = so_lan_thu
        node_hien_tai["thanh_cong"] = thanh_cong
        node_hien_tai["ty_le_thanh_cong"] = round(ty_le, 3)
        node_hien_tai["lan_dung_cuoi"] = int(time.time())

        luu_node(node_hien_tai)
    except Exception as e:
        _ghi_log("loi", f"Cập nhật node lỗi: {e}")
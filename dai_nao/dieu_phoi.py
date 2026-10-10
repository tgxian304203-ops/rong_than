"""
dieu_phoi.py - Điều phối toàn bộ luồng Đại não.

Nhiệm vụ:
    - Nhận yêu cầu đã phân loại.
    - Điều phối: phân loại → ghi hợp đồng → gọi Boss → verify → trả kết quả.
    - Xử lý 2 luồng: ĐƠN GIẢN và DỰ ÁN.
    - Xử lý sự kiện: Boss hết quota → chuyển Boss thế.
    - Verify: Code → Sandbox; Toán/Văn/Khác → Boss tự verify.

Nguyên tắc:
    - Đây là trung tâm điều phối — code logic thuần.
    - Gọi Boss để suy luận.
    - Gọi Model để sinh code.
    - Vòng lặp sửa lỗi tối đa 99s.
"""

import time


# ================================================================
# HẰNG SỐ
# ================================================================
THOI_GIAN_VERIFY_TOI_DA = 99   # giây
SO_LAN_SUA_TOI_DA = 5


# ================================================================
# GHI LOG
# ================================================================
def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ================================================================
# ĐIỀU PHỐI CHÍNH
# ================================================================
def dieu_phoi(du_lieu):
    """
    Điều phối toàn bộ luồng xử lý.

    du_lieu: {
        noi_dung, anh, file, lich_su,
        id_chat, id_du_an, chu_so_huu, thoi_gian,
    }

    Trả về: {
        thanh_cong, tra_loi, code?, ngon_ngu?,
        ket_qua_chay?, loi?,
    }
    """
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    noi_dung = du_lieu.get("noi_dung", "")
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    id_chat = du_lieu.get("id_chat", "")

    if not noi_dung:
        return {"thanh_cong": False, "loi": "Không có nội dung."}

    _ghi_log("dai-nao", f"Điều phối: {noi_dung[:80]}")

    # 1. Phân loại
    try:
        from dai_nao.phan_loai import phan_loai
        phan_loai_ket_qua = phan_loai(noi_dung)
    except Exception as e:
        _ghi_log("loi", f"Phân loại lỗi: {e}")
        phan_loai_ket_qua = {"loai": "don_gian", "loai_noi_dung": "khac"}

    loai = phan_loai_ket_qua.get("loai", "don_gian")

    # 2. Điều phối theo loại
    if loai == "du_an":
        return _dieu_phoi_du_an(du_lieu, phan_loai_ket_qua)
    return _dieu_phoi_don_gian(du_lieu, phan_loai_ket_qua)


# ================================================================
# ĐIỀU PHỐI ĐƠN GIẢN
# ================================================================
def _dieu_phoi_don_gian(du_lieu, phan_loai_ket_qua):
    """
    Luồng đơn giản:
        - Ghi hợp đồng ngắn.
        - Gọi Boss trả lời.
        - Verify (nếu code → sandbox).
        - Trả kết quả.
    """
    noi_dung = du_lieu.get("noi_dung", "")
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    id_chat = du_lieu.get("id_chat", "")

    # 1. Ghi hợp đồng ngắn
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

    # 2. Gọi Boss
    ket_qua_boss = _goi_boss(du_lieu, phan_loai_ket_qua)

    if not ket_qua_boss or not ket_qua_boss.get("thanh_cong"):
        return {
            "thanh_cong": False,
            "loi": (ket_qua_boss or {}).get("loi", "Boss không trả lời."),
        }

    # 3. Nếu có code → verify qua sandbox
    ket_qua_cuoi = ket_qua_boss
    if ket_qua_boss.get("code"):
        ket_qua_cuoi = _verify_code(ket_qua_boss, chu_so_huu, id_chat)

    # 4. Lưu kết quả vào cây
    if chu_so_huu and id_chat:
        try:
            from dai_nao.luu_ket_qua import luu_ket_qua
            luu_ket_qua(chu_so_huu, id_chat, ket_qua_cuoi)
        except Exception:
            pass

    return ket_qua_cuoi


# ================================================================
# ĐIỀU PHỐI DỰ ÁN
# ================================================================
def _dieu_phoi_du_an(du_lieu, phan_loai_ket_qua):
    """
    Luồng dự án:
        - Boss lập kế hoạch + hợp đồng + hướng dẫn.
        - Ghi vào cây.
        - Chỉ huy Model từng bước.
        - Verify + cập nhật hợp đồng.
        - Trả kết quả.
    """
    noi_dung = du_lieu.get("noi_dung", "")
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")
    id_chat = du_lieu.get("id_chat", "")

    # 1. Kiểm tra cây đã có hợp đồng chưa
    co_hop_dong = False
    if chu_so_huu and id_chat:
        try:
            from dai_nao.ghi_hop_dong import doc_hop_dong
            co_hop_dong = doc_hop_dong(chu_so_huu, id_chat) is not None
        except Exception:
            co_hop_dong = False

    # 2. Nếu chưa có → Boss lập kế hoạch
    if not co_hop_dong:
        ket_qua_ke_hoach = _goi_boss_lap_ke_hoach(du_lieu, phan_loai_ket_qua)

        if not ket_qua_ke_hoach or not ket_qua_ke_hoach.get("thanh_cong"):
            return {
                "thanh_cong": False,
                "loi": (ket_qua_ke_hoach or {}).get("loi", "Boss lập kế hoạch lỗi."),
            }

        # Ghi kế hoạch vào cây
        if chu_so_huu and id_chat:
            try:
                from dai_nao.ghi_hop_dong import ghi_tu_ke_hoach
                ghi_tu_ke_hoach(chu_so_huu, id_chat, ket_qua_ke_hoach)
            except Exception as e:
                _ghi_log("loi", f"Ghi kế hoạch lỗi: {e}")

    # 3. Chỉ huy Model thực hiện bước hiện tại
    ket_qua_buoc = _chi_huy_model(du_lieu)

    if not ket_qua_buoc or not ket_qua_buoc.get("thanh_cong"):
        return {
            "thanh_cong": False,
            "loi": (ket_qua_buoc or {}).get("loi", "Model không thực hiện được."),
        }

    # 4. Verify + cập nhật
    ket_qua_cuoi = _verify_va_cap_nhat(ket_qua_buoc, chu_so_huu, id_chat)

    # 5. Lưu kết quả
    if chu_so_huu and id_chat:
        try:
            from dai_nao.luu_ket_qua import luu_ket_qua
            luu_ket_qua(chu_so_huu, id_chat, ket_qua_cuoi)
        except Exception:
            pass

    return ket_qua_cuoi


# ================================================================
# GỌI BOSS
# ================================================================
def _goi_boss(du_lieu, phan_loai_ket_qua):
    """
    Gọi Boss trả lời (luồng đơn giản).

    Trả về: dict.
    """
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


# ================================================================
# GỌI BOSS LẬP KẾ HOẠCH
# ================================================================
def _goi_boss_lap_ke_hoach(du_lieu, phan_loai_ket_qua):
    """Gọi Boss lập kế hoạch cho dự án."""
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


# ================================================================
# CHỈ HUY MODEL
# ================================================================
def _chi_huy_model(du_lieu):
    """Chỉ huy Model thực hiện bước hiện tại."""
    try:
        from tieu_nao.nhan_lenh import nhan_lenh
        return nhan_lenh(du_lieu)
    except ImportError:
        return _goi_model_truc_tiep(du_lieu)
    except Exception as e:
        _ghi_log("loi", f"Chỉ huy Model lỗi: {e}")
        return {"thanh_cong": False, "loi": f"Model lỗi: {e}"}


# ================================================================
# GỌI MODEL TRỰC TIẾP (FALLBACK)
# ================================================================
def _goi_model_truc_tiep(du_lieu):
    """
    Fallback khi chưa có boss_model hoặc tieu_nao.
    Trả về câu trả lời mặc định.
    """
    noi_dung = du_lieu.get("noi_dung", "")
    return {
        "thanh_cong": True,
        "tra_loi": f"Rồng Thần đã nhận: {noi_dung[:200]}",
        "code": None,
        "ngon_ngu": None,
    }


# ================================================================
# VERIFY CODE QUA SANDBOX
# ================================================================
def _verify_code(ket_qua, chu_so_huu, id_chat):
    """
    Verify code qua Sandbox.

    Vòng lặp sửa lỗi tối đa 99s.

    Trả về: ket_qua đã verify.
    """
    code = ket_qua.get("code")
    ngon_ngu = ket_qua.get("ngon_ngu", "python")

    if not code:
        return ket_qua

    bat_dau = time.time()
    so_lan_sua = 0
    ket_qua_hien_tai = ket_qua

    while so_lan_sua < SO_LAN_SUA_TOI_DA:
        # Kiểm tra timeout 99s
        if time.time() - bat_dau > THOI_GIAN_VERIFY_TOI_DA:
            _ghi_log("dai-nao", "Hết 99s verify — dừng.")
            ket_qua_hien_tai["het_thoi_gian"] = True
            return ket_qua_hien_tai

        # Chạy sandbox
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

        # Kiểm tra lỗi
        if ket_qua_chay.get("thanh_cong"):
            ket_qua_hien_tai["ket_qua_chay"] = ket_qua_chay
            _ghi_log("dai-nao", f"Code OK sau {so_lan_sua} lần sửa.")
            return ket_qua_hien_tai

        # Có lỗi → gọi Boss sửa
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


# ================================================================
# VERIFY + CẬP NHẬT
# ================================================================
def _verify_va_cap_nhat(ket_qua, chu_so_huu, id_chat):
    """
    Verify + cập nhật hợp đồng/tiến độ.

    - Code → Sandbox.
    - Toán/Văn/Khác → Boss tự verify.
    """
    loai_noi_dung = ket_qua.get("loai_noi_dung", "")

    if ket_qua.get("code"):
        ket_qua = _verify_code(ket_qua, chu_so_huu, id_chat)

    # Cập nhật hợp đồng
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


# ================================================================
# ĐẾM BƯỚC HIỆN TẠI
# ================================================================
def _dem_buoc_hien_tai(chu_so_huu, id_chat):
    """Đếm bước hiện tại / tổng."""
    try:
        from cay_linh_hon.tien_do import doc_tien_do
        tien_do = doc_tien_do(chu_so_huu, id_chat)
        if tien_do:
            return f"{tien_do.get('buoc_hien_tai', 0)}/{tien_do.get('tong_buoc', 0)}"
    except Exception:
        pass
    return "0/0"


# ================================================================
# XỬ LÝ KHI BOSS HẾT QUOTA
# ================================================================
def xu_ly_boss_het_quota(chu_so_huu, id_chat, du_lieu):
    """
    Xử lý khi Boss đầu hết quota → chuyển Boss thế.

    Boss thế bị CODE ÉP đọc hợp đồng trước khi làm.

    Trả về: ket_qua.
    """
    _ghi_log("dai-nao", f"Boss hết quota — chuyển Boss thế chat {id_chat}")

    # 1. ÉP Boss thế đọc hợp đồng
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

    # 2. Tiếp tục xử lý với Boss thế
    return dieu_phoi(du_lieu)


# ================================================================
# XỬ LÝ USER ĐỔI Ý
# ================================================================
def xu_ly_doi_y(chu_so_huu, id_chat, noi_dung, muc_do="nho"):
    """
    Xử lý khi user đổi ý.

    muc_do: "nho" | "vua" | "lon".

    Trả về: True/False.
    """
    try:
        from cay_linh_hon.ket_noi import su_kien_doi_y
        return su_kien_doi_y(chu_so_huu, id_chat, muc_do, noi_dung)
    except Exception as e:
        _ghi_log("loi", f"Xử lý đổi ý lỗi: {e}")
        return False


# ================================================================
# 3 TÌNH HUỐNG BOSS THẾ PHẢI XỬ LÝ
# ================================================================
def boss_the_gui_lai_code(chu_so_huu, id_chat, buoc=None):
    """Tình huống 1: User bảo gửi lại code cũ."""
    try:
        from cay_linh_hon.doc_code import format_gui_user
        return format_gui_user(chu_so_huu, id_chat, buoc)
    except Exception as e:
        _ghi_log("loi", f"Gửi lại code lỗi: {e}")
        return ""


def boss_the_tra_web_cap_nhat(chu_so_huu, id_chat, cau_hoi):
    """Tình huống 2: User bảo tra web cập nhật thông tin."""
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
    """
    Tình huống 3: User bảo kiểm tra toàn bộ code.

    Chia nhỏ từng bước, kiểm tra lần lượt.
    Nếu bước N lỗi → dừng sửa ngay, rồi mới tiếp.
    """
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

        # Chạy sandbox
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


# ================================================================
# ĐOÁN NGÔN NGỮ TỪ TÊN FILE
# ================================================================
def _doan_ngon_ngu(ten_file):
    """Đoán ngôn ngữ từ tên file."""
    if not ten_file or "." not in ten_file:
        return "python"

    duoi = ten_file.rsplit(".", 1)[-1].lower()
    bang = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "html": "html",
        "css": "css",
    }
    return bang.get(duoi, "python")
"""
tra_ket_qua.py - Trả kết quả cuối cho giao diện.

Nhiệm vụ:
    - Chuẩn hóa kết quả trước khi trả giao diện.
    - Tách code khỏi câu trả lời.
    - Đính kèm thông tin bước / tiến độ / lỗi (nếu có).

Nguyên tắc:
    - Đại não gọi hàm này cuối cùng.
    - Trả về format mà giao diện hiểu.
"""


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
# TRẢ KẾT QUẢ CHÍNH
# ================================================================
def tra_ket_qua(ket_qua_dai_nao, chu_so_huu="", id_chat=""):
    """
    Chuẩn hóa kết quả trước khi trả giao diện.

    ket_qua_dai_nao: {
        thanh_cong, tra_loi, code, ngon_ngu,
        ket_qua_chay, loi, ...
    }

    Trả về: {
        thanh_cong, tra_loi, code?, ngon_ngu?,
        ket_qua_chay?, tien_do?, loi?
    }
    """
    ket_qua_tra = {
        "thanh_cong": False,
        "tra_loi": "",
    }

    if not ket_qua_dai_nao:
        ket_qua_tra["loi"] = "Không có kết quả."
        return ket_qua_tra

    # 1. Trạng thái
    ket_qua_tra["thanh_cong"] = bool(ket_qua_dai_nao.get("thanh_cong", False))

    # 2. Câu trả lời
    tra_loi = ket_qua_dai_nao.get("tra_loi") or ""
    ket_qua_tra["tra_loi"] = tra_loi

    # 3. Code (nếu có)
    if ket_qua_dai_nao.get("code"):
        ket_qua_tra["code"] = ket_qua_dai_nao["code"]
        ket_qua_tra["ngon_ngu"] = ket_qua_dai_nao.get("ngon_ngu") or "code"

    # 4. Kết quả chạy (nếu có)
    if ket_qua_dai_nao.get("ket_qua_chay"):
        ket_qua_tra["ket_qua_chay"] = ket_qua_dai_nao["ket_qua_chay"]

    # 5. Lỗi (nếu có)
    if ket_qua_dai_nao.get("loi"):
        ket_qua_tra["loi"] = ket_qua_dai_nao["loi"]

    # 6. Tiến độ (nếu có chu_so_huu + id_chat)
    if chu_so_huu and id_chat:
        try:
            from cay_linh_hon.tien_do import (
                doc_tien_do,
                phan_tram_hoan_thanh,
            )
            tien_do = doc_tien_do(chu_so_huu, id_chat)
            if tien_do:
                ket_qua_tra["tien_do"] = {
                    "buoc_hien_tai": tien_do.get("buoc_hien_tai", 0),
                    "tong_buoc": tien_do.get("tong_buoc", 0),
                    "trang_thai": tien_do.get("trang_thai", ""),
                    "phan_tram": phan_tram_hoan_thanh(chu_so_huu, id_chat),
                }
        except Exception:
            pass

    # 7. Đảm bảo có nội dung
    if not ket_qua_tra["tra_loi"] and not ket_qua_tra.get("code"):
        if ket_qua_tra.get("loi"):
            ket_qua_tra["tra_loi"] = f"⚠️ {ket_qua_tra['loi']}"
        else:
            ket_qua_tra["tra_loi"] = "Rồng Thần không có phản hồi."

    return ket_qua_tra


# ================================================================
# TRẢ KẾT QUẢ LỖI
# ================================================================
def tra_ket_qua_loi(loi, id_tin_nhan=""):
    """
    Trả kết quả lỗi cho giao diện.

    Trả về: dict.
    """
    ket_qua = {
        "thanh_cong": False,
        "tra_loi": f"⚠️ {loi}",
        "loi": loi,
    }

    if id_tin_nhan:
        ket_qua["id_tin_nhan"] = id_tin_nhan

    return ket_qua


# ================================================================
# TRẢ KẾT QUẢ THÀNH CÔNG
# ================================================================
def tra_ket_qua_thanh_cong(tra_loi, code=None, ngon_ngu=None,
                            ket_qua_chay=None, id_tin_nhan=""):
    """
    Trả kết quả thành công cho giao diện.

    Trả về: dict.
    """
    ket_qua = {
        "thanh_cong": True,
        "tra_loi": tra_loi or "",
    }

    if code:
        ket_qua["code"] = code
        ket_qua["ngon_ngu"] = ngon_ngu or "code"

    if ket_qua_chay:
        ket_qua["ket_qua_chay"] = ket_qua_chay

    if id_tin_nhan:
        ket_qua["id_tin_nhan"] = id_tin_nhan

    return ket_qua


# ================================================================
# TRẢ KẾT QUẢ CHO CHAT DỰ ÁN
# ================================================================
def tra_ket_qua_du_an(ket_qua_dai_nao, chu_so_huu="", id_tro=""):
    """
    Chuẩn hóa kết quả cho chat dự án.

    Trả về: dict.
    """
    ket_qua = tra_ket_qua(ket_qua_dai_nao, chu_so_huu, id_tro)
    return ket_qua


# ================================================================
# ĐÓNG GÓI KẾT QUẢ ĐẦY ĐỦ
# ================================================================
def dong_goi_day_du(ket_qua_dai_nao, chu_so_huu, id_chat):
    """
    Đóng gói kết quả đầy đủ (kèm tiến độ, code cũ, blacklist).

    Trả về: dict.
    """
    ket_qua = tra_ket_qua(ket_qua_dai_nao, chu_so_huu, id_chat)

    if not chu_so_huu or not id_chat:
        return ket_qua

    # Thêm thông tin cây linh hồn
    try:
        from cay_linh_hon.hop_dong import doc_hop_dong
        hop_dong = doc_hop_dong(chu_so_huu, id_chat)
        if hop_dong:
            ket_qua["hop_dong"] = {
                "dang_lam_gi": hop_dong.get("dang_lam_gi", ""),
                "dang_lam_toi_dau": hop_dong.get("dang_lam_toi_dau", ""),
                "tiep_theo_lam_gi": hop_dong.get("tiep_theo_lam_gi", ""),
            }
    except Exception:
        pass

    try:
        from cay_linh_hon.luu_code import dem_file_da_viet
        ket_qua["so_file_da_viet"] = dem_file_da_viet(chu_so_huu, id_chat)
    except Exception:
        pass

    return ket_qua


# ================================================================
# TÓM TẮT KẾT QUẢ
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        tra_loi = ket_qua.get("tra_loi", "")
        return f"✅ {tra_loi[:200]}"

    return f"❌ {ket_qua.get('loi', 'Lỗi không xác định.')[:200]}"
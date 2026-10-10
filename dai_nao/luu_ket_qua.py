"""
luu_ket_qua.py - Lưu kết quả vào Cây linh hồn (từ Đại não).

Nhiệm vụ:
    - Lưu kết quả Boss/Model vào cây linh hồn.
    - Gộp từ chức năng cũ (luu_ket_qua_boss + luu_ket_qua).
    - Cập nhật hợp đồng + hướng dẫn sau khi lưu.

Nguyên tắc:
    - Đại não gọi hàm này sau khi có kết quả cuối.
    - Lưu vào kho 2 (cây linh hồn).
"""

import time


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
# LƯU KẾT QUẢ CHUNG
# ================================================================
def luu_ket_qua(chu_so_huu, id_chat, ket_qua, buoc=None):
    """
    Lưu kết quả (Boss hoặc Model) vào cây.

    ket_qua: {
        tra_loi, code, ngon_ngu, ket_qua_chay,
        thanh_cong, ...
    }

    buoc: nếu có → lưu theo bước.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat or not ket_qua:
        return False

    try:
        # Lưu code (nếu có)
        if ket_qua.get("code"):
            from cay_linh_hon.luu_code import luu_code_moi
            luu_code_moi(
                chu_so_huu, id_chat,
                buoc or 0,
                _doan_ten_file(ket_qua.get("ngon_ngu")),
                ket_qua["code"],
            )

        # Lưu kết quả chạy (nếu có)
        if ket_qua.get("ket_qua_chay"):
            from cay_linh_hon.luu_ket_qua import luu_ket_qua as _luu_kq
            _luu_kq(
                chu_so_huu, id_chat,
                buoc or 0,
                ket_qua["ket_qua_chay"],
            )

        return True
    except Exception as e:
        _ghi_log("loi", f"Lưu kết quả lỗi: {e}")
        return False


# ================================================================
# LƯU KẾT QUẢ CỦA BOSS
# ================================================================
def luu_ket_qua_boss(chu_so_huu, id_chat, ket_qua_boss):
    """
    Lưu kết quả Boss trả về (kế hoạch, hướng dẫn, code).

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat or not ket_qua_boss:
        return False

    try:
        # Lưu hướng dẫn (nếu có)
        huong_dan = ket_qua_boss.get("huong_dan")
        if huong_dan:
            from cay_linh_hon.huong_dan import cap_nhat_huong_dan
            cap_nhat_huong_dan(chu_so_huu, id_chat, {
                "nen_lam_gi": huong_dan,
            })

        # Lưu hợp đồng (nếu có)
        hop_dong = ket_qua_boss.get("hop_dong")
        if hop_dong:
            from cay_linh_hon.hop_dong import cap_nhat_hop_dong
            cap_nhat_hop_dong(
                chu_so_huu, id_chat,
                dang_lam_gi=hop_dong.get("dang_lam_gi"),
                dang_lam_toi_dau=hop_dong.get("dang_lam_toi_dau"),
                tiep_theo_lam_gi=hop_dong.get("tiep_theo_lam_gi"),
            )

        _ghi_log("dai-nao", f"Lưu kết quả Boss chat {id_chat}")
        return True
    except Exception as e:
        _ghi_log("loi", f"Lưu kết quả Boss lỗi: {e}")
        return False


# ================================================================
# LƯU KẾT QUẢ SANG BƯỚC TIẾP
# ================================================================
def luu_va_chuyen_buoc(chu_so_huu, id_chat, buoc,
                        ket_qua, tiep_theo=""):
    """
    Lưu kết quả + chuyển sang bước tiếp.

    Trả về: True/False.
    """
    ok1 = luu_ket_qua(chu_so_huu, id_chat, ket_qua, buoc)

    try:
        from cay_linh_hon.tien_do import them_buoc, tang_buoc
        them_buoc(chu_so_huu, id_chat,
                  f"Bước {buoc}", "xong")
        tang_buoc(chu_so_huu, id_chat)
    except Exception:
        pass

    try:
        from cay_linh_hon.hop_dong import cap_nhat_hop_dong
        cap_nhat_hop_dong(
            chu_so_huu, id_chat,
            tiep_theo_lam_gi=tiep_theo or f"Bước {buoc + 1}",
        )
    except Exception:
        pass

    return ok1


# ================================================================
# ĐOÁN TÊN FILE TỪ NGÔN NGỮ
# ================================================================
def _doan_ten_file(ngon_ngu):
    """Đoán tên file từ ngôn ngữ code."""
    if not ngon_ngu:
        return "code.txt"

    bang = {
        "python": "code.py",
        "py": "code.py",
        "javascript": "code.js",
        "js": "code.js",
        "typescript": "code.ts",
        "ts": "code.ts",
        "html": "index.html",
        "css": "style.css",
        "json": "data.json",
        "sql": "query.sql",
        "bash": "script.sh",
        "sh": "script.sh",
        "markdown": "doc.md",
        "md": "doc.md",
    }

    return bang.get(str(ngon_ngu).lower(), "code.txt")


# ================================================================
# LƯU KẾT QUẢ CUỐI CÙNG
# ================================================================
def luu_ket_qua_cuoi(chu_so_huu, id_chat, ket_qua_cuoi):
    """
    Lưu kết quả cuối cùng của dự án.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat:
        return False

    try:
        from cay_linh_hon.tien_do import danh_dau_xong
        danh_dau_xong(chu_so_huu, id_chat)
    except Exception:
        pass

    try:
        from cay_linh_hon.hop_dong import cap_nhat_hop_dong
        cap_nhat_hop_dong(
            chu_so_huu, id_chat,
            dang_lam_gi="Đã hoàn thành",
            dang_lam_toi_dau="Xong",
            tiep_theo_lam_gi="Chờ yêu cầu mới",
        )
    except Exception:
        pass

    _ghi_log("dai-nao", f"Lưu kết quả cuối chat {id_chat}")
    return True


# ================================================================
# TÓM TẮT KẾT QUẢ
# ================================================================
def tom_tat_ket_qua(ket_qua):
    """Tạo chuỗi tóm tắt kết quả."""
    if not ket_qua:
        return ""

    if ket_qua.get("thanh_cong"):
        tra_loi = ket_qua.get("tra_loi", "")
        if tra_loi:
            return f"✅ {tra_loi[:200]}"
        return "✅ Xong."

    return f"❌ {ket_qua.get('loi', 'Lỗi không xác định.')[:200]}"
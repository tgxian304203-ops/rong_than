"""
ep_boss_doc.py - ÉP Boss THẾ đọc hợp đồng trước khi làm.

Nhiệm vụ:
    - Chỉ ép Boss THẾ (khi Boss đầu hết quota).
    - Boss ĐẦU không bị ép (vì là người tạo).
    - Chuẩn bị dữ liệu hợp đồng + hướng dẫn để Boss đọc.
    - Ghi log đã ép đọc.

Nguyên tắc:
    - Đại não gọi hàm này khi phát hiện Boss thế lên.
    - Boss phải trả "da_doc": true → mới cho làm.
    - Nếu Boss không đọc → từ chối xử lý.
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
# CHUẨN BỊ DỮ LIỆU ÉP ĐỌC
# ================================================================
def chuan_bi_du_lieu_ep_doc(chu_so_huu, id_chat):
    """
    Chuẩn bị dữ liệu để ép Boss THẾ đọc.

    Trả về: {
        hop_dong: dict,
        huong_dan: dict,
        cau_lenh_ep: str,
    }
    """
    ket_qua = {
        "hop_dong": None,
        "huong_dan": None,
        "cau_lenh_ep": "",
    }

    if not chu_so_huu or not id_chat:
        return ket_qua

    try:
        from cay_linh_hon.hop_dong import doc_hop_dong
        from cay_linh_hon.huong_dan import doc_huong_dan

        ket_qua["hop_dong"] = doc_hop_dong(chu_so_huu, id_chat)
        ket_qua["huong_dan"] = doc_huong_dan(chu_so_huu, id_chat)
    except Exception as e:
        _ghi_log("loi", f"Chuẩn bị data ép đọc lỗi: {e}")

    ket_qua["cau_lenh_ep"] = _tao_cau_lenh_ep(ket_qua)
    return ket_qua


# ================================================================
# TẠO CÂU LỆNH ÉP ĐỌC
# ================================================================
def _tao_cau_lenh_ep(du_lieu):
    """Tạo câu lệnh ép Boss THẾ đọc."""
    phan = [
        "🔴 BẠN LÀ BOSS THẾ — ĐỌC KỸ TRƯỚC KHI LÀM:",
        "",
    ]

    hop_dong = du_lieu.get("hop_dong")
    if hop_dong:
        phan.append("📋 HỢP ĐỒNG HIỆN TẠI:")
        phan.append(f"  - Đang làm: {hop_dong.get('dang_lam_gi', '(chưa có)')}")
        phan.append(f"  - Tới đâu: {hop_dong.get('dang_lam_toi_dau', '(chưa có)')}")
        phan.append(f"  - Tiếp theo: {hop_dong.get('tiep_theo_lam_gi', '(chưa có)')}")
        phan.append("")
    else:
        phan.append("📋 HỢP ĐỒNG: Chưa có (dự án mới).")
        phan.append("")

    huong_dan = du_lieu.get("huong_dan")
    if huong_dan:
        phan.append("📖 HƯỚNG DẪN:")
        if huong_dan.get("nen_lam_gi"):
            phan.append(f"  - Nên làm: {huong_dan['nen_lam_gi']}")
        blacklist = huong_dan.get("blacklist", [])
        if blacklist:
            phan.append(f"  - TRÁNH: {len(blacklist)} mục trong blacklist")
        phan.append("")

    phan.append("⚠️ BẮT BUỘC: Trả về {\"da_doc\": true} nếu đã hiểu.")
    phan.append("Nếu KHÔNG đọc → Đại não sẽ từ chối xử lý.")

    return "\n".join(phan)


# ================================================================
# ÉP BOSS ĐỌC (CHÍNH)
# ================================================================
def ep_boss_doc(chu_so_huu, id_chat, boss_the):
    """
    ÉP Boss THẾ đọc hợp đồng + hướng dẫn.

    boss_the: hàm gọi Boss (callback).
        boss_the(cau_lenh) → dict {da_doc, tra_loi}.

    Trả về: {
        thanh_cong: bool,
        da_doc: bool,
        tra_loi: str,
        loi: str?,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "da_doc": False,
        "tra_loi": "",
        "loi": "",
    }

    if not chu_so_huu or not id_chat:
        ket_qua["loi"] = "Thiếu chu_so_huu hoặc id_chat."
        return ket_qua

    if not callable(boss_the):
        ket_qua["loi"] = "boss_the không phải hàm."
        return ket_qua

    # 1. Chuẩn bị dữ liệu ép đọc
    du_lieu = chuan_bi_du_lieu_ep_doc(chu_so_huu, id_chat)

    # 2. Gọi Boss đọc
    try:
        phan_hoi = boss_the(du_lieu.get("cau_lenh_ep", ""))
    except Exception as e:
        ket_qua["loi"] = f"Boss đọc lỗi: {e}"
        return ket_qua

    if not phan_hoi or not isinstance(phan_hoi, dict):
        ket_qua["loi"] = "Boss không trả về kết quả hợp lệ."
        return ket_qua

    # 3. Kiểm tra Boss có trả "da_doc": true không
    da_doc = bool(phan_hoi.get("da_doc", False))
    ket_qua["da_doc"] = da_doc
    ket_qua["tra_loi"] = phan_hoi.get("tra_loi", "") or ""

    if not da_doc:
        ket_qua["loi"] = "Boss THẾ chưa đọc hợp đồng — từ chối xử lý."
        _ghi_log("dai-nao", f"Boss THẾ chưa đọc hợp đồng chat {id_chat}")
        return ket_qua

    ket_qua["thanh_cong"] = True
    _ghi_log("dai-nao", f"Boss THẾ đã đọc hợp đồng chat {id_chat}")
    return ket_qua


# ================================================================
# KIỂM TRA BOSS ĐÃ ĐỌC CHƯA
# ================================================================
def kiem_tra_boss_da_doc(phan_hoi_boss):
    """
    Kiểm tra phản hồi Boss có chứa da_doc=true không.

    Trả về: True/False.
    """
    if not phan_hoi_boss or not isinstance(phan_hoi_boss, dict):
        return False
    return bool(phan_hoi_boss.get("da_doc", False))


# ================================================================
# GHI NHẬN BOSS ĐÃ ĐỌC
# ================================================================
def ghi_nhan_da_doc(chu_so_huu, id_chat):
    """
    Ghi nhận Boss đã đọc (dùng để tracking).

    Trả về: True/False.
    """
    try:
        from luu_tru.ghi_nho import cap_nhat_hop_dong
        return cap_nhat_hop_dong(chu_so_huu, id_chat, {
            "boss_da_doc": True,
            "thoi_gian_boss_doc": int(time.time()),
        })
    except Exception:
        return False
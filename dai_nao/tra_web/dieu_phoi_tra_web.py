"""
dieu_phoi_tra_web.py - Điều phối tra web cho Đại não.

Nhiệm vụ:
    - Nhận yêu cầu tra web.
    - Gọi tim_kiem (xoay API: SERPJET → Tavily → Bright Data).
    - Lấy nội dung trang (nếu cần).
    - Tổng hợp kết quả.
    - Trả về Đại não.

Nguyên tắc:
    - KHÔNG lưu gì vào cây.
    - Chỉ lấy dữ liệu về cho Đại não.
    - Tự xoay API khi hết quota.
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
# ĐIỀU PHỐI TRA WEB
# ================================================================
def dieu_phoi_tra_web(cau_hoi, chu_so_huu="", so_ket_qua=5,
                      lay_noi_dung=False, so_trang_lay=3):
    """
    Điều phối tra web.

    cau_hoi: từ khóa tìm kiếm.
    chu_so_huu: tên đăng nhập (để lấy key).
    so_ket_qua: số kết quả cần lấy.
    lay_noi_dung: có lấy nội dung trang không.
    so_trang_lay: số trang lấy nội dung (nếu lay_noi_dung=True).

    Trả về: {
        thanh_cong: bool,
        ket_qua: [{tieu_de, mo_ta, url}],
        nguon: [str],
        tong_hop: str,
        so_ket_qua: int,
        loi: str?,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "ket_qua": [],
        "nguon": [],
        "tong_hop": "",
        "so_ket_qua": 0,
        "loi": "",
    }

    if not cau_hoi:
        ket_qua["loi"] = "Thiếu câu hỏi."
        return ket_qua

    _ghi_log("tra-web", f"Điều phối tra web: {cau_hoi[:80]}")

    # 1. Tìm kiếm
    try:
        from dai_nao.tra_web.tim_kiem import tim_kiem
        ket_qua_tim = tim_kiem(cau_hoi, chu_so_huu, so_ket_qua)
    except Exception as e:
        ket_qua["loi"] = f"Tìm kiếm lỗi: {e}"
        return ket_qua

    if not ket_qua_tim.get("thanh_cong"):
        ket_qua["loi"] = ket_qua_tim.get("loi", "Tìm kiếm thất bại.")
        return ket_qua

    ket_qua["ket_qua"] = ket_qua_tim.get("ket_qua", [])
    ket_qua["nguon"] = ket_qua_tim.get("nguon", [])
    ket_qua["so_ket_qua"] = len(ket_qua["ket_qua"])

    # 2. Lấy nội dung trang (nếu cần)
    noi_dung_dict = {}
    if lay_noi_dung and ket_qua["ket_qua"]:
        try:
            from dai_nao.tra_web.lay_noi_dung import lay_noi_dung_nhieu
            urls = [item.get("url") for item in ket_qua["ket_qua"] if item.get("url")]
            noi_dung_dict = lay_noi_dung_nhieu(urls, so_trang_lay)
        except Exception as e:
            _ghi_log("loi", f"Lấy nội dung trang lỗi: {e}")

    # 3. Tổng hợp
    try:
        from dai_nao.tra_web.tong_hop import tong_hop_co_noi_dung
        if noi_dung_dict:
            ket_qua["tong_hop"] = tong_hop_co_noi_dung(
                ket_qua["ket_qua"], noi_dung_dict, cau_hoi
            )
        else:
            from dai_nao.tra_web.tong_hop import tong_hop
            ket_qua["tong_hop"] = tong_hop(ket_qua["ket_qua"], cau_hoi)
    except Exception as e:
        _ghi_log("loi", f"Tổng hợp lỗi: {e}")

    ket_qua["thanh_cong"] = True
    _ghi_log("tra-web", f"Tra web OK: {ket_qua['so_ket_qua']} kết quả")

    return ket_qua


# ================================================================
# TRA WEB NHANH
# ================================================================
def tra_web_nhanh(cau_hoi, chu_so_huu="", so_ket_qua=5):
    """Tra web nhanh không lấy nội dung."""
    return dieu_phoi_tra_web(
        cau_hoi, chu_so_huu, so_ket_qua,
        lay_noi_dung=False,
    )


# ================================================================
# TRA WEB CHUYÊN SÂU
# ================================================================
def tra_web_chuyen_sau(cau_hoi, chu_so_huu="", so_ket_qua=5, so_trang_lay=3):
    """Tra web chuyên sâu (có lấy nội dung)."""
    return dieu_phoi_tra_web(
        cau_hoi, chu_so_huu, so_ket_qua,
        lay_noi_dung=True,
        so_trang_lay=so_trang_lay,
    )


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả tra web."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        nguon = ", ".join(ket_qua.get("nguon", []))
        return f"✅ {ket_qua.get('so_ket_qua', 0)} kết quả từ {nguon}"
    return f"❌ Tra web lỗi: {ket_qua.get('loi', '')[:100]}"
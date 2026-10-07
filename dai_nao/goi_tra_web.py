"""
goi_tra_web.py - Cầu nối Đại não → Tra web Rồng Thần.

Nhiệm vụ:
    - goi_tra_web(cau_hoi, chu_so_huu): gọi công cụ Tra web, trả kết quả chuẩn hóa.
    - goi_tim_kiem(cau_hoi, chu_so_huu): gọi module tìm kiếm.
    - goi_lay_noi_dung(url): gọi module lấy nội dung trang.
    - goi_tong_hop(danh_sach, cau_hoi): gọi module tổng hợp.

ĐÃ SỬA:
    - L25: truyền chu_so_huu xuống tim_kiem.
    - L26: _xoay_api truyền đúng chữ ký (chu_so_huu, api_hien_tai),
      trả về TÊN provider (str) thay vì dict.
    - Thêm tham số chu_so_huu cho goi_tra_web và goi_tim_kiem.

Quy tắc:
    - Đây là CẦU NỐI — không tự tìm kiếm.
    - Chuẩn hóa kết quả về format thống nhất.
    - Tự xoay API khi hết quota (SERPJET → Tavily → Bright Data).
    - Không sập khi module Tra web chưa có.

Tầng dữ liệu: Không.
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
# HÀM GỌI MODULE TÌM KIẾM
# ================================================================
def goi_tim_kiem(cau_hoi, chu_so_huu=""):
    """
    Gọi module tìm kiếm trong tra_web/.

    SỬA L25: Truyền chu_so_huu xuống tim_kiem.
    """
    ket_qua = {
        "thanh_cong": False,
        "ket_qua": [],
        "nguon": [],
        "loi": "",
    }

    if not cau_hoi:
        ket_qua["loi"] = "Câu hỏi rỗng."
        return ket_qua

    # Thử module tra_web.tim_kiem trước
    try:
        from tra_web.tim_kiem import tim_kiem
        ket_qua_tho = tim_kiem(cau_hoi, chu_so_huu)
        if ket_qua_tho:
            ket_qua = _chuan_hoa_ket_qua(ket_qua_tho, "tra_web.tim_kiem")
            _ghi_log(
                "tra-web",
                f"Tìm kiếm qua tra_web.tim_kiem: "
                f"{len(ket_qua.get('ket_qua', []))} kết quả",
            )
            return ket_qua
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"tra_web.tim_kiem lỗi: {e}")

    # Thử module tra_web.xoay_api.tim_kiem_xoay_api
    try:
        from tra_web.xoay_api import tim_kiem_xoay_api
        ket_qua_tho = tim_kiem_xoay_api(cau_hoi, chu_so_huu)
        if ket_qua_tho:
            ket_qua = _chuan_hoa_ket_qua(ket_qua_tho, "tra_web.xoay_api")
            return ket_qua
    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"tra_web.xoay_api lỗi: {e}")

    ket_qua["loi"] = "tra_web/tim_kiem.py chưa có hoặc không trả kết quả."
    return ket_qua


# ================================================================
# HÀM GỌI LẤY NỘI DUNG TRANG
# ================================================================
def goi_lay_noi_dung(url):
    """Gọi module lấy nội dung trang web."""
    ket_qua = {"thanh_cong": False, "noi_dung": "", "loi": ""}

    if not url:
        ket_qua["loi"] = "URL rỗng."
        return ket_qua

    try:
        from tra_web.lay_noi_dung import lay_noi_dung
        noi_dung = lay_noi_dung(url)
        if noi_dung:
            ket_qua["thanh_cong"] = True
            ket_qua["noi_dung"] = noi_dung
        else:
            ket_qua["loi"] = "Không lấy được nội dung."
    except ImportError:
        ket_qua["loi"] = "tra_web/lay_noi_dung.py chưa có."
    except Exception as e:
        ket_qua["loi"] = f"Lấy nội dung lỗi: {e}"

    return ket_qua


# ================================================================
# HÀM GỌI TỔNG HỢP
# ================================================================
def goi_tong_hop(danh_sach, cau_hoi=""):
    """
    Gọi module tổng hợp kết quả.

    danh_sach: list [{tieu_de, mo_ta, url}].
    cau_hoi: câu hỏi gốc (để sắp xếp theo độ liên quan).
    """
    if not danh_sach:
        return ""

    try:
        from tra_web.tong_hop import tong_hop
        return tong_hop(danh_sach, cau_hoi) or ""
    except ImportError:
        # Fallback: tổng hợp đơn giản
        return _tong_hop_don_gian(danh_sach)
    except Exception as e:
        _ghi_log("loi", f"Tổng hợp lỗi: {e}")
        return _tong_hop_don_gian(danh_sach)


def _tong_hop_don_gian(danh_sach):
    """Fallback tổng hợp đơn giản nếu module tong_hop không có."""
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


# ================================================================
# CHUẨN HÓA KẾT QUẢ
# ================================================================
def _chuan_hoa_ket_qua(ket_qua_tho, nguon=""):
    """Chuẩn hóa kết quả từ module tìm kiếm về format thống nhất."""
    ket_qua = {
        "thanh_cong": False,
        "ket_qua": [],
        "nguon": [],
        "loi": "",
    }

    if not ket_qua_tho:
        ket_qua["loi"] = "Kết quả rỗng."
        return ket_qua

    if isinstance(ket_qua_tho, str):
        ket_qua["thanh_cong"] = True
        ket_qua["ket_qua"] = [{"tieu_de": "", "mo_ta": ket_qua_tho, "url": ""}]
        ket_qua["nguon"] = [nguon or "tra_web"]
        return ket_qua

    if isinstance(ket_qua_tho, list):
        ket_qua["thanh_cong"] = True
        ket_qua["ket_qua"] = [_chuan_hoa_mot_ket_qua(item) for item in ket_qua_tho]
        ket_qua["nguon"] = [nguon or "tra_web"]
        return ket_qua

    if isinstance(ket_qua_tho, dict):
        ket_qua["thanh_cong"] = bool(ket_qua_tho.get("thanh_cong", True))

        danh_sach = (
            ket_qua_tho.get("ket_qua")
            or ket_qua_tho.get("results")
            or ket_qua_tho.get("data")
            or []
        )
        if isinstance(danh_sach, list):
            ket_qua["ket_qua"] = [_chuan_hoa_mot_ket_qua(item) for item in danh_sach]

        nguon_tho = ket_qua_tho.get("nguon") or ket_qua_tho.get("source") or nguon
        if isinstance(nguon_tho, str):
            ket_qua["nguon"] = [nguon_tho]
        elif isinstance(nguon_tho, list):
            ket_qua["nguon"] = nguon_tho

        ket_qua["loi"] = ket_qua_tho.get("loi", "")
        return ket_qua

    ket_qua["loi"] = "Kết quả không hợp lệ."
    return ket_qua


def _chuan_hoa_mot_ket_qua(item):
    """Chuẩn hóa 1 kết quả về {tieu_de, mo_ta, url}."""
    if isinstance(item, str):
        return {"tieu_de": "", "mo_ta": item, "url": ""}

    if not isinstance(item, dict):
        return {"tieu_de": "", "mo_ta": str(item), "url": ""}

    return {
        "tieu_de": item.get("tieu_de") or item.get("title") or item.get("name") or "",
        "mo_ta": item.get("mo_ta") or item.get("description") or item.get("snippet") or "",
        "url": item.get("url") or item.get("link") or item.get("href") or "",
    }


# ================================================================
# XOAY API KHI HẾT QUOTA
# ================================================================
def _xoay_api(chu_so_huu, api_hien_tai=""):
    """
    Gọi module xoay API trong tra_web/.

    SỬA L26: Truyền đúng chữ ký (chu_so_huu, api_hien_tai).
    Trả về TÊN provider (str) hoặc "".
    """
    try:
        from tra_web.xoay_api import xoay_api
        ket_qua = xoay_api(chu_so_huu, api_hien_tai)
        if not ket_qua:
            return ""
        # xoay_api trả dict api_info → lấy tên provider
        if isinstance(ket_qua, dict):
            return ket_qua.get("provider", "")
        if isinstance(ket_qua, str):
            return ket_qua
        return ""
    except ImportError:
        return ""
    except Exception as e:
        _ghi_log("loi", f"Xoay API lỗi: {e}")
        return ""


def _kiem_tra_het_quota(ket_qua):
    """Kiểm tra kết quả có phải do hết quota không."""
    if not ket_qua:
        return False

    loi = (ket_qua.get("loi") or "").lower()
    tu_khoa_het_quota = [
        "quota", "rate limit", "429", "too many requests",
        "hết lượt", "vượt giới hạn", "insufficient",
    ]
    return any(tk in loi for tk in tu_khoa_het_quota)


# ================================================================
# HÀM CHÍNH
# ================================================================
def goi_tra_web(cau_hoi, chu_so_huu=""):
    """
    Gọi công cụ Tra web, trả kết quả chuẩn hóa.

    cau_hoi: chuỗi câu hỏi.
    chu_so_huu: tên tài khoản (để lấy key tra web).

    SỬA L25: Truyền chu_so_huu xuống goi_tim_kiem.
    SỬA L26: Xoay API dùng chu_so_huu + api_hien_tai.

    Trả về:
    {
        thanh_cong: bool,
        ket_qua: [{tieu_de, mo_ta, url}],
        nguon: [str],
        so_ket_qua: int,
        tom_tat: str,     # Chuỗi tổng hợp sẵn để gán vào tra_loi
        loi: str,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "ket_qua": [],
        "nguon": [],
        "so_ket_qua": 0,
        "tom_tat": "",
        "loi": "",
    }

    if not cau_hoi:
        ket_qua["loi"] = "Câu hỏi rỗng."
        return ket_qua

    thoi_gian_bat_dau = time.time()

    _ghi_log(
        "tra-web",
        f"Gọi Tra web cho {chu_so_huu or 'khach'}: {cau_hoi[:80]}",
    )

    # 1. Gọi tìm kiếm (truyền chu_so_huu)
    ket_qua_tim = goi_tim_kiem(cau_hoi, chu_so_huu)

    # 2. Nếu hết quota → xoay API và thử lại
    if not ket_qua_tim.get("thanh_cong") and _kiem_tra_het_quota(ket_qua_tim):
        _ghi_log("tra-web", "Hết quota — xoay API.")
        api_moi = _xoay_api(chu_so_huu, "")
        if api_moi:
            _ghi_log("tra-web", f"Đã xoay sang API: {api_moi}")
            ket_qua_tim = goi_tim_kiem(cau_hoi, chu_so_huu)

    # 3. Không tìm được → trả lỗi
    if not ket_qua_tim.get("thanh_cong"):
        ket_qua["loi"] = ket_qua_tim.get("loi", "Không tìm được kết quả.")
        ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
        return ket_qua

    # 4. Chuẩn hóa
    danh_sach = ket_qua_tim.get("ket_qua", [])
    ket_qua.update({
        "thanh_cong": True,
        "ket_qua": danh_sach,
        "nguon": ket_qua_tim.get("nguon", []),
        "so_ket_qua": len(danh_sach),
    })

    # 5. Tổng hợp thành chuỗi (để gán vào tra_loi)
    ket_qua["tom_tat"] = goi_tong_hop(danh_sach, cau_hoi)

    ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)

    _ghi_log(
        "tra-web",
        f"Tra web xong: {ket_qua['so_ket_qua']} kết quả, "
        f"{ket_qua['thoi_gian']}s",
    )

    return ket_qua


# ================================================================
# HÀM PHỤ: LẤY NỘI DUNG NHIỀU URL
# ================================================================
def goi_lay_noi_dung_nhieu(urls, so_toi_da=3):
    """Gọi lấy nội dung cho nhiều URL."""
    ket_qua = {}
    if not urls:
        return ket_qua

    for url in urls[:so_toi_da]:
        if not url:
            continue
        ket_qua_url = goi_lay_noi_dung(url)
        if ket_qua_url.get("thanh_cong"):
            ket_qua[url] = ket_qua_url["noi_dung"]

    return ket_qua


# ================================================================
# HÀM PHỤ: TÓM TẮT KẾT QUẢ
# ================================================================
def tom_tat_ket_qua(ket_qua):
    """Tạo chuỗi tóm tắt kết quả tra web."""
    if not ket_qua:
        return ""

    if not ket_qua.get("thanh_cong"):
        return f"❌ Tra web lỗi: {ket_qua.get('loi', 'không rõ')}"

    so = ket_qua.get("so_ket_qua", 0)
    nguon = ", ".join(ket_qua.get("nguon", [])) or "không rõ"
    tg = ket_qua.get("thoi_gian", 0)

    return f"✅ Tra web: {so} kết quả, nguồn={nguon}, {tg}s"


# ================================================================
# HÀM PHỤ: KIỂM TRA TRA WEB SẴN SÀNG
# ================================================================
def tra_web_san_sang():
    """Kiểm tra module Tra web đã sẵn sàng chưa."""
    cac_module = [
        "tra_web.tim_kiem",
        "tra_web.xoay_api",
        "tra_web.lay_noi_dung",
        "tra_web.tong_hop",
    ]
    co_san = []
    for duong_dan in cac_module:
        try:
            __import__(duong_dan)
            co_san.append(duong_dan)
        except ImportError:
            continue
    return co_san


# ================================================================
# HÀM PHỤ: LIỆT KÊ API TRA WEB CÓ SẴN
# ================================================================
def liet_ke_api_tra_web():
    """Liệt kê API tra web có sẵn."""
    cac_api = [
        ("tra_web.api.serpjet", "SERPJET"),
        ("tra_web.api.tavily", "Tavily"),
        ("tra_web.api.brightdata", "Bright Data"),
    ]
    co_san = []
    for duong_dan, ten in cac_api:
        try:
            __import__(duong_dan)
            co_san.append(ten)
        except ImportError:
            continue
    return co_san
"""
tong_hop.py - Tổng hợp kết quả Tra web Rồng Thần.

Nhiệm vụ:
    - tong_hop(danh_sach_ket_qua): tổng hợp kết quả tìm kiếm thành chuỗi.
    - tong_hop_co_noi_dung(danh_sach, noi_dung_dict): tổng hợp + nội dung trang.
    - _loai_trung(danh_sach): loại bỏ URL trùng.
    - _sap_xep_theo_lien_quan(danh_sach, cau_hoi): sắp xếp theo độ liên quan.
    - _tao_tom_tat(danh_sach, so_luong): tạo tóm tắt từ nhiều kết quả.

Quy tắc:
    - Tổng hợp nhiều nguồn thành 1 kết quả dễ đọc.
    - Loại bỏ URL trùng.
    - Sắp xếp theo độ liên quan với câu hỏi.
    - Giới hạn số kết quả trả về.

Trả về:
    - Chuỗi tổng hợp hoặc dict.

Tầng dữ liệu: Không.
"""

import re


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
# HẰNG SỐ
# ================================================================
SO_KET_QUA_TOI_DA = 5
DO_DAI_MO_TA_TOI_DA = 300
DO_DAI_TONG_HOP_TOI_DA = 3000


# ================================================================
# TỔNG HỢP CHÍNH
# ================================================================
def tong_hop(danh_sach_ket_qua, cau_hoi=""):
    """
    Tổng hợp kết quả tìm kiếm thành chuỗi dễ đọc.

    danh_sach_ket_qua: list [{tieu_de, mo_ta, url}].
    cau_hoi: câu hỏi gốc (để sắp xếp theo độ liên quan).

    Trả về: chuỗi tổng hợp.
    """
    if not danh_sach_ket_qua:
        return ""

    # 1. Loại trùng
    danh_sach = _loai_trung(danh_sach_ket_qua)

    # 2. Sắp xếp theo độ liên quan
    if cau_hoi:
        danh_sach = _sap_xep_theo_lien_quan(danh_sach, cau_hoi)

    # 3. Giới hạn số lượng
    danh_sach = danh_sach[:SO_KET_QUA_TOI_DA]

    # 4. Tạo chuỗi
    phan = []
    for i, item in enumerate(danh_sach, 1):
        tieu_de = (item.get("tieu_de") or "").strip()
        mo_ta = (item.get("mo_ta") or "").strip()
        url = (item.get("url") or "").strip()

        if len(mo_ta) > DO_DAI_MO_TA_TOI_DA:
            mo_ta = mo_ta[:DO_DAI_MO_TA_TOI_DA].rstrip() + "..."

        dong = f"{i}. {tieu_de}" if tieu_de else f"{i}."
        if mo_ta:
            dong += f"\n   {mo_ta}"
        if url:
            dong += f"\n   🔗 {url}"

        phan.append(dong)

    ket_qua = "\n\n".join(phan)

    # 5. Giới hạn tổng
    if len(ket_qua) > DO_DAI_TONG_HOP_TOI_DA:
        ket_qua = ket_qua[:DO_DAI_TONG_HOP_TOI_DA] + "\n\n..."

    return ket_qua


# ================================================================
# TỔNG HỢP CÓ NỘI DUNG TRANG
# ================================================================
def tong_hop_co_noi_dung(danh_sach_ket_qua, noi_dung_dict=None, cau_hoi=""):
    """
    Tổng hợp + thêm nội dung trang (nếu có).

    danh_sach_ket_qua: list [{tieu_de, mo_ta, url}].
    noi_dung_dict: { url: noi_dung }.
    cau_hoi: câu hỏi gốc.

    Trả về: chuỗi tổng hợp.
    """
    if not danh_sach_ket_qua:
        return ""

    noi_dung_dict = noi_dung_dict or {}

    # Loại trùng
    danh_sach = _loai_trung(danh_sach_ket_qua)

    # Sắp xếp
    if cau_hoi:
        danh_sach = _sap_xep_theo_lien_quan(danh_sach, cau_hoi)

    danh_sach = danh_sach[:SO_KET_QUA_TOI_DA]

    phan = []
    for i, item in enumerate(danh_sach, 1):
        tieu_de = (item.get("tieu_de") or "").strip()
        mo_ta = (item.get("mo_ta") or "").strip()
        url = (item.get("url") or "").strip()

        # Ưu tiên nội dung trang nếu có
        noi_dung = noi_dung_dict.get(url, "")
        if noi_dung:
            mo_ta = noi_dung[:DO_DAI_MO_TA_TOI_DA * 2]
        elif len(mo_ta) > DO_DAI_MO_TA_TOI_DA:
            mo_ta = mo_ta[:DO_DAI_MO_TA_TOI_DA].rstrip() + "..."

        dong = f"{i}. {tieu_de}" if tieu_de else f"{i}."
        if mo_ta:
            dong += f"\n   {mo_ta}"
        if url:
            dong += f"\n   🔗 {url}"

        phan.append(dong)

    ket_qua = "\n\n".join(phan)

    if len(ket_qua) > DO_DAI_TONG_HOP_TOI_DA:
        ket_qua = ket_qua[:DO_DAI_TONG_HOP_TOI_DA] + "\n\n..."

    return ket_qua


# ================================================================
# LOẠI TRÙNG
# ================================================================
def _loai_trung(danh_sach):
    """
    Loại bỏ kết quả có URL trùng.
    Giữ kết quả có mô tả dài hơn.
    """
    if not danh_sach:
        return []

    ban_do = {}  # url → item

    for item in danh_sach:
        if not isinstance(item, dict):
            continue

        url = (item.get("url") or "").strip()

        if not url:
            # Không có URL → dùng tieu_de làm khóa
            khoa = (item.get("tieu_de") or "")[:100]
        else:
            # Chuẩn hóa URL (bỏ trailing slash, query)
            khoa = _chuan_hoa_url(url)

        if not khoa:
            continue

        if khoa in ban_do:
            # Giữ item có mô tả dài hơn
            cu = ban_do[khoa]
            if len(item.get("mo_ta") or "") > len(cu.get("mo_ta") or ""):
                ban_do[khoa] = item
        else:
            ban_do[khoa] = item

    return list(ban_do.values())


def _chuan_hoa_url(url):
    """Chuẩn hóa URL để so sánh."""
    if not url:
        return ""

    # Bỏ query string
    url = url.split("?")[0]
    # Bỏ trailing slash
    url = url.rstrip("/")
    # Bỏ www.
    url = re.sub(r"^https?://(www\.)?", "https://", url)
    return url.lower()


# ================================================================
# SẮP XẾP THEO ĐỘ LIÊN QUAN
# ================================================================
def _sap_xep_theo_lien_quan(danh_sach, cau_hoi):
    """
    Sắp xếp theo độ liên quan với câu hỏi:
        - Từ khóa trong tiêu đề: +3 điểm.
        - Từ khóa trong mô tả: +1 điểm.
        - URL có từ khóa: +2 điểm.
    """
    if not danh_sach or not cau_hoi:
        return danh_sach

    # Trích từ khóa từ câu hỏi
    tu_khoa = _trich_tu_khoa(cau_hoi)
    if not tu_khoa:
        return danh_sach

    def diem(item):
        tieu_de = (item.get("tieu_de") or "").lower()
        mo_ta = (item.get("mo_ta") or "").lower()
        url = (item.get("url") or "").lower()

        d = 0
        for tk in tu_khoa:
            if tk in tieu_de:
                d += 3
            if tk in mo_ta:
                d += 1
            if tk in url:
                d += 2

        return -d  # Sắp xếp giảm dần

    try:
        return sorted(danh_sach, key=diem)
    except Exception:
        return danh_sach


def _trich_tu_khoa(cau_hoi):
    """Trích từ khóa từ câu hỏi (bỏ từ đệm, từ ngắn)."""
    if not cau_hoi:
        return []

    tu_dem = {
        "là", "gì", "của", "và", "có", "cho", "với", "thì",
        "một", "các", "những", "này", "đó", "kia", "được",
        "không", "như", "thế", "nào", "khi", "tại", "sao",
        "ai", "ở", "đâu", "bao", "nhiêu", "cách", "hãy",
        "cho", "tôi", "mình", "bạn", "về", "trong",
    }

    tu = re.findall(r"\b[a-zA-Zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]{3,}\b", cau_hoi.lower())

    ket_qua = []
    for t in tu:
        if t not in tu_dem and t not in ket_qua:
            ket_qua.append(t)

    return ket_qua[:10]


# ================================================================
# TẠO TÓM TẮT
# ================================================================
def _tao_tom_tat(danh_sach, so_luong=3):
    """Tạo tóm tắt ngắn từ nhiều kết quả."""
    if not danh_sach:
        return ""

    phan = []
    for i, item in enumerate(danh_sach[:so_luong], 1):
        mo_ta = (item.get("mo_ta") or "").strip()
        if mo_ta:
            phan.append(mo_ta[:150])

    return "\n".join(phan)


# ================================================================
# HÀM PHỤ: TỔNG HỢP DẠNG DICT
# ================================================================
def tong_hop_dict(danh_sach_ket_qua, cau_hoi=""):
    """
    Tổng hợp thành dict có cấu trúc.

    Trả về:
        {
            tong: int,
            ket_qua: [...],
            tom_tat: str,
            nguon: [str],
        }
    """
    if not danh_sach_ket_qua:
        return {"tong": 0, "ket_qua": [], "tom_tat": "", "nguon": []}

    danh_sach = _loai_trung(danh_sach_ket_qua)
    if cau_hoi:
        danh_sach = _sap_xep_theo_lien_quan(danh_sach, cau_hoi)

    danh_sach = danh_sach[:SO_KET_QUA_TOI_DA]

    nguon = list(set([item.get("url", "").split("/")[2] for item in danh_sach if item.get("url") and "/" in item.get("url")]))

    return {
        "tong": len(danh_sach),
        "ket_qua": danh_sach,
        "tom_tat": _tao_tom_tat(danh_sach),
        "nguon": nguon[:5],
    }


# ================================================================
# HÀM PHỤ: GỘP MÔ TẢ
# ================================================================
def gop_mo_ta(danh_sach, so_luong=3):
    """Gộp mô tả của nhiều kết quả thành 1 chuỗi."""
    if not danh_sach:
        return ""

    phan = []
    for item in danh_sach[:so_luong]:
        mo_ta = (item.get("mo_ta") or "").strip()
        if mo_ta:
            phan.append(mo_ta)

    return "\n\n".join(phan)


# ================================================================
# HÀM PHỤ: ĐẾM URL DUY NHẤT
# ================================================================
def dem_url_duy_nhat(danh_sach):
    """Đếm số URL duy nhất trong danh sách."""
    if not danh_sach:
        return 0

    da_gap = set()
    for item in danh_sach:
        url = _chuan_hoa_url(item.get("url", ""))
        if url:
            da_gap.add(url)

    return len(da_gap)


# ================================================================
# HÀM PHỤ: LỌC KẾT QUẢ CHẤT LƯỢNG
# ================================================================
def loc_chat_luong(danh_sach, do_dai_mo_ta_toi_thieu=50):
    """Lọc kết quả có mô tả đủ dài."""
    if not danh_sach:
        return []

    return [
        item for item in danh_sach
        if len((item.get("mo_ta") or "").strip()) >= do_dai_mo_ta_toi_thieu
    ]


# ================================================================
# HÀM PHỤ: TÓM TẮT NGẮN
# ================================================================
def tom_tat_ngan(danh_sach, so_ky_tu=500):
    """Tạo tóm tắt siêu ngắn."""
    if not danh_sach:
        return ""

    ket_qua = tong_hop(danh_sach)
    if len(ket_qua) <= so_ky_tu:
        return ket_qua

    return ket_qua[:so_ky_tu].rstrip() + "..."
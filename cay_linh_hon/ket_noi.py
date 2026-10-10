"""
ket_noi.py - Cầu nối giữa Đại não ↔ Boss ↔ Tiểu não ↔ Model.

Nhiệm vụ:
    - Chuẩn bị dữ liệu để Đại não gọi Boss.
    - Chuẩn bị dữ liệu để Boss gọi Model.
    - Cập nhật cây linh hồn sau khi Model xong.
    - Xử lý sự kiện: bắt đầu, kết thúc bước, lỗi.

Nguyên tắc:
    - Đây là cầu nối — không chứa logic nghiệp vụ.
    - Chỉ đọc / ghi cây linh hồn + chuẩn bị data.
"""

import time


# ================================================================
# CHUẨN BỊ DATA CHO BOSS
# ================================================================
def chuan_bi_data_cho_boss(chu_so_huu, id_chat):
    """
    Chuẩn bị dữ liệu để Đại não gửi cho Boss.

    Trả về: dict {hop_dong, huong_dan, tien_do, ke_hoach}.
    """
    from cay_linh_hon.hop_dong import doc_hop_dong
    from cay_linh_hon.huong_dan import doc_huong_dan
    from cay_linh_hon.tien_do import doc_tien_do
    from cay_linh_hon.ke_hoach import doc_ke_hoach

    return {
        "hop_dong": doc_hop_dong(chu_so_huu, id_chat),
        "huong_dan": doc_huong_dan(chu_so_huu, id_chat),
        "tien_do": doc_tien_do(chu_so_huu, id_chat),
        "ke_hoach": doc_ke_hoach(chu_so_huu, id_chat),
    }


# ================================================================
# CHUẨN BỊ DATA CHO MODEL
# ================================================================
def chuan_bi_data_cho_model(chu_so_huu, id_chat, buoc):
    """
    Chuẩn bị dữ liệu để Boss gửi cho Model.

    Trả về: dict {hop_dong, huong_dan, code_cu}.
    """
    from cay_linh_hon.hop_dong import doc_hop_dong
    from cay_linh_hon.huong_dan import doc_huong_dan
    from cay_linh_hon.luu_code import doc_code

    return {
        "hop_dong": doc_hop_dong(chu_so_huu, id_chat),
        "huong_dan": doc_huong_dan(chu_so_huu, id_chat),
        "code_cu": doc_code(chu_so_huu, id_chat, buoc),
    }


# ================================================================
# SỰ KIỆN: BẮT ĐẦU DỰ ÁN
# ================================================================
def su_kien_bat_dau(chu_so_huu, id_chat, dang_lam_gi, tong_buoc=0):
    """
    Sự kiện bắt đầu dự án — tạo hợp đồng + tiến độ.

    Trả về: True/False.
    """
    from cay_linh_hon.hop_dong import ghi_hop_dong
    from cay_linh_hon.tien_do import tao_tien_do

    ok1 = ghi_hop_dong(
        chu_so_huu, id_chat,
        dang_lam_gi=dang_lam_gi,
        dang_lam_toi_dau="0/" + str(tong_buoc),
        tiep_theo_lam_gi="Bước 1",
    )

    ok2 = tao_tien_do(chu_so_huu, id_chat, tong_buoc)

    return ok1 and ok2


# ================================================================
# SỰ KIỆN: KẾT THÚC BƯỚC
# ================================================================
def su_kien_ket_thuc_buoc(chu_so_huu, id_chat, buoc,
                          ten_buoc, tiep_theo=""):
    """
    Sự kiện kết thúc 1 bước — cập nhật hợp đồng + tiến độ.

    Trả về: True/False.
    """
    from cay_linh_hon.hop_dong import cap_nhat_hop_dong
    from cay_linh_hon.tien_do import them_buoc, tang_buoc, doc_tien_do

    # Cập nhật tiến độ
    them_buoc(chu_so_huu, id_chat, ten_buoc, "xong")
    tang_buoc(chu_so_huu, id_chat)

    # Cập nhật hợp đồng
    tien_do = doc_tien_do(chu_so_huu, id_chat)
    buoc_moi = tien_do.get("buoc_hien_tai", 0) if tien_do else 0
    tong = tien_do.get("tong_buoc", 0) if tien_do else 0

    cap_nhat_hop_dong(
        chu_so_huu, id_chat,
        dang_lam_toi_dau=f"{buoc_moi}/{tong}",
        tiep_theo_lam_gi=tiep_theo or f"Bước {buoc_moi + 1}",
    )

    return True


# ================================================================
# SỰ KIỆN: LỖI
# ================================================================
def su_kien_loi(chu_so_huu, id_chat, buoc, loai_loi,
                thong_diep, cach_sua=""):
    """
    Sự kiện lỗi — lưu lỗi + cập nhật hướng dẫn.

    Trả về: True/False.
    """
    from cay_linh_hon.luu_loi import luu_loi_va_cach_sua

    return luu_loi_va_cach_sua(
        chu_so_huu, id_chat, buoc,
        loai_loi, thong_diep, cach_sua,
    )


# ================================================================
# SỰ KIỆN: USER ĐỔI Ý
# ================================================================
def su_kien_doi_y(chu_so_huu, id_chat, muc_do, mo_ta_moi):
    """
    Sự kiện user đổi ý.

    muc_do: "nho" | "vua" | "lon".
        - nho: thêm bước.
        - vua: sửa hợp đồng 1 phần.
        - lon: hợp đồng mới.

    Trả về: True/False.
    """
    from cay_linh_hon.hop_dong import cap_nhat_hop_dong

    if muc_do == "nho":
        cap_nhat_hop_dong(
            chu_so_huu, id_chat,
            tiep_theo_lam_gi=mo_ta_moi,
        )
        return True

    if muc_do == "vua":
        cap_nhat_hop_dong(
            chu_so_huu, id_chat,
            dang_lam_gi=mo_ta_moi,
        )
        return True

    if muc_do == "lon":
        cap_nhat_hop_dong(
            chu_so_huu, id_chat,
            dang_lam_gi=mo_ta_moi,
            dang_lam_toi_dau="0/N",
            tiep_theo_lam_gi="Bước 1",
        )
        return True

    return False


# ================================================================
# LẤY TRẠNG THÁI TỔNG
# ================================================================
def lay_trang_thai_tong(chu_so_huu, id_chat):
    """
    Lấy trạng thái tổng của 1 chat.

    Trả về: dict.
    """
    from cay_linh_hon.hop_dong import doc_hop_dong
    from cay_linh_hon.tien_do import doc_tien_do, phan_tram_hoan_thanh
    from cay_linh_hon.luu_code import dem_file_da_viet

    hop_dong = doc_hop_dong(chu_so_huu, id_chat) or {}
    tien_do = doc_tien_do(chu_so_huu, id_chat) or {}

    return {
        "id_chat": id_chat,
        "dang_lam_gi": hop_dong.get("dang_lam_gi", ""),
        "dang_lam_toi_dau": hop_dong.get("dang_lam_toi_dau", ""),
        "tiep_theo_lam_gi": hop_dong.get("tiep_theo_lam_gi", ""),
        "buoc_hien_tai": tien_do.get("buoc_hien_tai", 0),
        "tong_buoc": tien_do.get("tong_buoc", 0),
        "trang_thai": tien_do.get("trang_thai", ""),
        "phan_tram": phan_tram_hoan_thanh(chu_so_huu, id_chat),
        "so_file": dem_file_da_viet(chu_so_huu, id_chat),
    }
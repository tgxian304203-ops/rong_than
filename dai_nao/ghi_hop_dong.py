"""
ghi_hop_dong.py - Ghi / cập nhật hợp đồng vào Cây linh hồn.

Nhiệm vụ:
    - Ghi hợp đồng lần đầu (khi Boss đầu lập kế hoạch).
    - Cập nhật hợp đồng sau mỗi sự kiện.
    - Chuẩn hóa dữ liệu trước khi ghi.

Nguyên tắc:
    - Đại não là bên ghi/cập nhật.
    - Cập nhật LIÊN TỤC sau mỗi sự kiện.
    - Ghi vào kho 2 (Cây linh hồn) qua cay_linh_hon/hop_dong.py.
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
# GHI HỢP ĐỒNG MỚI
# ================================================================
def ghi_hop_dong_moi(chu_so_huu, id_chat,
                     dang_lam_gi="", dang_lam_toi_dau="",
                     tiep_theo_lam_gi=""):
    """
    Ghi hợp đồng mới cho 1 chat.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat:
        return False

    try:
        from cay_linh_hon.hop_dong import ghi_hop_dong

        ket_qua = ghi_hop_dong(
            chu_so_huu, id_chat,
            dang_lam_gi=dang_lam_gi,
            dang_lam_toi_dau=dang_lam_toi_dau,
            tiep_theo_lam_gi=tiep_theo_lam_gi,
        )

        if ket_qua:
            _ghi_log("dai-nao", f"Ghi hợp đồng: {dang_lam_gi[:80]}")

        return ket_qua
    except Exception as e:
        _ghi_log("loi", f"Ghi hợp đồng lỗi: {e}")
        return False


# ================================================================
# CẬP NHẬT HỢP ĐỒNG
# ================================================================
def cap_nhat_hop_dong(chu_so_huu, id_chat,
                      dang_lam_gi=None, dang_lam_toi_dau=None,
                      tiep_theo_lam_gi=None):
    """
    Cập nhật hợp đồng sau mỗi sự kiện.

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat:
        return False

    try:
        from cay_linh_hon.hop_dong import cap_nhat_hop_dong as _cap_nhat
        return _cap_nhat(
            chu_so_huu, id_chat,
            dang_lam_gi=dang_lam_gi,
            dang_lam_toi_dau=dang_lam_toi_dau,
            tiep_theo_lam_gi=tiep_theo_lam_gi,
        )
    except Exception as e:
        _ghi_log("loi", f"Cập nhật hợp đồng lỗi: {e}")
        return False


# ================================================================
# GHI HỢP ĐỒNG TỪ KẾ HOẠCH BOSS
# ================================================================
def ghi_tu_ke_hoach(chu_so_huu, id_chat, ke_hoach_boss):
    """
    Ghi hợp đồng từ kế hoạch do Boss tạo.

    ke_hoach_boss: {
        dang_lam_gi, dang_lam_toi_dau, tiep_theo_lam_gi,
        danh_sach_buoc (list),
        huong_dan (str),
    }

    Trả về: True/False.
    """
    if not chu_so_huu or not id_chat or not ke_hoach_boss:
        return False

    try:
        from cay_linh_hon.hop_dong import ghi_hop_dong
        from cay_linh_hon.huong_dan import ghi_huong_dan
        from cay_linh_hon.ke_hoach import tao_ke_hoach
        from cay_linh_hon.tien_do import tao_tien_do

        # 1. Ghi hợp đồng
        ghi_hop_dong(
            chu_so_huu, id_chat,
            dang_lam_gi=ke_hoach_boss.get("dang_lam_gi", ""),
            dang_lam_toi_dau=ke_hoach_boss.get("dang_lam_toi_dau", "0/N"),
            tiep_theo_lam_gi=ke_hoach_boss.get("tiep_theo_lam_gi", ""),
        )

        # 2. Ghi hướng dẫn
        huong_dan = ke_hoach_boss.get("huong_dan", "")
        if huong_dan:
            ghi_huong_dan(chu_so_huu, id_chat, nen_lam_gi=huong_dan)

        # 3. Tạo kế hoạch
        danh_sach_buoc = ke_hoach_boss.get("danh_sach_buoc", [])
        if danh_sach_buoc:
            tao_ke_hoach(chu_so_huu, id_chat, danh_sach_buoc)

        # 4. Tạo tiến độ
        tao_tien_do(chu_so_huu, id_chat, len(danh_sach_buoc))

        _ghi_log("dai-nao", f"Ghi hợp đồng từ kế hoạch Boss ({len(danh_sach_buoc)} bước)")
        return True
    except Exception as e:
        _ghi_log("loi", f"Ghi hợp đồng từ kế hoạch lỗi: {e}")
        return False


# ================================================================
# ĐỌC HỢP ĐỒNG
# ================================================================
def doc_hop_dong(chu_so_huu, id_chat):
    """Đọc hợp đồng hiện tại."""
    try:
        from cay_linh_hon.hop_dong import doc_hop_dong as _doc
        return _doc(chu_so_huu, id_chat)
    except Exception:
        return None


# ================================================================
# TÓM TẮT HỢP ĐỒNG
# ================================================================
def tom_tat_hop_dong(chu_so_huu, id_chat):
    """Trả chuỗi tóm tắt hợp đồng."""
    try:
        from cay_linh_hon.hop_dong import tom_tat_hop_dong as _tom_tat
        return _tom_tat(chu_so_huu, id_chat)
    except Exception:
        return ""
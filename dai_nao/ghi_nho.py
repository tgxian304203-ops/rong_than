

# ================================================================
# NHÓM 12: TRÒ CHUYỆN TRONG DỰ ÁN (BỔ SUNG)
# ================================================================
def luu_tro_chuyen(tro_chuyen):
    """Lưu 1 trò chuyện vào collection tro_chuyen trong kho 1."""
    if not tro_chuyen or not tro_chuyen.get("id"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db["tro_chuyen"].insert_one(dict(tro_chuyen))
        return True
    except Exception:
        return False


def lay_danh_sach_tro_chuyen_cua(id_du_an, ten_tk):
    """Lấy danh sách trò chuyện của 1 dự án của 1 tài khoản."""
    if not id_du_an or not ten_tk:
        return []
    db, _ = _ket_noi_kho_1()
    ket_qua = db["tro_chuyen"].find(
        {"id_du_an": id_du_an, "chu_so_huu": ten_tk}
    ).sort("ngay_tao", DESCENDING)
    return [_chuan_hoa_doc(t) for t in ket_qua]


def lay_tro_chuyen(id_tro_chuyen):
    """Lấy 1 trò chuyện theo id."""
    if not id_tro_chuyen:
        return None
    db, _ = _ket_noi_kho_1()
    ket_qua = db["tro_chuyen"].find_one({"id": id_tro_chuyen})
    return _chuan_hoa_doc(ket_qua) if ket_qua else None


def xoa_tro_chuyen_theo_id(id_tro_chuyen, ten_tk):
    """
    Xóa 1 trò chuyện — CHỈ khi đúng chủ sở hữu.
    Đồng thời xóa mọi tin nhắn thuộc trò chuyện đó.
    """
    if not id_tro_chuyen or not ten_tk:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        # Xóa tin nhắn trước
        db[C_LICH_SU_CHAT].delete_many({
            "id_tro_chuyen": id_tro_chuyen,
            "chu_so_huu": ten_tk,
        })
        # Xóa trò chuyện
        ket_qua = db["tro_chuyen"].delete_one({
            "id": id_tro_chuyen,
            "chu_so_huu": ten_tk,
        })
        return ket_qua.deleted_count > 0
    except Exception:
        return False


def luu_tin_nhan_tro_chuyen(tin_nhan):
    """Lưu 1 tin nhắn trong trò chuyện."""
    if not tin_nhan or not tin_nhan.get("id"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_LICH_SU_CHAT].insert_one(dict(tin_nhan))
        return True
    except Exception:
        return False


def lay_tin_nhan_tro_chuyen_cua(id_du_an, id_tro_chuyen, ten_tk):
    """Lấy tin nhắn của 1 trò chuyện trong dự án."""
    if not id_du_an or not id_tro_chuyen or not ten_tk:
        return []
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_LICH_SU_CHAT].find({
        "id_du_an": id_du_an,
        "id_tro_chuyen": id_tro_chuyen,
        "chu_so_huu": ten_tk,
    }).sort("thoi_gian", ASCENDING)
    return [_chuan_hoa_doc(t) for t in ket_qua]
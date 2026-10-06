"""
quan_ly_loi.py - Quản lý lỗi model Rồng Thần.

Nhiệm vụ:
    - ghi_loi_model(provider, model, loi): ghi 1 lần lỗi.
    - kiem_tra_blacklist(provider, model): kiểm tra model có bị blacklist không.
    - blacklist_model(provider, model): đưa model vào blacklist.
    - xoa_blacklist(provider, model): xóa model khỏi blacklist.
    - lay_danh_sach_blacklist(): lấy toàn bộ model bị blacklist.
    - loc_model_bi_blacklist(danh_sach, provider): lọc bỏ model bị blacklist.

Quy tắc (theo Phần 4):
    - Model lỗi 3 lần → blacklist.
    - Blacklist vĩnh viễn (hoặc đến khi xóa thủ công).
    - Phân loại lỗi: key_sai, het_quota, model_chet, timeout, khac.
    - Lỗi key_sai/het_quota không tính vào blacklist model.
    - Lỗi model_chet → blacklist ngay (không cần đợi 3 lần).

Tầng dữ liệu: dai_nao/ghi_nho.py (kho 2)
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
# HẰNG SỐ
# ================================================================
SO_LAN_LOI_BLACKLIST = 3

LOAI_LOI_KHONG_TINH_BLACKLIST = [
    "key_sai",
    "het_quota",
]

LOAI_LOI_BLACKLIST_NGAY = [
    "model_chet",
]


# ================================================================
# ĐỌC / GHI KHO 2
# ================================================================
def _collection_blacklist():
    """Lấy collection blacklist từ kho 2."""
    try:
        from dai_nao.ghi_nho import _ket_noi_kho_2
        db = _ket_noi_kho_2()
        return db["model_blacklist"]
    except Exception:
        return None


# ================================================================
# GHI LỖI MODEL
# ================================================================
def ghi_loi_model(provider, model, loi="", loai_loi="khac"):
    """
    Ghi 1 lần lỗi của model.

    provider: "Groq" | "OpenRouter" | "Gemini".
    model: tên model.
    loi: mô tả lỗi.
    loai_loi: "key_sai" | "het_quota" | "model_chet" | "timeout" | "khac".

    Trả về: True nếu ghi thành công.
    """
    if not provider or not model:
        return False

    col = _collection_blacklist()
    if col is None:
        return False

    # Lỗi key_sai / het_quota không tính vào model
    if loai_loi in LOAI_LOI_KHONG_TINH_BLACKLIST:
        _ghi_log("tieu-nao", f"Bỏ qua lỗi {loai_loi} của {provider}/{model}")
        return False

    try:
        # Kiểm tra model đã có trong blacklist chưa
        hien_tai = col.find_one({"provider": provider, "model": model})
        so_lan_loi = (hien_tai.get("so_lan_loi", 0) if hien_tai else 0) + 1

        # Lỗi model_chet → blacklist ngay
        blacklist = loai_loi in LOAI_LOI_BLACKLIST_NGAY

        # Lỗi khác → đủ 3 lần → blacklist
        if so_lan_loi >= SO_LAN_LOI_BLACKLIST:
            blacklist = True

        col.update_one(
            {"provider": provider, "model": model},
            {
                "$set": {
                    "provider": provider,
                    "model": model,
                    "so_lan_loi": so_lan_loi,
                    "loi_cuoi": loi[:500],
                    "loai_loi_cuoi": loai_loi,
                    "blacklist": blacklist,
                    "thoi_gian_cuoi": int(time.time()),
                }
            },
            upsert=True,
        )

        if blacklist:
            _ghi_log(
                "tieu-nao",
                f"Blacklist {provider}/{model} (lỗi {so_lan_loi} lần, "
                f"loại {loai_loi}).",
            )

        return True
    except Exception as e:
        _ghi_log("loi", f"Ghi lỗi model lỗi: {e}")
        return False


# ================================================================
# KIỂM TRA BLACKLIST
# ================================================================
def kiem_tra_blacklist(provider, model):
    """
    Kiểm tra model có bị blacklist không.

    Trả về: True nếu bị blacklist.
    """
    if not provider or not model:
        return False

    col = _collection_blacklist()
    if col is None:
        return False

    try:
        ket_qua = col.find_one({"provider": provider, "model": model})
        if ket_qua and ket_qua.get("blacklist"):
            return True
    except Exception:
        pass

    return False


# ================================================================
# BLACKLIST THỦ CÔNG
# ================================================================
def blacklist_model(provider, model, ly_do="Thủ công"):
    """Đưa model vào blacklist (thủ công)."""
    if not provider or not model:
        return False

    col = _collection_blacklist()
    if col is None:
        return False

    try:
        col.update_one(
            {"provider": provider, "model": model},
            {
                "$set": {
                    "provider": provider,
                    "model": model,
                    "blacklist": True,
                    "ly_do": ly_do,
                    "thoi_gian_blacklist": int(time.time()),
                }
            },
            upsert=True,
        )
        _ghi_log("tieu-nao", f"Blacklist {provider}/{model}: {ly_do}")
        return True
    except Exception:
        return False


# ================================================================
# XÓA BLACKLIST
# ================================================================
def xoa_blacklist(provider, model):
    """Xóa model khỏi blacklist."""
    if not provider or not model:
        return False

    col = _collection_blacklist()
    if col is None:
        return False

    try:
        col.update_one(
            {"provider": provider, "model": model},
            {
                "$set": {
                    "blacklist": False,
                    "so_lan_loi": 0,
                    "thoi_gian_xoa": int(time.time()),
                }
            },
        )
        _ghi_log("tieu-nao", f"Xóa blacklist {provider}/{model}")
        return True
    except Exception:
        return False


def xoa_tat_ca_blacklist(provider=None):
    """Xóa toàn bộ blacklist (hoặc theo provider)."""
    col = _collection_blacklist()
    if col is None:
        return False

    try:
        dieu_kien = {"blacklist": True}
        if provider:
            dieu_kien["provider"] = provider

        ket_qua = col.update_many(
            dieu_kien,
            {"$set": {"blacklist": False, "so_lan_loi": 0}},
        )
        _ghi_log("tieu-nao", f"Xóa blacklist: {ket_qua.modified_count} model.")
        return True
    except Exception:
        return False


# ================================================================
# LẤY DANH SÁCH BLACKLIST
# ================================================================
def lay_danh_sach_blacklist(provider=None):
    """Lấy danh sách model bị blacklist."""
    col = _collection_blacklist()
    if col is None:
        return []

    try:
        dieu_kien = {"blacklist": True}
        if provider:
            dieu_kien["provider"] = provider

        return list(col.find(dieu_kien))
    except Exception:
        return []


def lay_danh_sach_loi(provider=None, chi_blacklist=False):
    """Lấy danh sách tất cả model có lỗi (không chỉ blacklist)."""
    col = _collection_blacklist()
    if col is None:
        return []

    try:
        dieu_kien = {}
        if provider:
            dieu_kien["provider"] = provider
        if chi_blacklist:
            dieu_kien["blacklist"] = True

        return list(col.find(dieu_kien))
    except Exception:
        return []


# ================================================================
# LỌC MODEL BỊ BLACKLIST
# ================================================================
def loc_model_bi_blacklist(danh_sach_model, provider):
    """
    Lọc bỏ model bị blacklist khỏi danh sách.

    danh_sach_model: list tên model.
    provider: tên provider.

    Trả về: list model không bị blacklist.
    """
    if not danh_sach_model or not provider:
        return list(danh_sach_model) if danh_sach_model else []

    ket_qua = []
    for model in danh_sach_model:
        if not kiem_tra_blacklist(provider, model):
            ket_qua.append(model)

    return ket_qua


# ================================================================
# HÀM PHỤ: ĐẾM BLACKLIST
# ================================================================
def dem_blacklist(provider=None):
    """Đếm số model bị blacklist."""
    return len(lay_danh_sach_blacklist(provider))


def dem_model_co_loi(provider=None):
    """Đếm số model có ghi nhận lỗi."""
    return len(lay_danh_sach_loi(provider))


# ================================================================
# HÀM PHỤ: XÓA LỖI CỦA MODEL
# ================================================================
def xoa_loi_model(provider, model):
    """Xóa toàn bộ ghi nhận lỗi của model."""
    if not provider or not model:
        return False

    col = _collection_blacklist()
    if col is None:
        return False

    try:
        col.delete_one({"provider": provider, "model": model})
        _ghi_log("tieu-nao", f"Xóa lỗi {provider}/{model}")
        return True
    except Exception:
        return False


# ================================================================
# HÀM PHỤ: XỬ LÝ LỖI TỪ KẾT QUẢ GỌI MODEL
# ================================================================
def xu_ly_loi_tu_ket_qua(key_info, ket_qua_goi):
    """
    Xử lý lỗi từ kết quả gọi model.
    Tự động ghi lỗi + blacklist nếu cần.

    key_info: dict { id, key, provider, ... }.
    ket_qua_goi: dict { thanh_cong, loi, loai_loi }.

    Trả về: hành động: "chuyen_key" | "chuyen_model" | "thu_lai" | "ok".
    """
    if not key_info or not ket_qua_goi:
        return "ok"

    if ket_qua_goi.get("thanh_cong"):
        return "ok"

    provider = key_info.get("provider", "")
    model = key_info.get("model", "") or ket_qua_goi.get("model", "")
    loi = ket_qua_goi.get("loi", "")
    loai_loi = ket_qua_goi.get("loai_loi", "khac")

    # Ghi lỗi
    if provider and model:
        ghi_loi_model(provider, model, loi, loai_loi)

    # Quyết định hành động
    if loai_loi in ("key_sai", "het_quota"):
        return "chuyen_key"
    if loai_loi == "model_chet":
        return "chuyen_model"
    return "thu_lai"


# ================================================================
# HÀM PHỤ: TÓM TẮT BLACKLIST
# ================================================================
def tom_tat_blacklist(provider=None):
    """Tạo chuỗi tóm tắt blacklist."""
    danh_sach = lay_danh_sach_blacklist(provider)
    if not danh_sach:
        return "✅ Không có model nào bị blacklist."

    phan = [f"⚫ {len(danh_sach)} model bị blacklist:"]
    for item in danh_sach[:20]:
        phan.append(
            f"  - {item.get('provider')}/{item.get('model')} "
            f"(lỗi {item.get('so_lan_loi', 0)} lần)"
        )

    return "\n".join(phan)


# ================================================================
# HÀM PHỤ: DỌN DẸP BLACKLIST CŨ
# ================================================================
def don_dep_blacklist(ngay=30):
    """
    Xóa blacklist cũ hơn N ngày (mặc định 30 ngày).
    Model có thể đã hoạt động trở lại.
    """
    col = _collection_blacklist()
    if col is None:
        return 0

    nguong = int(time.time()) - ngay * 24 * 3600
    try:
        ket_qua = col.update_many(
            {
                "blacklist": True,
                "thoi_gian_blacklist": {"$lt": nguong},
            },
            {"$set": {"blacklist": False, "so_lan_loi": 0}},
        )
        _ghi_log("tieu-nao", f"Dọn blacklist cũ: {ket_qua.modified_count} model.")
        return ket_qua.modified_count
    except Exception:
        return 0


# ================================================================
# HÀM PHỤ: THỐNG KÊ LỖI THEO PROVIDER
# ================================================================
def thong_ke_loi_theo_provider():
    """Thống kê số model bị lỗi theo provider."""
    ket_qua = {"Groq": 0, "OpenRouter": 0, "Gemini": 0}

    danh_sach = lay_danh_sach_loi()
    for item in danh_sach:
        p = item.get("provider", "")
        if p in ket_qua:
            ket_qua[p] += 1

    return ket_qua


# ================================================================
# HÀM PHỤ: LẤY MODEL LỖI NHIỀU NHẤT
# ================================================================
def lay_model_loi_nhieu_nhat(top=10):
    """Lấy top model lỗi nhiều nhất."""
    col = _collection_blacklist()
    if col is None:
        return []

    try:
        ket_qua = col.find({}).sort("so_lan_loi", -1).limit(top)
        return list(ket_qua)
    except Exception:
        return []
"""
ghi_nho.py - Tầng dữ liệu Rồng Thần (kết nối 2 kho MongoDB Atlas).

Nhiệm vụ:
    - Kết nối 2 kho MongoDB Atlas.
    - Cung cấp toàn bộ hàm CRUD cho dự án.
    - Không tự sập nếu MongoDB chưa kết nối.

2 kho:
    - KHO 1 (rong_than_user): tài khoản, phiên, chat, key, ảnh/file.
    - KHO 2 (rong_than_cay): hợp đồng, hướng dẫn, node, code, tiến độ.

Nguyên tắc:
    - Mọi collection kho 2 đều gắn chu_so_huu + id_chat.
    - Cây linh hồn LÀ CỦA RIÊNG mỗi chat.

ĐÃ SỬA:
    - _doc_uri_tu_file() đọc ENV trước (URI_KHO_1, URI_KHO_2).
    - Fallback: đọc file du_lieu/cau_hinh_kho.json.
"""

import os
import json
import time

from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId


# ================================================================
# HẰNG SỐ
# ================================================================
THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_CAU_HINH_KHO = os.path.join(THU_MUC_GOC, "du_lieu", "cau_hinh_kho.json")

TEN_KHO_1 = "rong_than_user"
TEN_KHO_2 = "rong_than_cay"
TIMEOUT_MS = 5000

_client_1 = None
_db_1 = None
_client_2 = None
_db_2 = None


# ================================================================
# ĐỌC / GHI URI
# ================================================================
def _doc_uri_tu_file():
    """Đọc URI 2 kho — ưu tiên ENV, fallback file."""
    # 1. Ưu tiên ENV (Render)
    uri_1_env = os.environ.get("URI_KHO_1", "")
    uri_2_env = os.environ.get("URI_KHO_2", "")
    if uri_1_env and uri_2_env:
        return uri_1_env, uri_2_env

    # 2. Fallback: đọc file local
    if not os.path.exists(FILE_CAU_HINH_KHO):
        return "", ""
    try:
        with open(FILE_CAU_HINH_KHO, "r", encoding="utf-8") as f:
            du_lieu = json.load(f)
        return (
            du_lieu.get("uri_kho_1", "") or "",
            du_lieu.get("uri_kho_2", "") or "",
        )
    except (json.JSONDecodeError, OSError):
        return "", ""


def _ghi_uri_vao_file(uri_1="", uri_2=""):
    os.makedirs(os.path.dirname(FILE_CAU_HINH_KHO), exist_ok=True)
    du_lieu = {}
    if os.path.exists(FILE_CAU_HINH_KHO):
        try:
            with open(FILE_CAU_HINH_KHO, "r", encoding="utf-8") as f:
                du_lieu = json.load(f)
        except (json.JSONDecodeError, OSError):
            du_lieu = {}
    if uri_1:
        du_lieu["uri_kho_1"] = uri_1
    if uri_2:
        du_lieu["uri_kho_2"] = uri_2
    try:
        with open(FILE_CAU_HINH_KHO, "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


# ================================================================
# KẾT NỐI 2 KHO
# ================================================================
def _ket_noi_kho_1():
    global _client_1, _db_1
    if _db_1 is not None:
        return _db_1, _client_1
    uri_1, _ = _doc_uri_tu_file()
    if not uri_1:
        return None, None
    try:
        _client_1 = MongoClient(uri_1, serverSelectionTimeoutMS=TIMEOUT_MS)
        _db_1 = _client_1[TEN_KHO_1]
        _client_1.admin.command("ping")
        return _db_1, _client_1
    except Exception:
        _client_1 = None
        _db_1 = None
        return None, None


def _ket_noi_kho_2():
    global _client_2, _db_2
    if _db_2 is not None:
        return _db_2, _client_2
    _, uri_2 = _doc_uri_tu_file()
    if not uri_2:
        return None, None
    try:
        _client_2 = MongoClient(uri_2, serverSelectionTimeoutMS=TIMEOUT_MS)
        _db_2 = _client_2[TEN_KHO_2]
        _client_2.admin.command("ping")
        return _db_2, _client_2
    except Exception:
        _client_2 = None
        _db_2 = None
        return None, None


def ping_ca_2_kho():
    ket_qua = {"kho_1": False, "kho_2": False}
    try:
        db1, _ = _ket_noi_kho_1()
        if db1 is not None:
            db1.command("ping")
            ket_qua["kho_1"] = True
    except Exception:
        pass
    try:
        db2, _ = _ket_noi_kho_2()
        if db2 is not None:
            db2.command("ping")
            ket_qua["kho_2"] = True
    except Exception:
        pass
    return ket_qua


def dat_lai_ket_noi():
    global _client_1, _db_1, _client_2, _db_2
    try:
        if _client_1:
            _client_1.close()
    except Exception:
        pass
    try:
        if _client_2:
            _client_2.close()
    except Exception:
        pass
    _client_1 = None
    _db_1 = None
    _client_2 = None
    _db_2 = None


# ================================================================
# URI KHO
# ================================================================
def luu_uri_kho_cua(chu_so_huu, so_kho, uri):
    if so_kho not in (1, 2) or not uri:
        return False
    if so_kho == 1:
        ok = _ghi_uri_vao_file(uri_1=uri)
    else:
        ok = _ghi_uri_vao_file(uri_2=uri)
    if ok:
        dat_lai_ket_noi()
    return ok


def lay_uri_kho_cua(chu_so_huu, so_kho):
    uri_1, uri_2 = _doc_uri_tu_file()
    if so_kho == 1:
        return uri_1
    if so_kho == 2:
        return uri_2
    return ""


# ================================================================
# TÀI KHOẢN
# ================================================================
def dem_tai_khoan():
    db, _ = _ket_noi_kho_1()
    if db is None:
        return 0
    try:
        return db["tai_khoan"].count_documents({})
    except Exception:
        return 0


def lay_tai_khoan(ten_dang_nhap):
    db, _ = _ket_noi_kho_1()
    if db is None or not ten_dang_nhap:
        return None
    try:
        return db["tai_khoan"].find_one({"ten_dang_nhap": ten_dang_nhap})
    except Exception:
        return None


def luu_tai_khoan(tai_khoan):
    db, _ = _ket_noi_kho_1()
    if db is None or not tai_khoan:
        return False
    try:
        db["tai_khoan"].insert_one(dict(tai_khoan))
        return True
    except Exception:
        return False


def lay_tai_khoan_cu_nhat():
    db, _ = _ket_noi_kho_1()
    if db is None:
        return None
    try:
        return db["tai_khoan"].find_one(sort=[("ngay_tao", 1)])
    except Exception:
        return None


def cap_nhat_mat_khau(ten_dang_nhap, chuoi_bam_moi):
    db, _ = _ket_noi_kho_1()
    if db is None or not ten_dang_nhap:
        return False
    try:
        kq = db["tai_khoan"].update_one(
            {"ten_dang_nhap": ten_dang_nhap},
            {"$set": {"mat_khau_bam": chuoi_bam_moi}},
        )
        return kq.modified_count > 0
    except Exception:
        return False


def xoa_tai_khoan_va_du_lieu(ten_dang_nhap):
    db, _ = _ket_noi_kho_1()
    if db is None or not ten_dang_nhap:
        return False
    try:
        db["tai_khoan"].delete_one({"ten_dang_nhap": ten_dang_nhap})
        db["phien_dang_nhap"].delete_many({"ten_dang_nhap": ten_dang_nhap})
        db["key_da_luu"].delete_many({"chu_so_huu": ten_dang_nhap})
        db["du_an"].delete_many({"chu_so_huu": ten_dang_nhap})
        db["chat_nhanh"].delete_many({"chu_so_huu": ten_dang_nhap})
        db["tro_chuyen"].delete_many({"chu_so_huu": ten_dang_nhap})
        db["tin_nhan"].delete_many({"chu_so_huu": ten_dang_nhap})
        db["lich_su_chat"].delete_many({"chu_so_huu": ten_dang_nhap})
        db["anh_file"].delete_many({"chu_so_huu": ten_dang_nhap})
        db["noi_dung_da_trich_xuat"].delete_many({"chu_so_huu": ten_dang_nhap})
        db["lich_su_gui"].delete_many({"chu_so_huu": ten_dang_nhap})
        return True
    except Exception:
        return False


# ================================================================
# PHIÊN ĐĂNG NHẬP
# ================================================================
def luu_phien_dang_nhap(phien):
    db, _ = _ket_noi_kho_1()
    if db is None or not phien:
        return False
    try:
        db["phien_dang_nhap"].insert_one(dict(phien))
        return True
    except Exception:
        return False


def lay_phien_dang_nhap(token):
    db, _ = _ket_noi_kho_1()
    if db is None or not token:
        return None
    try:
        return db["phien_dang_nhap"].find_one({"token": token})
    except Exception:
        return None


def xoa_phien_dang_nhap(token):
    db, _ = _ket_noi_kho_1()
    if db is None or not token:
        return False
    try:
        kq = db["phien_dang_nhap"].delete_one({"token": token})
        return kq.deleted_count > 0
    except Exception:
        return False


def gia_han_phien_dang_nhap(token, thoi_gian_het_han_moi):
    db, _ = _ket_noi_kho_1()
    if db is None or not token:
        return False
    try:
        kq = db["phien_dang_nhap"].update_one(
            {"token": token},
            {"$set": {"thoi_gian_het_han": thoi_gian_het_han_moi}},
        )
        return kq.modified_count > 0
    except Exception:
        return False


# ================================================================
# KEY
# ================================================================
def luu_key_da_luu(key):
    db, _ = _ket_noi_kho_1()
    if db is None or not key:
        return False
    try:
        db["key_da_luu"].insert_one(dict(key))
        return True
    except Exception:
        return False


def lay_danh_sach_key_cua(chu_so_huu):
    db, _ = _ket_noi_kho_1()
    if db is None or not chu_so_huu:
        return []
    try:
        return list(db["key_da_luu"].find({"chu_so_huu": chu_so_huu}))
    except Exception:
        return []


def lay_danh_sach_key_web_cua(chu_so_huu):
    db, _ = _ket_noi_kho_1()
    if db is None or not chu_so_huu:
        return []
    try:
        return list(db["key_da_luu"].find({
            "chu_so_huu": chu_so_huu,
            "loai_key": "tra_web",
        }))
    except Exception:
        return []


def lay_key_da_luu(id_key):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_key:
        return None
    try:
        return db["key_da_luu"].find_one({"id": id_key})
    except Exception:
        return None


def xoa_key_da_luu(id_key):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_key:
        return False
    try:
        kq = db["key_da_luu"].delete_one({"id": id_key})
        return kq.deleted_count > 0
    except Exception:
        return False


def cap_nhat_quota_key(id_key, phan_tram):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_key:
        return False
    try:
        kq = db["key_da_luu"].update_one(
            {"id": id_key},
            {"$set": {
                "phan_tram": phan_tram,
                "lan_kiem_tra_cuoi": int(time.time()),
            }},
        )
        return kq.modified_count > 0
    except Exception:
        return False


# ================================================================
# DỰ ÁN
# ================================================================
def lay_danh_sach_du_an_cua(chu_so_huu):
    db, _ = _ket_noi_kho_1()
    if db is None or not chu_so_huu:
        return []
    try:
        return list(db["du_an"].find({"chu_so_huu": chu_so_huu}))
    except Exception:
        return []


def luu_du_an(du_an):
    db, _ = _ket_noi_kho_1()
    if db is None or not du_an:
        return False
    try:
        db["du_an"].insert_one(dict(du_an))
        return True
    except Exception:
        return False


def lay_du_an(id_du_an):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_du_an:
        return None
    try:
        return db["du_an"].find_one({"id": id_du_an})
    except Exception:
        return None


def xoa_du_an_theo_id(id_du_an):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_du_an:
        return False
    try:
        kq = db["du_an"].delete_one({"id": id_du_an})
        db["tro_chuyen"].delete_many({"id_du_an": id_du_an})
        db["tin_nhan"].delete_many({"id_du_an": id_du_an})
        return kq.deleted_count > 0
    except Exception:
        return False


# ================================================================
# CHAT NHANH
# ================================================================
def lay_danh_sach_chat_nhanh_cua(chu_so_huu):
    db, _ = _ket_noi_kho_1()
    if db is None or not chu_so_huu:
        return []
    try:
        return list(db["chat_nhanh"].find({"chu_so_huu": chu_so_huu}))
    except Exception:
        return []


def luu_chat_nhanh(chat):
    db, _ = _ket_noi_kho_1()
    if db is None or not chat:
        return False
    try:
        db["chat_nhanh"].insert_one(dict(chat))
        return True
    except Exception:
        return False


def xoa_chat_nhanh_theo_id(id_chat, chu_so_huu=""):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_chat:
        return False
    try:
        dieu_kien = {"id": id_chat}
        if chu_so_huu:
            dieu_kien["chu_so_huu"] = chu_so_huu
        kq = db["chat_nhanh"].delete_one(dieu_kien)
        db["lich_su_chat"].delete_many({"id_chat": id_chat})
        return kq.deleted_count > 0
    except Exception:
        return False


def cap_nhat_ten_chat_nhanh(id_chat, chu_so_huu, ten_moi):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_chat:
        return False
    try:
        kq = db["chat_nhanh"].update_one(
            {"id": id_chat, "chu_so_huu": chu_so_huu},
            {"$set": {"ten": ten_moi}},
        )
        return kq.modified_count > 0
    except Exception:
        return False


def lay_tin_nhan_chat_nhanh(id_chat, chu_so_huu):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_chat:
        return []
    try:
        return list(db["lich_su_chat"].find({
            "id_chat": id_chat,
            "chu_so_huu": chu_so_huu,
        }).sort("thoi_gian", 1))
    except Exception:
        return []


def luu_tin_nhan_chat(tin):
    db, _ = _ket_noi_kho_1()
    if db is None or not tin:
        return False
    try:
        db["lich_su_chat"].insert_one(dict(tin))
        return True
    except Exception:
        return False


def lay_lich_su_chat(chu_so_huu, id_chat, gioi_han=20):
    db, _ = _ket_noi_kho_1()
    if db is None or not chu_so_huu or not id_chat:
        return []
    try:
        con_tro = db["lich_su_chat"].find({
            "chu_so_huu": chu_so_huu,
            "id_chat": id_chat,
        }).sort("thoi_gian", -1).limit(gioi_han)
        return list(reversed(list(con_tro)))
    except Exception:
        return []


# ================================================================
# TRÒ CHUYỆN
# ================================================================
def luu_tro_chuyen(tro):
    db, _ = _ket_noi_kho_1()
    if db is None or not tro:
        return False
    try:
        db["tro_chuyen"].insert_one(dict(tro))
        return True
    except Exception:
        return False


def lay_danh_sach_tro_chuyen_cua(id_du_an, chu_so_huu):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_du_an:
        return []
    try:
        return list(db["tro_chuyen"].find({
            "id_du_an": id_du_an,
            "chu_so_huu": chu_so_huu,
        }))
    except Exception:
        return []


def lay_tro_chuyen(id_tro):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_tro:
        return None
    try:
        return db["tro_chuyen"].find_one({"id": id_tro})
    except Exception:
        return None


def xoa_tro_chuyen_theo_id(id_tro, chu_so_huu=""):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_tro:
        return False
    try:
        dieu_kien = {"id": id_tro}
        if chu_so_huu:
            dieu_kien["chu_so_huu"] = chu_so_huu
        kq = db["tro_chuyen"].delete_one(dieu_kien)
        db["tin_nhan"].delete_many({"id_tro_chuyen": id_tro})
        return kq.deleted_count > 0
    except Exception:
        return False


# ================================================================
# TIN NHẮN
# ================================================================
def luu_tin_nhan_tro_chuyen(tin):
    db, _ = _ket_noi_kho_1()
    if db is None or not tin:
        return False
    try:
        db["tin_nhan"].insert_one(dict(tin))
        return True
    except Exception:
        return False


def lay_tin_nhan_tro_chuyen_cua(id_du_an, id_tro, chu_so_huu):
    db, _ = _ket_noi_kho_1()
    if db is None:
        return []
    try:
        return list(db["tin_nhan"].find({
            "id_du_an": id_du_an,
            "id_tro_chuyen": id_tro,
            "chu_so_huu": chu_so_huu,
        }).sort("thoi_gian", 1))
    except Exception:
        return []


# ================================================================
# ẢNH / FILE
# ================================================================
def luu_file_gridfs(ten_file, noi_dung, metadata=None):
    db, _ = _ket_noi_kho_1()
    if db is None:
        return None
    try:
        fs = GridFS(db)
        id_file = fs.put(
            noi_dung,
            filename=ten_file,
            metadata=metadata or {},
        )
        return id_file
    except Exception:
        return None


def doc_file_gridfs(id_gridfs):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_gridfs:
        return None
    try:
        fs = GridFS(db)
        try:
            oid = ObjectId(id_gridfs)
        except Exception:
            oid = id_gridfs
        file = fs.get(oid)
        return file.read()
    except Exception:
        return None


def luu_metadata_anh_file(metadata):
    db, _ = _ket_noi_kho_1()
    if db is None or not metadata:
        return False
    try:
        db["anh_file"].insert_one(dict(metadata))
        return True
    except Exception:
        return False


def lay_file_theo_id(id_file):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_file:
        return None
    try:
        return db["anh_file"].find_one({"id_file": id_file})
    except Exception:
        return None


def xoa_file_theo_tro_chuyen(id_tro, chu_so_huu=""):
    db, _ = _ket_noi_kho_1()
    if db is None or not id_tro:
        return False
    try:
        dieu_kien = {"id_tro_chuyen": id_tro}
        if chu_so_huu:
            dieu_kien["chu_so_huu"] = chu_so_huu
        danh_sach = list(db["anh_file"].find(dieu_kien))
        fs = GridFS(db)
        for f in danh_sach:
            id_gridfs = f.get("id_gridfs")
            if id_gridfs:
                try:
                    fs.delete(ObjectId(id_gridfs))
                except Exception:
                    pass
        db["anh_file"].delete_many(dieu_kien)
        return True
    except Exception:
        return False


def luu_noi_dung_trich_xuat(du_lieu):
    db, _ = _ket_noi_kho_1()
    if db is None or not du_lieu:
        return False
    try:
        db["noi_dung_da_trich_xuat"].insert_one(dict(du_lieu))
        return True
    except Exception:
        return False


def luu_lich_su_gui(du_lieu):
    db, _ = _ket_noi_kho_1()
    if db is None or not du_lieu:
        return False
    try:
        db["lich_su_gui"].insert_one(dict(du_lieu))
        return True
    except Exception:
        return False


# ================================================================
# LOGS
# ================================================================
def _collection_logs():
    db, _ = _ket_noi_kho_1()
    if db is None:
        return None
    return db["logs"]


def dem_log(loai=None):
    col = _collection_logs()
    if col is None:
        return 0
    try:
        dieu_kien = {"loai": loai} if loai else {}
        return col.count_documents(dieu_kien)
    except Exception:
        return 0


def xoa_log_cu(ngay=30):
    col = _collection_logs()
    if col is None or ngay < 1:
        return 0
    try:
        nguong = int(time.time()) - ngay * 24 * 3600
        kq = col.delete_many({"thoi_gian": {"$lt": nguong}})
        return kq.deleted_count
    except Exception:
        return 0


# ================================================================
# KHO 2 — CÂY LINH HỒN
# ================================================================
def _collection_kho_2(ten):
    db, _ = _ket_noi_kho_2()
    if db is None:
        return None
    return db[ten]


# ---------- HỢP ĐỒNG ----------
def luu_hop_dong(hop_dong):
    col = _collection_kho_2("hop_dong")
    if col is None or not hop_dong:
        return False
    try:
        col.insert_one(dict(hop_dong))
        return True
    except Exception:
        return False


def lay_hop_dong(chu_so_huu, id_chat):
    col = _collection_kho_2("hop_dong")
    if col is None or not chu_so_huu or not id_chat:
        return None
    try:
        return col.find_one(
            {"chu_so_huu": chu_so_huu, "id_chat": id_chat},
            sort=[("phien_ban", -1)],
        )
    except Exception:
        return None


def cap_nhat_hop_dong(chu_so_huu, id_chat, du_lieu_moi):
    col = _collection_kho_2("hop_dong")
    if col is None or not chu_so_huu or not id_chat:
        return False
    try:
        du_lieu_moi["thoi_gian_cap_nhat"] = int(time.time())
        kq = col.update_one(
            {"chu_so_huu": chu_so_huu, "id_chat": id_chat},
            {"$set": du_lieu_moi, "$inc": {"phien_ban": 1}},
            upsert=True,
        )
        return kq.modified_count > 0 or kq.upserted_id is not None
    except Exception:
        return False


def xoa_hop_dong(chu_so_huu, id_chat):
    col = _collection_kho_2("hop_dong")
    if col is None:
        return False
    try:
        kq = col.delete_one({"chu_so_huu": chu_so_huu, "id_chat": id_chat})
        return kq.deleted_count > 0
    except Exception:
        return False


# ---------- HƯỚNG DẪN ----------
def luu_huong_dan(huong_dan):
    col = _collection_kho_2("huong_dan")
    if col is None or not huong_dan:
        return False
    try:
        col.insert_one(dict(huong_dan))
        return True
    except Exception:
        return False


def lay_huong_dan(chu_so_huu, id_chat):
    col = _collection_kho_2("huong_dan")
    if col is None or not chu_so_huu or not id_chat:
        return None
    try:
        return col.find_one(
            {"chu_so_huu": chu_so_huu, "id_chat": id_chat},
            sort=[("thoi_gian_cap_nhat", -1)],
        )
    except Exception:
        return None


def cap_nhat_huong_dan(chu_so_huu, id_chat, du_lieu_moi):
    col = _collection_kho_2("huong_dan")
    if col is None or not chu_so_huu or not id_chat:
        return False
    try:
        du_lieu_moi["thoi_gian_cap_nhat"] = int(time.time())
        kq = col.update_one(
            {"chu_so_huu": chu_so_huu, "id_chat": id_chat},
            {"$set": du_lieu_moi},
            upsert=True,
        )
        return kq.modified_count > 0 or kq.upserted_id is not None
    except Exception:
        return False


def them_blacklist(chu_so_huu, id_chat, muc_moi):
    col = _collection_kho_2("huong_dan")
    if col is None or not chu_so_huu or not id_chat:
        return False
    try:
        col.update_one(
            {"chu_so_huu": chu_so_huu, "id_chat": id_chat},
            {"$addToSet": {"blacklist": muc_moi},
             "$set": {"thoi_gian_cap_nhat": int(time.time())}},
            upsert=True,
        )
        return True
    except Exception:
        return False


# ---------- NODE ----------
def luu_node(node):
    col = _collection_kho_2("node")
    if col is None or not node:
        return False
    try:
        col.insert_one(dict(node))
        return True
    except Exception:
        return False


def lay_node(chu_so_huu, id_chat, id_node):
    col = _collection_kho_2("node")
    if col is None:
        return None
    try:
        return col.find_one({
            "chu_so_huu": chu_so_huu,
            "id_chat": id_chat,
            "id_node": id_node,
        })
    except Exception:
        return None


def lay_danh_sach_node(chu_so_huu, id_chat):
    col = _collection_kho_2("node")
    if col is None or not chu_so_huu or not id_chat:
        return []
    try:
        return list(col.find({
            "chu_so_huu": chu_so_huu,
            "id_chat": id_chat,
        }))
    except Exception:
        return []


def cap_nhat_node(chu_so_huu, id_chat, id_node, du_lieu_moi):
    col = _collection_kho_2("node")
    if col is None:
        return False
    try:
        kq = col.update_one(
            {"chu_so_huu": chu_so_huu,
             "id_chat": id_chat,
             "id_node": id_node},
            {"$set": du_lieu_moi},
        )
        return kq.modified_count > 0
    except Exception:
        return False


def xoa_node(chu_so_huu, id_chat, id_node):
    col = _collection_kho_2("node")
    if col is None:
        return False
    try:
        kq = col.delete_one({
            "chu_so_huu": chu_so_huu,
            "id_chat": id_chat,
            "id_node": id_node,
        })
        return kq.deleted_count > 0
    except Exception:
        return False


def tang_so_lan_thu_node(chu_so_huu, id_chat, id_node):
    col = _collection_kho_2("node")
    if col is None:
        return False
    try:
        kq = col.update_one(
            {"chu_so_huu": chu_so_huu,
             "id_chat": id_chat,
             "id_node": id_node},
            {"$inc": {"so_lan_thu": 1}},
        )
        return kq.modified_count > 0
    except Exception:
        return False


def cap_nhat_score_node(chu_so_huu, id_chat, id_node, score_moi):
    col = _collection_kho_2("node")
    if col is None:
        return False
    try:
        kq = col.update_one(
            {"chu_so_huu": chu_so_huu,
             "id_chat": id_chat,
             "id_node": id_node},
            {"$set": {"score": score_moi}},
        )
        return kq.modified_count > 0
    except Exception:
        return False


# ---------- CODE ĐÃ VIẾT ----------
def luu_code_da_viet(du_lieu):
    col = _collection_kho_2("code_da_viet")
    if col is None or not du_lieu:
        return False
    try:
        col.insert_one(dict(du_lieu))
        return True
    except Exception:
        return False


def lay_code_da_viet(chu_so_huu, id_chat, buoc):
    col = _collection_kho_2("code_da_viet")
    if col is None:
        return None
    try:
        return col.find_one(
            {"chu_so_huu": chu_so_huu,
             "id_chat": id_chat,
             "buoc": buoc},
            sort=[("phien_ban", -1)],
        )
    except Exception:
        return None


def lay_tat_ca_code(chu_so_huu, id_chat):
    col = _collection_kho_2("code_da_viet")
    if col is None:
        return []
    try:
        return list(col.find({
            "chu_so_huu": chu_so_huu,
            "id_chat": id_chat,
        }).sort("buoc", 1))
    except Exception:
        return []


def xoa_code_da_viet(chu_so_huu, id_chat):
    col = _collection_kho_2("code_da_viet")
    if col is None:
        return False
    try:
        kq = col.delete_many({
            "chu_so_huu": chu_so_huu,
            "id_chat": id_chat,
        })
        return kq.deleted_count > 0
    except Exception:
        return False


# ---------- TIẾN ĐỘ ----------
def luu_tien_do(tien_do):
    col = _collection_kho_2("tien_do")
    if col is None or not tien_do:
        return False
    try:
        col.insert_one(dict(tien_do))
        return True
    except Exception:
        return False


def lay_tien_do(chu_so_huu, id_chat):
    col = _collection_kho_2("tien_do")
    if col is None or not chu_so_huu or not id_chat:
        return None
    try:
        return col.find_one({
            "chu_so_huu": chu_so_huu,
            "id_chat": id_chat,
        })
    except Exception:
        return None


def cap_nhat_tien_do(chu_so_huu, id_chat, du_lieu_moi):
    col = _collection_kho_2("tien_do")
    if col is None:
        return False
    try:
        du_lieu_moi["thoi_gian_cap_nhat"] = int(time.time())
        kq = col.update_one(
            {"chu_so_huu": chu_so_huu, "id_chat": id_chat},
            {"$set": du_lieu_moi},
            upsert=True,
        )
        return kq.modified_count > 0 or kq.upserted_id is not None
    except Exception:
        return False


def xoa_tien_do(chu_so_huu, id_chat):
    col = _collection_kho_2("tien_do")
    if col is None:
        return False
    try:
        kq = col.delete_one({
            "chu_so_huu": chu_so_huu,
            "id_chat": id_chat,
        })
        return kq.deleted_count > 0
    except Exception:
        return False


# ---------- XÓA TOÀN BỘ CÂY ----------
def xoa_toan_bo_cay_cua_chat(chu_so_huu, id_chat):
    db, _ = _ket_noi_kho_2()
    if db is None or not chu_so_huu or not id_chat:
        return False
    try:
        dieu_kien = {"chu_so_huu": chu_so_huu, "id_chat": id_chat}
        for ten in ["hop_dong", "huong_dan", "node", "code_da_viet", "tien_do"]:
            db[ten].delete_many(dieu_kien)
        return True
    except Exception:
        return False


def xoa_toan_bo_cay_cua_user(chu_so_huu):
    db, _ = _ket_noi_kho_2()
    if db is None or not chu_so_huu:
        return False
    try:
        for ten in ["hop_dong", "huong_dan", "node", "code_da_viet", "tien_do"]:
            db[ten].delete_many({"chu_so_huu": chu_so_huu})
        return True
    except Exception:
        return False
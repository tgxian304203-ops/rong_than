"""
ghi_nho.py - Tầng dữ liệu Rồng Thần.
"""

import os
import json
import time
from threading import Lock

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import (
        ConnectionFailure,
        ServerSelectionTimeoutError,
        ConfigurationError,
    )
    import gridfs
    PYMONGO_SAN_SANG = True
except ImportError:
    PYMONGO_SAN_SANG = False


THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_DU_LIEU = os.path.join(THU_MUC_GOC, "du_lieu")
FILE_CAU_HINH = os.path.join(THU_MUC_DU_LIEU, "cau_hinh_kho.json")


MAX_TAI_KHOAN = 50

TEN_KHO_1 = "rong_than_user"
TEN_KHO_2 = "rong_than_cay"

C_TAI_KHOAN = "tai_khoan"
C_PHIEN = "phien_dang_nhap"
C_LICH_SU_CHAT = "lich_su_chat"
C_DU_AN = "du_an"
C_KEY = "key_da_luu"
C_CAU_HINH_KHO = "cau_hinh_kho"
C_ANH_FILE = "anh_file"
C_NOI_DUNG_TRICH_XUAT = "noi_dung_da_trich_xuat"
C_LICH_SU_GUI = "lich_su_gui"
C_TRO_CHUYEN = "tro_chuyen"

C_NODE = "node"
C_LICH_SU_HOC = "lich_su_hoc"
C_TU_DIEN_LOI = "tu_dien_loi"
C_FAILED_PATHS = "failed_paths"
C_TU_KHOA_PHAN_LOAI = "tu_khoa_phan_loai"


_khoa = Lock()
_client_1 = None
_client_2 = None
_db_1 = None
_db_2 = None
_fs_1 = None
_uri_1_da_dung = None
_uri_2_da_dung = None


def _doc_cau_hinh():
    os.makedirs(THU_MUC_DU_LIEU, exist_ok=True)
    if not os.path.exists(FILE_CAU_HINH):
        return {}
    try:
        with open(FILE_CAU_HINH, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, OSError):
        return {}


def _lay_uri(so_kho):
    uri_env = os.environ.get(f"URI_KHO_{so_kho}")
    if uri_env:
        return uri_env
    cau_hinh = _doc_cau_hinh()
    return cau_hinh.get(f"uri_kho_{so_kho}")


def _ket_noi_kho_1():
    global _client_1, _db_1, _fs_1, _uri_1_da_dung
    if not PYMONGO_SAN_SANG:
        raise RuntimeError("Chua cai pymongo.")
    uri = _lay_uri(1)
    if not uri:
        raise RuntimeError("Chua co URI kho 1.")
    with _khoa:
        if _client_1 is not None and _uri_1_da_dung == uri:
            return _db_1, _fs_1
        try:
            _client_1 = MongoClient(uri, serverSelectionTimeoutMS=8000)
            _client_1.admin.command("ping")
        except (ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError) as e:
            _client_1 = None
            raise RuntimeError(f"Khong ket noi duoc kho 1: {e}")
        _db_1 = _client_1[TEN_KHO_1]
        _fs_1 = gridfs.GridFS(_db_1)
        _uri_1_da_dung = uri
        _tao_index_kho_1()
    return _db_1, _fs_1


def _ket_noi_kho_2():
    global _client_2, _db_2, _uri_2_da_dung
    if not PYMONGO_SAN_SANG:
        raise RuntimeError("Chua cai pymongo.")
    uri = _lay_uri(2)
    if not uri:
        raise RuntimeError("Chua co URI kho 2.")
    with _khoa:
        if _client_2 is not None and _uri_2_da_dung == uri:
            return _db_2
        try:
            _client_2 = MongoClient(uri, serverSelectionTimeoutMS=8000)
            _client_2.admin.command("ping")
        except (ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError) as e:
            _client_2 = None
            raise RuntimeError(f"Khong ket noi duoc kho 2: {e}")
        _db_2 = _client_2[TEN_KHO_2]
        _uri_2_da_dung = uri
        _tao_index_kho_2()
    return _db_2


def lam_moi_ket_noi():
    global _client_1, _client_2, _db_1, _db_2, _fs_1
    global _uri_1_da_dung, _uri_2_da_dung
    with _khoa:
        _client_1 = None
        _client_2 = None
        _db_1 = None
        _db_2 = None
        _fs_1 = None
        _uri_1_da_dung = None
        _uri_2_da_dung = None


def _tao_index_kho_1():
    try:
        _db_1[C_TAI_KHOAN].create_index([("ten_dang_nhap", ASCENDING)], unique=True)
        _db_1[C_TAI_KHOAN].create_index([("ngay_tao", ASCENDING)])
        _db_1[C_PHIEN].create_index(
            [("thoi_gian_het_han", ASCENDING)],
            expireAfterSeconds=0,
        )
        _db_1[C_PHIEN].create_index([("token", ASCENDING)], unique=True)
        _db_1[C_LICH_SU_CHAT].create_index(
            [("chu_so_huu", ASCENDING), ("id_chat", ASCENDING), ("thoi_gian", ASCENDING)]
        )
        _db_1[C_DU_AN].create_index([("chu_so_huu", ASCENDING)])
        _db_1[C_KEY].create_index([("chu_so_huu", ASCENDING)])
        _db_1[C_KEY].create_index([("loai_key", ASCENDING)])
        _db_1[C_ANH_FILE].create_index([("chu_so_huu", ASCENDING)])
        _db_1[C_NOI_DUNG_TRICH_XUAT].create_index([("id_file", ASCENDING)])
        _db_1[C_LICH_SU_GUI].create_index([("chu_so_huu", ASCENDING)])
        _db_1[C_TRO_CHUYEN].create_index([("id_du_an", ASCENDING)])
        _db_1[C_TRO_CHUYEN].create_index([("chu_so_huu", ASCENDING)])
    except Exception:
        pass


def _tao_index_kho_2():
    try:
        _db_2[C_NODE].create_index([("id", ASCENDING)], unique=True)
        _db_2[C_NODE].create_index([("linh_vuc", ASCENDING)])
        _db_2[C_LICH_SU_HOC].create_index([("thoi_gian", ASCENDING)])
        _db_2[C_TU_DIEN_LOI].create_index([("loai_loi", ASCENDING)], unique=True)
        _db_2[C_FAILED_PATHS].create_index([("id_node", ASCENDING)])
        _db_2[C_TU_KHOA_PHAN_LOAI].create_index([("tu_khoa", ASCENDING)], unique=True)
    except Exception:
        pass


def dem_tai_khoan():
    db, _ = _ket_noi_kho_1()
    return db[C_TAI_KHOAN].count_documents({})


def lay_tai_khoan(ten_dang_nhap):
    if not ten_dang_nhap:
        return None
    db, _ = _ket_noi_kho_1()
    return db[C_TAI_KHOAN].find_one({"ten_dang_nhap": ten_dang_nhap})


def luu_tai_khoan(tai_khoan):
    if not tai_khoan or not tai_khoan.get("ten_dang_nhap"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_TAI_KHOAN].insert_one(dict(tai_khoan))
        return True
    except Exception:
        return False


def lay_tai_khoan_cu_nhat():
    db, _ = _ket_noi_kho_1()
    return db[C_TAI_KHOAN].find_one(sort=[("ngay_tao", ASCENDING)])


def cap_nhat_mat_khau(ten_dang_nhap, chuoi_bam_moi):
    if not ten_dang_nhap or not chuoi_bam_moi:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        ket_qua = db[C_TAI_KHOAN].update_one(
            {"ten_dang_nhap": ten_dang_nhap},
            {"$set": {"mat_khau_bam": chuoi_bam_moi, "ngay_doi_mat_khau": int(time.time())}},
        )
        return ket_qua.modified_count > 0
    except Exception:
        return False


def xoa_tai_khoan_va_du_lieu(ten_dang_nhap):
    if not ten_dang_nhap:
        return False
    db, fs = _ket_noi_kho_1()
    dieu_kien = {"chu_so_huu": ten_dang_nhap}
    try:
        for metadata in db[C_ANH_FILE].find(dieu_kien):
            id_gridfs = metadata.get("id_gridfs")
            if id_gridfs:
                try:
                    from bson.objectid import ObjectId
                    fs.delete(ObjectId(id_gridfs))
                except Exception:
                    pass
    except Exception:
        pass
    for ten_coll in (
        C_LICH_SU_CHAT, C_DU_AN, C_KEY, C_CAU_HINH_KHO,
        C_ANH_FILE, C_NOI_DUNG_TRICH_XUAT, C_LICH_SU_GUI, C_TRO_CHUYEN,
    ):
        try:
            db[ten_coll].delete_many(dieu_kien)
        except Exception:
            pass
    try:
        db[C_PHIEN].delete_many({"ten_dang_nhap": ten_dang_nhap})
    except Exception:
        pass
    try:
        db[C_TAI_KHOAN].delete_one({"ten_dang_nhap": ten_dang_nhap})
    except Exception:
        return False
    return True


def luu_phien_dang_nhap(phien):
    if not phien or not phien.get("token"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_PHIEN].insert_one(dict(phien))
        return True
    except Exception:
        return False


def lay_phien_dang_nhap(token):
    if not token:
        return None
    db, _ = _ket_noi_kho_1()
    return db[C_PHIEN].find_one({"token": token})


def xoa_phien_dang_nhap(token):
    if not token:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_PHIEN].delete_one({"token": token})
        return True
    except Exception:
        return False


def gia_han_phien_dang_nhap(token, thoi_gian_het_han_moi):
    if not token:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        ket_qua = db[C_PHIEN].update_one(
            {"token": token},
            {"$set": {"thoi_gian_het_han": thoi_gian_het_han_moi}},
        )
        return ket_qua.modified_count > 0
    except Exception:
        return False


def lay_danh_sach_du_an_cua(ten_tk):
    if not ten_tk:
        return []
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_DU_AN].find(
        {"chu_so_huu": ten_tk, "loai": {"$ne": "chat_nhanh"}}
    ).sort("ngay_tao", DESCENDING)
    return [_chuan_hoa_doc(d) for d in ket_qua]


def luu_du_an(du_an):
    if not du_an or not du_an.get("id"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        du_an = dict(du_an)
        du_an.setdefault("loai", "du_an")
        db[C_DU_AN].insert_one(du_an)
        return True
    except Exception:
        return False


def lay_du_an(id_du_an):
    if not id_du_an:
        return None
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_DU_AN].find_one({"id": id_du_an})
    return _chuan_hoa_doc(ket_qua) if ket_qua else None


def xoa_du_an_theo_id(id_du_an):
    if not id_du_an:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        ket_qua = db[C_DU_AN].delete_one({"id": id_du_an})
        return ket_qua.deleted_count > 0
    except Exception:
        return False


def lay_danh_sach_chat_nhanh_cua(ten_tk):
    if not ten_tk:
        return []
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_DU_AN].find(
        {"chu_so_huu": ten_tk, "loai": "chat_nhanh"}
    ).sort("ngay_tao", DESCENDING)
    return [_chuan_hoa_doc(d) for d in ket_qua]


def luu_chat_nhanh(chat):
    if not chat or not chat.get("id"):
        return False
    chat = dict(chat)
    chat["loai"] = "chat_nhanh"
    db, _ = _ket_noi_kho_1()
    try:
        db[C_DU_AN].insert_one(chat)
        return True
    except Exception:
        return False


def xoa_chat_nhanh_theo_id(id_chat, ten_tk):
    if not id_chat or not ten_tk:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        ket_qua = db[C_DU_AN].delete_one(
            {"id": id_chat, "chu_so_huu": ten_tk, "loai": "chat_nhanh"}
        )
        return ket_qua.deleted_count > 0
    except Exception:
        return False


def cap_nhat_ten_chat_nhanh(id_chat, ten_tk, ten_moi):
    if not id_chat or not ten_tk or not ten_moi:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        ket_qua = db[C_DU_AN].update_one(
            {"id": id_chat, "chu_so_huu": ten_tk, "loai": "chat_nhanh"},
            {"$set": {"ten": ten_moi}},
        )
        return ket_qua.modified_count > 0
    except Exception:
        return False


def luu_key_da_luu(key):
    if not key or not key.get("id"):
        return False
    key = dict(key)
    key.setdefault("loai_key", "model")
    db, _ = _ket_noi_kho_1()
    try:
        db[C_KEY].insert_one(key)
        return True
    except Exception:
        return False


def lay_danh_sach_key_cua(ten_tk):
    if not ten_tk:
        return []
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_KEY].find(
        {"chu_so_huu": ten_tk, "loai_key": "model"}
    ).sort("ngay_tao", DESCENDING)
    return [_chuan_hoa_doc(k) for k in ket_qua]


def lay_danh_sach_key_web_cua(ten_tk):
    if not ten_tk:
        return []
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_KEY].find(
        {"chu_so_huu": ten_tk, "loai_key": "tra_web"}
    ).sort("ngay_tao", DESCENDING)
    return [_chuan_hoa_doc(k) for k in ket_qua]


def lay_key_da_luu(id_key):
    if not id_key:
        return None
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_KEY].find_one({"id": id_key})
    return _chuan_hoa_doc(ket_qua) if ket_qua else None


def xoa_key_da_luu(id_key):
    if not id_key:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        ket_qua = db[C_KEY].delete_one({"id": id_key})
        return ket_qua.deleted_count > 0
    except Exception:
        return False


def cap_nhat_quota_key(id_key, phan_tram):
    if not id_key:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        ket_qua = db[C_KEY].update_one(
            {"id": id_key},
            {"$set": {"phan_tram": phan_tram, "lan_kiem_tra_cuoi": int(time.time())}},
        )
        return ket_qua.modified_count > 0
    except Exception:
        return False


def luu_uri_kho_cua(ten_tk, so_kho, uri):
    if not ten_tk or so_kho not in (1, 2) or not uri:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_CAU_HINH_KHO].update_one(
            {"chu_so_huu": ten_tk},
            {
                "$set": {
                    f"uri_kho_{so_kho}": uri,
                    f"thoi_gian_luu_kho_{so_kho}": int(time.time()),
                    "chu_so_huu": ten_tk,
                }
            },
            upsert=True,
        )
        return True
    except Exception:
        return False


def lay_uri_kho_cua(ten_tk, so_kho):
    if not ten_tk or so_kho not in (1, 2):
        return ""
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_CAU_HINH_KHO].find_one({"chu_so_huu": ten_tk})
    if not ket_qua:
        return ""
    return ket_qua.get(f"uri_kho_{so_kho}", "") or ""


def luu_file_gridfs(ten_file, noi_dung, metadata=None):
    if not noi_dung:
        return None
    _, fs = _ket_noi_kho_1()
    try:
        id_file = fs.put(
            noi_dung,
            filename=ten_file or "khong_ten",
            metadata=metadata or {},
        )
        return str(id_file)
    except Exception:
        return None


def doc_file_gridfs(id_gridfs):
    if not id_gridfs:
        return None
    _, fs = _ket_noi_kho_1()
    try:
        from bson.objectid import ObjectId
        grid_out = fs.get(ObjectId(id_gridfs))
        return grid_out.read()
    except Exception:
        return None


def luu_metadata_anh_file(metadata):
    if not metadata or not metadata.get("id_file"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_ANH_FILE].insert_one(dict(metadata))
        return True
    except Exception:
        return False


def lay_metadata_anh_file(id_file):
    if not id_file:
        return None
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_ANH_FILE].find_one({"id_file": id_file})
    return _chuan_hoa_doc(ket_qua) if ket_qua else None


def luu_noi_dung_trich_xuat(du_lieu):
    if not du_lieu or not du_lieu.get("id_file"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_NOI_DUNG_TRICH_XUAT].insert_one(dict(du_lieu))
        return True
    except Exception:
        return False


def luu_lich_su_gui(du_lieu):
    if not du_lieu or not du_lieu.get("id_file"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_LICH_SU_GUI].insert_one(dict(du_lieu))
        return True
    except Exception:
        return False


def luu_tin_nhan_chat(tin_nhan):
    if not tin_nhan or not tin_nhan.get("id_tin_nhan"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_LICH_SU_CHAT].insert_one(dict(tin_nhan))
        return True
    except Exception:
        return False


def lay_lich_su_chat(ten_tk, id_chat, gioi_han=20):
    if not ten_tk:
        return []
    db, _ = _ket_noi_kho_1()
    dieu_kien = {"chu_so_huu": ten_tk}
    if id_chat:
        dieu_kien["id_chat"] = id_chat
    ket_qua = (
        db[C_LICH_SU_CHAT]
        .find(dieu_kien)
        .sort("thoi_gian", DESCENDING)
        .limit(gioi_han)
    )
    danh_sach = [_chuan_hoa_doc(t) for t in ket_qua]
    danh_sach.reverse()
    return danh_sach


def lay_tin_nhan_chat_nhanh(id_chat, ten_tk, gioi_han=200):
    """
    Lấy toàn bộ tin nhắn của 1 chat nhanh theo id_chat.
    Trả về mảng tin nhắn sắp xếp theo thời gian tăng dần.
    """
    if not id_chat or not ten_tk:
        return []
    db, _ = _ket_noi_kho_1()
    try:
        ket_qua = (
            db[C_LICH_SU_CHAT]
            .find({"chu_so_huu": ten_tk, "id_chat": id_chat})
            .sort("thoi_gian", ASCENDING)
            .limit(gioi_han)
        )
        return [_chuan_hoa_doc(t) for t in ket_qua]
    except Exception:
        return []


def doc_cay():
    cay_goc = _doc_cay_local()
    cay_kho_2 = _doc_cay_kho_2()
    if cay_goc and cay_kho_2:
        return _gop_cay(cay_goc, cay_kho_2)
    if cay_goc:
        return cay_goc
    if cay_kho_2:
        return cay_kho_2
    return {
        "id": "root",
        "ten": "ROOT",
        "nhanh_con": [],
        "so_lan_thu": 0,
        "score": 1.0,
    }


def _doc_cay_local():
    duong_dan_goc = os.path.join(THU_MUC_DU_LIEU, "cay_quyet_dinh.json")
    if not os.path.exists(duong_dan_goc):
        return None
    try:
        with open(duong_dan_goc, "r", encoding="utf-8") as f:
            cay_goc = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    file_con = {
        "toán": "cay_toan.json",
        "code": "cay_code.json",
        "bug": "cay_bug.json",
        "khac": "cay_khac.json",
    }

    for linh_vuc, ten_file in file_con.items():
        duong_dan = os.path.join(THU_MUC_DU_LIEU, ten_file)
        if not os.path.exists(duong_dan):
            continue
        try:
            with open(duong_dan, "r", encoding="utf-8") as f:
                du_lieu_con = json.load(f)
            _ghep_file_con_vao_cay(cay_goc, du_lieu_con, linh_vuc)
        except (json.JSONDecodeError, OSError):
            continue

    return cay_goc


def _ghep_file_con_vao_cay(cay_goc, du_lieu_con, linh_vuc):
    if not cay_goc or not du_lieu_con:
        return
    if linh_vuc in ("toán", "code", "bug"):
        for node in cay_goc.get("nhanh_con", []):
            if node.get("linh_vuc") == linh_vuc:
                if isinstance(du_lieu_con, dict):
                    nhanh_con = du_lieu_con.get("nhanh_con", [])
                    if nhanh_con:
                        node["nhanh_con"] = nhanh_con
                elif isinstance(du_lieu_con, list):
                    node["nhanh_con"] = du_lieu_con
                return
    if linh_vuc == "khac":
        if isinstance(du_lieu_con, dict):
            cac_node_con = du_lieu_con.get("nhanh_con", [])
            for node_con in cac_node_con:
                lv = node_con.get("linh_vuc", "")
                for node_goc in cay_goc.get("nhanh_con", []):
                    if node_goc.get("linh_vuc") == lv:
                        node_goc["nhanh_con"] = node_con.get("nhanh_con", [])
                        break


def _doc_cay_kho_2():
    try:
        db = _ket_noi_kho_2()
    except Exception:
        return None
    try:
        tat_ca = list(db[C_NODE].find({}))
    except Exception:
        return None
    if not tat_ca:
        return None
    ban_do = {}
    for node in tat_ca:
        node_id = node.get("id", "")
        ban_do[node_id] = _chuan_hoa_doc(node)
        ban_do[node_id].setdefault("nhanh_con", [])
    goc = None
    for node in tat_ca:
        node_id = node.get("id", "")
        cha_id = node.get("node_cha")
        if cha_id and cha_id in ban_do:
            ban_do[cha_id]["nhanh_con"].append(ban_do[node_id])
        elif node_id == "root" or not cha_id:
            goc = ban_do[node_id]
    if goc is None:
        goc = {
            "id": "root",
            "ten": "ROOT",
            "nhanh_con": list(ban_do.values()),
            "so_lan_thu": 0,
            "score": 1.0,
        }
    return goc


def _gop_cay(cay_a, cay_b):
    if not cay_a:
        return cay_b
    if not cay_b:
        return cay_a
    ban_do_b = {}
    for node in cay_b.get("nhanh_con", []):
        ban_do_b[node.get("id", "")] = node
    for node_a in cay_a.get("nhanh_con", []):
        node_b = ban_do_b.get(node_a.get("id", ""))
        if node_b:
            node_a["nhanh_con"] = _gop_nhanh_con(
                node_a.get("nhanh_con", []),
                node_b.get("nhanh_con", []),
            )
    id_a = {node.get("id", "") for node in cay_a.get("nhanh_con", [])}
    for node_b in cay_b.get("nhanh_con", []):
        if node_b.get("id", "") not in id_a:
            cay_a["nhanh_con"].append(node_b)
    return cay_a


def _gop_nhanh_con(danh_sach_a, danh_sach_b):
    ban_do = {node.get("id", ""): node for node in danh_sach_a}
    for node_b in danh_sach_b:
        node_id = node_b.get("id", "")
        if node_id in ban_do:
            node_a = ban_do[node_id]
            node_a["nhanh_con"] = _gop_nhanh_con(
                node_a.get("nhanh_con", []),
                node_b.get("nhanh_con", []),
            )
            if node_b.get("score", 0) > node_a.get("score", 0):
                node_a["score"] = node_b["score"]
        else:
            danh_sach_a.append(node_b)
    return danh_sach_a


def luu_node(node):
    if not node or not node.get("id"):
        return False
    db = _ket_noi_kho_2()
    try:
        db[C_NODE].update_one(
            {"id": node["id"]},
            {"$set": dict(node)},
            upsert=True,
        )
        return True
    except Exception:
        return False


def lay_node(id_node):
    if not id_node:
        return None
    db = _ket_noi_kho_2()
    ket_qua = db[C_NODE].find_one({"id": id_node})
    return _chuan_hoa_doc(ket_qua) if ket_qua else None


def luu_lich_su_hoc(du_lieu):
    if not du_lieu:
        return False
    db = _ket_noi_kho_2()
    try:
        db[C_LICH_SU_HOC].insert_one(dict(du_lieu))
        return True
    except Exception:
        return False


def luu_tu_dien_loi(loai_loi, du_lieu):
    if not loai_loi:
        return False
    db = _ket_noi_kho_2()
    try:
        db[C_TU_DIEN_LOI].update_one(
            {"loai_loi": loai_loi},
            {"$set": dict(du_lieu, loai_loi=loai_loi)},
            upsert=True,
        )
        return True
    except Exception:
        return False


def lay_tu_dien_loi():
    db = _ket_noi_kho_2()
    return [_chuan_hoa_doc(t) for t in db[C_TU_DIEN_LOI].find({})]


def luu_failed_path(du_lieu):
    if not du_lieu:
        return False
    db = _ket_noi_kho_2()
    try:
        db[C_FAILED_PATHS].insert_one(dict(du_lieu))
        return True
    except Exception:
        return False


def luu_tu_khoa_phan_loai(du_lieu):
    if not du_lieu or not du_lieu.get("tu_khoa"):
        return False
    db = _ket_noi_kho_2()
    try:
        db[C_TU_KHOA_PHAN_LOAI].update_one(
            {"tu_khoa": du_lieu["tu_khoa"]},
            {
                "$set": dict(du_lieu),
                "$setOnInsert": {"thoi_gian_tao": int(time.time())},
            },
            upsert=True,
        )
        return True
    except Exception:
        return False


def lay_tat_ca_tu_khoa_phan_loai():
    db = _ket_noi_kho_2()
    return [_chuan_hoa_doc(t) for t in db[C_TU_KHOA_PHAN_LOAI].find({})]


def tang_dem_tu_khoa(tu_khoa):
    if not tu_khoa:
        return False
    db = _ket_noi_kho_2()
    try:
        db[C_TU_KHOA_PHAN_LOAI].update_one(
            {"tu_khoa": tu_khoa},
            {
                "$inc": {"so_lan_dung": 1},
                "$set": {"lan_dung_cuoi": int(time.time())},
            },
        )
        return True
    except Exception:
        return False


def xoa_tu_khoa_phan_loai(tu_khoa):
    if not tu_khoa:
        return False
    db = _ket_noi_kho_2()
    try:
        db[C_TU_KHOA_PHAN_LOAI].delete_one({"tu_khoa": tu_khoa})
        return True
    except Exception:
        return False


def luu_cay_ra_local(cay):
    if not cay:
        return False
    os.makedirs(THU_MUC_DU_LIEU, exist_ok=True)

    cac_lv_khac = {"văn", "khoa học", "đời sống", "kinh doanh", "sáng tạo",
                   "học tập", "tra cứu", "kỹ thuật", "luật - hành chính"}

    cay_goc = dict(cay)
    cay_goc["nhanh_con"] = [
        {k: v for k, v in node.items() if k != "nhanh_con"}
        for node in cay.get("nhanh_con", [])
    ]

    _luu_json_local("cay_quyet_dinh.json", cay_goc)

    for node in cay.get("nhanh_con", []):
        linh_vuc = node.get("linh_vuc", "")
        if linh_vuc == "toán":
            _luu_json_local("cay_toan.json", node)
        elif linh_vuc == "code":
            _luu_json_local("cay_code.json", node)
        elif linh_vuc == "bug":
            _luu_json_local("cay_bug.json", node)

    cac_lv_khac_node = [
        node for node in cay.get("nhanh_con", [])
        if node.get("linh_vuc") in cac_lv_khac
    ]
    _luu_json_local("cay_khac.json", {
        "id": "nut-khac-0001",
        "ten": "Các lĩnh vực khác",
        "nhanh_con": cac_lv_khac_node,
    })

    return True


def _luu_json_local(ten_file, du_lieu):
    duong_dan = os.path.join(THU_MUC_DU_LIEU, ten_file)
    try:
        with open(duong_dan, "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, ensure_ascii=False, indent=2)
        return True
    except (OSError, TypeError):
        return False


def dem_node_cay(cay):
    if not cay:
        return 0
    dem = 1
    for con in cay.get("nhanh_con", []):
        dem += dem_node_cay(con)
    return dem


def thong_ke_cay(cay=None):
    if cay is None:
        cay = doc_cay()
    if not cay:
        return {"tong_node": 0, "theo_linh_vuc": {}, "do_sau_max": 0}

    theo_lv = {}
    do_sau_max = [0]

    def _duyet(node, do_sau=0):
        lv = node.get("linh_vuc", "")
        if lv:
            theo_lv[lv] = theo_lv.get(lv, 0) + 1
        if do_sau > do_sau_max[0]:
            do_sau_max[0] = do_sau
        for con in node.get("nhanh_con", []):
            _duyet(con, do_sau + 1)

    _duyet(cay)

    return {
        "tong_node": dem_node_cay(cay),
        "theo_linh_vuc": theo_lv,
        "do_sau_max": do_sau_max[0],
    }


def _chuan_hoa_doc(doc):
    if not doc:
        return doc
    ket_qua = {}
    for k, v in doc.items():
        if k == "_id":
            ket_qua[k] = str(v)
        else:
            ket_qua[k] = v
    return ket_qua


def luu_tro_chuyen(tro_chuyen):
    if not tro_chuyen or not tro_chuyen.get("id"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_TRO_CHUYEN].insert_one(dict(tro_chuyen))
        return True
    except Exception:
        return False


def lay_danh_sach_tro_chuyen_cua(id_du_an, ten_tk):
    if not id_du_an or not ten_tk:
        return []
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_TRO_CHUYEN].find(
        {"id_du_an": id_du_an, "chu_so_huu": ten_tk}
    ).sort("ngay_tao", DESCENDING)
    return [_chuan_hoa_doc(t) for t in ket_qua]


def lay_tro_chuyen(id_tro_chuyen):
    if not id_tro_chuyen:
        return None
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_TRO_CHUYEN].find_one({"id": id_tro_chuyen})
    return _chuan_hoa_doc(ket_qua) if ket_qua else None


def xoa_tro_chuyen_theo_id(id_tro_chuyen, ten_tk):
    if not id_tro_chuyen or not ten_tk:
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_LICH_SU_CHAT].delete_many({
            "id_tro_chuyen": id_tro_chuyen,
            "chu_so_huu": ten_tk,
        })
        ket_qua = db[C_TRO_CHUYEN].delete_one({
            "id": id_tro_chuyen,
            "chu_so_huu": ten_tk,
        })
        return ket_qua.deleted_count > 0
    except Exception:
        return False


def luu_tin_nhan_tro_chuyen(tin_nhan):
    if not tin_nhan or not tin_nhan.get("id"):
        return False
    db, _ = _ket_noi_kho_1()
    try:
        db[C_LICH_SU_CHAT].insert_one(dict(tin_nhan))
        return True
    except Exception:
        return False


def lay_tin_nhan_tro_chuyen_cua(id_du_an, id_tro_chuyen, ten_tk):
    if not id_du_an or not id_tro_chuyen or not ten_tk:
        return []
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_LICH_SU_CHAT].find({
        "id_du_an": id_du_an,
        "id_tro_chuyen": id_tro_chuyen,
        "chu_so_huu": ten_tk,
    }).sort("thoi_gian", ASCENDING)
    return [_chuan_hoa_doc(t) for t in ket_qua]


def ping_ca_2_kho():
    ket_qua = {"kho_1": False, "kho_2": False}
    try:
        db1, _ = _ket_noi_kho_1()
        db1.command("ping")
        ket_qua["kho_1"] = True
    except Exception:
        pass
    try:
        db2 = _ket_noi_kho_2()
        db2.command("ping")
        ket_qua["kho_2"] = True
    except Exception:
        pass
    return ket_qua


def xoa_file_theo_tro_chuyen(id_tro_chuyen, chu_so_huu):
    """
    Xóa toàn bộ ảnh/file thuộc 1 trò chuyện.
    - Xóa file thật trong GridFS.
    - Xóa metadata trong anh_file, noi_dung_da_trich_xuat, lich_su_gui.
    Trả về: số file đã xóa khỏi GridFS.
    """
    if not id_tro_chuyen or not chu_so_huu:
        return 0
    db, fs = _ket_noi_kho_1()
    dieu_kien = {
        "id_tro_chuyen": id_tro_chuyen,
        "chu_so_huu": chu_so_huu,
    }
    dem = 0
    try:
        for metadata in db[C_ANH_FILE].find(dieu_kien):
            id_gridfs = metadata.get("id_gridfs")
            if id_gridfs:
                try:
                    from bson.objectid import ObjectId
                    fs.delete(ObjectId(id_gridfs))
                    dem += 1
                except Exception:
                    pass
    except Exception:
        pass
    for ten_coll in (C_ANH_FILE, C_NOI_DUNG_TRICH_XUAT, C_LICH_SU_GUI):
        try:
            db[ten_coll].delete_many(dieu_kien)
        except Exception:
            pass
    return dem


def lay_file_theo_id(id_file):
    """
    Lấy metadata của file theo id_file.
    Trả về dict hoặc None.
    """
    if not id_file:
        return None
    db, _ = _ket_noi_kho_1()
    ket_qua = db[C_ANH_FILE].find_one({"id_file": id_file})
    return _chuan_hoa_doc(ket_qua) if ket_qua else None
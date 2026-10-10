"""
cau_hinh.py - Cấu hình trung tâm Rồng Thần.

Nhiệm vụ:
    - Khai báo đường dẫn thư mục, file.
    - Khai báo hằng số dùng chung toàn dự án.
    - Khai báo tên 2 kho MongoDB, collection.
    - Khai báo cấu hình sandbox, cây linh hồn, quota.

ĐÃ SỬA:
    - Bỏ 5 file cây cũ (cay_quyet_dinh, cay_toan, cay_code, cay_bug, cay_khac).
    - Chỉ còn 1 file cây linh hồn (cay_linh_hon.json).
    - Bỏ file lich_su_hoc.json.
    - Thêm hằng số hợp đồng, quota Boss/Model.
"""

import os


# ================================================================
# ĐƯỜNG DẪN GỐC
# ================================================================
THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))
THU_MUC_DU_LIEU = os.path.join(THU_MUC_GOC, "du_lieu")
THU_MUC_ANH = os.path.join(THU_MUC_DU_LIEU, "anh")
THU_MUC_FILE = os.path.join(THU_MUC_DU_LIEU, "file")
THU_MUC_LOGS = os.path.join(THU_MUC_GOC, "logs")
THU_MUC_GIAO_DIEN = os.path.join(THU_MUC_GOC, "giao_dien")
THU_MUC_SANDBOX = os.path.join(THU_MUC_GOC, "tieu_nao", "sanbox")


# ================================================================
# ĐƯỜNG DẪN FILE
# ================================================================
FILE_CAU_HINH_KHO = os.path.join(THU_MUC_DU_LIEU, "cau_hinh_kho.json")
FILE_CAY_LINH_HON = os.path.join(THU_MUC_DU_LIEU, "cay_linh_hon.json")
FILE_NHAT_KY = os.path.join(THU_MUC_DU_LIEU, "nhat_ky.log")
FILE_TU_DIEN_LOI = os.path.join(THU_MUC_DU_LIEU, "tu_dien_loi.json")
FILE_LICH_SU_CHAT = os.path.join(THU_MUC_DU_LIEU, "lich_su_chat.json")
FILE_TAI_KHOAN = os.path.join(THU_MUC_DU_LIEU, "tai_khoan.json")
FILE_TEN_DU_AN = os.path.join(THU_MUC_DU_LIEU, "ten_du_an.json")


# ================================================================
# MONGODB - TÊN 2 KHO
# ================================================================
TEN_KHO_1 = "rong_than_user"
TEN_KHO_2 = "rong_than_cay"

# ----------------------------------------------------------------
# Collection kho 1
# ----------------------------------------------------------------
C_TAI_KHOAN = "tai_khoan"
C_PHIEN = "phien_dang_nhap"
C_LICH_SU_CHAT = "lich_su_chat"
C_DU_AN = "du_an"
C_KEY = "key_da_luu"
C_CAU_HINH_KHO = "cau_hinh_kho"
C_ANH_FILE = "anh_file"
C_NOI_DUNG_TRICH_XUAT = "noi_dung_da_trich_xuat"
C_LICH_SU_GUI = "lich_su_gui"
C_CHAT_NHANH = "chat_nhanh"
C_TRO_CHUYEN = "tro_chuyen"
C_TIN_NHAN = "tin_nhan"

# ----------------------------------------------------------------
# Collection kho 2 (CÂY LINH HỒN)
# ----------------------------------------------------------------
C_HOP_DONG = "hop_dong"
C_HUONG_DAN = "huong_dan"
C_NODE = "node"
C_CODE_DA_VIET = "code_da_viet"
C_TIEN_DO = "tien_do"

KHOA_CHU_SO_HUU = "chu_so_huu"
KHOA_ID_CHAT = "id_chat"


# ================================================================
# GIỚI HẠN TÀI KHOẢN
# ================================================================
MAX_TAI_KHOAN = 50
THOI_GIAN_PHIEN = 7 * 24 * 60 * 60


# ================================================================
# PHÂN LOẠI
# ================================================================
LOAI_DON_GIAN = "don_gian"
LOAI_DU_AN = "du_an"

LINH_VUC_HOP_LE = [
    "toán", "văn", "code", "bug", "khoa học", "đời sống",
    "kinh doanh", "sáng tạo", "học tập", "tra cứu",
    "kỹ thuật", "luật - hành chính",
]


# ================================================================
# HỢP ĐỒNG
# ================================================================
HOP_DONG_CAP_NHAT_MOI_SU_KIEN = True
SO_BUOC_TOI_DA = 50


# ================================================================
# TIỂU NÃO / MODEL — API
# ================================================================
SO_LAN_THU_TOI_DA = 3
SO_LAN_RETRY = 3
TIMEOUT_API = 30

THU_TU_PROVIDER = ["Groq", "OpenRouter", "Gemini"]

# 3 loại key
LOAI_KEY_BOSS = "boss"
LOAI_KEY_TIEU_BOSS = "tieu_boss"
LOAI_KEY_TRA_WEB = "tra_web"
LOAI_KEY_HOP_LE = [LOAI_KEY_BOSS, LOAI_KEY_TIEU_BOSS, LOAI_KEY_TRA_WEB]


# ================================================================
# BOSS — QUOTA
# ================================================================
SO_LAN_THU_BOSS = 3
THOI_GIAN_VERIFY_TOI_DA = 99
SO_BUOC_KIEM_TRA_TOI_DA = 20


# ================================================================
# TRA WEB — API
# ================================================================
THU_TU_API_TRA_WEB = ["SERPJET", "Tavily", "Bright Data"]
TIMEOUT_TRA_WEB = 30
SO_KET_QUA_TRA_WEB = 5
DO_DAI_MO_TA_TOI_DA = 300
DO_DAI_TONG_HOP_TOI_DA = 3000

QUOTA_MAC_DINH = {
    "SERPJET": 1000,
    "Tavily": 1000,
    "Bright Data": 5000,
}


# ================================================================
# SANDBOX
# ================================================================
TIMEOUT_SANDBOX = 10
DO_DAI_CODE_TOI_DA = 50000
DO_DAI_OUTPUT_TOI_DA = 50000
LIVECODES_VERSION = "0.14.1"
LIVECODES_CDN = "https://cdn.jsdelivr.net/npm/livecodes@0.14.1"


# ================================================================
# LOGS
# ================================================================
LOAI_LOG_HOP_LE = ["dai-nao", "tieu-nao", "tra-web", "sandbox", "loi"]
SO_LOG_MAC_DINH = 100
SO_LOG_TOI_DA = 1000
NGAY_XOA_LOG_CU = 30


# ================================================================
# KEEP-ALIVE
# ================================================================
THOI_GIAN_KEEP_ALIVE = 12 * 3600
THOI_GIAN_KEEP_ALIVE_DAU = 60


# ================================================================
# FLASK / RENDER
# ================================================================
PORT_MAC_DINH = 5000
HOST = "0.0.0.0"
DEBUG = False
SECRET_KEY_FILE = "secret_key"


# ================================================================
# GIAO DIỆN
# ================================================================
SO_DONG_INPUT_TOI_DA = 6
CHIEU_CAO_DONG_INPUT = 24
CHIEU_CAO_INPUT_TOI_DA = SO_DONG_INPUT_TOI_DA * CHIEU_CAO_DONG_INPUT


# ================================================================
# UPLOAD
# ================================================================
DO_DAI_FILE_TOI_DA = 20 * 1024 * 1024
DUOI_ANH_HOP_LE = ["png", "jpg", "jpeg", "gif", "webp", "bmp", "svg"]
DUOI_TAI_LIEU_HOP_LE = [
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "txt", "csv", "json", "xml", "yaml", "yml",
    "zip", "rar", "7z",
]


# ================================================================
# HÀM TIỆN ÍCH
# ================================================================
def tao_thu_muc_can_thiet():
    """Tạo các thư mục cần thiết."""
    cac_thu_muc = [
        THU_MUC_DU_LIEU,
        THU_MUC_ANH,
        THU_MUC_FILE,
        THU_MUC_LOGS,
    ]
    for thu_muc in cac_thu_muc:
        try:
            os.makedirs(thu_muc, exist_ok=True)
        except OSError:
            pass


def lay_port():
    """Lấy PORT từ biến môi trường."""
    return int(os.environ.get("PORT", PORT_MAC_DINH))


def lay_thu_muc_goc():
    return THU_MUC_GOC


def lay_danh_sach_linh_vuc():
    return list(LINH_VUC_HOP_LE)


def lay_danh_sach_loai_log():
    return list(LOAI_LOG_HOP_LE)


def lay_danh_sach_loai_key():
    return list(LOAI_KEY_HOP_LE)


def la_linh_vuc_hop_le(linh_vuc):
    return linh_vuc in LINH_VUC_HOP_LE


def la_duoi_anh_hop_le(duoi):
    return duoi.lower() in DUOI_ANH_HOP_LE


def la_duoi_tai_lieu_hop_le(duoi):
    return duoi.lower() in DUOI_TAI_LIEU_HOP_LE


def la_loai_key_hop_le(loai):
    return loai in LOAI_KEY_HOP_LE


# ================================================================
# TỰ CHẠY KHI IMPORT
# ================================================================
tao_thu_muc_can_thiet()
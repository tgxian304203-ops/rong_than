"""
cau_hinh.py - Cấu hình trung tâm Rồng Thần.

Nhiệm vụ:
    - Khai báo đường dẫn thư mục, file.
    - Khai báo hằng số dùng chung toàn dự án.
    - Khai báo thông số giới hạn (max tài khoản, timeout, ...).
    - Khai báo tên 2 kho MongoDB, collection.
    - Khai báo cấu hình sandbox, cây quyết định, quota.

Quy tắc:
    - Không chứa logic — chỉ khai báo hằng số.
    - Mọi file khác import từ đây nếu cần.
    - Đọc biến môi trường khi cần thiết.

Dùng:
    from cau_hinh import MAX_TAI_KHOAN, TEN_KHO_1
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
THU_MUC_SANDBOX = os.path.join(THU_MUC_GOC, "sanbox")


# ================================================================
# ĐƯỜNG DẪN FILE
# ================================================================
FILE_CAU_HINH_KHO = os.path.join(THU_MUC_DU_LIEU, "cau_hinh_kho.json")
FILE_CAY_GOC = os.path.join(THU_MUC_DU_LIEU, "cay_quyet_dinh.json")
FILE_CAY_TOAN = os.path.join(THU_MUC_DU_LIEU, "cay_toan.json")
FILE_CAY_CODE = os.path.join(THU_MUC_DU_LIEU, "cay_code.json")
FILE_CAY_BUG = os.path.join(THU_MUC_DU_LIEU, "cay_bug.json")
FILE_CAY_KHAC = os.path.join(THU_MUC_DU_LIEU, "cay_khac.json")
FILE_NHAT_KY = os.path.join(THU_MUC_DU_LIEU, "nhat_ky.log")
FILE_TU_DIEN_LOI = os.path.join(THU_MUC_DU_LIEU, "tu_dien_loi.json")
FILE_LICH_SU_HOC = os.path.join(THU_MUC_DU_LIEU, "lich_su_hoc.json")
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

# ----------------------------------------------------------------
# Collection kho 2
# ----------------------------------------------------------------
C_NODE = "node"
C_LICH_SU_HOC = "lich_su_hoc"
C_TU_DIEN_LOI = "tu_dien_loi"
C_FAILED_PATHS = "failed_paths"
C_TU_KHOA_PHAN_LOAI = "tu_khoa_phan_loai"


# ================================================================
# GIỚI HẠN TÀI KHOẢN
# ================================================================
MAX_TAI_KHOAN = 50
THOI_GIAN_PHIEN = 7 * 24 * 60 * 60  # 7 ngày (giây)


# ================================================================
# CÂY QUYẾT ĐỊNH
# ================================================================
SO_LAN_FAIL_BLACKLIST = 3
TY_LE_FAIL_GIAM_SCORE = 0.5
MUC_GIAM_SCORE = 0.2
NGUONG_SCORE_MUON = 0.5
NGUONG_DUNG = 0.7
NGUONG_TIN_CAY_CAO = 0.95
TY_LE_GIONG_FAILED_PATH = 0.8
SO_NODE_TOI_DA_XET = 200


# ================================================================
# CHUẨN HÓA INPUT
# ================================================================
NGUONG_GIONG_CHINH_TA = 0.9  # giống > 90% mới sửa


# ================================================================
# TIỂU NÃO - API MODEL
# ================================================================
SO_LAN_THU_TOI_DA = 3
SO_LAN_RETRY = 3
TIMEOUT_API = 30
TIMEOUT_GROQ = 30
TIMEOUT_OPENROUTER = 30
TIMEOUT_GEMINI = 30

# Thứ tự ưu tiên provider
THU_TU_PROVIDER = ["Groq", "OpenRouter", "Gemini"]


# ================================================================
# TRA WEB - API
# ================================================================
THU_TU_API_TRA_WEB = ["SERPJET", "Tavily", "Bright Data"]
TIMEOUT_TRA_WEB = 30
SO_KET_QUA_TRA_WEB = 5
DO_DAI_MO_TA_TOI_DA = 300
DO_DAI_TONG_HOP_TOI_DA = 3000

# Quota mặc định mỗi API (reset ngày 1 hàng tháng)
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
PYODIDE_VERSION = "v0.29.0"
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
THOI_GIAN_KEEP_ALIVE = 12 * 3600  # 12 giờ
THOI_GIAN_KEEP_ALIVE_DAU = 60      # đợi 60 giây trước lần ping đầu


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
CHIEU_CAO_DONG_INPUT = 24  # px
CHIEU_CAO_INPUT_TOI_DA = SO_DONG_INPUT_TOI_DA * CHIEU_CAO_DONG_INPUT  # 144px


# ================================================================
# UPLOAD
# ================================================================
DO_DAI_FILE_TOI_DA = 20 * 1024 * 1024  # 20MB
DUOI_ANH_HOP_LE = ["png", "jpg", "jpeg", "gif", "webp", "bmp", "svg"]
DUOI_TAI_LIEU_HOP_LE = [
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "txt", "csv", "json", "xml", "yaml", "yml",
    "zip", "rar", "7z",
]


# ================================================================
# PHÂN LOẠI - 12 LĨNH VỰC
# ================================================================
LINH_VUC_HOP_LE = [
    "toán", "văn", "code", "bug", "khoa học", "đời sống",
    "kinh doanh", "sáng tạo", "học tập", "tra cứu",
    "kỹ thuật", "luật - hành chính",
]


# ================================================================
# 5 YẾU TỐ TRÍCH XUẤT
# ================================================================
CAN_5_YEU_TO = (
    "hanh_dong", "doi_tuong", "thuoc_tinh", "rang_buoc", "ngu_canh",
)


# ================================================================
# 10 LOẠI NGỮ CẢNH
# ================================================================
LOAI_NGU_CANH = [
    "hoi_thoai", "du_an", "file", "task_truoc", "linh_vuc",
    "ngon_ngu", "moi_truong", "rang_buoc", "thoi_gian", "cam_xuc",
]


# ================================================================
# HÀM TIỆN ÍCH
# ================================================================
def tao_thu_muc_can_thiet():
    """Tạo các thư mục cần thiết nếu chưa có."""
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
    """Lấy PORT từ biến môi trường (Render set tự động)."""
    return int(os.environ.get("PORT", PORT_MAC_DINH))


def lay_thu_muc_goc():
    """Trả đường dẫn thư mục gốc."""
    return THU_MUC_GOC


def lay_danh_sach_cay():
    """Trả danh sách 5 file cây."""
    return [
        FILE_CAY_GOC,
        FILE_CAY_TOAN,
        FILE_CAY_CODE,
        FILE_CAY_BUG,
        FILE_CAY_KHAC,
    ]


def lay_danh_sach_linh_vuc():
    """Trả danh sách 12 lĩnh vực."""
    return list(LINH_VUC_HOP_LE)


def lay_danh_sach_loai_log():
    """Trả danh sách 5 loại log."""
    return list(LOAI_LOG_HOP_LE)


def la_linh_vuc_hop_le(linh_vuc):
    """Kiểm tra lĩnh vực có hợp lệ không."""
    return linh_vuc in LINH_VUC_HOP_LE


def la_duoi_anh_hop_le(duoi):
    """Kiểm tra đuôi ảnh có hợp lệ không."""
    return duoi.lower() in DUOI_ANH_HOP_LE


def la_duoi_tai_lieu_hop_le(duoi):
    """Kiểm tra đuôi tài liệu có hợp lệ không."""
    return duoi.lower() in DUOI_TAI_LIEU_HOP_LE


# ================================================================
# TỰ CHẠY KHI IMPORT
# ================================================================
tao_thu_muc_can_thiet()
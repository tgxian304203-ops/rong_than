"""
sinh_cay_linh_hon.py - Sinh cây linh hồn khởi tạo.

Nhiệm vụ:
    - Tạo file du_lieu/cay_linh_hon.json nếu chưa có.
    - Cây linh hồn là của riêng mỗi chat.
    - File này chỉ là template khởi tạo (không chứa dữ liệu thật).

Nguyên tắc:
    - Chạy 1 lần khi khởi động.
    - Nếu file đã có → không ghi đè.
    - Dữ liệu thật nằm ở KHO 2 (MongoDB).
"""

import os
import json


# ================================================================
# ĐƯỜNG DẪN
# ================================================================
THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_CAY = os.path.join(THU_MUC_GOC, "du_lieu", "cay_linh_hon.json")


# ================================================================
# TEMPLATE CÂY LINH HỒN
# ================================================================
def _tao_template():
    """Tạo template cây linh hồn khởi tạo."""
    return {
        "phien_ban": "1.0",
        "khoi_tao_luc": 0,
        "ghi_chu": "File template cây linh hồn. Dữ liệu thật ở KHO 2 MongoDB.",
        "cau_truc": {
            "hop_dong": {
                "mo_ta": "Đang làm gì, tới đâu, tiếp theo",
                "truong": ["chu_so_huu", "id_chat",
                           "dang_lam_gi", "dang_lam_toi_dau",
                           "tiep_theo_lam_gi", "phien_ban"],
            },
            "huong_dan": {
                "mo_ta": "Nên làm gì để không sai",
                "truong": ["chu_so_huu", "id_chat",
                           "nen_lam_gi", "da_thu",
                           "blacklist", "thong_tin_moi"],
            },
            "node": {
                "mo_ta": "Node của cây (nếu cần)",
                "truong": ["chu_so_huu", "id_chat", "id_node",
                           "ten", "linh_vuc", "score", "so_lan_thu"],
            },
            "code_da_viet": {
                "mo_ta": "Code đã viết (GIỮ MÃI MÃI)",
                "truong": ["chu_so_huu", "id_chat", "buoc",
                           "file", "code", "phien_ban"],
            },
            "tien_do": {
                "mo_ta": "Tiến độ + lịch sử bước",
                "truong": ["chu_so_huu", "id_chat",
                           "buoc_hien_tai", "tong_buoc",
                           "trang_thai", "lich_su_buoc"],
            },
        },
    }


# ================================================================
# SINH CÂY
# ================================================================
def sinh_cay():
    """
    Sinh file cây linh hồn nếu chưa có.

    Trả về: True/False.
    """
    # Kiểm tra file đã tồn tại chưa
    if os.path.exists(FILE_CAY):
        return True

    # Tạo thư mục nếu chưa có
    os.makedirs(os.path.dirname(FILE_CAY), exist_ok=True)

    # Tạo template
    import time
    template = _tao_template()
    template["khoi_tao_luc"] = int(time.time())

    try:
        with open(FILE_CAY, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


# ================================================================
# ĐỌC CÂY
# ================================================================
def doc_cay():
    """Đọc file cây linh hồn."""
    if not os.path.exists(FILE_CAY):
        return None

    try:
        with open(FILE_CAY, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


# ================================================================
# KIỂM TRA TỒN TẠI
# ================================================================
def cay_ton_tai():
    """Kiểm tra file cây đã tồn tại chưa."""
    return os.path.exists(FILE_CAY)


# ================================================================
# TỰ CHẠY KHI IMPORT
# ================================================================
sinh_cay()
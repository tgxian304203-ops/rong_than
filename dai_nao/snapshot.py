"""
snapshot.py - Lưu + đọc trạng thái dự án Rồng Thần.

Nhiệm vụ:
    - tao_snapshot(id_du_an, du_lieu): tạo snapshot mới cho dự án.
    - cap_nhat_snapshot(id_du_an, cap_nhat): cập nhật snapshot.
    - lay_snapshot(id_du_an): đọc snapshot hiện tại.
    - tom_tat_cho_model(id_du_an): tóm tắt snapshot cho model mới đọc.
    - xoa_snapshot(id_du_an): xóa snapshot.

Snapshot dùng để:
    - Khi Boss A hết quota → Boss B đọc snapshot → hiểu ngữ cảnh.
    - Khi Tiểu não B thay Tiểu não A → đọc snapshot → viết tiếp đúng.

Schema snapshot:
    {
        id_du_an: str,
        yeu_cau_goc: str,              # Yêu cầu ban đầu của user
        loai_du_an: str,               # "web" | "python" | "văn" | ...
        da_chia: [                     # Danh sách task đã chia
            {
                so: int,               # Số thứ tự
                ten: str,              # Tên task
                file: str,             # File liên quan (nếu có)
                trang_thai: str,       # "chua_lam" | "dang_lam" | "xong" | "loi"
                mo_ta: str,            # Mô tả task
            }
        ],
        hop_dong_da_chot: {            # Hợp đồng đã chốt cho từng file
            ten_file: { ...hop_dong... }
        },
        quy_uoc_chung: {               # Quy ước chung của dự án
            ngon_ngu: str,
            khong_dung: [str],
            ten_bien: str,
        },
        model_da_dung: [str],          # Danh sách model đã dùng
        model_hien_tai: str,           # Model đang dùng
        buoc_hien_tai: int,            # Bước thứ mấy
        lan_cap_nhat_cuoi: int,        # Timestamp
        thoi_gian_tao: int,            # Timestamp
    }

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import time
import json


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
# SCHEMA MẶC ĐỊNH
# ================================================================
SNAPSHOT_MAC_DINH = {
    "id_du_an": "",
    "yeu_cau_goc": "",
    "loai_du_an": "",
    "da_chia": [],
    "hop_dong_da_chot": {},
    "quy_uoc_chung": {
        "ngon_ngu": "",
        "khong_dung": [],
        "ten_bien": "camelCase",
        "css": "flexbox",
    },
    "model_da_dung": [],
    "model_hien_tai": "",
    "buoc_hien_tai": 0,
    "lan_cap_nhat_cuoi": 0,
    "thoi_gian_tao": 0,
}

TRANG_THAI_HOP_LE = ("chua_lam", "dang_lam", "xong", "loi")


# ================================================================
# TẠO SNAPSHOT MỚI
# ================================================================
def tao_snapshot(id_du_an, du_lieu=None):
    """
    Tạo snapshot mới cho dự án.

    id_du_an: mã dự án (VD "web-pokemon").
    du_lieu: dict các trường cần ghi đè.

    Trả về: dict snapshot hoàn chỉnh hoặc None nếu lỗi.
    """
    if not id_du_an:
        _ghi_log("loi", "tao_snapshot: thiếu id_du_an.")
        return None

    snapshot = dict(SNAPSHOT_MAC_DINH)
    snapshot["id_du_an"] = id_du_an
    snapshot["thoi_gian_tao"] = int(time.time())
    snapshot["lan_cap_nhat_cuoi"] = int(time.time())

    # Ghi đè các trường từ du_lieu
    if du_lieu and isinstance(du_lieu, dict):
        for khoa, gia_tri in du_lieu.items():
            if khoa in ("id_du_an", "thoi_gian_tao"):
                continue
            snapshot[khoa] = gia_tri

    # Lưu vào MongoDB
    try:
        from dai_nao.ghi_nho import luu_snapshot
        if not luu_snapshot(snapshot):
            _ghi_log("loi", f"Không lưu được snapshot cho {id_du_an}.")
            return None
    except ImportError:
        _ghi_log("loi", "ghi_nho.py chưa có.")
        return None
    except Exception as e:
        _ghi_log("loi", f"Lưu snapshot lỗi: {e}")
        return None

    _ghi_log("dai-nao", f"Đã tạo snapshot cho dự án {id_du_an}")
    return snapshot


# ================================================================
# ĐỌC SNAPSHOT
# ================================================================
def lay_snapshot(id_du_an):
    """
    Đọc snapshot hiện tại.

    Trả về dict snapshot hoặc None nếu không có.
    """
    if not id_du_an:
        return None

    try:
        from dai_nao.ghi_nho import lay_snapshot as _lay
        return _lay(id_du_an)
    except ImportError:
        _ghi_log("loi", "ghi_nho.py chưa có.")
        return None
    except Exception as e:
        _ghi_log("loi", f"Đọc snapshot lỗi: {e}")
        return None


# ================================================================
# CẬP NHẬT SNAPSHOT
# ================================================================
def cap_nhat_snapshot(id_du_an, cap_nhat):
    """
    Cập nhật 1 số trường trong snapshot.

    id_du_an: mã dự án.
    cap_nhat: dict các trường cần cập nhật.

    Trả về True/False.
    """
    if not id_du_an or not cap_nhat:
        return False

    try:
        from dai_nao.ghi_nho import cap_nhat_snapshot as _cap_nhat
        return _cap_nhat(id_du_an, cap_nhat)
    except ImportError:
        _ghi_log("loi", "ghi_nho.py chưa có.")
        return False
    except Exception as e:
        _ghi_log("loi", f"Cập nhật snapshot lỗi: {e}")
        return False


# ================================================================
# XÓA SNAPSHOT
# ================================================================
def xoa_snapshot(id_du_an):
    """Xóa snapshot theo id_du_an."""
    if not id_du_an:
        return False
    try:
        from dai_nao.ghi_nho import xoa_snapshot as _xoa
        return _xoa(id_du_an)
    except ImportError:
        return False
    except Exception as e:
        _ghi_log("loi", f"Xóa snapshot lỗi: {e}")
        return False


# ================================================================
# CẬP NHẬT TASK CỤ THỂ
# ================================================================
def cap_nhat_task(id_du_an, so_task, trang_thai, ghi_chu=""):
    """
    Cập nhật trạng thái 1 task trong snapshot.

    so_task: số thứ tự task (1-based).
    trang_thai: "chua_lam" | "dang_lam" | "xong" | "loi".
    ghi_chu: ghi chú thêm.
    """
    if not id_du_an or not so_task:
        return False

    if trang_thai not in TRANG_THAI_HOP_LE:
        _ghi_log("loi", f"Trạng thái không hợp lệ: {trang_thai}")
        return False

    snapshot = lay_snapshot(id_du_an)
    if not snapshot:
        _ghi_log("loi", f"Không có snapshot cho {id_du_an}.")
        return False

    da_chia = snapshot.get("da_chia", [])
    if not isinstance(da_chia, list):
        da_chia = []

    # Tìm task theo số
    tim_thay = False
    for task in da_chia:
        if task.get("so") == so_task:
            task["trang_thai"] = trang_thai
            if ghi_chu:
                task["ghi_chu"] = ghi_chu
            tim_thay = True
            break

    if not tim_thay:
        _ghi_log("loi", f"Không tìm thấy task số {so_task}.")
        return False

    return cap_nhat_snapshot(id_du_an, {"da_chia": da_chia})


# ================================================================
# ĐÁNH DẤU FILE XONG
# ================================================================
def danh_dau_file_xong(id_du_an, ten_file, model_tao=""):
    """
    Đánh dấu file đã hoàn thành + ghi model đã tạo.

    ten_file: tên file (VD "index.html").
    model_tao: model đã tạo file này (VD "gemini-3-flash").
    """
    if not id_du_an or not ten_file:
        return False

    snapshot = lay_snapshot(id_du_an)
    if not snapshot:
        return False

    # Cập nhật hợp đồng đã chốt
    hop_dong = snapshot.get("hop_dong_da_chot", {})
    if not isinstance(hop_dong, dict):
        hop_dong = {}

    if ten_file not in hop_dong:
        hop_dong[ten_file] = {"trang_thai": "xong"}
    else:
        hop_dong[ten_file]["trang_thai"] = "xong"

    if model_tao:
        hop_dong[ten_file]["model_tao"] = model_tao

    # Cập nhật model_da_dung
    model_da_dung = snapshot.get("model_da_dung", [])
    if not isinstance(model_da_dung, list):
        model_da_dung = []
    if model_tao and model_tao not in model_da_dung:
        model_da_dung.append(model_tao)

    return cap_nhat_snapshot(id_du_an, {
        "hop_dong_da_chot": hop_dong,
        "model_da_dung": model_da_dung,
    })


# ================================================================
# ĐỔI MODEL HIỆN TẠI
# ================================================================
def doi_model_hien_tai(id_du_an, model_moi):
    """Ghi lại model hiện tại đang dùng."""
    if not id_du_an or not model_moi:
        return False

    snapshot = lay_snapshot(id_du_an)
    if not snapshot:
        return False

    model_da_dung = snapshot.get("model_da_dung", [])
    if not isinstance(model_da_dung, list):
        model_da_dung = []
    if model_moi not in model_da_dung:
        model_da_dung.append(model_moi)

    return cap_nhat_snapshot(id_du_an, {
        "model_hien_tai": model_moi,
        "model_da_dung": model_da_dung,
    })


# ================================================================
# TĂNG BƯỚC HIỆN TẠI
# ================================================================
def tang_buoc(id_du_an):
    """Tăng bước hiện tại lên 1."""
    if not id_du_an:
        return False

    snapshot = lay_snapshot(id_du_an)
    if not snapshot:
        return False

    buoc = int(snapshot.get("buoc_hien_tai", 0) or 0) + 1
    return cap_nhat_snapshot(id_du_an, {"buoc_hien_tai": buoc})


# ================================================================
# TÓM TẮT CHO MODEL MỚI ĐỌC
# ================================================================
def tom_tat_cho_model(id_du_an, gioi_han_ky_tu=3000):
    """
    Tạo tóm tắt snapshot cho model mới đọc khi đổi Boss.

    Trả về chuỗi text ngắn gọn — mô tả:
        - Yêu cầu gốc.
        - Đã làm gì.
        - Đang làm gì.
        - Còn gì chưa làm.
        - Quy ước dự án.
        - Hợp đồng đã chốt.

    Model mới đọc text này → hiểu ngay ngữ cảnh → không ngáo.
    """
    if not id_du_an:
        return ""

    snapshot = lay_snapshot(id_du_an)
    if not snapshot:
        return f"[Không có snapshot cho dự án {id_du_an}]"

    phan = []

    # 1. Yêu cầu gốc
    yeu_cau = snapshot.get("yeu_cau_goc", "")
    if yeu_cau:
        phan.append(f"📋 YÊU CẦU GỐC: {yeu_cau}")

    # 2. Loại dự án
    loai_du_an = snapshot.get("loai_du_an", "")
    if loai_du_an:
        phan.append(f"📁 LOẠI DỰ ÁN: {loai_du_an}")

    # 3. Quy ước chung
    quy_uoc = snapshot.get("quy_uoc_chung", {})
    if quy_uoc:
        phan.append("\n⚙️ QUY ƯỚC CHUNG:")
        if quy_uoc.get("ngon_ngu"):
            phan.append(f"  - Ngôn ngữ: {quy_uoc['ngon_ngu']}")
        if quy_uoc.get("khong_dung"):
            phan.append(f"  - Không dùng: {', '.join(quy_uoc['khong_dung'])}")
        if quy_uoc.get("ten_bien"):
            phan.append(f"  - Tên biến: {quy_uoc['ten_bien']}")
        if quy_uoc.get("css"):
            phan.append(f"  - CSS: {quy_uoc['css']}")

    # 4. Danh sách task
    da_chia = snapshot.get("da_chia", [])
    if da_chia:
        phan.append("\n📝 DANH SÁCH TASK:")
        for task in da_chia:
            so = task.get("so", "?")
            ten = task.get("ten", "?")
            file = task.get("file", "")
            trang_thai = task.get("trang_thai", "chua_lam")

            ky_hieu = {
                "xong": "✅",
                "dang_lam": "🔄",
                "loi": "❌",
                "chua_lam": "⏳",
            }.get(trang_thai, "⏳")

            dong = f"  {ky_hieu} Task {so}: {ten}"
            if file:
                dong += f" ({file})"
            phan.append(dong)

    # 5. Hợp đồng đã chốt
    hop_dong = snapshot.get("hop_dong_da_chot", {})
    if hop_dong:
        phan.append("\n📜 HỢP ĐỒNG ĐÃ CHỐT:")
        for ten_file, hd in hop_dong.items():
            if isinstance(hd, dict):
                xuat_ra = hd.get("xuat_ra", {})
                ham = xuat_ra.get("ham", []) if isinstance(xuat_ra, dict) else []
                if ham:
                    ten_ham = [h.get("ten", "?") if isinstance(h, dict) else str(h) for h in ham]
                    phan.append(f"  - {ten_file}: hàm [{', '.join(ten_ham)}]")
                else:
                    phan.append(f"  - {ten_file}: {hd.get('trang_thai', '?')}")

    # 6. Model đã dùng
    model_da_dung = snapshot.get("model_da_dung", [])
    if model_da_dung:
        phan.append(f"\n🤖 MODEL ĐÃ DÙNG: {', '.join(model_da_dung)}")

    model_hien_tai = snapshot.get("model_hien_tai", "")
    if model_hien_tai:
        phan.append(f"🎯 MODEL HIỆN TẠI: {model_hien_tai}")

    # 7. Bước hiện tại
    buoc = snapshot.get("buoc_hien_tai", 0)
    if buoc:
        phan.append(f"👣 BƯỚC HIỆN TẠI: {buoc}")

    tom_tat = "\n".join(phan)

    # Cắt nếu quá dài
    if len(tom_tat) > gioi_han_ky_tu:
        tom_tat = tom_tat[:gioi_han_ky_tu] + "\n...[cắt bớt]"

    return tom_tat


# ================================================================
# HÀM PHỤ
# ================================================================
def co_snapshot(id_du_an):
    """Kiểm tra có snapshot chưa."""
    return lay_snapshot(id_du_an) is not None


def lay_trang_thai_task(id_du_an, so_task):
    """Lấy trạng thái 1 task."""
    snapshot = lay_snapshot(id_du_an)
    if not snapshot:
        return None

    for task in snapshot.get("da_chia", []):
        if task.get("so") == so_task:
            return task.get("trang_thai", "chua_lam")
    return None


def dem_task_theo_trang_thai(id_du_an):
    """Đếm task theo trạng thái."""
    snapshot = lay_snapshot(id_du_an)
    if not snapshot:
        return {}

    ket_qua = {"chua_lam": 0, "dang_lam": 0, "xong": 0, "loi": 0}
    for task in snapshot.get("da_chia", []):
        tt = task.get("trang_thai", "chua_lam")
        if tt in ket_qua:
            ket_qua[tt] += 1
    return ket_qua


def lay_task_tiep_theo(id_du_an):
    """Lấy task tiếp theo chưa làm."""
    snapshot = lay_snapshot(id_du_an)
    if not snapshot:
        return None

    for task in snapshot.get("da_chia", []):
        if task.get("trang_thai") in ("chua_lam", "dang_lam"):
            return task
    return None
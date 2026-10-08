"""
hop_dong.py - Quản lý hợp đồng giữa các file Rồng Thần.

Nhiệm vụ:
    - tao_hop_dong(id_du_an, ten_file, du_lieu): tạo hợp đồng cho 1 file.
    - luu_hop_dong(hop_dong): lưu vào MongoDB.
    - lay_hop_dong(id_du_an, ten_file): đọc hợp đồng.
    - lay_tat_ca_hop_dong(id_du_an): đọc toàn bộ hợp đồng của dự án.
    - tom_tat_cho_model(id_du_an): tóm tắt hợp đồng cho model đọc.
    - kiem_tra_code_khop_hop_dong(code, hop_dong): kiểm tra code có khớp không.
    - xoa_hop_dong(id_du_an, ten_file): xóa 1 hợp đồng.

Hợp đồng dùng để:
    - Chốt trước: "cart.js PHẢI có hàm themVaoGio(sanPham)".
    - Khi Tiểu não A viết cart.js → kiểm tra khớp hợp đồng.
    - Khi Tiểu não B thay → viết lại cart.js → cũng phải khớp hợp đồng.
    - Chống lệch khi đổi model.

Schema hợp đồng:
    {
        id_du_an: str,
        ten_file: str,
        ngon_ngu: str,                 # "python" | "html" | "javascript"
        vai_tro: str,                  # Mô tả chức năng file
        xuat_ra: {
            ham: [
                {"ten": str, "tham_so": [str], "tra_ve": str}
            ],
            bien: [
                {"ten": str, "kieu": str}
            ],
            class_: [
                {"ten": str, "phuong_thuc": [str]}
            ],
        },
        nhap_vao: {
            tu_file: [str],            # Import từ file nào
            dung_bien: [str],          # Dùng biến gì (localStorage, DOM id)
            goi_ham: [str],            # Gọi hàm từ file khác
        },
        cau_truc_du_lieu: {            # Kiểu dữ liệu chính
            ten_kieu: str,
        },
        quy_uoc: [str],                # Quy ước riêng của file
        trang_thai: str,               # "chot" | "dang_viet" | "xong"
        model_tao: str,
        ngay_tao: int,
        lan_cap_nhat_cuoi: int,
    }

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import time
import re


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
HOP_DONG_MAC_DINH = {
    "id_du_an": "",
    "ten_file": "",
    "ngon_ngu": "",
    "vai_tro": "",
    "xuat_ra": {
        "ham": [],
        "bien": [],
        "class_": [],
    },
    "nhap_vao": {
        "tu_file": [],
        "dung_bien": [],
        "goi_ham": [],
    },
    "cau_truc_du_lieu": {},
    "quy_uoc": [],
    "trang_thai": "chot",
    "model_tao": "",
    "ngay_tao": 0,
    "lan_cap_nhat_cuoi": 0,
}

TRANG_THAI_HOP_LE = ("chot", "dang_viet", "xong")


# ================================================================
# TẠO HỢP ĐỒNG MỚI
# ================================================================
def tao_hop_dong(id_du_an, ten_file, du_lieu=None):
    """
    Tạo hợp đồng mới cho 1 file.

    id_du_an: mã dự án.
    ten_file: tên file (VD "cart.js").
    du_lieu: dict các trường cần ghi đè.

    Trả về: dict hợp đồng hoàn chỉnh hoặc None nếu lỗi.
    """
    if not id_du_an or not ten_file:
        _ghi_log("loi", "tao_hop_dong: thiếu id_du_an hoặc ten_file.")
        return None

    hop_dong = dict(HOP_DONG_MAC_DINH)
    hop_dong["id_du_an"] = id_du_an
    hop_dong["ten_file"] = ten_file
    hop_dong["ngay_tao"] = int(time.time())
    hop_dong["lan_cap_nhat_cuoi"] = int(time.time())

    # Ghi đè các trường từ du_lieu
    if du_lieu and isinstance(du_lieu, dict):
        for khoa, gia_tri in du_lieu.items():
            if khoa in ("id_du_an", "ten_file", "ngay_tao"):
                continue
            hop_dong[khoa] = gia_tri

    # Lưu vào MongoDB
    try:
        from dai_nao.ghi_nho import luu_hop_dong as _luu
        if not _luu(hop_dong):
            _ghi_log("loi", f"Không lưu được hợp đồng {ten_file}.")
            return None
    except ImportError:
        _ghi_log("loi", "ghi_nho.py chưa có.")
        return None
    except Exception as e:
        _ghi_log("loi", f"Lưu hợp đồng lỗi: {e}")
        return None

    _ghi_log("dai-nao", f"Đã tạo hợp đồng {ten_file} cho dự án {id_du_an}")
    return hop_dong


# ================================================================
# LƯU HỢP ĐỒNG
# ================================================================
def luu_hop_dong(hop_dong):
    """Lưu hợp đồng vào MongoDB."""
    if not hop_dong or not hop_dong.get("id_du_an") or not hop_dong.get("ten_file"):
        return False

    hop_dong["lan_cap_nhat_cuoi"] = int(time.time())

    try:
        from dai_nao.ghi_nho import luu_hop_dong as _luu
        return _luu(hop_dong)
    except ImportError:
        return False
    except Exception as e:
        _ghi_log("loi", f"Lưu hợp đồng lỗi: {e}")
        return False


# ================================================================
# ĐỌC HỢP ĐỒNG
# ================================================================
def lay_hop_dong(id_du_an, ten_file):
    """Đọc hợp đồng 1 file."""
    if not id_du_an or not ten_file:
        return None

    try:
        from dai_nao.ghi_nho import lay_hop_dong as _lay
        return _lay(id_du_an, ten_file)
    except ImportError:
        _ghi_log("loi", "ghi_nho.py chưa có.")
        return None
    except Exception as e:
        _ghi_log("loi", f"Đọc hợp đồng lỗi: {e}")
        return None


def lay_tat_ca_hop_dong(id_du_an):
    """Đọc toàn bộ hợp đồng của dự án."""
    if not id_du_an:
        return []

    try:
        from dai_nao.ghi_nho import lay_tat_ca_hop_dong as _lay
        return _lay(id_du_an) or []
    except ImportError:
        return []
    except Exception as e:
        _ghi_log("loi", f"Đọc tất cả hợp đồng lỗi: {e}")
        return []


# ================================================================
# XÓA HỢP ĐỒNG
# ================================================================
def xoa_hop_dong(id_du_an, ten_file):
    """Xóa 1 hợp đồng."""
    if not id_du_an or not ten_file:
        return False
    try:
        from dai_nao.ghi_nho import xoa_hop_dong as _xoa
        return _xoa(id_du_an, ten_file)
    except ImportError:
        return False
    except Exception as e:
        _ghi_log("loi", f"Xóa hợp đồng lỗi: {e}")
        return False


def xoa_tat_ca_hop_dong(id_du_an):
    """Xóa toàn bộ hợp đồng của dự án."""
    if not id_du_an:
        return False
    try:
        from dai_nao.ghi_nho import xoa_tat_ca_hop_dong as _xoa
        return _xoa(id_du_an)
    except ImportError:
        return False
    except Exception as e:
        _ghi_log("loi", f"Xóa tất cả hợp đồng lỗi: {e}")
        return False


# ================================================================
# CẬP NHẬT HỢP ĐỒNG
# ================================================================
def cap_nhat_hop_dong(id_du_an, ten_file, cap_nhat):
    """Cập nhật 1 số trường trong hợp đồng."""
    if not id_du_an or not ten_file or not cap_nhat:
        return False

    hop_dong = lay_hop_dong(id_du_an, ten_file)
    if not hop_dong:
        _ghi_log("loi", f"Không có hợp đồng {ten_file}.")
        return False

    for khoa, gia_tri in cap_nhat.items():
        hop_dong[khoa] = gia_tri

    return luu_hop_dong(hop_dong)


def danh_dau_hop_dong_xong(id_du_an, ten_file, model_tao=""):
    """Đánh dấu hợp đồng đã hoàn thành."""
    cap_nhat = {"trang_thai": "xong"}
    if model_tao:
        cap_nhat["model_tao"] = model_tao
    return cap_nhat_hop_dong(id_du_an, ten_file, cap_nhat)


# ================================================================
# KIỂM TRA CODE KHỚP HỢP ĐỒNG
# ================================================================
def kiem_tra_code_khop_hop_dong(code, hop_dong, ngon_ngu=None):
    """
    Kiểm tra code có khớp hợp đồng không.

    Kiểm tra:
        - Hàm yêu cầu có tồn tại trong code không.
        - Tên hàm có đúng không.
        - Biến yêu cầu có tồn tại không.

    Trả về: {
        "dat": True/False,
        "ly_do": str,
        "thieu_ham": [str],
        "thua_ham": [str],
        "thieu_bien": [str],
    }
    """
    ket_qua = {
        "dat": True,
        "ly_do": "",
        "thieu_ham": [],
        "thua_ham": [],
        "thieu_bien": [],
    }

    if not code or not hop_dong:
        ket_qua["dat"] = False
        ket_qua["ly_do"] = "Thiếu code hoặc hợp đồng."
        return ket_qua

    nn = ngon_ngu or hop_dong.get("ngon_ngu", "") or "python"

    # Lấy hợp đồng yêu cầu
    xuat_ra = hop_dong.get("xuat_ra", {})
    if not isinstance(xuat_ra, dict):
        xuat_ra = {}

    ham_yeu_cau = xuat_ra.get("ham", [])
    bien_yeu_cau = xuat_ra.get("bien", [])

    # Phân tích code để tìm hàm/biến có thật
    ham_trong_code = _trich_ham_tu_code(code, nn)
    bien_trong_code = _trich_bien_tu_code(code, nn)

    # Kiểm tra hàm
    for ham in ham_yeu_cau:
        if isinstance(ham, dict):
            ten = ham.get("ten", "")
        else:
            ten = str(ham)

        if not ten:
            continue

        if ten not in ham_trong_code:
            ket_qua["thieu_ham"].append(ten)

    # Kiểm tra biến
    for bien in bien_yeu_cau:
        if isinstance(bien, dict):
            ten = bien.get("ten", "")
        else:
            ten = str(bien)

        if not ten:
            continue

        if ten not in bien_trong_code:
            ket_qua["thieu_bien"].append(ten)

    # Đánh giá
    if ket_qua["thieu_ham"] or ket_qua["thieu_bien"]:
        ket_qua["dat"] = False
        phan = []
        if ket_qua["thieu_ham"]:
            phan.append(f"Thiếu hàm: {', '.join(ket_qua['thieu_ham'])}")
        if ket_qua["thieu_bien"]:
            phan.append(f"Thiếu biến: {', '.join(ket_qua['thieu_bien'])}")
        ket_qua["ly_do"] = " | ".join(phan)

    return ket_qua


def _trich_ham_tu_code(code, ngon_ngu):
    """Trích tên hàm từ code."""
    ham = set()

    if ngon_ngu.lower() == "python":
        # def ten_ham(...)
        mau = re.findall(r"\bdef\s+([a-zA-Z_]\w*)\s*\(", code)
        ham.update(mau)
    elif ngon_ngu.lower() in ("javascript", "js"):
        # function ten_ham(...) hoặc ten_ham = (...) => hoặc ten_ham: function
        mau1 = re.findall(r"\bfunction\s+([a-zA-Z_]\w*)\s*\(", code)
        mau2 = re.findall(r"\b([a-zA-Z_]\w*)\s*=\s*(?:function|\([^)]*\)\s*=>)", code)
        ham.update(mau1)
        ham.update(mau2)
    elif ngon_ngu.lower() == "html":
        # onclick="ten_ham()" hoặc id="..."
        mau = re.findall(r"on\w+\s*=\s*['\"]([a-zA-Z_]\w*)\s*\(", code)
        ham.update(mau)
    elif ngon_ngu.lower() == "java":
        mau = re.findall(r"\b(?:public|private|protected|static)?\s*(?:\w+\s+)?([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{", code)
        ham.update(mau)

    return ham


def _trich_bien_tu_code(code, ngon_ngu):
    """Trích tên biến từ code."""
    bien = set()

    if ngon_ngu.lower() == "python":
        # ten_bien = ...
        mau = re.findall(r"^\s*([a-zA-Z_]\w*)\s*=", code, re.MULTILINE)
        bien.update(mau)
    elif ngon_ngu.lower() in ("javascript", "js"):
        # var/let/const ten_bien
        mau = re.findall(r"\b(?:var|let|const)\s+([a-zA-Z_]\w*)", code)
        bien.update(mau)
    elif ngon_ngu.lower() == "html":
        # id="ten_bien"
        mau = re.findall(r'\bid\s*=\s*["\']([a-zA-Z_]\w*)["\']', code)
        bien.update(mau)

    return bien


# ================================================================
# TÓM TẮT CHO MODEL ĐỌC
# ================================================================
def tom_tat_cho_model(id_du_an, gioi_han_ky_tu=2000):
    """
    Tạo tóm tắt hợp đồng cho model đọc.

    Model đọc → biết chính xác interface của từng file → không viết lệch.
    """
    if not id_du_an:
        return ""

    tat_ca = lay_tat_ca_hop_dong(id_du_an)
    if not tat_ca:
        return f"[Chưa có hợp đồng nào cho dự án {id_du_an}]"

    phan = ["📜 HỢP ĐỒNG FILE:"]

    for hd in tat_ca:
        ten_file = hd.get("ten_file", "?")
        ngon_ngu = hd.get("ngon_ngu", "")
        vai_tro = hd.get("vai_tro", "")
        trang_thai = hd.get("trang_thai", "chot")

        phan.append(f"\n📄 {ten_file} [{ngon_ngu}] ({trang_thai})")
        if vai_tro:
            phan.append(f"   Vai trò: {vai_tro}")

        # Hàm xuất ra
        xuat_ra = hd.get("xuat_ra", {})
        if isinstance(xuat_ra, dict):
            ham = xuat_ra.get("ham", [])
            if ham:
                ds = []
                for h in ham:
                    if isinstance(h, dict):
                        ten = h.get("ten", "?")
                        tham_so = h.get("tham_so", [])
                        tra_ve = h.get("tra_ve", "")
                        dong = f"{ten}({', '.join(tham_so)})"
                        if tra_ve:
                            dong += f" → {tra_ve}"
                        ds.append(dong)
                    else:
                        ds.append(str(h))
                phan.append(f"   Hàm: {' | '.join(ds)}")

            bien = xuat_ra.get("bien", [])
            if bien:
                ds_bien = []
                for b in bien:
                    if isinstance(b, dict):
                        ds_bien.append(f"{b.get('ten', '?')}: {b.get('kieu', '?')}")
                    else:
                        ds_bien.append(str(b))
                phan.append(f"   Biến: {', '.join(ds_bien)}")

        # Nhập vào
        nhap_vao = hd.get("nhap_vao", {})
        if isinstance(nhap_vao, dict):
            goi_ham = nhap_vao.get("goi_ham", [])
            if goi_ham:
                phan.append(f"   Gọi hàm từ file khác: {', '.join(goi_ham)}")
            dung_bien = nhap_vao.get("dung_bien", [])
            if dung_bien:
                phan.append(f"   Dùng biến: {', '.join(dung_bien)}")

        # Quy ước
        quy_uoc = hd.get("quy_uoc", [])
        if quy_uoc:
            phan.append(f"   Quy ước: {' | '.join(quy_uoc)}")

    tom_tat = "\n".join(phan)

    if len(tom_tat) > gioi_han_ky_tu:
        tom_tat = tom_tat[:gioi_han_ky_tu] + "\n...[cắt bớt]"

    return tom_tat


# ================================================================
# HÀM PHỤ
# ================================================================
def co_hop_dong(id_du_an, ten_file):
    """Kiểm tra có hợp đồng chưa."""
    return lay_hop_dong(id_du_an, ten_file) is not None


def dem_hop_dong(id_du_an):
    """Đếm số hợp đồng của dự án."""
    return len(lay_tat_ca_hop_dong(id_du_an))


def lay_danh_sach_file(id_du_an):
    """Lấy danh sách tên file có hợp đồng."""
    tat_ca = lay_tat_ca_hop_dong(id_du_an)
    return [hd.get("ten_file", "") for hd in tat_ca if hd.get("ten_file")]


def hop_dong_da_xong(id_du_an):
    """Lấy danh sách hợp đồng đã xong."""
    tat_ca = lay_tat_ca_hop_dong(id_du_an)
    return [hd for hd in tat_ca if hd.get("trang_thai") == "xong"]


def hop_dong_chua_xong(id_du_an):
    """Lấy danh sách hợp đồng chưa xong."""
    tat_ca = lay_tat_ca_hop_dong(id_du_an)
    return [hd for hd in tat_ca if hd.get("trang_thai") != "xong"]
"""
doi_chieu.py - Đối chiếu code với hợp đồng Rồng Thần.

Nhiệm vụ:
    - doi_chieu(id_du_an, ten_file, code, ngon_ngu): kiểm tra code khớp hợp đồng.
    - kiem_tra_ham(code, hop_dong, ngon_ngu): kiểm tra hàm.
    - kiem_tra_bien(code, hop_dong, ngon_ngu): kiểm tra biến.
    - kiem_tra_import(code, hop_dong, ngon_ngu): kiểm tra import.
    - tom_tat_loi(ket_qua): tóm tắt lỗi cho user.

Đối chiếu dùng để:
    - Sau khi Tiểu não viết code → Đại não kiểm tra.
    - Nếu khớp hợp đồng → PASS → trả user.
    - Nếu không khớp → FAIL → yêu cầu sửa.

Quy tắc:
    - Khớp hàm: tên hàm trong hợp đồng phải có trong code.
    - Khớp biến: tên biến trong hợp đồng phải có trong code.
    - Khớp import: file gọi hàm từ file khác → hàm đó phải tồn tại.
"""

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
# TRÍCH HÀM TỪ CODE
# ================================================================
def _trich_ham(code, ngon_ngu):
    """
    Trích tên hàm từ code — hỗ trợ nhiều ngôn ngữ.

    Trả về: set các tên hàm.
    """
    ham = set()
    if not code:
        return ham

    nn = (ngon_ngu or "").lower()

    if nn == "python":
        # def ten_ham(...)
        mau = re.findall(r"\bdef\s+([a-zA-Z_]\w*)\s*\(", code)
        ham.update(mau)
        # lambda
        mau_lambda = re.findall(r"\b([a-zA-Z_]\w*)\s*=\s*lambda", code)
        ham.update(mau_lambda)

    elif nn in ("javascript", "js", "typescript", "ts"):
        # function ten_ham(...)
        mau1 = re.findall(r"\bfunction\s+([a-zA-Z_]\w*)\s*\(", code)
        # ten_ham = function(...)
        mau2 = re.findall(r"\b([a-zA-Z_]\w*)\s*=\s*function", code)
        # ten_ham = (...) =>
        mau3 = re.findall(r"\b([a-zA-Z_]\w*)\s*=\s*\([^)]*\)\s*=>", code)
        # const ten_ham = ...
        mau4 = re.findall(r"\b(?:const|let|var)\s+([a-zA-Z_]\w*)\s*=\s*(?:async\s+)?(?:function|\()", code)
        ham.update(mau1)
        ham.update(mau2)
        ham.update(mau3)
        ham.update(mau4)

    elif nn == "html":
        # onclick="ten_ham()"
        mau = re.findall(r'on\w+\s*=\s*["\']([a-zA-Z_]\w*)\s*\(', code)
        ham.update(mau)

    elif nn == "java":
        # public void ten_ham(...)
        mau = re.findall(
            r"\b(?:public|private|protected|static|final|\s)*"
            r"(?:\w+(?:<[^>]+>)?(?:\[\])?)\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*\{",
            code,
        )
        ham.update(mau)

    elif nn == "css":
        # Không có hàm — bỏ qua
        pass

    return ham


# ================================================================
# TRÍCH BIẾN TỪ CODE
# ================================================================
def _trich_bien(code, ngon_ngu):
    """Trích tên biến toàn cục từ code."""
    bien = set()
    if not code:
        return bien

    nn = (ngon_ngu or "").lower()

    if nn == "python":
        # ten_bien = ... (cấp 0, không thụt lề)
        mau = re.findall(r"^\s*([a-zA-Z_]\w*)\s*=", code, re.MULTILINE)
        bien.update(mau)

    elif nn in ("javascript", "js", "typescript", "ts"):
        # var/let/const ten_bien
        mau = re.findall(r"\b(?:var|let|const)\s+([a-zA-Z_]\w*)", code)
        bien.update(mau)

    elif nn == "html":
        # id="ten_bien"
        mau = re.findall(r'\bid\s*=\s*["\']([a-zA-Z_]\w*)["\']', code)
        bien.update(mau)

    return bien


# ================================================================
# TRÍCH IMPORT TỪ CODE
# ================================================================
def _trich_import(code, ngon_ngu):
    """Trích import từ code."""
    import_ = set()
    if not code:
        return import_

    nn = (ngon_ngu or "").lower()

    if nn == "python":
        # from X import Y
        mau = re.findall(r"^\s*from\s+[\w.]+\s+import\s+([\w,\s]+)", code, re.MULTILINE)
        for m in mau:
            for ten in m.split(","):
                ten = ten.strip()
                if ten:
                    import_.add(ten.split(" as ")[0].strip())
        # import X
        mau2 = re.findall(r"^\s*import\s+([\w.,\s]+)", code, re.MULTILINE)
        for m in mau2:
            for ten in m.split(","):
                ten = ten.strip().split(".")[0]
                if ten:
                    import_.add(ten)

    elif nn in ("javascript", "js"):
        # import { A, B } from 'X'
        mau = re.findall(r"import\s+\{([^}]+)\}", code)
        for m in mau:
            for ten in m.split(","):
                ten = ten.strip()
                if ten:
                    import_.add(ten)

    return import_


# ================================================================
# KIỂM TRA HÀM
# ================================================================
def kiem_tra_ham(code, hop_dong, ngon_ngu=None):
    """
    Kiểm tra hàm trong hợp đồng có trong code không.

    Trả về: (thieu: list, thua: list).
    """
    if not hop_dong:
        return [], []

    xuat_ra = hop_dong.get("xuat_ra", {})
    if not isinstance(xuat_ra, dict):
        return [], []

    ham_yeu_cau = xuat_ra.get("ham", [])
    if not ham_yeu_cau:
        return [], []

    ham_trong_code = _trich_ham(code, ngon_ngu or hop_dong.get("ngon_ngu", ""))

    ham_yeu_cau_ten = set()
    for h in ham_yeu_cau:
        if isinstance(h, dict):
            ten = h.get("ten", "")
        else:
            ten = str(h)
        if ten:
            ham_yeu_cau_ten.add(ten)

    thieu = [ten for ten in ham_yeu_cau_ten if ten not in ham_trong_code]
    thua = [ten for ten in ham_trong_code if ten not in ham_yeu_cau_ten and ten.startswith("_") is False and ten not in ("main", "init")]

    return thieu, thua


# ================================================================
# KIỂM TRA BIẾN
# ================================================================
def kiem_tra_bien(code, hop_dong, ngon_ngu=None):
    """Kiểm tra biến trong hợp đồng có trong code không."""
    if not hop_dong:
        return []

    xuat_ra = hop_dong.get("xuat_ra", {})
    if not isinstance(xuat_ra, dict):
        return []

    bien_yeu_cau = xuat_ra.get("bien", [])
    if not bien_yeu_cau:
        return []

    bien_trong_code = _trich_bien(code, ngon_ngu or hop_dong.get("ngon_ngu", ""))

    bien_yeu_cau_ten = set()
    for b in bien_yeu_cau:
        if isinstance(b, dict):
            ten = b.get("ten", "")
        else:
            ten = str(b)
        if ten:
            bien_yeu_cau_ten.add(ten)

    thieu = [ten for ten in bien_yeu_cau_ten if ten not in bien_trong_code]
    return thieu


# ================================================================
# KIỂM TRA IMPORT
# ================================================================
def kiem_tra_import(code, hop_dong, ngon_ngu=None):
    """Kiểm tra import trong hợp đồng có trong code không."""
    if not hop_dong:
        return []

    nhap_vao = hop_dong.get("nhap_vao", {})
    if not isinstance(nhap_vao, dict):
        return []

    goi_ham = nhap_vao.get("goi_ham", [])
    if not goi_ham:
        return []

    import_trong_code = _trich_import(code, ngon_ngu or hop_dong.get("ngon_ngu", ""))

    thieu = [ten for ten in goi_ham if ten not in import_trong_code]
    return thieu


# ================================================================
# HÀM CHÍNH — ĐỐI CHIẾU
# ================================================================
def doi_chieu(id_du_an, ten_file, code, ngon_ngu=None, hop_dong=None):
    """
    Đối chiếu code với hợp đồng.

    id_du_an: mã dự án.
    ten_file: tên file (VD "cart.js").
    code: code Tiểu não đã viết.
    ngon_ngu: ngôn ngữ (nếu không → đọc từ hợp đồng).
    hop_dong: hợp đồng (nếu không → tự đọc từ MongoDB).

    Trả về: {
        thanh_cong: bool,
        dat: bool,
        thieu_ham: [str],
        thua_ham: [str],
        thieu_bien: [str],
        thieu_import: [str],
        ly_do: str,
        so_loi: int,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "dat": True,
        "thieu_ham": [],
        "thua_ham": [],
        "thieu_bien": [],
        "thieu_import": [],
        "ly_do": "",
        "so_loi": 0,
    }

    if not id_du_an or not ten_file or not code:
        ket_qua["thanh_cong"] = False
        ket_qua["ly_do"] = "Thiếu id_du_an, ten_file hoặc code."
        return ket_qua

    # Lấy hợp đồng nếu chưa có
    if not hop_dong:
        try:
            from dai_nao.hop_dong import lay_hop_dong
            hop_dong = lay_hop_dong(id_du_an, ten_file)
        except ImportError:
            _ghi_log("loi", "hop_dong.py chưa có.")
            ket_qua["thanh_cong"] = False
            ket_qua["ly_do"] = "hop_dong.py chưa có."
            return ket_qua
        except Exception as e:
            _ghi_log("loi", f"Đọc hợp đồng lỗi: {e}")
            ket_qua["thanh_cong"] = False
            ket_qua["ly_do"] = f"Đọc hợp đồng lỗi: {e}"
            return ket_qua

    if not hop_dong:
        ket_qua["thanh_cong"] = False
        ket_qua["ly_do"] = f"Không có hợp đồng cho {ten_file}."
        return ket_qua

    # Ngôn ngữ
    nn = ngon_ngu or hop_dong.get("ngon_ngu", "")

    # 1. Kiểm tra hàm
    thieu_ham, thua_ham = kiem_tra_ham(code, hop_dong, nn)
    ket_qua["thieu_ham"] = thieu_ham
    ket_qua["thua_ham"] = thua_ham

    # 2. Kiểm tra biến
    thieu_bien = kiem_tra_bien(code, hop_dong, nn)
    ket_qua["thieu_bien"] = thieu_bien

    # 3. Kiểm tra import
    thieu_import = kiem_tra_import(code, hop_dong, nn)
    ket_qua["thieu_import"] = thieu_import

    # 4. Đánh giá
    so_loi = (
        len(thieu_ham)
        + len(thieu_bien)
        + len(thieu_import)
    )
    ket_qua["so_loi"] = so_loi

    if so_loi > 0:
        ket_qua["dat"] = False
        phan = []
        if thieu_ham:
            phan.append(f"Thiếu hàm: {', '.join(thieu_ham)}")
        if thieu_bien:
            phan.append(f"Thiếu biến: {', '.join(thieu_bien)}")
        if thieu_import:
            phan.append(f"Thiếu import: {', '.join(thieu_import)}")
        ket_qua["ly_do"] = " | ".join(phan)

        _ghi_log(
            "dai-nao",
            f"Đối chiếu {ten_file}: FAIL ({so_loi} lỗi) — {ket_qua['ly_do']}",
        )
    else:
        ket_qua["dat"] = True
        ket_qua["ly_do"] = f"Code {ten_file} khớp hợp đồng."
        _ghi_log("dai-nao", f"Đối chiếu {ten_file}: PASS")

    ket_qua["thanh_cong"] = True
    return ket_qua


# ================================================================
# TÓM TẮT LỖI CHO USER
# ================================================================
def tom_tat_loi(ket_qua):
    """Tóm tắt lỗi từ kết quả đối chiếu."""
    if not ket_qua:
        return ""

    if not ket_qua.get("thanh_cong"):
        return ket_qua.get("ly_do", "Lỗi đối chiếu.")

    if ket_qua.get("dat"):
        return "✅ Code khớp hợp đồng."

    phan = ["❌ Code KHÔNG khớp hợp đồng:"]

    if ket_qua.get("thieu_ham"):
        phan.append(f"  - Thiếu hàm: {', '.join(ket_qua['thieu_ham'])}")
    if ket_qua.get("thua_ham"):
        phan.append(f"  - Hàm thừa (có thể bỏ): {', '.join(ket_qua['thua_ham'])}")
    if ket_qua.get("thieu_bien"):
        phan.append(f"  - Thiếu biến: {', '.join(ket_qua['thieu_bien'])}")
    if ket_qua.get("thieu_import"):
        phan.append(f"  - Thiếu import: {', '.join(ket_qua['thieu_import'])}")

    return "\n".join(phan)


# ================================================================
# HÀM PHỤ
# ================================================================
def dat_khong(ket_qua):
    """Kiểm tra kết quả đối chiếu có đạt không."""
    if not ket_qua:
        return False
    return ket_qua.get("thanh_cong") and ket_qua.get("dat")


def so_loi(ket_qua):
    """Đếm số lỗi."""
    if not ket_qua:
        return 0
    return ket_qua.get("so_loi", 0)


def lay_danh_sach_loi(ket_qua):
    """Lấy danh sách lỗi dạng list."""
    if not ket_qua:
        return []

    loi = []
    for thieu_ham in ket_qua.get("thieu_ham", []):
        loi.append(f"Thiếu hàm: {thieu_ham}")
    for thieu_bien in ket_qua.get("thieu_bien", []):
        loi.append(f"Thiếu biến: {thieu_bien}")
    for thieu_import in ket_qua.get("thieu_import", []):
        loi.append(f"Thiếu import: {thieu_import}")

    return loi


# ================================================================
# ĐỐI CHIẾU NHIỀU FILE CÙNG LÚC
# ================================================================
def doi_chieu_nhieu(id_du_an, danh_sach_code):
    """
    Đối chiếu nhiều file cùng lúc.

    danh_sach_code: list [{"ten_file": str, "code": str, "ngon_ngu": str}, ...]

    Trả về: {
        thanh_cong: bool,
        tat_ca_dat: bool,
        ket_qua_tung_file: {ten_file: ket_qua},
    }
    """
    ket_qua = {
        "thanh_cong": True,
        "tat_ca_dat": True,
        "ket_qua_tung_file": {},
    }

    if not id_du_an or not danh_sach_code:
        ket_qua["thanh_cong"] = False
        ket_qua["tat_ca_dat"] = False
        return ket_qua

    for muc in danh_sach_code:
        if not isinstance(muc, dict):
            continue
        ten_file = muc.get("ten_file", "")
        code = muc.get("code", "")
        ngon_ngu = muc.get("ngon_ngu", "")

        if not ten_file or not code:
            continue

        kq = doi_chieu(id_du_an, ten_file, code, ngon_ngu)
        ket_qua["ket_qua_tung_file"][ten_file] = kq

        if not kq.get("dat"):
            ket_qua["tat_ca_dat"] = False

    return ket_qua
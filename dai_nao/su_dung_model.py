"""
su_dung_model.py - Cầu nối Đại não → Tiểu não Rồng Thần.

ĐÃ SỬA:
    - Thêm hàm sua_code_theo_loi() — gửi yêu cầu gốc + code cũ + lỗi
      + cách sửa + hợp đồng cho Tiểu não → nhận code đã sửa.
    - Thêm hàm sinh_code_cho_file() (như cũ).
"""

import time
import json
import re


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ================================================================
# GỌI MODEL TIỂU NÃO
# ================================================================
def _goi_model_tieu_nao(prompt, chu_so_huu=""):
    if not chu_so_huu:
        chu_so_huu = "khach"

    try:
        from tieu_nao.do_model import do_model
        ket_qua = do_model(chu_so_huu, prompt, loai_nao="tieu_boss")
    except ImportError:
        return {"thanh_cong": False, "ket_qua": "", "loi": "do_model.py chưa có."}
    except Exception as e:
        return {"thanh_cong": False, "ket_qua": "", "loi": f"Lỗi gọi Tiểu não: {e}"}

    if not ket_qua.get("thanh_cong"):
        return {
            "thanh_cong": False,
            "ket_qua": "",
            "loi": ket_qua.get("loi", "Không gọi được Tiểu não."),
        }

    return {
        "thanh_cong": True,
        "ket_qua": ket_qua.get("ket_qua", ""),
        "loi": "",
        "model": ket_qua.get("model", ""),
        "provider": ket_qua.get("provider", ""),
    }


# ================================================================
# TRÍCH JSON
# ================================================================
def _trich_json(chuoi):
    if not chuoi:
        return None
    chuoi = chuoi.strip()
    try:
        return json.loads(chuoi)
    except (json.JSONDecodeError, ValueError):
        pass
    mau_markdown = r"```(?:json)?\s*([\s\S]*?)```"
    khop = re.search(mau_markdown, chuoi)
    if khop:
        try:
            return json.loads(khop.group(1).strip())
        except (json.JSONDecodeError, ValueError):
            pass
    vi_tri_dau = chuoi.find("{")
    vi_tri_cuoi = chuoi.rfind("}")
    if vi_tri_dau >= 0 and vi_tri_cuoi > vi_tri_dau:
        try:
            return json.loads(chuoi[vi_tri_dau:vi_tri_cuoi + 1])
        except (json.JSONDecodeError, ValueError):
            pass
    return None


# ================================================================
# SINH CODE CHO 1 FILE (lần đầu)
# ================================================================
def sinh_code_cho_file(id_du_an, ten_file, ten_buoc, mo_ta_buoc,
                       chu_so_huu="", code_da_co="", ham_da_viet=None):
    """Sinh code lần đầu cho 1 file."""
    ket_qua = {
        "thanh_cong": False,
        "code": "",
        "ngon_ngu": "",
        "ham_da_viet": [],
        "ham_con_lai": [],
        "loi": "",
    }

    hop_dong = None
    try:
        from dai_nao.ghi_nho import lay_hop_dong
        hop_dong = lay_hop_dong(id_du_an, ten_file)
    except Exception as e:
        _ghi_log("loi", f"Lấy hợp đồng lỗi: {e}")

    ngon_ngu = _doan_ngon_ngu(ten_file)

    prompt = _tao_prompt_sinh_code(
        id_du_an=id_du_an,
        ten_file=ten_file,
        ten_buoc=ten_buoc,
        mo_ta_buoc=mo_ta_buoc,
        ngon_ngu=ngon_ngu,
        hop_dong=hop_dong,
        code_da_co=code_da_co,
    )

    kq = _goi_model_tieu_nao(prompt, chu_so_huu)
    if not kq.get("thanh_cong"):
        ket_qua["loi"] = kq.get("loi", "Không gọi được Tiểu não.")
        return ket_qua

    code = _trich_code(kq.get("ket_qua", ""))
    if not code:
        ket_qua["loi"] = "Tiểu não không trả về code."
        return ket_qua

    ham_da_viet_moi, ham_con_lai = _xac_dinh_tien_do(code, hop_dong, ham_da_viet or [])

    ket_qua["thanh_cong"] = True
    ket_qua["code"] = code
    ket_qua["ngon_ngu"] = ngon_ngu
    ket_qua["ham_da_viet"] = ham_da_viet_moi
    ket_qua["ham_con_lai"] = ham_con_lai
    ket_qua["model"] = kq.get("model", "")
    return ket_qua


# ================================================================
# SỬA CODE THEO LỖI CỤ THỂ
# ================================================================
def sua_code_theo_loi(id_du_an, ten_file, code_cu, loi_chi_tiet,
                      chu_so_huu=""):
    """
    Gửi Tiểu não: yêu cầu gốc + code cũ + lỗi + cách sửa + hợp đồng.
    Nhận code đã sửa.

    loi_chi_tiet: dict từ phan_tich_loi() chứa:
        - loai_loi
        - dong_bi_loi: {so_dong, noi_dung}
        - nguyen_nhan_goc
        - cach_sua: [list gợi ý]
        - code_sua_mau
    """
    ket_qua = {
        "thanh_cong": False,
        "code": "",
        "ngon_ngu": "",
        "loi": "",
    }

    if not code_cu:
        ket_qua["loi"] = "Code cũ rỗng."
        return ket_qua

    # Lấy hợp đồng
    hop_dong = None
    try:
        from dai_nao.ghi_nho import lay_hop_dong
        hop_dong = lay_hop_dong(id_du_an, ten_file)
    except Exception:
        pass

    # Lấy yêu cầu gốc từ snapshot
    yeu_cau_goc = ""
    ten_buoc = ""
    try:
        from dai_nao.snapshot import lay_snapshot
        snapshot = lay_snapshot(id_du_an)
        if snapshot:
            yeu_cau_goc = snapshot.get("yeu_cau_goc", "")
            for task in snapshot.get("da_chia", []):
                if task.get("file") == ten_file:
                    ten_buoc = task.get("ten", "")
                    break
    except Exception:
        pass

    ngon_ngu = _doan_ngon_ngu(ten_file)

    # Tạo prompt sửa lỗi
    prompt = _tao_prompt_sua_loi(
        yeu_cau_goc=yeu_cau_goc,
        ten_file=ten_file,
        ten_buoc=ten_buoc,
        ngon_ngu=ngon_ngu,
        code_cu=code_cu,
        loi_chi_tiet=loi_chi_tiet,
        hop_dong=hop_dong,
    )

    kq = _goi_model_tieu_nao(prompt, chu_so_huu)
    if not kq.get("thanh_cong"):
        ket_qua["loi"] = kq.get("loi", "Không gọi được Tiểu não.")
        return ket_qua

    code_moi = _trich_code(kq.get("ket_qua", ""))
    if not code_moi:
        ket_qua["loi"] = "Tiểu não không trả về code."
        return ket_qua

    ket_qua["thanh_cong"] = True
    ket_qua["code"] = code_moi
    ket_qua["ngon_ngu"] = ngon_ngu
    ket_qua["model"] = kq.get("model", "")
    return ket_qua


# ================================================================
# ĐOÁN NGÔN NGỮ
# ================================================================
def _doan_ngon_ngu(ten_file):
    if not ten_file:
        return "python"
    t = ten_file.lower()
    if t.endswith(".html"):
        return "html"
    if t.endswith(".css"):
        return "css"
    if t.endswith(".js") or t.endswith(".jsx") or t.endswith(".tsx"):
        return "javascript"
    if t.endswith(".ts"):
        return "typescript"
    if t.endswith(".py"):
        return "python"
    if t.endswith(".json"):
        return "json"
    if t.endswith(".md"):
        return "markdown"
    return "python"


# ================================================================
# PROMPT SINH CODE (lần đầu)
# ================================================================
def _tao_prompt_sinh_code(id_du_an, ten_file, ten_buoc, mo_ta_buoc,
                          ngon_ngu, hop_dong=None, code_da_co=""):
    phan = []
    phan.append(f"Viết code cho file: {ten_file}")
    phan.append(f"Ngôn ngữ: {ngon_ngu}")
    phan.append(f"Bước: {ten_buoc}")
    phan.append(f"Mô tả: {mo_ta_buoc}")

    if hop_dong:
        phan.append("")
        phan.append("═══════════════════════════")
        phan.append("HỢP ĐỒNG BẮT BUỘC:")
        phan.append("═══════════════════════════")
        phan.extend(_dinh_dang_hop_dong(hop_dong))

    if code_da_co:
        phan.append("")
        phan.append("═══════════════════════════")
        phan.append("CODE ĐÃ CÓ — ĐỌC STYLE TRƯỚC KHI VIẾT TIẾP:")
        phan.append("═══════════════════════════")
        phan.append(code_da_co[:2000])

    phan.append("")
    phan.append("═══════════════════════════")
    phan.append("YÊU CẦU OUTPUT:")
    phan.append("═══════════════════════════")
    phan.append("- Viết code ĐẦY ĐỦ, không cắt cụt.")
    phan.append("- Đúng tên hàm/biến trong hợp đồng.")
    phan.append("- Có comment giải thích.")
    phan.append(f"- CHỈ trả code trong ```{ngon_ngu}```, không giải thích ngoài.")
    if ngon_ngu == "html":
        phan.append("- KIỂM TRA: mỗi thẻ mở PHẢI có thẻ đóng tương ứng.")

    return "\n".join(phan)


# ================================================================
# PROMPT SỬA LỖI (gửi kèm lỗi + cách sửa)
# ================================================================
def _tao_prompt_sua_loi(yeu_cau_goc, ten_file, ten_buoc, ngon_ngu,
                        code_cu, loi_chi_tiet, hop_dong=None):
    """Tạo prompt sửa lỗi — gửi đầy đủ ngữ cảnh cho Tiểu não."""
    phan = []

    phan.append("Bạn cần SỬA LỖI trong code dưới đây.")
    phan.append("")

    # 1. YÊU CẦU GỐC
    if yeu_cau_goc:
        phan.append("═══════════════════════════")
        phan.append("YÊU CẦU GỐC CỦA DỰ ÁN:")
        phan.append("═══════════════════════════")
        phan.append(yeu_cau_goc)
        phan.append("")

    # 2. THÔNG TIN FILE
    phan.append("═══════════════════════════")
    phan.append("FILE CẦN SỬA:")
    phan.append("═══════════════════════════")
    phan.append(f"Tên file: {ten_file}")
    phan.append(f"Ngôn ngữ: {ngon_ngu}")
    if ten_buoc:
        phan.append(f"Bước: {ten_buoc}")
    phan.append("")

    # 3. LỖI CỤ THỂ
    phan.append("═══════════════════════════")
    phan.append("LỖI CỤ THỂ:")
    phan.append("═══════════════════════════")

    loai_loi = loi_chi_tiet.get("loai_loi", "")
    if loai_loi:
        phan.append(f"Loại lỗi: {loai_loi}")

    dong_bi_loi = loi_chi_tiet.get("dong_bi_loi") or {}
    if dong_bi_loi:
        phan.append(f"Dòng lỗi: {dong_bi_loi.get('so_dong', '?')}")
        phan.append(f"Nội dung dòng: {dong_bi_loi.get('noi_dung', '')}")

    nguyen_nhan = loi_chi_tiet.get("nguyen_nhan_goc", "")
    if nguyen_nhan:
        phan.append(f"Nguyên nhân: {nguyen_nhan}")

    thong_diep = loi_chi_tiet.get("thong_diep", "")
    if thong_diep:
        phan.append(f"Thông điệp lỗi: {thong_diep[:300]}")

    # 4. CÁCH SỬA
    cach_sua = loi_chi_tiet.get("cach_sua", [])
    if cach_sua:
        phan.append("")
        phan.append("═══════════════════════════")
        phan.append("CÁCH SỬA GỢI Ý:")
        phan.append("═══════════════════════════")
        for i, c in enumerate(cach_sua[:5], 1):
            phan.append(f"{i}. {c}")

    code_sua_mau = loi_chi_tiet.get("code_sua_mau", "")
    if not code_sua_mau:
        fix_da_cap = loi_chi_tiet.get("fix_da_cap", {})
        code_sua_mau = fix_da_cap.get("fix_chuan", "")

    if code_sua_mau:
        phan.append("")
        phan.append("Code mẫu sửa:")
        phan.append(code_sua_mau)

    # 5. HỢP ĐỒNG
    if hop_dong:
        phan.append("")
        phan.append("═══════════════════════════")
        phan.append("HỢP ĐỒNG — CODE MỚI PHẢI TUÂN THỦ:")
        phan.append("═══════════════════════════")
        phan.extend(_dinh_dang_hop_dong(hop_dong))

    # 6. CODE CŨ
    phan.append("")
    phan.append("═══════════════════════════")
    phan.append("CODE CŨ (CẦN SỬA):")
    phan.append("═══════════════════════════")
    phan.append(f"```{ngon_ngu}")
    phan.append(code_cu)
    phan.append("```")

    # 7. YÊU CẦU OUTPUT
    phan.append("")
    phan.append("═══════════════════════════")
    phan.append("YÊU CẦU:")
    phan.append("═══════════════════════════")
    phan.append("1. SỬA đúng lỗi đã báo — KHÔNG viết lại từ đầu.")
    phan.append("2. Giữ nguyên phần code đã đúng.")
    phan.append("3. Đảm bảo code mới chạy được, không có lỗi cú pháp.")
    phan.append("4. Đúng tên hàm/biến trong hợp đồng.")
    phan.append(f"5. CHỈ trả code trong ```{ngon_ngu}```, không giải thích ngoài.")

    if ngon_ngu == "html":
        phan.append("6. KIỂM TRA: mỗi thẻ mở PHẢI có thẻ đóng tương ứng.")

    return "\n".join(phan)


# ================================================================
# ĐỊNH DẠNG HỢP ĐỒNG
# ================================================================
def _dinh_dang_hop_dong(hop_dong):
    phan = []
    vai_tro = hop_dong.get("vai_tro", "")
    if vai_tro:
        phan.append(f"Vai trò: {vai_tro}")

    xuat_ra = hop_dong.get("xuat_ra", {})
    if isinstance(xuat_ra, dict):
        ham = xuat_ra.get("ham", [])
        if ham:
            phan.append("Hàm PHẢI có:")
            for h in ham:
                if isinstance(h, dict):
                    ten = h.get("ten", "?")
                    tham_so = h.get("tham_so", [])
                    tra_ve = h.get("tra_ve", "")
                    phan.append(f"  - {ten}({', '.join(tham_so)}) → {tra_ve}")
                else:
                    phan.append(f"  - {h}")

        bien = xuat_ra.get("bien", [])
        if bien:
            phan.append("Biến PHẢI có:")
            for b in bien:
                if isinstance(b, dict):
                    phan.append(f"  - {b.get('ten', '?')}: {b.get('kieu', '?')}")
                else:
                    phan.append(f"  - {b}")

        id_list = xuat_ra.get("id", [])
        if id_list:
            phan.append("ID PHẢI có:")
            for i in id_list:
                phan.append(f"  - {i}")

        class_list = xuat_ra.get("class", [])
        if class_list:
            phan.append("Class PHẢI có:")
            for c in class_list:
                phan.append(f"  - {c}")

    nhap_vao = hop_dong.get("nhap_vao", {})
    if isinstance(nhap_vao, dict):
        goi_ham = nhap_vao.get("goi_ham", [])
        if goi_ham:
            phan.append(f"Gọi hàm từ file khác: {', '.join(goi_ham)}")
        dung_bien = nhap_vao.get("dung_bien", [])
        if dung_bien:
            phan.append(f"Dùng biến: {', '.join(dung_bien)}")

    quy_uoc = hop_dong.get("quy_uoc", [])
    if quy_uoc:
        phan.append(f"Quy ước: {' | '.join(quy_uoc)}")

    return phan


# ================================================================
# TRÍCH CODE TỪ RESPONSE
# ================================================================
def _trich_code(chuoi):
    if not chuoi:
        return ""
    mau = r"```(?:\w+)?\s*([\s\S]*?)```"
    cac_khop = re.findall(mau, chuoi)
    if cac_khop:
        dai_nhat = max(cac_khop, key=len)
        return dai_nhat.strip()
    return chuoi.strip()


# ================================================================
# XÁC ĐỊNH TIẾN ĐỘ
# ================================================================
def _xac_dinh_tien_do(code, hop_dong, ham_da_viet_cu):
    ham_da_viet = set(ham_da_viet_cu or [])
    ham_con_lai = []
    if not code or not hop_dong:
        return list(ham_da_viet), ham_con_lai

    xuat_ra = hop_dong.get("xuat_ra", {})
    if not isinstance(xuat_ra, dict):
        return list(ham_da_viet), ham_con_lai

    for h in xuat_ra.get("ham", []):
        ten = h.get("ten", "") if isinstance(h, dict) else str(h)
        if not ten:
            continue
        if re.search(r"\b" + re.escape(ten) + r"\s*\(", code):
            ham_da_viet.add(ten)
        else:
            ham_con_lai.append(ten)

    return list(ham_da_viet), ham_con_lai


# ================================================================
# HÀM CŨ (tương thích)
# ================================================================
def su_dung_model(task, ngu_canh=None, chu_so_huu=""):
    if not task or not chu_so_huu:
        return None
    ten_file = task.get("ten_file", "")
    if ten_file:
        ket_qua = sinh_code_cho_file(
            id_du_an=task.get("id_du_an", ""),
            ten_file=ten_file,
            ten_buoc=task.get("noi_dung", ""),
            mo_ta_buoc=task.get("mo_ta", ""),
            chu_so_huu=chu_so_huu,
        )
        if ket_qua.get("thanh_cong"):
            return {
                "thanh_cong": True,
                "code": ket_qua["code"],
                "ngon_ngu": ket_qua["ngon_ngu"],
                "model": ket_qua.get("model", ""),
            }
    return None


def tieu_nao_san_sang():
    try:
        __import__("tieu_nao.do_model")
        return True
    except ImportError:
        return False
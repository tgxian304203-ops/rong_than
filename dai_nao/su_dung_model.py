"""
su_dung_model.py - Cầu nối Đại não → Tiểu não Rồng Thần.

ĐÃ SỬA:
    - Tiểu não đọc hợp đồng file + tiến độ trước khi sinh code.
    - Lưu tiến độ (dang_viet) sau mỗi lần sinh.
    - Sinh code trực tiếp từ brief, không qua ep_viet_truong.
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
# SINH CODE CHO 1 FILE (theo hợp đồng)
# ================================================================
def sinh_code_cho_file(id_du_an, ten_file, ten_buoc, mo_ta_buoc,
                       chu_so_huu="", code_da_co="", ham_da_viet=None):
    """
    Sinh code cho 1 file theo hợp đồng + tiến độ.

    Trả về: {
        thanh_cong: bool,
        code: str,
        ngon_ngu: str,
        ham_da_viet: [str],
        ham_con_lai: [str],
        loi: str,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "code": "",
        "ngon_ngu": "",
        "ham_da_viet": [],
        "ham_con_lai": [],
        "loi": "",
    }

    # 1. Đọc hợp đồng file
    hop_dong = None
    try:
        from dai_nao.ghi_nho import lay_hop_dong
        hop_dong = lay_hop_dong(id_du_an, ten_file)
    except Exception as e:
        _ghi_log("loi", f"Lấy hợp đồng lỗi: {e}")

    # 2. Đọc tiến độ
    dang_viet = None
    try:
        from dai_nao.snapshot import lay_dang_viet
        dang_viet = lay_dang_viet(id_du_an)
    except Exception:
        pass

    # 3. Xác định ngôn ngữ từ tên file
    ngon_ngu = _doan_ngon_ngu(ten_file)

    # 4. Xây prompt
    prompt = _tao_prompt_sinh_code(
        ten_file=ten_file,
        ten_buoc=ten_buoc,
        mo_ta_buoc=mo_ta_buoc,
        ngon_ngu=ngon_ngu,
        hop_dong=hop_dong,
        dang_viet=dang_viet,
        code_da_co=code_da_co,
    )

    # 5. Gọi Tiểu não
    kq = _goi_model_tieu_nao(prompt, chu_so_huu)
    if not kq.get("thanh_cong"):
        ket_qua["loi"] = kq.get("loi", "Không gọi được Tiểu não.")
        return ket_qua

    # 6. Trích code từ response
    code = _trich_code(kq.get("ket_qua", ""), ngon_ngu)
    if not code:
        ket_qua["loi"] = "Tiểu não không trả về code."
        return ket_qua

    # 7. Xác định hàm đã viết / còn lại
    ham_da_viet_moi, ham_con_lai = _xac_dinh_tien_do(
        code, hop_dong, ham_da_viet or []
    )

    ket_qua["thanh_cong"] = True
    ket_qua["code"] = code
    ket_qua["ngon_ngu"] = ngon_ngu
    ket_qua["ham_da_viet"] = ham_da_viet_moi
    ket_qua["ham_con_lai"] = ham_con_lai
    ket_qua["model"] = kq.get("model", "")

    return ket_qua


# ================================================================
# ĐOÁN NGÔN NGỮ TỪ TÊN FILE
# ================================================================
def _doan_ngon_ngu(ten_file):
    if not ten_file:
        return "python"
    t = ten_file.lower()
    if t.endswith(".html"):
        return "html"
    if t.endswith(".css"):
        return "css"
    if t.endswith(".js"):
        return "javascript"
    if t.endswith(".jsx") or t.endswith(".tsx"):
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
# TẠO PROMPT SINH CODE
# ================================================================
def _tao_prompt_sinh_code(ten_file, ten_buoc, mo_ta_buoc, ngon_ngu,
                          hop_dong=None, dang_viet=None, code_da_co=""):
    """Tạo prompt sinh code cho Tiểu não."""

    phan = []
    phan.append(f"Viết code cho file: {ten_file}")
    phan.append(f"Ngôn ngữ: {ngon_ngu}")
    phan.append(f"Bước: {ten_buoc}")
    phan.append(f"Mô tả: {mo_ta_buoc}")

    # Hợp đồng
    if hop_dong:
        phan.append("\n═══════════════════════════")
        phan.append("HỢP ĐỒNG BẮT BUỘC — PHẢI TUÂN THỦ:")
        phan.append("═══════════════════════════")

        vai_tro = hop_dong.get("vai_tro", "")
        if vai_tro:
            phan.append(f"Vai trò: {vai_tro}")

        xuat_ra = hop_dong.get("xuat_ra", {})
        if isinstance(xuat_ra, dict):
            ham = xuat_ra.get("ham", [])
            if ham:
                phan.append("Các hàm PHẢI có (đúng tên, đúng tham số):")
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
                phan.append("Các biến PHẢI có:")
                for b in bien:
                    if isinstance(b, dict):
                        phan.append(f"  - {b.get('ten', '?')}: {b.get('kieu', '?')}")
                    else:
                        phan.append(f"  - {b}")

            id_list = xuat_ra.get("id", [])
            if id_list:
                phan.append("Các id PHẢI có trong DOM:")
                for i in id_list:
                    phan.append(f"  - {i}")

            class_list = xuat_ra.get("class", [])
            if class_list:
                phan.append("Các class PHẢI có:")
                for c in class_list:
                    phan.append(f"  - {c}")

        nhap_vao = hop_dong.get("nhap_vao", {})
        if isinstance(nhap_vao, dict):
            goi_ham = nhap_vao.get("goi_ham", [])
            if goi_ham:
                phan.append("Cần gọi hàm từ file khác:")
                for g in goi_ham:
                    phan.append(f"  - {g}")

            dung_bien = nhap_vao.get("dung_bien", [])
            if dung_bien:
                phan.append("Cần dùng biến:")
                for d in dung_bien:
                    phan.append(f"  - {d}")

        quy_uoc = hop_dong.get("quy_uoc", [])
        if quy_uoc:
            phan.append("Quy ước:")
            for q in quy_uoc:
                phan.append(f"  - {q}")

    # Tiến độ viết dở
    if dang_viet and dang_viet.get("ten_file") == ten_file:
        da_viet_xong = dang_viet.get("da_viet_xong", [])
        if da_viet_xong:
            phan.append("\n═══════════════════════════")
            phan.append("TIẾN ĐỘ ĐÃ VIẾT — KHÔNG VIẾT LẠI:")
            phan.append("═══════════════════════════")
            phan.append(f"Đã viết xong: {', '.join(da_viet_xong)}")

    # Code đã có
    if code_da_co:
        phan.append("\n═══════════════════════════")
        phan.append("CODE ĐÃ CÓ — ĐỌC STYLE TRƯỚC KHI VIẾT TIẾP:")
        phan.append("═══════════════════════════")
        phan.append(code_da_co[:2000])

    phan.append("\n═══════════════════════════")
    phan.append("YÊU CẦU OUTPUT:")
    phan.append("═══════════════════════════")
    phan.append("- Viết code ĐẦY ĐỦ, không cắt cụt.")
    phan.append("- Đúng tên hàm/biến trong hợp đồng.")
    phan.append("- Có comment giải thích.")
    phan.append("- CHỈ trả code trong ```{ngôn_ngữ}```, không giải thích ngoài.")

    return "\n".join(phan)


# ================================================================
# TRÍCH CODE TỪ RESPONSE
# ================================================================
def _trich_code(chuoi, ngon_ngu="python"):
    if not chuoi:
        return ""

    mau = r"```(?:\w+)?\s*([\s\S]*?)```"
    cac_khop = re.findall(mau, chuoi)
    if cac_khop:
        # Lấy khối dài nhất
        dai_nhat = max(cac_khop, key=len)
        return dai_nhat.strip()

    # Không có ``` → trả toàn bộ
    return chuoi.strip()


# ================================================================
# XÁC ĐỊNH TIẾN ĐỘ (hàm nào đã viết)
# ================================================================
def _xac_dinh_tien_do(code, hop_dong, ham_da_viet_cu):
    """Xác định hàm nào đã viết xong trong code."""
    ham_da_viet = set(ham_da_viet_cu or [])
    ham_con_lai = []

    if not code:
        return list(ham_da_viet), ham_con_lai

    if not hop_dong:
        return list(ham_da_viet), ham_con_lai

    xuat_ra = hop_dong.get("xuat_ra", {})
    if not isinstance(xuat_ra, dict):
        return list(ham_da_viet), ham_con_lai

    ham_yeu_cau = xuat_ra.get("ham", [])

    for h in ham_yeu_cau:
        ten = h.get("ten", "") if isinstance(h, dict) else str(h)
        if not ten:
            continue

        # Kiểm tra code có hàm này không
        if re.search(r"\b" + re.escape(ten) + r"\s*\(", code):
            ham_da_viet.add(ten)
        else:
            ham_con_lai.append(ten)

    return list(ham_da_viet), ham_con_lai


# ================================================================
# HÀM CHÍNH CŨ (giữ để tương thích)
# ================================================================
def su_dung_model(task, ngu_canh=None, chu_so_huu=""):
    """
    Hàm cũ — gọi Tiểu não qua ep_viet_truong.
    Vẫn giữ để tương thích với xu_ly_task.py cũ.
    """
    if not task or not chu_so_huu:
        return None

    noi_dung = task.get("noi_dung", "")
    ten_file = task.get("ten_file", "")

    if ten_file:
        ket_qua = sinh_code_cho_file(
            id_du_an=task.get("id_du_an", ""),
            ten_file=ten_file,
            ten_buoc=noi_dung,
            mo_ta_buoc=task.get("mo_ta", noi_dung),
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

    return None


# ================================================================
# HÀM PHỤ
# ================================================================
def tieu_nao_san_sang():
    try:
        __import__("tieu_nao.do_model")
        return True
    except ImportError:
        return False


def tom_tat_ket_qua(ket_qua):
    if not ket_qua:
        return ""
    if not ket_qua.get("thanh_cong"):
        return f"❌ {ket_qua.get('loi', 'không rõ')}"
    return (
        f"✅ Code {len(ket_qua.get('code', ''))} ký tự, "
        f"hàm đã viết: {', '.join(ket_qua.get('ham_da_viet', []))}"
    )
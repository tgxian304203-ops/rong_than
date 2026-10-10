"""
sua_code.py - Sửa code lỗi bằng Model.

Nhiệm vụ:
    - Nhận code cũ + lỗi.
    - Tạo prompt sửa code.
    - Gọi Model qua goi_model.
    - Trích code mới.
    - Trả về code mới + cách sửa.

Nguyên tắc:
    - Model là công cụ — không giữ ngữ cảnh.
    - Ghi nhớ lỗi cũ để không lặp lại.
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
# SỬA CODE
# ================================================================
def sua_code(du_lieu):
    """
    Sửa code lỗi.

    du_lieu: {
        code_cu, loi, ngon_ngu,
        chu_so_huu, id_chat, lich_su
    }

    Trả về: {
        thanh_cong, code_moi, cach_sua?, loi?
    }
    """
    if not du_lieu:
        return {"thanh_cong": False, "loi": "Thiếu dữ liệu."}

    code_cu = du_lieu.get("code_cu", "")
    loi = du_lieu.get("loi", "")
    ngon_ngu = du_lieu.get("ngon_ngu", "python")

    if not code_cu:
        return {"thanh_cong": False, "loi": "Thiếu code cũ."}

    # Tạo prompt sửa code
    prompt = _tao_prompt_sua_code(code_cu, loi, ngon_ngu)

    du_lieu_prompt = dict(du_lieu)
    du_lieu_prompt["noi_dung"] = prompt

    # Gọi Model
    try:
        from tieu_nao.model.goi_model import goi_model
        ket_qua = goi_model(du_lieu_prompt)
    except Exception as e:
        _ghi_log("loi", f"Gọi Model sửa code lỗi: {e}")
        return {"thanh_cong": False, "loi": f"Gọi Model lỗi: {e}"}

    if not ket_qua.get("thanh_cong"):
        return ket_qua

    tra_loi = ket_qua.get("tra_loi", "")
    code_moi = _trich_code(tra_loi, ngon_ngu)

    if not code_moi:
        return {
            "thanh_cong": False,
            "loi": "Model không trả về code mới.",
            "tra_loi": tra_loi,
        }

    _ghi_log("tieu-nao", f"Sửa code OK: {len(code_moi)} ký tự")

    return {
        "thanh_cong": True,
        "code_moi": code_moi,
        "cach_sua": tra_loi[:300],
        "ngon_ngu": ngon_ngu,
    }


# ================================================================
# TẠO PROMPT SỬA CODE
# ================================================================
def _tao_prompt_sua_code(code_cu, loi, ngon_ngu):
    """Tạo prompt yêu cầu Model sửa code."""
    return f"""Code {ngon_ngu} sau bị lỗi:

{code_cu}

LỖI:
{loi}

Yêu cầu:
- Sửa code để không còn lỗi.
- Chỉ trả về code đã sửa trong khối markdown có ghi ngôn ngữ.
- Không giải thích dài dòng."""


# ================================================================
# TRÍCH CODE
# ================================================================
def _trich_code(tra_loi, ngon_ngu):
    """Trích code từ câu trả lời Model."""
    if not tra_loi:
        return ""

    bt = chr(96) * 3

    mau = bt + ngon_ngu + r"\s*([\s\S]*?)" + bt
    khop = re.search(mau, tra_loi, re.IGNORECASE)
    if khop:
        return khop.group(1).strip()

    mau = bt + r"(?:\w+)?\s*([\s\S]*?)" + bt
    khop = re.search(mau, tra_loi)
    if khop:
        return khop.group(1).strip()

    return ""


# ================================================================
# SỬA CODE NHANH
# ================================================================
def sua_code_nhanh(code_cu, loi, ngon_ngu="python",
                   chu_so_huu="khach", id_chat=""):
    """Sửa code nhanh."""
    return sua_code({
        "code_cu": code_cu,
        "loi": loi,
        "ngon_ngu": ngon_ngu,
        "chu_so_huu": chu_so_huu,
        "id_chat": id_chat,
    })


# ================================================================
# SỬA NHIỀU LẦN (LOOP)
# ================================================================
def sua_code_nhieu_lan(code_cu, loi, ngon_ngu="python",
                        chu_so_huu="khach", id_chat="",
                        so_lan_toi_da=3):
    """
    Sửa code nhiều lần cho đến khi hết lỗi (hoặc hết số lần).

    Trả về: { thanh_cong, code_moi, so_lan_sua, loi? }
    """
    code_hien_tai = code_cu
    loi_hien_tai = loi

    for lan in range(1, so_lan_toi_da + 1):
        ket_qua = sua_code({
            "code_cu": code_hien_tai,
            "loi": loi_hien_tai,
            "ngon_ngu": ngon_ngu,
            "chu_so_huu": chu_so_huu,
            "id_chat": id_chat,
        })

        if not ket_qua.get("thanh_cong"):
            return {
                "thanh_cong": False,
                "so_lan_sua": lan,
                "loi": ket_qua.get("loi", ""),
            }

        code_hien_tai = ket_qua.get("code_moi", code_hien_tai)

        # Kiểm tra cứng (syntax)
        try:
            from tieu_nao.kiem_tra_cung import kiem_tra_cung
            kiem_tra = kiem_tra_cung(code_hien_tai, ngon_ngu)
            if kiem_tra.get("thanh_cong"):
                return {
                    "thanh_cong": True,
                    "code_moi": code_hien_tai,
                    "so_lan_sua": lan,
                }
            loi_hien_tai = kiem_tra.get("loi", "")
        except Exception:
            pass

    return {
        "thanh_cong": False,
        "code_moi": code_hien_tai,
        "so_lan_sua": so_lan_toi_da,
        "loi": "Đã sửa nhiều lần nhưng vẫn còn lỗi.",
    }


# ================================================================
# TÓM TẮT
# ================================================================
def tom_tat(ket_qua):
    """Tạo chuỗi tóm tắt kết quả sửa code."""
    if not ket_qua:
        return ""
    if ket_qua.get("thanh_cong"):
        return f"✅ Sửa code OK: {len(ket_qua.get('code_moi', ''))} ký tự"
    return f"❌ Sửa code lỗi: {ket_qua.get('loi', '')[:100]}"
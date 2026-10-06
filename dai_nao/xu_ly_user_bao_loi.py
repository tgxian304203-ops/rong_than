"""
xu_ly_user_bao_loi.py - Tự chạy lại code khi user báo lỗi Rồng Thần.

Nhiệm vụ:
    - xu_ly_user_bao_loi(du_lieu): xử lý khi user báo lỗi.
    - tu_dong_sua_va_thu_lai(code, ngon_ngu): tự sửa và chạy lại.
    - _chay_sandbox(code, ngon_ngu): chạy code qua sandbox.

Luồng xử lý (theo Phần 3):
    1. User báo lỗi → Đại não nhận phản hồi.
    2. Đại não tự chạy lại code qua sandbox.
    3. Sandbox trả stderr.
    4. Đại não tự đọc lỗi (doc_loi.py).
    5. Đại não tự phân tích (phan_tich_loi.py).
    6. Nếu lỗi có trong từ điển → tự sửa (tu_sua_loi.py).
    7. Nếu lỗi lạ → gọi Tiểu não (su_dung_model.py).
    8. Thử lại với code đã sửa.
    9. Thành công → trả code mới. Thất bại → báo user.
    10. Cập nhật cây (ghi_nho.py).

Quy tắc:
    - KHÔNG hỏi user lỗi ở đâu.
    - Tự chạy, tự đọc, tự phân tích, tự sửa.
    - Tối đa 3 lần thử lại.
    - Mỗi lần thử ghi log.

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import re
import time


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
# HẰNG SỐ
# ================================================================
SO_LAN_THU_TOI_DA = 3
TU_KHOA_BAO_LOI = [
    "lỗi", "sai", "không chạy", "không đúng", "bug",
    "error", "fail", "không hoạt động", "chạy không được",
    "bị lỗi", "gặp lỗi", "sửa lỗi", "sửa giúp",
    "fix", "debug", "không ra kết quả", "không như ý",
    "chạy lỗi", "báo lỗi", "hỏng", "hư",
]


# ================================================================
# PHÁT HIỆN USER ĐANG BÁO LỖI
# ================================================================
def la_user_bao_loi(noi_dung):
    """
    Kiểm tra tin nhắn có phải user đang báo lỗi không.

    Trả về: True/False
    """
    if not noi_dung:
        return False

    t = noi_dung.lower()
    return any(tk in t for tk in TU_KHOA_BAO_LOI)


# ================================================================
# CHẠY SANDBOX
# ================================================================
def _chay_sandbox(code, ngon_ngu="python"):
    """
    Chạy code qua sandbox.

    Trả về:
    {
        thanh_cong: bool,
        stdout: str,
        stderr: str,
        thoi_gian: float,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "stdout": "",
        "stderr": "",
        "thoi_gian": 0.0,
    }

    if not code:
        ket_qua["stderr"] = "Code rỗng."
        return ket_qua

    thoi_gian_bat_dau = time.time()

    try:
        if ngon_ngu == "html":
            from sanbox.chay_html import chay_html
            ket_qua_tho = chay_html({"code": code})
        else:
            from sanbox.chay_python import chay_python
            ket_qua_tho = chay_python({"code": code})

        if isinstance(ket_qua_tho, dict):
            ket_qua["thanh_cong"] = bool(ket_qua_tho.get("thanh_cong", False))
            ket_qua["stdout"] = ket_qua_tho.get("stdout", "") or ""
            ket_qua["stderr"] = ket_qua_tho.get("stderr", "") or ""

    except ImportError:
        ket_qua["stderr"] = "Sandbox chưa có (sanbox/chay_python.py hoặc chay_html.py)."
    except Exception as e:
        ket_qua["stderr"] = f"Sandbox lỗi: {e}"

    ket_qua["thoi_gian"] = round(time.time() - thoi_gian_bat_dau, 3)
    return ket_qua


# ================================================================
# TỰ SỬA VÀ THỬ LẠI
# ================================================================
def tu_dong_sua_va_thu_lai(code, ngon_ngu="python"):
    """
    Tự sửa lỗi và chạy lại.

    code: code gốc.
    ngon_ngu: "python" | "html".

    Trả về:
    {
        thanh_cong: bool,
        code_moi: str,
        so_lan_thu: int,
        lich_su: list,       # [{lan_thu, thanh_cong, stderr, cach_sua, nguon}]
        loi_cuoi: str,       # lỗi còn lại (nếu thất bại)
        thoi_gian_tong: float,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "code_moi": code,
        "so_lan_thu": 0,
        "lich_su": [],
        "loi_cuoi": "",
        "thoi_gian_tong": 0.0,
    }

    if not code:
        ket_qua["loi_cuoi"] = "Code rỗng."
        return ket_qua

    thoi_gian_bat_dau = time.time()
    code_hien_tai = code

    for lan_thu in range(1, SO_LAN_THU_TOI_DA + 1):
        ket_qua["so_lan_thu"] = lan_thu
        _ghi_log("dai-nao", f"Thử lần {lan_thu}/{SO_LAN_THU_TOI_DA}")

        # 1. Chạy sandbox
        ket_qua_sandbox = _chay_sandbox(code_hien_tai, ngon_ngu)

        lich_su_lan = {
            "lan_thu": lan_thu,
            "thanh_cong": ket_qua_sandbox.get("thanh_cong"),
            "stderr": ket_qua_sandbox.get("stderr", "")[:500],
            "cach_sua": "",
            "nguon": "",
        }

        # 2. Thành công → dừng
        if ket_qua_sandbox.get("thanh_cong"):
            ket_qua["thanh_cong"] = True
            ket_qua["code_moi"] = code_hien_tai
            ket_qua["lich_su"].append(lich_su_lan)
            _ghi_log("dai-nao", f"Thành công sau {lan_thu} lần thử.")
            break

        # 3. Thất bại → đọc lỗi
        stderr = ket_qua_sandbox.get("stderr", "")
        if not stderr:
            ket_qua["loi_cuoi"] = "Sandbox không trả lỗi cụ thể."
            ket_qua["lich_su"].append(lich_su_lan)
            break

        # 4. Tự sửa
        ket_qua_sua = _tu_sua(code_hien_tai, stderr, ngon_ngu)

        lich_su_lan["cach_sua"] = ket_qua_sua.get("cach_sua", "")
        lich_su_lan["nguon"] = ket_qua_sua.get("nguon", "")

        if ket_qua_sua.get("thanh_cong") and ket_qua_sua.get("code_moi"):
            code_hien_tai = ket_qua_sua["code_moi"]
            ket_qua["lich_su"].append(lich_su_lan)
            continue
        else:
            # Không sửa được → thử gọi Tiểu não
            ket_qua_tieu_nao = _goi_tieu_nao_sua(code_hien_tai, stderr, ngon_ngu)
            if ket_qua_tieu_nao.get("thanh_cong") and ket_qua_tieu_nao.get("code_moi"):
                code_hien_tai = ket_qua_tieu_nao["code_moi"]
                lich_su_lan["cach_sua"] = "Tiểu não sinh node mới"
                lich_su_lan["nguon"] = "tieu_nao"
            else:
                lich_su_lan["cach_sua"] = "Không sửa được"
                lich_su_lan["nguon"] = ""

            ket_qua["lich_su"].append(lich_su_lan)

            # Không sửa được lần này → có thể vẫn thử lần sau
            if lan_thu >= SO_LAN_THU_TOI_DA:
                ket_qua["loi_cuoi"] = stderr
                break

    ket_qua["thoi_gian_tong"] = round(time.time() - thoi_gian_bat_dau, 3)

    if not ket_qua["thanh_cong"]:
        _ghi_log(
            "loi",
            f"Tự sửa thất bại sau {ket_qua['so_lan_thu']} lần thử.",
        )

    return ket_qua


# ================================================================
# TỰ SỬA (DÙNG tu_sua_loi.py)
# ================================================================
def _tu_sua(code, stderr, ngon_ngu):
    """Gọi tu_sua_loi.py để sửa."""
    try:
        from dai_nao.tu_sua_loi import tu_sua_loi
        return tu_sua_loi(code, stderr, ngon_ngu)
    except ImportError:
        return {"thanh_cong": False}
    except Exception as e:
        _ghi_log("loi", f"Tự sửa lỗi: {e}")
        return {"thanh_cong": False}


# ================================================================
# GỌI TIỂU NÃO ĐỂ SỬA
# ================================================================
def _goi_tieu_nao_sua(code, stderr, ngon_ngu):
    """
    Gọi Tiểu não khi không tự sửa được.
    Tiểu não sinh node mới, node mới có code sửa.
    """
    try:
        from dai_nao.su_dung_model import su_dung_model
        from dai_nao.doc_loi import doc_loi

        thong_tin_loi = doc_loi(stderr)
        task = {
            "noi_dung": f"Sửa lỗi {thong_tin_loi.get('loai_loi', '')} trong code",
            "yeu_to": {},
            "loai_task": {"linh_vuc": "bug"},
            "code": code,
            "loi": stderr,
        }

        node_moi = su_dung_model(task, {})
        if not node_moi:
            return {"thanh_cong": False}

        # Lấy code từ node
        if hasattr(node_moi, "hanh_dong"):
            hanh_dong = node_moi.hanh_dong or {}
        else:
            hanh_dong = (node_moi or {}).get("hanh_dong", {}) or {}

        code_moi = hanh_dong.get("code", "")
        if code_moi:
            return {"thanh_cong": True, "code_moi": code_moi}

    except ImportError:
        pass
    except Exception as e:
        _ghi_log("loi", f"Gọi Tiểu não sửa lỗi: {e}")

    return {"thanh_cong": False}


# ================================================================
# CẬP NHẬT CÂY (kho 2)
# ================================================================
def _cap_nhat_cay_sau_khi_sua(ket_qua_sua, loai_loi="", task_goc=""):
    """
    Cập nhật cây quyết định sau khi sửa thành công.
    """
    if not ket_qua_sua or not ket_qua_sua.get("thanh_cong"):
        return False

    try:
        from dai_nao.ghi_nho import luu_lich_su_hoc
        luu_lich_su_hoc({
            "loai": "user_bao_loi",
            "loai_loi": loai_loi,
            "task_goc": task_goc[:200],
            "code_moi": (ket_qua_sua.get("code_moi") or "")[:500],
            "so_lan_thu": ket_qua_sua.get("so_lan_thu"),
            "thoi_gian_tong": ket_qua_sua.get("thoi_gian_tong"),
            "thoi_gian": int(time.time()),
        })
        return True
    except Exception as e:
        _ghi_log("loi", f"Không cập nhật cây: {e}")
        return False


# ================================================================
# HÀM CHÍNH
# ================================================================
def xu_ly_user_bao_loi(du_lieu):
    """
    Xử lý khi user báo lỗi.

    du_lieu: {
        noi_dung: str,         # tin nhắn user báo lỗi
        code: str,             # code gốc cần sửa
        ngon_ngu: str,         # "python" | "html"
        chu_so_huu: str,       # tên đăng nhập
        task_goc: str,         # nội dung task gốc
    }

    Trả về:
    {
        thanh_cong: bool,
        tra_loi: str,          # câu trả lời cho user
        code: str,             # code đã sửa (nếu thành công)
        ngon_ngu: str,
        so_lan_thu: int,
        lich_su: list,
        loi: str?,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "tra_loi": "",
        "code": "",
        "ngon_ngu": "",
        "so_lan_thu": 0,
        "lich_su": [],
        "loi": "",
    }

    if not du_lieu:
        ket_qua["loi"] = "Không có dữ liệu."
        return ket_qua

    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    code = du_lieu.get("code") or ""
    ngon_ngu = du_lieu.get("ngon_ngu") or "python"
    chu_so_huu = du_lieu.get("chu_so_huu") or "khach"
    task_goc = du_lieu.get("task_goc") or ""

    if not code:
        ket_qua["tra_loi"] = (
            "Bạn chưa có code để sửa. Hãy gửi code (hoặc mô tả lỗi cụ thể) "
            "để ta cùng sửa nhé 🐉"
        )
        return ket_qua

    _ghi_log(
        "dai-nao",
        f"User {chu_so_huu} báo lỗi: {noi_dung[:80]}",
    )

    # 1. Tự chạy lại + tự sửa
    ket_qua_sua = tu_dong_sua_va_thu_lai(code, ngon_ngu)

    ket_qua["so_lan_thu"] = ket_qua_sua.get("so_lan_thu", 0)
    ket_qua["lich_su"] = ket_qua_sua.get("lich_su", [])
    ket_qua["ngon_ngu"] = ngon_ngu

    # 2. Thành công
    if ket_qua_sua.get("thanh_cong"):
        ket_qua["thanh_cong"] = True
        ket_qua["code"] = ket_qua_sua.get("code_moi", "")

        if ket_qua["so_lan_thu"] == 1:
            ket_qua["tra_loi"] = (
                "✅ Code đã chạy lại thành công, không cần sửa gì! "
                "Có thể lỗi do dữ liệu đầu vào. Bạn thử lại xem 🐉"
            )
        else:
            ket_qua["tra_loi"] = (
                f"✅ Ta đã tự sửa và chạy lại thành công sau "
                f"{ket_qua['so_lan_thu']} lần thử. Đây là code đã sửa:"
            )

        # Cập nhật cây
        _cap_nhat_cay_sau_khi_sua(
            ket_qua_sua,
            loai_loi=_trich_loai_loi_tu_lich_su(ket_qua["lich_su"]),
            task_goc=task_goc,
        )

        return ket_qua

    # 3. Thất bại
    ket_qua["loi"] = ket_qua_sua.get("loi_cuoi", "")
    ket_qua["tra_loi"] = _tao_tra_loi_that_bai(ket_qua_sua, noi_dung)

    return ket_qua


# ================================================================
# TẠO CÂU TRẢ LỜI KHI THẤT BẠI
# ================================================================
def _tao_tra_loi_that_bai(ket_qua_sua, noi_dung_user):
    """Tạo câu trả lời khi không sửa được."""
    phan = []
    phan.append("🐉 Ta đã thử sửa nhưng chưa thành công sau "
                f"{ket_qua_sua.get('so_lan_thu', 0)} lần.")

    lich_su = ket_qua_sua.get("lich_su", [])
    if lich_su:
        phan.append("\n📋 Lịch sử thử:")
        for item in lich_su[-3:]:
            lan = item.get("lan_thu", "?")
            ok = "✅" if item.get("thanh_cong") else "❌"
            cach = item.get("cach_sua", "không có")
            phan.append(f"  Lần {lan}: {ok} {cach[:60]}")

    loi_cuoi = ket_qua_sua.get("loi_cuoi", "")
    if loi_cuoi:
        phan.append(f"\n🔴 Lỗi cuối: {loi_cuoi[:200]}")

    phan.append(
        "\n💡 Bạn có thể:\n"
        "  1. Gửi lại lỗi cụ thể hơn.\n"
        "  2. Dán đoạn code bị lỗi.\n"
        "  3. Nói rõ môi trường chạy (Python/HTML...)."
    )

    return "\n".join(phan)


# ================================================================
# TRÍCH LOẠI LỖI TỪ LỊCH SỬ
# ================================================================
def _trich_loai_loi_tu_lich_su(lich_su):
    """Trích loại lỗi đầu tiên từ lịch sử."""
    if not lich_su:
        return ""
    for item in lich_su:
        stderr = item.get("stderr", "")
        if stderr:
            try:
                from dai_nao.doc_loi import lay_loai_loi
                return lay_loai_loi(stderr)
            except ImportError:
                return ""
    return ""


# ================================================================
# HÀM PHỤ: KIỂM TRA NHANH
# ================================================================
def can_sua_loi(noi_dung, code=None):
    """
    Kiểm tra có cần vào luồng sửa lỗi không.
    Trả về True nếu:
        - User báo lỗi (từ khóa).
        - VÀ có code để sửa.
    """
    if not la_user_bao_loi(noi_dung):
        return False
    return bool(code)


# ================================================================
# HÀM PHỤ: TÓM TẮT LỊCH SỬ
# ================================================================
def tom_tat_lich_su(lich_su):
    """Tạo chuỗi tóm tắt lịch sử thử."""
    if not lich_su:
        return ""

    phan = []
    for item in lich_su:
        lan = item.get("lan_thu", "?")
        ok = "✅" if item.get("thanh_cong") else "❌"
        cach = item.get("cach_sua", "")
        nguon = item.get("nguon", "")
        phan.append(f"Lần {lan}: {ok} {cach[:50]} [{nguon}]")

    return "\n".join(phan)
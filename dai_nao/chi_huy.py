"""
chi_huy.py - Đại não gọi model riêng Rồng Thần.

ĐÃ SỬA:
    - Boss viết TRƯỜNG đầy đủ: thuat_toan.buoc + hop_dong_file.
    - Bỏ chia_task riêng — gộp vào viết trường.
"""

import re
import json
import time


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


# ================================================================
# KIỂM TRA CÓ CẦN BOSS KHÔNG
# ================================================================
def can_boss(noi_dung):
    if not noi_dung:
        return False

    noi_dung_lower = noi_dung.lower().strip()

    if len(noi_dung_lower) < 10:
        return False

    for tk in ("hôm nay", "bây giờ", "mấy giờ", "ngày mấy"):
        if tk in noi_dung_lower:
            return False

    for tk in ("chào", "hello", "hi ", "cảm ơn"):
        if noi_dung_lower.startswith(tk):
            return False

    tu_hanh_dong = ("làm", "tạo", "xây", "viết", "dựng", "thiết kế", "code", "lập trình")
    tu_doi_tuong = (
        "web", "app", "ứng dụng", "dự án", "game", "tool", "công cụ",
        "hệ thống", "phần mềm", "website", "trang web", "api", "bot",
        "chatbot", "ai", "trò chơi", "quản lý", "sinh viên", "bán hàng",
        "thẻ bài", "shop", "cửa hàng", "landing", "portfolio",
    )

    co_hanh_dong = any(tk in noi_dung_lower for tk in tu_hanh_dong)
    co_doi_tuong = any(tk in noi_dung_lower for tk in tu_doi_tuong)

    if co_hanh_dong and co_doi_tuong:
        return True

    if len(noi_dung_lower) > 25 and co_hanh_dong:
        return True

    so_dau_cau = (
        noi_dung_lower.count(",") +
        noi_dung_lower.count(";") +
        noi_dung_lower.count(" và ")
    )
    if so_dau_cau >= 3 and co_hanh_dong:
        return True

    return False


# ================================================================
# NHẬN DIỆN LỆNH "SỐ N"
# ================================================================
def la_lenh_lam_task(noi_dung):
    if not noi_dung:
        return None

    t = noi_dung.lower().strip()

    mau = r"^(?:số|task|làm\s+task|làm|bắt\s+đầu\s+từ)\s+(\d+)"
    khop = re.match(mau, t)
    if khop:
        try:
            return int(khop.group(1))
        except ValueError:
            return None

    khop2 = re.match(r"^(\d+)$", t)
    if khop2:
        try:
            return int(khop2.group(1))
        except ValueError:
            return None

    return None


# ================================================================
# GỌI MODEL BOSS
# ================================================================
def _goi_model_boss(prompt, chu_so_huu=""):
    if not chu_so_huu:
        chu_so_huu = "khach"

    try:
        from tieu_nao.do_model import do_model
        ket_qua = do_model(chu_so_huu, prompt, loai_nao="boss")
    except ImportError:
        return {"thanh_cong": False, "ket_qua": "", "loi": "do_model.py chưa có."}
    except Exception as e:
        return {"thanh_cong": False, "ket_qua": "", "loi": f"Lỗi gọi Boss: {e}"}

    if not ket_qua.get("thanh_cong"):
        return {
            "thanh_cong": False,
            "ket_qua": "",
            "loi": ket_qua.get("loi", "Không gọi được Boss."),
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

    try:
        from dai_nao.khuon import trich_json_tu_response
        return trich_json_tu_response(chuoi)
    except ImportError:
        pass

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
# BOSS VIẾT TRƯỜNG ĐẦY ĐỦ
# ================================================================
def viet_truong(noi_dung, chu_so_huu=""):
    """
    Boss viết trường đầy đủ cho dự án:
        - ten, linh_vuc, cach_giai_phap
        - thuat_toan.buoc (danh sách bước)
        - hop_dong_file (hợp đồng từng file)
    """
    ket_qua = {
        "thanh_cong": False,
        "truong": {},
        "loi": "",
    }

    if not noi_dung:
        ket_qua["loi"] = "Nội dung rỗng."
        return ket_qua

    prompt = f"""Bạn là chuyên gia phân tích dự án. Đọc yêu cầu user và viết trường theo JSON.

YÊU CẦU: "{noi_dung}"

Trả về JSON (CHỈ JSON):
{{
  "ten": "Tên dự án ngắn gọn",
  "linh_vuc": "code | toán | văn | ...",
  "cach_giai_phap": "làm_web | làm_app | làm_game | ...",
  "thuat_toan": {{
    "buoc": [
      "1. Tạo file index.html",
      "2. Tạo file style.css",
      "3. Tạo file cart.js"
    ]
  }},
  "hop_dong_file": {{
    "index.html": {{
      "vai_tro": "trang chủ hiển thị sản phẩm",
      "xuat_ra": {{"id": ["app", "product-list"]}},
      "nhap_vao": {{"tu_file": ["style.css", "cart.js"]}}
    }},
    "cart.js": {{
      "vai_tro": "xử lý giỏ hàng",
      "xuat_ra": {{
        "ham": [
          {{"ten": "themVaoGio", "tham_so": ["sanPham"], "tra_ve": "void"}},
          {{"ten": "xoaKhoiGio", "tham_so": ["id"], "tra_ve": "void"}},
          {{"ten": "tinhTongTien", "tham_so": [], "tra_ve": "number"}}
        ]
      }},
      "nhap_vao": {{"dung_bien": ["localStorage.cart"]}},
      "quy_uoc": ["camelCase", "ES modules"]
    }}
  }},
  "quy_uoc_chung": {{
    "ngon_ngu": "HTML + JavaScript",
    "khong_dung": ["jQuery"],
    "ten_bien": "camelCase"
  }}
}}

QUY TẮC:
1. thuat_toan.buoc: liệt kê TỪNG BƯỚC cụ thể (mỗi bước 1 file hoặc 1 chức năng).
2. hop_dong_file: với MỖI file trong buoc, viết hợp đồng:
   - vai_tro: file làm gì
   - xuat_ra: hàm/biến/id mà file này cung cấp
   - nhap_vao: file cần gì từ nơi khác
   - quy_uoc: quy ước viết file này
3. Nếu file là HTML → xuat_ra có "id" (các id trong DOM).
4. Nếu file là JS → xuat_ra có "ham" (các hàm xuất ra).
5. Nếu file là CSS → xuat_ra có "class" (các class chính).
6. Số bước và số file tùy dự án.

CHỈ TRẢ VỀ JSON."""

    kq = _goi_model_boss(prompt, chu_so_huu)
    if not kq.get("thanh_cong"):
        ket_qua["loi"] = kq.get("loi", "Không gọi được Boss.")
        return ket_qua

    du_lieu = _trich_json(kq.get("ket_qua", ""))
    if not du_lieu:
        ket_qua["loi"] = "Boss trả về không phải JSON."
        return ket_qua

    ket_qua["thanh_cong"] = True
    ket_qua["truong"] = du_lieu
    ket_qua["model"] = kq.get("model", "")

    _ghi_log(
        "dai-nao",
        f"Boss viết trường: {len(du_lieu.get('thuat_toan', {}).get('buoc', []))} bước, "
        f"{len(du_lieu.get('hop_dong_file', {}))} file",
    )

    return ket_qua


# ================================================================
# LƯU TRƯỜNG + HỢP ĐỒNG VÀO KHO
# ================================================================
def luu_truong_va_hop_dong(ten_tk, id_du_an, truong):
    """Lưu trường vào snapshot + hợp đồng file vào collection hop_dong."""
    if not ten_tk or not id_du_an or not truong:
        return False

    try:
        from dai_nao.snapshot import tao_snapshot
        import time as _time

        # Chuẩn bị danh sách task
        ds_buoc = truong.get("thuat_toan", {}).get("buoc", [])
        hop_dong_file = truong.get("hop_dong_file", {})

        da_chia = []
        for i, buoc in enumerate(ds_buoc, 1):
            # Tìm file liên quan
            ten_file = ""
            for f in hop_dong_file.keys():
                if f.lower() in buoc.lower():
                    ten_file = f
                    break

            da_chia.append({
                "so": i,
                "ten": buoc,
                "file": ten_file,
                "trang_thai": "chua_lam",
                "mo_ta": buoc,
            })

        snapshot = tao_snapshot(id_du_an, {
            "yeu_cau_goc": truong.get("ten", ""),
            "loai_du_an": truong.get("linh_vuc", "code"),
            "da_chia": da_chia,
            "hop_dong_da_chot": hop_dong_file,
            "quy_uoc_chung": truong.get("quy_uoc_chung", {}),
        })

        if not snapshot:
            return False

        # Lưu hợp đồng vào collection hop_dong
        try:
            from dai_nao.ghi_nho import luu_hop_dong
            for ten_file, hd in hop_dong_file.items():
                if not isinstance(hd, dict):
                    continue
                hd_full = dict(hd)
                hd_full["id_du_an"] = id_du_an
                hd_full["ten_file"] = ten_file
                hd_full["trang_thai"] = "chot"
                luu_hop_dong(hd_full)
        except Exception as e:
            _ghi_log("loi", f"Lỗi lưu hợp đồng: {e}")

        # Lưu dự án vào kho 1
        try:
            from dai_nao.ghi_nho import luu_du_an
            luu_du_an({
                "id": id_du_an,
                "ten": truong.get("ten", "Dự án Boss"),
                "chu_so_huu": ten_tk,
                "loai": "du_an",
                "ngay_tao": int(_time.time() * 1000),
                "boss_tao": True,
            })
        except Exception as e:
            _ghi_log("loi", f"Lỗi lưu dự án kho 1: {e}")

        return True

    except Exception as e:
        _ghi_log("loi", f"Lưu trường + hợp đồng lỗi: {e}")
        return False


# ================================================================
# TẠO PHẢN HỒI CHO USER
# ================================================================
def tao_phan_hoi(truong, id_du_an):
    """Tạo phản hồi cho user từ trường Boss viết."""
    if not truong:
        return ""

    ten = truong.get("ten", "")
    ds_buoc = truong.get("thuat_toan", {}).get("buoc", [])

    phan = []
    phan.append(f"🔥 Boss đã phân tích dự án: **{ten}**")
    phan.append("")
    phan.append(f"📊 **Số bước**: {len(ds_buoc)}")
    phan.append(f"🆔 **Mã dự án**: `{id_du_an}`")
    phan.append("")

    if ds_buoc:
        phan.append("**📝 DANH SÁCH BƯỚC:**")
        for i, buoc in enumerate(ds_buoc, 1):
            phan.append(f"  {i}. {buoc}")

    phan.append("")
    phan.append("💡 Gõ **Số 1** để bắt đầu bước 1.")

    return "\n".join(phan)


# ================================================================
# HÀM CHÍNH
# ================================================================
def chi_huy(du_lieu):
    ket_qua = {
        "thanh_cong": False,
        "can_boss": False,
        "truong": {},
        "id_du_an": "",
        "loi": "",
    }

    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    chu_so_huu = du_lieu.get("chu_so_huu", "khach")

    if not noi_dung:
        ket_qua["loi"] = "Nội dung rỗng."
        return ket_qua

    if not can_boss(noi_dung):
        ket_qua["can_boss"] = False
        ket_qua["thanh_cong"] = True
        return ket_qua

    ket_qua["can_boss"] = True

    # Boss viết trường
    kq_truong = viet_truong(noi_dung, chu_so_huu)

    if not kq_truong.get("thanh_cong"):
        ket_qua["loi"] = kq_truong.get("loi", "Boss không viết được trường.")
        _ghi_log("dai-nao", f"Boss thất bại: {ket_qua['loi']}")
        return ket_qua

    truong = kq_truong.get("truong", {})

    # Tạo id dự án
    import secrets
    id_du_an = "du-an-" + secrets.token_hex(4)

    # Lưu trường + hợp đồng
    luu_truong_va_hop_dong(chu_so_huu, id_du_an, truong)

    ket_qua["thanh_cong"] = True
    ket_qua["truong"] = truong
    ket_qua["id_du_an"] = id_du_an
    ket_qua["model"] = kq_truong.get("model", "")

    return ket_qua


# ================================================================
# LẤY TRƯỜNG THEO SỐ BƯỚC (Cây tạo lệnh)
# ================================================================
def lay_buoc_theo_so(id_du_an, so_buoc):
    """Lấy bước N từ snapshot để gửi Tiểu não."""
    try:
        from dai_nao.snapshot import lay_snapshot
        snapshot = lay_snapshot(id_du_an)
        if not snapshot:
            return None

        da_chia = snapshot.get("da_chia", [])
        for task in da_chia:
            if task.get("so") == so_buoc:
                return task
        return None
    except Exception as e:
        _ghi_log("loi", f"Lấy bước lỗi: {e}")
        return None


def lay_hop_dong_file(id_du_an, ten_file):
    """Lấy hợp đồng của 1 file."""
    try:
        from dai_nao.ghi_nho import lay_hop_dong
        return lay_hop_dong(id_du_an, ten_file)
    except Exception as e:
        _ghi_log("loi", f"Lấy hợp đồng lỗi: {e}")
        return None
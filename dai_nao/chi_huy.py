"""
chi_huy.py - Đại não gọi model riêng Rồng Thần.

ĐÃ SỬA:
    - Bọc try/except từng bước trong phan_tich_du_an.
    - Chia task fail → vẫn trả kết quả hieu_yeu_cau (không crash).
    - Timeout nhanh cho từng bước → tránh Render timeout.
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
# HIỂU YÊU CẦU
# ================================================================
def hieu_yeu_cau(noi_dung, chu_so_huu=""):
    ket_qua = {
        "thanh_cong": False,
        "loai_task": "khac",
        "do_phuc_tap": "don_gian",
        "yeu_cau_chinh": noi_dung,
        "cac_yeu_cau_con": [],
        "loi": "",
    }

    if not noi_dung:
        ket_qua["loi"] = "Nội dung rỗng."
        return ket_qua

    prompt = f"""Bạn là chuyên gia phân tích yêu cầu. Phân tích yêu cầu sau.

YÊU CẦU: "{noi_dung}"

Trả về JSON (CHỈ JSON):
{{
  "loai_task": "lam_web | lam_python | viet_van | sua_bug | giai_toan | khac",
  "do_phuc_tap": "don_gian | trung_binh | phuc_tap",
  "yeu_cau_chinh": "Tóm tắt 1 câu",
  "cac_yeu_cau_con": ["yêu cầu con 1", "yêu cầu con 2"]
}}

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
    ket_qua["loai_task"] = du_lieu.get("loai_task", "khac")
    ket_qua["do_phuc_tap"] = du_lieu.get("do_phuc_tap", "don_gian")
    ket_qua["yeu_cau_chinh"] = du_lieu.get("yeu_cau_chinh", noi_dung)
    ket_qua["cac_yeu_cau_con"] = du_lieu.get("cac_yeu_cau_con", [])
    ket_qua["model"] = kq.get("model", "")

    _ghi_log("dai-nao", f"Boss hiểu yêu cầu: {ket_qua['loai_task']} / {ket_qua['do_phuc_tap']}")

    return ket_qua


# ================================================================
# CHIA TASK
# ================================================================
def chia_task(noi_dung, yeu_cau_da_hieu=None, chu_so_huu=""):
    ket_qua = {
        "thanh_cong": False,
        "ds_task": [],
        "loi": "",
    }

    if not noi_dung:
        ket_qua["loi"] = "Nội dung rỗng."
        return ket_qua

    yeu_cau_da_hieu = yeu_cau_da_hieu or {}
    loai_task = yeu_cau_da_hieu.get("loai_task", "khac")
    yeu_cau_chinh = yeu_cau_da_hieu.get("yeu_cau_chinh", noi_dung)
    cac_yeu_cau_con = yeu_cau_da_hieu.get("cac_yeu_cau_con", [])

    if not cac_yeu_cau_con:
        cac_yeu_cau_con = [yeu_cau_chinh]

    prompt = f"""Chia task dự án sau thành các task nhỏ.

LOẠI: {loai_task}
YÊU CẦU: {yeu_cau_chinh}
YÊU CẦU CON: {json.dumps(cac_yeu_cau_con, ensure_ascii=False)}

Trả về JSON (CHỈ JSON):
{{
  "ds_task": [
    {{"so": 1, "ten": "...", "file": "...", "mo_ta": "...", "phu_thuoc": []}}
  ]
}}

CHỈ TRẢ VỀ JSON."""

    kq = _goi_model_boss(prompt, chu_so_huu)
    if not kq.get("thanh_cong"):
        ket_qua["loi"] = kq.get("loi", "Không gọi được Boss.")
        return ket_qua

    du_lieu = _trich_json(kq.get("ket_qua", ""))
    if not du_lieu:
        ket_qua["loi"] = "Boss trả về không phải JSON."
        return ket_qua

    ds_task = du_lieu.get("ds_task", [])
    if not isinstance(ds_task, list):
        ket_qua["loi"] = "ds_task không phải mảng."
        return ket_qua

    ket_qua["thanh_cong"] = True
    ket_qua["ds_task"] = ds_task

    _ghi_log("dai-nao", f"Boss chia thành {len(ds_task)} task cho dự án {loai_task}")

    return ket_qua


# ================================================================
# VIẾT BRIEF
# ================================================================
def viet_brief(task_con, ngu_canh=None, chu_so_huu=""):
    ket_qua = {"thanh_cong": False, "brief": {}, "loi": ""}

    if not task_con:
        ket_qua["loi"] = "Task con rỗng."
        return ket_qua

    ten = task_con.get("ten", "")
    file = task_con.get("file", "")
    mo_ta = task_con.get("mo_ta", "")

    prompt = f"""Viết brief cho lập trình viên viết file sau.

TASK: {ten}
FILE: {file}
MÔ TẢ: {mo_ta}

Trả về JSON (CHỈ JSON):
{{
  "yeu_cau": "...",
  "file": "{file}",
  "ngon_ngu": "html | python | javascript | css",
  "ham_yeu_cau": [],
  "bien_yeu_cau": [],
  "quy_uoc": [],
  "mo_ta": "..."
}}

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
    ket_qua["brief"] = du_lieu

    return ket_qua


# ================================================================
# KIỂM TRA KẾT QUẢ
# ================================================================
def kiem_tra_ket_qua(code, hop_dong, ngon_ngu="", chu_so_huu=""):
    ket_qua = {"thanh_cong": False, "dat": False, "ly_do": ""}

    if not code or not hop_dong:
        ket_qua["ly_do"] = "Thiếu code hoặc hợp đồng."
        return ket_qua

    try:
        from dai_nao.doi_chieu import doi_chieu as _doi_chieu
        id_du_an = hop_dong.get("id_du_an", "")
        ten_file = hop_dong.get("ten_file", "")
        kq = _doi_chieu(id_du_an, ten_file, code, ngon_ngu, hop_dong)

        ket_qua["thanh_cong"] = kq.get("thanh_cong", False)
        ket_qua["dat"] = kq.get("dat", False)
        ket_qua["ly_do"] = kq.get("ly_do", "")
        ket_qua["chi_tiet"] = kq

        return ket_qua
    except ImportError:
        ket_qua["ly_do"] = "doi_chieu.py chưa có."
        return ket_qua
    except Exception as e:
        ket_qua["ly_do"] = f"Lỗi đối chiếu: {e}"
        return ket_qua


# ================================================================
# PHÂN TÍCH DỰ ÁN — BỌC TRY/EXCEPT TỪNG BƯỚC
# ================================================================
def phan_tich_du_an(noi_dung, chu_so_huu=""):
    """
    Bọc try/except từng bước.
    - Bước 1 (hiểu yêu cầu): BẮT BUỘC. Fail → return lỗi.
    - Bước 2 (chia task): TÙY CHỌN. Fail → bỏ qua, vẫn tiếp tục.
    - Bước 3 (snapshot): TÙY CHỌN. Fail → bỏ qua, vẫn tiếp tục.
    """
    ket_qua = {
        "thanh_cong": False,
        "yeu_cau": {},
        "ds_task": [],
        "snapshot": None,
        "loi": "",
    }

    if not noi_dung:
        ket_qua["loi"] = "Nội dung rỗng."
        return ket_qua

    # Bước 1: Hiểu yêu cầu (BẮT BUỘC)
    try:
        yeu_cau = hieu_yeu_cau(noi_dung, chu_so_huu)
    except Exception as e:
        ket_qua["loi"] = f"Lỗi hiểu yêu cầu: {e}"
        _ghi_log("loi", ket_qua["loi"])
        return ket_qua

    if not yeu_cau.get("thanh_cong"):
        ket_qua["loi"] = f"Không hiểu yêu cầu: {yeu_cau.get('loi', '')}"
        return ket_qua

    ket_qua["yeu_cau"] = yeu_cau

    # Bước 2: Chia task (TÙY CHỌN)
    ds_task = []
    try:
        chia = chia_task(noi_dung, yeu_cau, chu_so_huu)
        if chia.get("thanh_cong"):
            ds_task = chia.get("ds_task", [])
        else:
            _ghi_log("dai-nao", f"Chia task fail (bỏ qua): {chia.get('loi', '')}")
    except Exception as e:
        _ghi_log("loi", f"Chia task lỗi (bỏ qua): {e}")

    ket_qua["ds_task"] = ds_task

    # Bước 3: Tạo snapshot (TÙY CHỌN)
    try:
        from dai_nao.snapshot import tao_snapshot
        import secrets

        id_du_an = "du-an-" + secrets.token_hex(4)

        da_chia = []
        for i, task in enumerate(ds_task, 1):
            da_chia.append({
                "so": task.get("so", i),
                "ten": task.get("ten", ""),
                "file": task.get("file", ""),
                "trang_thai": "chua_lam",
                "mo_ta": task.get("mo_ta", ""),
            })

        snapshot = tao_snapshot(id_du_an, {
            "yeu_cau_goc": noi_dung,
            "loai_du_an": yeu_cau.get("loai_task", "khac"),
            "da_chia": da_chia,
        })

        if snapshot:
            ket_qua["snapshot"] = snapshot
            ket_qua["id_du_an"] = id_du_an
    except Exception as e:
        _ghi_log("loi", f"Tạo snapshot lỗi (bỏ qua): {e}")

    ket_qua["thanh_cong"] = True

    _ghi_log(
        "dai-nao",
        f"Boss phân tích dự án: {len(ds_task)} task, id={ket_qua.get('id_du_an', '')}",
    )

    return ket_qua


# ================================================================
# HÀM CHÍNH
# ================================================================
def chi_huy(du_lieu):
    ket_qua = {
        "thanh_cong": False,
        "can_boss": False,
        "yeu_cau": {},
        "ds_task": [],
        "snapshot": None,
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
        ket_qua["ly_do"] = "Task đơn giản — không cần Boss."
        return ket_qua

    ket_qua["can_boss"] = True

    try:
        kq_phan_tich = phan_tich_du_an(noi_dung, chu_so_huu)
    except Exception as e:
        ket_qua["loi"] = f"Lỗi phân tích: {e}"
        _ghi_log("loi", f"Boss phân tích lỗi: {e}")
        return ket_qua

    if not kq_phan_tich.get("thanh_cong"):
        ket_qua["loi"] = kq_phan_tich.get("loi", "Boss thất bại.")
        _ghi_log("dai-nao", f"Boss thất bại: {ket_qua['loi']}")
        return ket_qua

    ket_qua["thanh_cong"] = True
    ket_qua["yeu_cau"] = kq_phan_tich.get("yeu_cau", {})
    ket_qua["ds_task"] = kq_phan_tich.get("ds_task", [])
    ket_qua["snapshot"] = kq_phan_tich.get("snapshot")
    ket_qua["id_du_an"] = kq_phan_tich.get("id_du_an", "")

    return ket_qua


# ================================================================
# HÀM PHỤ
# ================================================================
def tom_tat_ket_qua(ket_qua):
    if not ket_qua:
        return ""

    if not ket_qua.get("thanh_cong"):
        return f"❌ Boss thất bại: {ket_qua.get('loi', 'không rõ')}"

    if not ket_qua.get("can_boss"):
        return "✅ Task đơn giản — không cần Boss."

    yeu_cau = ket_qua.get("yeu_cau", {})
    ds_task = ket_qua.get("ds_task", [])

    phan = ["✅ Boss hoàn thành:"]
    phan.append(f"  - Loại: {yeu_cau.get('loai_task', '?')}")
    phan.append(f"  - Độ phức tạp: {yeu_cau.get('do_phuc_tap', '?')}")
    phan.append(f"  - Số task: {len(ds_task)}")

    id_du_an = ket_qua.get("id_du_an", "")
    if id_du_an:
        phan.append(f"  - Mã dự án: {id_du_an}")

    return "\n".join(phan)
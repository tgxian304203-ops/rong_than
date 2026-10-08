"""
chi_huy.py - Đại não gọi model riêng Rồng Thần.

Nhiệm vụ:
    - chi_huy(du_lieu): Đại não gọi model để suy luận.
    - hieu_yeu_cau(noi_dung): hiểu yêu cầu user.
    - chia_task(yeu_cau, du_lieu): chia task lớn thành task nhỏ.
    - viet_brief(task_con): viết brief cho Tiểu não.
    - kiem_tra_ket_qua(code, hop_dong): kiểm tra kết quả Tiểu não.
    - phan_tich_du_an(noi_dung): phân tích dự án lớn.

Đại não (Boss) dùng:
    - Key Boss (loai_nao="boss") — tách biệt với Tiểu não.
    - Model mạnh (Gemini / Groq) — để suy luận.

Khi nào gọi Boss:
    - Task phức tạp (dự án nhiều file, viết văn dài).
    - KHÔNG gọi cho task đơn giản (1+1, hỏi thời gian).

Boss hết quota:
    - Trả về thanh_cong=False.
    - Đại não fallback về logic Python cũ.

Tầng dữ liệu: dai_nao/ghi_nho.py
Điều phối model: tieu_nao/do_model.py
"""

import re
import json
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
SO_LAN_RETRY = 3

# Loại task cần Boss
LOAI_TASK_CAN_BOSS = (
    "làm web", "làm app", "làm dự án", "làm game",
    "viết văn dài", "viết bài dài",
    "phân tích dự án", "chia task",
    "tạo dự án", "làm nhiều file",
)

# Loại task KHÔNG cần Boss
LOAI_TASK_KHONG_CAN_BOSS = (
    "1+1", "tính", "hôm nay", "bây giờ",
    "chào", "hello", "cảm ơn",
)


# ================================================================
# KIỂM TRA CÓ CẦN BOSS KHÔNG
# ================================================================
def can_boss(noi_dung):
    """
    Kiểm tra task có cần Boss không.

    Boss cần cho:
        - Task dài (> 200 ký tự).
        - Có từ khoá "làm web", "làm dự án"...
        - Có nhiều yêu cầu (dấu phẩy, chấm phẩy nhiều).

    Boss KHÔNG cần cho:
        - Task ngắn, đơn giản.
    """
    if not noi_dung:
        return False

    noi_dung_lower = noi_dung.lower().strip()

    # Task rất ngắn → không cần
    if len(noi_dung_lower) < 15:
        return False

    # Có từ khoá loại trừ → không cần
    for tk in LOAI_TASK_KHONG_CAN_BOSS:
        if noi_dung_lower.startswith(tk):
            return False

    # Có từ khoá cần Boss → cần
    for tk in LOAI_TASK_CAN_BOSS:
        if tk in noi_dung_lower:
            return True

    # Task dài (> 200 ký tự) → cần
    if len(noi_dung_lower) > 200:
        return True

    # Có nhiều yêu cầu (nhiều dấu phẩy/chấm) → cần
    so_dau_cau = noi_dung_lower.count(",") + noi_dung_lower.count(";") + noi_dung_lower.count(" và ")
    if so_dau_cau >= 3:
        return True

    return False


# ================================================================
# GỌI MODEL BOSS
# ================================================================
def _goi_model_boss(prompt, chu_so_huu=""):
    """
    Gọi model Boss qua do_model với loai_nao="boss".

    Trả về: {"thanh_cong": bool, "ket_qua": str, "loi": str}
    """
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
# TRÍCH JSON TỪ RESPONSE
# ================================================================
def _trich_json(chuoi):
    """Trích JSON từ response model."""
    if not chuoi:
        return None

    try:
        from dai_nao.khuon import trich_json_tu_response
        return trich_json_tu_response(chuoi)
    except ImportError:
        pass

    # Fallback
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
    """
    Boss phân tích yêu cầu user.

    Trả về: {
        thanh_cong: bool,
        loai_task: str,      # "lam_web" | "viet_van" | "sua_bug" | "giai_toan" | "khac"
        do_phuc_tap: str,    # "don_gian" | "trung_binh" | "phuc_tap"
        yeu_cau_chinh: str,
        cac_yeu_cau_con: [str],
        loi: str,
    }
    """
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

    prompt = f"""Bạn là chuyên gia phân tích yêu cầu. Hãy phân tích yêu cầu sau của user.

YÊU CẦU: "{noi_dung}"

Hãy trả về JSON (CHỈ JSON, không text khác):
{{
  "loai_task": "lam_web | lam_python | viet_van | sua_bug | giai_toan | khac",
  "do_phuc_tap": "don_gian | trung_binh | phuc_tap",
  "yeu_cau_chinh": "Tóm tắt yêu cầu chính (1 câu)",
  "cac_yeu_cau_con": ["yêu cầu con 1", "yêu cầu con 2", ...]
}}

QUY TẮC:
1. loai_task: chọn 1 trong các giá trị trên.
2. do_phuc_tap: đơn giản (1 bước), trung bình (2-3 bước), phức tạp (>3 bước).
3. yeu_cau_chinh: 1 câu ngắn gọn.
4. cac_yeu_cau_con: tách thành các yêu cầu nhỏ nếu có.
5. Nếu không có yêu cầu con → để mảng rỗng [].

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

    _ghi_log(
        "dai-nao",
        f"Boss hiểu yêu cầu: {ket_qua['loai_task']} / {ket_qua['do_phuc_tap']}",
    )

    return ket_qua


# ================================================================
# CHIA TASK
# ================================================================
def chia_task(noi_dung, yeu_cau_da_hieu=None, chu_so_huu=""):
    """
    Boss chia task lớn thành nhiều task nhỏ.

    Trả về: {
        thanh_cong: bool,
        ds_task: [
            {
                so: int,
                ten: str,
                file: str,
                mo_ta: str,
                phu_thuoc: [int],
            }
        ],
        loi: str,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "ds_task": [],
        "loi": "",
    }

    if not noi_dung:
        ket_qua["loi"] = "Nội dung rỗng."
        return ket_qua

    # Thông tin từ bước hiểu yêu cầu
    yeu_cau_da_hieu = yeu_cau_da_hieu or {}
    loai_task = yeu_cau_da_hieu.get("loai_task", "khac")
    yeu_cau_chinh = yeu_cau_da_hieu.get("yeu_cau_chinh", noi_dung)
    cac_yeu_cau_con = yeu_cau_da_hieu.get("cac_yeu_cau_con", [])

    # Nếu không có yêu cầu con → tạo 1 task tổng
    if not cac_yeu_cau_con:
        cac_yeu_cau_con = [yeu_cau_chinh]

    prompt = f"""Bạn là chuyên gia chia task dự án.

LOẠI DỰ ÁN: {loai_task}
YÊU CẦU CHÍNH: {yeu_cau_chinh}
CÁC YÊU CẦU CON: {json.dumps(cac_yeu_cau_con, ensure_ascii=False)}

Hãy chia thành các task NHỎ để làm từng bước.

Trả về JSON (CHỈ JSON):
{{
  "ds_task": [
    {{
      "so": 1,
      "ten": "Tên task ngắn",
      "file": "Tên file (nếu có, VD index.html) hoặc để rỗng",
      "mo_ta": "Mô tả chi tiết task này",
      "phu_thuoc": []
    }},
    {{
      "so": 2,
      "ten": "Tên task 2",
      "file": "style.css",
      "mo_ta": "Mô tả",
      "phu_thuoc": [1]
    }}
  ]
}}

QUY TẮC:
1. Mỗi task làm 1 việc cụ thể (1 file, 1 chức năng).
2. Task sau có thể phụ thuộc task trước (phu_thuoc = [số task]).
3. Số task tùy dự án — có thể 2, 3, 5, 10.
4. Đánh số từ 1 tăng dần.
5. Nếu task không có file riêng → để file rỗng "".

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

    _ghi_log(
        "dai-nao",
        f"Boss chia thành {len(ds_task)} task cho dự án {loai_task}",
    )

    return ket_qua


# ================================================================
# VIẾT BRIEF CHO TIỂU NÃO
# ================================================================
def viet_brief(task_con, ngu_canh=None, chu_so_huu=""):
    """
    Boss viết brief chi tiết cho Tiểu não viết code.

    task_con: dict 1 task (từ ds_task).
    ngu_canh: dict ngữ cảnh dự án (snapshot).

    Trả về: {
        thanh_cong: bool,
        brief: {
            yeu_cau: str,
            file: str,
            ngon_ngu: str,
            ham_yeu_cau: [dict],
            bien_yeu_cau: [dict],
            quy_uoc: [str],
            mo_ta: str,
        },
        loi: str,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "brief": {},
        "loi": "",
    }

    if not task_con:
        ket_qua["loi"] = "Task con rỗng."
        return ket_qua

    ten = task_con.get("ten", "")
    file = task_con.get("file", "")
    mo_ta = task_con.get("mo_ta", "")

    # Tóm tắt ngữ cảnh nếu có
    tom_tat_ngu_canh = ""
    if ngu_canh:
        quy_uoc = ngu_canh.get("quy_uoc_chung", {})
        if quy_uoc:
            tom_tat_ngu_canh = f"Quy ước dự án: {json.dumps(quy_uoc, ensure_ascii=False)}"

    prompt = f"""Bạn là chuyên gia viết brief cho lập trình viên.

TASK CẦN LÀM:
- Tên: {ten}
- File: {file}
- Mô tả: {mo_ta}

{tom_tat_ngu_canh}

Hãy viết brief chi tiết cho Tiểu não (lập trình viên) viết code.

Trả về JSON (CHỈ JSON):
{{
  "yeu_cau": "Yêu cầu cụ thể cho file này",
  "file": "{file}",
  "ngon_ngu": "html | python | javascript | css | ...",
  "ham_yeu_cau": [
    {{"ten": "tenHam", "tham_so": ["a", "b"], "tra_ve": "number", "mo_ta": "..."}},
    ...
  ],
  "bien_yeu_cau": [
    {{"ten": "tenBien", "kieu": "string", "mo_ta": "..."}}
  ],
  "quy_uoc": ["Dùng camelCase", "Không dùng framework", ...],
  "mo_ta": "Mô tả chi tiết nội dung file"
}}

QUY TẮC:
1. Nếu file HTML → ngon_ngu = "html".
2. Nếu file JS → ngon_ngu = "javascript".
3. Nếu file CSS → ngon_ngu = "css".
4. Nếu file Python → ngon_ngu = "python".
5. ham_yeu_cau: liệt kê các hàm cần có (nếu có).
6. bien_yeu_cau: liệt kê các biến chính (nếu có).
7. quy_uoc: quy ước viết code cho file này.

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

    _ghi_log(
        "dai-nao",
        f"Boss viết brief cho {file}: "
        f"{len(du_lieu.get('ham_yeu_cau', []))} hàm, "
        f"{len(du_lieu.get('bien_yeu_cau', []))} biến",
    )

    return ket_qua


# ================================================================
# KIỂM TRA KẾT QUẢ TIỂU NÃO
# ================================================================
def kiem_tra_ket_qua(code, hop_dong, ngon_ngu="", chu_so_huu=""):
    """
    Boss kiểm tra code Tiểu não viết có khớp hợp đồng không.

    Dùng đối chiếu tự động (doi_chieu.py) — không gọi model.
    Chỉ gọi model khi cần phán đoán phức tạp.

    Trả về: {
        thanh_cong: bool,
        dat: bool,
        ly_do: str,
    }
    """
    ket_qua = {
        "thanh_cong": False,
        "dat": False,
        "ly_do": "",
    }

    if not code or not hop_dong:
        ket_qua["ly_do"] = "Thiếu code hoặc hợp đồng."
        return ket_qua

    # Gọi đối chiếu tự động
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
# PHÂN TÍCH DỰ ÁN LỚN
# ================================================================
def phan_tich_du_an(noi_dung, chu_so_huu=""):
    """
    Boss phân tích dự án lớn — hiểu yêu cầu + chia task.

    Đây là hàm gộp:
        1. Hiểu yêu cầu.
        2. Chia task.
        3. Tạo snapshot.

    Trả về: {
        thanh_cong: bool,
        yeu_cau: dict,
        ds_task: list,
        snapshot: dict,
        loi: str,
    }
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

    # Bước 1: Hiểu yêu cầu
    yeu_cau = hieu_yeu_cau(noi_dung, chu_so_huu)
    if not yeu_cau.get("thanh_cong"):
        ket_qua["loi"] = f"Không hiểu yêu cầu: {yeu_cau.get('loi', '')}"
        return ket_qua

    ket_qua["yeu_cau"] = yeu_cau

    # Bước 2: Chia task
    chia = chia_task(noi_dung, yeu_cau, chu_so_huu)
    if not chia.get("thanh_cong"):
        ket_qua["loi"] = f"Không chia task: {chia.get('loi', '')}"
        return ket_qua

    ds_task = chia.get("ds_task", [])
    ket_qua["ds_task"] = ds_task

    # Bước 3: Tạo snapshot
    try:
        from dai_nao.snapshot import tao_snapshot
        import secrets

        id_du_an = "du-an-" + secrets.token_hex(4)

        # Chuẩn hóa task cho snapshot
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
        else:
            ket_qua["loi"] = "Không tạo được snapshot."

    except ImportError:
        ket_qua["loi"] = "snapshot.py chưa có."
        return ket_qua
    except Exception as e:
        ket_qua["loi"] = f"Lỗi tạo snapshot: {e}"
        return ket_qua

    ket_qua["thanh_cong"] = True

    _ghi_log(
        "dai-nao",
        f"Boss phân tích dự án: {len(ds_task)} task, id={ket_qua.get('id_du_an', '')}",
    )

    return ket_qua


# ================================================================
# HÀM CHÍNH — CHI_HUY
# ================================================================
def chi_huy(du_lieu):
    """
    Đại não gọi Boss để xử lý task.

    du_lieu: dict { noi_dung, chu_so_huu }.

    Trả về: {
        thanh_cong: bool,
        can_boss: bool,
        yeu_cau: dict,
        ds_task: list,
        snapshot: dict,
        loi: str,
    }
    """
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

    # Kiểm tra có cần Boss không
    if not can_boss(noi_dung):
        ket_qua["can_boss"] = False
        ket_qua["thanh_cong"] = True
        ket_qua["ly_do"] = "Task đơn giản — không cần Boss."
        return ket_qua

    ket_qua["can_boss"] = True

    # Phân tích dự án
    kq_phan_tich = phan_tich_du_an(noi_dung, chu_so_huu)

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
    """Tóm tắt kết quả Boss."""
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
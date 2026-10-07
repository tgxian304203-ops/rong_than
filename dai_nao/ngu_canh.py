"""
ngu_canh.py - Quản lý 10 loại ngữ cảnh Rồng Thần (bản mạnh x10).

Nhiệm vụ:
    - lay_ngu_canh(du_lieu): lấy 10 loại ngữ cảnh, mỗi loại 10 khía cạnh.
    - hoc_ngu_canh(du_lieu): học ngữ cảnh từ lịch sử.
    - phat_hien_mau_thuan(ngu_canh_moi, ngu_canh_cu): phát hiện mâu thuẫn.
    - luu_ngu_canh(ngu_canh, chu_so_huu): lưu vào kho 1.
    - doc_ngu_canh_cu(chu_so_huu): đọc ngữ cảnh đã lưu.

ĐÃ SỬA:
    - L40: _thoi_gian_10_khia_canh dùng giờ VN (UTC+7) thay vì giờ server.

10 loại ngữ cảnh, mỗi loại 10 khía cạnh (tổng 100 khía cạnh).

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import re
import time


def _ghi_log(loai, noi_dung):
    try:
        from logs.ghi_log import ghi_log
        ghi_log(loai, noi_dung)
    except Exception:
        pass


BANG_CAM_XUC = {
    "vui": [
        "vui", "hạnh phúc", "sung sướng", "phấn khích", "hào hứng",
        "tuyệt", "hay quá", "giỏi", "cảm ơn", "thanks", "tks",
        "yêu", "thích", "tốt", "ok", "oke", "ngon", "quá đỉnh",
    ],
    "buồn": [
        "buồn", "chán", "thất vọng", "tệ", "dở", "kém",
        "không vui", "ủ rũ", "mệt mỏi", "chán nản",
    ],
    "bực": [
        "bực", "tức", "giận", "khó chịu", "bực mình",
        "dở hơi", "vớ vẩn", "chán quá", "sao lại",
        "không đúng", "sai rồi", "tệ quá", "kém quá",
        "không chấp nhận", "sai bét",
    ],
    "gấp": [
        "gấp", "khẩn cấp", "ngay", "liền", "mau",
        "nhanh", "cần gấp", "lẹ", "khẩn", "gấp lắm",
        "cần ngay", "sớm nhất",
    ],
    "lo_lắng": [
        "lo", "lo lắng", "hồi hộp", "sợ", "không chắc",
        "băn khoăn", "phân vân", "không biết", "chưa rõ",
    ],
    "trung_tinh": [],
}

CAM_XUC_TICH_CUC = ["vui", "hạnh phúc", "tuyệt", "hay", "giỏi", "cảm ơn", "thích"]
CAM_XUC_TIEU_CUC = ["buồn", "bực", "tức", "tệ", "kém", "chán", "sai"]

BANG_DUOI_FILE = {
    "py": "python", "js": "javascript", "ts": "typescript",
    "jsx": "jsx", "tsx": "tsx",
    "html": "html", "htm": "html", "css": "css", "scss": "scss",
    "sass": "sass", "less": "less",
    "json": "json", "yaml": "yaml", "yml": "yaml", "toml": "toml",
    "xml": "xml", "sql": "sql", "sh": "bash", "bash": "bash",
    "java": "java", "cpp": "cpp", "cc": "cpp", "c": "c", "h": "c",
    "cs": "csharp", "go": "go", "rs": "rust", "rb": "ruby",
    "php": "php", "swift": "swift", "kt": "kotlin",
    "md": "markdown", "txt": "text", "csv": "csv",
    "dockerfile": "dockerfile", "env": "env",
}


# ================================================================
# 1. NGỮ CẢNH HỘI THOẠI (10 khía cạnh)
# ================================================================
def _hoi_thoai_10_khia_canh(lich_su):
    ket_qua = {
        "so_tin_nhan": 0, "chu_de_chinh": "", "chu_de_phu": [],
        "cam_xuc_tong_the": "trung_tinh", "tu_khoa_lap_lai": [],
        "cau_hoi_chua_tra_loi": [], "task_dang_dang_do": "",
        "so_lan_chuyen_chu_de": 0, "muc_do_hieu_nhau": 0.0,
        "toc_do_hoi_thoai": "bình_thường",
    }

    if not lich_su or not isinstance(lich_su, list):
        return ket_qua

    ket_qua["so_tin_nhan"] = len(lich_su)

    cac_noi_dung = []
    for tin in lich_su:
        if isinstance(tin, dict):
            nd = tin.get("noi_dung") or tin.get("content") or ""
            if nd:
                cac_noi_dung.append(nd)
        elif isinstance(tin, str):
            cac_noi_dung.append(tin)

    if not cac_noi_dung:
        return ket_qua

    sap_xep = sorted(cac_noi_dung[-10:], key=len, reverse=True)
    if sap_xep:
        ket_qua["chu_de_chinh"] = sap_xep[0][:100]

    ket_qua["chu_de_phu"] = [nd[:60] for nd in cac_noi_dung[-5:]]

    tong_cam_xuc = {"vui": 0, "buồn": 0, "bực": 0, "gấp": 0, "lo_lắng": 0}
    for nd in cac_noi_dung[-10:]:
        t = nd.lower()
        for cx, tk in BANG_CAM_XUC.items():
            if cx == "trung_tinh":
                continue
            for k in tk:
                if k in t:
                    tong_cam_xuc[cx] += 1
                    break

    if any(v > 0 for v in tong_cam_xuc.values()):
        cx_manh = max(tong_cam_xuc, key=tong_cam_xuc.get)
        ket_qua["cam_xuc_tong_the"] = cx_manh

    dem_tu = {}
    for nd in cac_noi_dung:
        for tu in re.findall(r"\b[a-zA-Zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]{3,}\b", nd.lower()):
            dem_tu[tu] = dem_tu.get(tu, 0) + 1

    tu_lap = sorted(dem_tu.items(), key=lambda x: x[1], reverse=True)
    ket_qua["tu_khoa_lap_lai"] = [tu for tu, dem in tu_lap[:10] if dem >= 2]

    if cac_noi_dung and ("?" in cac_noi_dung[-1] or "nào" in cac_noi_dung[-1].lower()):
        ket_qua["cau_hoi_chua_tra_loi"] = [cac_noi_dung[-1][:100]]

    if cac_noi_dung:
        ket_qua["task_dang_dang_do"] = cac_noi_dung[-1][:120]

    chu_de_truoc = ""
    so_chuyen = 0
    for nd in cac_noi_dung[-20:]:
        tu_khoa = set(re.findall(r"\b[a-zA-Zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]{4,}\b", nd.lower()))
        tu_khoa_chinh = " ".join(sorted(tu_khoa)[:3])
        if chu_de_truoc and tu_khoa_chinh != chu_de_truoc and tu_khoa_chinh:
            so_chuyen += 1
        chu_de_truoc = tu_khoa_chinh
    ket_qua["so_lan_chuyen_chu_de"] = so_chuyen

    do_dai_tb = sum(len(nd) for nd in cac_noi_dung) / len(cac_noi_dung)
    ket_qua["muc_do_hieu_nhau"] = round(min(1.0, do_dai_tb / 200), 3)

    if len(lich_su) >= 2:
        tg_dau = 0
        tg_cuoi = 0
        for tin in lich_su:
            if isinstance(tin, dict):
                tg = tin.get("thoi_gian") or tin.get("timestamp") or 0
                if tg and not tg_dau:
                    tg_dau = tg
                if tg:
                    tg_cuoi = tg
        if tg_dau and tg_cuoi and tg_cuoi > tg_dau:
            giay = tg_cuoi - tg_dau
            tb_giay = giay / len(lich_su)
            if tb_giay < 10:
                ket_qua["toc_do_hoi_thoai"] = "rất_nhanh"
            elif tb_giay < 60:
                ket_qua["toc_do_hoi_thoai"] = "nhanh"
            elif tb_giay < 300:
                ket_qua["toc_do_hoi_thoai"] = "bình_thường"
            else:
                ket_qua["toc_do_hoi_thoai"] = "chậm"

    return ket_qua


# ================================================================
# 2. NGỮ CẢNH DỰ ÁN (10 khía cạnh)
# ================================================================
def _du_an_10_khia_canh(du_lieu):
    ket_qua = {
        "id_du_an": "", "ten_du_an": "", "mo_ta": "", "loai_du_an": "",
        "ngon_ngu_chinh": "", "framework": "", "tien_do": "",
        "file_quan_trong": [], "muc_tieu": "", "deadline": "",
    }

    if not du_lieu:
        return ket_qua

    id_du_an = du_lieu.get("id_du_an") or ""
    ket_qua["id_du_an"] = id_du_an

    if not id_du_an:
        return ket_qua

    try:
        from dai_nao.ghi_nho import lay_du_an
        du_an = lay_du_an(id_du_an)
        if not du_an:
            return ket_qua

        ket_qua["ten_du_an"] = du_an.get("ten", "")
        ket_qua["mo_ta"] = du_an.get("mo_ta", "")
        ket_qua["loai_du_an"] = du_an.get("loai", "")
        ket_qua["ngon_ngu_chinh"] = du_an.get("ngon_ngu", "")
        ket_qua["framework"] = du_an.get("framework", "")
        ket_qua["tien_do"] = du_an.get("tien_do", "")
        ket_qua["muc_tieu"] = du_an.get("muc_tieu", "")
        ket_qua["deadline"] = du_an.get("deadline", "")

        files = du_an.get("file_quan_trong", [])
        if isinstance(files, list):
            ket_qua["file_quan_trong"] = files[:10]
    except Exception:
        pass

    return ket_qua


# ================================================================
# 3. NGỮ CẢNH FILE (10 khía cạnh)
# ================================================================
def _file_10_khia_canh(noi_dung):
    ket_qua = {
        "ten_file": "", "duoi_file": "", "ngon_ngu": "", "kich_thuoc": 0,
        "so_dong": 0, "chuc_nang_chinh": "", "import_": [],
        "class_ham_chinh": [], "comment": [], "file_lien_quan": [],
    }

    if not noi_dung:
        return ket_qua

    mau_file = r"\b([\w\-]+\.(\w{1,5}))\b"
    khop = re.search(mau_file, noi_dung)

    if khop:
        ket_qua["ten_file"] = khop.group(1)
        ket_qua["duoi_file"] = khop.group(2).lower()
        ket_qua["ngon_ngu"] = BANG_DUOI_FILE.get(ket_qua["duoi_file"], "")

    tat_ca_file = re.findall(mau_file, noi_dung)
    ket_qua["file_lien_quan"] = list(set([f[0] for f in tat_ca_file]))[:10]

    if len(noi_dung) > 50:
        ket_qua["kich_thuoc"] = len(noi_dung)
        ket_qua["so_dong"] = len(noi_dung.split("\n"))

        imports = re.findall(r"^\s*(?:from\s+(\S+)\s+)?import\s+(\S+)", noi_dung, re.M)
        tat_ca_import = []
        for mod, ten in imports:
            tat_ca_import.append(mod or ten)
        ket_qua["import_"] = list(set(tat_ca_import))[:10]

        ham = re.findall(r"^\s*def\s+(\w+)", noi_dung, re.M)
        cls = re.findall(r"^\s*class\s+(\w+)", noi_dung, re.M)
        ket_qua["class_ham_chinh"] = (cls + ham)[:10]

        comments = re.findall(r"#\s*(.+)", noi_dung)
        ket_qua["comment"] = [c[:60] for c in comments[:5]]

        if comments:
            ket_qua["chuc_nang_chinh"] = comments[0][:100]

    return ket_qua


# ================================================================
# 4. NGỮ CẢNH TASK TRƯỚC (10 khía cạnh)
# ================================================================
def _task_truoc_10_khia_canh(lich_su):
    ket_qua = {
        "noi_dung_task": "", "loai_task": "", "ket_qua": "", "thoi_gian": 0,
        "loi": "", "cach_sua": "", "node_dung": "", "score": 0.0,
        "nguoi_gui": "", "phan_hoi": "",
    }

    if not lich_su or not isinstance(lich_su, list):
        return ket_qua

    for tin in reversed(lich_su):
        if not isinstance(tin, dict):
            continue
        vai_tro = tin.get("vai_tro") or tin.get("role") or ""
        if vai_tro in ("nguoi_dung", "user"):
            ket_qua["noi_dung_task"] = (tin.get("noi_dung") or tin.get("content") or "")[:200]
            ket_qua["nguoi_gui"] = tin.get("chu_so_huu") or "khach"
            ket_qua["thoi_gian"] = tin.get("thoi_gian") or tin.get("timestamp") or 0
            ket_qua["phan_hoi"] = tin.get("phan_hoi", "")
            ket_qua["loi"] = tin.get("loi", "")
            break

    for tin in reversed(lich_su):
        if not isinstance(tin, dict):
            continue
        vai_tro = tin.get("vai_tro") or tin.get("role") or ""
        if vai_tro in ("rong_than", "assistant", "bot"):
            ket_qua["ket_qua"] = (tin.get("noi_dung") or tin.get("content") or "")[:200]
            ket_qua["cach_sua"] = tin.get("cach_sua", "")
            ket_qua["node_dung"] = tin.get("id_node", "")
            ket_qua["score"] = float(tin.get("score", 0.0) or 0.0)
            break

    return ket_qua


# ================================================================
# 5. NGỮ CẢNH LĨNH VỰC (10 khía cạnh)
# ================================================================
def _linh_vuc_10_khia_canh(noi_dung):
    ket_qua = {
        "linh_vuc_chinh": "", "linh_vuc_phu": [], "nhom": "", "loai": "",
        "do_kho": 0.5, "kien_thuc_can": [], "node_khop": "",
        "do_tin_cay": 0.0, "xu_huong": "", "tu_khoa_dac_trung": [],
    }

    if not noi_dung:
        return ket_qua

    try:
        from dai_nao.phan_loai import phan_loai
        loai_task = phan_loai(noi_dung, {})
        ket_qua["linh_vuc_chinh"] = loai_task.get("linh_vuc", "")
        ket_qua["nhom"] = loai_task.get("nhom", "")
        ket_qua["loai"] = loai_task.get("loai", "")
        ket_qua["do_tin_cay"] = loai_task.get("do_tin_cay", 0.0)
    except ImportError:
        pass

    tu_dac_trung = re.findall(r"\b[a-zA-Zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]{4,}\b", noi_dung.lower())
    ket_qua["tu_khoa_dac_trung"] = list(set(tu_dac_trung))[:10]

    do_dai = len(noi_dung)
    if do_dai < 30:
        ket_qua["do_kho"] = 0.3
    elif do_dai < 100:
        ket_qua["do_kho"] = 0.5
    else:
        ket_qua["do_kho"] = 0.7

    bang_kien_thuc = {
        "toán": ["công thức", "phép tính", "logic"],
        "văn": ["ngữ pháp", "từ vựng", "bố cục"],
        "code": ["cú pháp", "thuật toán", "thư viện"],
        "bug": ["đọc lỗi", "debug", "phân tích"],
        "khoa học": ["kiến thức chuyên ngành", "số liệu"],
        "đời sống": ["kinh nghiệm", "thực tế"],
        "kinh doanh": ["chiến lược", "thị trường"],
        "sáng tạo": ["ý tưởng", "cảm hứng"],
        "học tập": ["kiến thức nền", "ví dụ"],
        "tra cứu": ["thông tin", "nguồn"],
        "kỹ thuật": ["nguyên lý", "ứng dụng"],
        "luật - hành chính": ["điều luật", "thủ tục"],
    }
    ket_qua["kien_thuc_can"] = bang_kien_thuc.get(ket_qua["linh_vuc_chinh"], [])

    return ket_qua


# ================================================================
# 6. NGỮ CẢNH NGÔN NGỮ LẬP TRÌNH (10 khía cạnh)
# ================================================================
def _ngon_ngu_10_khia_canh(noi_dung):
    ket_qua = {
        "ngon_ngu_chinh": "", "framework": "", "library": [],
        "version": "", "style_code": "", "convention": "",
        "tooling": "", "package_manager": "", "build_system": "",
        "test_framework": "",
    }

    if not noi_dung:
        return ket_qua

    t = noi_dung.lower()

    bang_ngon_ngu = {
        "python": "Python", "pandas": "Python", "numpy": "Python",
        "javascript": "JavaScript", "typescript": "TypeScript",
        "java ": "Java", "c++": "C++", "cpp": "C++",
        "c#": "C#", "csharp": "C#", "golang": "Go",
        "rust": "Rust", "ruby": "Ruby", "php": "PHP",
        "swift": "Swift", "kotlin": "Kotlin",
        "html": "HTML", "css": "CSS", "sql": "SQL",
        "bash": "Bash", "shell": "Shell",
    }
    for k, v in bang_ngon_ngu.items():
        if k in t:
            ket_qua["ngon_ngu_chinh"] = v
            break

    bang_framework = {
        "react": "React", "vue": "Vue", "angular": "Angular",
        "django": "Django", "flask": "Flask", "fastapi": "FastAPI",
        "express": "Express", "nextjs": "Next.js",
        "spring": "Spring", "laravel": "Laravel", "rails": "Rails",
        "pytorch": "PyTorch", "tensorflow": "TensorFlow",
    }
    for k, v in bang_framework.items():
        if k in t:
            ket_qua["framework"] = v
            break

    bang_lib = {
        "requests": "requests", "pandas": "pandas", "numpy": "numpy",
        "axios": "axios", "jquery": "jquery", "lodash": "lodash",
    }
    ket_qua["library"] = [v for k, v in bang_lib.items() if k in t][:5]

    if "pip" in t or "pip install" in t:
        ket_qua["package_manager"] = "pip"
    elif "npm" in t:
        ket_qua["package_manager"] = "npm"
    elif "yarn" in t:
        ket_qua["package_manager"] = "yarn"
    elif "cargo" in t:
        ket_qua["package_manager"] = "cargo"

    if "webpack" in t:
        ket_qua["build_system"] = "webpack"
    elif "vite" in t:
        ket_qua["build_system"] = "vite"
    elif "gradle" in t:
        ket_qua["build_system"] = "gradle"
    elif "maven" in t:
        ket_qua["build_system"] = "maven"

    if "pytest" in t:
        ket_qua["test_framework"] = "pytest"
    elif "unittest" in t:
        ket_qua["test_framework"] = "unittest"
    elif "jest" in t:
        ket_qua["test_framework"] = "jest"

    if re.search(r"\b[a-z]+_[a-z]+\b", noi_dung):
        ket_qua["style_code"] = "snake_case"
    elif re.search(r"\b[a-z]+[A-Z][a-z]+\b", noi_dung):
        ket_qua["style_code"] = "camelCase"

    return ket_qua


# ================================================================
# 7. NGỮ CẢNH MÔI TRƯỜNG (10 khía cạnh)
# ================================================================
def _moi_truong_10_khia_canh(noi_dung):
    ket_qua = {
        "moi_truong": "khong_ro", "os": "", "python_version": "",
        "node_version": "", "database": "", "cache": "",
        "storage": "", "network": "", "ssl": "", "region": "",
    }

    if not noi_dung:
        return ket_qua

    t = noi_dung.lower()

    bang_mt = {
        "render": "Render", "heroku": "Heroku", "vercel": "Vercel",
        "netlify": "Netlify", "aws": "AWS", "gcp": "GCP",
        "azure": "Azure", "local": "Local", "máy tính": "Local",
        "sandbox": "Sandbox", "docker": "Docker",
        "kubernetes": "Kubernetes", "k8s": "Kubernetes",
        "vps": "VPS", "server": "Server",
    }
    for k, v in bang_mt.items():
        if k in t:
            ket_qua["moi_truong"] = v
            break

    if "windows" in t or "win" in t:
        ket_qua["os"] = "Windows"
    elif "linux" in t or "ubuntu" in t:
        ket_qua["os"] = "Linux"
    elif "macos" in t or "mac " in t:
        ket_qua["os"] = "macOS"

    khop_py = re.search(r"python\s*(\d+\.\d+)", t)
    if khop_py:
        ket_qua["python_version"] = khop_py.group(1)

    khop_node = re.search(r"node\s*(\d+)", t)
    if khop_node:
        ket_qua["node_version"] = khop_node.group(1)

    bang_db = {
        "mongodb": "MongoDB", "mysql": "MySQL",
        "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
        "sqlite": "SQLite", "redis": "Redis",
        "firebase": "Firebase",
    }
    for k, v in bang_db.items():
        if k in t:
            ket_qua["database"] = v
            break

    if "redis" in t:
        ket_qua["cache"] = "Redis"
    elif "memcached" in t:
        ket_qua["cache"] = "Memcached"

    if "s3" in t:
        ket_qua["storage"] = "S3"
    elif "gridfs" in t:
        ket_qua["storage"] = "GridFS"
    elif "disk" in t or "ổ đĩa" in t:
        ket_qua["storage"] = "Disk"

    if "http" in t:
        ket_qua["network"] = "HTTP"
    elif "https" in t:
        ket_qua["network"] = "HTTPS"
    elif "websocket" in t:
        ket_qua["network"] = "WebSocket"

    if "ssl" in t or "https" in t:
        ket_qua["ssl"] = "Bật"
    elif "không ssl" in t:
        ket_qua["ssl"] = "Tắt"

    khop_region = re.search(r"\b(us|eu|ap|sg|vn)-[a-z]+\b", t)
    if khop_region:
        ket_qua["region"] = khop_region.group(0)

    return ket_qua


# ================================================================
# 8. NGỮ CẢNH RÀNG BUỘC (10 khía cạnh)
# ================================================================
def _rang_buoc_10_khia_canh(noi_dung):
    ket_qua = {
        "so_dong_toi_da": "", "so_ky_tu_toi_da": "",
        "thoi_gian_toi_da": "", "dung_luong_toi_da": "",
        "khong_dung": [], "chi_dung": [], "bat_buoc": [],
        "tuy_chon": [], "ngan_sach": "", "license": "",
    }

    if not noi_dung:
        return ket_qua

    t = noi_dung.lower()

    khop = re.search(r"(?:tối đa|dưới|ít hơn)\s*(\d+)\s*dòng", t)
    if khop:
        ket_qua["so_dong_toi_da"] = khop.group(1)

    khop = re.search(r"(?:tối đa|dưới)\s*(\d+)\s*(?:ký tự|chữ|character)", t)
    if khop:
        ket_qua["so_ky_tu_toi_da"] = khop.group(1)

    khop = re.search(r"(?:trong vòng|tối đa)\s*(\d+)\s*(giây|phút|giờ|ngày)", t)
    if khop:
        ket_qua["thoi_gian_toi_da"] = f"{khop.group(1)} {khop.group(2)}"

    khop = re.search(r"(?:tối đa|dưới)\s*(\d+)\s*(kb|mb|gb)", t)
    if khop:
        ket_qua["dung_luong_toi_da"] = f"{khop.group(1)} {khop.group(2).upper()}"

    mau_khong_dung = r"không\s+(?:dùng|sử dụng|cần)\s+([\w\s]+?)(?:[,.]|$)"
    for khop in re.finditer(mau_khong_dung, t):
        ket_qua["khong_dung"].append(khop.group(1).strip()[:50])

    mau_chi_dung = r"chỉ\s+(?:dùng|sử dụng|cần)\s+([\w\s]+?)(?:[,.]|$)"
    for khop in re.finditer(mau_chi_dung, t):
        ket_qua["chi_dung"].append(khop.group(1).strip()[:50])

    mau_bat_buoc = r"(?:bắt buộc|phải)\s+([\w\s]+?)(?:[,.]|$)"
    for khop in re.finditer(mau_bat_buoc, t):
        ket_qua["bat_buoc"].append(khop.group(1).strip()[:50])

    mau_tuy_chon = r"(?:tùy chọn|nếu có thể|không bắt buộc)\s+([\w\s]+?)(?:[,.]|$)"
    for khop in re.finditer(mau_tuy_chon, t):
        ket_qua["tuy_chon"].append(khop.group(1).strip()[:50])

    khop = re.search(r"(?:ngân sách|chi phí|giá)\s*[:]?\s*(\d+[\w\s]+)", t)
    if khop:
        ket_qua["ngan_sach"] = khop.group(1).strip()[:50]

    bang_license = ["mit", "apache", "gpl", "bsd", "creative commons"]
    for lic in bang_license:
        if lic in t:
            ket_qua["license"] = lic.upper()
            break

    ket_qua["khong_dung"] = ket_qua["khong_dung"][:5]
    ket_qua["chi_dung"] = ket_qua["chi_dung"][:5]
    ket_qua["bat_buoc"] = ket_qua["bat_buoc"][:5]
    ket_qua["tuy_chon"] = ket_qua["tuy_chon"][:5]

    return ket_qua


# ================================================================
# 9. NGỮ CẢNH THỜI GIAN (10 khía cạnh) — SỬA L40: DÙNG GIỜ VN
# ================================================================
def _thoi_gian_10_khia_canh():
    """
    Lấy thông tin thời gian theo giờ Việt Nam (UTC+7).

    SỬA L40: Dùng datetime với timezone VN thay vì time.localtime()
    (giờ server Render thường là UTC).
    """
    from datetime import datetime, timedelta, timezone

    mui_gio_vn = timezone(timedelta(hours=7))
    now = datetime.now(mui_gio_vn)

    gio = now.hour
    thang = now.month
    thu_index = now.weekday()  # 0 = Thứ 2, 6 = Chủ nhật

    if 5 <= gio < 12:
        buoi = "sáng"
    elif 12 <= gio < 18:
        buoi = "chiều"
    elif 18 <= gio < 22:
        buoi = "tối"
    else:
        buoi = "đêm"

    thu_map = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]

    if 3 <= thang <= 5:
        mua = "xuân"
    elif 6 <= thang <= 8:
        mua = "hạ"
    elif 9 <= thang <= 11:
        mua = "thu"
    else:
        mua = "đông"

    # Ngày lễ VN
    ngay_le = ""
    if thang == 1 and now.day == 1:
        ngay_le = "Tết Dương lịch"
    elif thang == 4 and now.day == 30:
        ngay_le = "30/4"
    elif thang == 5 and now.day == 1:
        ngay_le = "1/5"
    elif thang == 9 and now.day == 2:
        ngay_le = "Quốc khánh"
    elif thang == 1 and 20 <= now.day <= 31:
        ngay_le = "cận Tết"
    elif thang == 2 and 1 <= now.day <= 15:
        ngay_le = "Tết Nguyên Đán"

    return {
        "thoi_gian": int(now.timestamp()),
        "gio": gio,
        "phut": now.minute,
        "ngay": now.day,
        "thang": thang,
        "nam": now.year,
        "thu": thu_map[thu_index],
        "buoi": buoi,
        "mua": mua,
        "ngay_le": ngay_le,
    }


# ================================================================
# 10. NGỮ CẢNH CẢM XÚC (10 khía cạnh)
# ================================================================
def _cam_xuc_10_khia_canh(noi_dung):
    ket_qua = {
        "cam_xuc_chinh": "trung_tinh", "cam_xuc_phu": [], "do_manh": 0.0,
        "do_tin_cay": 0.0, "tu_khoa": [], "dau_hieu": [],
        "xu_huong": "trung_tinh", "anh_huong_tra_loi": "",
        "cach_xung_ho": "", "muc_do_khan_cap": "bình_thường",
    }

    if not noi_dung:
        return ket_qua

    t = noi_dung.lower()
    diem = {}

    for cam_xuc, tu_khoa in BANG_CAM_XUC.items():
        if cam_xuc == "trung_tinh":
            continue
        so_khop = 0
        tu_da_khop = []
        for tk in tu_khoa:
            if tk in t:
                so_khop += 1
                tu_da_khop.append(tk)
        if so_khop > 0:
            diem[cam_xuc] = so_khop
            ket_qua["tu_khoa"].extend(tu_da_khop)

    if "!!!" in noi_dung or "??" in noi_dung:
        diem["bực"] = diem.get("bực", 0) + 1
        ket_qua["dau_hieu"].append("dấu !!! hoặc ??")
    if "..." in noi_dung and len(noi_dung) < 30:
        diem["lo_lắng"] = diem.get("lo_lắng", 0) + 1
        ket_qua["dau_hieu"].append("dấu ...")
    if noi_dung.isupper():
        diem["bực"] = diem.get("bực", 0) + 1
        ket_qua["dau_hieu"].append("viết HOA toàn bộ")

    if not diem:
        ket_qua["cam_xuc_chinh"] = "trung_tinh"
        return ket_qua

    sap_xep = sorted(diem.items(), key=lambda x: x[1], reverse=True)
    ket_qua["cam_xuc_chinh"] = sap_xep[0][0]
    ket_qua["cam_xuc_phu"] = [cx for cx, _ in sap_xep[1:3]]
    ket_qua["do_manh"] = min(1.0, sap_xep[0][1] / 3)
    ket_qua["do_tin_cay"] = ket_qua["do_manh"]

    if ket_qua["cam_xuc_chinh"] in ("vui",):
        ket_qua["xu_huong"] = "tích_cực"
    elif ket_qua["cam_xuc_chinh"] in ("buồn", "bực"):
        ket_qua["xu_huong"] = "tiêu_cực"
    else:
        ket_qua["xu_huong"] = "trung_tinh"

    anh_huong = {
        "vui": "Trả lời vui vẻ, thân thiện.",
        "buồn": "Trả lời nhẹ nhàng, động viên.",
        "bực": "Trả lời bình tĩnh, xin lỗi nếu cần.",
        "gấp": "Trả lời ngắn gọn, đi thẳng vào vấn đề.",
        "lo_lắng": "Trả lời rõ ràng, trấn an.",
    }
    ket_qua["anh_huong_tra_loi"] = anh_huong.get(ket_qua["cam_xuc_chinh"], "")

    if "anh" in t or "chị" in t:
        ket_qua["cach_xung_ho"] = "lịch_sự"
    elif "mày" in t or "tao" in t or "tui" in t:
        ket_qua["cach_xung_ho"] = "thân_mật"
    elif "bạn" in t or "mình" in t:
        ket_qua["cach_xung_ho"] = "thân_thiện"

    if ket_qua["cam_xuc_chinh"] == "gấp" or "!!!" in noi_dung:
        ket_qua["muc_do_khan_cap"] = "cao"
    elif "gấp" in t or "nhanh" in t:
        ket_qua["muc_do_khan_cap"] = "trung_binh"

    return ket_qua


# ================================================================
# HỌC NGỮ CẢNH TỪ LỊCH SỬ
# ================================================================
def hoc_ngu_canh(du_lieu):
    if not du_lieu:
        return {}

    lich_su = du_lieu.get("lich_su") or []
    if not lich_su:
        return {}

    hoc = {
        "so_lan_xuat_hien_linh_vuc": {},
        "so_lan_xuat_hien_ngon_ngu": {},
        "tu_khoa_thuong_gap": {},
        "cam_xuc_gan_day": [],
        "chu_de_dang_lam": "",
    }

    for tin in lich_su[-20:]:
        if not isinstance(tin, dict):
            continue
        nd = tin.get("noi_dung") or tin.get("content") or ""
        if not nd:
            continue

        try:
            from dai_nao.phan_loai import phan_loai
            ket_qua = phan_loai(nd, {})
            lv = ket_qua.get("linh_vuc", "")
            if lv:
                hoc["so_lan_xuat_hien_linh_vuc"][lv] = \
                    hoc["so_lan_xuat_hien_linh_vuc"].get(lv, 0) + 1
        except ImportError:
            pass

        cx = _cam_xuc_10_khia_canh(nd)
        if cx["cam_xuc_chinh"] != "trung_tinh":
            hoc["cam_xuc_gan_day"].append(cx["cam_xuc_chinh"])

        for tu in re.findall(r"\b[a-zA-Zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]{4,}\b", nd.lower()):
            hoc["tu_khoa_thuong_gap"][tu] = hoc["tu_khoa_thuong_gap"].get(tu, 0) + 1

    hoc["tu_khoa_thuong_gap"] = dict(sorted(
        hoc["tu_khoa_thuong_gap"].items(),
        key=lambda x: x[1], reverse=True,
    )[:20])

    if lich_su and isinstance(lich_su[-1], dict):
        hoc["chu_de_dang_lam"] = (lich_su[-1].get("noi_dung") or "")[:100]

    return hoc


# ================================================================
# PHÁT HIỆN MÂU THUẪN
# ================================================================
def phat_hien_mau_thuan(ngu_canh_moi, ngu_canh_cu):
    if not ngu_canh_moi or not ngu_canh_cu:
        return []

    ket_qua = []

    nn_cu = (ngu_canh_cu.get("ngon_ngu") or {}).get("ngon_ngu_chinh", "")
    nn_moi = (ngu_canh_moi.get("ngon_ngu") or {}).get("ngon_ngu_chinh", "")
    if nn_cu and nn_moi and nn_cu != nn_moi:
        ket_qua.append({
            "truong": "ngon_ngu",
            "gia_tri_cu": nn_cu,
            "gia_tri_moi": nn_moi,
            "muc_do": "cao",
            "mo_ta": f"Ngôn ngữ đổi từ {nn_cu} sang {nn_moi}",
        })

    fw_cu = (ngu_canh_cu.get("ngon_ngu") or {}).get("framework", "")
    fw_moi = (ngu_canh_moi.get("ngon_ngu") or {}).get("framework", "")
    if fw_cu and fw_moi and fw_cu != fw_moi:
        ket_qua.append({
            "truong": "framework",
            "gia_tri_cu": fw_cu,
            "gia_tri_moi": fw_moi,
            "muc_do": "cao",
        })

    da_cu = (ngu_canh_cu.get("du_an") or {}).get("id_du_an", "")
    da_moi = (ngu_canh_moi.get("du_an") or {}).get("id_du_an", "")
    if da_cu and da_moi and da_cu != da_moi:
        ket_qua.append({
            "truong": "du_an",
            "gia_tri_cu": da_cu,
            "gia_tri_moi": da_moi,
            "muc_do": "thap",
            "mo_ta": "Chuyển dự án — bình thường.",
        })

    mt_cu = (ngu_canh_cu.get("moi_truong") or {}).get("moi_truong", "")
    mt_moi = (ngu_canh_moi.get("moi_truong") or {}).get("moi_truong", "")
    if mt_cu and mt_moi and mt_cu != mt_moi and "khong_ro" not in (mt_cu, mt_moi):
        ket_qua.append({
            "truong": "moi_truong",
            "gia_tri_cu": mt_cu,
            "gia_tri_moi": mt_moi,
            "muc_do": "trung_binh",
        })

    cx_cu = (ngu_canh_cu.get("cam_xuc") or {}).get("cam_xuc_chinh", "")
    cx_moi = (ngu_canh_moi.get("cam_xuc") or {}).get("cam_xuc_chinh", "")
    if cx_cu and cx_moi and cx_cu in CAM_XUC_TICH_CUC and cx_moi in ("bực", "buồn"):
        ket_qua.append({
            "truong": "cam_xuc",
            "gia_tri_cu": cx_cu,
            "gia_tri_moi": cx_moi,
            "muc_do": "cao",
            "mo_ta": "Cảm xúc đổi tiêu cực đột ngột.",
        })

    rb_cu = set((ngu_canh_cu.get("rang_buoc") or {}).get("khong_dung", []))
    rb_moi = set((ngu_canh_moi.get("rang_buoc") or {}).get("khong_dung", []))
    if rb_cu and rb_moi and rb_cu != rb_moi:
        ket_qua.append({
            "truong": "rang_buoc",
            "gia_tri_cu": list(rb_cu),
            "gia_tri_moi": list(rb_moi),
            "muc_do": "trung_binh",
        })

    return ket_qua


# ================================================================
# LƯU / ĐỌC NGỮ CẢNH
# ================================================================
def luu_ngu_canh(ngu_canh, chu_so_huu):
    if not ngu_canh or not chu_so_huu:
        return False

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
        db["ngu_canh"].update_one(
            {"chu_so_huu": chu_so_huu},
            {
                "$set": {
                    "chu_so_huu": chu_so_huu,
                    "ngu_canh": ngu_canh,
                    "thoi_gian": int(time.time()),
                }
            },
            upsert=True,
        )
        return True
    except Exception as e:
        _ghi_log("loi", f"Không lưu được ngữ cảnh: {e}")
        return False


def doc_ngu_canh_cu(chu_so_huu):
    if not chu_so_huu:
        return {}

    try:
        from dai_nao.ghi_nho import _ket_noi_kho_1
        db, _ = _ket_noi_kho_1()
        ket_qua = db["ngu_canh"].find_one({"chu_so_huu": chu_so_huu})
        if ket_qua:
            return ket_qua.get("ngu_canh", {})
    except Exception:
        pass

    return {}


# ================================================================
# HÀM CHÍNH
# ================================================================
def lay_ngu_canh(du_lieu):
    if not du_lieu:
        du_lieu = {}

    noi_dung = (du_lieu.get("noi_dung") or "").strip()
    lich_su = du_lieu.get("lich_su") or []
    chu_so_huu = du_lieu.get("chu_so_huu") or "khach"

    ket_qua = {
        "hoi_thoai": _hoi_thoai_10_khia_canh(lich_su),
        "du_an": _du_an_10_khia_canh(du_lieu),
        "file": _file_10_khia_canh(noi_dung),
        "task_truoc": _task_truoc_10_khia_canh(lich_su),
        "linh_vuc": _linh_vuc_10_khia_canh(noi_dung),
        "ngon_ngu": _ngon_ngu_10_khia_canh(noi_dung),
        "moi_truong": _moi_truong_10_khia_canh(noi_dung),
        "rang_buoc": _rang_buoc_10_khia_canh(noi_dung),
        "thoi_gian": _thoi_gian_10_khia_canh(),
        "cam_xuc": _cam_xuc_10_khia_canh(noi_dung),
    }

    hoc = hoc_ngu_canh(du_lieu)
    if hoc:
        ket_qua["hoc_tu_lich_su"] = hoc

    if chu_so_huu != "khach":
        ngu_canh_cu = doc_ngu_canh_cu(chu_so_huu)
        if ngu_canh_cu:
            mau_thuan = phat_hien_mau_thuan(ket_qua, ngu_canh_cu)
            if mau_thuan:
                ket_qua["mau_thuan"] = mau_thuan
                _ghi_log(
                    "dai-nao",
                    f"Phát hiện {len(mau_thuan)} mâu thuẫn ngữ cảnh cho {chu_so_huu}",
                )

        luu_ngu_canh(ket_qua, chu_so_huu)

    _ghi_log("dai-nao", "Đã lấy 10 loại ngữ cảnh × 10 khía cạnh = 100 khía cạnh.")
    return ket_qua


# ================================================================
# HÀM PHỤ
# ================================================================
def tom_tat_ngu_canh(ngu_canh):
    if not ngu_canh:
        return ""

    phan = []

    ht = ngu_canh.get("hoi_thoai", {})
    if ht.get("so_tin_nhan"):
        phan.append(f"💬 Hội thoại: {ht['so_tin_nhan']} tin, "
                    f"chủ đề: {ht.get('chu_de_chinh', '')[:50]}")

    da = ngu_canh.get("du_an", {})
    if da.get("ten_du_an"):
        phan.append(f"📁 Dự án: {da['ten_du_an']}")

    f = ngu_canh.get("file", {})
    if f.get("ten_file"):
        phan.append(f"📄 File: {f['ten_file']} ({f.get('ngon_ngu', '')})")

    tt = ngu_canh.get("task_truoc", {})
    if tt.get("noi_dung_task"):
        phan.append(f"⏮️ Task trước: {tt['noi_dung_task'][:50]}")

    lv = ngu_canh.get("linh_vuc", {})
    if lv.get("linh_vuc_chinh"):
        phan.append(f"🎯 Lĩnh vực: {lv['linh_vuc_chinh']} ({lv.get('nhom', '')})")

    nn = ngu_canh.get("ngon_ngu", {})
    if nn.get("ngon_ngu_chinh") or nn.get("framework"):
        phan.append(f"💻 Ngôn ngữ: {nn.get('ngon_ngu_chinh', '')} {nn.get('framework', '')}")

    mt = ngu_canh.get("moi_truong", {})
    if mt.get("moi_truong") and mt["moi_truong"] != "khong_ro":
        phan.append(f"🌐 Môi trường: {mt['moi_truong']}")

    rb = ngu_canh.get("rang_buoc", {})
    so_rb = (len(rb.get("khong_dung", [])) + len(rb.get("chi_dung", [])) +
             len(rb.get("bat_buoc", [])))
    if so_rb:
        phan.append(f"🔒 Ràng buộc: {so_rb}")

    tg = ngu_canh.get("thoi_gian", {})
    if tg.get("buoi"):
        phan.append(f"🕐 Thời gian: {tg['buoi']}, {tg.get('thu', '')}")

    cx = ngu_canh.get("cam_xuc", {})
    if cx.get("cam_xuc_chinh") and cx["cam_xuc_chinh"] != "trung_tinh":
        phan.append(f"😊 Cảm xúc: {cx['cam_xuc_chinh']} "
                    f"({cx.get('xu_huong', '')})")

    mau_thuan = ngu_canh.get("mau_thuan", [])
    if mau_thuan:
        phan.append(f"\n⚠️ Phát hiện {len(mau_thuan)} mâu thuẫn:")
        for mt_item in mau_thuan[:3]:
            phan.append(f"  - {mt_item.get('mo_ta', mt_item.get('truong'))}")

    return "\n".join(phan)


def lay_mot_loai(ngu_canh, ten_loai):
    if not ngu_canh or not ten_loai:
        return {}
    return ngu_canh.get(ten_loai, {})


def danh_sach_loai_ngu_canh():
    return [
        "hoi_thoai", "du_an", "file", "task_truoc", "linh_vuc",
        "ngon_ngu", "moi_truong", "rang_buoc", "thoi_gian", "cam_xuc",
    ]


def mo_ta_loai_ngu_canh():
    return {
        "hoi_thoai": "Những gì đã nói trước đó (10 khía cạnh)",
        "du_an": "Dự án hiện tại người dùng đang làm (10 khía cạnh)",
        "file": "File người dùng đang mở hoặc vừa nhắc (10 khía cạnh)",
        "task_truoc": "Task vừa làm xong (10 khía cạnh)",
        "linh_vuc": "Lĩnh vực đang làm việc (10 khía cạnh)",
        "ngon_ngu": "Ngôn ngữ lập trình đang dùng (10 khía cạnh)",
        "moi_truong": "Môi trường chạy local/Render/sandbox (10 khía cạnh)",
        "rang_buoc": "Yêu cầu đặc biệt đã nói trước (10 khía cạnh)",
        "thoi_gian": "Thời điểm task được gửi (10 khía cạnh)",
        "cam_xuc": "Thái độ của người dùng (10 khía cạnh)",
    }


def dem_khia_canh(ngu_canh):
    if not ngu_canh:
        return 0

    dem = 0
    for loai in danh_sach_loai_ngu_canh():
        du_lieu = ngu_canh.get(loai, {})
        if isinstance(du_lieu, dict):
            for k, v in du_lieu.items():
                if v not in (None, "", [], {}, 0, 0.0, "khong_ro", "trung_tinh"):
                    dem += 1
    return dem
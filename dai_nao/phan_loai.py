"""
phan_loai.py - Phân loại task Rồng Thần (bản đầy đủ, sâu, rộng).

Nhiệm vụ:
    - phan_loai(noi_dung, yeu_to): phân loại task thành 12 lĩnh vực chính.
    - Học thêm từ khóa mới khi gặp task không phân loại được.

Cấu trúc:
    12 lĩnh vực ngang:
        toán, văn, code, bug, khoa học, đời sống, kinh doanh,
        sáng tạo, học tập, tra cứu, kỹ thuật, luật - hành chính.

    Mỗi lĩnh vực chia nhiều nhóm dọc (nhóm → loại).

Cơ chế học:
    - Ưu tiên 1: từ khóa đã học (kho 2, collection tu_khoa_phan_loai).
    - Ưu tiên 2: từ khóa tĩnh (viết sẵn trong file).
    - Khi không khớp gì → trả "khac" và lưu lại làm mẫu học.

Trả về:
    {
        linh_vuc: str,
        nhom: str,
        loai: str,
        ngon_ngu: str,
        do_tin_cay: float,
        nguon: "hoc" | "tinh" | "khong",
    }
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
# TỪ KHÓA TĨNH — 12 LĨNH VỰC NGANG, CHIA SÂU
# ================================================================

# ----------------------------------------------------------------
# 1. TOÁN
# ----------------------------------------------------------------
TU_KHOA_TOAN = {
    "số học": {
        "cộng": ["cộng", "tổng", "+"],
        "trừ": ["trừ", "hiệu", "-"],
        "nhân": ["nhân", "tích", "x", "*"],
        "chia": ["chia", "thương", "/"],
        "phân số": ["phân số", "tử số", "mẫu số"],
        "phần trăm": ["phần trăm", "percent", "%"],
        "lũy thừa": ["lũy thừa", "mũ", "^", "power"],
        "căn bậc 2": ["căn bậc 2", "căn hai", "sqrt", "√"],
    },
    "đại số": {
        "logarit": ["logarit", "log", "ln"],
        "phương trình": ["phương trình", "giải pt", "tìm x"],
        "bất phương trình": ["bất phương trình", "bpt"],
        "hệ phương trình": ["hệ phương trình", "hpt"],
        "đa thức": ["đa thức", "polynomial"],
        "ma trận": ["ma trận", "matrix", "định thức"],
    },
    "hình học": {
        "diện tích": ["diện tích", "area"],
        "chu vi": ["chu vi", "perimeter"],
        "thể tích": ["thể tích", "volume"],
        "tam giác": ["tam giác", "triangle"],
        "hình tròn": ["hình tròn", "đường tròn", "circle"],
        "đa giác": ["đa giác", "polygon"],
        "vector": ["vector", "véc tơ", "vectơ"],
    },
    "giải tích": {
        "đạo hàm": ["đạo hàm", "derivative"],
        "tích phân": ["tích phân", "integral"],
        "giới hạn": ["giới hạn", "limit"],
        "chuỗi": ["chuỗi", "series"],
    },
    "lượng giác": {
        "sin": ["sin"],
        "cos": ["cos"],
        "tan": ["tan"],
        "cot": ["cot"],
    },
    "xác suất thống kê": {
        "xác suất": ["xác suất", "probability"],
        "trung bình": ["trung bình", "mean", "average"],
        "phương sai": ["phương sai", "variance"],
        "phân phối": ["phân phối", "distribution"],
        "tổ hợp": ["tổ hợp", "chỉnh hợp", "combination"],
    },
    "logic toán": {
        "chứng minh": ["chứng minh", "prove"],
        "mệnh đề": ["mệnh đề", "logic"],
    },
}


# ----------------------------------------------------------------
# 2. VĂN
# ----------------------------------------------------------------
TU_KHOA_VAN = {
    "viết đoạn văn": [
        "viết đoạn văn", "viết bài", "viết văn", "soạn văn",
    ],
    "viết email": ["viết email", "viết thư", "email"],
    "tiểu luận": ["tiểu luận", "essay", "bài luận"],
    "phân tích": ["phân tích", "analyze"],
    "nghị luận": ["nghị luận", "argument"],
    "tóm tắt": ["tóm tắt", "summary", "summarize", "rút gọn"],
    "dịch": ["dịch", "translate", "sang tiếng", "sang english", "sang việt"],
    "thơ": ["làm thơ", "sáng tác thơ", "viết thơ", "poem"],
    "kể chuyện": ["kể chuyện", "kể lại", "viết truyện"],
    "chính tả": ["chính tả", "ngữ pháp", "spelling"],
}


# ----------------------------------------------------------------
# 3. CODE
# ----------------------------------------------------------------
TU_KHOA_CODE = {
    "tạo mới": {
        "web": [
            "làm web", "tạo web", "trang web", "website",
            "giao diện", "html", "css", "landing page", "form",
            "frontend", "backend", "fullstack",
        ],
        "API": ["api", "rest", "endpoint", "graphql"],
        "mobile": ["app", "mobile", "android", "ios", "flutter", "react native"],
        "hàm": ["viết hàm", "tạo hàm", "function", "def "],
        "class": ["viết class", "tạo class", "class ", "oop"],
        "AI": [
            "làm ai", "tạo ai", "model", "machine learning",
            "deep learning", "neural", "dự đoán", "regression", "classifier",
            "chatbot", "llm", "gpt",
        ],
        "script": ["viết script", "viết tool", "viết bot", "crawl", "scrape", "automation"],
        "database": ["database", "sql", "mongodb", "mysql", "postgres", "redis"],
        "game": ["game", "unity", "pygame"],
        "thuật toán": ["thuật toán", "algorithm", "sort", "search", "dynamic"],
    },
    "sửa": ["sửa", "fix", "sửa lỗi", "sửa code", "refactor"],
    "tối ưu": ["tối ưu", "optimize", "nhanh hơn", "gọn hơn", "performance"],
    "review": ["review code", "đánh giá code", "kiểm tra code"],
    "giải thích": ["giải thích code", "code này làm gì", "hiểu code"],
    "chuyển đổi": ["chuyển", "convert", "đổi sang", "sang python", "sang js"],
}


# ----------------------------------------------------------------
# 4. BUG
# ----------------------------------------------------------------
TU_KHOA_BUG = {
    "syntax": ["syntaxerror", "cú pháp", "syntax", "indentationerror", "taberror"],
    "logic": ["logic", "kết quả sai", "sai kết quả", "không đúng", "sai logic"],
    "runtime": {
        "NameError": ["nameerror", "name '"],
        "TypeError": ["typeerror", "type '"],
        "ValueError": ["valueerror", "invalid literal"],
        "IndexError": ["indexerror", "list index out of range"],
        "KeyError": ["keyerror", "key '"],
        "AttributeError": ["attributeerror", "has no attribute"],
        "ImportError": ["importerror", "modulenotfounderror", "no module named"],
        "ZeroDivisionError": ["zerodivisionerror", "division by zero"],
        "RuntimeError": ["runtimeerror"],
    },
    "network": ["network", "timeout", "connection refused", "mạng"],
    "security": ["security", "xss", "sql injection", "csrf", "bảo mật"],
    "performance": ["chậm", "lag", "tốn ram", "tốn cpu", "memory leak"],
    "payment": ["402", "payment required", "thanh toán", "hết tiền"],
    "database": ["database error", "lỗi database", "duplicate key", "connection pool"],
}


# ----------------------------------------------------------------
# 5. KHOA HỌC
# ----------------------------------------------------------------
TU_KHOA_KHOA_HOC = {
    "vật lý": [
        "vật lý", "physics", "lực", "vận tốc", "gia tốc", "năng lượng",
        "điện", "từ", "quang", "nhiệt", "sóng",
    ],
    "hóa học": [
        "hóa học", "chemistry", "phản ứng", "nguyên tố", "phân tử",
        "axit", "bazơ", "muối", "công thức hóa",
    ],
    "sinh học": [
        "sinh học", "biology", "tế bào", "adn", "dna", "gen", "di truyền",
        "vi khuẩn", "virus", "thực vật", "động vật",
    ],
    "thiên văn": [
        "thiên văn", "astronomy", "hành tinh", "ngôi sao", "thiên hà",
        "vũ trụ", "sao hỏa", "mặt trời",
    ],
    "địa lý": [
        "địa lý", "geography", "quốc gia", "châu lục", "đại dương",
        "núi", "sông", "khí hậu",
    ],
    "môi trường": ["môi trường", "environment", "ô nhiễm", "biến đổi khí hậu"],
    "y học": ["y học", "bệnh", "triệu chứng", "thuốc", "sức khỏe"],
}


# ----------------------------------------------------------------
# 6. ĐỜI SỐNG
# ----------------------------------------------------------------
TU_KHOA_DOI_SONG = {
    "sức khỏe": [
        "sức khỏe", "bệnh", "đau", "triệu chứng", "dinh dưỡng",
        "thể dục", "yoga", "giảm cân",
    ],
    "nấu ăn": [
        "nấu ăn", "công thức", "món", "recipe", "nguyên liệu",
        "cách làm bánh", "cách nấu",
    ],
    "du lịch": [
        "du lịch", "travel", "địa điểm", "khách sạn", "vé",
        "lịch trình", "tour",
    ],
    "tài chính cá nhân": [
        "tiết kiệm", "đầu tư cá nhân", "ngân sách", "quản lý tiền",
        "chứng khoán", "vàng", "coin", "crypto",
    ],
    "tâm lý": [
        "tâm lý", "tâm trạng", "stress", "lo âu", "căng thẳng",
        "tự tin", "động lực",
    ],
    "mối quan hệ": ["tình yêu", "gia đình", "bạn bè", "hẹn hò", "chia tay"],
    "thể thao": ["bóng đá", "bóng rổ", "tennis", "cầu lông", "thể thao"],
    "thời trang": ["thời trang", "fashion", "quần áo", "phối đồ", "makeup"],
}


# ----------------------------------------------------------------
# 7. KINH DOANH
# ----------------------------------------------------------------
TU_KHOA_KINH_DOANH = {
    "marketing": [
        "marketing", "quảng cáo", "seo", "content", "facebook ads",
        "google ads", "thương hiệu", "brand",
    ],
    "bán hàng": ["bán hàng", "sales", "chốt đơn", "khách hàng", "telesales"],
    "quản lý": ["quản lý", "management", "nhân sự", "quy trình", "kpi"],
    "khởi nghiệp": ["khởi nghiệp", "startup", "ý tưởng kinh doanh", "business plan"],
    "tài chính doanh nghiệp": [
        "kế toán", "báo cáo tài chính", "lợi nhuận", "doanh thu", "chi phí",
    ],
    "đầu tư": ["đầu tư", "invest", "cổ phiếu", "trái phiếu", "bất động sản"],
    "thương mại điện tử": ["shopee", "lazada", "tiktok shop", "sàn tmđt", "ecommerce"],
}


# ----------------------------------------------------------------
# 8. SÁNG TẠO
# ----------------------------------------------------------------
TU_KHOA_SANG_TAO = {
    "viết truyện": ["viết truyện", "sáng tác truyện", "tiểu thuyết", "truyện ngắn"],
    "làm thơ": ["làm thơ", "sáng tác thơ", "viết thơ", "thơ"],
    "thiết kế": ["thiết kế", "design", "logo", "poster", "banner", "ui design"],
    "âm nhạc": ["âm nhạc", "sáng tác nhạc", "viết lời", "music", "melody"],
    "kịch bản": ["kịch bản", "script", "screenplay", "tiktok script"],
    "ý tưởng": ["ý tưởng", "idea", "brainstorm", "sáng kiến"],
    "vẽ": ["vẽ", "vẽ tranh", "digital art", "minh họa"],
}


# ----------------------------------------------------------------
# 9. HỌC TẬP
# ----------------------------------------------------------------
TU_KHOA_HOC_TAP = {
    "giải thích": ["giải thích", "explain", "nghĩa là gì", "hiểu"],
    "hướng dẫn": ["hướng dẫn", "tutorial", "cách làm", "làm sao", "how to"],
    "luyện tập": ["luyện tập", "bài tập", "exercise", "practice"],
    "kiểm tra": ["kiểm tra", "test", "quiz", "đề thi", "trắc nghiệm"],
    "tóm tắt bài học": ["tóm tắt bài", "ghi chú", "note", "summarize"],
}


# ----------------------------------------------------------------
# 10. TRA CỨU
# ----------------------------------------------------------------
TU_KHOA_TRA_CUU = {
    "định nghĩa": ["định nghĩa", "definition", "là gì"],
    "so sánh": ["so sánh", "compare", "khác nhau", "giống nhau"],
    "lịch sử": ["lịch sử", "history", "năm nào", "khi nào"],
    "tin tức": ["tin tức", "news", "mới nhất", "hôm nay"],
    "danh nhân": ["danh nhân", "ai là", "tiểu sử", "người nổi tiếng"],
    "sự kiện": ["sự kiện", "event", "diễn ra"],
}


# ----------------------------------------------------------------
# 11. KỸ THUẬT
# ----------------------------------------------------------------
TU_KHOA_KY_THUAT = {
    "điện": ["điện", "mạch điện", "nối dây", "điện áp", "dòng điện"],
    "cơ khí": ["cơ khí", "động cơ", "bánh răng", "piston", "máy móc"],
    "xây dựng": ["xây dựng", "bê tông", "móng", "cột", "dầm", "kiến trúc"],
    "ô tô": ["ô tô", "xe hơi", "động cơ xe", "bảo dưỡng xe", "oto"],
    "điện tử": ["điện tử", "vi mạch", "arduino", "esp32", "raspberry"],
    "robot": ["robot", "tự động hóa", "servo", "điều khiển"],
}


# ----------------------------------------------------------------
# 12. LUẬT - HÀNH CHÍNH
# ----------------------------------------------------------------
TU_KHOA_LUAT = {
    "luật": ["luật", "pháp luật", "điều luật", "bộ luật", "hình sự", "dân sự"],
    "hợp đồng": ["hợp đồng", "contract", "thỏa thuận", "biên bản"],
    "thủ tục": ["thủ tục", "giấy tờ", "hồ sơ", "đăng ký", "chứng minh"],
    "thuế": ["thuế", "tax", "khai thuế", "quyết toán"],
    "bảo hiểm": ["bảo hiểm", "insurance", "bhxh", "bhyt"],
}


# ================================================================
# GOM TẤT CẢ TỪ KHÓA TĨNH VÀO 1 BẢNG
# ================================================================
BANG_TU_KHOA_TINH = {
    "toán": TU_KHOA_TOAN,
    "văn": TU_KHOA_VAN,
    "code": TU_KHOA_CODE,
    "bug": TU_KHOA_BUG,
    "khoa học": TU_KHOA_KHOA_HOC,
    "đời sống": TU_KHOA_DOI_SONG,
    "kinh doanh": TU_KHOA_KINH_DOANH,
    "sáng tạo": TU_KHOA_SANG_TAO,
    "học tập": TU_KHOA_HOC_TAP,
    "tra cứu": TU_KHOA_TRA_CUU,
    "kỹ thuật": TU_KHOA_KY_THUAT,
    "luật - hành chính": TU_KHOA_LUAT,
}


# ================================================================
# NHẬN DIỆN NGÔN NGỮ LẬP TRÌNH
# ================================================================
def _nhan_dien_ngon_ngu(noi_dung):
    """Đoán ngôn ngữ lập trình từ nội dung."""
    if not noi_dung:
        return ""
    t = noi_dung.lower()

    if any(k in t for k in ("html", "css", "web", "giao diện", "trang")):
        return "HTML"
    if any(k in t for k in ("react", "vue", "angular", "next")):
        return "JavaScript"
    if any(k in t for k in ("python", "py", "print(", "def ", "import ")):
        return "Python"
    if any(k in t for k in ("javascript", "node", "js ")):
        return "JavaScript"
    if any(k in t for k in ("java ", "public class")):
        return "Java"
    if any(k in t for k in ("c++", "cpp", "#include")):
        return "C++"
    if any(k in t for k in ("c#", "csharp", "unity")):
        return "C#"
    if any(k in t for k in ("sql", "select ", "insert ")):
        return "SQL"
    return ""


# ================================================================
# ĐẾM KHỚP TỪ KHÓA
# ================================================================
def _dem_khop(noi_dung, danh_sach_tu_khoa):
    """Đếm số từ khóa khớp (xử lý ký tự đặc biệt)."""
    dem = 0
    for tk in danh_sach_tu_khoa:
        if tk and tk[0] in "+-*/^%":
            # Ký tự toán tử — chỉ khớp nếu đứng riêng
            if re.search(r"(?<!\w)" + re.escape(tk) + r"(?!\w)", noi_dung):
                dem += 1
        else:
            if tk in noi_dung:
                dem += 1
    return dem


# ================================================================
# DUYỆT CÂY TỪ KHÓA TĨNH
# ================================================================
def _duyet_tu_khoa_tinh(noi_dung, co_so):
    """
    Duyệt bảng từ khóa tĩnh, trả về kết quả tốt nhất.
    co_so: True nếu nội dung có số (cần cho toán).
    """
    tot_nhat = None
    diem_tot_nhat = 0

    for linh_vuc, cau_truc in BANG_TU_KHOA_TINH.items():

        # --- Trường hợp cấu trúc là dict 2 tầng ---
        if isinstance(cau_truc, dict) and cau_truc and isinstance(next(iter(cau_truc.values())), dict):
            # Ví dụ: toán → { "số học": { "cộng": [...] } }
            # Hoặc: bug → { "runtime": { "NameError": [...] } }
            for nhom, tu_khoa_con in cau_truc.items():
                if not isinstance(tu_khoa_con, dict):
                    continue
                for loai, danh_sach in tu_khoa_con.items():
                    if not isinstance(danh_sach, list):
                        continue
                    so_khop = _dem_khop(noi_dung, danh_sach)
                    if so_khop > 0:
                        # Toán cần có số
                        if linh_vuc == "toán" and not co_so:
                            continue
                        diem = so_khop
                        if diem > diem_tot_nhat:
                            diem_tot_nhat = diem
                            tot_nhat = {
                                "linh_vuc": linh_vuc,
                                "nhom": nhom,
                                "loai": loai,
                                "so_khop": so_khop,
                            }

        # --- Trường hợp cấu trúc là dict 1 tầng (list giá trị) ---
        elif isinstance(cau_truc, dict) and cau_truc and isinstance(next(iter(cau_truc.values())), list):
            # Ví dụ: văn → { "viết đoạn văn": [...], "tóm tắt": [...] }
            # Hoặc: code → { "tạo mới": { ... }, "sửa": [...] }  ← lẫn
            for nhom, danh_sach in cau_truc.items():
                if isinstance(danh_sach, dict):
                    # Nhóm con (như code → tạo mới → {web: [...]})
                    for loai, ds_con in danh_sach.items():
                        if not isinstance(ds_con, list):
                            continue
                        so_khop = _dem_khop(noi_dung, ds_con)
                        if so_khop > 0:
                            diem = so_khop
                            if diem > diem_tot_nhat:
                                diem_tot_nhat = diem
                                tot_nhat = {
                                    "linh_vuc": linh_vuc,
                                    "nhom": nhom,
                                    "loai": loai,
                                    "so_khop": so_khop,
                                }
                elif isinstance(danh_sach, list):
                    so_khop = _dem_khop(noi_dung, danh_sach)
                    if so_khop > 0:
                        diem = so_khop
                        if diem > diem_tot_nhat:
                            diem_tot_nhat = diem
                            tot_nhat = {
                                "linh_vuc": linh_vuc,
                                "nhom": nhom,
                                "loai": nhom,
                                "so_khop": so_khop,
                            }

    return tot_nhat


# ================================================================
# DUYỆT TỪ KHÓA ĐÃ HỌC (KHO 2)
# ================================================================
def _duyet_tu_khoa_da_hoc(noi_dung):
    """
    Duyệt từ khóa đã học từ kho 2.
    Ưu tiên từ khóa dài (khớp chính xác hơn) + nhiều lần dùng.
    """
    try:
        from dai_nao.ghi_nho import lay_tat_ca_tu_khoa_phan_loai
        danh_sach = lay_tat_ca_tu_khoa_phan_loai() or []
    except Exception:
        return None

    tot_nhat = None
    diem_tot_nhat = 0

    for tk in danh_sach:
        tu_khoa = (tk.get("tu_khoa") or "").lower()
        if not tu_khoa:
            continue
        if tu_khoa in noi_dung:
            # Điểm = độ dài từ khóa + số lần dùng
            diem = len(tu_khoa) + int(tk.get("so_lan_dung", 0))
            if diem > diem_tot_nhat:
                diem_tot_nhat = diem
                tot_nhat = {
                    "linh_vuc": tk.get("linh_vuc", ""),
                    "nhom": tk.get("nhom", ""),
                    "loai": tk.get("loai", ""),
                    "so_khop": 1,
                }
                # Tăng đếm
                try:
                    from dai_nao.ghi_nho import tang_dem_tu_khoa
                    tang_dem_tu_khoa(tu_khoa)
                except Exception:
                    pass

    return tot_nhat


# ================================================================
# HÀM HỌC TỪ KHÓA MỚI
# ================================================================
def _hoc_tu_khoa_moi(noi_dung, linh_vuc="khac", nhom="", loai=""):
    """
    Khi không phân loại được → lưu lại toàn bộ nội dung làm mẫu học.
    Lần sau gặp nội dung tương tự sẽ khớp nhanh hơn.
    Chỉ lưu nếu nội dung đủ dài (≥ 3 ký tự) và chưa có.
    """
    noi_dung = (noi_dung or "").strip().lower()
    if len(noi_dung) < 3:
        return

    # Cắt gọn — chỉ lưu tối đa 200 ký tự đầu
    tu_khoa = noi_dung[:200]

    try:
        from dai_nao.ghi_nho import luu_tu_khoa_phan_loai
        luu_tu_khoa_phan_loai({
            "tu_khoa": tu_khoa,
            "linh_vuc": linh_vuc,
            "nhom": nhom,
            "loai": loai,
            "so_lan_dung": 1,
            "thoi_gian": int(time.time()),
        })
    except Exception as e:
        _ghi_log("loi", f"Không lưu được từ khóa học: {e}")


# ================================================================
# HÀM CHÍNH
# ================================================================
def phan_loai(noi_dung, yeu_to=None):
    """
    Phân loại task (bản đầy đủ).

    Ưu tiên:
        1. Từ khóa đã học (kho 2).
        2. Từ khóa tĩnh (viết sẵn trong file).
        3. Không khớp → "khac" + lưu mẫu học.
    """
    noi_dung_goc = (noi_dung or "").strip()
    noi_dung = noi_dung_goc.lower()
    yeu_to = yeu_to or {}

    if not noi_dung:
        return {
            "linh_vuc": "khac",
            "nhom": "",
            "loai": "",
            "ngon_ngu": "",
            "do_tin_cay": 0.0,
            "nguon": "khong",
        }

    co_so = bool(re.search(r"\d", noi_dung))

    # ------------------------------------------------------------
    # 1. Ưu tiên từ khóa đã học
    # ------------------------------------------------------------
    ket_qua_hoc = _duyet_tu_khoa_da_hoc(noi_dung)
    if ket_qua_hoc and ket_qua_hoc.get("linh_vuc") not in ("", "khac"):
        return {
            "linh_vuc": ket_qua_hoc["linh_vuc"],
            "nhom": ket_qua_hoc.get("nhom", ""),
            "loai": ket_qua_hoc.get("loai", ""),
            "ngon_ngu": _nhan_dien_ngon_ngu(noi_dung_goc),
            "do_tin_cay": 0.9,
            "nguon": "hoc",
        }

    # ------------------------------------------------------------
    # 2. Duyệt từ khóa tĩnh
    # ------------------------------------------------------------
    ket_qua_tinh = _duyet_tu_khoa_tinh(noi_dung, co_so)
    if ket_qua_tinh:
        so_khop = ket_qua_tinh.get("so_khop", 1)
        # Độ tin cậy dựa trên số khớp
        do_tin_cay = min(0.95, 0.6 + 0.08 * so_khop)
        return {
            "linh_vuc": ket_qua_tinh["linh_vuc"],
            "nhom": ket_qua_tinh["nhom"],
            "loai": ket_qua_tinh["loai"],
            "ngon_ngu": _nhan_dien_ngon_ngu(noi_dung_goc),
            "do_tin_cay": do_tin_cay,
            "nguon": "tinh",
        }

    # ------------------------------------------------------------
    # 3. Không khớp → lưu mẫu học + trả "khac"
    # ------------------------------------------------------------
    _hoc_tu_khoa_moi(noi_dung_goc, linh_vuc="khac")

    return {
        "linh_vuc": "khac",
        "nhom": "",
        "loai": "",
        "ngon_ngu": _nhan_dien_ngon_ngu(noi_dung_goc),
        "do_tin_cay": 0.3,
        "nguon": "khong",
    }


# ================================================================
# TIỆN ÍCH
# ================================================================
def lay_nhom_chinh(loai_task):
    """Trả về lĩnh vực chính."""
    if not loai_task or not isinstance(loai_task, dict):
        return ""
    return loai_task.get("linh_vuc", "") or ""


def lay_tat_ca_linh_vuc():
    """Trả về danh sách 12 lĩnh vực."""
    return list(BANG_TU_KHOA_TINH.keys())
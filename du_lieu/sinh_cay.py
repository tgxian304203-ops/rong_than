"""
sinh_cay.py - Script sinh cây quyết định lớn cho Rồng Thần.

Nhiệm vụ:
    - Đọc template có sẵn trong file này.
    - Tự sinh 2000+ node cho cây quyết định.
    - Xuất ra 5 file JSON:
        + cay_quyet_dinh.json (gốc 12 lĩnh vực)
        + cay_toan.json
        + cay_code.json
        + cay_bug.json
        + cay_khac.json

Cách dùng:
    python du_lieu/sinh_cay.py

Sau khi chạy:
    - 5 file JSON được tạo trong du_lieu/.
    - Chạy Rồng Thần → ghi_nho.py tự gộp 5 file.

Quy tắc:
    - Node sinh ra KHÔNG có code mẫu (chỉ node cha có).
    - Node con kế thừa code từ cha khi cần.
    - Cây mọc tự do, không giới hạn nhánh con.
    - Mỗi node có đủ 25 trường theo schema_node.py.

Tầng dữ liệu: Không (script độc lập).
"""

import os
import json
import secrets
import time


# ================================================================
# HẰNG SỐ
# ================================================================
THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_DU_LIEU = os.path.join(THU_MUC_GOC, "du_lieu")

# Ngữ cảnh để sinh biến thể
NGU_CANH_LIST = [
    "cho học sinh cấp 1", "cho học sinh cấp 2", "cho học sinh cấp 3",
    "cho sinh viên", "cho người mới bắt đầu", "cho dân chuyên",
    "cho giáo viên", "cho phụ huynh",
    "bằng Python", "bằng JavaScript", "bằng Java", "bằng C++",
    "bằng HTML", "bằng SQL",
    "trong 5 phút", "trong 30 phút", "trong 1 giờ",
    "đơn giản nhất", "chi tiết nhất", "ngắn gọn nhất",
    "trên web", "trên mobile", "trên desktop",
    "local", "trên Render", "trên cloud",
    "vui vẻ", "nghiêm túc", "khẩn cấp",
]

MUC_DO_LIST = ["cơ bản", "trung bình", "nâng cao", "chuyên sâu", "siêu khó"]

# 12 lĩnh vực chính
LINH_VUC = [
    "toán", "văn", "code", "bug", "khoa học", "đời sống",
    "kinh doanh", "sáng tạo", "học tập", "tra cứu",
    "kỹ thuật", "luật - hành chính",
]


# ================================================================
# HÀM TẠO ID
# ================================================================
def _tao_id(prefix="nut"):
    """Tạo id ngẫu nhiên."""
    return f"{prefix}-{secrets.token_hex(6)}"


# ================================================================
# HÀM TẠO NODE RỖNG (25 trường)
# ================================================================
def _tao_node(ten, linh_vuc, loai_van_de="", cach_giai_phap="",
              ngu_canh="", code="", ngon_ngu="", dieu_kien_chua=None):
    """
    Tạo 1 node đầy đủ 25 trường.
    """
    return {
        "id": _tao_id(),
        "ten": ten,
        "phien_ban": 1,
        "dieu_kien": {
            "chua": dieu_kien_chua or [],
            "yeu_to_can": ["hanh_dong"],
        },
        "quy_tac": f"Xử lý task thuộc '{ten}'.",
        "thuat_toan": {
            "ten": ten.lower().replace(" ", "_"),
            "mo_ta": f"Thuật toán cho {ten}.",
            "do_phuc_tap": "O(1)",
        },
        "cach_giai": {
            "mo_ta": f"Cách giải cho {ten}.",
            "cac_buoc": ["Phân tích", "Xử lý", "Trả kết quả"],
            "vi_du": "",
        },
        "hanh_dong": {
            "loai": "chay_code" if code else "tra_loi",
            "code": code,
            "ngon_ngu": ngon_ngu,
        },
        "score": 0.7,
        "so_lan_thu": 0,
        "thanh_cong": 0,
        "that_bai": 0,
        "do_kho": 0.5,
        "thoi_gian_uoc_tinh": 1,
        "phu_thuoc": [],
        "uu_tien": 50,
        "nhanh_con": [],
        "chia_se_voi": [],
        "muon_tu": "",
        "failed_paths": [],
        "blacklist": False,
        "linh_vuc": linh_vuc,
        "loai_van_de": loai_van_de,
        "cach_giai_phap": cach_giai_phap,
        "ngu_canh_node": ngu_canh,
        "ngay_tao": int(time.time()),
        "lan_dung_cuoi": 0,
    }


# ================================================================
# TEMPLATE CÁC NHÓM CON
# ================================================================
TEMPLATE = {
    "toán": {
        "số học": {
            "cộng": ["cộng", "tổng", "+"],
            "trừ": ["trừ", "hiệu", "-"],
            "nhân": ["nhân", "tích", "x", "*"],
            "chia": ["chia", "thương", "/"],
            "phân số": ["phân số", "tử", "mẫu"],
            "phần trăm": ["phần trăm", "%", "percent"],
            "lũy thừa": ["lũy thừa", "mũ", "^", "power"],
            "căn bậc 2": ["căn", "sqrt", "√"],
            "logarit": ["logarit", "log", "ln"],
            "giai thừa": ["giai thừa", "factorial", "n!"],
            "trung bình": ["trung bình", "mean", "average"],
            "ước chung": ["ước chung", "ucln", "gcd"],
            "bội chung": ["bội chung", "bcnn", "lcm"],
            "số nguyên tố": ["số nguyên tố", "nguyên tố", "prime"],
            "dãy số": ["dãy số", "cấp số cộng", "cấp số nhân"],
            "làm tròn": ["làm tròn", "round"],
            "trị tuyệt đối": ["trị tuyệt đối", "abs"],
        },
        "đại số": {
            "phương trình bậc 1": ["phương trình bậc 1", "ax+b=0"],
            "phương trình bậc 2": ["phương trình bậc 2", "delta"],
            "phương trình bậc 3": ["phương trình bậc 3"],
            "bất phương trình": ["bất phương trình", "bpt"],
            "hệ phương trình": ["hệ phương trình", "hpt"],
            "đa thức": ["đa thức", "polynomial"],
            "ma trận": ["ma trận", "matrix", "định thức"],
            "vector": ["vector", "véc tơ"],
            "số phức": ["số phức", "complex"],
            "tổ hợp": ["tổ hợp", "combination"],
            "chỉnh hợp": ["chỉnh hợp", "permutation"],
            "hoán vị": ["hoán vị", "permutation"],
            "nhị thức newton": ["nhị thức newton"],
            "cấp số cộng": ["cấp số cộng"],
            "cấp số nhân": ["cấp số nhân"],
        },
        "hình học": {
            "diện tích tam giác": ["diện tích tam giác"],
            "diện tích hình tròn": ["diện tích hình tròn"],
            "diện tích hình vuông": ["diện tích hình vuông"],
            "diện tích hình chữ nhật": ["diện tích hình chữ nhật"],
            "diện tích hình thang": ["diện tích hình thang"],
            "chu vi hình tròn": ["chu vi hình tròn"],
            "chu vi hình vuông": ["chu vi hình vuông"],
            "thể tích hình lập phương": ["thể tích hình lập phương"],
            "thể tích hình cầu": ["thể tích hình cầu"],
            "thể tích hình trụ": ["thể tích hình trụ"],
            "thể tích hình nón": ["thể tích hình nón"],
            "định lý pitago": ["pitago", "pythagoras"],
            "tam giác đều": ["tam giác đều"],
            "đường tròn": ["đường tròn"],
            "elip": ["elip", "ellipse"],
            "parabol": ["parabol", "parabola"],
            "hypebol": ["hypebol", "hyperbola"],
        },
        "giải tích": {
            "đạo hàm": ["đạo hàm", "derivative"],
            "tích phân": ["tích phân", "integral"],
            "giới hạn": ["giới hạn", "limit"],
            "chuỗi": ["chuỗi", "series"],
            "hàm số": ["hàm số", "function"],
            "khảo sát hàm số": ["khảo sát hàm số"],
            "cực trị": ["cực trị", "cực đại", "cực tiểu"],
            "tiệm cận": ["tiệm cận"],
            "vi phân": ["vi phân"],
            "phương trình vi phân": ["phương trình vi phân"],
            "chuỗi taylor": ["taylor"],
            "chuỗi fourier": ["fourier"],
        },
        "lượng giác": {
            "sin": ["sin"],
            "cos": ["cos"],
            "tan": ["tan"],
            "cot": ["cot"],
            "arcsin": ["arcsin"],
            "arccos": ["arccos"],
            "arctan": ["arctan"],
            "công thức lượng giác": ["công thức lượng giác"],
            "phương trình lượng giác": ["phương trình lượng giác"],
            "bất đẳng thức lượng giác": ["bất đẳng thức lượng giác"],
        },
        "xác suất thống kê": {
            "xác suất": ["xác suất", "probability"],
            "phương sai": ["phương sai", "variance"],
            "độ lệch chuẩn": ["độ lệch chuẩn", "std"],
            "phân phối chuẩn": ["phân phối chuẩn", "normal"],
            "phân phối nhị thức": ["phân phối nhị thức"],
            "phân phối poisson": ["poisson"],
            "hồi quy": ["hồi quy", "regression"],
            "tương quan": ["tương quan", "correlation"],
            "kiểm định giả thuyết": ["kiểm định giả thuyết"],
            "trung vị": ["trung vị", "median"],
            "mode": ["mode", "yếu vị"],
            "tứ phân vị": ["tứ phân vị"],
        },
    },
    "văn": {
        "viết đoạn văn": ["viết đoạn văn", "viết bài", "soạn văn"],
        "viết email": ["viết email", "viết thư"],
        "tiểu luận": ["tiểu luận", "essay"],
        "phân tích": ["phân tích văn", "phân tích bài"],
        "nghị luận": ["nghị luận", "argument"],
        "tóm tắt": ["tóm tắt", "summary"],
        "dịch": ["dịch", "translate"],
        "thơ": ["làm thơ", "viết thơ", "poem"],
        "kể chuyện": ["kể chuyện", "viết truyện"],
        "chính tả": ["chính tả", "ngữ pháp"],
        "thuyết trình": ["thuyết trình", "presentation"],
        "thư từ": ["thư từ", "thư tay"],
    },
    "code": {
        "tạo mới web": ["web", "html", "css", "trang web", "landing"],
        "tạo mới API": ["api", "rest", "endpoint"],
        "tạo mới mobile": ["app", "mobile", "android", "ios"],
        "tạo mới hàm": ["viết hàm", "function"],
        "tạo mới class": ["class", "oop"],
        "tạo mới AI": ["ai", "model", "machine learning"],
        "tạo mới script": ["script", "tool", "bot", "crawl"],
        "tạo mới database": ["database", "sql", "mongodb"],
        "tạo mới game": ["game", "unity"],
        "thuật toán": ["thuật toán", "algorithm", "sort", "search"],
        "sửa code": ["sửa code", "fix", "refactor"],
        "tối ưu code": ["tối ưu", "optimize"],
        "review code": ["review code"],
        "giải thích code": ["giải thích code"],
        "chuyển đổi code": ["chuyển code", "convert"],
        "unit test": ["unit test", "test case"],
        "design pattern": ["design pattern"],
        "docker": ["docker", "dockerfile"],
        "deploy": ["deploy", "render", "heroku"],
    },
    "bug": {
        "syntax": ["syntaxerror", "cú pháp"],
        "nameerror": ["nameerror", "name '"],
        "typeerror": ["typeerror"],
        "valueerror": ["valueerror"],
        "indexerror": ["indexerror"],
        "keyerror": ["keyerror"],
        "attributeerror": ["attributeerror"],
        "importerror": ["importerror", "modulenotfound"],
        "runtimeerror": ["runtimeerror"],
        "zerodivision": ["zerodivision"],
        "recursion": ["recursionerror"],
        "memory": ["memoryerror"],
        "filenotfound": ["filenotfound"],
        "permission": ["permissionerror"],
        "connection": ["connectionerror", "connection refused"],
        "timeout": ["timeout"],
        "unicode": ["unicodeerror"],
        "assertion": ["assertionerror"],
        "network": ["network", "mạng"],
        "security": ["security", "xss", "csrf"],
        "performance": ["chậm", "lag", "tốn ram"],
        "payment": ["402", "payment"],
        "database": ["database error"],
        "config": ["config error", "sai config"],
    },
    "khoa học": {
        "vật lý": ["vật lý", "physics", "lực", "vận tốc", "năng lượng"],
        "hóa học": ["hóa học", "chemistry", "phản ứng"],
        "sinh học": ["sinh học", "biology", "tế bào"],
        "thiên văn": ["thiên văn", "astronomy", "hành tinh"],
        "địa lý": ["địa lý", "geography", "quốc gia"],
        "môi trường": ["môi trường", "ô nhiễm", "khí hậu"],
        "y học": ["y học", "bệnh", "triệu chứng"],
        "tâm lý học": ["tâm lý học", "psychology"],
        "xã hội học": ["xã hội học", "sociology"],
        "lịch sử": ["lịch sử", "history"],
    },
    "đời sống": {
        "sức khỏe": ["sức khỏe", "dinh dưỡng", "thể dục"],
        "nấu ăn": ["nấu ăn", "công thức", "món"],
        "du lịch": ["du lịch", "địa điểm", "lịch trình"],
        "tài chính cá nhân": ["tiết kiệm", "đầu tư", "ngân sách"],
        "tâm lý": ["tâm lý", "stress", "lo âu"],
        "mối quan hệ": ["tình yêu", "gia đình", "bạn bè"],
        "thể thao": ["bóng đá", "thể thao", "gym"],
        "thời trang": ["thời trang", "quần áo", "makeup"],
        "nuôi dạy con": ["nuôi con", "dạy con"],
        "chăm sóc thú cưng": ["thú cưng", "chó", "mèo"],
    },
    "kinh doanh": {
        "marketing": ["marketing", "quảng cáo", "seo"],
        "bán hàng": ["bán hàng", "sales"],
        "quản lý": ["quản lý", "management"],
        "khởi nghiệp": ["khởi nghiệp", "startup"],
        "tài chính DN": ["kế toán", "báo cáo tài chính"],
        "đầu tư": ["đầu tư", "cổ phiếu"],
        "tmđt": ["shopee", "lazada", "ecommerce"],
        "nhân sự": ["nhân sự", "tuyển dụng", "hr"],
        "thương hiệu": ["thương hiệu", "brand"],
        "logistics": ["logistics", "vận chuyển"],
    },
    "sáng tạo": {
        "viết truyện": ["viết truyện", "tiểu thuyết"],
        "làm thơ": ["làm thơ", "thơ"],
        "thiết kế": ["thiết kế", "design", "logo"],
        "âm nhạc": ["âm nhạc", "sáng tác nhạc"],
        "kịch bản": ["kịch bản", "script phim"],
        "ý tưởng": ["ý tưởng", "brainstorm"],
        "vẽ": ["vẽ", "digital art"],
        "nhiếp ảnh": ["nhiếp ảnh", "chụp ảnh"],
        "video": ["video", "edit video"],
        "content": ["content", "nội dung sáng tạo"],
    },
    "học tập": {
        "giải thích": ["giải thích", "explain"],
        "hướng dẫn": ["hướng dẫn", "tutorial"],
        "luyện tập": ["luyện tập", "bài tập"],
        "kiểm tra": ["kiểm tra", "quiz", "đề thi"],
        "tóm tắt bài": ["tóm tắt bài", "ghi chú"],
        "flashcard": ["flashcard", "thẻ ghi nhớ"],
        "mindmap": ["mindmap", "sơ đồ tư duy"],
        "ghi nhớ": ["ghi nhớ", "mẹo nhớ"],
        "ôn thi": ["ôn thi", "luyện thi"],
        "đọc hiểu": ["đọc hiểu"],
    },
    "tra cứu": {
        "định nghĩa": ["định nghĩa", "là gì"],
        "so sánh": ["so sánh", "khác nhau"],
        "lịch sử": ["lịch sử", "năm nào"],
        "tin tức": ["tin tức", "news"],
        "danh nhân": ["danh nhân", "tiểu sử"],
        "sự kiện": ["sự kiện", "event"],
        "thống kê": ["thống kê", "số liệu"],
        "địa chỉ": ["địa chỉ", "ở đâu"],
        "giá cả": ["giá cả", "bao nhiêu tiền"],
        "review": ["review", "đánh giá"],
    },
    "kỹ thuật": {
        "điện": ["điện", "mạch điện"],
        "cơ khí": ["cơ khí", "động cơ"],
        "xây dựng": ["xây dựng", "bê tông"],
        "ô tô": ["ô tô", "xe hơi"],
        "điện tử": ["điện tử", "arduino"],
        "robot": ["robot", "tự động hóa"],
        "nhiệt": ["nhiệt", "nhiệt động học"],
        "thủy lực": ["thủy lực", "khí nén"],
        "vật liệu": ["vật liệu", "kim loại"],
        "in 3d": ["in 3d", "3d printing"],
    },
    "luật - hành chính": {
        "luật dân sự": ["luật dân sự", "dân sự"],
        "luật hình sự": ["luật hình sự", "hình sự"],
        "luật lao động": ["luật lao động", "lao động"],
        "hợp đồng": ["hợp đồng", "contract"],
        "thủ tục hành chính": ["thủ tục", "giấy tờ"],
        "thuế": ["thuế", "tax"],
        "bảo hiểm": ["bảo hiểm", "bhxh"],
        "sở hữu trí tuệ": ["sở hữu trí tuệ", "bản quyền"],
        "hôn nhân": ["hôn nhân", "kết hôn", "ly hôn"],
        "đất đai": ["đất đai", "nhà đất"],
    },
}


# ================================================================
# HÀM SINH BIẾN THỂ
# ================================================================
def _sinh_bien_the(ten_goc, linh_vuc, loai_van_de, cach_giai_phap):
    """
    Sinh nhiều biến thể của 1 node gốc dựa trên ngữ cảnh + mức độ.
    Trả về list node.
    """
    danh_sach = []

    for ngu_canh in NGU_CANH_LIST[:15]:
        for muc_do in MUC_DO_LIST[:3]:
            ten_moi = f"{ten_goc} {muc_do} {ngu_canh}"

            node = _tao_node(
                ten=ten_moi,
                linh_vuc=linh_vuc,
                loai_van_de=loai_van_de,
                cach_giai_phap=cach_giai_phap,
                ngu_canh=ngu_canh,
                dieu_kien_chua=[ten_goc.lower()] + [ngu_canh.lower()],
            )
            node["do_kho"] = 0.5 if muc_do == "cơ bản" else 0.7
            node["uu_tien"] = 60 if muc_do == "cơ bản" else 40
            danh_sach.append(node)

    return danh_sach


# ================================================================
# HÀM SINH CÂY CHO 1 LĨNH VỰC
# ================================================================
def _sinh_cay_linh_vuc(linh_vuc, template):
    """
    Sinh cây cho 1 lĩnh vực từ template.

    Trả về: node lĩnh vực có nhánh con.
    """
    node_linh_vuc = _tao_node(
        ten=linh_vuc.title(),
        linh_vuc=linh_vuc,
        dieu_kien_chua=[],
    )
    node_linh_vuc["score"] = 0.9
    node_linh_vuc["uu_tien"] = 80
    node_linh_vuc["do_kho"] = 0.3

    # Duyệt template
    if isinstance(template, dict):
        # Template 2 tầng: nhóm → list hoặc dict
        for nhom, gia_tri in template.items():
            node_nhom = _tao_node(
                ten=nhom.title(),
                linh_vuc=linh_vuc,
                loai_van_de=nhom,
                dieu_kien_chua=[],
            )
            node_nhom["score"] = 0.85
            node_nhom["uu_tien"] = 75
            node_nhom["do_kho"] = 0.4

            if isinstance(gia_tri, dict):
                # Tầng 3: loại → list từ khóa
                for loai, tu_khoa in gia_tri.items():
                    node_loai = _tao_node(
                        ten=loai.title(),
                        linh_vuc=linh_vuc,
                        loai_van_de=nhom,
                        cach_giai_phap=loai,
                        dieu_kien_chua=tu_khoa if isinstance(tu_khoa, list) else [],
                    )
                    node_loai["score"] = 0.85
                    node_loai["uu_tien"] = 80
                    node_loai["do_kho"] = 0.5

                    # Sinh biến thể tầng 4
                    bien_the = _sinh_bien_the(loai, linh_vuc, nhom, loai)
                    node_loai["nhanh_con"] = bien_the

                    node_nhom["nhanh_con"].append(node_loai)

            elif isinstance(gia_tri, list):
                # Tầng 3 trực tiếp: nhóm → list từ khóa
                node_loai = _tao_node(
                    ten=nhom.title(),
                    linh_vuc=linh_vuc,
                    loai_van_de=nhom,
                    cach_giai_phap=nhom,
                    dieu_kien_chua=gia_tri,
                )
                node_loai["score"] = 0.85
                node_loai["uu_tien"] = 75

                bien_the = _sinh_bien_the(nhom, linh_vuc, nhom, nhom)
                node_loai["nhanh_con"] = bien_the
                node_nhom["nhanh_con"].append(node_loai)

            node_linh_vuc["nhanh_con"].append(node_nhom)

    return node_linh_vuc


# ================================================================
# HÀM CHÍNH
# ================================================================
def sinh_cay():
    """
    Sinh cây cho 12 lĩnh vực và xuất ra 5 file JSON.
    """
    print("=" * 60)
    print("🌱 Bắt đầu sinh cây quyết định Rồng Thần")
    print("=" * 60)

    # Tạo thư mục
    os.makedirs(THU_MUC_DU_LIEU, exist_ok=True)

    # Đếm tổng
    tong_node = 0

    # 1. Cây Toán
    print("\n📊 Sinh cây Toán...")
    cay_toan = _sinh_cay_linh_vuc("toán", TEMPLATE["toán"])
    _luu_file("cay_toan.json", cay_toan)
    dem = _dem_node(cay_toan)
    print(f"   → {dem} node")
    tong_node += dem

    # 2. Cây Code
    print("\n📊 Sinh cây Code...")
    cay_code = _sinh_cay_linh_vuc("code", TEMPLATE["code"])
    _luu_file("cay_code.json", cay_code)
    dem = _dem_node(cay_code)
    print(f"   → {dem} node")
    tong_node += dem

    # 3. Cây Bug
    print("\n📊 Sinh cây Bug...")
    cay_bug = _sinh_cay_linh_vuc("bug", TEMPLATE["bug"])
    _luu_file("cay_bug.json", cay_bug)
    dem = _dem_node(cay_bug)
    print(f"   → {dem} node")
    tong_node += dem

    # 4. Cây Khác (9 lĩnh vực còn lại)
    print("\n📊 Sinh cây cho 9 lĩnh vực còn lại...")
    cac_linh_vuc_khac = [
        "văn", "khoa học", "đời sống", "kinh doanh", "sáng tạo",
        "học tập", "tra cứu", "kỹ thuật", "luật - hành chính",
    ]
    cay_khac = {
        "id": _tao_id(),
        "ten": "Các lĩnh vực khác",
        "nhanh_con": [],
    }

    for linh_vuc in cac_linh_vuc_khac:
        if linh_vuc in TEMPLATE:
            node = _sinh_cay_linh_vuc(linh_vuc, TEMPLATE[linh_vuc])
            cay_khac["nhanh_con"].append(node)
            dem_lv = _dem_node(node)
            print(f"   → {linh_vuc}: {dem_lv} node")
            tong_node += dem_lv

    _luu_file("cay_khac.json", cay_khac)

    # 5. Cây gốc (12 node cấp 1)
    print("\n📊 Sinh cây gốc...")
    cay_goc = {
        "id": "root",
        "ten": "ROOT",
        "phien_ban": 1,
        "dieu_kien": {"chua": [], "yeu_to_can": []},
        "quy_tac": "Node gốc cây quyết định Rồng Thần.",
        "thuat_toan": {"ten": "duyet_cay", "mo_ta": "Duyệt 4 tầng", "do_phuc_tap": "O(n)"},
        "cach_giai": {"mo_ta": "Node gốc.", "cac_buoc": [], "vi_du": ""},
        "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
        "score": 1.0,
        "so_lan_thu": 0,
        "thanh_cong": 0,
        "that_bai": 0,
        "do_kho": 0.0,
        "thoi_gian_uoc_tinh": 0,
        "phu_thuoc": [],
        "uu_tien": 100,
        "nhanh_con": [
            {"id": "nut-linhvuc-toan-0001", "ten": "Toán", "phien_ban": 1,
             "dieu_kien": {"chua": ["toán", "tính", "cộng", "trừ"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Toán.",
             "thuat_toan": {"ten": "phan_loai_toan", "mo_ta": "7 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_toan.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.9, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.3, "thoi_gian_uoc_tinh": 1, "phu_thuoc": [], "uu_tien": 80,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "toán", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-van-0001", "ten": "Văn", "phien_ban": 1,
             "dieu_kien": {"chua": ["văn", "viết", "đoạn văn"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Văn.",
             "thuat_toan": {"ten": "phan_loai_van", "mo_ta": "12 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_khac.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.85, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.4, "thoi_gian_uoc_tinh": 2, "phu_thuoc": [], "uu_tien": 75,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "văn", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-code-0001", "ten": "Code", "phien_ban": 1,
             "dieu_kien": {"chua": ["code", "lập trình", "web", "hàm"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Code.",
             "thuat_toan": {"ten": "phan_loai_code", "mo_ta": "19 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_code.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.95, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.5, "thoi_gian_uoc_tinh": 2, "phu_thuoc": [], "uu_tien": 90,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "code", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-bug-0001", "ten": "Bug", "phien_ban": 1,
             "dieu_kien": {"chua": ["lỗi", "bug", "error"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Bug.",
             "thuat_toan": {"ten": "phan_loai_bug", "mo_ta": "24 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_bug.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.95, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.6, "thoi_gian_uoc_tinh": 3, "phu_thuoc": [], "uu_tien": 90,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "bug", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-khoahoc-0001", "ten": "Khoa học", "phien_ban": 1,
             "dieu_kien": {"chua": ["khoa học", "vật lý", "hóa học"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Khoa học.",
             "thuat_toan": {"ten": "phan_loai_khoahoc", "mo_ta": "10 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_khac.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.85, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.5, "thoi_gian_uoc_tinh": 2, "phu_thuoc": [], "uu_tien": 75,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "khoa học", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-doisong-0001", "ten": "Đời sống", "phien_ban": 1,
             "dieu_kien": {"chua": ["sức khỏe", "nấu ăn", "du lịch"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Đời sống.",
             "thuat_toan": {"ten": "phan_loai_doisong", "mo_ta": "10 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_khac.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.85, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.4, "thoi_gian_uoc_tinh": 2, "phu_thuoc": [], "uu_tien": 75,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "đời sống", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-kinhdoanh-0001", "ten": "Kinh doanh", "phien_ban": 1,
             "dieu_kien": {"chua": ["kinh doanh", "marketing", "bán hàng"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Kinh doanh.",
             "thuat_toan": {"ten": "phan_loai_kinhdoanh", "mo_ta": "10 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_khac.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.85, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.5, "thoi_gian_uoc_tinh": 2, "phu_thuoc": [], "uu_tien": 75,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "kinh doanh", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-sangtao-0001", "ten": "Sáng tạo", "phien_ban": 1,
             "dieu_kien": {"chua": ["sáng tạo", "viết truyện", "thiết kế"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Sáng tạo.",
             "thuat_toan": {"ten": "phan_loai_sangtao", "mo_ta": "10 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_khac.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.85, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.5, "thoi_gian_uoc_tinh": 2, "phu_thuoc": [], "uu_tien": 75,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "sáng tạo", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-hoctap-0001", "ten": "Học tập", "phien_ban": 1,
             "dieu_kien": {"chua": ["giải thích", "hướng dẫn", "luyện tập"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Học tập.",
             "thuat_toan": {"ten": "phan_loai_hoctap", "mo_ta": "10 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_khac.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.85, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.4, "thoi_gian_uoc_tinh": 2, "phu_thuoc": [], "uu_tien": 75,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "học tập", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-tracuu-0001", "ten": "Tra cứu", "phien_ban": 1,
             "dieu_kien": {"chua": ["tra cứu", "định nghĩa", "so sánh"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Tra cứu.",
             "thuat_toan": {"ten": "phan_loai_tracuu", "mo_ta": "10 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_khac.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.85, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.3, "thoi_gian_uoc_tinh": 2, "phu_thuoc": [], "uu_tien": 75,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "tra cứu", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-kithuat-0001", "ten": "Kỹ thuật", "phien_ban": 1,
             "dieu_kien": {"chua": ["kỹ thuật", "điện", "cơ khí"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Kỹ thuật.",
             "thuat_toan": {"ten": "phan_loai_kithuat", "mo_ta": "10 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_khac.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.85, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.5, "thoi_gian_uoc_tinh": 2, "phu_thuoc": [], "uu_tien": 75,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "kỹ thuật", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
            {"id": "nut-linhvuc-luat-0001", "ten": "Luật - Hành chính", "phien_ban": 1,
             "dieu_kien": {"chua": ["luật", "hợp đồng", "thủ tục"], "yeu_to_can": ["hanh_dong"]},
             "quy_tac": "Lĩnh vực Luật.",
             "thuat_toan": {"ten": "phan_loai_luat", "mo_ta": "10 nhóm", "do_phuc_tap": "O(1)"},
             "cach_giai": {"mo_ta": "Xem cay_khac.json", "cac_buoc": [], "vi_du": ""},
             "hanh_dong": {"loai": "tra_loi", "code": "", "ngon_ngu": ""},
             "score": 0.85, "so_lan_thu": 0, "thanh_cong": 0, "that_bai": 0,
             "do_kho": 0.5, "thoi_gian_uoc_tinh": 2, "phu_thuoc": [], "uu_tien": 75,
             "nhanh_con": [], "chia_se_voi": [], "muon_tu": "", "failed_paths": [],
             "blacklist": False, "linh_vuc": "luật - hành chính", "loai_van_de": "",
             "cach_giai_phap": "", "ngu_canh_node": "", "ngay_tao": 0, "lan_dung_cuoi": 0},
        ],
        "chia_se_voi": [],
        "muon_tu": "",
        "failed_paths": [],
        "blacklist": False,
        "linh_vuc": "",
        "loai_van_de": "",
        "cach_giai_phap": "",
        "ngu_canh_node": "",
        "ngay_tao": 0,
        "lan_dung_cuoi": 0,
    }
    _luu_file("cay_quyet_dinh.json", cay_goc)

    # Tổng kết
    print("\n" + "=" * 60)
    print(f"✅ HOÀN THÀNH! Tổng cộng: {tong_node} node")
    print(f"📁 Đã ghi vào: {THU_MUC_DU_LIEU}")
    print("=" * 60)
    print("\nCác file đã tạo:")
    for f in ["cay_quyet_dinh.json", "cay_toan.json", "cay_code.json",
              "cay_bug.json", "cay_khac.json"]:
        duong_dan = os.path.join(THU_MUC_DU_LIEU, f)
        if os.path.exists(duong_dan):
            size = os.path.getsize(duong_dan) / 1024
            print(f"  - {f}: {size:.1f} KB")


# ================================================================
# HÀM PHỤ
# ================================================================
def _luu_file(ten_file, du_lieu):
    """Lưu dữ liệu vào file JSON."""
    duong_dan = os.path.join(THU_MUC_DU_LIEU, ten_file)
    try:
        with open(duong_dan, "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Lỗi ghi file {ten_file}: {e}")
        return False


def _dem_node(node):
    """Đếm tổng số node trong cây (đệ quy)."""
    if not node:
        return 0
    dem = 1
    for con in node.get("nhanh_con", []):
        dem += _dem_node(con)
    return dem


# ================================================================
# CHẠY
# ================================================================
if __name__ == "__main__":
    sinh_cay()
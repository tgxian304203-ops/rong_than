"""
doc_loi.py - Đọc lỗi khổng lồ Rồng Thần (300+ loại).

Nhiệm vụ:
    - doc_loi(stderr): đọc lỗi đầu tiên, nhận diện loại + vị trí + gợi ý.
    - doc_loi_nhieu(stderr): đọc TẤT CẢ lỗi.
    - trich_traceback(stderr): trích toàn bộ traceback.
    - tim_dong_bi_loi(stderr, code): tìm đúng dòng code bị lỗi.
    - goi_y_sua_loi(stderr): gợi ý sửa.
    - tra_tu_dien_loi(loai_loi): tra từ điển kho 2.

Hỗ trợ 20 nhóm ngôn ngữ/môi trường:
    Python, JavaScript/Node, Java, C/C++, Web/HTTP, Database,
    Framework, API/Network, Docker/Deploy, OS/File,
    Ruby, PHP, Go, Rust, Swift, Kotlin, C#/.NET, SQL, Bash, Git,
    Redis, Elasticsearch, Kubernetes, Cloud, AI/ML, Web3,
    Game Dev, Mobile, Testing, Build/Package.

Mỗi loại lỗi có 12 trường:
    ngon_ngu, muc_do, mau, mo_ta, vi_du, goi_y,
    co_the_tu_sua, code_sua_mau, tai_lieu, thoi_gian_sua,
    do_nghiem_trong (1-5), pho_bien.

Tầng dữ liệu: dai_nao/ghi_nho.py
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
# HÀM TIỆN: TẠO MỤC LỖI (12 TRƯỜNG)
# ================================================================
def _muc(ngon_ngu, muc_do, mau, mo_ta, vi_du="", goi_y=None,
         co_the_tu_sua=False, code_sua_mau="",
         tai_lieu="", thoi_gian_sua="trung_binh",
         do_nghiem_trong=3, pho_bien=False):
    """
    Tạo dict mục lỗi đầy đủ 12 trường.

    muc_do: "nghiem_trong" | "canh_bao" | "thong_tin"
    thoi_gian_sua: "nhanh" (<5 phút) | "trung_binh" (5-30 phút) | "lau" (>30 phút)
    do_nghiem_trong: 1-5 sao
    pho_bien: True/False — lỗi có gặp thường xuyên không
    """
    return {
        "ngon_ngu": ngon_ngu,
        "muc_do": muc_do,
        "mau": mau,
        "mo_ta": mo_ta,
        "vi_du": vi_du,
        "goi_y": goi_y or [],
        "co_the_tu_sua": co_the_tu_sua,
        "code_sua_mau": code_sua_mau,
        "tai_lieu": tai_lieu,
        "thoi_gian_sua": thoi_gian_sua,
        "do_nghiem_trong": do_nghiem_trong,
        "pho_bien": pho_bien,
    }


# ================================================================
# BẢNG NHẬN DIỆN LỖI — 300+ LOẠI
# ================================================================
LOAI_LOI = {

    # ============================================================
    # NHÓM 1: PYTHON (50+ loại)
    # ============================================================
    "NameError": _muc(
        "Python", "nghiem_trong",
        r"NameError:\s*name\s+'([^']+)'\s+is\s+not\s+defined",
        "Dùng biến/hàm chưa khai báo.",
        "print(x) khi x chưa gán",
        ["Khai báo biến trước khi dùng: x = 0",
         "Kiểm tra viết đúng tên chưa (chữ hoa/thường).",
         "Kiểm tra đã import thư viện chưa."],
        True, "# Sửa:\nx = 0\nprint(x)",
        "https://docs.python.org/3/library/exceptions.html#NameError",
        "nhanh", 4, True,
    ),
    "TypeError": _muc(
        "Python", "nghiem_trong",
        r"TypeError:\s*(.+)",
        "Sai kiểu dữ liệu (ví dụ: cộng số với chuỗi).",
        "1 + 'abc'",
        ["Ép kiểu: int(), float(), str() trước khi tính.",
         "Kiểm tra hàm nhận đúng số lượng tham số chưa.",
         "In type() để xem kiểu dữ liệu hiện tại."],
        True, "# Sửa:\nint('5') + 3  # thay vì '5' + 3",
        "https://docs.python.org/3/library/exceptions.html#TypeError",
        "nhanh", 4, True,
    ),
    "ValueError": _muc(
        "Python", "nghiem_trong",
        r"ValueError:\s*(.+)",
        "Giá trị không hợp lệ cho hàm.",
        "int('abc')",
        ["Kiểm tra giá trị đầu vào.",
         "Dùng try/except để bắt lỗi.",
         "int('abc') lỗi — phải là int('123')."],
        True, "# Sửa:\ntry:\n    n = int(s)\nexcept ValueError:\n    n = 0",
        "https://docs.python.org/3/library/exceptions.html#ValueError",
        "nhanh", 4, True,
    ),
    "ImportError": _muc(
        "Python", "nghiem_trong",
        r"ImportError:\s*(.+)",
        "Không import được module.",
        "from xxx import yyy",
        ["Kiểm tra tên module.",
         "Cài thêm: pip install <tên>.",
         "Kiểm tra yeu_cau.txt."],
        False, "# Sửa:\n# pip install flask",
        "https://docs.python.org/3/library/exceptions.html#ImportError",
        "nhanh", 4, True,
    ),
    "ModuleNotFoundError": _muc(
        "Python", "nghiem_trong",
        r"ModuleNotFoundError:\s*No\s+module\s+named\s+'([^']+)'",
        "Không tìm thấy module.",
        "import pandas  (chưa cài)",
        ["Cài: pip install <module>.",
         "Thêm vào yeu_cau.txt."],
        False, "# Sửa:\n# Thêm vào yeu_cau.txt:\n# pandas",
        "https://docs.python.org/3/library/exceptions.html#ModuleNotFoundError",
        "nhanh", 4, True,
    ),
    "SyntaxError": _muc(
        "Python", "nghiem_trong",
        r"SyntaxError:\s*(.+)",
        "Sai cú pháp.",
        "print('abc'  (thiếu dấu đóng)",
        ["Kiểm tra dấu ngoặc.",
         "Kiểm tra dấu hai chấm sau if/for/def.",
         "Kiểm tra dấu nháy."],
        True, "# Sửa:\nprint('abc')",
        "https://docs.python.org/3/library/exceptions.html#SyntaxError",
        "nhanh", 4, True,
    ),
    "IndentationError": _muc(
        "Python", "nghiem_trong",
        r"IndentationError:\s*(.+)",
        "Sai thụt lề.",
        "Thiếu/thừa space đầu dòng.",
        ["Python cần 4 space.",
         "Không trộn tab và space."],
        True, "# Sửa:\nif x:\n    print('a')",
        "https://docs.python.org/3/library/exceptions.html#IndentationError",
        "nhanh", 4, True,
    ),
    "TabError": _muc(
        "Python", "nghiem_trong",
        r"TabError:\s*(.+)",
        "Trộn tab và space.",
        "Dòng dùng tab, dòng dùng space.",
        ["Chỉ dùng space."],
        True, "# Sửa:\n# Chỉ dùng space.",
        "https://docs.python.org/3/library/exceptions.html#TabError",
        "nhanh", 3, False,
    ),
    "IndexError": _muc(
        "Python", "nghiem_trong",
        r"IndexError:\s*(.+)",
        "Truy cập index ngoài phạm vi.",
        "[1,2,3][10]",
        ["Kiểm tra index.",
         "Dùng list[-1].",
         "Dùng if i < len(lst)."],
        True, "# Sửa:\nif i < len(lst):\n    print(lst[i])",
        "https://docs.python.org/3/library/exceptions.html#IndexError",
        "nhanh", 4, True,
    ),
    "KeyError": _muc(
        "Python", "nghiem_trong",
        r"KeyError:\s*(.+)",
        "Key không tồn tại trong dict.",
        "{}['abc']",
        ["Dùng dict.get(key, mặc_định).",
         "Kiểm tra key trước."],
        True, "# Sửa:\ngia_tri = d.get('abc', 0)",
        "https://docs.python.org/3/library/exceptions.html#KeyError",
        "nhanh", 4, True,
    ),
    "AttributeError": _muc(
        "Python", "nghiem_trong",
        r"AttributeError:\s*(.+)",
        "Object không có thuộc tính đó.",
        "'abc'.xyz()",
        ["Kiểm tra kiểu của object.",
         "Dùng dir(obj)."],
        False, "# Sửa:\n# 'abc'.upper() thay vì .xyz()",
        "https://docs.python.org/3/library/exceptions.html#AttributeError",
        "trung_binh", 3, True,
    ),
    "ZeroDivisionError": _muc(
        "Python", "nghiem_trong",
        r"ZeroDivisionError:\s*(.+)",
        "Chia cho 0.",
        "1 / 0",
        ["Kiểm tra mẫu số trước khi chia."],
        True, "# Sửa:\nif b != 0:\n    kq = a / b",
        "https://docs.python.org/3/library/exceptions.html#ZeroDivisionError",
        "nhanh", 4, True,
    ),
    "RuntimeError": _muc(
        "Python", "nghiem_trong",
        r"RuntimeError:\s*(.+)",
        "Lỗi runtime chung.",
        "raise RuntimeError('...')",
        ["Kiểm tra logic."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#RuntimeError",
        "trung_binh", 3, False,
    ),
    "RecursionError": _muc(
        "Python", "nghiem_trong",
        r"RecursionError:\s*(.+)",
        "Đệ quy quá sâu.",
        "def f(): return f()",
        ["Thêm điều kiện dừng.",
         "Chuyển sang vòng lặp."],
        True, "# Sửa:\ndef f(n):\n    if n <= 0:\n        return 0\n    return f(n-1)",
        "https://docs.python.org/3/library/exceptions.html#RecursionError",
        "trung_binh", 4, True,
    ),
    "MemoryError": _muc(
        "Python", "nghiem_trong",
        r"MemoryError",
        "Hết bộ nhớ.",
        "Tạo list quá lớn.",
        ["Giảm dữ liệu.",
         "Dùng generator."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#MemoryError",
        "lau", 5, False,
    ),
    "OverflowError": _muc(
        "Python", "nghiem_trong",
        r"OverflowError:\s*(.+)",
        "Tràn số.",
        "math.exp(1000)",
        ["Kiểm tra giới hạn.",
         "Dùng log."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#OverflowError",
        "trung_binh", 3, False,
    ),
    "FloatingPointError": _muc(
        "Python", "canh_bao",
        r"FloatingPointError:\s*(.+)",
        "Lỗi số thực (hiếm).",
        "Chia 0 trong numpy.",
        ["Kiểm tra numpy.seterr()."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#FloatingPointError",
        "trung_binh", 2, False,
    ),
    "FileNotFoundError": _muc(
        "Python", "nghiem_trong",
        r"FileNotFoundError:\s*(.+)",
        "Không tìm thấy file.",
        "open('khong_ton_tai.txt')",
        ["Kiểm tra đường dẫn.",
         "Dùng os.path.exists()."],
        True, "# Sửa:\nimport os\nif os.path.exists(path):\n    f = open(path)",
        "https://docs.python.org/3/library/exceptions.html#FileNotFoundError",
        "nhanh", 4, True,
    ),
    "FileExistsError": _muc(
        "Python", "canh_bao",
        r"FileExistsError:\s*(.+)",
        "File đã tồn tại.",
        "os.mkdir('abc') khi abc đã có.",
        ["Dùng exist_ok=True."],
        True, "# Sửa:\nos.makedirs('abc', exist_ok=True)",
        "https://docs.python.org/3/library/exceptions.html#FileExistsError",
        "nhanh", 3, False,
    ),
    "PermissionError": _muc(
        "Python", "nghiem_trong",
        r"PermissionError:\s*(.+)",
        "Không có quyền.",
        "open('/root/abc')",
        ["Kiểm tra quyền.",
         "Chmod."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#PermissionError",
        "trung_binh", 3, True,
    ),
    "IsADirectoryError": _muc(
        "Python", "nghiem_trong",
        r"IsADirectoryError:\s*(.+)",
        "Mở thư mục như file.",
        "open('/home')",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://docs.python.org/3/library/exceptions.html#IsADirectoryError",
        "nhanh", 3, False,
    ),
    "NotADirectoryError": _muc(
        "Python", "nghiem_trong",
        r"NotADirectoryError:\s*(.+)",
        "Không phải thư mục.",
        "os.listdir('abc.txt')",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://docs.python.org/3/library/exceptions.html#NotADirectoryError",
        "nhanh", 3, False,
    ),
    "OSError": _muc(
        "Python", "nghiem_trong",
        r"OSError:\s*(.+)",
        "Lỗi hệ điều hành.",
        "open('/root/abc')",
        ["Đọc kỹ thông điệp.",
         "Kiểm tra đường dẫn."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#OSError",
        "trung_binh", 3, False,
    ),
    "IOError": _muc(
        "Python", "nghiem_trong",
        r"IOError:\s*(.+)",
        "Lỗi vào/ra.",
        "Đọc file lỗi.",
        ["Tương tự OSError."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#IOError",
        "trung_binh", 2, False,
    ),
    "EOFError": _muc(
        "Python", "nghiem_trong",
        r"EOFError:\s*(.*)",
        "Đọc input nhưng gặp EOF.",
        "input() khi không có dữ liệu.",
        ["Bọc try/except EOFError."],
        True, "# Sửa:\ntry:\n    s = input()\nexcept EOFError:\n    s = ''",
        "https://docs.python.org/3/library/exceptions.html#EOFError",
        "nhanh", 3, True,
    ),
    "StopIteration": _muc(
        "Python", "canh_bao",
        r"StopIteration",
        "Iterator kết thúc.",
        "next(iter([]))",
        ["Dùng for thay next().",
         "Bọc try/except."],
        True, "",
        "https://docs.python.org/3/library/exceptions.html#StopIteration",
        "nhanh", 3, True,
    ),
    "StopAsyncIteration": _muc(
        "Python", "canh_bao",
        r"StopAsyncIteration",
        "Async iterator kết thúc.",
        "Tương tự StopIteration.",
        ["Dùng async for."],
        True, "",
        "https://docs.python.org/3/library/exceptions.html#StopAsyncIteration",
        "nhanh", 2, False,
    ),
    "AssertionError": _muc(
        "Python", "nghiem_trong",
        r"AssertionError:\s*(.*)",
        "Câu lệnh assert thất bại.",
        "assert 1 == 2",
        ["Kiểm tra điều kiện assert.",
         "Bỏ assert nếu chỉ để debug."],
        True, "# Sửa:\n# assert x > 0 → if x <= 0: raise ValueError",
        "https://docs.python.org/3/library/exceptions.html#AssertionError",
        "nhanh", 3, True,
    ),
    "NotImplementedError": _muc(
        "Python", "canh_bao",
        r"NotImplementedError:\s*(.*)",
        "Hàm chưa cài đặt.",
        "raise NotImplementedError",
        ["Cài đặt hàm.",
         "Kiểm tra lớp con override."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#NotImplementedError",
        "trung_binh", 3, False,
    ),
    "UnboundLocalError": _muc(
        "Python", "nghiem_trong",
        r"UnboundLocalError:\s*(.+)",
        "Biến local dùng trước khi gán.",
        "def f():\n    print(x)\n    x = 1",
        ["Gán trước khi dùng.",
         "Dùng global nếu cần."],
        True, "# Sửa:\ndef f():\n    x = 1\n    print(x)",
        "https://docs.python.org/3/library/exceptions.html#UnboundLocalError",
        "nhanh", 4, True,
    ),
    "ReferenceError": _muc(
        "Python", "nghiem_trong",
        r"ReferenceError:\s*(.+)",
        "Tham chiếu yếu đã bị giải phóng.",
        "Dùng weakref sau khi object bị xóa.",
        ["Kiểm tra object còn tồn tại."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#ReferenceError",
        "trung_binh", 2, False,
    ),
    "ArithmeticError": _muc(
        "Python", "nghiem_trong",
        r"ArithmeticError:\s*(.+)",
        "Lỗi số học chung.",
        "Lỗi chia, tràn số.",
        ["Kiểm tra mẫu số."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#ArithmeticError",
        "nhanh", 3, False,
    ),
    "LookupError": _muc(
        "Python", "nghiem_trong",
        r"LookupError:\s*(.+)",
        "Lỗi tra cứu.",
        "lst[999] hoặc d['xxx']",
        ["Kiểm tra index/key."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#LookupError",
        "nhanh", 3, False,
    ),
    "SystemExit": _muc(
        "Python", "thong_tin",
        r"SystemExit:\s*(.*)",
        "Chương trình gọi sys.exit().",
        "sys.exit(0)",
        ["Bình thường nếu chủ ý thoát."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#SystemExit",
        "nhanh", 1, False,
    ),
    "SystemError": _muc(
        "Python", "nghiem_trong",
        r"SystemError:\s*(.+)",
        "Lỗi hệ thống Python.",
        "Rất hiếm gặp.",
        ["Khởi động lại."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#SystemError",
        "lau", 4, False,
    ),
    "UnicodeDecodeError": _muc(
        "Python", "nghiem_trong",
        r"UnicodeDecodeError:\s*(.+)",
        "Không giải mã được chuỗi.",
        "Mở file binary với 'r'.",
        ["Dùng encoding='utf-8'.",
         "Dùng errors='replace'.",
         "Mở 'rb' nếu binary."],
        True, "# Sửa:\nopen('file.txt', 'r', encoding='utf-8', errors='replace')",
        "https://docs.python.org/3/library/exceptions.html#UnicodeDecodeError",
        "nhanh", 3, True,
    ),
    "UnicodeEncodeError": _muc(
        "Python", "nghiem_trong",
        r"UnicodeEncodeError:\s*(.+)",
        "Không mã hóa được chuỗi.",
        "Ghi emoji vào file ASCII.",
        ["Dùng encoding='utf-8'."],
        True, "# Sửa:\nopen('file.txt', 'w', encoding='utf-8')",
        "https://docs.python.org/3/library/exceptions.html#UnicodeEncodeError",
        "nhanh", 3, True,
    ),
    "UnicodeError": _muc(
        "Python", "nghiem_trong",
        r"UnicodeError:\s*(.+)",
        "Lỗi Unicode chung.",
        "Chuỗi không hợp lệ.",
        ["Kiểm tra encoding."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#UnicodeError",
        "trung_binh", 3, False,
    ),
    "ConnectionError": _muc(
        "Python", "nghiem_trong",
        r"ConnectionError:\s*(.+)",
        "Lỗi kết nối mạng.",
        "requests.get() khi mất mạng.",
        ["Kiểm tra mạng.",
         "Bọc try/except."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#ConnectionError",
        "trung_binh", 3, True,
    ),
    "ConnectionRefusedError": _muc(
        "Python", "nghiem_trong",
        r"ConnectionRefusedError:\s*(.+)",
        "Kết nối bị từ chối.",
        "Server chưa chạy.",
        ["Kiểm tra server.",
         "Kiểm tra port."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#ConnectionRefusedError",
        "trung_binh", 3, True,
    ),
    "ConnectionResetError": _muc(
        "Python", "nghiem_trong",
        r"ConnectionResetError:\s*(.+)",
        "Kết nối bị reset.",
        "Server đóng kết nối.",
        ["Retry."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#ConnectionResetError",
        "nhanh", 3, True,
    ),
    "ConnectionAbortedError": _muc(
        "Python", "nghiem_trong",
        r"ConnectionAbortedError:\s*(.+)",
        "Kết nối bị hủy.",
        "Client hủy giữa chừng.",
        ["Retry."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#ConnectionAbortedError",
        "nhanh", 2, False,
    ),
    "BrokenPipeError": _muc(
        "Python", "nghiem_trong",
        r"BrokenPipeError:\s*(.+)",
        "Ống dẫn bị đứt.",
        "Ghi vào pipe đã đóng.",
        ["Kiểm tra đầu nhận."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#BrokenPipeError",
        "trung_binh", 3, False,
    ),
    "TimeoutError": _muc(
        "Python", "nghiem_trong",
        r"TimeoutError:\s*(.+)",
        "Hết thời gian chờ.",
        "requests.get(timeout=5).",
        ["Tăng timeout."],
        True, "# Sửa:\nrequests.get(url, timeout=30)",
        "https://docs.python.org/3/library/exceptions.html#TimeoutError",
        "nhanh", 3, True,
    ),
    "InterruptedError": _muc(
        "Python", "canh_bao",
        r"InterruptedError:\s*(.+)",
        "Bị ngắt bởi signal.",
        "Ctrl+C khi syscall.",
        ["Thử lại."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#InterruptedError",
        "nhanh", 2, False,
    ),
    "BlockingIOError": _muc(
        "Python", "canh_bao",
        r"BlockingIOError:\s*(.+)",
        "Non-blocking I/O chưa sẵn sàng.",
        "Socket chưa có dữ liệu.",
        ["Chờ và thử lại."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#BlockingIOError",
        "trung_binh", 2, False,
    ),
    "ChildProcessError": _muc(
        "Python", "nghiem_trong",
        r"ChildProcessError:\s*(.+)",
        "Lỗi tiến trình con.",
        "waitpid() thất bại.",
        ["Kiểm tra tiến trình."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#ChildProcessError",
        "trung_binh", 3, False,
    ),
    "ProcessLookupError": _muc(
        "Python", "nghiem_trong",
        r"ProcessLookupError:\s*(.+)",
        "Không tìm thấy tiến trình.",
        "os.kill() PID không tồn tại.",
        ["Kiểm tra PID."],
        False, "",
        "https://docs.python.org/3/library/exceptions.html#ProcessLookupError",
        "nhanh", 2, False,
    ),

    # ============================================================
    # NHÓM 2: JAVASCRIPT / NODE (17 loại)
    # ============================================================
    "JS_ReferenceError": _muc(
        "JavaScript", "nghiem_trong",
        r"ReferenceError:\s*(.+)",
        "Dùng biến chưa khai báo (JS).",
        "console.log(x) khi x chưa khai báo.",
        ["Khai báo: let x = 0;",
         "Kiểm tra phạm vi."],
        True, "// Sửa:\nlet x = 0;\nconsole.log(x);",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ReferenceError",
        "nhanh", 4, True,
    ),
    "JS_TypeError": _muc(
        "JavaScript", "nghiem_trong",
        r"TypeError:\s*(.+)",
        "Sai kiểu dữ liệu (JS).",
        "null.foo",
        ["Kiểm tra null/undefined.",
         "Dùng optional chaining: obj?.foo."],
        True, "// Sửa:\nconsole.log(obj?.foo);",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypeError",
        "nhanh", 4, True,
    ),
    "JS_RangeError": _muc(
        "JavaScript", "nghiem_trong",
        r"RangeError:\s*(.+)",
        "Giá trị ngoài phạm vi.",
        "new Array(-1)",
        ["Kiểm tra giá trị đầu vào."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RangeError",
        "nhanh", 3, True,
    ),
    "JS_SyntaxError": _muc(
        "JavaScript", "nghiem_trong",
        r"SyntaxError:\s*(.+)",
        "Sai cú pháp JS.",
        "Thiếu dấu đóng ngoặc.",
        ["Kiểm tra dấu ngoặc."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SyntaxError",
        "nhanh", 4, True,
    ),
    "JS_URIError": _muc(
        "JavaScript", "nghiem_trong",
        r"URIError:\s*(.+)",
        "Lỗi URI.",
        "decodeURIComponent('%')",
        ["Kiểm tra chuỗi URI."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/URIError",
        "nhanh", 2, False,
    ),
    "JS_EvalError": _muc(
        "JavaScript", "canh_bao",
        r"EvalError:\s*(.+)",
        "Lỗi eval (hiếm).",
        "eval() lỗi.",
        ["Tránh eval()."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/EvalError",
        "trung_binh", 2, False,
    ),
    "JS_UnhandledPromiseRejection": _muc(
        "JavaScript", "nghiem_trong",
        r"UnhandledPromiseRejection(?:Warning)?:\s*(.+)",
        "Promise rejected không catch.",
        "async lỗi không try/catch.",
        ["Thêm .catch().",
         "Bọc try/await catch."],
        True, "// Sửa:\ntry {\n  await ham();\n} catch (e) {\n  console.error(e);\n}",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/catch",
        "nhanh", 4, True,
    ),
    "JS_CannotReadProperty": _muc(
        "JavaScript", "nghiem_trong",
        r"Cannot read propert(?:y|ies) '([^']+)' of (null|undefined)",
        "Đọc thuộc tính của null/undefined.",
        "obj.foo khi obj null.",
        ["Kiểm tra object.",
         "Dùng optional chaining."],
        True, "// Sửa:\nobj?.foo",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining",
        "nhanh", 5, True,
    ),
    "JS_UndefinedIsNotFunction": _muc(
        "JavaScript", "nghiem_trong",
        r"(.+?) is not a function",
        "Gọi hàm nhưng không phải hàm.",
        "x() khi x không phải function.",
        ["Kiểm tra typeof x."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/Not_a_function",
        "nhanh", 4, True,
    ),
    "JS_MaxCallStack": _muc(
        "JavaScript", "nghiem_trong",
        r"Maximum call stack size exceeded",
        "Đệ quy quá sâu (JS).",
        "function f() { f(); }",
        ["Thêm điều kiện dừng."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/Too_much_recursion",
        "trung_binh", 4, True,
    ),
    "JS_ModuleNotFound": _muc(
        "JavaScript", "nghiem_trong",
        r"Cannot find module '([^']+)'",
        "Không tìm thấy module (Node).",
        "require('xyz') chưa cài.",
        ["npm install <tên>."],
        False, "// Sửa:\n// npm install express",
        "https://nodejs.org/api/modules.html",
        "nhanh", 4, True,
    ),
    "JS_EADDRINUSE": _muc(
        "JavaScript", "nghiem_trong",
        r"EADDRINUSE.*?:(\d+)",
        "Port đã bị chiếm.",
        "Server port 3000 đã dùng.",
        ["Đổi port.",
         "Kill process."],
        False, "",
        "https://nodejs.org/api/errors.html#errors_eaddrinuse",
        "nhanh", 3, True,
    ),
    "JS_ENOENT": _muc(
        "JavaScript", "nghiem_trong",
        r"ENOENT:\s*no\s+such\s+file\s+or\s+directory.*?'([^']+)'",
        "Không tìm thấy file (Node).",
        "fs.readFile('abc.txt').",
        ["Kiểm tra đường dẫn.",
         "Tạo file trước."],
        True, "",
        "https://nodejs.org/api/errors.html#errors_enoent",
        "nhanh", 3, True,
    ),
    "JS_ECONNREFUSED": _muc(
        "JavaScript", "nghiem_trong",
        r"ECONNREFUSED.*?:(\d+)",
        "Kết nối bị từ chối.",
        "Server chưa chạy.",
        ["Kiểm tra server."],
        False, "",
        "https://nodejs.org/api/errors.html#errors_econnrefused",
        "nhanh", 3, True,
    ),
    "JS_ETIMEDOUT": _muc(
        "JavaScript", "nghiem_trong",
        r"ETIMEDOUT",
        "Kết nối hết thời gian.",
        "Server không phản hồi.",
        ["Tăng timeout."],
        False, "",
        "https://nodejs.org/api/errors.html#errors_etimedout",
        "nhanh", 3, True,
    ),
    "JS_ERR_INVALID_ARG_TYPE": _muc(
        "JavaScript", "nghiem_trong",
        r"ERR_INVALID_ARG_TYPE",
        "Sai kiểu đối số (Node).",
        "Truyền string khi cần Buffer.",
        ["Kiểm tra kiểu."],
        False, "",
        "https://nodejs.org/api/errors.html",
        "nhanh", 3, False,
    ),
    "JS_ERR_REQUIRE_ESM": _muc(
        "JavaScript", "nghiem_trong",
        r"ERR_REQUIRE_ESM",
        "Module ESM không require() được.",
        "require() module ESM.",
        ["Dùng import.",
         "Chuyển CommonJS."],
        False, "",
        "https://nodejs.org/api/errors.html",
        "trung_binh", 3, False,
    ),

    # ============================================================
    # NHÓM 3: JAVA (13 loại)
    # ============================================================
    "Java_NullPointerException": _muc(
        "Java", "nghiem_trong",
        r"NullPointerException",
        "Dùng biến null (Java).",
        "str.length() khi str = null.",
        ["Kiểm tra null.",
         "Dùng Optional."],
        True, "// Sửa:\nif (str != null) {\n    int n = str.length();\n}",
        "https://docs.oracle.com/javase/8/docs/api/java/lang/NullPointerException.html",
        "nhanh", 5, True,
    ),
    "Java_ArrayIndexOutOfBounds": _muc(
        "Java", "nghiem_trong",
        r"ArrayIndexOutOfBoundsException",
        "Index ngoài phạm vi mảng.",
        "arr[10] khi arr.length = 5.",
        ["Kiểm tra index."],
        True, "",
        "https://docs.oracle.com/javase/8/docs/api/java/lang/ArrayIndexOutOfBoundsException.html",
        "nhanh", 4, True,
    ),
    "Java_ClassNotFound": _muc(
        "Java", "nghiem_trong",
        r"ClassNotFoundException",
        "Không tìm thấy class.",
        "Class.forName('abc.xyz')",
        ["Kiểm tra classpath."],
        False, "",
        "https://docs.oracle.com/javase/8/docs/api/java/lang/ClassNotFoundException.html",
        "trung_binh", 3, False,
    ),
    "Java_NumberFormat": _muc(
        "Java", "nghiem_trong",
        r"NumberFormatException",
        "Không parse được số.",
        "Integer.parseInt('abc')",
        ["Kiểm tra chuỗi."],
        True, "",
        "https://docs.oracle.com/javase/8/docs/api/java/lang/NumberFormatException.html",
        "nhanh", 3, True,
    ),
    "Java_Arithmetic": _muc(
        "Java", "nghiem_trong",
        r"ArithmeticException",
        "Lỗi số học (chia 0).",
        "10 / 0",
        ["Kiểm tra mẫu số."],
        True, "",
        "https://docs.oracle.com/javase/8/docs/api/java/lang/ArithmeticException.html",
        "nhanh", 4, True,
    ),
    "Java_FileNotFound": _muc(
        "Java", "nghiem_trong",
        r"FileNotFoundException",
        "Không tìm thấy file (Java).",
        "new FileReader('abc.txt')",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://docs.oracle.com/javase/8/docs/api/java/io/FileNotFoundException.html",
        "nhanh", 3, True,
    ),
    "Java_IOException": _muc(
        "Java", "nghiem_trong",
        r"IOException",
        "Lỗi vào/ra Java.",
        "Đọc file lỗi.",
        ["Bọc try/catch."],
        False, "",
        "https://docs.oracle.com/javase/8/docs/api/java/io/IOException.html",
        "trung_binh", 3, True,
    ),
    "Java_StackOverflow": _muc(
        "Java", "nghiem_trong",
        r"StackOverflowError",
        "Đệ quy quá sâu (Java).",
        "Đệ quy vô hạn.",
        ["Thêm điều kiện dừng."],
        True, "",
        "https://docs.oracle.com/javase/8/docs/api/java/lang/StackOverflowError.html",
        "trung_binh", 4, True,
    ),
    "Java_OutOfMemory": _muc(
        "Java", "nghiem_trong",
        r"OutOfMemoryError",
        "Hết bộ nhớ Java.",
        "Mảng quá lớn.",
        ["Tăng -Xmx.",
         "Giảm dữ liệu."],
        False, "",
        "https://docs.oracle.com/javase/8/docs/api/java/lang/OutOfMemoryError.html",
        "lau", 5, False,
    ),
    "Java_ClassCast": _muc(
        "Java", "nghiem_trong",
        r"ClassCastException",
        "Ép kiểu sai.",
        "(String) obj khi obj là Integer.",
        ["Kiểm tra instanceof."],
        False, "",
        "https://docs.oracle.com/javase/8/docs/api/java/lang/ClassCastException.html",
        "nhanh", 3, True,
    ),
    "Java_IllegalArgument": _muc(
        "Java", "nghiem_trong",
        r"IllegalArgumentException",
        "Đối số không hợp lệ.",
        "Thread.sleep(-1)",
        ["Kiểm tra đối số."],
        False, "",
        "https://docs.oracle.com/javase/8/docs/api/java/lang/IllegalArgumentException.html",
        "nhanh", 3, True,
    ),
    "Java_IllegalState": _muc(
        "Java", "nghiem_trong",
        r"IllegalStateException",
        "Trạng thái không hợp lệ.",
        "next() khi chưa hasNext().",
        ["Kiểm tra trạng thái."],
        False, "",
        "https://docs.oracle.com/javase/8/docs/api/java/lang/IllegalStateException.html",
        "nhanh", 3, True,
    ),
    "Java_ConcurrentModification": _muc(
        "Java", "nghiem_trong",
        r"ConcurrentModificationException",
        "Sửa collection khi đang duyệt.",
        "for (X x : list) list.remove(x);",
        ["Dùng Iterator.remove().",
         "Copy list."],
        True, "",
        "https://docs.oracle.com/javase/8/docs/api/java/util/ConcurrentModificationException.html",
        "trung_binh", 4, True,
    ),

    # ============================================================
    # NHÓM 4: C / C++ (7 loại)
    # ============================================================
    "Cpp_SegmentationFault": _muc(
        "C/C++", "nghiem_trong",
        r"[Ss]egmentation\s+fault|SIGSEGV",
        "Truy cập bộ nhớ không hợp lệ.",
        "int *p = NULL; *p = 5;",
        ["Kiểm tra con trỏ NULL.",
         "Kiểm tra index mảng.",
         "Dùng valgrind."],
        False, "",
        "https://en.wikipedia.org/wiki/Segmentation_fault",
        "lau", 5, True,
    ),
    "Cpp_BusError": _muc(
        "C/C++", "nghiem_trong",
        r"[Bb]us\s+error|SIGBUS",
        "Lỗi bus.",
        "Truy cập mảng sai kiểu.",
        ["Kiểm tra alignment."],
        False, "",
        "https://en.wikipedia.org/wiki/Bus_error",
        "lau", 5, False,
    ),
    "Cpp_DoubleFree": _muc(
        "C/C++", "nghiem_trong",
        r"double free|free\(\): invalid pointer",
        "Giải phóng bộ nhớ 2 lần.",
        "free(p); free(p);",
        ["Gán p = NULL sau free."],
        True, "// Sửa:\nfree(p);\np = NULL;",
        "https://owasp.org/www-community/vulnerabilities/Doubly_freeing_memory",
        "trung_binh", 5, True,
    ),
    "Cpp_MemoryLeak": _muc(
        "C/C++", "canh_bao",
        r"memory leak",
        "Rò rỉ bộ nhớ.",
        "malloc không free.",
        ["Free sau khi dùng.",
         "Dùng valgrind."],
        False, "",
        "https://en.wikipedia.org/wiki/Memory_leak",
        "lau", 4, True,
    ),
    "Cpp_StackOverflow": _muc(
        "C/C++", "nghiem_trong",
        r"stack overflow",
        "Tràn stack.",
        "Đệ quy vô hạn.",
        ["Thêm điều kiện dừng."],
        True, "",
        "https://en.wikipedia.org/wiki/Stack_overflow",
        "trung_binh", 4, True,
    ),
    "Cpp_NullPointer": _muc(
        "C/C++", "nghiem_trong",
        r"null pointer dereference",
        "Truy cập con trỏ NULL.",
        "*p khi p = NULL.",
        ["Kiểm tra p != NULL."],
        True, "",
        "https://en.wikipedia.org/wiki/Dereference_operator",
        "nhanh", 5, True,
    ),
    "Cpp_BufferOverflow": _muc(
        "C/C++", "nghiem_trong",
        r"buffer overflow",
        "Tràn buffer.",
        "strcpy(buf, s) khi s dài.",
        ["Dùng strncpy.",
         "Kiểm tra kích thước."],
        True, "",
        "https://owasp.org/www-community/vulnerabilities/Buffer_Overflow",
        "trung_binh", 5, True,
    ),

    # ============================================================
    # NHÓM 5: WEB / HTTP (18 mã lỗi)
    # ============================================================
    "HTTP_400": _muc(
        "Web", "nghiem_trong",
        r"\b400\b.*?(?:Bad Request)?",
        "Bad Request.",
        "Gửi JSON sai format.",
        ["Kiểm tra body.",
         "Kiểm tra Content-Type."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400",
        "nhanh", 3, True,
    ),
    "HTTP_401": _muc(
        "Web", "nghiem_trong",
        r"\b401\b.*?(?:Unauthorized)?",
        "Unauthorized.",
        "Gọi API không token.",
        ["Đăng nhập.",
         "Thêm Authorization."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401",
        "nhanh", 4, True,
    ),
    "HTTP_402": _muc(
        "Web", "nghiem_trong",
        r"\b402\b.*?(?:Payment Required)?",
        "Payment Required.",
        "API yêu cầu trả phí.",
        ["Nạp tiền / dùng free tier."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/402",
        "nhanh", 3, False,
    ),
    "HTTP_403": _muc(
        "Web", "nghiem_trong",
        r"\b403\b.*?(?:Forbidden)?",
        "Forbidden.",
        "Truy cập bị cấm.",
        ["Kiểm tra quyền."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403",
        "nhanh", 3, True,
    ),
    "HTTP_404": _muc(
        "Web", "nghiem_trong",
        r"\b404\b.*?(?:Not Found)?",
        "Not Found.",
        "URL sai.",
        ["Kiểm tra URL.",
         "Kiểm tra route."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404",
        "nhanh", 5, True,
    ),
    "HTTP_405": _muc(
        "Web", "nghiem_trong",
        r"\b405\b.*?(?:Method Not Allowed)?",
        "Method Not Allowed.",
        "POST vào route GET.",
        ["Kiểm tra method."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/405",
        "nhanh", 3, True,
    ),
    "HTTP_408": _muc(
        "Web", "nghiem_trong",
        r"\b408\b.*?(?:Request Timeout)?",
        "Request Timeout.",
        "Client gửi chậm.",
        ["Gửi lại."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408",
        "nhanh", 2, False,
    ),
    "HTTP_409": _muc(
        "Web", "nghiem_trong",
        r"\b409\b.*?(?:Conflict)?",
        "Conflict.",
        "Trùng key unique.",
        ["Kiểm tra dữ liệu trùng."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409",
        "nhanh", 3, False,
    ),
    "HTTP_429": _muc(
        "Web", "nghiem_trong",
        r"\b429\b.*?(?:Too Many Requests|Rate Limit)?",
        "Too Many Requests.",
        "Gọi API quá nhiều.",
        ["Chờ.", "Xoay key."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429",
        "nhanh", 4, True,
    ),
    "HTTP_500": _muc(
        "Web", "nghiem_trong",
        r"\b500\b.*?(?:Internal Server Error)?",
        "Internal Server Error.",
        "Server crash.",
        ["Xem log.", "Kiểm tra code."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500",
        "trung_binh", 4, True,
    ),
    "HTTP_502": _muc(
        "Web", "nghiem_trong",
        r"\b502\b.*?(?:Bad Gateway)?",
        "Bad Gateway.",
        "Reverse proxy lỗi.",
        ["Kiểm tra backend."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502",
        "trung_binh", 3, False,
    ),
    "HTTP_503": _muc(
        "Web", "nghiem_trong",
        r"\b503\b.*?(?:Service Unavailable)?",
        "Service Unavailable.",
        "Server quá tải.",
        ["Chờ.", "Kiểm tra tài nguyên."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503",
        "trung_binh", 3, True,
    ),
    "HTTP_504": _muc(
        "Web", "nghiem_trong",
        r"\b504\b.*?(?:Gateway Timeout)?",
        "Gateway Timeout.",
        "Backend chậm.",
        ["Tăng timeout.", "Tối ưu backend."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504",
        "trung_binh", 3, True,
    ),
    "Web_CORS": _muc(
        "Web", "nghiem_trong",
        r"CORS\s+(?:policy|error)",
        "Lỗi CORS.",
        "Gọi API khác domain.",
        ["Bật CORS server.",
         "Thêm Access-Control-Allow-Origin."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS",
        "trung_binh", 4, True,
    ),
    "Web_ERR_CONNECTION_REFUSED": _muc(
        "Web", "nghiem_trong",
        r"ERR_CONNECTION_REFUSED",
        "Kết nối bị từ chối.",
        "Server chưa chạy.",
        ["Kiểm tra server."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        "nhanh", 3, True,
    ),
    "Web_ERR_NAME_NOT_RESOLVED": _muc(
        "Web", "nghiem_trong",
        r"ERR_NAME_NOT_RESOLVED",
        "Không phân giải tên miền.",
        "DNS lỗi.",
        ["Kiểm tra domain.", "Kiểm tra DNS."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        "trung_binh", 3, False,
    ),
    "Web_ERR_SSL": _muc(
        "Web", "nghiem_trong",
        r"ERR_SSL_PROTOCOL_ERROR|SSL: CERTIFICATE_VERIFY_FAILED",
        "Lỗi SSL/TLS.",
        "Cert hết hạn.",
        ["Kiểm tra cert.", "Cập nhật CA."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/Security",
        "trung_binh", 4, True,
    ),
    "Web_ERR_TIMED_OUT": _muc(
        "Web", "nghiem_trong",
        r"ERR_TIMED_OUT",
        "Hết thời gian kết nối.",
        "Server chậm.",
        ["Tăng timeout.", "Kiểm tra mạng."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        "nhanh", 3, True,
    ),

    # ============================================================
    # NHÓM 6: DATABASE (9 loại)
    # ============================================================
    "DB_DuplicateKey": _muc(
        "Database", "nghiem_trong",
        r"duplicate key|E11000",
        "Trùng key unique.",
        "Insert _id đã tồn tại.",
        ["Kiểm tra key.", "Dùng upsert."],
        True, "",
        "https://www.mongodb.com/docs/manual/core/index-unique/",
        "nhanh", 3, True,
    ),
    "DB_ConnectionRefused": _muc(
        "Database", "nghiem_trong",
        r"Connection refused|could not connect to server",
        "Kết nối DB bị từ chối.",
        "DB chưa chạy.",
        ["Kiểm tra DB.", "Kiểm tra port."],
        False, "",
        "https://www.postgresql.org/docs/current/",
        "trung_binh", 4, True,
    ),
    "DB_AuthFailed": _muc(
        "Database", "nghiem_trong",
        r"Authentication failed|Access denied for user",
        "Xác thực DB thất bại.",
        "Sai user/password.",
        ["Kiểm tra credential."],
        False, "",
        "https://www.mongodb.com/docs/manual/core/authentication/",
        "nhanh", 4, True,
    ),
    "DB_Timeout": _muc(
        "Database", "nghiem_trong",
        r"connection timed out|Operation timed out",
        "DB timeout.",
        "Query lâu.",
        ["Tối ưu query.", "Thêm index."],
        False, "",
        "https://www.mongodb.com/docs/manual/core/indexes/",
        "trung_binh", 3, True,
    ),
    "DB_Deadlock": _muc(
        "Database", "nghiem_trong",
        r"Deadlock found",
        "Deadlock DB.",
        "2 transaction chờ nhau.",
        ["Sắp xếp lock.", "Giảm transaction time."],
        False, "",
        "https://dev.mysql.com/doc/refman/8.0/en/innodb-deadlocks.html",
        "lau", 4, False,
    ),
    "DB_ConstraintViolation": _muc(
        "Database", "nghiem_trong",
        r"constraint violation|foreign key constraint",
        "Vi phạm ràng buộc.",
        "Xóa record có FK.",
        ["Xóa con trước cha."],
        False, "",
        "https://www.postgresql.org/docs/current/ddl-constraints.html",
        "trung_binh", 3, True,
    ),
    "DB_TooManyConnections": _muc(
        "Database", "nghiem_trong",
        r"too many connections",
        "Quá nhiều kết nối DB.",
        "Không đóng connection.",
        ["Dùng pool.", "Đóng sau khi dùng."],
        True, "",
        "https://www.postgresql.org/docs/current/runtime-config-connection.html",
        "trung_binh", 4, True,
    ),
    "DB_SSL_Error": _muc(
        "Database", "nghiem_trong",
        r"SSL.*?error.*?database|mongodb.*?ssl",
        "Lỗi SSL khi kết nối DB.",
        "Cert sai.",
        ["Kiểm tra URI SSL."],
        False, "",
        "https://www.mongodb.com/docs/manual/reference/connection-string/",
        "trung_binh", 3, False,
    ),
    "DB_Atlas_IPWhitelist": _muc(
        "Database", "nghiem_trong",
        r"not whitelisted|IP.*?not.*?allowed",
        "IP chưa được whitelist.",
        "Atlas chặn IP.",
        ["Atlas → Network Access → thêm IP."],
        True, "",
        "https://www.mongodb.com/docs/atlas/security-whitelist/",
        "nhanh", 4, True,
    ),

    # ============================================================
    # NHÓM 7: FRAMEWORK (14 loại)
    # ============================================================
    "React_HooksError": _muc(
        "React", "nghiem_trong",
        r"Rendered more hooks than during the previous render",
        "Gọi hook sai thứ tự.",
        "Hook trong if/loop.",
        ["Chỉ gọi hook top-level."],
        True, "",
        "https://react.dev/reference/rules/rules-of-hooks",
        "trung_binh", 4, True,
    ),
    "React_CannotUpdateWhileRendering": _muc(
        "React", "nghiem_trong",
        r"Cannot update a component while rendering",
        "Update state khi render.",
        "setState trong render.",
        ["Dùng useEffect."],
        True, "",
        "https://react.dev/reference/react/useEffect",
        "trung_binh", 3, True,
    ),
    "React_MissingKey": _muc(
        "React", "canh_bao",
        r"Each child in a list should have a unique \"key\"",
        "Thiếu key trong list.",
        "Map không key.",
        ["Thêm key unique."],
        True, "// Sửa:\nitems.map(i => <li key={i.id}>{i.ten}</li>)",
        "https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key",
        "nhanh", 2, True,
    ),
    "Vue_PropertyNotDefined": _muc(
        "Vue", "nghiem_trong",
        r"Property or method \"([^\"]+)\" is not defined",
        "Thuộc tính không tồn tại.",
        "Dùng {{ xyz }} không khai báo.",
        ["Khai báo trong data/computed."],
        True, "",
        "https://vuejs.org/api/options-state.html",
        "nhanh", 3, True,
    ),
    "Vue_FailedMount": _muc(
        "Vue", "nghiem_trong",
        r"Failed to mount component",
        "Không mount được component.",
        "Template lỗi.",
        ["Kiểm tra template."],
        False, "",
        "https://vuejs.org/guide/essentials/component-basics.html",
        "trung_binh", 3, False,
    ),
    "Django_TemplateDoesNotExist": _muc(
        "Django", "nghiem_trong",
        r"TemplateDoesNotExist.*?'([^']+)'",
        "Không tìm thấy template.",
        "render('abc.html') không có file.",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://docs.djangoproject.com/en/stable/topics/templates/",
        "nhanh", 3, True,
    ),
    "Django_NoReverseMatch": _muc(
        "Django", "nghiem_trong",
        r"NoReverseMatch",
        "Không tìm thấy URL name.",
        "{% url 'abc' %} không có route.",
        ["Kiểm tra name."],
        False, "",
        "https://docs.djangoproject.com/en/stable/topics/http/urls/",
        "nhanh", 3, True,
    ),
    "Django_DoesNotExist": _muc(
        "Django", "nghiem_trong",
        r"DoesNotExist",
        "Object không tồn tại.",
        "Model.objects.get(id=999).",
        ["Dùng get_object_or_404."],
        True, "",
        "https://docs.djangoproject.com/en/stable/topics/http/shortcuts/",
        "nhanh", 3, True,
    ),
    "Flask_OutsideRequestContext": _muc(
        "Flask", "nghiem_trong",
        r"Working outside of request context",
        "Dùng request/session ngoài request.",
        "request.json trong background job.",
        ["Bọc app.app_context()."],
        True, "",
        "https://flask.palletsprojects.com/en/stable/appcontext/",
        "trung_binh", 3, True,
    ),
    "Flask_MethodNotAllowed": _muc(
        "Flask", "nghiem_trong",
        r"Method Not Allowed",
        "Sai HTTP method.",
        "GET route nhưng POST request.",
        ["Thêm methods=['POST']."],
        True, "",
        "https://flask.palletsprojects.com/en/stable/quickstart/#http-methods",
        "nhanh", 3, True,
    ),
    "Node_MODULE_NOT_FOUND": _muc(
        "Node", "nghiem_trong",
        r"MODULE_NOT_FOUND",
        "Không tìm thấy module.",
        "require('xyz') chưa cài.",
        ["npm install <tên>."],
        True, "",
        "https://nodejs.org/api/modules.html",
        "nhanh", 4, True,
    ),
    "Node_EADDRINUSE": _muc(
        "Node", "nghiem_trong",
        r"EADDRINUSE.*?:(\d+)",
        "Port đã dùng.",
        "Server chạy port đã chiếm.",
        ["Đổi port."],
        False, "",
        "https://nodejs.org/api/errors.html#errors_eaddrinuse",
        "nhanh", 3, True,
    ),
    "Node_ENOENT": _muc(
        "Node", "nghiem_trong",
        r"ENOENT:\s*no\s+such\s+file\s+or\s+directory",
        "File không tồn tại.",
        "fs.readFile('abc').",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://nodejs.org/api/errors.html#errors_enoent",
        "nhanh", 3, True,
    ),
    "Node_UnhandledRejection": _muc(
        "Node", "nghiem_trong",
        r"UnhandledPromiseRejection",
        "Promise rejected không catch.",
        "async lỗi.",
        ["process.on(...)", "Bọc try/catch."],
        True, "",
        "https://nodejs.org/api/process.html#event-unhandledrejection",
        "nhanh", 3, True,
    ),

    # ============================================================
    # NHÓM 8: API / NETWORK (10 loại)
    # ============================================================
    "API_Timeout": _muc(
        "API", "nghiem_trong",
        r"(?:request|api).*?(?:timeout|timed out)",
        "API timeout.",
        "Server chậm.",
        ["Tăng timeout.", "Retry."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/API/AbortController",
        "nhanh", 3, True,
    ),
    "API_RateLimit": _muc(
        "API", "nghiem_trong",
        r"rate.?limit|too many requests",
        "Vượt rate limit.",
        "Gọi API quá nhiều.",
        ["Chờ.", "Xoay key."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429",
        "nhanh", 4, True,
    ),
    "API_QuotaExceeded": _muc(
        "API", "nghiem_trong",
        r"quota exceeded|insufficient quota",
        "Hết quota API.",
        "Dùng hết quota tháng.",
        ["Chờ reset.", "Xoay key."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429",
        "nhanh", 4, True,
    ),
    "API_Unauthorized": _muc(
        "API", "nghiem_trong",
        r"unauthorized|invalid api key|authentication failed",
        "API key sai.",
        "Key sai.",
        ["Kiểm tra key.", "Đổi key."],
        True, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401",
        "nhanh", 4, True,
    ),
    "API_Forbidden": _muc(
        "API", "nghiem_trong",
        r"forbidden|access denied",
        "Không có quyền.",
        "Tài khoản bị cấm.",
        ["Kiểm tra quyền."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403",
        "nhanh", 3, True,
    ),
    "API_BadRequest": _muc(
        "API", "nghiem_trong",
        r"bad request|invalid request",
        "Request sai.",
        "Thiếu tham số.",
        ["Kiểm tra body."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400",
        "nhanh", 3, True,
    ),
    "API_ServerError": _muc(
        "API", "nghiem_trong",
        r"internal server error|server error",
        "Server API lỗi.",
        "Provider lỗi.",
        ["Retry.", "Báo provider."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500",
        "trung_binh", 3, True,
    ),
    "API_DNS_Error": _muc(
        "API", "nghiem_trong",
        r"DNS.*?(?:error|failed)|getaddrinfo failed|name or service not known",
        "DNS không phân giải.",
        "Domain sai.",
        ["Kiểm tra domain."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        "trung_binh", 3, False,
    ),
    "API_SSL_Error": _muc(
        "API", "nghiem_trong",
        r"SSL.*?error|certificate verify failed",
        "Lỗi SSL.",
        "Cert sai.",
        ["Cập nhật CA."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/Security",
        "trung_binh", 3, True,
    ),
    "API_SocketHangUp": _muc(
        "API", "nghiem_trong",
        r"socket hang up|connection reset",
        "Kết nối bị đóng.",
        "Server đóng.",
        ["Retry."],
        False, "",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        "nhanh", 2, True,
    ),

    # ============================================================
    # NHÓM 9: DOCKER / DEPLOY (5 loại)
    # ============================================================
    "Docker_ImagePull": _muc(
        "Docker", "nghiem_trong",
        r"ImagePullBackOff|failed to pull image",
        "Không pull được image.",
        "Image sai.",
        ["Kiểm tra tên image."],
        False, "",
        "https://kubernetes.io/docs/concepts/containers/images/",
        "trung_binh", 3, True,
    ),
    "Docker_CrashLoop": _muc(
        "Docker", "nghiem_trong",
        r"CrashLoopBackOff",
        "Container restart liên tục.",
        "App crash.",
        ["Xem log.", "Kiểm tra entrypoint."],
        False, "",
        "https://kubernetes.io/docs/tasks/debug/debug-application/",
        "trung_binh", 4, True,
    ),
    "Docker_OOMKilled": _muc(
        "Docker", "nghiem_trong",
        r"OOMKilled|out of memory",
        "Container bị kill vì hết RAM.",
        "Dùng nhiều RAM.",
        ["Tăng RAM.", "Tối ưu."],
        False, "",
        "https://kubernetes.io/docs/tasks/configure-pod-container/",
        "lau", 5, True,
    ),
    "Docker_PortInUse": _muc(
        "Docker", "nghiem_trong",
        r"port is already allocated",
        "Port đã chiếm.",
        "Container khác dùng.",
        ["Đổi port."],
        False, "",
        "https://docs.docker.com/engine/reference/commandline/run/",
        "nhanh", 3, True,
    ),
    "Deploy_BuildFailed": _muc(
        "Deploy", "nghiem_trong",
        r"build failed|Build failed",
        "Build thất bại.",
        "Cài thư viện lỗi.",
        ["Xem log.", "Kiểm tra yeu_cau.txt."],
        False, "",
        "https://render.com/docs",
        "trung_binh", 3, True,
    ),

    # ============================================================
    # NHÓM 10: OS / FILE (8 loại)
    # ============================================================
    "OS_PermissionDenied": _muc(
        "OS", "nghiem_trong",
        r"[Pp]ermission\s+denied",
        "Không có quyền.",
        "Đọc/ghi file.",
        ["Chmod.", "Sudo."],
        False, "",
        "https://man7.org/linux/man-pages/man1/chmod.1.html",
        "trung_binh", 3, True,
    ),
    "OS_NoSuchFile": _muc(
        "OS", "nghiem_trong",
        r"[Nn]o\s+such\s+file\s+or\s+directory",
        "File không tồn tại.",
        "Đường dẫn sai.",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://man7.org/linux/man-pages/man2/open.2.html",
        "nhanh", 3, True,
    ),
    "OS_DiskFull": _muc(
        "OS", "nghiem_trong",
        r"[Nn]o\s+space\s+left\s+on\s+device|disk full",
        "Hết dung lượng.",
        "Ổ đĩa đầy.",
        ["Xóa file.", "Tăng dung lượng."],
        False, "",
        "https://man7.org/linux/man-pages/man1/df.1.html",
        "trung_binh", 4, True,
    ),
    "OS_IsADirectory": _muc(
        "OS", "nghiem_trong",
        r"[Ii]s\s+a\s+directory",
        "Là thư mục.",
        "Mở thư mục như file.",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://man7.org/linux/man-pages/man2/open.2.html",
        "nhanh", 2, False,
    ),
    "OS_NotADirectory": _muc(
        "OS", "nghiem_trong",
        r"[Nn]ot\s+a\s+directory",
        "Không phải thư mục.",
        "Truy cập file như thư mục.",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://man7.org/linux/man-pages/man2/open.2.html",
        "nhanh", 2, False,
    ),
    "OS_ReadOnly": _muc(
        "OS", "nghiem_trong",
        r"[Rr]ead-only\s+file\s+system",
        "Hệ thống file chỉ đọc.",
        "Ghi vào ổ read-only.",
        ["Remount rw.", "Đổi đường dẫn."],
        False, "",
        "https://man7.org/linux/man-pages/man8/mount.8.html",
        "trung_binh", 3, False,
    ),
    "OS_TooManyFiles": _muc(
        "OS", "nghiem_trong",
        r"[Tt]oo\s+many\s+open\s+files",
        "Quá nhiều file đang mở.",
        "Không đóng file.",
        ["Đóng file.", "Tăng ulimit."],
        True, "",
        "https://man7.org/linux/man-pages/man2/getrlimit.2.html",
        "trung_binh", 3, False,
    ),
    "OS_Killed": _muc(
        "OS", "nghiem_trong",
        r"[Kk]illed",
        "Tiến trình bị kill.",
        "OOM killer.",
        ["Giảm RAM.", "Tăng RAM."],
        False, "",
        "https://www.kernel.org/doc/gorman/html/understand/understand016.html",
        "trung_binh", 4, True,
    ),
}


# ============================================================
# NHÓM 11: RUBY / RAILS (10 loại)
# ============================================================
LOAI_LOI.update({
    "Ruby_NoMethodError": _muc(
        "Ruby", "nghiem_trong",
        r"NoMethodError\s*\(?.*?undefined method ['`]([^']+)",
        "Gọi method không tồn tại (Ruby).",
        "obj.abc khi obj không có method abc.",
        ["Kiểm tra tên method.",
         "Kiểm tra object type."],
        True, "# Sửa:\n# Kiểm tra obj.respond_to?(:abc)",
        "https://ruby-doc.org/core-3.0.0/NoMethodError.html",
        "nhanh", 4, True,
    ),
    "Ruby_NameError": _muc(
        "Ruby", "nghiem_trong",
        r"NameError.*?undefined local variable or method ['`]([^']+)",
        "Dùng biến/method chưa khai báo (Ruby).",
        "puts x khi x chưa gán.",
        ["Khai báo biến trước."],
        True, "",
        "https://ruby-doc.org/core-3.0.0/NameError.html",
        "nhanh", 4, True,
    ),
    "Ruby_LoadError": _muc(
        "Ruby", "nghiem_trong",
        r"LoadError:\s*cannot load such file\s*--\s*(.+)",
        "Không load được file/gem.",
        "require 'xyz' chưa cài.",
        ["gem install <tên>.", "Kiểm tra Gemfile."],
        False, "",
        "https://ruby-doc.org/core-3.0.0/LoadError.html",
        "nhanh", 3, True,
    ),
    "Ruby_ArgumentError": _muc(
        "Ruby", "nghiem_trong",
        r"ArgumentError:\s*(.+)",
        "Đối số sai (Ruby).",
        "wrong number of arguments.",
        ["Kiểm tra số tham số."],
        False, "",
        "https://ruby-doc.org/core-3.0.0/ArgumentError.html",
        "nhanh", 3, True,
    ),
    "Ruby_TypeError": _muc(
        "Ruby", "nghiem_trong",
        r"TypeError:\s*(.+)",
        "Sai kiểu dữ liệu (Ruby).",
        "1 + 'abc'",
        ["Ép kiểu."],
        True, "",
        "https://ruby-doc.org/core-3.0.0/TypeError.html",
        "nhanh", 3, True,
    ),
    "Ruby_ZeroDivisionError": _muc(
        "Ruby", "nghiem_trong",
        r"ZeroDivisionError",
        "Chia cho 0 (Ruby).",
        "1 / 0",
        ["Kiểm tra mẫu số."],
        True, "",
        "https://ruby-doc.org/core-3.0.0/ZeroDivisionError.html",
        "nhanh", 3, True,
    ),
    "Ruby_ENOENT": _muc(
        "Ruby", "nghiem_trong",
        r"Errno::ENOENT",
        "File không tồn tại (Ruby).",
        "File.read('abc.txt')",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://ruby-doc.org/core-3.0.0/Errno.html",
        "nhanh", 3, True,
    ),
    "Rails_RecordNotFound": _muc(
        "Rails", "nghiem_trong",
        r"ActiveRecord::RecordNotFound",
        "Record không tồn tại (Rails).",
        "User.find(999)",
        ["Dùng find_by.", "Bọc rescue."],
        True, "# Sửa:\nUser.find_by(id: 999) || raise",
        "https://api.rubyonrails.org/classes/ActiveRecord/RecordNotFound.html",
        "nhanh", 3, True,
    ),
    "Rails_RecordInvalid": _muc(
        "Rails", "nghiem_trong",
        r"ActiveRecord::RecordInvalid",
        "Validation thất bại (Rails).",
        "Save record không hợp lệ.",
        ["Kiểm tra validation.", "Dùng save!."],
        False, "",
        "https://api.rubyonrails.org/classes/ActiveRecord/RecordInvalid.html",
        "nhanh", 3, True,
    ),
    "Rails_UnknownAttribute": _muc(
        "Rails", "nghiem_trong",
        r"ActiveModel::UnknownAttributeError",
        "Thuộc tính không tồn tại (Rails).",
        "Model.new(xyz: 1) khi không có cột.",
        ["Kiểm tra schema."],
        False, "",
        "https://api.rubyonrails.org/classes/ActiveModel/UnknownAttributeError.html",
        "nhanh", 3, False,
    ),

    # ============================================================
    # NHÓM 12: PHP (10 loại)
    # ============================================================
    "PHP_FatalError": _muc(
        "PHP", "nghiem_trong",
        r"PHP Fatal error:\s*(.+)",
        "Lỗi nghiêm trọng PHP.",
        "Gọi hàm không tồn tại.",
        ["Kiểm tra hàm.", "Kiểm tra include."],
        False, "",
        "https://www.php.net/manual/en/errorfunc.constants.php",
        "trung_binh", 4, True,
    ),
    "PHP_ParseError": _muc(
        "PHP", "nghiem_trong",
        r"PHP Parse error:\s*(.+)",
        "Sai cú pháp PHP.",
        "Thiếu dấu ; hoặc }",
        ["Kiểm tra dấu ;, {}."],
        True, "",
        "https://www.php.net/manual/en/errorfunc.constants.php",
        "nhanh", 4, True,
    ),
    "PHP_UndefinedVariable": _muc(
        "PHP", "canh_bao",
        r"Undefined variable:\s*\$?(\w+)",
        "Biến chưa khai báo PHP.",
        "$x dùng khi chưa gán.",
        ["Khởi tạo biến."],
        True, "<?php\n// Sửa:\n$x = 0;\necho $x;",
        "https://www.php.net/manual/en/language.variables.basics.php",
        "nhanh", 3, True,
    ),
    "PHP_UndefinedIndex": _muc(
        "PHP", "canh_bao",
        r"Undefined index:\s*(\w+)",
        "Index chưa tồn tại trong array.",
        "$arr['abc'] không có key.",
        ["Dùng isset() hoặc array_key_exists()."],
        True, "<?php\n// Sửa:\n$val = $arr['abc'] ?? null;",
        "https://www.php.net/manual/en/language.types.array.php",
        "nhanh", 3, True,
    ),
    "PHP_UndefinedFunction": _muc(
        "PHP", "nghiem_trong",
        r"Call to undefined function\s+(\w+)",
        "Gọi hàm chưa định nghĩa.",
        "abc() khi chưa khai báo.",
        ["Kiểm tra tên hàm.", "Kiểm tra include."],
        False, "",
        "https://www.php.net/manual/en/functions.user-defined.php",
        "nhanh", 3, True,
    ),
    "PHP_MemoryExhausted": _muc(
        "PHP", "nghiem_trong",
        r"Allowed memory size of \d+ bytes exhausted",
        "Hết bộ nhớ PHP.",
        "Xử lý dữ liệu lớn.",
        ["Tăng memory_limit.", "Tối ưu code."],
        False, "",
        "https://www.php.net/manual/en/ini.core.php#ini.memory-limit",
        "trung_binh", 4, True,
    ),
    "PHP_Timeout": _muc(
        "PHP", "nghiem_trong",
        r"Maximum execution time of \d+ seconds exceeded",
        "Vượt thời gian thực thi.",
        "Script chạy quá lâu.",
        ["Tăng max_execution_time.", "Tối ưu."],
        False, "",
        "https://www.php.net/manual/en/info.configuration.php#ini.max-execution-time",
        "trung_binh", 3, True,
    ),
    "PHP_Notice": _muc(
        "PHP", "thong_tin",
        r"PHP Notice:\s*(.+)",
        "Thông báo PHP (nhẹ).",
        "Dùng biến chưa khởi tạo.",
        ["Khởi tạo biến."],
        True, "",
        "https://www.php.net/manual/en/errorfunc.constants.php",
        "nhanh", 2, True,
    ),
    "PHP_Warning": _muc(
        "PHP", "canh_bao",
        r"PHP Warning:\s*(.+)",
        "Cảnh báo PHP.",
        "include file không tồn tại.",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://www.php.net/manual/en/errorfunc.constants.php",
        "nhanh", 3, True,
    ),
    "PHP_Deprecated": _muc(
        "PHP", "thong_tin",
        r"PHP Deprecated:\s*(.+)",
        "Cảnh báo tính năng sắp bỏ.",
        "Dùng hàm cũ.",
        ["Cập nhật sang hàm mới."],
        False, "",
        "https://www.php.net/manual/en/errorfunc.constants.php",
        "trung_binh", 2, False,
    ),

    # ============================================================
    # NHÓM 13: GO (8 loại)
    # ============================================================
    "Go_Panic": _muc(
        "Go", "nghiem_trong",
        r"panic:\s*(.+)",
        "Panic trong Go.",
        "nil pointer hoặc lỗi runtime.",
        ["Dùng recover().", "Kiểm tra logic."],
        False, "",
        "https://go.dev/ref/spec#Run_time_panics",
        "trung_binh", 4, True,
    ),
    "Go_NilPointer": _muc(
        "Go", "nghiem_trong",
        r"invalid memory address or nil pointer dereference",
        "Truy cập nil pointer.",
        "var p *int; *p = 5.",
        ["Kiểm tra nil."],
        True, "// Sửa:\nif p != nil {\n    *p = 5\n}",
        "https://go.dev/ref/spec#Address_operators",
        "nhanh", 4, True,
    ),
    "Go_IndexOutOfRange": _muc(
        "Go", "nghiem_trong",
        r"index out of range",
        "Index ngoài phạm vi.",
        "arr[10] khi len=5.",
        ["Kiểm tra index."],
        True, "",
        "https://go.dev/ref/spec#Index_expressions",
        "nhanh", 4, True,
    ),
    "Go_SliceBounds": _muc(
        "Go", "nghiem_trong",
        r"slice bounds out of range",
        "Slice vượt phạm vi.",
        "s[10:20] khi len=5.",
        ["Kiểm tra len slice."],
        True, "",
        "https://go.dev/ref/spec#Slice_expressions",
        "nhanh", 3, True,
    ),
    "Go_MapRead": _muc(
        "Go", "nghiem_trong",
        r"assignment to entry in nil map",
        "Ghi vào map nil.",
        "var m map[string]int; m[\"a\"]=1",
        ["Khởi tạo map: make(map[...]...)."],
        True, "// Sửa:\nm := make(map[string]int)",
        "https://go.dev/ref/spec#Map_types",
        "nhanh", 3, True,
    ),
    "Go_Deadlock": _muc(
        "Go", "nghiem_trong",
        r"all goroutines are asleep - deadlock",
        "Deadlock goroutine.",
        "Channel chờ nhau.",
        ["Kiểm tra channel.", "Dùng select + default."],
        False, "",
        "https://go.dev/ref/spec#Channel_types",
        "lau", 5, False,
    ),
    "Go_InterfaceConversion": _muc(
        "Go", "nghiem_trong",
        r"interface conversion:\s*(.+)",
        "Ép interface sai.",
        "v.(int) khi v là string.",
        ["Dùng comma-ok: v, ok := x.(int)"],
        True, "// Sửa:\nif v, ok := x.(int); ok {\n    // dùng v\n}",
        "https://go.dev/ref/spec#Type_assertions",
        "nhanh", 3, True,
    ),
    "Go_ClosedChannel": _muc(
        "Go", "nghiem_trong",
        r"send on closed channel",
        "Gửi vào channel đã đóng.",
        "close(ch); ch <- 1",
        ["Kiểm tra channel trước khi gửi."],
        False, "",
        "https://go.dev/ref/spec#Close",
        "trung_binh", 4, True,
    ),

    # ============================================================
    # NHÓM 14: RUST (6 loại)
    # ============================================================
    "Rust_Panic": _muc(
        "Rust", "nghiem_trong",
        r"thread '.*?' panicked at\s*(.+)",
        "Panic trong Rust.",
        "unwrap() trên None/Err.",
        ["Dùng match hoặc ?.", "Tránh unwrap()."],
        True, "// Sửa:\n// let x = opt.unwrap_or(0);",
        "https://doc.rust-lang.org/std/result/enum.Result.html",
        "trung_binh", 4, True,
    ),
    "Rust_UnwrapErr": _muc(
        "Rust", "nghiem_trong",
        r"called `Result::unwrap\(\)` on an `Err` value",
        "unwrap() trên Err.",
        "let x = ham().unwrap();",
        ["Dùng ? để propagate.", "Dùng match."],
        True, "// Sửa:\nlet x = ham()?;",
        "https://doc.rust-lang.org/std/result/enum.Result.html",
        "nhanh", 3, True,
    ),
    "Rust_IndexOutOfBounds": _muc(
        "Rust", "nghiem_trong",
        r"index out of bounds",
        "Index ngoài phạm vi (Rust).",
        "v[10] khi v.len()=5.",
        ["Dùng v.get(10)."],
        True, "// Sửa:\nif let Some(x) = v.get(10) {\n    // dùng x\n}",
        "https://doc.rust-lang.org/std/vec/struct.Vec.html",
        "nhanh", 3, True,
    ),
    "Rust_BorrowChecker": _muc(
        "Rust", "nghiem_trong",
        r"cannot borrow\s*(.+)",
        "Vi phạm borrow checker.",
        "Mượn mutable + immutable cùng lúc.",
        ["Clone dữ liệu.", "Rút ngắn scope."],
        False, "",
        "https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html",
        "lau", 5, True,
    ),
    "Rust_CannotMove": _muc(
        "Rust", "nghiem_trong",
        r"cannot move out of",
        "Move giá trị bị cấm.",
        "Dùng giá trị sau khi move.",
        ["Clone.", "Dùng reference."],
        False, "",
        "https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html",
        "trung_binh", 4, True,
    ),
    "Rust_LifetimeError": _muc(
        "Rust", "nghiem_trong",
        r"lifetime may not live long enough",
        "Lifetime không hợp lệ.",
        "Reference sống lâu hơn dữ liệu.",
        ["Thêm lifetime annotation.", "Đổi ownership."],
        False, "",
        "https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html",
        "lau", 5, False,
    ),

    # ============================================================
    # NHÓM 15: SWIFT (5 loại)
    # ============================================================
    "Swift_UnexpectedlyFoundNil": _muc(
        "Swift", "nghiem_trong",
        r"Unexpectedly found nil while unwrapping",
        "Force unwrap nil.",
        "let x = opt! khi opt nil.",
        ["Dùng if let hoặc guard let."],
        True, "// Sửa:\nif let x = opt {\n    // dùng x\n}",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/optionalchaining/",
        "nhanh", 4, True,
    ),
    "Swift_IndexOutOfRange": _muc(
        "Swift", "nghiem_trong",
        r"Fatal error:\s*Index out of range",
        "Index ngoài phạm vi.",
        "arr[10] khi arr.count=5.",
        ["Kiểm tra count."],
        True, "",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/collectiontypes/",
        "nhanh", 4, True,
    ),
    "Swift_FatalError": _muc(
        "Swift", "nghiem_trong",
        r"Thread \d+: Fatal error:\s*(.+)",
        "Fatal error Swift.",
        "Lỗi runtime nghiêm trọng.",
        ["Đọc thông điệp.", "Kiểm tra logic."],
        False, "",
        "https://docs.swift.org/swift-book/",
        "trung_binh", 4, True,
    ),
    "Swift_TypeMismatch": _muc(
        "Swift", "nghiem_trong",
        r"Cannot convert value of type",
        "Sai kiểu Swift.",
        "Gán Int cho String.",
        ["Ép kiểu."],
        True, "",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/types/",
        "nhanh", 3, True,
    ),
    "Swift_MissingArgument": _muc(
        "Swift", "nghiem_trong",
        r"Missing argument for parameter",
        "Thiếu tham số Swift.",
        "Gọi hàm thiếu đối số.",
        ["Thêm đối số."],
        True, "",
        "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/functions/",
        "nhanh", 2, True,
    ),

    # ============================================================
    # NHÓM 16: KOTLIN (5 loại)
    # ============================================================
    "Kotlin_NullPointer": _muc(
        "Kotlin", "nghiem_trong",
        r"KotlinNullPointerException|NullPointerException",
        "Dùng biến null (Kotlin).",
        "x!! khi x = null.",
        ["Dùng ?. hoặc ?:."],
        True, "// Sửa:\nval y = x ?: 0",
        "https://kotlinlang.org/docs/null-safety.html",
        "nhanh", 4, True,
    ),
    "Kotlin_ClassCast": _muc(
        "Kotlin", "nghiem_trong",
        r"ClassCastException",
        "Ép kiểu sai (Kotlin).",
        "x as String khi x là Int.",
        ["Dùng as? (safe cast)."],
        True, "// Sửa:\nval y = x as? String",
        "https://kotlinlang.org/docs/typecasts.html",
        "nhanh", 3, True,
    ),
    "Kotlin_IndexOutOfBounds": _muc(
        "Kotlin", "nghiem_trong",
        r"IndexOutOfBoundsException",
        "Index ngoài phạm vi.",
        "list[10] khi size=5.",
        ["Kiểm tra size."],
        True, "",
        "https://kotlinlang.org/docs/collections-overview.html",
        "nhanh", 3, True,
    ),
    "Kotlin_NumberFormat": _muc(
        "Kotlin", "nghiem_trong",
        r"NumberFormatException",
        "Parse số lỗi.",
        "'abc'.toInt()",
        ["Kiểm tra chuỗi."],
        True, "",
        "https://kotlinlang.org/docs/strings.html",
        "nhanh", 3, True,
    ),
    "Kotlin_StackOverflow": _muc(
        "Kotlin", "nghiem_trong",
        r"StackOverflowError",
        "Đệ quy quá sâu.",
        "Đệ quy vô hạn.",
        ["Thêm điều kiện dừng."],
        True, "",
        "https://kotlinlang.org/docs/functions.html",
        "trung_binh", 4, True,
    ),

    # ============================================================
    # NHÓM 17: C# / .NET (10 loại)
    # ============================================================
    "CSharp_NullReference": _muc(
        "C#/.NET", "nghiem_trong",
        r"NullReferenceException",
        "Dùng biến null (C#).",
        "obj.Method() khi obj = null.",
        ["Kiểm tra null.", "Dùng ?."],
        True, "// Sửa:\nobj?.Method();",
        "https://learn.microsoft.com/en-us/dotnet/api/system.nullreferenceexception",
        "nhanh", 5, True,
    ),
    "CSharp_IndexOutOfRange": _muc(
        "C#/.NET", "nghiem_trong",
        r"IndexOutOfRangeException",
        "Index ngoài phạm vi.",
        "arr[10] khi length=5.",
        ["Kiểm tra length."],
        True, "",
        "https://learn.microsoft.com/en-us/dotnet/api/system.indexoutofrangeexception",
        "nhanh", 3, True,
    ),
    "CSharp_ArgumentException": _muc(
        "C#/.NET", "nghiem_trong",
        r"ArgumentException",
        "Đối số không hợp lệ.",
        "Truyền sai đối số.",
        ["Kiểm tra đối số."],
        False, "",
        "https://learn.microsoft.com/en-us/dotnet/api/system.argumentexception",
        "nhanh", 3, True,
    ),
    "CSharp_ArgumentNullException": _muc(
        "C#/.NET", "nghiem_trong",
        r"ArgumentNullException",
        "Đối số là null.",
        "Truyền null khi không cho phép.",
        ["Kiểm tra null.", "Ném lỗi sớm."],
        True, "",
        "https://learn.microsoft.com/en-us/dotnet/api/system.argumentnullexception",
        "nhanh", 3, True,
    ),
    "CSharp_InvalidOperation": _muc(
        "C#/.NET", "nghiem_trong",
        r"InvalidOperationException",
        "Trạng thái không hợp lệ.",
        "Sửa collection khi đang duyệt.",
        ["Kiểm tra trạng thái."],
        False, "",
        "https://learn.microsoft.com/en-us/dotnet/api/system.invalidoperationexception",
        "trung_binh", 3, True,
    ),
    "CSharp_FormatException": _muc(
        "C#/.NET", "nghiem_trong",
        r"FormatException",
        "Parse lỗi.",
        "int.Parse(\"abc\")",
        ["Dùng TryParse."],
        True, "// Sửa:\nif (int.TryParse(s, out int n)) { /* dùng n */ }",
        "https://learn.microsoft.com/en-us/dotnet/api/system.formatexception",
        "nhanh", 3, True,
    ),
    "CSharp_OverflowException": _muc(
        "C#/.NET", "nghiem_trong",
        r"OverflowException",
        "Tràn số (C#).",
        "int.MaxValue + 1.",
        ["Dùng long.", "Kiểm tra checked."],
        False, "",
        "https://learn.microsoft.com/en-us/dotnet/api/system.overflowexception",
        "nhanh", 3, False,
    ),
    "CSharp_OutOfMemory": _muc(
        "C#/.NET", "nghiem_trong",
        r"OutOfMemoryException",
        "Hết bộ nhớ (C#).",
        "Cấp phát quá lớn.",
        ["Giảm dữ liệu."],
        False, "",
        "https://learn.microsoft.com/en-us/dotnet/api/system.outofmemoryexception",
        "lau", 5, False,
    ),
    "CSharp_StackOverflow": _muc(
        "C#/.NET", "nghiem_trong",
        r"StackOverflowException",
        "Đệ quy quá sâu (C#).",
        "Đệ quy vô hạn.",
        ["Thêm điều kiện dừng."],
        True, "",
        "https://learn.microsoft.com/en-us/dotnet/api/system.stackoverflowexception",
        "trung_binh", 4, True,
    ),
    "CSharp_FileNotFound": _muc(
        "C#/.NET", "nghiem_trong",
        r"FileNotFoundException",
        "Không tìm thấy file (C#).",
        "File.ReadAllText(\"abc\")",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://learn.microsoft.com/en-us/dotnet/api/system.io.filenotfoundexception",
        "nhanh", 3, True,
    ),

    # ============================================================
    # NHÓM 18: SQL (6 loại)
    # ============================================================
    "SQL_SyntaxError": _muc(
        "SQL", "nghiem_trong",
        r"You have an error in your SQL syntax|Syntax error",
        "Sai cú pháp SQL.",
        "Thiếu dấu ; hoặc FROM.",
        ["Kiểm tra câu query."],
        True, "",
        "https://dev.mysql.com/doc/refman/8.0/en/sql-statements.html",
        "nhanh", 3, True,
    ),
    "SQL_UnknownColumn": _muc(
        "SQL", "nghiem_trong",
        r"Unknown column '([^']+)'",
        "Cột không tồn tại.",
        "SELECT xyz FROM abc khi không có cột xyz.",
        ["Kiểm tra tên cột."],
        True, "",
        "https://dev.mysql.com/doc/refman/8.0/en/select.html",
        "nhanh", 3, True,
    ),
    "SQL_TableNotExist": _muc(
        "SQL", "nghiem_trong",
        r"Table '([^']+)' doesn't exist",
        "Bảng không tồn tại.",
        "SELECT * FROM abc khi bảng không có.",
        ["Kiểm tra tên bảng."],
        True, "",
        "https://dev.mysql.com/doc/refman/8.0/en/show-tables.html",
        "nhanh", 3, True,
    ),
    "SQL_DuplicateEntry": _muc(
        "SQL", "nghiem_trong",
        r"Duplicate entry '([^']+)' for key",
        "Trùng key unique (SQL).",
        "Insert giá trị đã tồn tại.",
        ["Dùng INSERT IGNORE.", "Dùng ON DUPLICATE KEY UPDATE."],
        True, "INSERT IGNORE INTO ...",
        "https://dev.mysql.com/doc/refman/8.0/en/insert.html",
        "nhanh", 3, True,
    ),
    "SQL_ForeignKey": _muc(
        "SQL", "nghiem_trong",
        r"Cannot add or update a child row: a foreign key constraint fails",
        "Vi phạm foreign key.",
        "Insert FK không tồn tại.",
        ["Tạo bản ghi cha trước."],
        False, "",
        "https://dev.mysql.com/doc/refman/8.0/en/create-table-foreign-keys.html",
        "trung_binh", 3, True,
    ),
    "SQL_DataTooLong": _muc(
        "SQL", "nghiem_trong",
        r"Data too long for column '([^']+)'",
        "Dữ liệu vượt độ dài cột.",
        "Insert chuỗi dài hơn VARCHAR.",
        ["Tăng độ dài cột.", "Cắt chuỗi."],
        True, "",
        "https://dev.mysql.com/doc/refman/8.0/en/char.html",
        "nhanh", 3, True,
    ),

    # ============================================================
    # NHÓM 19: BASH / SHELL (8 loại)
    # ============================================================
    "Bash_CommandNotFound": _muc(
        "Bash", "nghiem_trong",
        r"command not found:\s*(.+)",
        "Lệnh không tồn tại.",
        "abc khi chưa cài abc.",
        ["Cài đặt.", "Kiểm tra PATH."],
        False, "",
        "https://www.gnu.org/software/bash/manual/",
        "nhanh", 3, True,
    ),
    "Bash_PermissionDenied": _muc(
        "Bash", "nghiem_trong",
        r"Permission denied",
        "Không có quyền thực thi.",
        "Chạy file không có +x.",
        ["chmod +x file."],
        True, "chmod +x script.sh",
        "https://www.gnu.org/software/bash/manual/",
        "nhanh", 3, True,
    ),
    "Bash_NoSuchFile": _muc(
        "Bash", "nghiem_trong",
        r"No such file or directory",
        "File không tồn tại (Bash).",
        "cd /xyz",
        ["Kiểm tra đường dẫn."],
        True, "",
        "https://www.gnu.org/software/bash/manual/",
        "nhanh", 3, True,
    ),
    "Bash_SyntaxError": _muc(
        "Bash", "nghiem_trong",
        r"syntax error near unexpected token",
        "Sai cú pháp Bash.",
        "Thiếu dấu fi, done.",
        ["Kiểm tra if/fi, for/done."],
        True, "",
        "https://www.gnu.org/software/bash/manual/",
        "nhanh", 3, True,
    ),
    "Bash_AmbiguousRedirect": _muc(
        "Bash", "nghiem_trong",
        r"ambiguous redirect",
        "Redirect không rõ ràng.",
        "> $var với var nhiều từ.",
        ["Đặt trong dấu ngoặc: \"$var\"."],
        True, "",
        "https://www.gnu.org/software/bash/manual/",
        "nhanh", 3, False,
    ),
    "Bash_UnboundVariable": _muc(
        "Bash", "nghiem_trong",
        r"unbound variable",
        "Biến chưa định nghĩa (set -u).",
        "echo $xyz khi chưa gán.",
        ["Gán biến trước."],
        True, "// Sửa:\nxyz=\"\"\necho $xyz",
        "https://www.gnu.org/software/bash/manual/",
        "nhanh", 3, True,
    ),
    "Bash_BadSubstitution": _muc(
        "Bash", "nghiem_trong",
        r"bad substitution",
        "Substitution sai.",
        "Dùng ${var[bad]}.",
        ["Kiểm tra cú pháp."],
        True, "",
        "https://www.gnu.org/software/bash/manual/",
        "nhanh", 3, False,
    ),
    "Bash_TooManyArguments": _muc(
        "Bash", "nghiem_trong",
        r"too many arguments",
        "Quá nhiều đối số.",
        "[ $a = $b = $c ]",
        ["Dùng [[ ]]."],
        True, "",
        "https://www.gnu.org/software/bash/manual/",
        "nhanh", 3, False,
    ),

    # ============================================================
    # NHÓM 20: GIT (6 loại)
    # ============================================================
    "Git_NotRepo": _muc(
        "Git", "nghiem_trong",
        r"fatal:\s*not a git repository",
        "Không phải git repo.",
        "Chạy git trong thư mục không có .git.",
        ["git init.", "cd vào repo."],
        True, "git init",
        "https://git-scm.com/docs",
        "nhanh", 3, True,
    ),
    "Git_PushFailed": _muc(
        "Git", "nghiem_trong",
        r"failed to push some refs",
        "Push thất bại.",
        "Remote có commit mới.",
        ["git pull trước.", "git push --force (cẩn thận)."],
        False, "git pull --rebase\ngit push",
        "https://git-scm.com/docs/git-push",
        "nhanh", 3, True,
    ),
    "Git_MergeConflict": _muc(
        "Git", "nghiem_trong",
        r"CONFLICT.*?Merge conflict in\s*(.+)",
        "Xung đột merge.",
        "2 nhánh sửa cùng file.",
        ["Sửa thủ công file.", "git add + commit."],
        False, "",
        "https://git-scm.com/docs/git-merge",
        "trung_binh", 4, True,
    ),
    "Git_DetachedHead": _muc(
        "Git", "canh_bao",
        r"You are in 'detached HEAD' state",
        "Detached HEAD.",
        "Checkout commit cụ thể.",
        ["git checkout -b <nhánh mới>."],
        True, "git checkout -b nhanh-moi",
        "https://git-scm.com/docs/git-checkout",
        "nhanh", 3, True,
    ),
    "Git_NonFastForward": _muc(
        "Git", "nghiem_trong",
        r"rejected.*?non-fast-forward",
        "Push bị từ chối (non-fast-forward).",
        "Remote đi trước local.",
        ["git pull --rebase.", "git push lại."],
        True, "git pull --rebase\ngit push",
        "https://git-scm.com/docs/git-push",
        "nhanh", 3, True,
    ),
    "Git_UnrelatedHistories": _muc(
        "Git", "nghiem_trong",
        r"refusing to merge unrelated histories",
        "Merge 2 lịch sử không liên quan.",
        "Merge repo mới với repo cũ.",
        ["git pull --allow-unrelated-histories."],
        True, "git pull origin main --allow-unrelated-histories",
        "https://git-scm.com/docs/git-merge",
        "nhanh", 3, True,
    ),

    # ============================================================
    # NHÓM 21: REDIS (4 loại)
    # ============================================================
    "Redis_NOAUTH": _muc(
        "Redis", "nghiem_trong",
        r"NOAUTH Authentication required",
        "Redis cần xác thực.",
        "Chưa gửi password.",
        ["Thêm AUTH password."],
        True, "AUTH matkhau",
        "https://redis.io/commands/auth/",
        "nhanh", 3, True,
    ),
    "Redis_WRONGTYPE": _muc(
        "Redis", "nghiem_trong",
        r"WRONGTYPE Operation against a key holding the wrong kind of value",
        "Sai kiểu dữ liệu Redis.",
        "Dùng list command trên string key.",
        ["Kiểm tra kiểu key.", "Xóa key cũ."],
        True, "",
        "https://redis.io/commands/type/",
        "nhanh", 3, True,
    ),
    "Redis_OOM": _muc(
        "Redis", "nghiem_trong",
        r"OOM command not allowed",
        "Redis hết bộ nhớ.",
        "Vượt maxmemory.",
        ["Tăng maxmemory.", "Xóa key cũ."],
        False, "",
        "https://redis.io/docs/management/optimization/memory-optimization/",
        "trung_binh", 4, True,
    ),
    "Redis_LOADING": _muc(
        "Redis", "canh_bao",
        r"LOADING Redis is loading the dataset in memory",
        "Redis đang load dữ liệu.",
        "Khởi động lại Redis.",
        ["Chờ Redis load xong."],
        False, "",
        "https://redis.io/docs/management/persistence/",
        "nhanh", 2, True,
    ),

    # ============================================================
    # NHÓM 22: ELASTICSEARCH (4 loại)
    # ============================================================
    "ES_IndexNotFound": _muc(
        "Elasticsearch", "nghiem_trong",
        r"index_not_found_exception",
        "Index không tồn tại.",
        "Query index chưa tạo.",
        ["Tạo index trước."],
        True, "",
        "https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules.html",
        "nhanh", 3, True,
    ),
    "ES_SearchPhaseExecution": _muc(
        "Elasticsearch", "nghiem_trong",
        r"search_phase_execution_exception",
        "Lỗi khi search ES.",
        "Query sai / shard lỗi.",
        ["Kiểm tra query.", "Kiểm tra shards."],
        False, "",
        "https://www.elastic.co/guide/en/elasticsearch/reference/current/search.html",
        "trung_binh", 3, True,
    ),
    "ES_MapperParsing": _muc(
        "Elasticsearch", "nghiem_trong",
        r"mapper_parsing_exception",
        "Parse mapping lỗi.",
        "Document không khớp mapping.",
        ["Kiểm tra mapping.", "Ép kiểu đúng."],
        False, "",
        "https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html",
        "trung_binh", 3, True,
    ),
    "ES_CircuitBreaking": _muc(
        "Elasticsearch", "nghiem_trong",
        r"circuit_breaking_exception",
        "Vượt giới hạn bộ nhớ ES.",
        "Query quá lớn.",
        ["Tăng heap.", "Chia nhỏ query."],
        False, "",
        "https://www.elastic.co/guide/en/elasticsearch/reference/current/circuit-breaker.html",
        "trung_binh", 4, True,
    ),

    # ============================================================
    # NHÓM 23: KUBERNETES (7 loại)
    # ============================================================
    "K8s_CrashLoopBackOff": _muc(
        "Kubernetes", "nghiem_trong",
        r"CrashLoopBackOff",
        "Pod restart liên tục.",
        "App crash khi khởi động.",
        ["kubectl logs <pod>."],
        False, "kubectl logs <pod>",
        "https://kubernetes.io/docs/tasks/debug/",
        "trung_binh", 5, True,
    ),
    "K8s_ImagePullBackOff": _muc(
        "Kubernetes", "nghiem_trong",
        r"ImagePullBackOff",
        "Không pull được image.",
        "Image sai / registry lỗi.",
        ["Kiểm tra image name.", "Kiểm tra secret."],
        False, "",
        "https://kubernetes.io/docs/concepts/containers/images/",
        "trung_binh", 3, True,
    ),
    "K8s_ErrImagePull": _muc(
        "Kubernetes", "nghiem_trong",
        r"ErrImagePull",
        "Lỗi pull image.",
        "Tương tự ImagePullBackOff.",
        ["Kiểm tra image."],
        False, "",
        "https://kubernetes.io/docs/concepts/containers/images/",
        "trung_binh", 3, True,
    ),
    "K8s_OOMKilled": _muc(
        "Kubernetes", "nghiem_trong",
        r"OOMKilled",
        "Pod bị kill vì hết RAM.",
        "Vượt memory limit.",
        ["Tăng limit.", "Tối ưu code."],
        False, "",
        "https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/",
        "trung_binh", 4, True,
    ),
    "K8s_Pending": _muc(
        "Kubernetes", "canh_bao",
        r"Pending",
        "Pod đang chờ schedule.",
        "Không đủ resource.",
        ["Kiểm tra node.", "Kiểm tra resource request."],
        False, "kubectl describe pod <pod>",
        "https://kubernetes.io/docs/concepts/scheduling-eviction/",
        "trung_binh", 3, True,
    ),
    "K8s_Evicted": _muc(
        "Kubernetes", "nghiem_trong",
        r"Evicted",
        "Pod bị evict.",
        "Node hết tài nguyên.",
        ["Dọn dẹp node.", "Tăng tài nguyên."],
        False, "",
        "https://kubernetes.io/docs/concepts/scheduling-eviction/",
        "trung_binh", 3, False,
    ),
    "K8s_NodeNotReady": _muc(
        "Kubernetes", "nghiem_trong",
        r"NodeNotReady",
        "Node không sẵn sàng.",
        "Node down.",
        ["Kiểm tra node.", "Restart kubelet."],
        False, "",
        "https://kubernetes.io/docs/concepts/architecture/nodes/",
        "lau", 4, False,
    ),

    # ============================================================
    # NHÓM 24: CLOUD (AWS/GCP/Azure) (8 loại)
    # ============================================================
    "Cloud_AccessDenied": _muc(
        "Cloud", "nghiem_trong",
        r"AccessDenied|Access Denied",
        "Truy cập cloud bị từ chối.",
        "IAM policy không cho phép.",
        ["Kiểm tra IAM."],
        False, "",
        "https://docs.aws.amazon.com/IAM/latest/UserGuide/",
        "trung_binh", 3, True,
    ),
    "Cloud_InvalidAccessKey": _muc(
        "Cloud", "nghiem_trong",
        r"InvalidAccessKeyId",
        "Access key sai.",
        "Key sai / hết hạn.",
        ["Kiểm tra key."],
        False, "",
        "https://docs.aws.amazon.com/IAM/latest/UserGuide/",
        "nhanh", 3, True,
    ),
    "Cloud_SignatureMismatch": _muc(
        "Cloud", "nghiem_trong",
        r"SignatureDoesNotMatch",
        "Chữ ký request sai.",
        "Secret key sai.",
        ["Kiểm tra secret."],
        False, "",
        "https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html",
        "nhanh", 3, True,
    ),
    "Cloud_Throttling": _muc(
        "Cloud", "nghiem_trong",
        r"ThrottlingException|Throttling",
        "Vượt rate limit cloud.",
        "Gọi API quá nhiều.",
        ["Chờ.", "Xoay key."],
        True, "",
        "https://docs.aws.amazon.com/general/latest/gr/api-retries.html",
        "nhanh", 3, True,
    ),
    "Cloud_ResourceNotFound": _muc(
        "Cloud", "nghiem_trong",
        r"ResourceNotFoundException",
        "Không tìm thấy resource.",
        "Resource đã xóa / sai id.",
        ["Kiểm tra id."],
        False, "",
        "https://docs.aws.amazon.com/",
        "nhanh", 3, False,
    ),
    "Cloud_QuotaExceeded": _muc(
        "Cloud", "nghiem_trong",
        r"QuotaExceeded|quota exceeded",
        "Vượt quota cloud.",
        "Đã dùng hết quota.",
        ["Xin tăng quota.", "Chờ reset."],
        False, "",
        "https://docs.aws.amazon.com/servicequotas/",
        "trung_binh", 3, True,
    ),
    "Cloud_RegionError": _muc(
        "Cloud", "nghiem_trong",
        r"InvalidRegion|region.*?does not exist",
        "Region không hợp lệ.",
        "Sai region.",
        ["Kiểm tra region."],
        False, "",
        "https://docs.aws.amazon.com/general/latest/gr/rande.html",
        "nhanh", 2, False,
    ),
    "Cloud_PermissionDenied": _muc(
        "Cloud", "nghiem_trong",
        r"PermissionDenied|permission denied",
        "Không có quyền.",
        "IAM thiếu permission.",
        ["Cập nhật IAM."],
        False, "",
        "https://cloud.google.com/iam/docs",
        "trung_binh", 3, True,
    ),

    # ============================================================
    # NHÓM 25: AI / ML (8 loại)
    # ============================================================
    "AI_CUDA_OOM": _muc(
        "AI/ML", "nghiem_trong",
        r"CUDA out of memory",
        "Hết VRAM GPU.",
        "Batch size quá lớn.",
        ["Giảm batch size.", "Dùng gradient accumulation."],
        True, "# Sửa:\nbatch_size = 8  # giảm từ 32",
        "https://pytorch.org/docs/stable/notes/cuda.html",
        "trung_binh", 4, True,
    ),
    "AI_ShapeMismatch": _muc(
        "AI/ML", "nghiem_trong",
        r"(?:shape|size) mismatch|expected.*?got",
        "Shape tensor không khớp.",
        "Nhập (32,10) vào model cần (32,5).",
        ["Kiểm tra shape.", "Reshape."],
        True, "# Sửa:\nx = x.reshape(-1, 5)",
        "https://pytorch.org/docs/stable/tensors.html",
        "trung_binh", 4, True,
    ),
    "AI_NaN_Loss": _muc(
        "AI/ML", "nghiem_trong",
        r"loss.*?nan|nan.*?loss",
        "Loss = NaN.",
        "LR quá cao / chia 0.",
        ["Giảm LR.", "Clip gradient."],
        True, "# Sửa:\noptimizer = Adam(model.parameters(), lr=1e-4)",
        "https://pytorch.org/docs/stable/optim.html",
        "lau", 5, True,
    ),
    "AI_GradientExplosion": _muc(
        "AI/ML", "nghiem_trong",
        r"gradient.*?explod|inf.*?gradient",
        "Gradient bùng nổ.",
        "LR cao / mạng sâu.",
        ["Gradient clipping.", "Giảm LR."],
        True, "# Sửa:\ntorch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)",
        "https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html",
        "trung_binh", 4, True,
    ),
    "AI_DeviceMismatch": _muc(
        "AI/ML", "nghiem_trong",
        r"Expected all tensors to be on the same device",
        "Tensor khác device.",
        "1 cái CPU, 1 cái GPU.",
        ["Chuyển hết sang cùng device."],
        True, "# Sửa:\nx = x.to(device)\ny = y.to(device)",
        "https://pytorch.org/docs/stable/notes/cuda.html",
        "nhanh", 4, True,
    ),
    "AI_KeyErrorInputIds": _muc(
        "AI/ML", "nghiem_trong",
        r"KeyError:\s*'input_ids'",
        "Thiếu input_ids cho model.",
        "Tokenizer chưa chạy.",
        ["Chạy tokenizer trước."],
        True, "# Sửa:\ninputs = tokenizer(text, return_tensors='pt')",
        "https://huggingface.co/docs/transformers/",
        "nhanh", 3, True,
    ),
    "AI_TokenizerError": _muc(
        "AI/ML", "nghiem_trong",
        r"tokenizer.*?error|Tokenizer.*?not found",
        "Lỗi tokenizer.",
        "Chưa load tokenizer.",
        ["Load tokenizer trước."],
        False, "# Sửa:\ntokenizer = AutoTokenizer.from_pretrained('...')",
        "https://huggingface.co/docs/transformers/",
        "nhanh", 3, True,
    ),
    "AI_TrainingOOM": _muc(
        "AI/ML", "nghiem_trong",
        r"out of memory during training|RuntimeError: CUDA",
        "Hết bộ nhớ khi train.",
        "Batch size lớn.",
        ["Giảm batch.", "Dùng mixed precision."],
        True, "# Sửa:\nbatch_size = 4",
        "https://pytorch.org/docs/stable/notes/cuda.html",
        "trung_binh", 4, True,
    ),

    # ============================================================
    # NHÓM 26: WEB3 / BLOCKCHAIN (5 loại)
    # ============================================================
    "Web3_OutOfGas": _muc(
        "Web3", "nghiem_trong",
        r"out of gas",
        "Hết gas khi giao dịch.",
        "Gas limit thấp.",
        ["Tăng gas limit."],
        True, "",
        "https://ethereum.org/en/developers/docs/gas/",
        "nhanh", 3, True,
    ),
    "Web3_NonceTooLow": _muc(
        "Web3", "nghiem_trong",
        r"nonce too low",
        "Nonce quá thấp.",
        "Gửi tx với nonce cũ.",
        ["Dùng nonce mới."],
        True, "",
        "https://ethereum.org/en/developers/docs/apis/json-rpc/",
        "nhanh", 3, True,
    ),
    "Web3_InsufficientFunds": _muc(
        "Web3", "nghiem_trong",
        r"insufficient funds",
        "Không đủ tiền cho gas.",
        "Số dư thấp.",
        ["Nạp thêm."],
        False, "",
        "https://ethereum.org/en/developers/docs/gas/",
        "nhanh", 3, True,
    ),
    "Web3_Revert": _muc(
        "Web3", "nghiem_trong",
        r"(?:execution )?revert(?:ed)?",
        "Giao dịch bị revert.",
        "require() thất bại.",
        ["Đọc lý do revert.", "Kiểm tra điều kiện."],
        False, "",
        "https://docs.soliditylang.org/en/latest/control-structures.html#error-handling-assert-require-revert-and-exceptions",
        "trung_binh", 4, True,
    ),
    "Web3_ExecutionReverted": _muc(
        "Web3", "nghiem_trong",
        r"execution reverted",
        "Thực thi bị revert.",
        "Hợp đồng từ chối.",
        ["Kiểm tra input.", "Đọc reason."],
        False, "",
        "https://docs.soliditylang.org/",
        "trung_binh", 3, True,
    ),

    # ============================================================
    # NHÓM 27: GAME DEV (5 loại)
    # ============================================================
    "Unity_NullReference": _muc(
        "Unity", "nghiem_trong",
        r"NullReferenceException",
        "Dùng biến null (Unity).",
        "GetComponent<T>() trả null.",
        ["Kiểm tra null.", "Dùng TryGetComponent."],
        True, "// Sửa:\nif (TryGetComponent<Rigidbody>(out var rb)) { /* dùng rb */ }",
        "https://docs.unity3d.com/ScriptReference/",
        "nhanh", 4, True,
    ),
    "Unity_MissingReference": _muc(
        "Unity", "nghiem_trong",
        r"MissingReferenceException",
        "Reference bị mất.",
        "Object đã bị destroy.",
        ["Kiểm tra object còn tồn tại."],
        False, "",
        "https://docs.unity3d.com/ScriptReference/",
        "trung_binh", 4, True,
    ),
    "Unity_MissingComponent": _muc(
        "Unity", "nghiem_trong",
        r"MissingComponentException",
        "Component không tồn tại.",
        "GetComponent<T>() khi object không có T.",
        ["Add component trước.", "Dùng TryGetComponent."],
        True, "",
        "https://docs.unity3d.com/ScriptReference/",
        "nhanh", 3, True,
    ),
    "Unity_GameObjectNotFound": _muc(
        "Unity", "nghiem_trong",
        r"GameObject.*?not found",
        "Không tìm thấy GameObject.",
        "GameObject.Find sai tên.",
        ["Kiểm tra tên object."],
        False, "",
        "https://docs.unity3d.com/ScriptReference/GameObject.Find.html",
        "nhanh", 3, True,
    ),
    "Unreal_NullReference": _muc(
        "Unreal", "nghiem_trong",
        r"NullReferenceException|Fatal error.*?null",
        "Dùng null (Unreal).",
        "Truy cập pointer null.",
        ["Kiểm tra IsValid()."],
        True, "// Sửa:\nif (IsValid(Obj)) { Obj->Method(); }",
        "https://docs.unrealengine.com/",
        "trung_binh", 4, True,
    ),

    # ============================================================
    # NHÓM 28: MOBILE (Android/iOS) (8 loại)
    # ============================================================
    "Android_ANR": _muc(
        "Android", "nghiem_trong",
        r"ANR in|Application Not Responding",
        "App không phản hồi (Android).",
        "Block UI thread.",
        ["Chuyển việc nặng sang thread khác."],
        False, "",
        "https://developer.android.com/topic/performance/vitals/anr",
        "trung_binh", 4, True,
    ),
    "Android_ActivityNotFound": _muc(
        "Android", "nghiem_trong",
        r"ActivityNotFoundException",
        "Không tìm thấy Activity.",
        "Intent sai.",
        ["Kiểm tra intent.", "Khai báo trong manifest."],
        True, "",
        "https://developer.android.com/reference/android/content/ActivityNotFoundException",
        "nhanh", 3, True,
    ),
    "Android_ClassNotFound": _muc(
        "Android", "nghiem_trong",
        r"ClassNotFoundException",
        "Không tìm thấy class (Android).",
        "Thiếu dependency.",
        ["Kiểm tra gradle."],
        False, "",
        "https://developer.android.com/studio/build/dependencies",
        "trung_binh", 3, True,
    ),
    "Android_ResourcesNotFound": _muc(
        "Android", "nghiem_trong",
        r"Resources\$NotFoundException",
        "Không tìm thấy resource.",
        "R.id.xyz không tồn tại.",
        ["Kiểm tra res/."],
        False, "",
        "https://developer.android.com/guide/topics/resources/",
        "nhanh", 3, True,
    ),
    "iOS_SIGABRT": _muc(
        "iOS", "nghiem_trong",
        r"SIGABRT",
        "App crash (iOS).",
        "Assertion hoặc exception.",
        ["Xem crash log."],
        False, "",
        "https://developer.apple.com/documentation/xcode/diagnosing_issues_using_crash_reports_and_device_logs",
        "trung_binh", 4, True,
    ),
    "iOS_EXC_BAD_ACCESS": _muc(
        "iOS", "nghiem_trong",
        r"EXC_BAD_ACCESS",
        "Truy cập bộ nhớ sai (iOS).",
        "Dùng object đã release.",
        ["Kiểm tra ARC.", "Tránh retain cycle."],
        False, "",
        "https://developer.apple.com/documentation/xcode/diagnosing_issues_using_crash_reports_and_device_logs",
        "lau", 5, True,
    ),
    "iOS_UnrecognizedSelector": _muc(
        "iOS", "nghiem_trong",
        r"unrecognized selector sent to instance",
        "Gọi method không tồn tại (iOS).",
        "SEL sai.",
        ["Kiểm tra respondsToSelector."],
        True, "",
        "https://developer.apple.com/documentation/objectivec/nsobject",
        "nhanh", 4, True,
    ),
    "Mobile_OutOfMemory": _muc(
        "Mobile", "nghiem_trong",
        r"OutOfMemoryError|out of memory",
        "Hết bộ nhớ mobile.",
        "Dùng quá nhiều RAM.",
        ["Giảm ảnh.", "Giải phóng object."],
        False, "",
        "https://developer.android.com/topic/performance/memory",
        "trung_binh", 4, True,
    ),

    # ============================================================
    # NHÓM 29: TESTING (4 loại)
    # ============================================================
    "Test_AssertionFailed": _muc(
        "Testing", "nghiem_trong",
        r"AssertionError|Assertion failed",
        "Test assertion failed.",
        "expect(a).toBe(b) sai.",
        ["Kiểm tra giá trị thực tế.", "Sửa code hoặc sửa test."],
        False, "",
        "https://jestjs.io/docs/expect",
        "nhanh", 3, True,
    ),
    "Test_Failed": _muc(
        "Testing", "nghiem_trong",
        r"\d+\s+failed|FAILED",
        "Test bị fail.",
        "1 hoặc nhiều test fail.",
        ["Đọc output test.", "Sửa code."],
        False, "",
        "https://docs.pytest.org/",
        "trung_binh", 3, True,
    ),
    "Test_SnapshotMismatch": _muc(
        "Testing", "canh_bao",
        r"snapshot.*?(?:mismatch|does not match)",
        "Snapshot không khớp.",
        "UI thay đổi.",
        ["Cập nhật snapshot: jest -u."],
        True, "npm test -- -u",
        "https://jestjs.io/docs/snapshot-testing",
        "nhanh", 3, True,
    ),
    "Test_Timeout": _muc(
        "Testing", "nghiem_trong",
        r"Timeout.*?exceeded|test timed out",
        "Test timeout.",
        "Test chạy quá lâu.",
        ["Tăng timeout.", "Tối ưu test."],
        True, "",
        "https://jestjs.io/docs/api#testname-fn-timeout",
        "nhanh", 3, True,
    ),

    # ============================================================
    # NHÓM 30: BUILD / PACKAGE (6 loại)
    # ============================================================
    "Build_npm_Error": _muc(
        "Build", "nghiem_trong",
        r"npm ERR!\s*(.+)",
        "Lỗi npm.",
        "Cài package lỗi.",
        ["Xem log npm.", "Xóa node_modules + cài lại."],
        True, "rm -rf node_modules\nnpm install",
        "https://docs.npmjs.com/cli/v10/using-npm/logging",
        "trung_binh", 3, True,
    ),
    "Build_yarn_Error": _muc(
        "Build", "nghiem_trong",
        r"error\s+(?:An unexpected error occurred|Command failed)",
        "Lỗi yarn.",
        "Cài package lỗi.",
        ["Xóa node_modules + cài lại."],
        True, "rm -rf node_modules\nyarn install",
        "https://classic.yarnpkg.com/en/docs/cli/",
        "trung_binh", 3, True,
    ),
    "Build_pip_Error": _muc(
        "Build", "nghiem_trong",
        r"ERROR: Could not (?:find a version|install packages)",
        "Lỗi pip.",
        "Package không tồn tại / version sai.",
        ["Kiểm tra tên package.", "Kiểm tra version."],
        True, "pip install --upgrade pip",
        "https://pip.pypa.io/en/stable/",
        "nhanh", 3, True,
    ),
    "Build_Gradle_Failed": _muc(
        "Build", "nghiem_trong",
        r"Gradle build failed|FAILURE: Build failed",
        "Gradle build thất bại.",
        "Lỗi compile / dependency.",
        ["Xem log chi tiết.", "Kiểm tra build.gradle."],
        False, "./gradlew build --stacktrace",
        "https://docs.gradle.org/current/userguide/userguide.html",
        "trung_binh", 4, True,
    ),
    "Build_Maven_Failed": _muc(
        "Build", "nghiem_trong",
        r"BUILD FAILURE",
        "Maven build thất bại.",
        "Lỗi pom.xml / dependency.",
        ["mvn clean install -X."],
        False, "mvn clean install -X",
        "https://maven.apache.org/guides/",
        "trung_binh", 4, True,
    ),
    "Build_Cargo_Failed": _muc(
        "Build", "nghiem_trong",
        r"error\[E\d+\]|error: could not compile",
        "Cargo build thất bại (Rust).",
        "Lỗi compile.",
        ["Đọc lỗi chi tiết.", "Kiểm tra Cargo.toml."],
        False, "cargo build --verbose",
        "https://doc.rust-lang.org/cargo/",
        "trung_binh", 4, True,
    ),
})


# ================================================================
# ĐỌC LỖI ĐẦU TIÊN
# ================================================================
def doc_loi(stderr):
    """Đọc lỗi ĐẦU TIÊN trong chuỗi stderr. Trả về dict 13 trường."""
    ket_qua = {
        "co_loi": False, "loai_loi": "", "ngon_ngu": "", "muc_do": "",
        "thong_diep": "", "dong": None, "ten_bien": "", "mo_ta": "",
        "vi_du": "", "goi_y": [], "co_the_tu_sua": False,
        "code_sua_mau": "", "tai_lieu": "", "thoi_gian_sua": "",
        "do_nghiem_trong": 0, "pho_bien": False,
    }

    if not stderr or not isinstance(stderr, str):
        return ket_qua

    stderr = stderr.strip()[:20000]

    for loai, thong_tin in LOAI_LOI.items():
        khop = re.search(thong_tin["mau"], stderr)
        if khop:
            ket_qua.update({
                "co_loi": True, "loai_loi": loai,
                "ngon_ngu": thong_tin["ngon_ngu"],
                "muc_do": thong_tin["muc_do"],
                "mo_ta": thong_tin["mo_ta"],
                "vi_du": thong_tin["vi_du"],
                "goi_y": list(thong_tin["goi_y"]),
                "co_the_tu_sua": thong_tin["co_the_tu_sua"],
                "code_sua_mau": thong_tin.get("code_sua_mau", ""),
                "tai_lieu": thong_tin.get("tai_lieu", ""),
                "thoi_gian_sua": thong_tin.get("thoi_gian_sua", ""),
                "do_nghiem_trong": thong_tin.get("do_nghiem_trong", 3),
                "pho_bien": thong_tin.get("pho_bien", False),
            })
            try:
                ket_qua["thong_diep"] = khop.group(0).strip()
                if khop.groups():
                    ket_qua["ten_bien"] = khop.group(1).strip()
            except (IndexError, AttributeError):
                ket_qua["thong_diep"] = stderr[:500]
            break

    ket_qua["dong"] = _trich_so_dong(stderr)

    if not ket_qua["co_loi"] and ("Error" in stderr or "error" in stderr):
        ket_qua.update({
            "co_loi": True, "loai_loi": "UnknownError",
            "ngon_ngu": "Không rõ", "muc_do": "nghiem_trong",
            "mo_ta": "Lỗi không xác định.", "thong_diep": stderr[:500],
        })

    return ket_qua


# ================================================================
# ĐỌC TẤT CẢ LỖI
# ================================================================
def doc_loi_nhieu(stderr):
    """Đọc TẤT CẢ lỗi trong 1 chuỗi stderr (không trùng loại)."""
    if not stderr or not isinstance(stderr, str):
        return []

    stderr = stderr[:30000]
    da_gap = set()
    ket_qua = []

    for loai, thong_tin in LOAI_LOI.items():
        for khop in re.finditer(thong_tin["mau"], stderr):
            if loai in da_gap:
                break
            da_gap.add(loai)

            muc = {
                "loai_loi": loai,
                "ngon_ngu": thong_tin["ngon_ngu"],
                "muc_do": thong_tin["muc_do"],
                "mo_ta": thong_tin["mo_ta"],
                "vi_du": thong_tin["vi_du"],
                "goi_y": list(thong_tin["goi_y"]),
                "co_the_tu_sua": thong_tin["co_the_tu_sua"],
                "code_sua_mau": thong_tin.get("code_sua_mau", ""),
                "tai_lieu": thong_tin.get("tai_lieu", ""),
                "thoi_gian_sua": thong_tin.get("thoi_gian_sua", ""),
                "do_nghiem_trong": thong_tin.get("do_nghiem_trong", 3),
                "pho_bien": thong_tin.get("pho_bien", False),
                "thong_diep": khop.group(0).strip(),
                "dong": None,
            }
            try:
                if khop.groups():
                    muc["ten_bien"] = khop.group(1).strip()
            except (IndexError, AttributeError):
                pass

            ket_qua.append(muc)
            break

    return ket_qua


# ================================================================
# TRÍCH TRACEBACK ĐẦY ĐỦ
# ================================================================
def trich_traceback(stderr):
    """Trích toàn bộ traceback thành list frame (Python, Java, JS)."""
    if not stderr:
        return []

    ket_qua = []
    # Mẫu Python: File "abc.py", line 10, in ham_a
    mau_py = r'File\s+"([^"]+)",\s+line\s+(\d+)(?:,\s+in\s+(.+))?'
    # Mẫu JS: at func (file.js:10:5)
    mau_js = r'at\s+(.+?)\s+\((.+?):(\d+):(\d+)\)'
    # Mẫu Java: at com.abc.Class.method(Class.java:10)
    mau_java = r'at\s+([\w.$]+)\(([\w.]+):(\d+)\)'

    cac_dong = stderr.split("\n")

    for i, dong in enumerate(cac_dong):
        # Python
        khop = re.search(mau_py, dong)
        if khop:
            frame = {
                "ngon_ngu": "Python",
                "file": khop.group(1),
                "dong": int(khop.group(2)),
                "ham": khop.group(3).strip() if khop.group(3) else "<module>",
                "code": "",
            }
            if i + 1 < len(cac_dong):
                frame["code"] = cac_dong[i + 1].strip()
            ket_qua.append(frame)
            continue

        # JavaScript
        khop = re.search(mau_js, dong)
        if khop:
            ket_qua.append({
                "ngon_ngu": "JavaScript",
                "file": khop.group(2),
                "dong": int(khop.group(3)),
                "cot": int(khop.group(4)),
                "ham": khop.group(1).strip(),
                "code": "",
            })
            continue

        # Java
        khop = re.search(mau_java, dong)
        if khop:
            ket_qua.append({
                "ngon_ngu": "Java",
                "file": khop.group(2),
                "dong": int(khop.group(3)),
                "ham": khop.group(1).strip(),
                "code": "",
            })

    return ket_qua


# ================================================================
# TÌM DÒNG BỊ LỖI TRONG CODE GỐC
# ================================================================
def tim_dong_bi_loi(stderr, code):
    """Tìm đúng dòng code bị lỗi trong code gốc."""
    if not stderr or not code:
        return None

    so_dong = _trich_so_dong(stderr)
    if so_dong is None:
        return None

    cac_dong = code.split("\n")
    if 1 <= so_dong <= len(cac_dong):
        return {"so_dong": so_dong, "noi_dung": cac_dong[so_dong - 1]}
    return None


def _trich_so_dong(stderr):
    """Trích số dòng từ stderr."""
    if not stderr:
        return None
    khop = re.search(r"line\s+(\d+)", stderr)
    if khop:
        try:
            return int(khop.group(1))
        except ValueError:
            return None
    return None


# ================================================================
# TRA TỪ ĐIỂN LỖI (KHO 2)
# ================================================================
def tra_tu_dien_loi(loai_loi):
    """Tra từ điển lỗi trong kho 2."""
    if not loai_loi:
        return None
    try:
        from dai_nao.ghi_nho import lay_tu_dien_loi
        danh_sach = lay_tu_dien_loi() or []
    except Exception:
        return None
    for muc in danh_sach:
        if muc.get("loai_loi") == loai_loi:
            return muc
    return None


def luu_vao_tu_dien_loi(loai_loi, du_lieu):
    """Lưu/cập nhật 1 mục trong từ điển lỗi."""
    if not loai_loi or not du_lieu:
        return False
    try:
        from dai_nao.ghi_nho import luu_tu_dien_loi as _luu
        return _luu(loai_loi, du_lieu)
    except Exception as e:
        _ghi_log("loi", f"Không lưu được từ điển lỗi: {e}")
        return False


# ================================================================
# GỢI Ý SỬA LỖI (GỘP)
# ================================================================
def goi_y_sua_loi(stderr):
    """Đọc lỗi + gợi ý sửa (gộp từ điển + mặc định)."""
    thong_tin = doc_loi(stderr)

    ket_qua = {
        "co_loi": thong_tin["co_loi"],
        "loai_loi": thong_tin["loai_loi"],
        "ngon_ngu": thong_tin["ngon_ngu"],
        "muc_do": thong_tin["muc_do"],
        "do_nghiem_trong": thong_tin["do_nghiem_trong"],
        "thoi_gian_sua": thong_tin["thoi_gian_sua"],
        "goi_y": list(thong_tin["goi_y"]),
        "code_sua_mau": thong_tin["code_sua_mau"],
        "tai_lieu": thong_tin["tai_lieu"],
        "tu_dien_co": False,
        "cach_sua_tu_dien": None,
    }

    if not thong_tin["co_loi"]:
        return ket_qua

    muc_tu_dien = tra_tu_dien_loi(thong_tin["loai_loi"])
    if muc_tu_dien:
        ket_qua["tu_dien_co"] = True
        ket_qua["cach_sua_tu_dien"] = muc_tu_dien
        goi_y_tu_dien = muc_tu_dien.get("goi_y", [])
        if isinstance(goi_y_tu_dien, list) and goi_y_tu_dien:
            ket_qua["goi_y"] = goi_y_tu_dien + ket_qua["goi_y"]

    return ket_qua


# ================================================================
# CÁC HÀM MỞ RỘNG
# ================================================================
def lay_tat_ca_loai_loi():
    """Trả danh sách tên tất cả loại lỗi."""
    return list(LOAI_LOI.keys())


def thong_tin_loai_loi(loai_loi):
    """Trả mô tả + ví dụ + gợi ý của 1 loại lỗi."""
    return LOAI_LOI.get(loai_loi)


def co_loi(stderr):
    """Kiểm tra nhanh."""
    if not stderr:
        return False
    return "Error" in stderr or "error" in stderr or "Traceback" in stderr


def lay_loai_loi(stderr):
    """Lấy nhanh tên loại lỗi đầu tiên."""
    if not stderr:
        return ""
    for loai, thong_tin in LOAI_LOI.items():
        if re.search(thong_tin["mau"], stderr):
            return loai
    return ""


def thong_ke_loai_loi():
    """Thống kê số loại lỗi theo ngôn ngữ."""
    thong_ke = {}
    for loai, thong_tin in LOAI_LOI.items():
        nn = thong_tin["ngon_ngu"]
        thong_ke[nn] = thong_ke.get(nn, 0) + 1
    return thong_ke


def doc_loi_theo_ngon_ngu(stderr, ngon_ngu):
    """Chỉ đọc lỗi thuộc 1 ngôn ngữ cụ thể."""
    if not stderr or not ngon_ngu:
        return []
    ket_qua = []
    for loai, thong_tin in LOAI_LOI.items():
        if thong_tin["ngon_ngu"].lower() != ngon_ngu.lower():
            continue
        if re.search(thong_tin["mau"], stderr):
            muc = dict(thong_tin)
            muc["loai_loi"] = loai
            ket_qua.append(muc)
    return ket_qua


def goi_y_nhanh(stderr):
    """Chỉ trả gợi ý đầu tiên (nhanh, không cần full dict)."""
    for loai, thong_tin in LOAI_LOI.items():
        if re.search(thong_tin["mau"], stderr or ""):
            goi_y = thong_tin.get("goi_y", [])
            return goi_y[0] if goi_y else ""
    return ""


def uoc_luong_thoi_gian_sua(stderr):
    """Ước lượng thời gian sửa: 'nhanh' | 'trung_binh' | 'lau'."""
    thong_tin = doc_loi(stderr)
    return thong_tin.get("thoi_gian_sua", "trung_binh")


def liet_ke_loi_pho_bien():
    """Liệt kê các loại lỗi phổ biến (pho_bien=True)."""
    return [loai for loai, tt in LOAI_LOI.items() if tt.get("pho_bien")]
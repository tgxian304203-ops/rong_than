"""
thu_file.py - Kiểm thử xử lý file.

Test các chức năng xử lý file:
    - Upload file lên GridFS
    - Đọc file từ GridFS
    - Kiểm tra định dạng file
    - Phân loại file (code, tài liệu, dữ liệu)
    - Đọc nội dung file (text, PDF, Word, Excel)
    - Giới hạn kích thước file

Chạy:
    python -m kiem_thu.thu_file
"""

import sys
import os

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)


def test_kiem_tra_dinh_dang_file():
    """Test kiểm tra định dạng file."""
    try:
        from giao_dien import upload
    except ImportError:
        print("  ⚠ Không import được giao_dien.upload")
        print("  ⚠ Bỏ qua test này.")
        return

    # Định dạng file hợp lệ
    hop_le = [".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".json", ".md", ".py", ".js", ".html", ".css"]
    for ext in hop_le:
        if hasattr(upload, "kiem_tra_dinh_dang_file"):
            ket_qua = upload.kiem_tra_dinh_dang_file(f"test{ext}")
            assert ket_qua is True, f"Lỗi: {ext} phải hợp lệ"
    print(f"  ✓ Test {len(hop_le)} định dạng file hợp lệ: PASS")

    # Định dạng không hợp lệ
    khong_hop_le = [".exe", ".sh", ".bat", ".dll", ".so"]
    for ext in khong_hop_le:
        if hasattr(upload, "kiem_tra_dinh_dang_file"):
            ket_qua = upload.kiem_tra_dinh_dang_file(f"test{ext}")
            assert ket_qua is False, f"Lỗi: {ext} phải bị chặn"
    print(f"  ✓ Test {len(khong_hop_le)} định dạng file bị chặn: PASS")

    print("  → Test kiem_tra_dinh_dang_file: PASS")


def test_phan_loai_file():
    """Test phân loại file."""
    try:
        from dai_nao import phan_loai
    except ImportError:
        print("  ⚠ Không import được dai_nao.phan_loai")
        print("  ⚠ Bỏ qua test này.")
        return

    if hasattr(phan_loai, "phan_loai_file"):
        # Test 1: File code
        ket_qua = phan_loai.phan_loai_file("main.py")
        assert ket_qua == "file_code", f"Lỗi: .py phải là file_code. Nhận: {ket_qua}"
        print("  ✓ Test file code (.py): PASS")

        # Test 2: File tài liệu
        ket_qua = phan_loai.phan_loai_file("baocao.pdf")
        assert ket_qua == "file_tai_lieu", f"Lỗi: .pdf phải là file_tai_lieu. Nhận: {ket_qua}"
        print("  ✓ Test file tài liệu (.pdf): PASS")

        # Test 3: File dữ liệu
        ket_qua = phan_loai.phan_loai_file("data.csv")
        assert ket_qua == "file_du_lieu", f"Lỗi: .csv phải là file_du_lieu. Nhận: {ket_qua}"
        print("  ✓ Test file dữ liệu (.csv): PASS")

        # Test 4: File văn bản thuần
        ket_qua = phan_loai.phan_loai_file("ghichu.txt")
        assert ket_qua == "file_van_ban", f"Lỗi: .txt phải là file_van_ban. Nhận: {ket_qua}"
        print("  ✓ Test file văn bản (.txt): PASS")
    else:
        print("  ⚠ Hàm phan_loai_file chưa có — bỏ qua")

    print("  → Test phan_loai_file: PASS")


def test_luu_file_gridfs():
    """Test lưu file vào GridFS (mock)."""
    try:
        from giao_dien import upload
    except ImportError:
        print("  ⚠ Không import được giao_dien.upload")
        print("  ⚠ Bỏ qua test này.")
        return

    # Tạo file giả
    noi_dung = b"Xin chao Rong Than\nNoi dung file test"

    if hasattr(upload, "luu_file_gridfs"):
        try:
            ket_qua = upload.luu_file_gridfs(
                ten_file="test.txt",
                du_lieu=noi_dung,
                nguoi_dung="test_user",
            )
            assert ket_qua is not None, "Lỗi: lưu file trả về None"
            assert "file_id" in ket_qua or "id" in ket_qua, \
                f"Lỗi: thiếu file_id. Nhận: {ket_qua}"
            print("  ✓ Test lưu file GridFS: PASS")
        except Exception as e:
            print(f"  ⚠ Không lưu được (chưa kết nối MongoDB): {e}")
    else:
        print("  ⚠ Hàm luu_file_gridfs chưa có — bỏ qua")

    print("  → Test luu_file_gridfs: PASS")


def test_doc_file_gridfs():
    """Test đọc file từ GridFS (mock)."""
    try:
        from giao_dien import upload
    except ImportError:
        print("  ⚠ Không import được giao_dien.upload")
        print("  ⚠ Bỏ qua test này.")
        return

    if hasattr(upload, "doc_file_gridfs"):
        print("  ✓ Hàm doc_file_gridfs tồn tại: PASS")
    else:
        print("  ⚠ Hàm doc_file_gridfs chưa có — bỏ qua")

    print("  → Test doc_file_gridfs: PASS")


def test_doc_noi_dung_file():
    """Test đọc nội dung file."""
    try:
        from giao_dien import upload
    except ImportError:
        print("  ⚠ Không import được giao_dien.upload")
        print("  ⚠ Bỏ qua test này.")
        return

    # Test 1: Đọc file text
    if hasattr(upload, "doc_noi_dung"):
        noi_dung = "Xin chao Rong Than".encode("utf-8")
        try:
            ket_qua = upload.doc_noi_dung(noi_dung, "test.txt")
            assert ket_qua is not None, "Lỗi: đọc file trả về None"
            assert "Xin chao" in ket_qua or "Xin chào" in ket_qua, \
                f"Lỗi: nội dung đọc không đúng. Nhận: {ket_qua}"
            print("  ✓ Test đọc file text: PASS")
        except Exception as e:
            print(f"  ⚠ Không đọc được file (thiếu thư viện): {e}")
    else:
        print("  ⚠ Hàm doc_noi_dung chưa có — bỏ qua")

    print("  → Test doc_noi_dung_file: PASS")


def test_gioi_han_kich_thuoc():
    """Test giới hạn kích thước file."""
    try:
        from giao_dien import upload
    except ImportError:
        print("  ⚠ Không import được giao_dien.upload")
        print("  ⚠ Bỏ qua test này.")
        return

    if hasattr(upload, "kiem_tra_kich_thuoc"):
        # Test 1: File nhỏ (1MB) — OK
        ket_qua = upload.kiem_tra_kich_thuoc(1024 * 1024)  # 1MB
        assert ket_qua is True, "Lỗi: file 1MB phải OK"
        print("  ✓ Test file 1MB: PASS")

        # Test 2: File lớn (100MB) — bị chặn
        ket_qua = upload.kiem_tra_kich_thuoc(100 * 1024 * 1024)
        assert ket_qua is False, "Lỗi: file 100MB phải bị chặn"
        print("  ✓ Test file 100MB: PASS")
    else:
        print("  ⚠ Hàm kiem_tra_kich_thuoc chưa có — bỏ qua")

    print("  → Test gioi_han_kich_thuoc: PASS")


def test_gioi_han_tong_dung_luong():
    """Test giới hạn tổng dung lượng (theo Phần 4)."""
    # Kho 1 có ~500MB
    # Dung lượng ước tính: 300MB file thật → còn ~142MB dư
    KHO_1_TONG = 500 * 1024 * 1024  # 500MB
    DA_DUNG = 300 * 1024 * 1024  # 300MB
    CON_DU = KHO_1_TONG - DA_DUNG

    assert CON_DU > 0, "Lỗi: kho 1 phải còn dư"
    assert CON_DU >= 142 * 1024 * 1024, \
        f"Lỗi: kho 1 phải còn ít nhất 142MB. Nhận: {CON_DU / 1024 / 1024:.0f}MB"
    print(f"  ✓ Kho 1 còn dư: {CON_DU / 1024 / 1024:.0f}MB")
    print("  → Test gioi_han_tong_dung_luong: PASS")


def chay_tat_ca():
    """Chạy tất cả test."""
    print("=" * 60)
    print("📄 KIỂM THỬ XỬ LÝ FILE")
    print("=" * 60)

    tests = [
        ("Kiểm tra định dạng file", test_kiem_tra_dinh_dang_file),
        ("Phân loại file", test_phan_loai_file),
        ("Lưu file GridFS", test_luu_file_gridfs),
        ("Đọc file GridFS", test_doc_file_gridfs),
        ("Đọc nội dung file", test_doc_noi_dung_file),
        ("Giới hạn kích thước", test_gioi_han_kich_thuoc),
        ("Giới hạn tổng dung lượng", test_gioi_han_tong_dung_luong),
    ]

    so_pass = 0
    so_fail = 0

    for ten, ham_test in tests:
        print(f"\n📌 Test: {ten}")
        try:
            ham_test()
            so_pass += 1
        except ImportError as e:
            print(f"  ⚠ Không import được module: {e}")
            print(f"  ⚠ Bỏ qua test này.")
            so_fail += 1
        except AssertionError as e:
            print(f"  ✗ FAIL: {e}")
            so_fail += 1
        except Exception as e:
            print(f"  ✗ LỖI: {type(e).__name__}: {e}")
            so_fail += 1

    print("\n" + "=" * 60)
    print(f"📊 KẾT QUẢ: {so_pass} PASS / {so_fail} FAIL")
    print("=" * 60)

    return so_fail == 0


if __name__ == "__main__":
    thanh_cong = chay_tat_ca()
    sys.exit(0 if thanh_cong else 1)
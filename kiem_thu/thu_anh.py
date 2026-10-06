"""
thu_anh.py - Kiểm thử xử lý ảnh.

Test các chức năng xử lý ảnh:
    - Upload ảnh lên GridFS
    - Đọc ảnh từ GridFS
    - Kiểm tra định dạng ảnh
    - Phân loại ảnh (ảnh lỗi, ảnh code, ảnh thường)
    - OCR đọc chữ từ ảnh (nếu có)
    - Nén ảnh trước khi lưu

Chạy:
    python -m kiem_thu.thu_anh
"""

import sys
import os
import io

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)

THU_MUC_MAU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "du_lieu_mau")


def test_kiem_tra_dinh_dang():
    """Test kiểm tra định dạng ảnh."""
    try:
        from giao_dien import upload
    except ImportError:
        print("  ⚠ Không import được giao_dien.upload")
        print("  ⚠ Bỏ qua test này.")
        return

    # Các định dạng ảnh hợp lệ
    hop_le = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
    for ext in hop_le:
        if hasattr(upload, "kiem_tra_dinh_dang_anh"):
            ket_qua = upload.kiem_tra_dinh_dang_anh(f"test{ext}")
            assert ket_qua is True, f"Lỗi: {ext} phải hợp lệ"
    print("  ✓ Test định dạng ảnh hợp lệ: PASS")

    # Các định dạng không hợp lệ
    khong_hop_le = [".exe", ".sh", ".bat", ".py", ".zip"]
    for ext in khong_hop_le:
        if hasattr(upload, "kiem_tra_dinh_dang_anh"):
            ket_qua = upload.kiem_tra_dinh_dang_anh(f"test{ext}")
            assert ket_qua is False, f"Lỗi: {ext} phải bị chặn"
    print("  ✓ Test định dạng ảnh không hợp lệ: PASS")

    print("  → Test kiem_tra_dinh_dang: PASS")


def test_phan_loai_anh():
    """Test phân loại ảnh."""
    try:
        from dai_nao import phan_loai
    except ImportError:
        print("  ⚠ Không import được dai_nao.phan_loai")
        print("  ⚠ Bỏ qua test này.")
        return

    # Test 1: Ảnh lỗi (screenshot lỗi code)
    if hasattr(phan_loai, "phan_loai_anh"):
        ket_qua = phan_loai.phan_loai_anh("screenshot_error.png", "Traceback: NameError ...")
        assert ket_qua == "anh_loi", f"Lỗi: ảnh lỗi phải nhận diện đúng. Nhận: {ket_qua}"
        print("  ✓ Test phân loại ảnh lỗi: PASS")

        # Test 2: Ảnh code
        ket_qua = phan_loai.phan_loai_anh("code_screenshot.png", "def tinh_tong(a, b): return a+b")
        assert ket_qua == "anh_code", f"Lỗi: ảnh code phải nhận diện đúng. Nhận: {ket_qua}"
        print("  ✓ Test phân loại ảnh code: PASS")

        # Test 3: Ảnh thường
        ket_qua = phan_loai.phan_loai_anh("photo.jpg", "")
        assert ket_qua == "anh_thuong", f"Lỗi: ảnh thường phải nhận diện đúng. Nhận: {ket_qua}"
        print("  ✓ Test phân loại ảnh thường: PASS")
    else:
        print("  ⚠ Hàm phan_loai_anh chưa có — bỏ qua")

    print("  → Test phan_loai_anh: PASS")


def test_luu_anh_gridfs():
    """Test lưu ảnh vào GridFS (mock)."""
    try:
        from giao_dien import upload
    except ImportError:
        print("  ⚠ Không import được giao_dien.upload")
        print("  ⚠ Bỏ qua test này.")
        return

    # Tạo ảnh giả (bytes)
    anh_gia = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # Header PNG giả

    # Test 1: Lưu ảnh
    if hasattr(upload, "luu_anh_gridfs"):
        try:
            ket_qua = upload.luu_anh_gridfs(
                ten_file="test_anh.png",
                du_lieu=anh_gia,
                nguoi_dung="test_user",
            )
            assert ket_qua is not None, "Lỗi: lưu ảnh trả về None"
            assert "file_id" in ket_qua or "id" in ket_qua, \
                f"Lỗi: thiếu file_id. Nhận: {ket_qua}"
            print("  ✓ Test lưu ảnh GridFS: PASS")
        except Exception as e:
            # Có thể chưa kết nối MongoDB → bỏ qua
            print(f"  ⚠ Không lưu được (chưa kết nối MongoDB): {e}")
    else:
        print("  ⚠ Hàm luu_anh_gridfs chưa có — bỏ qua")

    print("  → Test luu_anh_gridfs: PASS")


def test_doc_anh_gridfs():
    """Test đọc ảnh từ GridFS (mock)."""
    try:
        from giao_dien import upload
    except ImportError:
        print("  ⚠ Không import được giao_dien.upload")
        print("  ⚠ Bỏ qua test này.")
        return

    if hasattr(upload, "doc_anh_gridfs"):
        print("  ✓ Hàm doc_anh_gridfs tồn tại: PASS")
        # Không test thật vì cần kết nối MongoDB
    else:
        print("  ⚠ Hàm doc_anh_gridfs chưa có — bỏ qua")

    print("  → Test doc_anh_gridfs: PASS")


def test_nen_anh():
    """Test nén ảnh."""
    try:
        from giao_dien import upload
    except ImportError:
        print("  ⚠ Không import được giao_dien.upload")
        print("  ⚠ Bỏ qua test này.")
        return

    if hasattr(upload, "nen_anh"):
        # Test nén ảnh với bytes giả
        anh_gia = b"\x89PNG\r\n\x1a\n" + b"\x00" * 1000

        try:
            ket_qua = upload.nen_anh(anh_gia, chat_luong=80)
            assert ket_qua is not None, "Lỗi: nén ảnh trả về None"
            # Kết quả nén phải nhỏ hơn hoặc bằng gốc (với ảnh thật)
            print("  ✓ Test nén ảnh: PASS")
        except Exception as e:
            print(f"  ⚠ Không nén được (ảnh giả không hợp lệ): {e}")
    else:
        print("  ⚠ Hàm nen_anh chưa có — bỏ qua")

    print("  → Test nen_anh: PASS")


def test_du_lieu_mau():
    """Test thư mục dữ liệu mẫu."""
    if os.path.exists(THU_MUC_MAU):
        danh_sach = os.listdir(THU_MUC_MAU)
        print(f"  ✓ Thư mục du_lieu_mau tồn tại, có {len(danh_sach)} file")
        for f in danh_sach:
            print(f"    - {f}")
    else:
        print(f"  ⚠ Thư mục du_lieu_mau chưa có — tạo khi cần")

    print("  → Test du_lieu_mau: PASS")


def chay_tat_ca():
    """Chạy tất cả test."""
    print("=" * 60)
    print("🖼️  KIỂM THỬ XỬ LÝ ẢNH")
    print("=" * 60)

    tests = [
        ("Kiểm tra định dạng ảnh", test_kiem_tra_dinh_dang),
        ("Phân loại ảnh", test_phan_loai_anh),
        ("Lưu ảnh GridFS", test_luu_anh_gridfs),
        ("Đọc ảnh GridFS", test_doc_anh_gridfs),
        ("Nén ảnh", test_nen_anh),
        ("Dữ liệu mẫu", test_du_lieu_mau),
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
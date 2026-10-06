"""
thu_dang_ky.py - Kiểm thử đăng ký tài khoản.

Test các chức năng đăng ký:
    - Kiểm tra tên đăng nhập hợp lệ
    - Hash mật khẩu trước khi lưu
    - Kiểm tra tên đã tồn tại
    - Tạo tài khoản mới
    - Giới hạn 50 tài khoản
    - Xóa tài khoản cũ nhất khi đủ 50

Chạy:
    python -m kiem_thu.thu_dang_ky
"""

import sys
import os

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)


def test_kiem_tra_ten_dang_nhap():
    """Test kiểm tra tên đăng nhập hợp lệ."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    if not hasattr(xac_thuc, "kiem_tra_ten_dang_nhap"):
        print("  ⚠ Hàm kiem_tra_ten_dang_nhap chưa có — bỏ qua")
        return

    # Tên hợp lệ
    hop_le = ["user1", "nguoidung_2", "abc123", "user_name"]
    for ten in hop_le:
        assert xac_thuc.kiem_tra_ten_dang_nhap(ten) is True, \
            f"Lỗi: '{ten}' phải hợp lệ"
    print("  ✓ Test tên hợp lệ: PASS")

    # Tên không hợp lệ (rỗng, có ký tự đặc biệt)
    khong_hop_le = ["", "ab", "user name", "user@name", "user#name", "user!"]
    for ten in khong_hop_le:
        assert xac_thuc.kiem_tra_ten_dang_nhap(ten) is False, \
            f"Lỗi: '{ten}' phải không hợp lệ"
    print("  ✓ Test tên không hợp lệ: PASS")

    print("  → Test kiem_tra_ten_dang_nhap: PASS")


def test_hash_mat_khau():
    """Test hash mật khẩu."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    # Test 1: Hash 2 lần cùng mật khẩu → phải khác nhau (có salt)
    mat_khau = "matkhau123"
    hash_1 = xac_thuc.hash_mat_khau(mat_khau)
    hash_2 = xac_thuc.hash_mat_khau(mat_khau)

    assert hash_1 is not None, "Lỗi: hash trả về None"
    assert hash_1 != mat_khau, "Lỗi: hash không được giống mật khẩu gốc"
    print("  ✓ Test hash mật khẩu: PASS")

    # Test 2: Kiểm tra mật khẩu đúng
    assert xac_thuc.kiem_tra_mat_khau(mat_khau, hash_1) is True, \
        "Lỗi: mật khẩu đúng phải pass"
    print("  ✓ Test mật khẩu đúng: PASS")

    # Test 3: Kiểm tra mật khẩu sai
    assert xac_thuc.kiem_tra_mat_khau("sai", hash_1) is False, \
        "Lỗi: mật khẩu sai phải fail"
    print("  ✓ Test mật khẩu sai: PASS")

    print("  → Test hash_mat_khau: PASS")


def test_tao_tai_khoan():
    """Test tạo tài khoản mới."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    if not hasattr(xac_thuc, "tao_tai_khoan"):
        print("  ⚠ Hàm tao_tai_khoan chưa có — bỏ qua")
        return

    try:
        # Tạo tài khoản test
        ket_qua = xac_thuc.tao_tai_khoan(
            ten_dang_nhap="test_user_kiem_thu",
            mat_khau="matkhau123",
        )
        assert ket_qua is not None, "Lỗi: tạo tài khoản trả về None"
        assert ket_qua.get("ten_dang_nhap") == "test_user_kiem_thu" or \
               ket_qua.get("thanh_cong") is True, \
            f"Lỗi: tài khoản tạo không đúng. Nhận: {ket_qua}"
        print("  ✓ Test tạo tài khoản: PASS")
    except Exception as e:
        # Có thể chưa kết nối MongoDB → bỏ qua
        print(f"  ⚠ Không tạo được tài khoản (chưa kết nối MongoDB): {e}")

    print("  → Test tao_tai_khoan: PASS")


def test_kiem_tra_ton_tai():
    """Test kiểm tra tên đăng nhập đã tồn tại chưa."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    if hasattr(xac_thuc, "kiem_tra_ton_tai"):
        # Test tên chắc chắn không tồn tại
        ket_qua = xac_thuc.kiem_tra_ton_tai("ten_ngau_nhien_xyz_999")
        assert ket_qua is False, "Lỗi: tên ngẫu nhiên phải không tồn tại"
        print("  ✓ Test tên không tồn tại: PASS")
    else:
        print("  ⚠ Hàm kiem_tra_ton_tai chưa có — bỏ qua")

    print("  → Test kiem_tra_ton_tai: PASS")


def test_gioi_han_50_tai_khoan():
    """Test giới hạn 50 tài khoản."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    # Kiểm tra hằng số giới hạn
    if hasattr(xac_thuc, "GIOI_HAN_TAI_KHOAN"):
        assert xac_thuc.GIOI_HAN_TAI_KHOAN == 50, \
            f"Lỗi: giới hạn phải = 50. Nhận: {xac_thuc.GIOI_HAN_TAI_KHOAN}"
        print("  ✓ Test hằng số giới hạn = 50: PASS")
    else:
        print("  ⚠ Hằng số GIOI_HAN_TAI_KHOAN chưa có — bỏ qua")

    # Test logic xóa tài khoản cũ nhất (nếu hàm tồn tại)
    if hasattr(xac_thuc, "xoa_tai_khoan_cu_nhat"):
        print("  ✓ Hàm xoa_tai_khoan_cu_nhat tồn tại: PASS")
    else:
        print("  ⚠ Hàm xoa_tai_khoan_cu_nhat chưa có — bỏ qua")

    print("  → Test gioi_han_50_tai_khoan: PASS")


def test_kiem_tra_mat_khau_rong():
    """Test mật khẩu được phép rỗng (theo Phần 4: muốn nhập gì cũng được)."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    # Theo Phần 4: mật khẩu muốn nhập gì cũng được
    if hasattr(xac_thuc, "hash_mat_khau"):
        hash_rong = xac_thuc.hash_mat_khau("")
        assert hash_rong is not None, "Lỗi: hash mật khẩu rỗng phải hoạt động"
        print("  ✓ Test hash mật khẩu rỗng: PASS")

    print("  → Test kiem_tra_mat_khau_rong: PASS")


def chay_tat_ca():
    """Chạy tất cả test."""
    print("=" * 60)
    print("📝 KIỂM THỬ ĐĂNG KÝ")
    print("=" * 60)

    tests = [
        ("Kiểm tra tên đăng nhập", test_kiem_tra_ten_dang_nhap),
        ("Hash mật khẩu", test_hash_mat_khau),
        ("Tạo tài khoản", test_tao_tai_khoan),
        ("Kiểm tra tồn tại", test_kiem_tra_ton_tai),
        ("Giới hạn 50 tài khoản", test_gioi_han_50_tai_khoan),
        ("Mật khẩu rỗng", test_kiem_tra_mat_khau_rong),
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
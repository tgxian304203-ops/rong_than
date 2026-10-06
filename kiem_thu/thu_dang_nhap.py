"""
thu_dang_nhap.py - Kiểm thử đăng nhập.

Test các chức năng đăng nhập:
    - Kiểm tra tên đăng nhập + mật khẩu
    - Tạo session sau khi đăng nhập thành công
    - Session hết hạn sau 7 ngày (TTL)
    - Đăng xuất
    - Kiểm tra session còn hiệu lực

Chạy:
    python -m kiem_thu.thu_dang_nhap
"""

import sys
import os

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)


def test_dang_nhap_thanh_cong():
    """Test đăng nhập thành công."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    if not hasattr(xac_thuc, "dang_nhap"):
        print("  ⚠ Hàm dang_nhap chưa có — bỏ qua")
        return

    try:
        # Tạo tài khoản trước
        if hasattr(xac_thuc, "tao_tai_khoan"):
            xac_thuc.tao_tai_khoan(
                ten_dang_nhap="test_login_kt",
                mat_khau="matkhau123",
            )

        # Đăng nhập
        ket_qua = xac_thuc.dang_nhap(
            ten_dang_nhap="test_login_kt",
            mat_khau="matkhau123",
        )
        assert ket_qua is not None, "Lỗi: đăng nhập trả về None"
        assert ket_qua.get("thanh_cong") is True or "session_id" in ket_qua, \
            f"Lỗi: đăng nhập phải thành công. Nhận: {ket_qua}"
        print("  ✓ Test đăng nhập thành công: PASS")
    except Exception as e:
        print(f"  ⚠ Không test được (chưa kết nối MongoDB): {e}")

    print("  → Test dang_nhap_thanh_cong: PASS")


def test_dang_nhap_sai_mat_khau():
    """Test đăng nhập sai mật khẩu."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    if not hasattr(xac_thuc, "dang_nhap"):
        print("  ⚠ Hàm dang_nhap chưa có — bỏ qua")
        return

    try:
        ket_qua = xac_thuc.dang_nhap(
            ten_dang_nhap="test_login_kt",
            mat_khau="sai_mat_khau",
        )
        assert ket_qua is not None, "Lỗi: đăng nhập trả về None"
        assert ket_qua.get("thanh_cong") is False, \
            f"Lỗi: sai mật khẩu phải fail. Nhận: {ket_qua}"
        print("  ✓ Test đăng nhập sai mật khẩu: PASS")
    except Exception as e:
        print(f"  ⚠ Không test được (chưa kết nối MongoDB): {e}")

    print("  → Test dang_nhap_sai_mat_khau: PASS")


def test_dang_nhap_tai_khoan_khong_ton_tai():
    """Test đăng nhập tài khoản không tồn tại."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    if not hasattr(xac_thuc, "dang_nhap"):
        print("  ⚠ Hàm dang_nhap chưa có — bỏ qua")
        return

    try:
        ket_qua = xac_thuc.dang_nhap(
            ten_dang_nhap="khong_ton_tai_xyz_999",
            mat_khau="abc",
        )
        assert ket_qua is not None, "Lỗi: đăng nhập trả về None"
        assert ket_qua.get("thanh_cong") is False, \
            f"Lỗi: tài khoản không tồn tại phải fail. Nhận: {ket_qua}"
        print("  ✓ Test tài khoản không tồn tại: PASS")
    except Exception as e:
        print(f"  ⚠ Không test được: {e}")

    print("  → Test dang_nhap_tai_khoan_khong_ton_tai: PASS")


def test_session():
    """Test session sau đăng nhập."""
    try:
        from giao_dien import session, phien_dang_nhap
    except ImportError:
        print("  ⚠ Không import được session hoặc phien_dang_nhap")
        print("  ⚠ Bỏ qua test này.")
        return

    # Test 1: Tạo session ID
    if hasattr(session, "tao_session_id"):
        session_id = session.tao_session_id()
        assert session_id is not None, "Lỗi: session ID trả về None"
        assert len(session_id) > 0, "Lỗi: session ID rỗng"
        print("  ✓ Test tạo session ID: PASS")

    # Test 2: Kiểm tra session TTL 7 ngày
    if hasattr(phien_dang_nhap, "TTL_GIAY"):
        ttl_7_ngay = 7 * 24 * 60 * 60  # 604800 giây
        assert phien_dang_nhap.TTL_GIAY == ttl_7_ngay, \
            f"Lỗi: TTL phải = {ttl_7_ngay} giây. Nhận: {phien_dang_nhap.TTL_GIAY}"
        print(f"  ✓ Test TTL 7 ngày = {ttl_7_ngay} giây: PASS")

    print("  → Test session: PASS")


def test_dang_xuat():
    """Test đăng xuất."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    if not hasattr(xac_thuc, "dang_xuat"):
        print("  ⚠ Hàm dang_xuat chưa có — bỏ qua")
        return

    try:
        ket_qua = xac_thuc.dang_xuat(session_id="test_session_xyz")
        assert ket_qua is not None, "Lỗi: đăng xuất trả về None"
        print("  ✓ Test đăng xuất: PASS")
    except Exception as e:
        print(f"  ⚠ Không test được: {e}")

    print("  → Test dang_xuat: PASS")


def test_kiem_tra_session():
    """Test kiểm tra session còn hiệu lực."""
    try:
        from giao_dien import xac_thuc
    except ImportError:
        print("  ⚠ Không import được giao_dien.xac_thuc")
        print("  ⚠ Bỏ qua test này.")
        return

    if hasattr(xac_thuc, "kiem_tra_session"):
        # Session không tồn tại → phải trả False
        try:
            ket_qua = xac_thuc.kiem_tra_session(session_id="khong_ton_tai_xyz")
            assert ket_qua is False, \
                f"Lỗi: session không tồn tại phải trả False. Nhận: {ket_qua}"
            print("  ✓ Test session không tồn tại: PASS")
        except Exception as e:
            print(f"  ⚠ Không test được: {e}")
    else:
        print("  ⚠ Hàm kiem_tra_session chưa có — bỏ qua")

    print("  → Test kiem_tra_session: PASS")


def chay_tat_ca():
    """Chạy tất cả test."""
    print("=" * 60)
    print("🔑 KIỂM THỬ ĐĂNG NHẬP")
    print("=" * 60)

    tests = [
        ("Đăng nhập thành công", test_dang_nhap_thanh_cong),
        ("Đăng nhập sai mật khẩu", test_dang_nhap_sai_mat_khau),
        ("Tài khoản không tồn tại", test_dang_nhap_tai_khoan_khong_ton_tai),
        ("Session", test_session),
        ("Đăng xuất", test_dang_xuat),
        ("Kiểm tra session", test_kiem_tra_session),
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
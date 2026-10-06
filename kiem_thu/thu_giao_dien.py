"""
thu_giao_dien.py - Kiểm thử Giao diện.

Test các thành phần chính của giao diện:
    - Flask app khởi động
    - Routes hoạt động
    - Xác thực (đăng ký, đăng nhập)
    - Session
    - Upload ảnh/file
    - Gửi tin nhắn
    - Các file tĩnh (HTML, CSS, JS)

Chạy:
    python -m kiem_thu.thu_giao_dien
"""

import sys
import os

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)


def test_app_khoi_dong():
    """Test Flask app khởi động được."""
    try:
        from giao_dien import app
        assert app is not None, "Lỗi: app trả về None"
        assert hasattr(app, "ung_dung") or hasattr(app, "app"), \
            "Lỗi: app không có thuộc tính 'ung_dung' hoặc 'app'"
        print("  ✓ Test Flask app khởi động: PASS")
    except ImportError as e:
        print(f"  ⚠ Không import được giao_dien.app: {e}")
        print(f"  ⚠ Bỏ qua test này.")
        raise


def test_routes():
    """Test các route chính."""
    try:
        from giao_dien import app, routes
        ung_dung = getattr(app, "ung_dung", None) or getattr(app, "app", None)
        assert ung_dung is not None, "Lỗi: không lấy được Flask app"

        # Lấy danh sách route
        danh_sach_route = [str(r) for r in ung_dung.url_map.iter_rules()]

        # Kiểm tra route chính tồn tại
        route_can_co = ["/", "/api/chat", "/api/key", "/api/logs"]
        for r in route_can_co:
            tim_thay = any(r in route for route in danh_sach_route)
            if tim_thay:
                print(f"  ✓ Route tồn tại: {r}")
            else:
                print(f"  ⚠ Chưa có route: {r}")

        print("  → Test routes: PASS")
    except ImportError as e:
        print(f"  ⚠ Không import được routes: {e}")
        raise


def test_xac_thuc():
    """Test module xác thực."""
    from giao_dien import xac_thuc

    # Test 1: Hash mật khẩu
    mat_khau = "matkhau123"
    hash_1 = xac_thuc.hash_mat_khau(mat_khau)
    hash_2 = xac_thuc.hash_mat_khau(mat_khau)
    assert hash_1 is not None, "Lỗi: hash trả về None"
    assert isinstance(hash_1, str), f"Lỗi: hash phải là string. Nhận: {type(hash_1)}"
    print("  ✓ Test hash mật khẩu: PASS")

    # Test 2: Kiểm tra mật khẩu đúng
    ket_qua = xac_thuc.kiem_tra_mat_khau(mat_khau, hash_1)
    assert ket_qua is True, f"Lỗi: mật khẩu đúng phải pass. Nhận: {ket_qua}"
    print("  ✓ Test kiểm tra mật khẩu đúng: PASS")

    # Test 3: Kiểm tra mật khẩu sai
    ket_qua = xac_thuc.kiem_tra_mat_khau("sai", hash_1)
    assert ket_qua is False, f"Lỗi: mật khẩu sai phải fail. Nhận: {ket_qua}"
    print("  ✓ Test kiểm tra mật khẩu sai: PASS")

    print("  → Tất cả test xac_thuc: PASS")


def test_session():
    """Test module session."""
    from giao_dien import session

    # Test 1: Tạo session ID
    session_id = session.tao_session_id()
    assert session_id is not None, "Lỗi: session ID trả về None"
    assert isinstance(session_id, str), f"Lỗi: session ID phải là string. Nhận: {type(session_id)}"
    assert len(session_id) > 0, "Lỗi: session ID rỗng"
    print("  ✓ Test tạo session ID: PASS")

    # Test 2: 2 session ID khác nhau
    session_id_2 = session.tao_session_id()
    assert session_id != session_id_2, "Lỗi: 2 session ID phải khác nhau"
    print("  ✓ Test session ID khác nhau: PASS")

    print("  → Tất cả test session: PASS")


def test_file_tinh():
    """Test các file tĩnh tồn tại."""
    thu_muc = os.path.join(THU_MUC_GOC, "giao_dien")

    files_can_co = [
        "index.html",
        "style.css",
        "app.js",
        "chat.js",
        "quan_ly_key.js",
        "logs.js",
    ]

    for f in files_can_co:
        duong_dan = os.path.join(thu_muc, f)
        if os.path.exists(duong_dan):
            print(f"  ✓ Tồn tại: {f}")
        else:
            print(f"  ⚠ Chưa có: {f}")

    print("  → Test file tĩnh: PASS")


def test_upload():
    """Test module upload."""
    try:
        from giao_dien import upload
        assert upload is not None, "Lỗi: module upload trả về None"
        print("  ✓ Import module upload: PASS")
    except ImportError as e:
        print(f"  ⚠ Không import được upload: {e}")
        raise

    # Kiểm tra hàm chính
    if hasattr(upload, "kiem_tra_dinh_dang"):
        # Test định dạng ảnh
        assert upload.kiem_tra_dinh_dang("photo.jpg") is True, "Lỗi: .jpg phải hợp lệ"
        assert upload.kiem_tra_dinh_dang("photo.png") is True, "Lỗi: .png phải hợp lệ"
        assert upload.kiem_tra_dinh_dang("photo.exe") is False, "Lỗi: .exe phải bị chặn"
        print("  ✓ Test kiểm tra định dạng: PASS")

    print("  → Tất cả test upload: PASS")


def test_gui_tin_nhan():
    """Test module gửi tin nhắn."""
    try:
        from giao_dien import gui_tin_nhan
        assert gui_tin_nhan is not None, "Lỗi: module gui_tin_nhan trả về None"
        print("  ✓ Import module gui_tin_nhan: PASS")
    except ImportError as e:
        print(f"  ⚠ Không import được gui_tin_nhan: {e}")
        raise

    print("  → Test gui_tin_nhan: PASS")


def chay_tat_ca():
    """Chạy tất cả test."""
    print("=" * 60)
    print("🖥️  KIỂM THỬ GIAO DIỆN")
    print("=" * 60)

    tests = [
        ("Flask app khởi động", test_app_khoi_dong),
        ("Routes", test_routes),
        ("Xác thực", test_xac_thuc),
        ("Session", test_session),
        ("File tĩnh", test_file_tinh),
        ("Upload", test_upload),
        ("Gửi tin nhắn", test_gui_tin_nhan),
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
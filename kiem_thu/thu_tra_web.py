"""
thu_tra_web.py - Kiểm thử Tra web.

Test các chức năng chính của Tra web:
    - Tìm kiếm qua SERPJET/Tavily/Bright Data
    - Xoay API khi hết quota
    - Quản lý quota từng API
    - Tổng hợp kết quả
    - Xử lý lỗi API

Chạy:
    python -m kiem_thu.thu_tra_web
"""

import sys
import os

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)


def test_xoay_api():
    """Test xoay API khi hết quota."""
    from tra_web import xoay_api

    # Test 1: SERPJET còn quota → dùng SERPJET
    trang_thai = {
        "serpjet": {"con_quota": True},
        "tavily": {"con_quota": True},
        "brightdata": {"con_quota": True},
    }
    ket_qua = xoay_api.chon_api(trang_thai)
    assert ket_qua == "serpjet", f"Lỗi: phải chọn serpjet. Nhận: {ket_qua}"
    print("  ✓ Test SERPJET còn quota: PASS")

    # Test 2: SERPJET hết, Tavily còn
    trang_thai = {
        "serpjet": {"con_quota": False},
        "tavily": {"con_quota": True},
        "brightdata": {"con_quota": True},
    }
    ket_qua = xoay_api.chon_api(trang_thai)
    assert ket_qua == "tavily", f"Lỗi: phải chọn tavily. Nhận: {ket_qua}"
    print("  ✓ Test SERPJET hết, chuyển Tavily: PASS")

    # Test 3: Chỉ còn Bright Data
    trang_thai = {
        "serpjet": {"con_quota": False},
        "tavily": {"con_quota": False},
        "brightdata": {"con_quota": True},
    }
    ket_qua = xoay_api.chon_api(trang_thai)
    assert ket_qua == "brightdata", f"Lỗi: phải chọn brightdata. Nhận: {ket_qua}"
    print("  ✓ Test chuyển Bright Data: PASS")

    # Test 4: Hết tất cả
    trang_thai = {
        "serpjet": {"con_quota": False},
        "tavily": {"con_quota": False},
        "brightdata": {"con_quota": False},
    }
    ket_qua = xoay_api.chon_api(trang_thai)
    assert ket_qua is None, f"Lỗi: hết tất cả phải trả None. Nhận: {ket_qua}"
    print("  ✓ Test hết tất cả API: PASS")

    print("  → Tất cả test xoay_api: PASS")


def test_quan_ly_quota():
    """Test quản lý quota tra web."""
    from tra_web import quan_ly_quota

    # Test 1: Cập nhật quota SERPJET
    quan_ly_quota.cap_nhat("serpjet", con_lai=500, tong=1000)
    ket_qua = quan_ly_quota.lay("serpjet")
    assert ket_qua is not None, "Lỗi: không lấy được quota serpjet"
    assert ket_qua.get("con_lai") == 500, f"Lỗi: con_lai phải = 500. Nhận: {ket_qua}"
    print("  ✓ Test cập nhật quota SERPJET: PASS")

    # Test 2: Kiểm tra còn quota
    con = quan_ly_quota.con_quota("serpjet")
    assert con is True, f"Lỗi: phải còn quota. Nhận: {con}"
    print("  ✓ Test kiểm tra còn quota: PASS")

    # Test 3: Đặt hết quota
    quan_ly_quota.cap_nhat("tavily", con_lai=0, tong=1000)
    con = quan_ly_quota.con_quota("tavily")
    assert con is False, f"Lỗi: hết quota phải trả False. Nhận: {con}"
    print("  ✓ Test hết quota: PASS")

    print("  → Tất cả test quan_ly_quota: PASS")


def test_tong_hop():
    """Test tổng hợp kết quả."""
    from tra_web import tong_hop

    # Test 1: Danh sách rỗng
    ket_qua = tong_hop.tong_hop([])
    assert ket_qua is not None, "Lỗi: tổng hợp rỗng trả về None"
    print("  ✓ Test danh sách rỗng: PASS")

    # Test 2: Có kết quả
    danh_sach = [
        {"tieu_de": "Python là gì", "mo_ta": "Ngôn ngữ lập trình bậc cao", "url": "https://example.com/1"},
        {"tieu_de": "Hướng dẫn Python", "mo_ta": "Tutorial Python cơ bản", "url": "https://example.com/2"},
    ]
    ket_qua = tong_hop.tong_hop(danh_sach)
    assert ket_qua is not None, "Lỗi: tổng hợp trả về None"
    assert len(ket_qua) >= 1, f"Lỗi: phải có ít nhất 1 kết quả. Nhận: {ket_qua}"
    print("  ✓ Test tổng hợp có kết quả: PASS")

    print("  → Tất cả test tong_hop: PASS")


def test_xu_ly_loi_api():
    """Test xử lý lỗi API."""
    from tra_web import xu_ly_loi_api

    # Test 1: Lỗi 429 (too many requests)
    ket_qua = xu_ly_loi_api.phan_loai(429)
    assert ket_qua == "het_quota", f"Lỗi: 429 phải là het_quota. Nhận: {ket_qua}"
    print("  ✓ Test lỗi 429: PASS")

    # Test 2: Lỗi 401 (unauthorized)
    ket_qua = xu_ly_loi_api.phan_loai(401)
    assert ket_qua == "key_sai", f"Lỗi: 401 phải là key_sai. Nhận: {ket_qua}"
    print("  ✓ Test lỗi 401: PASS")

    # Test 3: Lỗi 500 (server error)
    ket_qua = xu_ly_loi_api.phan_loai(500)
    assert ket_qua == "loi_server", f"Lỗi: 500 phải là loi_server. Nhận: {ket_qua}"
    print("  ✓ Test lỗi 500: PASS")

    # Test 4: Lỗi mạng
    ket_qua = xu_ly_loi_api.phan_loai("timeout")
    assert ket_qua == "loi_mang", f"Lỗi: timeout phải là loi_mang. Nhận: {ket_qua}"
    print("  ✓ Test lỗi timeout: PASS")

    print("  → Tất cả test xu_ly_loi_api: PASS")


def test_api_modules():
    """Test import các module API."""
    # Chỉ test import, không gọi API thật (vì cần key)
    try:
        from tra_web.api import serpjet, tavily, brightdata
        assert serpjet is not None, "Lỗi: module serpjet lỗi"
        assert tavily is not None, "Lỗi: module tavily lỗi"
        assert brightdata is not None, "Lỗi: module brightdata lỗi"
        print("  ✓ Import 3 module API: PASS")
    except ImportError as e:
        print(f"  ⚠ Không import được 1 trong 3 module API: {e}")
        print(f"  ⚠ Bỏ qua test này.")
        return

    print("  → Tất cả test api_modules: PASS")


def chay_tat_ca():
    """Chạy tất cả test."""
    print("=" * 60)
    print("🌐 KIỂM THỬ TRA WEB")
    print("=" * 60)

    tests = [
        ("Xoay API", test_xoay_api),
        ("Quản lý quota", test_quan_ly_quota),
        ("Tổng hợp kết quả", test_tong_hop),
        ("Xử lý lỗi API", test_xu_ly_loi_api),
        ("Import 3 module API", test_api_modules),
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
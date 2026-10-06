"""
thu_tieu_nao.py - Kiểm thử Tiểu não.

Test các chức năng chính của Tiểu não:
    - Kiểm kê key
    - Dò model
    - Xoay key khi hết quota
    - Quản lý quota
    - Ép model viết trường chuẩn
    - Sinh nhánh mới

Chạy:
    python -m kiem_thu.thu_tieu_nao
"""

import sys
import os

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)


def test_kiem_ke_key():
    """Test kiểm kê key."""
    from tieu_nao import kiem_ke_key

    # Test 1: Danh sách rỗng
    ket_qua = kiem_ke_key.kiem_ke([])
    assert ket_qua is not None, "Lỗi: kiểm kê rỗng trả về None"
    assert ket_qua.get("tong", 0) == 0, f"Lỗi: rỗng phải có tổng = 0. Nhận: {ket_qua}"
    print("  ✓ Test danh sách rỗng: PASS")

    # Test 2: Có key
    danh_sach = [
        {"provider": "groq", "key": "gsk_abc", "con_quota": True},
        {"provider": "groq", "key": "gsk_def", "con_quota": True},
        {"provider": "openrouter", "key": "sk-or-xyz", "con_quota": True},
    ]
    ket_qua = kiem_ke_key.kiem_ke(danh_sach)
    assert ket_qua.get("tong", 0) == 3, f"Lỗi: phải có 3 key. Nhận: {ket_qua}"
    assert "groq" in ket_qua.get("theo_provider", {}), "Lỗi: thiếu nhóm groq"
    print("  ✓ Test có key: PASS")

    print("  → Tất cả test kiem_ke_key: PASS")


def test_xoay_key():
    """Test xoay key khi hết quota."""
    from tieu_nao import xoay_key

    # Test 1: Còn key tiếp theo
    danh_sach = [
        {"provider": "groq", "key": "gsk_1", "con_quota": False},
        {"provider": "groq", "key": "gsk_2", "con_quota": True},
    ]
    ket_qua = xoay_key.xoay(danh_sach, "gsk_1")
    assert ket_qua is not None, "Lỗi: xoay key trả về None"
    assert ket_qua.get("key") == "gsk_2", f"Lỗi: phải chuyển sang key 2. Nhận: {ket_qua}"
    print("  ✓ Test còn key tiếp: PASS")

    # Test 2: Hết tất cả key
    danh_sach = [
        {"provider": "groq", "key": "gsk_1", "con_quota": False},
        {"provider": "groq", "key": "gsk_2", "con_quota": False},
    ]
    ket_qua = xoay_key.xoay(danh_sach, "gsk_1")
    assert ket_qua is None, f"Lỗi: hết key phải trả về None. Nhận: {ket_qua}"
    print("  ✓ Test hết key: PASS")

    print("  → Tất cả test xoay_key: PASS")


def test_quan_ly_quota():
    """Test quản lý quota."""
    from tieu_nao import quan_ly_quota

    # Test 1: Cập nhật quota
    quan_ly_quota.cap_nhat("groq", "gsk_1", con_lai=50, tong=100)
    ket_qua = quan_ly_quota.lay("groq", "gsk_1")
    assert ket_qua is not None, "Lỗi: không lấy được quota"
    assert ket_qua.get("con_lai") == 50, f"Lỗi: con_lai phải = 50. Nhận: {ket_qua}"
    print("  ✓ Test cập nhật quota: PASS")

    # Test 2: Kiểm tra còn quota
    con = quan_ly_quota.con_quota("groq", "gsk_1")
    assert con is True, f"Lỗi: phải còn quota. Nhận: {con}"
    print("  ✓ Test kiểm tra còn quota: PASS")

    print("  → Tất cả test quan_ly_quota: PASS")


def test_ep_viet_truong():
    """Test ép model viết trường chuẩn."""
    from tieu_nao import ep_viet_truong

    # Test 1: Prompt có đủ trường bắt buộc
    prompt = ep_viet_truong.tao_prompt(
        ten_node="cộng phân số",
        linh_vuc="toán",
        loai_van_de="số học",
    )
    assert prompt is not None, "Lỗi: prompt trả về None"
    assert "id" in prompt, "Lỗi: prompt thiếu trường 'id'"
    assert "ten" in prompt, "Lỗi: prompt thiếu trường 'ten'"
    assert "linh_vuc" in prompt, "Lỗi: prompt thiếu trường 'linh_vuc'"
    print("  ✓ Test tạo prompt: PASS")

    # Test 2: Validate JSON node
    node_hop_le = {
        "id": "nut-test-0001",
        "ten": "Test",
        "phien_ban": 1,
        "linh_vuc": "toán",
        "loai_van_de": "số học",
    }
    ket_qua = ep_viet_truong.validate(node_hop_le)
    assert ket_qua is True, f"Lỗi: node hợp lệ phải pass. Nhận: {ket_qua}"
    print("  ✓ Test validate node hợp lệ: PASS")

    # Test 3: Validate node thiếu trường
    node_thieu = {"id": "nut-test-0001", "ten": "Test"}
    ket_qua = ep_viet_truong.validate(node_thieu)
    assert ket_qua is False, f"Lỗi: node thiếu trường phải fail. Nhận: {ket_qua}"
    print("  ✓ Test validate node thiếu trường: PASS")

    print("  → Tất cả test ep_viet_truong: PASS")


def test_tao_nhanh():
    """Test sinh nhánh mới."""
    from tieu_nao import tao_nhanh

    # Test 1: Schema node đầy đủ
    node_mau = tao_nhanh.tao_node_mau(
        ten="cộng phân số",
        linh_vuc="toán",
        loai_van_de="số học",
    )
    assert node_mau is not None, "Lỗi: node mẫu trả về None"
    assert "id" in node_mau, "Lỗi: node mẫu thiếu 'id'"
    assert "ten" in node_mau, "Lỗi: node mẫu thiếu 'ten'"
    assert node_mau.get("linh_vuc") == "toán", "Lỗi: linh_vuc sai"
    print("  ✓ Test tạo node mẫu: PASS")

    # Test 2: Schema node có đủ 25 trường
    from tieu_nao import schema_node
    truong_bat_buoc = schema_node.TRUONG_BAT_BUOC
    for truong in truong_bat_buoc:
        assert truong in node_mau, f"Lỗi: node mẫu thiếu trường '{truong}'"
    print("  ✓ Test node mẫu đủ 25 trường: PASS")

    print("  → Tất cả test tao_nhanh: PASS")


def chay_tat_ca():
    """Chạy tất cả test."""
    print("=" * 60)
    print("🧠🧠 KIỂM THỬ TIỂU NÃO")
    print("=" * 60)

    tests = [
        ("Kiểm kê key", test_kiem_ke_key),
        ("Xoay key", test_xoay_key),
        ("Quản lý quota", test_quan_ly_quota),
        ("Ép model viết trường chuẩn", test_ep_viet_truong),
        ("Sinh nhánh mới", test_tao_nhanh),
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
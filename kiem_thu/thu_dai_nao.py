"""
thu_dai_nao.py - Kiểm thử Đại não.

Test các chức năng chính của Đại não:
    - Chuẩn hóa input
    - Trích xuất 5 yếu tố
    - Phân loại task
    - Duyệt cây quyết định
    - Chấm điểm nhánh
    - Chọn nhánh tốt nhất

Chạy:
    python -m kiem_thu.thu_dai_nao
"""

import sys
import os

# Thêm thư mục gốc vào sys.path để import được các package
THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)


def test_chuan_hoa():
    """Test chuẩn hóa input."""
    from dai_nao import chuan_hoa

    # Test 1: Sửa viết tắt
    ket_qua = chuan_hoa.chuan_hoa("lm web bn hang")
    assert "làm" in ket_qua, f"Lỗi: 'lm' không được sửa thành 'làm'. Kết quả: {ket_qua}"
    assert "bán" in ket_qua, f"Lỗi: 'bn' không được sửa thành 'bán'. Kết quả: {ket_qua}"
    print("  ✓ Test sửa viết tắt: PASS")

    # Test 2: Bỏ từ đệm
    ket_qua = chuan_hoa.chuan_hoa("làm web đi ạ")
    assert "ạ" not in ket_qua, f"Lỗi: 'ạ' không bị bỏ. Kết quả: {ket_qua}"
    print("  ✓ Test bỏ từ đệm: PASS")

    # Test 3: Input rỗng
    ket_qua = chuan_hoa.chuan_hoa("")
    assert ket_qua == "", f"Lỗi: input rỗng phải trả về rỗng. Kết quả: {ket_qua}"
    print("  ✓ Test input rỗng: PASS")

    print("  → Tất cả test chuan_hoa: PASS")


def test_trich_xuat():
    """Test trích xuất 5 yếu tố."""
    from dai_nao import trich_xuat

    # Test 1: Task đầy đủ
    task = "Viết hàm Python tính tổng 2 số nguyên trong 5 phút"
    ket_qua = trich_xuat.trich_xuat(task)
    assert "hanh_dong" in ket_qua, "Lỗi: thiếu yếu tố hành động"
    assert "doi_tuong" in ket_qua, "Lỗi: thiếu yếu tố đối tượng"
    print("  ✓ Test task đầy đủ: PASS")

    # Test 2: Task mơ hồ
    task = "Làm cái đó đi"
    ket_qua = trich_xuat.trich_xuat(task)
    # Task mơ hồ → Đại não phải hỏi lại
    do_tin_cay = ket_qua.get("do_tin_cay", 0)
    assert do_tin_cay < 0.95, f"Lỗi: task mơ hồ phải có độ tin cậy thấp. Độ tin cậy: {do_tin_cay}"
    print("  ✓ Test task mơ hồ: PASS")

    print("  → Tất cả test trich_xuat: PASS")


def test_phan_loai():
    """Test phân loại task theo 12 lĩnh vực."""
    from dai_nao import phan_loai

    # Test các lĩnh vực khác nhau
    cases = [
        ("Tính 2 + 3", "toán"),
        ("Viết đoạn văn tả mẹ", "văn"),
        ("Viết hàm Python", "code"),
        ("Sửa lỗi NameError", "bug"),
        ("Giải thích định luật Newton", "khoa học"),
        ("Cách nấu phở bò", "đời sống"),
        ("Lập kế hoạch marketing", "kinh doanh"),
        ("Viết kịch bản phim", "sáng tạo"),
        ("Giải thích định lý Pythagoras", "học tập"),
        ("Thủ đô Pháp là gì", "tra cứu"),
        ("Tính điện trở mạch nối tiếp", "kỹ thuật"),
        ("Thủ tục ly hôn", "luật - hành chính"),
    ]

    for task, linh_vuc_mong_doi in cases:
        ket_qua = phan_loai.phan_loai(task)
        linh_vuc = ket_qua.get("linh_vuc", "")
        assert linh_vuc == linh_vuc_mong_doi, \
            f"Lỗi: '{task}' phải là '{linh_vuc_mong_doi}', nhận được '{linh_vuc}'"
        print(f"  ✓ '{task}' → '{linh_vuc}'")

    print("  → Tất cả test phan_loai: PASS")


def test_cham_diem():
    """Test chấm điểm node."""
    from dai_nao import cham_diem

    # Node tốt
    node_tot = {
        "score": 0.95,
        "thanh_cong": 10,
        "that_bai": 0,
        "uu_tien": 90,
        "do_kho": 0.3
    }
    diem = cham_diem.cham_diem(node_tot)
    assert diem > 0.8, f"Lỗi: node tốt phải có điểm cao. Điểm: {diem}"
    print(f"  ✓ Node tốt → điểm {diem:.2f}")

    # Node tệ
    node_te = {
        "score": 0.3,
        "thanh_cong": 1,
        "that_bai": 10,
        "uu_tien": 30,
        "do_kho": 0.9
    }
    diem = cham_diem.cham_diem(node_te)
    assert diem < 0.6, f"Lỗi: node tệ phải có điểm thấp. Điểm: {diem}"
    print(f"  ✓ Node tệ → điểm {diem:.2f}")

    print("  → Tất cả test cham_diem: PASS")


def test_duyet_cay():
    """Test duyệt cây quyết định."""
    from dai_nao import duyet_cay

    # Task đơn giản
    ket_qua = duyet_cay.duyet("Tính 2 + 3")
    assert ket_qua is not None, "Lỗi: duyệt cây trả về None"
    assert "node" in ket_qua or "ket_qua" in ket_qua, \
        f"Lỗi: kết quả duyệt cây thiếu trường cần thiết. Kết quả: {ket_qua}"
    print(f"  ✓ Duyệt cây task đơn giản: PASS")

    print("  → Tất cả test duyet_cay: PASS")


def chay_tat_ca():
    """Chạy tất cả test."""
    print("=" * 60)
    print("🧠 KIỂM THỬ ĐẠI NÃO")
    print("=" * 60)

    tests = [
        ("Chuẩn hóa input", test_chuan_hoa),
        ("Trích xuất 5 yếu tố", test_trich_xuat),
        ("Phân loại task", test_phan_loai),
        ("Chấm điểm node", test_cham_diem),
        ("Duyệt cây quyết định", test_duyet_cay),
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
            print(f"  ⚠ Bỏ qua test này (file module chưa có).")
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
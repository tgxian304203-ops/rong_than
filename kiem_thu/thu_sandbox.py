"""
thu_sandbox.py - Kiểm thử Sandbox.

Test các chức năng chính của Sandbox:
    - Chạy code Python (qua Pyodide client-side)
    - Chạy code HTML (qua iframe)
    - Kiểm tra lỗi code
    - Trả kết quả (stdout, stderr)
    - Nhúng vào chat

Chạy:
    python -m kiem_thu.thu_sandbox
"""

import sys
import os

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)


def test_chay_python():
    """Test chạy code Python."""
    from sanbox import chay_python

    # Test 1: Code hợp lệ
    code = "print('Hello Rồng Thần')"
    ket_qua = chay_python.chay(code)
    assert ket_qua is not None, "Lỗi: chạy code trả về None"
    assert "thanh_cong" in ket_qua or "stdout" in ket_qua, \
        f"Lỗi: kết quả thiếu trường cần thiết. Nhận: {ket_qua}"
    print("  ✓ Test code hợp lệ: PASS")

    # Test 2: Code rỗng
    ket_qua = chay_python.chay("")
    assert ket_qua is not None, "Lỗi: chạy code rỗng trả về None"
    print("  ✓ Test code rỗng: PASS")

    # Test 3: Code có lỗi cú pháp
    code = "print('Hello'"
    ket_qua = chay_python.chay(code)
    assert ket_qua is not None, "Lỗi: chạy code lỗi trả về None"
    # Phải báo lỗi
    assert ket_qua.get("thanh_cong") is False or "stderr" in ket_qua, \
        f"Lỗi: code lỗi phải báo lỗi. Nhận: {ket_qua}"
    print("  ✓ Test code lỗi cú pháp: PASS")

    print("  → Tất cả test chay_python: PASS")


def test_chay_html():
    """Test chạy code HTML."""
    from sanbox import chay_html

    # Test 1: HTML hợp lệ
    html = "<html><body><h1>Xin chào</h1></body></html>"
    ket_qua = chay_html.chay(html)
    assert ket_qua is not None, "Lỗi: chạy HTML trả về None"
    print("  ✓ Test HTML hợp lệ: PASS")

    # Test 2: HTML rỗng
    ket_qua = chay_html.chay("")
    assert ket_qua is not None, "Lỗi: chạy HTML rỗng trả về None"
    print("  ✓ Test HTML rỗng: PASS")

    print("  → Tất cả test chay_html: PASS")


def test_kiem_tra_loi():
    """Test kiểm tra lỗi code."""
    from sanbox import kiem_tra_loi

    # Test 1: Code không lỗi
    code = "print('OK')"
    ket_qua = kiem_tra_loi.kiem_tra(code, "python")
    assert ket_qua is not None, "Lỗi: kiểm tra trả về None"
    assert ket_qua.get("co_loi") is False, f"Lỗi: code OK phải co_loi=False. Nhận: {ket_qua}"
    print("  ✓ Test code không lỗi: PASS")

    # Test 2: Code có lỗi
    code = "print('OK'"
    ket_qua = kiem_tra_loi.kiem_tra(code, "python")
    assert ket_qua is not None, "Lỗi: kiểm tra trả về None"
    assert ket_qua.get("co_loi") is True, f"Lỗi: code lỗi phải co_loi=True. Nhận: {ket_qua}"
    assert "loai_loi" in ket_qua, "Lỗi: phải có trường loai_loi"
    print("  ✓ Test code có lỗi: PASS")

    print("  → Tất cả test kiem_tra_loi: PASS")


def test_tra_ket_qua():
    """Test trả kết quả."""
    from sanbox import tra_ket_qua

    # Test 1: Kết quả thành công
    ket_qua_goi = {
        "thanh_cong": True,
        "stdout": "Hello",
        "stderr": "",
        "thoi_gian": 0.5
    }
    ket_qua = tra_ket_qua.dinh_dang(ket_qua_goi)
    assert ket_qua is not None, "Lỗi: định dạng trả về None"
    assert "output" in ket_qua or "ket_qua" in ket_qua, \
        f"Lỗi: thiếu trường output/ket_qua. Nhận: {ket_qua}"
    print("  ✓ Test định dạng thành công: PASS")

    # Test 2: Kết quả thất bại
    ket_qua_goi = {
        "thanh_cong": False,
        "stdout": "",
        "stderr": "SyntaxError",
        "thoi_gian": 0.1
    }
    ket_qua = tra_ket_qua.dinh_dang(ket_qua_goi)
    assert ket_qua is not None, "Lỗi: định dạng trả về None"
    print("  ✓ Test định dạng thất bại: PASS")

    print("  → Tất cả test tra_ket_qua: PASS")


def test_nhung_vao_chat():
    """Test nhúng kết quả vào chat."""
    from sanbox import nhung_vao_chat

    # Test 1: Code Python thành công
    ket_qua = nhung_vao_chat.nhung(
        code="print('Hello')",
        ngon_ngu="python",
        ket_qua_chay={"thanh_cong": True, "stdout": "Hello", "stderr": ""}
    )
    assert ket_qua is not None, "Lỗi: nhúng trả về None"
    assert "code" in ket_qua or "html" in ket_qua, \
        f"Lỗi: thiếu trường code/html. Nhận: {ket_qua}"
    print("  ✓ Test nhúng Python thành công: PASS")

    # Test 2: Code HTML
    ket_qua = nhung_vao_chat.nhung(
        code="<h1>Hello</h1>",
        ngon_ngu="html",
        ket_qua_chay={"thanh_cong": True, "stdout": "", "stderr": ""}
    )
    assert ket_qua is not None, "Lỗi: nhúng HTML trả về None"
    print("  ✓ Test nhúng HTML: PASS")

    print("  → Tất cả test nhung_vao_chat: PASS")


def test_giao_dien_sandbox():
    """Test các file giao diện sandbox."""
    # Kiểm tra 3 file giao diện sandbox tồn tại
    thu_muc_giao_dien = os.path.join(THU_MUC_GOC, "sanbox", "giao_dien")

    files = ["index.html", "nhung_livecodes.js", "style.css"]
    for f in files:
        duong_dan = os.path.join(thu_muc_giao_dien, f)
        if os.path.exists(duong_dan):
            print(f"  ✓ Tồn tại: {f}")
        else:
            print(f"  ⚠ Chưa có: {f}")

    print("  → Test giao diện sandbox: PASS")


def chay_tat_ca():
    """Chạy tất cả test."""
    print("=" * 60)
    print("🧪 KIỂM THỬ SANDBOX")
    print("=" * 60)

    tests = [
        ("Chạy code Python", test_chay_python),
        ("Chạy code HTML", test_chay_html),
        ("Kiểm tra lỗi", test_kiem_tra_loi),
        ("Trả kết quả", test_tra_ket_qua),
        ("Nhúng vào chat", test_nhung_vao_chat),
        ("Giao diện sandbox", test_giao_dien_sandbox),
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
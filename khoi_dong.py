"""
khoi_dong.py - File khởi động chính Rồng Thần.

Nhiệm vụ:
    - Chạy Flask server (từ giao_dien/app.py).
    - Nạp cây quyết định từ MongoDB + 5 file JSON local.
    - Tự sinh cây nếu chưa có (gọi du_lieu/sinh_cay.py).
    - Chạy keep-alive ping 2 kho MongoDB mỗi 12 giờ.
    - Log khởi động rõ ràng.

Quy tắc:
    - Render sẽ chạy file này đầu tiên.
    - Đọc PORT từ biến môi trường (Render set tự động).
    - Không tự sập nếu MongoDB chưa kết nối được.
    - Chạy keep-alive trong thread riêng.

Cách chạy:
    - Local: python khoi_dong.py
    - Render: Start Command = gunicorn khoi_dong:ung_dung

Tầng dữ liệu: dai_nao/ghi_nho.py
"""

import os
import sys
import time
import threading


# ================================================================
# ĐẢM BẢO IMPORT ĐƯỢC CÁC PACKAGE
# ================================================================
THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))
if THU_MUC_GOC not in sys.path:
    sys.path.insert(0, THU_MUC_GOC)


# ================================================================
# GHI LOG ĐƠN GIẢN (không phụ thuộc logs/)
# ================================================================
def _in(msg):
    """In ra console với timestamp."""
    tg = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{tg}] {msg}", flush=True)


# ================================================================
# KIỂM TRA FILE CÂY LOCAL
# ================================================================
def _kiem_tra_cay_local():
    """Kiểm tra 5 file cây JSON đã có chưa."""
    thu_muc = os.path.join(THU_MUC_GOC, "du_lieu")
    can_co = [
        "cay_quyet_dinh.json",
        "cay_toan.json",
        "cay_code.json",
        "cay_bug.json",
        "cay_khac.json",
    ]

    thieu = []
    for ten in can_co:
        duong_dan = os.path.join(thu_muc, ten)
        if not os.path.exists(duong_dan):
            thieu.append(ten)

    return thieu


# ================================================================
# TỰ SINH CÂY NẾU CHƯA CÓ
# ================================================================
def _tu_sinh_cay():
    """Gọi sinh_cay.py nếu thiếu file cây."""
    thieu = _kiem_tra_cay_local()

    if not thieu:
        _in(f"✓ Đã có đủ 5 file cây local.")
        return True

    _in(f"⚠ Thiếu {len(thieu)} file cây: {', '.join(thieu)}")
    _in("→ Đang tự sinh cây từ template...")

    try:
        from du_lieu.sinh_cay import sinh_cay
        sinh_cay()
        _in("✓ Sinh cây thành công.")
        return True
    except ImportError:
        _in("✗ Không import được du_lieu/sinh_cay.py.")
        return False
    except Exception as e:
        _in(f"✗ Sinh cây lỗi: {e}")
        return False


# ================================================================
# NẠP CÂY QUYẾT ĐỊNH
# ================================================================
def _nap_cay():
    """Nạp cây quyết định từ MongoDB + 5 file local."""
    _in("→ Đang nạp cây quyết định...")

    try:
        from dai_nao.ghi_nho import doc_cay, thong_ke_cay

        cay = doc_cay()
        if not cay:
            _in("✗ Không nạp được cây.")
            return False

        # Thống kê
        try:
            thong_ke = thong_ke_cay(cay)
            _in(f"✓ Nạp cây thành công: {thong_ke.get('tong_node', 0)} node, "
                f"độ sâu max: {thong_ke.get('do_sau_max', 0)}")
        except Exception:
            _in("✓ Nạp cây thành công.")

        return True

    except ImportError:
        _in("✗ Không import được dai_nao/ghi_nho.py.")
        return False
    except Exception as e:
        _in(f"✗ Nạp cây lỗi: {e}")
        return False


# ================================================================
# KEEP-ALIVE PING 2 KHO
# ================================================================
def _keep_alive_loop(thoi_gian_cho=12 * 3600):
    """
    Ping 2 kho MongoDB mỗi 12 giờ để tránh bị tạm dừng.

    thoi_gian_cho: số giây giữa các lần ping (mặc định 12 giờ).
    """
    # Đợi 60 giây trước lần ping đầu để server khởi động xong
    time.sleep(60)

    while True:
        try:
            from dai_nao.ghi_nho import ping_ca_2_kho
            ket_qua = ping_ca_2_kho()
            kho_1 = "OK" if ket_qua.get("kho_1") else "LỖI"
            kho_2 = "OK" if ket_qua.get("kho_2") else "LỖI"
            _in(f"💓 Keep-alive: kho 1 = {kho_1}, kho 2 = {kho_2}")
        except Exception as e:
            _in(f"⚠ Keep-alive lỗi: {e}")

        time.sleep(thoi_gian_cho)


def _bat_keep_alive():
    """Chạy keep-alive trong thread riêng (daemon)."""
    try:
        t = threading.Thread(target=_keep_alive_loop, daemon=True)
        t.start()
        _in("✓ Đã bật keep-alive ping 2 kho (mỗi 12 giờ).")
    except Exception as e:
        _in(f"⚠ Không bật được keep-alive: {e}")


# ================================================================
# TẠO FLASK APP
# ================================================================
def _tao_ung_dung():
    """Tạo Flask app từ giao_dien/app.py."""
    _in("→ Đang khởi tạo Flask app...")

    try:
        from giao_dien.app import tao_app
        ung_dung = tao_app()
        _in("✓ Flask app sẵn sàng.")
        return ung_dung
    except ImportError as e:
        _in(f"✗ Không import được giao_dien/app.py: {e}")
        return None
    except Exception as e:
        _in(f"✗ Khởi tạo Flask app lỗi: {e}")
        return None


# ================================================================
# IN BANNER
# ================================================================
def _in_banner():
    """In banner khởi động."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              🌕🐉  RỒNG THẦN  🐉🌕                      ║
║                                                          ║
║         AI Agent tự trị - Kiến trúc 2 não                ║
║                                                          ║
║  • Đại não    : Xử lý chính, chạy local                 ║
║  • Tiểu não   : Sinh nhánh khi bí, dùng API free        ║
║  • Tra web    : SERPJET / Tavily / Bright Data          ║
║  • Sandbox    : LiveCodes + Pyodide                     ║
║  • Cây quyết định: Bộ nhớ dài hạn                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner, flush=True)


# ================================================================
# KHỞI ĐỘNG CHÍNH
# ================================================================
def _khoi_dong():
    """
    Hàm khởi động chính, chạy 1 lần khi server bật.
    """
    _in_banner()

    # 1. Tự sinh cây nếu chưa có
    _in("=" * 60)
    _in("BƯỚC 1: Kiểm tra và sinh cây quyết định")
    _in("=" * 60)
    _tu_sinh_cay()

    # 2. Nạp cây quyết định
    _in("")
    _in("=" * 60)
    _in("BƯỚC 2: Nạp cây quyết định")
    _in("=" * 60)
    _nap_cay()

    # 3. Bật keep-alive
    _in("")
    _in("=" * 60)
    _in("BƯỚC 3: Bật keep-alive ping 2 kho")
    _in("=" * 60)
    _bat_keep_alive()

    # 4. Khởi tạo Flask
    _in("")
    _in("=" * 60)
    _in("BƯỚC 4: Khởi tạo Flask app")
    _in("=" * 60)

    _in("")
    _in("=" * 60)
    _in("✅ RỒNG THẦN ĐÃ SẴN SÀNG!")
    _in("=" * 60)


# ================================================================
# GỌI KHỞI ĐỘNG NGAY KHI IMPORT
# (chạy 1 lần khi Render hoặc local load file này)
# ================================================================
_khoi_dong()


# ================================================================
# TẠO APP CHO GUNICORN / FLASK
# ================================================================
ung_dung = _tao_ung_dung()


# ================================================================
# CHẠY LOCAL (nếu chạy trực tiếp)
# ================================================================
if __name__ == "__main__":
    if ung_dung is None:
        _in("✗ Không có Flask app để chạy.")
        sys.exit(1)

    cong = int(os.environ.get("PORT", 5000))
    _in(f"→ Chạy server tại http://0.0.0.0:{cong}")

    try:
        ung_dung.run(
            host="0.0.0.0",
            port=cong,
            debug=False,
            use_reloader=False,
        )
    except KeyboardInterrupt:
        _in("→ Đã dừng server (Ctrl+C).")
    except Exception as e:
        _in(f"✗ Server lỗi: {e}")
        sys.exit(1)
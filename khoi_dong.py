"""
khoi_dong.py - File khởi động chính Rồng Thần.

Nhiệm vụ:
    - Chạy Flask server (từ giao_dien/app.py).
    - Sinh file cây linh hồn nếu chưa có.
    - Chạy keep-alive ping 2 kho MongoDB mỗi 12 giờ.
    - Log khởi động rõ ràng.

ĐÃ SỬA:
    - Bỏ 5 file cây cũ (cay_quyet_dinh, cay_toan, cay_code, cay_bug, cay_khac).
    - Chỉ còn 1 file cây linh hồn (cay_linh_hon.json).
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
# GHI LOG ĐƠN GIẢN
# ================================================================
def _in(msg):
    """In ra console với timestamp."""
    tg = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{tg}] {msg}", flush=True)


# ================================================================
# SINH CÂY LINH HỒN
# ================================================================
def _sinh_cay():
    """Sinh file cây linh hồn nếu chưa có."""
    try:
        from du_lieu.sinh_cay_linh_hon import sinh_cay, cay_ton_tai

        if cay_ton_tai():
            _in("✓ Cây linh hồn đã có sẵn.")
            return True

        _in("→ Đang sinh cây linh hồn...")
        if sinh_cay():
            _in("✓ Sinh cây linh hồn thành công.")
            return True
        _in("✗ Sinh cây linh hồn lỗi.")
        return False
    except ImportError as e:
        _in(f"✗ Không import được sinh_cay_linh_hon: {e}")
        return False
    except Exception as e:
        _in(f"✗ Sinh cây lỗi: {e}")
        return False


# ================================================================
# KEEP-ALIVE PING 2 KHO
# ================================================================
def _keep_alive_loop(thoi_gian_cho=12 * 3600):
    """Ping 2 kho MongoDB mỗi 12 giờ."""
    time.sleep(60)

    while True:
        try:
            from luu_tru.ghi_nho import ping_ca_2_kho
            ket_qua = ping_ca_2_kho()
            kho_1 = "OK" if ket_qua.get("kho_1") else "LỖI"
            kho_2 = "OK" if ket_qua.get("kho_2") else "LỖI"
            _in(f"💓 Keep-alive: kho 1 = {kho_1}, kho 2 = {kho_2}")
        except Exception as e:
            _in(f"⚠ Keep-alive lỗi: {e}")

        time.sleep(thoi_gian_cho)


def _bat_keep_alive():
    """Chạy keep-alive trong thread riêng."""
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
║  • Boss       : Trí tuệ của Đại não                     ║
║  • Model      : Công cụ của Tiểu não                    ║
║  • Tra web    : SERPJET / Tavily / Bright Data          ║
║  • Sandbox    : LiveCodes                               ║
║  • Cây linh hồn: Bộ nhớ dài hạn (của riêng mỗi chat)   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner, flush=True)


# ================================================================
# KHỞI ĐỘNG CHÍNH
# ================================================================
def _khoi_dong():
    """Hàm khởi động chính."""
    _in_banner()

    _in("=" * 60)
    _in("BƯỚC 1: Sinh cây linh hồn")
    _in("=" * 60)
    _sinh_cay()

    _in("")
    _in("=" * 60)
    _in("BƯỚC 2: Bật keep-alive ping 2 kho")
    _in("=" * 60)
    _bat_keep_alive()

    _in("")
    _in("=" * 60)
    _in("BƯỚC 3: Khởi tạo Flask app")
    _in("=" * 60)

    _in("")
    _in("=" * 60)
    _in("✅ RỒNG THẦN ĐÃ SẴN SÀNG!")
    _in("=" * 60)


# ================================================================
# GỌI KHỞI ĐỘNG KHI IMPORT
# ================================================================
_khoi_dong()


# ================================================================
# TẠO APP CHO GUNICORN / FLASK
# ================================================================
ung_dung = _tao_ung_dung()


# ================================================================
# CHẠY LOCAL
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
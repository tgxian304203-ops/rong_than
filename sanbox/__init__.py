"""
sanbox - Package Sandbox Rồng Thần.

Sandbox chạy thử code do Đại não sinh ra.
Dùng LiveCodes, chạy client-side, hỗ trợ Python (Pyodide) và HTML (iframe).
Không cần server riêng, không cần tài khoản, miễn phí vĩnh viễn.

Đặc điểm:
    - Trung lập, cách ly, không ảnh hưởng hệ thống.
    - Chạy client-side → code không rời khỏi trình duyệt.
    - Hỗ trợ Python 3.12+ (Pyodide) và HTML/CSS/JS (iframe).
    - Nhúng vào giao diện Rồng Thần như nhúng video YouTube.

Gồm 5 file chính:
    - __init__.py: đánh dấu package.
    - chay_python.py: chạy code Python.
    - chay_html.py: chạy code HTML.
    - kiem_tra_loi.py: bắt lỗi, timeout.
    - tra_ket_qua.py: trả stdout/stderr.
    - nhung_vao_chat.py: nhúng LiveCodes vào chat.

Thư mục con:
    - giao_dien/: giao diện sandbox (index.html, nhung_livecodes.js, style.css).

Công nghệ:
    - Pyodide: Python chạy trên WebAssembly.
    - LiveCodes: sandbox đa ngôn ngữ client-side.
    - Web Worker: cách ly code khỏi UI chính.

Tầng dữ liệu: Không (Sandbox không lưu).
"""
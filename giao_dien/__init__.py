"""
giao_dien - Package giao diện Rồng Thần.

Chứa:
    - app.py: Flask server.
    - routes.py: Định nghĩa route API.
    - Các file .py xử lý logic giao diện:
        + xac_thuc.py: đăng ký, đăng nhập.
        + session.py: quản lý dự án, chat.
        + phien_dang_nhap.py: quản lý phiên đăng nhập.
        + luu_key.py: lưu key model.
        + luu_key_web.py: lưu key tra web.
        + luu_uri_kho.py: lưu URI 2 kho MongoDB.
        + doi_mat_khau.py: đổi mật khẩu.
        + upload.py: upload ảnh/file.
        + gui_tin_nhan.py: xử lý nút gửi.
    - Các file .js, .html, .css: giao diện client.

Tầng dữ liệu: dai_nao/ghi_nho.py (kết nối 2 kho MongoDB Atlas).
"""
/* ============================================================
   dang_nhap.js - Xử lý form đăng nhập Rồng Thần
   ------------------------------------------------------------
   ĐÃ SỬA:
     - Sau khi đăng nhập thành công → tải lại danh sách chat nhanh
       và dự án (vì lúc load trang chưa có session).
   ============================================================ */

(function () {
    'use strict';

    const popup      = document.getElementById('popup-dang-nhap');
    const oTen        = document.getElementById('dang-nhap-ten');
    const oMatKhau    = document.getElementById('dang-nhap-mat-khau');
    const nutXacNhan  = document.getElementById('nut-xac-nhan-dang-nhap');
    const oThongBao   = document.getElementById('dang-nhap-thong-bao');

    if (!popup || !oTen || !oMatKhau || !nutXacNhan || !oThongBao) {
        return;
    }

    /* ------------------------------------------------------------
       THÔNG BÁO
       ------------------------------------------------------------ */
    function hienThongBao(noiDung, thanhCong) {
        oThongBao.textContent = noiDung || '';
        oThongBao.classList.toggle('thanh-cong', !!thanhCong);
    }

    function xoaThongBao() {
        oThongBao.textContent = '';
        oThongBao.classList.remove('thanh-cong');
    }

    /* ------------------------------------------------------------
       KIỂM TRA
       ------------------------------------------------------------ */
    function kiemTraDuLieu(ten, matKhau) {
        if (!ten || !ten.trim()) {
            return 'Vui lòng nhập tên đăng nhập.';
        }
        if (!matKhau) {
            return 'Vui lòng nhập mật khẩu.';
        }
        return null;
    }

    /* ------------------------------------------------------------
       SAU KHI ĐĂNG NHẬP THÀNH CÔNG — CẬP NHẬT LẠI GIAO DIỆN
       ------------------------------------------------------------ */
    function capNhatSauDangNhap(tenNguoiDung) {
        // 1. Đổi giao diện sang chế độ tài khoản
        if (typeof window.chuyenSangCheDoTaiKhoan === 'function') {
            window.chuyenSangCheDoTaiKhoan(tenNguoiDung);
        }

        // 2. Đánh dấu không còn là khách
        window.__LA_KHACH = false;

        // 3. Tải lại danh sách dự án + chat nhanh (vì lúc load trang chưa có session)
        if (typeof window.taiDanhSachDuAn === 'function') {
            window.taiDanhSachDuAn();
        }
        if (typeof window.taiDanhSachChatNhanh === 'function') {
            window.taiDanhSachChatNhanh();
        }
    }

    /* ------------------------------------------------------------
       GỬI ĐĂNG NHẬP
       ------------------------------------------------------------ */
    async function guiDangNhap() {
        xoaThongBao();

        const ten      = oTen.value.trim();
        const matKhau  = oMatKhau.value;

        const loi = kiemTraDuLieu(ten, matKhau);
        if (loi) {
            hienThongBao(loi, false);
            return;
        }

        nutXacNhan.disabled = true;
        const chuCu = nutXacNhan.textContent;
        nutXacNhan.textContent = 'Đang xử lý...';

        try {
            const phanHoi = await fetch('/api/dang-nhap', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ten_dang_nhap: ten, mat_khau: matKhau }),
            });

            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong) {
                hienThongBao('Đăng nhập thành công!', true);

                capNhatSauDangNhap(duLieu.ten_dang_nhap || ten);

                oTen.value = '';
                oMatKhau.value = '';

                setTimeout(function () {
                    popup.classList.remove('dang-mo');
                }, 800);
            } else {
                hienThongBao(
                    (duLieu && duLieu.loi) || 'Tên đăng nhập hoặc mật khẩu không đúng.',
                    false
                );
            }
        } catch (e) {
            hienThongBao('Lỗi kết nối: ' + e.message, false);
        } finally {
            nutXacNhan.disabled = false;
            nutXacNhan.textContent = chuCu;
        }
    }

    /* ------------------------------------------------------------
       SỰ KIỆN
       ------------------------------------------------------------ */
    nutXacNhan.addEventListener('click', function (e) {
        e.preventDefault();
        guiDangNhap();
    });

    [oTen, oMatKhau].forEach(function (o) {
        o.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                guiDangNhap();
            }
        });
    });

    popup.addEventListener('transitionend', function () {
        if (!popup.classList.contains('dang-mo')) {
            xoaThongBao();
            oTen.value = '';
            oMatKhau.value = '';
        }
    });

})();
/* ============================================================
   dang_nhap.js - Xử lý form đăng nhập Rồng Thần
   ------------------------------------------------------------
   Nhiệm vụ:
     - Lấy tên đăng nhập + mật khẩu từ popup #popup-dang-nhap.
     - Kiểm tra dữ liệu cơ bản (không rỗng).
     - Gửi POST /api/dang-nhap.
     - Hiển thị thông báo lỗi/thành công trong #dang-nhap-thong-bao.
     - Khi thành công: đóng popup, cập nhật giao diện sang chế độ
       tài khoản (dùng lại window.chuyenSangCheDoTaiKhoan từ dang_ky.js).
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const popup      = document.getElementById('popup-dang-nhap');
    const oTen        = document.getElementById('dang-nhap-ten');
    const oMatKhau    = document.getElementById('dang-nhap-mat-khau');
    const nutXacNhan  = document.getElementById('nut-xac-nhan-dang-nhap');
    const oThongBao   = document.getElementById('dang-nhap-thong-bao');

    if (!popup || !oTen || !oMatKhau || !nutXacNhan || !oThongBao) {
        return; // Thiếu DOM thì thoát.
    }

    /* ------------------------------------------------------------
       HÀM HIỂN THỊ THÔNG BÁO
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
       KIỂM TRA DỮ LIỆU
       ------------------------------------------------------------ */
    function kiemTraDuLieu(ten, matKhau) {
        if (!ten || !ten.trim()) {
            return 'Vui lòng nhập tên đăng nhập.';
        }
        if (!matKhau) {
            return 'Vui lòng nhập mật khẩu.';
        }
        return null; // Không có lỗi
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

                // Đổi giao diện sang chế độ tài khoản
                if (typeof window.chuyenSangCheDoTaiKhoan === 'function') {
                    window.chuyenSangCheDoTaiKhoan(duLieu.ten_dang_nhap || ten);
                }

                // Xóa input
                oTen.value = '';
                oMatKhau.value = '';

                // Đóng popup sau 0.8s
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

    // Nhấn Enter trong ô nhập → gửi
    [oTen, oMatKhau].forEach(function (o) {
        o.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                guiDangNhap();
            }
        });
    });

    // Xóa thông báo + input khi đóng popup
    popup.addEventListener('transitionend', function () {
        if (!popup.classList.contains('dang-mo')) {
            xoaThongBao();
            oTen.value = '';
            oMatKhau.value = '';
        }
    });

})();
/* ============================================================
   dang_ky.js - Xử lý form đăng ký Rồng Thần
   ------------------------------------------------------------
   Nhiệm vụ:
     - Lấy tên đăng nhập + mật khẩu từ popup #popup-dang-ky.
     - Kiểm tra dữ liệu cơ bản (không rỗng, độ dài).
     - Gửi POST /api/dang-ky.
     - Hiển thị thông báo lỗi/thành công trong #dang-ky-thong-bao.
     - Khi thành công: đóng popup, cập nhật giao diện sang chế độ
       tài khoản (hiện tên người dùng, ẩn nút đăng ký/đăng nhập).
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const popup      = document.getElementById('popup-dang-ky');
    const oTen        = document.getElementById('dang-ky-ten');
    const oMatKhau    = document.getElementById('dang-ky-mat-khau');
    const nutXacNhan  = document.getElementById('nut-xac-nhan-dang-ky');
    const oThongBao   = document.getElementById('dang-ky-thong-bao');

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
        if (ten.trim().length < 3) {
            return 'Tên đăng nhập phải có ít nhất 3 ký tự.';
        }
        if (!matKhau) {
            return 'Vui lòng nhập mật khẩu.';
        }
        if (matKhau.length < 1) {
            return 'Mật khẩu không hợp lệ.';
        }
        return null; // Không có lỗi
    }

    /* ------------------------------------------------------------
       CẬP NHẬT GIAO DIỆN SANG CHẾ ĐỘ TÀI KHOẢN
       ------------------------------------------------------------ */
    function chuyenSangCheDoTaiKhoan(tenNguoiDung) {
        const elDaDangNhap = document.getElementById('nguoi-dung-da-dang-nhap');
        const elKhach       = document.getElementById('nguoi-dung-khach');
        const elTen         = document.getElementById('ten-nguoi-dung');
        const nutDoiMatKhau = document.getElementById('nut-mo-doi-mat-khau');

        if (elTen) elTen.textContent = tenNguoiDung || 'Người dùng';
        if (elDaDangNhap) elDaDangNhap.classList.remove('an');
        if (elKhach) elKhach.classList.add('an');
        if (nutDoiMatKhau) nutDoiMatKhau.classList.remove('an');
    }

    /* ------------------------------------------------------------
       GỬI ĐĂNG KÝ
       ------------------------------------------------------------ */
    async function guiDangKy() {
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
            const phanHoi = await fetch('/api/dang-ky', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ten_dang_nhap: ten, mat_khau: matKhau }),
            });

            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong) {
                hienThongBao('Đăng ký thành công!', true);

                // Đổi giao diện sang chế độ tài khoản
                chuyenSangCheDoTaiKhoan(duLieu.ten_dang_nhap || ten);

                // Xóa input
                oTen.value = '';
                oMatKhau.value = '';

                // Đóng popup sau 0.8s
                setTimeout(function () {
                    popup.classList.remove('dang-mo');
                }, 800);
            } else {
                hienThongBao(
                    (duLieu && duLieu.loi) || 'Đăng ký thất bại.',
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
        guiDangKy();
    });

    // Nhấn Enter trong ô nhập → gửi
    [oTen, oMatKhau].forEach(function (o) {
        o.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                guiDangKy();
            }
        });
    });

    // Xóa thông báo khi mở lại popup
    popup.addEventListener('transitionend', function () {
        if (!popup.classList.contains('dang-mo')) {
            xoaThongBao();
            oTen.value = '';
            oMatKhau.value = '';
        }
    });

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC (cho file khác dùng nếu cần)
       ------------------------------------------------------------ */
    window.chuyenSangCheDoTaiKhoan = chuyenSangCheDoTaiKhoan;

})();
/* ============================================================
   quan_ly_cai_dat.js - Xử lý trang Cài đặt + đổi mật khẩu + đăng xuất
   ------------------------------------------------------------
   Nhiệm vụ:
     - Nút Chế độ sáng tối: đổi class "sang" trên body, lưu vào localStorage.
     - Nút Cài đặt → mở trang Cài đặt (do quan_ly_menu.js đảm nhiệm).
     - Nút Key → mở trang Quản lý Key (do quan_ly_menu.js đảm nhiệm).
     - Nút Đổi mật khẩu → mở popup đổi mật khẩu.
     - Submit đổi mật khẩu: gọi POST /api/doi-mat-khau.
     - Nút Đăng xuất: gọi POST /api/dang-xuat, quay về chế độ khách.
     - Kiểm tra phiên đăng nhập khi tải trang (GET /api/phien).
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const nutDoiSangToi = document.getElementById('nut-doi-sang-toi');
    const nutDangXuat    = document.getElementById('nut-dang-xuat');
    const popupDoiMk     = document.getElementById('popup-doi-mat-khau');
    const oMkCu          = document.getElementById('doi-mk-cu');
    const oMkMoi         = document.getElementById('doi-mk-moi');
    const oMkLai         = document.getElementById('doi-mk-lai');
    const nutXacNhanDoiMk = document.getElementById('nut-xac-nhan-doi-mk');
    const oThongBaoDoiMk  = document.getElementById('doi-mk-thong-bao');

    /* ------------------------------------------------------------
       HÀM ĐỔI CHẾ ĐỘ SÁNG TỐI
       ------------------------------------------------------------ */
    function apDungCheDoSangToi(sang) {
        if (sang) {
            document.body.classList.add('sang');
        } else {
            document.body.classList.remove('sang');
        }
        try {
            localStorage.setItem('che_do_sang', sang ? '1' : '0');
        } catch (e) {
            // localStorage có thể bị chặn ở chế độ riêng tư
        }
    }

    function doiCheDoSangToi() {
        const dangSang = document.body.classList.contains('sang');
        apDungCheDoSangToi(!dangSang);
    }

    function napCheDoSangToi() {
        let sang = false;
        try {
            sang = localStorage.getItem('che_do_sang') === '1';
        } catch (e) {
            sang = false;
        }
        if (sang) document.body.classList.add('sang');
    }

    /* ------------------------------------------------------------
       HÀM HIỂN THỊ THÔNG BÁO POPUP ĐỔI MẬT KHẨU
       ------------------------------------------------------------ */
    function hienThongBaoDoiMk(noiDung, thanhCong) {
        if (!oThongBaoDoiMk) return;
        oThongBaoDoiMk.textContent = noiDung || '';
        oThongBaoDoiMk.classList.toggle('thanh-cong', !!thanhCong);
    }

    function xoaThongBaoDoiMk() {
        if (!oThongBaoDoiMk) return;
        oThongBaoDoiMk.textContent = '';
        oThongBaoDoiMk.classList.remove('thanh-cong');
    }

    /* ------------------------------------------------------------
       GỬI ĐỔI MẬT KHẨU
       ------------------------------------------------------------ */
    async function guiDoiMatKhau() {
        if (!oMkCu || !oMkMoi || !oMkLai || !nutXacNhanDoiMk) return;

        xoaThongBaoDoiMk();

        const cu  = oMkCu.value;
        const moi = oMkMoi.value;
        const lai = oMkLai.value;

        if (!cu) {
            hienThongBaoDoiMk('Vui lòng nhập mật khẩu cũ.', false);
            return;
        }
        if (!moi) {
            hienThongBaoDoiMk('Vui lòng nhập mật khẩu mới.', false);
            return;
        }
        if (moi !== lai) {
            hienThongBaoDoiMk('Mật khẩu mới nhập lại không khớp.', false);
            return;
        }

        nutXacNhanDoiMk.disabled = true;
        const chuCu = nutXacNhanDoiMk.textContent;
        nutXacNhanDoiMk.textContent = 'Đang xử lý...';

        try {
            const phanHoi = await fetch('/api/doi-mat-khau', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mat_khau_cu: cu, mat_khau_moi: moi }),
            });

            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong) {
                hienThongBaoDoiMk('Đổi mật khẩu thành công!', true);
                oMkCu.value = '';
                oMkMoi.value = '';
                oMkLai.value = '';
                setTimeout(function () {
                    if (popupDoiMk) popupDoiMk.classList.remove('dang-mo');
                }, 900);
            } else {
                hienThongBaoDoiMk(
                    (duLieu && duLieu.loi) || 'Đổi mật khẩu thất bại.',
                    false
                );
            }
        } catch (e) {
            hienThongBaoDoiMk('Lỗi kết nối: ' + e.message, false);
        } finally {
            nutXacNhanDoiMk.disabled = false;
            nutXacNhanDoiMk.textContent = chuCu;
        }
    }

    /* ------------------------------------------------------------
       ĐĂNG XUẤT
       ------------------------------------------------------------ */
    async function dangXuat() {
        const hamDongY = async function () {
            try {
                await fetch('/api/dang-xuat', { method: 'POST' });
            } catch (e) {
                // Im lặng — vẫn xóa giao diện dù server lỗi
            }
            chuyenSangCheDoKhach();
        };

        if (typeof window.moXacNhanXoa === 'function') {
            window.moXacNhanXoa('Bạn có chắc muốn đăng xuất?', hamDongY);
        } else {
            if (confirm('Bạn có chắc muốn đăng xuất?')) hamDongY();
        }
    }

    /* ------------------------------------------------------------
       CHUYỂN GIAO DIỆN SANG CHẾ ĐỘ KHÁCH
       ------------------------------------------------------------ */
    function chuyenSangCheDoKhach() {
        const elDaDangNhap = document.getElementById('nguoi-dung-da-dang-nhap');
        const elKhach       = document.getElementById('nguoi-dung-khach');
        const elTen         = document.getElementById('ten-nguoi-dung');
        const nutDoiMatKhau = document.getElementById('nut-mo-doi-mat-khau');

        if (elDaDangNhap) elDaDangNhap.classList.add('an');
        if (elKhach) elKhach.classList.remove('an');
        if (elTen) elTen.textContent = 'Người dùng';
        if (nutDoiMatKhau) nutDoiMatKhau.classList.add('an');
    }

    /* ------------------------------------------------------------
       KIỂM TRA PHIÊN ĐĂNG NHẬP KHI TẢI TRANG
       ------------------------------------------------------------ */
    async function kiemTraPhien() {
        try {
            const phanHoi = await fetch('/api/phien');
            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.da_dang_nhap) {
                if (typeof window.chuyenSangCheDoTaiKhoan === 'function') {
                    window.chuyenSangCheDoTaiKhoan(duLieu.ten_dang_nhap || '');
                }
            } else {
                chuyenSangCheDoKhach();
            }
        } catch (e) {
            // Không kết nối được — mặc định là khách
            chuyenSangCheDoKhach();
        }
    }

    /* ------------------------------------------------------------
       SỰ KIỆN
       ------------------------------------------------------------ */
    if (nutDoiSangToi) {
        nutDoiSangToi.addEventListener('click', doiCheDoSangToi);
    }

    if (nutDangXuat) {
        nutDangXuat.addEventListener('click', dangXuat);
    }

    if (nutXacNhanDoiMk) {
        nutXacNhanDoiMk.addEventListener('click', function (e) {
            e.preventDefault();
            guiDoiMatKhau();
        });
    }

    // Nhấn Enter trong popup đổi mật khẩu → gửi
    [oMkCu, oMkMoi, oMkLai].forEach(function (o) {
        if (!o) return;
        o.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                guiDoiMatKhau();
            }
        });
    });

    // Xóa thông báo khi đóng popup đổi mật khẩu
    if (popupDoiMk) {
        popupDoiMk.addEventListener('transitionend', function () {
            if (!popupDoiMk.classList.contains('dang-mo')) {
                xoaThongBaoDoiMk();
                if (oMkCu) oMkCu.value = '';
                if (oMkMoi) oMkMoi.value = '';
                if (oMkLai) oMkLai.value = '';
            }
        });
    }

    /* ------------------------------------------------------------
       KHỞI ĐỘNG
       ------------------------------------------------------------ */
    function khoiDong() {
        napCheDoSangToi();
        kiemTraPhien();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.chuyenSangCheDoKhach = chuyenSangCheDoKhach;
    window.doiCheDoSangToi = doiCheDoSangToi;

})();
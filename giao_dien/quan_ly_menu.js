/* ============================================================
   quan_ly_menu.js - Quản lý mở/đóng menu và popup Rồng Thần
   ------------------------------------------------------------
   Nhiệm vụ:
     - Mở/đóng menu trái (overlay trượt từ trái, 100%).
     - Mở/đóng menu phải (overlay trượt từ phải, 100%).
     - Mở/đóng các trang con: Cài đặt, Key, Logs.
     - Mở/đóng các popup: Đăng ký, Đăng nhập, Đổi mật khẩu, Xác nhận xóa.
     - Cung cấp hàm toàn cục để file khác gọi mở popup xác nhận xóa.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       HÀM TIỆN ÍCH
       ------------------------------------------------------------ */
    function lay(id) {
        return document.getElementById(id);
    }

    function mo(el) {
        if (el) el.classList.add('dang-mo');
    }

    function dong(el) {
        if (el) el.classList.remove('dang-mo');
    }

    function hien(el) {
        if (el) el.classList.remove('an');
    }

    function an(el) {
        if (el) el.classList.add('an');
    }

    function ganSuKien(id, suKien, ham) {
        const el = lay(id);
        if (el) el.addEventListener(suKien, ham);
    }

    /* ------------------------------------------------------------
       MENU TRÁI
       ------------------------------------------------------------ */
    function moMenuTrai() {
        mo(lay('menu-trai'));
    }

    function dongMenuTrai() {
        dong(lay('menu-trai'));
    }

    /* ------------------------------------------------------------
       MENU PHẢI
       ------------------------------------------------------------ */
    function moMenuPhai() {
        mo(lay('menu-phai'));
    }

    function dongMenuPhai() {
        dong(lay('menu-phai'));
    }

    /* ------------------------------------------------------------
       TRANG CÀI ĐẶT
       ------------------------------------------------------------ */
    function moCaiDat() {
        dongMenuTrai();
        mo(lay('trang-cai-dat'));
    }

    function dongCaiDat() {
        dong(lay('trang-cai-dat'));
    }

    /* ------------------------------------------------------------
       TRANG KEY
       ------------------------------------------------------------ */
    function moTrangKey() {
        dongCaiDat();
        mo(lay('trang-key'));
    }

    function dongTrangKey() {
        dong(lay('trang-key'));
    }

    /* ------------------------------------------------------------
       TRANG LOGS
       ------------------------------------------------------------ */
    function moTrangLogs() {
        dongMenuPhai();
        mo(lay('trang-logs'));
    }

    function dongTrangLogs() {
        dong(lay('trang-logs'));
    }

    /* ------------------------------------------------------------
       POPUP ĐĂNG KÝ
       ------------------------------------------------------------ */
    function moPopupDangKy() {
        dongMenuTrai();
        mo(lay('popup-dang-ky'));
    }

    function dongPopupDangKy() {
        dong(lay('popup-dang-ky'));
    }

    /* ------------------------------------------------------------
       POPUP ĐĂNG NHẬP
       ------------------------------------------------------------ */
    function moPopupDangNhap() {
        dongMenuTrai();
        mo(lay('popup-dang-nhap'));
    }

    function dongPopupDangNhap() {
        dong(lay('popup-dang-nhap'));
    }

    /* ------------------------------------------------------------
       POPUP ĐỔI MẬT KHẨU
       ------------------------------------------------------------ */
    function moPopupDoiMatKhau() {
        dongCaiDat();
        mo(lay('popup-doi-mat-khau'));
    }

    function dongPopupDoiMatKhau() {
        dong(lay('popup-doi-mat-khau'));
    }

    /* ------------------------------------------------------------
       POPUP XÁC NHẬN XÓA
       - Hàm toàn cục để file khác gọi:
           window.moXacNhanXoa(noiDung, hamDongY)
       ------------------------------------------------------------ */
    let hamDongYXoaHienTai = null;

    function moXacNhanXoa(noiDung, hamDongY) {
        const elNoiDung = lay('xac-nhan-noi-dung');
        if (elNoiDung) {
            elNoiDung.textContent = noiDung || 'Bạn có chắc muốn xóa?';
        }
        hamDongYXoaHienTai = typeof hamDongY === 'function' ? hamDongY : null;
        mo(lay('popup-xac-nhan-xoa'));
    }

    function dongXacNhanXoa() {
        dong(lay('popup-xac-nhan-xoa'));
        hamDongYXoaHienTai = null;
    }

    function dongYXoa() {
        const ham = hamDongYXoaHienTai;
        dongXacNhanXoa();
        if (typeof ham === 'function') {
            try {
                ham();
            } catch (e) {
                console.error('Lỗi khi thực hiện xóa:', e);
            }
        }
    }

    /* ------------------------------------------------------------
       GẮN SỰ KIỆN
       ------------------------------------------------------------ */
    function ganToanBoSuKien() {

        // Menu trái
        ganSuKien('nut-menu-trai', 'click', moMenuTrai);
        ganSuKien('dong-menu-trai', 'click', dongMenuTrai);

        // Menu phải
        ganSuKien('nut-menu-phai', 'click', moMenuPhai);
        ganSuKien('dong-menu-phai', 'click', dongMenuPhai);

        // Cài đặt
        ganSuKien('nut-cai-dat', 'click', moCaiDat);
        ganSuKien('dong-cai-dat', 'click', dongCaiDat);
        ganSuKien('nut-mo-key', 'click', moTrangKey);
        ganSuKien('nut-mo-doi-mat-khau', 'click', moPopupDoiMatKhau);
        ganSuKien('dong-key', 'click', dongTrangKey);
        ganSuKien('dong-popup-doi-mat-khau', 'click', dongPopupDoiMatKhau);
        ganSuKien('nut-huy-doi-mk', 'click', dongPopupDoiMatKhau);

        // Logs
        ganSuKien('nut-mo-logs', 'click', moTrangLogs);
        ganSuKien('dong-logs', 'click', dongTrangLogs);

        // Popup đăng ký
        ganSuKien('nut-mo-dang-ky', 'click', moPopupDangKy);
        ganSuKien('dong-popup-dang-ky', 'click', dongPopupDangKy);

        // Popup đăng nhập
        ganSuKien('nut-mo-dang-nhap', 'click', moPopupDangNhap);
        ganSuKien('dong-popup-dang-nhap', 'click', dongPopupDangNhap);

        // Popup xác nhận xóa
        ganSuKien('nut-huy-xoa', 'click', dongXacNhanXoa);
        ganSuKien('nut-dong-y-xoa', 'click', dongYXoa);

        // Bấm vào nền popup (ngoài hộp) thì đóng popup
        ['popup-dang-ky', 'popup-dang-nhap', 'popup-xac-nhan-xoa', 'popup-doi-mat-khau']
            .forEach(function (idPopup) {
                const elPopup = lay(idPopup);
                if (elPopup) {
                    elPopup.addEventListener('click', function (e) {
                        if (e.target === elPopup) {
                            dong(elPopup);
                        }
                    });
                }
            });

        // Nhấn ESC để đóng tất cả overlay/popup đang mở
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                ['menu-trai', 'menu-phai', 'trang-cai-dat', 'trang-key', 'trang-logs']
                    .forEach(function (id) {
                        dong(lay(id));
                    });
                ['popup-dang-ky', 'popup-dang-nhap', 'popup-xac-nhan-xoa', 'popup-doi-mat-khau']
                    .forEach(function (id) {
                        dong(lay(id));
                    });
            }
        });
    }

    /* ------------------------------------------------------------
       XUẤT HÀM RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.moXacNhanXoa = moXacNhanXoa;
    window.moMenuTrai = moMenuTrai;
    window.dongMenuTrai = dongMenuTrai;
    window.moMenuPhai = moMenuPhai;
    window.dongMenuPhai = dongMenuPhai;
    window.moTrangKey = moTrangKey;
    window.moTrangLogs = moTrangLogs;
    window.moPopupDangKy = moPopupDangKy;
    window.moPopupDangNhap = moPopupDangNhap;
    window.hien = hien;
    window.an = an;

    /* ------------------------------------------------------------
       KHỞI ĐỘNG KHI DOM SẴN SÀNG
       ------------------------------------------------------------ */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ganToanBoSuKien);
    } else {
        ganToanBoSuKien();
    }

})();
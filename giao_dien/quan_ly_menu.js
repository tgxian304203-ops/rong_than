/* ============================================================
   quan_ly_menu.js - Quản lý mở/đóng menu và popup Rồng Thần
   ------------------------------------------------------------
   ĐÃ SỬA: Gắn sự kiện cho 6 nút thiếu:
     - New Chat
     - Tạo dự án
     - Share
     - Cây quyết định
     - Chế độ sáng tối
     - Đăng xuất
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
       MENU TRÁI / PHẢI
       ------------------------------------------------------------ */
    function moMenuTrai() { mo(lay('menu-trai')); }
    function dongMenuTrai() { dong(lay('menu-trai')); }
    function moMenuPhai() { mo(lay('menu-phai')); }
    function dongMenuPhai() { dong(lay('menu-phai')); }

    /* ------------------------------------------------------------
       TRANG CÀI ĐẶT / KEY / LOGS / CÂY
       ------------------------------------------------------------ */
    function moCaiDat() {
        dongMenuTrai();
        mo(lay('trang-cai-dat'));
    }
    function dongCaiDat() { dong(lay('trang-cai-dat')); }

    function moTrangKey() {
        dongCaiDat();
        mo(lay('trang-key'));
    }
    function dongTrangKey() { dong(lay('trang-key')); }

    function moTrangLogs() {
        dongMenuPhai();
        mo(lay('trang-logs'));
    }
    function dongTrangLogs() { dong(lay('trang-logs')); }

    function moTrangCay() {
        dongMenuTrai();
        mo(lay('trang-cay'));
        // Gọi hàm vẽ cây nếu có
        if (typeof window.taiCay === 'function') {
            window.taiCay();
        }
    }
    function dongTrangCay() { dong(lay('trang-cay')); }

    /* ------------------------------------------------------------
       POPUP ĐĂNG KÝ / ĐĂNG NHẬP / ĐỔI MẬT KHẨU
       ------------------------------------------------------------ */
    function moPopupDangKy() {
        dongMenuTrai();
        mo(lay('popup-dang-ky'));
    }
    function dongPopupDangKy() { dong(lay('popup-dang-ky')); }

    function moPopupDangNhap() {
        dongMenuTrai();
        mo(lay('popup-dang-nhap'));
    }
    function dongPopupDangNhap() { dong(lay('popup-dang-nhap')); }

    function moPopupDoiMatKhau() {
        dongCaiDat();
        mo(lay('popup-doi-mat-khau'));
    }
    function dongPopupDoiMatKhau() { dong(lay('popup-doi-mat-khau')); }

    /* ------------------------------------------------------------
       POPUP TẠO DỰ ÁN
       ------------------------------------------------------------ */
    function moPopupTaoDuAn() {
        dongMenuTrai();
        // Nếu popup chưa có trong HTML, tạo động
        let popup = lay('popup-tao-du-an');
        if (!popup) {
            popup = document.createElement('div');
            popup.id = 'popup-tao-du-an';
            popup.className = 'popup-nen';
            popup.innerHTML = `
                <div class="popup">
                    <div class="popup-header">
                        <div class="popup-tieude">📁 Tạo dự án</div>
                        <button id="dong-popup-tao-du-an" class="nut-icon" aria-label="Đóng">✕</button>
                    </div>
                    <div class="popup-body">
                        <input type="text" id="ten-du-an-moi" class="o-nhap-popup" placeholder="Nhập tên dự án...">
                        <div id="tao-du-an-thong-bao" class="thong-bao-popup"></div>
                        <div class="popup-nut-hang">
                            <button id="huy-tao-du-an" class="nut-phu">Hủy</button>
                            <button id="xac-nhan-tao-du-an" class="nut-chinh">Tạo</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(popup);

            // Gắn sự kiện cho popup vừa tạo
            const nutDong = popup.querySelector('#dong-popup-tao-du-an');
            const nutHuy = popup.querySelector('#huy-tao-du-an');
            const nutXacNhan = popup.querySelector('#xac-nhan-tao-du-an');
            const oTen = popup.querySelector('#ten-du-an-moi');

            if (nutDong) nutDong.addEventListener('click', function () { dong(popup); });
            if (nutHuy) nutHuy.addEventListener('click', function () { dong(popup); });

            if (nutXacNhan) {
                nutXacNhan.addEventListener('click', async function () {
                    const ten = oTen.value.trim();
                    if (!ten) {
                        popup.querySelector('#tao-du-an-thong-bao').textContent = 'Vui lòng nhập tên dự án.';
                        return;
                    }
                    await xuLyTaoDuAn(ten, popup);
                });
            }

            if (oTen) {
                oTen.addEventListener('keydown', function (e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        nutXacNhan.click();
                    }
                });
            }

            // Bấm nền popup thì đóng
            popup.addEventListener('click', function (e) {
                if (e.target === popup) dong(popup);
            });
        }

        // Reset
        const oTenReset = popup.querySelector('#ten-du-an-moi');
        if (oTenReset) oTenReset.value = '';
        const tbReset = popup.querySelector('#tao-du-an-thong-bao');
        if (tbReset) tbReset.textContent = '';

        mo(popup);

        // Focus vào ô nhập
        setTimeout(function () {
            if (oTenReset) oTenReset.focus();
        }, 100);
    }

    async function xuLyTaoDuAn(ten, popup) {
        const tb = popup.querySelector('#tao-du-an-thong-bao');
        const nutXacNhan = popup.querySelector('#xac-nhan-tao-du-an');
        if (nutXacNhan) nutXacNhan.disabled = true;
        if (tb) tb.textContent = 'Đang tạo...';

        try {
            const phanHoi = await fetch('/api/tao-du-an', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ten: ten }),
            });
            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong) {
                dong(popup);
                // Tải lại danh sách dự án
                if (typeof window.taiDanhSachDuAn === 'function') {
                    window.taiDanhSachDuAn();
                }
                if (typeof window.themTinNhanHeThong === 'function') {
                    window.themTinNhanHeThong('📁 Đã tạo dự án: ' + ten);
                }
            } else {
                if (tb) tb.textContent = (duLieu && duLieu.loi) || 'Không tạo được dự án.';
            }
        } catch (e) {
            if (tb) tb.textContent = 'Lỗi kết nối: ' + e.message;
        } finally {
            if (nutXacNhan) nutXacNhan.disabled = false;
        }
    }

    /* ------------------------------------------------------------
       NEW CHAT
       ------------------------------------------------------------ */
    async function xuLyNewChat() {
        dongMenuTrai();

        try {
            const phanHoi = await fetch('/api/tao-chat-nhanh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong) {
                // Xóa khung chat hiện tại
                const khung = lay('danh-sach-tin-nhan');
                if (khung) khung.innerHTML = '';

                // Hiện tin nhắn chào
                if (typeof window.themTinNhanRong === 'function') {
                    window.themTinNhanRong('Nói điều ước đi 🔥🐉');
                }

                // Tải lại danh sách chat nhanh
                if (typeof window.taiDanhSachChatNhanh === 'function') {
                    window.taiDanhSachChatNhanh();
                }
            } else {
                // Nếu API lỗi, vẫn xóa chat + hiện chào (fallback)
                const khung = lay('danh-sach-tin-nhan');
                if (khung) khung.innerHTML = '';
                if (typeof window.themTinNhanRong === 'function') {
                    window.themTinNhanRong('Nói điều ước đi 🔥🐉');
                }
            }
        } catch (e) {
            // Fallback khi lỗi kết nối
            const khung = lay('danh-sach-tin-nhan');
            if (khung) khung.innerHTML = '';
            if (typeof window.themTinNhanRong === 'function') {
                window.themTinNhanRong('Nói điều ước đi 🔥🐉');
            }
        }
    }

    /* ------------------------------------------------------------
       SHARE
       ------------------------------------------------------------ */
    async function xuLyShare() {
        try {
            const url = window.location.href;
            await navigator.clipboard.writeText(url);
            if (typeof window.themTinNhanHeThong === 'function') {
                window.themTinNhanHeThong('🔗 Đã copy link chia sẻ.');
            } else {
                alert('Đã copy link: ' + url);
            }
        } catch (e) {
            alert('Không copy được link. Link hiện tại: ' + window.location.href);
        }
        dongMenuTrai();
    }

    /* ------------------------------------------------------------
       ĐỔI SÁNG TỐI
       ------------------------------------------------------------ */
    function xuLyDoiSangToi() {
        document.body.classList.toggle('sang');
        const dangSang = document.body.classList.contains('sang');
        try {
            localStorage.setItem('che_do_sang', dangSang ? '1' : '0');
        } catch (e) {}
        dongMenuTrai();
    }

    // Áp dụng chế độ sáng đã lưu khi load trang
    function apDungCheDoSang() {
        try {
            const da = localStorage.getItem('che_do_sang');
            if (da === '1') {
                document.body.classList.add('sang');
            }
        } catch (e) {}
    }

    /* ------------------------------------------------------------
       ĐĂNG XUẤT
       ------------------------------------------------------------ */
    async function xuLyDangXuat() {
        try {
            await fetch('/api/dang-xuat', { method: 'POST' });
        } catch (e) {}
        window.location.reload();
    }

    /* ------------------------------------------------------------
       POPUP XÁC NHẬN XÓA
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

        // Menu trái / phải
        ganSuKien('nut-menu-trai', 'click', moMenuTrai);
        ganSuKien('dong-menu-trai', 'click', dongMenuTrai);
        ganSuKien('nut-menu-phai', 'click', moMenuPhai);
        ganSuKien('dong-menu-phai', 'click', dongMenuPhai);

        // Cài đặt / Key / Đổi mật khẩu
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

        // Cây quyết định
        ganSuKien('nut-mo-cay', 'click', moTrangCay);
        ganSuKien('dong-cay', 'click', dongTrangCay);

        // Popup đăng ký / đăng nhập
        ganSuKien('nut-mo-dang-ky', 'click', moPopupDangKy);
        ganSuKien('dong-popup-dang-ky', 'click', dongPopupDangKy);
        ganSuKien('nut-mo-dang-nhap', 'click', moPopupDangNhap);
        ganSuKien('dong-popup-dang-nhap', 'click', dongPopupDangNhap);

        // Popup xác nhận xóa
        ganSuKien('nut-huy-xoa', 'click', dongXacNhanXoa);
        ganSuKien('nut-dong-y-xoa', 'click', dongYXoa);

        // 6 NÚT MỚI GẮN SỰ KIỆN
        ganSuKien('nut-new-chat', 'click', xuLyNewChat);
        ganSuKien('nut-tao-du-an', 'click', moPopupTaoDuAn);
        ganSuKien('nut-share', 'click', xuLyShare);
        ganSuKien('nut-doi-sang-toi', 'click', xuLyDoiSangToi);
        ganSuKien('nut-dang-xuat', 'click', xuLyDangXuat);

        // Bấm nền popup thì đóng
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

        // ESC đóng tất cả
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                ['menu-trai', 'menu-phai', 'trang-cai-dat', 'trang-key', 'trang-logs', 'trang-cay']
                    .forEach(function (id) { dong(lay(id)); });
                ['popup-dang-ky', 'popup-dang-nhap', 'popup-xac-nhan-xoa',
                 'popup-doi-mat-khau', 'popup-tao-du-an']
                    .forEach(function (id) { dong(lay(id)); });
            }
        });

        // Áp dụng chế độ sáng đã lưu
        apDungCheDoSang();
    }

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.moXacNhanXoa = moXacNhanXoa;
    window.moMenuTrai = moMenuTrai;
    window.dongMenuTrai = dongMenuTrai;
    window.moMenuPhai = moMenuPhai;
    window.dongMenuPhai = dongMenuPhai;
    window.moTrangKey = moTrangKey;
    window.moTrangLogs = moTrangLogs;
    window.moTrangCay = moTrangCay;
    window.moPopupDangKy = moPopupDangKy;
    window.moPopupDangNhap = moPopupDangNhap;
    window.moPopupTaoDuAn = moPopupTaoDuAn;
    window.xuLyNewChat = xuLyNewChat;
    window.hien = hien;
    window.an = an;

    /* ------------------------------------------------------------
       KHỞI ĐỘNG
       ------------------------------------------------------------ */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ganToanBoSuKien);
    } else {
        ganToanBoSuKien();
    }

})();
/* ============================================================
   quan_ly_menu.js - Quản lý menu, popup, trang Rồng Thần
   ------------------------------------------------------------
   ĐÃ SỬA:
     - Bỏ nút Share.
     - Lưu trò chuyện vào localStorage khi khách tạo.
   ============================================================ */

(function () {
    'use strict';

    function lay(id) { return document.getElementById(id); }
    function mo(el) { if (el) el.classList.add('dang-mo'); }
    function dong(el) { if (el) el.classList.remove('dang-mo'); }
    function hien(el) { if (el) el.classList.remove('an'); }
    function an(el) { if (el) el.classList.add('an'); }
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
       CÀI ĐẶT / KEY / LOGS / CÂY
       ------------------------------------------------------------ */
    function moCaiDat() { dongMenuTrai(); mo(lay('trang-cai-dat')); }
    function dongCaiDat() { dong(lay('trang-cai-dat')); }

    function moTrangKey() { dongCaiDat(); mo(lay('trang-key')); }
    function dongTrangKey() { dong(lay('trang-key')); }

    function moTrangLogs() { dongMenuPhai(); mo(lay('trang-logs')); }
    function dongTrangLogs() { dong(lay('trang-logs')); }

    function moTrangCay() {
        dongMenuTrai();
        mo(lay('trang-cay'));
        if (typeof window.taiCay === 'function') window.taiCay();
    }
    function dongTrangCay() { dong(lay('trang-cay')); }

    /* ------------------------------------------------------------
       TRANG DỰ ÁN
       ------------------------------------------------------------ */
    function moTrangDuAn() {
        dongMenuTrai();
        mo(lay('trang-du-an'));
        if (typeof window.taiDanhSachDuAn === 'function') {
            window.taiDanhSachDuAn();
        }
    }
    function dongTrangDuAn() { dong(lay('trang-du-an')); }

    /* ------------------------------------------------------------
       TRANG CHI TIẾT DỰ ÁN
       ------------------------------------------------------------ */
    function moChiTietDuAn(idDuAn, tenDuAn) {
        dongTrangDuAn();
        const tieuDe = lay('tieude-chi-tiet-du-an');
        if (tieuDe) tieuDe.textContent = tenDuAn || 'Dự án';

        window.__ID_DU_AN_DANG_XEM = idDuAn;
        window.__TEN_DU_AN_DANG_XEM = tenDuAn;

        doiTab('tro-chuyen');
        mo(lay('trang-chi-tiet-du-an'));

        if (typeof window.taiDanhSachTroChuyen === 'function') {
            window.taiDanhSachTroChuyen(idDuAn);
        }
    }
    function dongChiTietDuAn() {
        dong(lay('trang-chi-tiet-du-an'));
    }

    function doiTab(tenTab) {
        document.querySelectorAll('.tab-nut').forEach(function (btn) {
            btn.classList.toggle('dang-chon', btn.dataset.tab === tenTab);
        });
        const noiTro = lay('noi-dung-tro-chuyen');
        const noiNguon = lay('noi-dung-nguon');
        if (noiTro) noiTro.classList.toggle('an', tenTab !== 'tro-chuyen');
        if (noiNguon) noiNguon.classList.toggle('an', tenTab !== 'nguon');
    }

    /* ------------------------------------------------------------
       TRANG CHAT TRONG DỰ ÁN
       ------------------------------------------------------------ */
    function moChatDuAn(idDuAn, idTroChuyen, tenTroChuyen) {
        const tieuDe = lay('tieu de-chat-du-an') || lay('tieude-chat-du-an');
        if (tieuDe) tieuDe.textContent = tenTroChuyen || 'Trò chuyện';

        window.__ID_DU_AN_DANG_CHAT = idDuAn;
        window.__ID_TRO_CHUYEN_DANG_CHAT = idTroChuyen;

        const khung = lay('danh-sach-tin-nhan-du-an');
        if (khung) khung.innerHTML = '';

        mo(lay('trang-chat-du-an'));

        if (typeof window.taiTinNhanTroChuyen === 'function') {
            window.taiTinNhanTroChuyen(idDuAn, idTroChuyen);
        }

        const oNhap = lay('o-nhap-du-an');
        if (oNhap) {
            oNhap.value = '';
            setTimeout(function () { oNhap.focus(); }, 200);
        }
    }
    function quayLaiDuAn() {
        dong(lay('trang-chat-du-an'));
        mo(lay('trang-chi-tiet-du-an'));
        // Tải lại danh sách trò chuyện — QUAN TRỌNG
        if (typeof window.taiDanhSachTroChuyen === 'function') {
            window.taiDanhSachTroChuyen(window.__ID_DU_AN_DANG_XEM);
        }
    }

    /* ------------------------------------------------------------
       POPUP ĐĂNG KÝ / ĐĂNG NHẬP / ĐỔI MẬT KHẨU
       ------------------------------------------------------------ */
    function moPopupDangKy() { dongMenuTrai(); mo(lay('popup-dang-ky')); }
    function dongPopupDangKy() { dong(lay('popup-dang-ky')); }

    function moPopupDangNhap() { dongMenuTrai(); mo(lay('popup-dang-nhap')); }
    function dongPopupDangNhap() { dong(lay('popup-dang-nhap')); }

    function moPopupDoiMatKhau() { dongCaiDat(); mo(lay('popup-doi-mat-khau')); }
    function dongPopupDoiMatKhau() { dong(lay('popup-doi-mat-khau')); }

    /* ------------------------------------------------------------
       POPUP TẠO DỰ ÁN
       ------------------------------------------------------------ */
    function moPopupTaoDuAn() {
        dongMenuTrai();
        let popup = lay('popup-tao-du-an');
        if (!popup) {
            popup = document.createElement('div');
            popup.id = 'popup-tao-du-an';
            popup.className = 'popup-nen';
            popup.innerHTML = `
                <div class="popup">
                    <div class="popup-header">
                        <div class="popup-tieude">📁 Tạo dự án</div>
                        <button id="dong-popup-tao-du-an" class="nut-icon">✕</button>
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

            popup.querySelector('#dong-popup-tao-du-an')
                .addEventListener('click', function () { dong(popup); });
            popup.querySelector('#huy-tao-du-an')
                .addEventListener('click', function () { dong(popup); });

            const oTen = popup.querySelector('#ten-du-an-moi');
            popup.querySelector('#xac-nhan-tao-du-an').addEventListener('click', async function () {
                const ten = oTen.value.trim();
                if (!ten) {
                    popup.querySelector('#tao-du-an-thong-bao').textContent = 'Vui lòng nhập tên dự án.';
                    return;
                }
                await xuLyTaoDuAn(ten, popup);
            });

            oTen.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    popup.querySelector('#xac-nhan-tao-du-an').click();
                }
            });

            popup.addEventListener('click', function (e) {
                if (e.target === popup) dong(popup);
            });
        }

        const oTenReset = popup.querySelector('#ten-du-an-moi');
        if (oTenReset) oTenReset.value = '';
        const tbReset = popup.querySelector('#tao-du-an-thong-bao');
        if (tbReset) tbReset.textContent = '';

        mo(popup);
        setTimeout(function () { if (oTenReset) oTenReset.focus(); }, 100);
    }

    async function xuLyTaoDuAn(ten, popup) {
        const tb = popup.querySelector('#tao-du-an-thong-bao');
        const nut = popup.querySelector('#xac-nhan-tao-du-an');
        if (nut) nut.disabled = true;
        if (tb) tb.textContent = 'Đang tạo...';

        try {
            const ph = await fetch('/api/tao-du-an', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ten: ten }),
            });
            const dl = await ph.json();

            if (dl && dl.thanh_cong) {
                if (dl.tam && dl.du_an && typeof window.luuDuAnKhach === 'function') {
                    window.luuDuAnKhach(dl.du_an);
                }
                dong(popup);
                if (typeof window.taiDanhSachDuAn === 'function') {
                    window.taiDanhSachDuAn();
                }
            } else {
                if (tb) tb.textContent = (dl && dl.loi) || 'Không tạo được dự án.';
            }
        } catch (e) {
            if (tb) tb.textContent = 'Lỗi kết nối: ' + e.message;
        } finally {
            if (nut) nut.disabled = false;
        }
    }

    /* ------------------------------------------------------------
       POPUP TẠO TRÒ CHUYỆN TRONG DỰ ÁN
       ------------------------------------------------------------ */
    function moPopupTaoTroChuyen() {
        const idDuAn = window.__ID_DU_AN_DANG_XEM;
        if (!idDuAn) return;

        let popup = lay('popup-tao-tro-chuyen');
        if (!popup) {
            popup = document.createElement('div');
            popup.id = 'popup-tao-tro-chuyen';
            popup.className = 'popup-nen';
            popup.innerHTML = `
                <div class="popup">
                    <div class="popup-header">
                        <div class="popup-tieude">💬 Trò chuyện mới</div>
                        <button id="dong-popup-tao-tro-chuyen" class="nut-icon">✕</button>
                    </div>
                    <div class="popup-body">
                        <input type="text" id="ten-tro-chuyen-moi" class="o-nhap-popup" placeholder="Nhập tên trò chuyện...">
                        <div id="tao-tro-chuyen-thong-bao" class="thong-bao-popup"></div>
                        <div class="popup-nut-hang">
                            <button id="huy-tao-tro-chuyen" class="nut-phu">Hủy</button>
                            <button id="xac-nhan-tao-tro-chuyen" class="nut-chinh">Tạo</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(popup);

            popup.querySelector('#dong-popup-tao-tro-chuyen')
                .addEventListener('click', function () { dong(popup); });
            popup.querySelector('#huy-tao-tro-chuyen')
                .addEventListener('click', function () { dong(popup); });

            const oTen = popup.querySelector('#ten-tro-chuyen-moi');
            popup.querySelector('#xac-nhan-tao-tro-chuyen').addEventListener('click', async function () {
                const ten = oTen.value.trim();
                if (!ten) {
                    popup.querySelector('#tao-tro-chuyen-thong-bao').textContent = 'Vui lòng nhập tên.';
                    return;
                }
                await xuLyTaoTroChuyen(ten, popup);
            });

            oTen.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    popup.querySelector('#xac-nhan-tao-tro-chuyen').click();
                }
            });

            popup.addEventListener('click', function (e) {
                if (e.target === popup) dong(popup);
            });
        }

        const oTenReset = popup.querySelector('#ten-tro-chuyen-moi');
        if (oTenReset) oTenReset.value = '';
        const tbReset = popup.querySelector('#tao-tro-chuyen-thong-bao');
        if (tbReset) tbReset.textContent = '';

        mo(popup);
        setTimeout(function () { if (oTenReset) oTenReset.focus(); }, 100);
    }

    async function xuLyTaoTroChuyen(ten, popup) {
        const idDuAn = window.__ID_DU_AN_DANG_XEM;
        if (!idDuAn) return;

        const tb = popup.querySelector('#tao-tro-chuyen-thong-bao');
        const nut = popup.querySelector('#xac-nhan-tao-tro-chuyen');
        if (nut) nut.disabled = true;
        if (tb) tb.textContent = 'Đang tạo...';

        try {
            const ph = await fetch('/api/tao-tro-chuyen', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_du_an: idDuAn, ten: ten }),
            });
            const dl = await ph.json();

            if (dl && dl.thanh_cong) {
                // LƯU VÀO LOCALSTORAGE NẾU LÀ KHÁCH
                if (dl.tam && dl.tro_chuyen && typeof window.luuTroChuyenKhach === 'function') {
                    window.luuTroChuyenKhach(dl.tro_chuyen);
                }
                dong(popup);
                if (typeof window.taiDanhSachTroChuyen === 'function') {
                    window.taiDanhSachTroChuyen(idDuAn);
                }
                if (dl.tro_chuyen) {
                    moChatDuAn(idDuAn, dl.tro_chuyen.id, dl.tro_chuyen.ten);
                }
            } else {
                if (tb) tb.textContent = (dl && dl.loi) || 'Không tạo được trò chuyện.';
            }
        } catch (e) {
            if (tb) tb.textContent = 'Lỗi kết nối: ' + e.message;
        } finally {
            if (nut) nut.disabled = false;
        }
    }

    /* ------------------------------------------------------------
       NEW CHAT
       ------------------------------------------------------------ */
    async function xuLyNewChat() {
        dongMenuTrai();
        try {
            const ph = await fetch('/api/tao-chat-nhanh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            const dl = await ph.json();

            const khung = lay('danh-sach-tin-nhan');
            if (khung) khung.innerHTML = '';

            if (dl && dl.thanh_cong && dl.tam && dl.chat) {
                // Lưu chat nhanh vào localStorage cho khách
                if (typeof window.luuChatNhanhKhach === 'function') {
                    window.luuChatNhanhKhach(dl.chat);
                }
                window.__ID_CHAT_NHANH_HIEN_TAI = dl.chat.id;
            }

            if (typeof window.themTinNhanRong === 'function') {
                window.themTinNhanRong('Nói điều ước đi 🔥🐉');
            }
            if (typeof window.taiDanhSachChatNhanh === 'function') {
                window.taiDanhSachChatNhanh();
            }
        } catch (e) {
            const khung = lay('danh-sach-tin-nhan');
            if (khung) khung.innerHTML = '';
            if (typeof window.themTinNhanRong === 'function') {
                window.themTinNhanRong('Nói điều ước đi 🔥🐉');
            }
        }
    }

    /* ------------------------------------------------------------
       ĐĂNG XUẤT
       ------------------------------------------------------------ */
    async function xuLyDangXuat() {
        try { await fetch('/api/dang-xuat', { method: 'POST' }); } catch (e) {}
        try {
            localStorage.removeItem('rong_than_du_an_khach');
            localStorage.removeItem('rong_than_chat_nhanh_khach');
            localStorage.removeItem('rong_than_tro_chuyen_khach');
            localStorage.removeItem('rong_than_tin_nhan_khach');
        } catch (e) {}
        window.location.reload();
    }

    /* ------------------------------------------------------------
       POPUP XÁC NHẬN XÓA
       ------------------------------------------------------------ */
    let hamDongYXoaHienTai = null;

    function moXacNhanXoa(noiDung, hamDongY) {
        const el = lay('xac-nhan-noi-dung');
        if (el) el.textContent = noiDung || 'Bạn có chắc muốn xóa?';
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
            try { ham(); } catch (e) { console.error(e); }
        }
    }

    /* ------------------------------------------------------------
       GẮN SỰ KIỆN
       ------------------------------------------------------------ */
    function ganToanBoSuKien() {
        ganSuKien('nut-menu-trai', 'click', moMenuTrai);
        ganSuKien('dong-menu-trai', 'click', dongMenuTrai);
        ganSuKien('nut-menu-phai', 'click', moMenuPhai);
        ganSuKien('dong-menu-phai', 'click', dongMenuPhai);

        ganSuKien('nut-cai-dat', 'click', moCaiDat);
        ganSuKien('dong-cai-dat', 'click', dongCaiDat);
        ganSuKien('nut-mo-key', 'click', moTrangKey);
        ganSuKien('nut-mo-doi-mat-khau', 'click', moPopupDoiMatKhau);
        ganSuKien('dong-key', 'click', dongTrangKey);
        ganSuKien('dong-popup-doi-mat-khau', 'click', dongPopupDoiMatKhau);
        ganSuKien('nut-huy-doi-mk', 'click', dongPopupDoiMatKhau);

        ganSuKien('nut-mo-logs', 'click', moTrangLogs);
        ganSuKien('dong-logs', 'click', dongTrangLogs);

        ganSuKien('nut-mo-cay', 'click', moTrangCay);
        ganSuKien('dong-cay', 'click', dongTrangCay);

        ganSuKien('nut-mo-dang-ky', 'click', moPopupDangKy);
        ganSuKien('dong-popup-dang-ky', 'click', dongPopupDangKy);
        ganSuKien('nut-mo-dang-nhap', 'click', moPopupDangNhap);
        ganSuKien('dong-popup-dang-nhap', 'click', dongPopupDangNhap);

        ganSuKien('nut-huy-xoa', 'click', dongXacNhanXoa);
        ganSuKien('nut-dong-y-xoa', 'click', dongYXoa);

        ganSuKien('nut-new-chat', 'click', xuLyNewChat);
        ganSuKien('nut-dang-xuat', 'click', xuLyDangXuat);

        ganSuKien('nut-mo-trang-du-an', 'click', moTrangDuAn);
        ganSuKien('dong-trang-du-an', 'click', dongTrangDuAn);
        ganSuKien('nut-tao-du-an-trong-trang', 'click', moPopupTaoDuAn);

        ganSuKien('dong-chi-tiet-du-an', 'click', dongChiTietDuAn);
        ganSuKien('nut-tao-tro-chuyen-trong-du-an', 'click', moPopupTaoTroChuyen);

        document.querySelectorAll('.tab-nut').forEach(function (btn) {
            btn.addEventListener('click', function () {
                doiTab(btn.dataset.tab);
            });
        });

        ganSuKien('nut-quay-lai-du-an', 'click', quayLaiDuAn);

        ['popup-dang-ky', 'popup-dang-nhap', 'popup-xac-nhan-xoa', 'popup-doi-mat-khau']
            .forEach(function (idPopup) {
                const el = lay(idPopup);
                if (el) {
                    el.addEventListener('click', function (e) {
                        if (e.target === el) dong(el);
                    });
                }
            });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                ['menu-trai', 'menu-phai', 'trang-cai-dat', 'trang-key',
                 'trang-logs', 'trang-cay', 'trang-du-an', 'trang-chi-tiet-du-an',
                 'trang-chat-du-an']
                    .forEach(function (id) { dong(lay(id)); });
                ['popup-dang-ky', 'popup-dang-nhap', 'popup-xac-nhan-xoa',
                 'popup-doi-mat-khau', 'popup-tao-du-an', 'popup-tao-tro-chuyen']
                    .forEach(function (id) { dong(lay(id)); });
            }
        });
    }

    /* ------------------------------------------------------------
       XUẤT TOÀN CỤC
       ------------------------------------------------------------ */
    window.moXacNhanXoa = moXacNhanXoa;
    window.moMenuTrai = moMenuTrai;
    window.dongMenuTrai = dongMenuTrai;
    window.moMenuPhai = moMenuPhai;
    window.dongMenuPhai = dongMenuPhai;
    window.moTrangKey = moTrangKey;
    window.moTrangLogs = moTrangLogs;
    window.moTrangCay = moTrangCay;
    window.moTrangDuAn = moTrangDuAn;
    window.moChiTietDuAn = moChiTietDuAn;
    window.moChatDuAn = moChatDuAn;
    window.moPopupDangKy = moPopupDangKy;
    window.moPopupDangNhap = moPopupDangNhap;
    window.moPopupTaoDuAn = moPopupTaoDuAn;
    window.moPopupTaoTroChuyen = moPopupTaoTroChuyen;
    window.xuLyNewChat = xuLyNewChat;
    window.hien = hien;
    window.an = an;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ganToanBoSuKien);
    } else {
        ganToanBoSuKien();
    }

})();
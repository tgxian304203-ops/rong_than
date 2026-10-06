/* ============================================================
   app.js - Khởi động chung giao diện Rồng Thần
   ------------------------------------------------------------
   ĐÃ SỬA: Vẽ danh sách dự án/chat nhanh vào trang riêng.
           Hỗ trợ localStorage cho khách.
   ============================================================ */

(function () {
    'use strict';

    const KHOA_LS_DU_AN = 'rong_than_du_an_khach';
    const KHOA_LS_CHAT = 'rong_than_chat_nhanh_khach';
    let laKhach = false;

    /* ============================================================
       HÀM TIỆN ÍCH
       ============================================================ */
    function layKhungTinNhan() {
        return document.getElementById('danh-sach-tin-nhan');
    }

    function cuonXuongCuoi() {
        const k = layKhungTinNhan();
        if (k) k.scrollTop = k.scrollHeight;
    }

    function taoBongBong(noiDung, loai) {
        const bong = document.createElement('div');
        bong.classList.add('tin-nhan', 'tin-' + loai);

        const avt = document.createElement('div');
        avt.classList.add('tin-avatar');
        avt.textContent = loai === 'rong' ? '🐉' : (loai === 'nguoi' ? '👤' : 'ℹ️');

        const noi = document.createElement('div');
        noi.classList.add('tin-noi-dung');
        noi.innerHTML = String(noiDung || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>');

        bong.appendChild(avt);
        bong.appendChild(noi);
        return bong;
    }

    function themTinNhanRong(noiDung) {
        const k = layKhungTinNhan();
        if (!k) return;
        k.appendChild(taoBongBong(noiDung, 'rong'));
        cuonXuongCuoi();
    }

    function themTinNhanNguoi(noiDung) {
        const k = layKhungTinNhan();
        if (!k) return;
        k.appendChild(taoBongBong(noiDung, 'nguoi'));
        cuonXuongCuoi();
    }

    function themTinNhanHeThong(noiDung) {
        const k = layKhungTinNhan();
        if (!k) return;
        k.appendChild(taoBongBong(noiDung, 'he-thong'));
        cuonXuongCuoi();
    }

    /* ============================================================
       KIỂM TRA PHIÊN
       ============================================================ */
    async function kiemTraPhien() {
        try {
            const ph = await fetch('/api/phien');
            const dl = await ph.json();
            laKhach = !(dl && dl.da_dang_nhap);
        } catch (e) {
            laKhach = true;
        }
        return laKhach;
    }

    /* ============================================================
       LOCALSTORAGE CHO KHÁCH
       ============================================================ */
    function docLS(khoa) {
        try {
            const raw = localStorage.getItem(khoa);
            if (!raw) return [];
            const ds = JSON.parse(raw);
            return Array.isArray(ds) ? ds : [];
        } catch (e) { return []; }
    }

    function ghiLS(khoa, ds) {
        try { localStorage.setItem(khoa, JSON.stringify(ds || [])); } catch (e) {}
    }

    // Hàm toàn cục — gọi từ quan_ly_menu.js
    function luuDuAnKhach(duAn) {
        const ds = docLS(KHOA_LS_DU_AN);
        ds.push(duAn);
        ghiLS(KHOA_LS_DU_AN, ds);
    }

    function luuChatNhanhKhach(chat) {
        let ds = docLS(KHOA_LS_CHAT);
        ds.push(chat);
        // Khách không giới hạn, nhưng để an toàn giữ 50 cái
        if (ds.length > 50) ds = ds.slice(-50);
        ghiLS(KHOA_LS_CHAT, ds);
    }

    /* ============================================================
       VẼ DANH SÁCH DỰ ÁN
       ============================================================ */
    function taoMucDuAn(duAn) {
        const muc = document.createElement('div');
        muc.classList.add('muc-du-an');

        const nut = document.createElement('button');
        nut.classList.add('muc-menu', 'muc-du-an-nut');
        nut.type = 'button';
        nut.innerHTML = '📁 <span class="muc-chu">' +
            String(duAn.ten || 'Dự án').replace(/</g, '&lt;') + '</span>';
        nut.addEventListener('click', function () {
            if (typeof window.moDuAn === 'function') {
                window.moDuAn(duAn.id);
            }
        });
        muc.appendChild(nut);

        const nutXoa = document.createElement('button');
        nutXoa.classList.add('nut-xoa-muc');
        nutXoa.type = 'button';
        nutXoa.innerHTML = '&#10005;';
        nutXoa.addEventListener('click', function (e) {
            e.stopPropagation();
            const noiDung = 'Bạn có chắc muốn xóa dự án "' + duAn.ten + '"?';
            const hamDongY = async function () {
                if (laKhach) {
                    // Xóa khỏi localStorage
                    const ds = docLS(KHOA_LS_DU_AN)
                        .filter(function (d) { return d.id !== duAn.id; });
                    ghiLS(KHOA_LS_DU_AN, ds);
                    taiDanhSachDuAn();
                    return;
                }
                try {
                    const ph = await fetch('/api/xoa-du-an', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: duAn.id }),
                    });
                    const dl = await ph.json();
                    if (dl && dl.thanh_cong) {
                        taiDanhSachDuAn();
                    } else {
                        alert((dl && dl.loi) || 'Không xóa được dự án.');
                    }
                } catch (err) {
                    alert('Lỗi kết nối: ' + err.message);
                }
            };
            if (typeof window.moXacNhanXoa === 'function') {
                window.moXacNhanXoa(noiDung, hamDongY);
            } else if (confirm(noiDung)) {
                hamDongY();
            }
        });
        muc.appendChild(nutXoa);

        return muc;
    }

    function veDanhSachDuAn(ds) {
        const khung = document.getElementById('danh-sach-du-an-trong-trang');
        if (!khung) return;
        khung.innerHTML = '';
        if (!Array.isArray(ds) || ds.length === 0) {
            khung.innerHTML = '<div class="muc-trong">Chưa có dự án nào</div>';
            return;
        }
        ds.forEach(function (d) {
            khung.appendChild(taoMucDuAn(d));
        });
    }

    async function taiDanhSachDuAn() {
        if (laKhach) {
            veDanhSachDuAn(docLS(KHOA_LS_DU_AN));
            return;
        }
        try {
            const ph = await fetch('/api/danh-sach-du-an');
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veDanhSachDuAn(dl.danh_sach);
            } else {
                veDanhSachDuAn([]);
            }
        } catch (e) {
            veDanhSachDuAn([]);
        }
    }

    /* ============================================================
       VẼ DANH SÁCH CHAT NHANH
       ============================================================ */
    function taoMucChatNhanh(chat) {
        const muc = document.createElement('div');
        muc.classList.add('muc-chat-nhanh');

        const nut = document.createElement('button');
        nut.classList.add('muc-menu', 'muc-chat-nut');
        nut.type = 'button';
        nut.innerHTML = '💬 <span class="muc-chu">' +
            String(chat.ten || chat.tieu_de || 'Chat').replace(/</g, '&lt;') + '</span>';
        nut.addEventListener('click', function () {
            if (typeof window.moChatNhanh === 'function') {
                window.moChatNhanh(chat.id);
            }
        });
        muc.appendChild(nut);

        const nutXoa = document.createElement('button');
        nutXoa.classList.add('nut-xoa-muc');
        nutXoa.type = 'button';
        nutXoa.innerHTML = '&#10005;';
        nutXoa.addEventListener('click', function (e) {
            e.stopPropagation();
            const tenChat = chat.ten || chat.tieu_de || 'chat này';
            const noiDung = 'Bạn có chắc muốn xóa "' + tenChat + '"?';
            const hamDongY = async function () {
                if (laKhach) {
                    const ds = docLS(KHOA_LS_CHAT)
                        .filter(function (c) { return c.id !== chat.id; });
                    ghiLS(KHOA_LS_CHAT, ds);
                    taiDanhSachChatNhanh();
                    return;
                }
                try {
                    const ph = await fetch('/api/xoa-chat-nhanh', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: chat.id }),
                    });
                    const dl = await ph.json();
                    if (dl && dl.thanh_cong) {
                        taiDanhSachChatNhanh();
                    } else {
                        alert((dl && dl.loi) || 'Không xóa được chat.');
                    }
                } catch (err) {
                    alert('Lỗi kết nối: ' + err.message);
                }
            };
            if (typeof window.moXacNhanXoa === 'function') {
                window.moXacNhanXoa(noiDung, hamDongY);
            } else if (confirm(noiDung)) {
                hamDongY();
            }
        });
        muc.appendChild(nutXoa);

        return muc;
    }

    function veDanhSachChatNhanh(ds) {
        const khung = document.getElementById('danh-sach-chat-nhanh-trong-trang');
        if (!khung) return;
        khung.innerHTML = '';
        if (!Array.isArray(ds) || ds.length === 0) {
            khung.innerHTML = '<div class="muc-trong">Chưa có chat nào</div>';
            return;
        }
        ds.forEach(function (c) {
            khung.appendChild(taoMucChatNhanh(c));
        });
    }

    async function taiDanhSachChatNhanh() {
        if (laKhach) {
            veDanhSachChatNhanh(docLS(KHOA_LS_CHAT));
            return;
        }
        try {
            const ph = await fetch('/api/danh-sach-chat-nhanh');
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veDanhSachChatNhanh(dl.danh_sach);
            } else {
                veDanhSachChatNhanh([]);
            }
        } catch (e) {
            veDanhSachChatNhanh([]);
        }
    }

    /* ============================================================
       PHIÊN ĐĂNG NHẬP (hiện/ẩn nút)
       ============================================================ */
    async function taiThongTinPhien() {
        try {
            const ph = await fetch('/api/phien');
            const dl = await ph.json();

            const khuKhach = document.getElementById('nguoi-dung-khach');
            const khuDN = document.getElementById('nguoi-dung-da-dang-nhap');
            const oTen = document.getElementById('ten-nguoi-dung');
            const nutDoiMK = document.getElementById('nut-mo-doi-mat-khau');

            if (dl && dl.da_dang_nhap) {
                laKhach = false;
                if (khuKhach) khuKhach.classList.add('an');
                if (khuDN) khuDN.classList.remove('an');
                if (oTen) oTen.textContent = dl.ten_dang_nhap || 'Người dùng';
                if (nutDoiMK) nutDoiMK.classList.remove('an');
            } else {
                laKhach = true;
                if (khuKhach) khuKhach.classList.remove('an');
                if (khuDN) khuDN.classList.add('an');
                if (nutDoiMK) nutDoiMK.classList.add('an');
            }
        } catch (e) {}
    }

    /* ============================================================
       KIỂM TRA + KHỞI ĐỘNG
       ============================================================ */
    function kiemTraMoiTruong() {
        const can = ['themTinNhanRong','themTinNhanNguoi','themTinNhanHeThong','moXacNhanXoa'];
        const thieu = can.filter(function (t) { return typeof window[t] !== 'function'; });
        if (thieu.length) console.warn('[Rồng Thần] Thiếu hàm:', thieu.join(', '));
    }

    function kiemTraNutChinh() {
        const can = ['nut-gui','nut-menu-trai','nut-menu-phai','nut-dinh-kem'];
        const thieu = can.filter(function (id) { return !document.getElementById(id); });
        if (thieu.length) console.warn('[Rồng Thần] Thiếu nút:', thieu.join(', '));
    }

    async function kiemTraKetNoi() {
        try {
            const ph = await fetch('/api/phien');
            if (!ph.ok && ph.status !== 401) {
                themTinNhanHeThong('⚠️ Server phản hồi mã ' + ph.status);
            }
        } catch (e) {
            themTinNhanHeThong('⚠️ Không kết nối được server.');
        }
    }

    async function khoiDong() {
        console.log('%c🌕🐉 Rồng Thần', 'color:#4ade80;font-size:16px;font-weight:bold;');

        await taiThongTinPhien();

        // Hiện chào nếu khung trống
        const khung = layKhungTinNhan();
        if (khung && khung.children.length === 0) {
            themTinNhanRong('Nói điều ước đi 🔥🐉');
        }

        kiemTraMoiTruong();
        kiemTraNutChinh();
        await kiemTraKetNoi();

        // Tải danh sách
        taiDanhSachDuAn();
        taiDanhSachChatNhanh();
    }

    /* ============================================================
       XUẤT TOÀN CỤC
       ============================================================ */
    window.themTinNhanRong = themTinNhanRong;
    window.themTinNhanNguoi = themTinNhanNguoi;
    window.themTinNhanHeThong = themTinNhanHeThong;
    window.taiDanhSachDuAn = taiDanhSachDuAn;
    window.taiDanhSachChatNhanh = taiDanhSachChatNhanh;
    window.veDanhSachDuAn = veDanhSachDuAn;
    window.veDanhSachChatNhanh = veDanhSachChatNhanh;
    window.taiThongTinPhien = taiThongTinPhien;
    window.luuDuAnKhach = luuDuAnKhach;
    window.luuChatNhanhKhach = luuChatNhanhKhach;

    window.addEventListener('error', function (e) {
        console.error('[Rồng Thần] Lỗi:', e.message);
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

})();
/* ============================================================
   app.js - Khởi động chung giao diện Rồng Thần
   ------------------------------------------------------------
   ĐÃ SỬA:
     - Thêm luuTroChuyenKhach.
     - Sửa tên chat nhanh sau tin nhắn đầu.
   ============================================================ */

(function () {
    'use strict';

    const KHOA_LS_DU_AN = 'rong_than_du_an_khach';
    const KHOA_LS_CHAT = 'rong_than_chat_nhanh_khach';
    const KHOA_LS_TRO_CHUYEN = 'rong_than_tro_chuyen_khach';
    const KHOA_LS_TIN_NHAN = 'rong_than_tin_nhan_khach';
    let laKhach = false;

    /* ============================================================
       HÀM TIỆN ÍCH CHUNG
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

    function luuDuAnKhach(duAn) {
        const ds = docLS(KHOA_LS_DU_AN);
        ds.push(duAn);
        ghiLS(KHOA_LS_DU_AN, ds);
    }

    function luuChatNhanhKhach(chat) {
        let ds = docLS(KHOA_LS_CHAT);
        ds.push(chat);
        if (ds.length > 50) ds = ds.slice(-50);
        ghiLS(KHOA_LS_CHAT, ds);
    }

    // LƯU TRÒ CHUYỆN KHÁCH (MỚI)
    function luuTroChuyenKhach(tro) {
        let ds = docLS(KHOA_LS_TRO_CHUYEN);
        ds.push(tro);
        ghiLS(KHOA_LS_TRO_CHUYEN, ds);
    }

    // LƯU TIN NHẮN KHÁCH (MỚI) — dùng cho chat trong dự án
    function luuTinNhanKhach(idDuAn, idTroChuyen, vaiTro, noiDung) {
        let ds = docLS(KHOA_LS_TIN_NHAN);
        ds.push({
            id_du_an: idDuAn,
            id_tro_chuyen: idTroChuyen,
            vai_tro: vaiTro,
            noi_dung: noiDung,
            thoi_gian: Date.now(),
        });
        ghiLS(KHOA_LS_TIN_NHAN, ds);
    }

    /* ============================================================
       CẬP NHẬT TÊN CHAT NHANH (giống ChatGPT)
       Lấy dòng đầu tiên của tin nhắn đầu làm tên.
       ============================================================ */
    function capNhatTenChatNhanh(idChat, noiDung) {
        if (!idChat || !noiDung) return;

        // Lấy dòng đầu tiên (dừng ở \n hoặc hết chuỗi)
        let ten = String(noiDung).split('\n')[0].trim();
        if (!ten) return;
        // Giới hạn 50 ký tự
        if (ten.length > 50) ten = ten.slice(0, 50) + '...';

        if (laKhach) {
            // Khách → sửa trong localStorage
            const ds = docLS(KHOA_LS_CHAT);
            for (let i = 0; i < ds.length; i++) {
                if (ds[i].id === idChat) {
                    ds[i].ten = ten;
                    ds[i].tin_nhan_dau = noiDung;
                    break;
                }
            }
            ghiLS(KHOA_LS_CHAT, ds);
        } else {
            // Tài khoản → gọi server cập nhật
            fetch('/api/doi-ten-chat-nhanh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: idChat, ten: ten }),
            }).catch(function () {});
        }

        // Vẽ lại danh sách
        taiDanhSachChatNhanh();
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
            if (typeof window.moChiTietDuAn === 'function') {
                window.moChiTietDuAn(duAn.id, duAn.ten);
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
            khung.innerHTML = '<div class="muc-trong">Chưa có dự án nào. Bấm [+] để tạo.</div>';
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
       VẼ CHAT NHANH VÀO MENU TRÁI
       ============================================================ */
    function taoMucChatNhanhMenu(chat) {
        const muc = document.createElement('div');
        muc.classList.add('muc-chat-nhanh');

        const nut = document.createElement('button');
        nut.classList.add('muc-menu', 'muc-chat-nut');
        nut.type = 'button';
        nut.innerHTML = '💬 <span class="muc-chu">' +
            String(chat.ten || 'Chat mới').replace(/</g, '&lt;') + '</span>';
        nut.addEventListener('click', function () {
            if (typeof window.moChatNhanh === 'function') {
                window.moChatNhanh(chat.id);
            } else if (window.dongMenuTrai) {
                window.dongMenuTrai();
            }
        });
        muc.appendChild(nut);

        const nutXoa = document.createElement('button');
        nutXoa.classList.add('nut-xoa-muc');
        nutXoa.type = 'button';
        nutXoa.innerHTML = '&#10005;';
        nutXoa.addEventListener('click', function (e) {
            e.stopPropagation();
            const tenChat = chat.ten || 'chat này';
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

    function veDanhSachChatNhanhMenu(ds) {
        const khung = document.getElementById('danh-sach-chat-nhanh-menu');
        if (!khung) return;
        khung.innerHTML = '';
        if (!Array.isArray(ds) || ds.length === 0) {
            return;
        }
        ds.slice(0, 10).forEach(function (c) {
            khung.appendChild(taoMucChatNhanhMenu(c));
        });
    }

    async function taiDanhSachChatNhanh() {
        if (laKhach) {
            veDanhSachChatNhanhMenu(docLS(KHOA_LS_CHAT));
            return;
        }
        try {
            const ph = await fetch('/api/danh-sach-chat-nhanh');
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veDanhSachChatNhanhMenu(dl.danh_sach);
            } else {
                veDanhSachChatNhanhMenu([]);
            }
        } catch (e) {
            veDanhSachChatNhanhMenu([]);
        }
    }

    /* ============================================================
       TRÒ CHUYỆN TRONG DỰ ÁN
       ============================================================ */
    function taoMucTroChuyen(tro) {
        const muc = document.createElement('div');
        muc.classList.add('muc-du-an');

        const nut = document.createElement('button');
        nut.classList.add('muc-menu', 'muc-du-an-nut');
        nut.type = 'button';
        nut.innerHTML = '💬 <span class="muc-chu">' +
            String(tro.ten || 'Trò chuyện').replace(/</g, '&lt;') + '</span>';
        nut.addEventListener('click', function () {
            if (typeof window.moChatDuAn === 'function') {
                window.moChatDuAn(window.__ID_DU_AN_DANG_XEM, tro.id, tro.ten);
            }
        });
        muc.appendChild(nut);

        const nutXoa = document.createElement('button');
        nutXoa.classList.add('nut-xoa-muc');
        nutXoa.type = 'button';
        nutXoa.innerHTML = '&#10005;';
        nutXoa.addEventListener('click', function (e) {
            e.stopPropagation();
            const noiDung = 'Bạn có chắc muốn xóa trò chuyện "' + tro.ten + '"?';
            const hamDongY = async function () {
                if (laKhach) {
                    let ds = docLS(KHOA_LS_TRO_CHUYEN)
                        .filter(function (t) { return t.id !== tro.id; });
                    ghiLS(KHOA_LS_TRO_CHUYEN, ds);
                    // Xóa tin nhắn
                    let dsTN = docLS(KHOA_LS_TIN_NHAN)
                        .filter(function (t) { return t.id_tro_chuyen !== tro.id; });
                    ghiLS(KHOA_LS_TIN_NHAN, dsTN);
                    taiDanhSachTroChuyen(window.__ID_DU_AN_DANG_XEM);
                    return;
                }
                try {
                    const ph = await fetch('/api/xoa-tro-chuyen', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            id_du_an: window.__ID_DU_AN_DANG_XEM,
                            id_tro_chuyen: tro.id,
                        }),
                    });
                    const dl = await ph.json();
                    if (dl && dl.thanh_cong) {
                        taiDanhSachTroChuyen(window.__ID_DU_AN_DANG_XEM);
                    } else {
                        alert((dl && dl.loi) || 'Không xóa được.');
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

    function veDanhSachTroChuyen(ds) {
        const khung = document.getElementById('danh-sach-tro-chuyen-trong-du-an');
        if (!khung) return;
        khung.innerHTML = '';
        if (!Array.isArray(ds) || ds.length === 0) {
            khung.innerHTML = '<div class="muc-trong">Chưa có trò chuyện nào. Bấm [+] để tạo.</div>';
            return;
        }
        ds.forEach(function (t) {
            khung.appendChild(taoMucTroChuyen(t));
        });
    }

    async function taiDanhSachTroChuyen(idDuAn) {
        if (!idDuAn) return;
        if (laKhach) {
            const ds = docLS(KHOA_LS_TRO_CHUYEN)
                .filter(function (t) { return t.id_du_an === idDuAn; });
            veDanhSachTroChuyen(ds);
            return;
        }
        try {
            const ph = await fetch('/api/danh-sach-tro-chuyen?id_du_an=' + encodeURIComponent(idDuAn));
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veDanhSachTroChuyen(dl.danh_sach);
            } else {
                veDanhSachTroChuyen([]);
            }
        } catch (e) {
            veDanhSachTroChuyen([]);
        }
    }

    /* ============================================================
       TIN NHẮN TRONG TRÒ CHUYỆN
       ============================================================ */
    function veTinNhanTrongDuAn(ds) {
        const khung = document.getElementById('danh-sach-tin-nhan-du-an');
        if (!khung) return;
        khung.innerHTML = '';
        if (!Array.isArray(ds) || ds.length === 0) {
            khung.appendChild(taoBongBong('Nói điều ước đi 🔥🐉', 'rong'));
            return;
        }
        ds.forEach(function (t) {
            const vaiTro = t.vai_tro === 'nguoi' ? 'nguoi'
                : (t.vai_tro === 'rong' ? 'rong' : 'he-thong');
            khung.appendChild(taoBongBong(t.noi_dung || '', vaiTro));
        });
        khung.scrollTop = khung.scrollHeight;
    }

    async function taiTinNhanTroChuyen(idDuAn, idTroChuyen) {
        if (!idDuAn || !idTroChuyen) return;
        if (laKhach) {
            const ds = docLS(KHOA_LS_TIN_NHAN)
                .filter(function (t) {
                    return t.id_du_an === idDuAn && t.id_tro_chuyen === idTroChuyen;
                });
            veTinNhanTrongDuAn(ds);
            return;
        }
        try {
            const ph = await fetch('/api/tin-nhan-tro-chuyen?id_du_an=' +
                encodeURIComponent(idDuAn) + '&id_tro_chuyen=' +
                encodeURIComponent(idTroChuyen));
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veTinNhanTrongDuAn(dl.danh_sach);
            } else {
                veTinNhanTrongDuAn([]);
            }
        } catch (e) {
            veTinNhanTrongDuAn([]);
        }
    }

    /* ============================================================
       PHIÊN ĐĂNG NHẬP
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
       KHỞI ĐỘNG
       ============================================================ */
    async function khoiDong() {
        console.log('%c🌕🐉 Rồng Thần', 'color:#4ade80;font-size:16px;font-weight:bold;');

        await taiThongTinPhien();

        const khung = layKhungTinNhan();
        if (khung && khung.children.length === 0) {
            themTinNhanRong('Nói điều ước đi 🔥🐉');
        }

        await kiemTraPhien();

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
    window.taiDanhSachTroChuyen = taiDanhSachTroChuyen;
    window.taiTinNhanTroChuyen = taiTinNhanTroChuyen;
    window.veDanhSachDuAn = veDanhSachDuAn;
    window.veDanhSachChatNhanhMenu = veDanhSachChatNhanhMenu;
    window.veDanhSachTroChuyen = veDanhSachTroChuyen;
    window.veTinNhanTrongDuAn = veTinNhanTrongDuAn;
    window.taiThongTinPhien = taiThongTinPhien;
    window.luuDuAnKhach = luuDuAnKhach;
    window.luuChatNhanhKhach = luuChatNhanhKhach;
    window.luuTroChuyenKhach = luuTroChuyenKhach;
    window.luuTinNhanKhach = luuTinNhanKhach;
    window.capNhatTenChatNhanh = capNhatTenChatNhanh;

    window.addEventListener('error', function (e) {
        console.error('[Rồng Thần] Lỗi:', e.message);
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

})();
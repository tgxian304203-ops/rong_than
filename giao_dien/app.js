/* ============================================================
   app.js - Khởi động chung giao diện Rồng Thần
   ------------------------------------------------------------
   ĐÃ SỬA: Bổ sung các hàm tiện ích cho chat + danh sách:
     - themTinNhanRong(noiDung)   : thêm tin nhắn Rồng Thần
     - themTinNhanNguoi(noiDung)  : thêm tin nhắn Người dùng
     - themTinNhanHeThong(noiDung): thêm tin nhắn hệ thống
     - taiDanhSachDuAn()          : tải danh sách dự án
     - taiDanhSachChatNhanh()     : tải danh sách chat nhanh
     - veDanhSachDuAn(ds)         : vẽ danh sách dự án vào menu
     - veDanhSachChatNhanh(ds)    : vẽ danh sách chat nhanh vào menu
   ============================================================ */

(function () {
    'use strict';

    /* ============================================================
       PHẦN 1: KIỂM TRA MÔI TRƯỜNG
       ============================================================ */
    function kiemTraMoiTruong() {
        const canCo = [
            'themTinNhanRong',
            'themTinNhanNguoi',
            'themTinNhanHeThong',
            'moXacNhanXoa',
        ];
        const thieu = canCo.filter(function (ten) {
            return typeof window[ten] !== 'function';
        });
        if (thieu.length > 0) {
            console.warn('[Rồng Thần] Thiếu hàm toàn cục:', thieu.join(', '));
        }
        return thieu.length === 0;
    }

    function kiemTraNutChinh() {
        const nutCanCo = ['nut-gui', 'nut-menu-trai', 'nut-menu-phai', 'nut-dinh-kem'];
        const thieu = nutCanCo.filter(function (id) {
            return !document.getElementById(id);
        });
        if (thieu.length > 0) {
            console.warn('[Rồng Thần] Thiếu nút chính:', thieu.join(', '));
        }
        return thieu.length === 0;
    }

    async function kiemTraKetNoi() {
        try {
            const phanHoi = await fetch('/api/phien', { method: 'GET' });
            if (!phanHoi.ok && phanHoi.status !== 401) {
                thongBaoHeThong('⚠️ Server phản hồi mã ' + phanHoi.status + '.');
                return false;
            }
            return true;
        } catch (e) {
            thongBaoHeThong('⚠️ Không kết nối được server.');
            return false;
        }
    }

    function logPhienBan() {
        console.log('%c🌕🐉 Rồng Thần', 'color:#4ade80;font-size:16px;font-weight:bold;');
    }

    /* ============================================================
       PHẦN 2: HÀM THÊM TIN NHẮN
       ============================================================ */
    function layKhungTinNhan() {
        return document.getElementById('danh-sach-tin-nhan');
    }

    function cuonXuongCuoi() {
        const khung = layKhungTinNhan();
        if (khung) khung.scrollTop = khung.scrollHeight;
    }

    function taoBongBong(noiDung, loai) {
        const bong = document.createElement('div');
        bong.classList.add('tin-nhan', 'tin-' + loai);

        const avt = document.createElement('div');
        avt.classList.add('tin-avatar');
        avt.textContent = loai === 'rong' ? '🐉' : (loai === 'nguoi' ? '👤' : 'ℹ️');

        const noi = document.createElement('div');
        noi.classList.add('tin-noi-dung');
        // Cho phép xuống dòng
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
        const khung = layKhungTinNhan();
        if (!khung) return;
        khung.appendChild(taoBongBong(noiDung, 'rong'));
        cuonXuongCuoi();
    }

    function themTinNhanNguoi(noiDung) {
        const khung = layKhungTinNhan();
        if (!khung) return;
        khung.appendChild(taoBongBong(noiDung, 'nguoi'));
        cuonXuongCuoi();
    }

    function themTinNhanHeThong(noiDung) {
        const khung = layKhungTinNhan();
        if (!khung) return;
        khung.appendChild(taoBongBong(noiDung, 'he-thong'));
        cuonXuongCuoi();
    }

    /* ============================================================
       PHẦN 3: DANH SÁCH DỰ ÁN
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
            } else if (window.moMenuTrai) {
                window.moMenuTrai();
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

    function veDanhSachDuAn(danhSach) {
        const khung = document.getElementById('danh-sach-du-an');
        if (!khung) return;
        khung.innerHTML = '';
        if (!Array.isArray(danhSach) || danhSach.length === 0) {
            khung.innerHTML = '<div class="muc-trong">Chưa có gì</div>';
            return;
        }
        danhSach.forEach(function (duAn) {
            khung.appendChild(taoMucDuAn(duAn));
        });
    }

    async function taiDanhSachDuAn() {
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
       PHẦN 4: DANH SÁCH CHAT NHANH
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
            const tenChat = chat.ten || chat.tieu_de || 'chat này';
            const noiDung = 'Bạn có chắc muốn xóa "' + tenChat + '"?';
            const hamDongY = async function () {
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

    function veDanhSachChatNhanh(danhSach) {
        const khung = document.getElementById('danh-sach-chat-nhanh');
        if (!khung) return;
        khung.innerHTML = '';
        if (!Array.isArray(danhSach) || danhSach.length === 0) {
            khung.innerHTML = '<div class="muc-trong">Chưa có gì</div>';
            return;
        }
        danhSach.forEach(function (chat) {
            khung.appendChild(taoMucChatNhanh(chat));
        });
    }

    async function taiDanhSachChatNhanh() {
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
       PHẦN 5: KHỞI ĐỘNG
       ============================================================ */
    async function khoiDong() {
        logPhienBan();

        // Hiện tin nhắn chào nếu khung chat trống
        const khung = layKhungTinNhan();
        if (khung && khung.children.length === 0) {
            themTinNhanRong('Nói điều ước đi 🔥🐉');
        }

        kiemTraMoiTruong();
        kiemTraNutChinh();
        if (typeof fetch === 'function') {
            await kiemTraKetNoi();
        }

        // Tải danh sách dự án + chat nhanh
        taiDanhSachDuAn();
        taiDanhSachChatNhanh();

        // Tải thông tin phiên (khách hay tài khoản)
        taiThongTinPhien();
    }

    /* ============================================================
       PHẦN 6: PHIÊN ĐĂNG NHẬP
       ============================================================ */
    async function taiThongTinPhien() {
        try {
            const ph = await fetch('/api/phien');
            const dl = await ph.json();

            const khuKhach = document.getElementById('nguoi-dung-khach');
            const khuDangNhap = document.getElementById('nguoi-dung-da-dang-nhap');
            const oTen = document.getElementById('ten-nguoi-dung');
            const nutDoiMatKhau = document.getElementById('nut-mo-doi-mat-khau');

            if (dl && dl.da_dang_nhap) {
                if (khuKhach) khuKhach.classList.add('an');
                if (khuDangNhap) khuDangNhap.classList.remove('an');
                if (oTen) oTen.textContent = dl.ten_dang_nhap || 'Người dùng';
                if (nutDoiMatKhau) nutDoiMatKhau.classList.remove('an');
            } else {
                if (khuKhach) khuKhach.classList.remove('an');
                if (khuDangNhap) khuDangNhap.classList.add('an');
                if (nutDoiMatKhau) nutDoiMatKhau.classList.add('an');
            }
        } catch (e) {
            // Im lặng
        }
    }

    /* ============================================================
       XUẤT RA TOÀN CỤC
       ============================================================ */
    window.themTinNhanRong = themTinNhanRong;
    window.themTinNhanNguoi = themTinNhanNguoi;
    window.themTinNhanHeThong = themTinNhanHeThong;
    window.taiDanhSachDuAn = taiDanhSachDuAn;
    window.taiDanhSachChatNhanh = taiDanhSachChatNhanh;
    window.veDanhSachDuAn = veDanhSachDuAn;
    window.veDanhSachChatNhanh = veDanhSachChatNhanh;
    window.taiThongTinPhien = taiThongTinPhien;
    window.kiemTraMoiTruong = kiemTraMoiTruong;
    window.thongBaoHeThong = themTinNhanHeThong;

    /* ============================================================
       XỬ LÝ LỖI TOÀN CỤC
       ============================================================ */
    window.addEventListener('error', function (e) {
        console.error('[Rồng Thần] Lỗi:', e.message, e.filename, e.lineno);
    });
    window.addEventListener('unhandledrejection', function (e) {
        console.error('[Rồng Thần] Promise bị từ chối:', e.reason);
    });

    /* ============================================================
       CHẠY KHI DOM SẴN SÀNG
       ============================================================ */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

})();
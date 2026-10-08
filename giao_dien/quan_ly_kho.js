/* ============================================================
   quan_ly_kho.js - Dán + quản lý URI 2 kho MongoDB
   ------------------------------------------------------------
   ĐÃ SỬA (Giai đoạn 1.5 — tách trang URI Kho riêng):
     - FIX 1: Chỉ xử lý trang URI Kho riêng.
     - FIX 2: Khách lưu sessionStorage (đóng tab mất).
     - FIX 3: Tài khoản gửi server lưu kho 1.

   ID không đổi:
     - o-uri-kho-1-2 + nut-run-kho-1-2
     - o-uri-kho-2-2 + nut-run-kho-2-2
   ============================================================ */

(function () {
    'use strict';

    const oKho1   = document.getElementById('o-uri-kho-1-2');
    const oKho2   = document.getElementById('o-uri-kho-2-2');
    const nutKho1 = document.getElementById('nut-run-kho-1-2');
    const nutKho2 = document.getElementById('nut-run-kho-2-2');

    if (!oKho1 || !oKho2 || !nutKho1 || !nutKho2) {
        return;
    }

    const KHOA_LS_1 = 'rong_than_uri_kho_1_khach';
    const KHOA_LS_2 = 'rong_than_uri_kho_2_khach';
    let laKhach = false;

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

    function cheUri(uri) {
        if (typeof uri !== 'string' || !uri) return '';
        const mau = /^(mongodb(?:\+srv)?:\/\/[^:]+:)([^@]+)(@.+)$/;
        const khop = uri.match(mau);
        if (khop) {
            const sao = '*'.repeat(Math.min(khop[2].length, 8));
            return khop[1] + sao + khop[3];
        }
        if (uri.length > 40) {
            return uri.slice(0, 20) + '...' + uri.slice(-15);
        }
        return uri;
    }

    function ghiLS(khoa, uri) {
        try {
            sessionStorage.setItem(khoa, uri || '');
        } catch (e) {}
    }

    function docLS(khoa) {
        try {
            return sessionStorage.getItem(khoa) || '';
        } catch (e) {
            return '';
        }
    }

    function hienTrangThai(nut, chu, mau) {
        if (!nut.dataset.chuGoc) {
            nut.dataset.chuGoc = nut.textContent;
        }
        nut.textContent = chu;
        nut.style.color = mau || '';
        setTimeout(function () {
            nut.textContent = nut.dataset.chuGoc;
            nut.style.color = '';
        }, 2500);
    }

    async function luuKho(soKho, oNhap, nut) {
        const uri = oNhap.value.trim();
        if (!uri) {
            hienTrangThai(nut, 'Trống', 'var(--do)');
            return;
        }

        if (!uri.startsWith('mongodb://') && !uri.startsWith('mongodb+srv://')) {
            hienTrangThai(nut, 'Sai định dạng', 'var(--do)');
            return;
        }

        nut.disabled = true;
        nut.textContent = '...';

        try {
            if (laKhach) {
                const khoa = soKho === 1 ? KHOA_LS_1 : KHOA_LS_2;
                ghiLS(khoa, uri);
                oNhap.value = cheUri(uri);
                hienTrangThai(nut, 'Đã lưu tạm', 'var(--chu-rong)');
            } else {
                const ph = await fetch('/api/luu-uri-kho', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ kho: soKho, uri: uri }),
                });
                const dl = await ph.json();
                if (dl && dl.thanh_cong) {
                    oNhap.value = cheUri(uri);
                    hienTrangThai(nut, 'Đã kết nối', 'var(--chu-rong)');
                } else {
                    hienTrangThai(nut, 'Lỗi', 'var(--do)');
                    alert((dl && dl.loi) || 'Không lưu được URI kho ' + soKho + '.');
                }
            }
        } catch (e) {
            hienTrangThai(nut, 'Lỗi', 'var(--do)');
            alert('Lỗi kết nối: ' + e.message);
        } finally {
            nut.disabled = false;
            if (nut.textContent === '...') {
                nut.textContent = nut.dataset.chuGoc || 'Run';
            }
        }
    }

    async function taiUriCu() {
        await kiemTraPhien();
        if (laKhach) {
            const u1 = docLS(KHOA_LS_1);
            const u2 = docLS(KHOA_LS_2);
            if (u1) oKho1.value = cheUri(u1);
            if (u2) oKho2.value = cheUri(u2);
            return;
        }
        try {
            const ph = await fetch('/api/lay-uri-kho');
            const dl = await ph.json();
            if (dl && dl.thanh_cong) {
                if (dl.kho_1) oKho1.value = cheUri(dl.kho_1);
                if (dl.kho_2) oKho2.value = cheUri(dl.kho_2);
            }
        } catch (e) {}
    }

    nutKho1.addEventListener('click', function (e) {
        e.preventDefault();
        luuKho(1, oKho1, nutKho1);
    });

    nutKho2.addEventListener('click', function (e) {
        e.preventDefault();
        luuKho(2, oKho2, nutKho2);
    });

    oKho1.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            luuKho(1, oKho1, nutKho1);
        }
    });

    oKho2.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            luuKho(2, oKho2, nutKho2);
        }
    });

    [oKho1, oKho2].forEach(function (oNhap) {
        oNhap.addEventListener('focus', function () {
            if (oNhap.value.includes('***')) {
                oNhap.value = '';
            }
        });
    });

    async function khoiDong() {
        await kiemTraPhien();
        await taiUriCu();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    window.taiUriKho = taiUriCu;
    window.cheUri = cheUri;

})();
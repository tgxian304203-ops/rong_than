/* ============================================================
   quan_ly_key_web.js - Dán + quản lý API Key tra web
   ------------------------------------------------------------
   ĐÃ SỬA:
     - Thêm hàm taiLaiKeyWeb() — reset phiên + reload key.
     - Sau khi đăng nhập → gọi hàm này để load key từ MongoDB.
   ============================================================ */

(function () {
    'use strict';

    const oKey     = document.getElementById('o-key-web-2');
    const nutRun   = document.getElementById('nut-run-key-web-2');
    const danhSach = document.getElementById('danh-sach-key-web-2');

    if (!oKey || !nutRun || !danhSach) {
        return;
    }

    const KHOA_LS = 'rong_than_key_web_khach';
    const THOI_GIAN_CAP_NHAT_QUOTA = 60 * 1000;
    let idHenQuota = null;
    let laKhach = false;
    let daKiemTraPhien = false;

    const BANG_PROVIDER = [
        { tien_to: 'serpjet',     provider: 'SERPJET' },
        { tien_to: 'tvly-',       provider: 'Tavily' },
        { tien_to: 'tavily-',     provider: 'Tavily' },
        { tien_to: 'bd_',         provider: 'Bright Data' },
        { tien_to: 'brightdata-', provider: 'Bright Data' },
    ];

    async function kiemTraPhien() {
        if (daKiemTraPhien) return laKhach;
        try {
            const ph = await fetch('/api/phien');
            const dl = await ph.json();
            laKhach = !(dl && dl.da_dang_nhap);
        } catch (e) {
            laKhach = true;
        }
        daKiemTraPhien = true;
        return laKhach;
    }

    function docLS() {
        try {
            const raw = sessionStorage.getItem(KHOA_LS);
            if (!raw) return [];
            const ds = JSON.parse(raw);
            return Array.isArray(ds) ? ds : [];
        } catch (e) {
            return [];
        }
    }

    function ghiLS(ds) {
        try {
            sessionStorage.setItem(KHOA_LS, JSON.stringify(ds || []));
        } catch (e) {}
    }

    function nhanDienProvider(key) {
        const k = String(key || '').trim().toLowerCase();
        for (let i = 0; i < BANG_PROVIDER.length; i++) {
            if (k.startsWith(BANG_PROVIDER[i].tien_to.toLowerCase())) {
                return BANG_PROVIDER[i].provider;
            }
        }
        return 'Khác';
    }

    function layClassQuota(phanTram) {
        if (phanTram <= 0) return 'quota-den';
        if (phanTram < 20) return 'quota-do';
        if (phanTram < 50) return 'quota-vang';
        return 'quota-xanh';
    }

    function taoTheKey(key, chiSo) {
        const the = document.createElement('div');
        the.classList.add('the-key');

        const hang = document.createElement('div');
        hang.classList.add('the-key-hang');

        const icon = document.createElement('span');
        icon.classList.add('the-key-icon');
        icon.textContent = '🌐';
        hang.appendChild(icon);

        const ten = document.createElement('span');
        ten.classList.add('the-key-ten');
        ten.textContent = key.provider || key.ten || 'Không rõ';
        hang.appendChild(ten);

        const so = document.createElement('span');
        so.classList.add('the-key-so');
        so.textContent = '#' + (chiSo + 1);
        hang.appendChild(so);

        const nutXoa = document.createElement('button');
        nutXoa.classList.add('nut-xoa-muc');
        nutXoa.type = 'button';
        nutXoa.innerHTML = '&#10005;';
        nutXoa.addEventListener('click', function () { xacNhanXoaKey(key); });
        hang.appendChild(nutXoa);

        the.appendChild(hang);

        const phanTram = typeof key.phan_tram === 'number' ? key.phan_tram : 100;
        const thanh = document.createElement('div');
        thanh.classList.add('thanh-quota');
        const fill = document.createElement('div');
        fill.classList.add('thanh-quota-fill', layClassQuota(phanTram));
        fill.style.width = Math.max(0, Math.min(100, phanTram)) + '%';
        thanh.appendChild(fill);
        the.appendChild(thanh);

        const pt = document.createElement('div');
        pt.classList.add('the-key-phan-tram');
        pt.textContent = phanTram + '% còn lại';
        the.appendChild(pt);

        return the;
    }

    function veDanhSach(ds) {
        danhSach.innerHTML = '';
        if (!Array.isArray(ds) || ds.length === 0) return;
        ds.forEach(function (key, i) {
            danhSach.appendChild(taoTheKey(key, i));
        });
    }

    async function taiDanhSach() {
        await kiemTraPhien();
        if (laKhach) {
            veDanhSach(docLS());
            return;
        }
        try {
            const ph = await fetch('/api/danh-sach-key-web');
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veDanhSach(dl.danh_sach);
            } else {
                veDanhSach([]);
            }
        } catch (e) {
            veDanhSach([]);
        }
    }

    async function luuKey() {
        const giaTri = oKey.value.trim();
        if (!giaTri) {
            alert('Vui lòng dán API Key tra web trước.');
            return;
        }

        nutRun.disabled = true;
        const chuCu = nutRun.textContent;
        nutRun.textContent = '...';

        try {
            await kiemTraPhien();

            if (laKhach) {
                const provider = nhanDienProvider(giaTri);
                const ds = docLS();
                ds.push({
                    id: 'khach-web-' + Date.now(),
                    provider: provider,
                    ten: provider,
                    phan_tram: 100,
                    key: giaTri,
                    ngay_tao: Date.now(),
                });
                ghiLS(ds);
                oKey.value = '';
                await taiDanhSach();
            } else {
                const ph = await fetch('/api/luu-key-web', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: giaTri }),
                });
                const dl = await ph.json();
                if (dl && dl.thanh_cong) {
                    oKey.value = '';
                    await taiDanhSach();
                } else {
                    alert((dl && dl.loi) || 'Không lưu được key.');
                }
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        } finally {
            nutRun.disabled = false;
            nutRun.textContent = chuCu;
        }
    }

    function xacNhanXoaKey(key) {
        const ten = key.provider || key.ten || 'Không rõ';
        const noiDung = 'Bạn có chắc muốn xóa key ' + ten + '?';

        const hamDongY = async function () {
            try {
                if (laKhach) {
                    const ds = docLS().filter(function (k) { return k.id !== key.id; });
                    ghiLS(ds);
                    await taiDanhSach();
                } else {
                    const ph = await fetch('/api/xoa-key-web', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: key.id }),
                    });
                    const dl = await ph.json();
                    if (dl && dl.thanh_cong) {
                        await taiDanhSach();
                    } else {
                        alert((dl && dl.loi) || 'Không xóa được key.');
                    }
                }
            } catch (e) {
                alert('Lỗi kết nối: ' + e.message);
            }
        };

        if (typeof window.moXacNhanXoa === 'function') {
            window.moXacNhanXoa(noiDung, hamDongY);
        } else if (confirm(noiDung)) {
            hamDongY();
        }
    }

    async function capNhatQuota() {
        if (laKhach) return;
        try {
            const ph = await fetch('/api/quota-key-web');
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veDanhSach(dl.danh_sach);
            }
        } catch (e) {}
    }

    function batDauCapNhatQuota() {
        if (idHenQuota) clearInterval(idHenQuota);
        idHenQuota = setInterval(capNhatQuota, THOI_GIAN_CAP_NHAT_QUOTA);
    }

    nutRun.addEventListener('click', function (e) {
        e.preventDefault();
        luuKey();
    });

    oKey.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            luuKey();
        }
    });

    // ============================================================
    // HÀM CÔNG KHAI: TẢI LẠI KEY WEB
    // ============================================================
    async function taiLaiKeyWeb() {
        daKiemTraPhien = false;   // Reset để check lại phiên
        await taiDanhSach();
    }

    async function khoiDong() {
        daKiemTraPhien = false;
        await taiDanhSach();
        batDauCapNhatQuota();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    window.taiDanhSachKeyWeb = taiDanhSach;
    window.taiLaiKeyWeb = taiLaiKeyWeb;

})();
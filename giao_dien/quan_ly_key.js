/* ============================================================
   quan_ly_key.js - Dán + quản lý API Key model (Boss + Tiểu Boss)
   ------------------------------------------------------------
   ĐÃ SỬA (Giai đoạn 1.5 — tách trang Key riêng):
     - FIX 1: Tách thành 2 khối độc lập:
              + BOSS: o-key-boss + nut-run-key-boss
                       + danh-sach-key-boss
              + TIỂU BOSS: o-key-tieu-boss + nut-run-key-tieu-boss
                       + danh-sach-key-tieu-boss
     - FIX 2: Khách lưu sessionStorage riêng theo từng loại.
     - FIX 3: Tài khoản gửi loai_nao="boss" / "tieu_boss".
     - FIX 4: Lấy danh sách + quota lọc theo loai_nao.
   ============================================================ */

(function () {
    'use strict';

    // ============================================================
    // HẰNG SỐ DÙNG CHUNG
    // ============================================================
    const THOI_GIAN_CAP_NHAT_QUOTA = 60 * 1000;

    const BANG_PROVIDER = [
        { tien_to: 'gsk_',    provider: 'Groq' },
        { tien_to: 'sk-or-',  provider: 'OpenRouter' },
        { tien_to: 'AIza',    provider: 'Gemini' },
        { tien_to: 'AQ.Ab',   provider: 'Gemini' },
    ];

    const KHOA_LS_BOSS      = 'rong_than_key_boss_khach';
    const KHOA_LS_TIEU_BOSS = 'rong_than_key_tieu_boss_khach';

    let laKhach = false;
    let daKiemTraPhien = false;

    // ============================================================
    // HÀM DÙNG CHUNG
    // ============================================================
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

    function docLS(khoaLS) {
        try {
            const raw = sessionStorage.getItem(khoaLS);
            if (!raw) return [];
            const ds = JSON.parse(raw);
            return Array.isArray(ds) ? ds : [];
        } catch (e) {
            return [];
        }
    }

    function ghiLS(khoaLS, ds) {
        try {
            sessionStorage.setItem(khoaLS, JSON.stringify(ds || []));
        } catch (e) {}
    }

    function nhanDienProvider(key) {
        const k = String(key || '').trim();
        for (let i = 0; i < BANG_PROVIDER.length; i++) {
            if (k.startsWith(BANG_PROVIDER[i].tien_to)) {
                return BANG_PROVIDER[i].provider;
            }
        }
        return null;
    }

    function layClassQuota(phanTram) {
        if (phanTram <= 0) return 'quota-den';
        if (phanTram < 20) return 'quota-do';
        if (phanTram < 50) return 'quota-vang';
        return 'quota-xanh';
    }

    function nhanProvider(ten) {
        const t = String(ten || '').toLowerCase();
        if (t.includes('groq'))       return 'Groq';
        if (t.includes('openrouter')) return 'OpenRouter';
        if (t.includes('gemini'))     return 'Gemini';
        return ten || 'Không rõ';
    }

    function taoTheKey(key, chiSo, hamXoa) {
        const the = document.createElement('div');
        the.classList.add('the-key');

        const hang = document.createElement('div');
        hang.classList.add('the-key-hang');

        const icon = document.createElement('span');
        icon.classList.add('the-key-icon');
        icon.textContent = '🔥🐉';
        hang.appendChild(icon);

        const ten = document.createElement('span');
        ten.classList.add('the-key-ten');
        ten.textContent = nhanProvider(key.provider || key.ten);
        hang.appendChild(ten);

        const so = document.createElement('span');
        so.classList.add('the-key-so');
        so.textContent = '#' + (chiSo + 1);
        hang.appendChild(so);

        const nutXoa = document.createElement('button');
        nutXoa.classList.add('nut-xoa-muc');
        nutXoa.type = 'button';
        nutXoa.innerHTML = '&#10005;';
        nutXoa.addEventListener('click', function () { hamXoa(key); });
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

    function veDanhSach(khung, ds, hamXoa) {
        if (!khung) return;
        khung.innerHTML = '';
        if (!Array.isArray(ds) || ds.length === 0) return;
        ds.forEach(function (key, i) {
            khung.appendChild(taoTheKey(key, i, hamXoa));
        });
    }

    function hoiXacNhan(noiDung, hamDongY) {
        if (typeof window.moXacNhanXoa === 'function') {
            window.moXacNhanXoa(noiDung, hamDongY);
        } else if (confirm(noiDung)) {
            hamDongY();
        }
    }

    // ============================================================
    // KHỐI BOSS
    // ============================================================
    const oKeyBoss    = document.getElementById('o-key-boss');
    const nutRunBoss  = document.getElementById('nut-run-key-boss');
    const dsBoss      = document.getElementById('danh-sach-key-boss');

    async function taiDanhSachBoss() {
        if (!dsBoss) return;
        await kiemTraPhien();

        if (laKhach) {
            veDanhSach(dsBoss, docLS(KHOA_LS_BOSS), xacNhanXoaBoss);
            return;
        }

        try {
            const ph = await fetch('/api/danh-sach-key?loai_nao=boss');
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veDanhSach(dsBoss, dl.danh_sach, xacNhanXoaBoss);
            } else {
                veDanhSach(dsBoss, [], xacNhanXoaBoss);
            }
        } catch (e) {
            veDanhSach(dsBoss, [], xacNhanXoaBoss);
        }
    }

    async function luuKeyBoss() {
        if (!oKeyBoss || !nutRunBoss) return;
        const giaTri = oKeyBoss.value.trim();
        if (!giaTri) {
            alert('Vui lòng dán API Key Boss trước.');
            return;
        }

        nutRunBoss.disabled = true;
        const chuCu = nutRunBoss.textContent;
        nutRunBoss.textContent = '...';

        try {
            await kiemTraPhien();

            if (laKhach) {
                const provider = nhanDienProvider(giaTri);
                if (!provider) {
                    alert('Không nhận diện được provider. Key phải bắt đầu bằng gsk_ (Groq), sk-or- (OpenRouter), AIza hoặc AQ.Ab (Gemini).');
                    return;
                }
                const ds = docLS(KHOA_LS_BOSS);
                ds.push({
                    id: 'khach-boss-' + Date.now(),
                    provider: provider,
                    ten: provider,
                    loai_nao: 'boss',
                    phan_tram: 100,
                    key: giaTri,
                    ngay_tao: Date.now(),
                });
                ghiLS(KHOA_LS_BOSS, ds);
                oKeyBoss.value = '';
                await taiDanhSachBoss();
            } else {
                const ph = await fetch('/api/luu-key-model', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: giaTri, loai_nao: 'boss' }),
                });
                const dl = await ph.json();
                if (dl && dl.thanh_cong) {
                    oKeyBoss.value = '';
                    await taiDanhSachBoss();
                } else {
                    alert((dl && dl.loi) || 'Không lưu được key Boss.');
                }
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        } finally {
            nutRunBoss.disabled = false;
            nutRunBoss.textContent = chuCu;
        }
    }

    function xacNhanXoaBoss(key) {
        const ten = nhanProvider(key.provider || key.ten);
        const noiDung = 'Bạn có chắc muốn xóa key Boss ' + ten + '?';

        hoiXacNhan(noiDung, async function () {
            try {
                if (laKhach) {
                    const ds = docLS(KHOA_LS_BOSS).filter(function (k) { return k.id !== key.id; });
                    ghiLS(KHOA_LS_BOSS, ds);
                    await taiDanhSachBoss();
                } else {
                    const ph = await fetch('/api/xoa-key', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: key.id }),
                    });
                    const dl = await ph.json();
                    if (dl && dl.thanh_cong) {
                        await taiDanhSachBoss();
                    } else {
                        alert((dl && dl.loi) || 'Không xóa được key.');
                    }
                }
            } catch (e) {
                alert('Lỗi kết nối: ' + e.message);
            }
        });
    }

    async function capNhatQuotaBoss() {
        if (laKhach || !dsBoss) return;
        try {
            const ph = await fetch('/api/quota-key?loai_nao=boss');
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veDanhSach(dsBoss, dl.danh_sach, xacNhanXoaBoss);
            }
        } catch (e) {}
    }

    if (nutRunBoss) {
        nutRunBoss.addEventListener('click', function (e) {
            e.preventDefault();
            luuKeyBoss();
        });
    }
    if (oKeyBoss) {
        oKeyBoss.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                luuKeyBoss();
            }
        });
    }

    // ============================================================
    // KHỐI TIỂU BOSS
    // ============================================================
    const oKeyTieuBoss   = document.getElementById('o-key-tieu-boss');
    const nutRunTieuBoss = document.getElementById('nut-run-key-tieu-boss');
    const dsTieuBoss     = document.getElementById('danh-sach-key-tieu-boss');

    async function taiDanhSachTieuBoss() {
        if (!dsTieuBoss) return;
        await kiemTraPhien();

        if (laKhach) {
            veDanhSach(dsTieuBoss, docLS(KHOA_LS_TIEU_BOSS), xacNhanXoaTieuBoss);
            return;
        }

        try {
            const ph = await fetch('/api/danh-sach-key?loai_nao=tieu_boss');
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veDanhSach(dsTieuBoss, dl.danh_sach, xacNhanXoaTieuBoss);
            } else {
                veDanhSach(dsTieuBoss, [], xacNhanXoaTieuBoss);
            }
        } catch (e) {
            veDanhSach(dsTieuBoss, [], xacNhanXoaTieuBoss);
        }
    }

    async function luuKeyTieuBoss() {
        if (!oKeyTieuBoss || !nutRunTieuBoss) return;
        const giaTri = oKeyTieuBoss.value.trim();
        if (!giaTri) {
            alert('Vui lòng dán API Key Tiểu Boss trước.');
            return;
        }

        nutRunTieuBoss.disabled = true;
        const chuCu = nutRunTieuBoss.textContent;
        nutRunTieuBoss.textContent = '...';

        try {
            await kiemTraPhien();

            if (laKhach) {
                const provider = nhanDienProvider(giaTri);
                if (!provider) {
                    alert('Không nhận diện được provider. Key phải bắt đầu bằng gsk_ (Groq), sk-or- (OpenRouter), AIza hoặc AQ.Ab (Gemini).');
                    return;
                }
                const ds = docLS(KHOA_LS_TIEU_BOSS);
                ds.push({
                    id: 'khach-tieu-boss-' + Date.now(),
                    provider: provider,
                    ten: provider,
                    loai_nao: 'tieu_boss',
                    phan_tram: 100,
                    key: giaTri,
                    ngay_tao: Date.now(),
                });
                ghiLS(KHOA_LS_TIEU_BOSS, ds);
                oKeyTieuBoss.value = '';
                await taiDanhSachTieuBoss();
            } else {
                const ph = await fetch('/api/luu-key-model', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: giaTri, loai_nao: 'tieu_boss' }),
                });
                const dl = await ph.json();
                if (dl && dl.thanh_cong) {
                    oKeyTieuBoss.value = '';
                    await taiDanhSachTieuBoss();
                } else {
                    alert((dl && dl.loi) || 'Không lưu được key Tiểu Boss.');
                }
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        } finally {
            nutRunTieuBoss.disabled = false;
            nutRunTieuBoss.textContent = chuCu;
        }
    }

    function xacNhanXoaTieuBoss(key) {
        const ten = nhanProvider(key.provider || key.ten);
        const noiDung = 'Bạn có chắc muốn xóa key Tiểu Boss ' + ten + '?';

        hoiXacNhan(noiDung, async function () {
            try {
                if (laKhach) {
                    const ds = docLS(KHOA_LS_TIEU_BOSS).filter(function (k) { return k.id !== key.id; });
                    ghiLS(KHOA_LS_TIEU_BOSS, ds);
                    await taiDanhSachTieuBoss();
                } else {
                    const ph = await fetch('/api/xoa-key', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: key.id }),
                    });
                    const dl = await ph.json();
                    if (dl && dl.thanh_cong) {
                        await taiDanhSachTieuBoss();
                    } else {
                        alert((dl && dl.loi) || 'Không xóa được key.');
                    }
                }
            } catch (e) {
                alert('Lỗi kết nối: ' + e.message);
            }
        });
    }

    async function capNhatQuotaTieuBoss() {
        if (laKhach || !dsTieuBoss) return;
        try {
            const ph = await fetch('/api/quota-key?loai_nao=tieu_boss');
            const dl = await ph.json();
            if (dl && dl.thanh_cong && Array.isArray(dl.danh_sach)) {
                veDanhSach(dsTieuBoss, dl.danh_sach, xacNhanXoaTieuBoss);
            }
        } catch (e) {}
    }

    if (nutRunTieuBoss) {
        nutRunTieuBoss.addEventListener('click', function (e) {
            e.preventDefault();
            luuKeyTieuBoss();
        });
    }
    if (oKeyTieuBoss) {
        oKeyTieuBoss.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                luuKeyTieuBoss();
            }
        });
    }

    // ============================================================
    // VÒNG LẶP CẬP NHẬT QUOTA
    // ============================================================
    let idHenQuota = null;

    function batDauCapNhatQuota() {
        if (idHenQuota) clearInterval(idHenQuota);
        idHenQuota = setInterval(function () {
            capNhatQuotaBoss();
            capNhatQuotaTieuBoss();
        }, THOI_GIAN_CAP_NHAT_QUOTA);
    }

    // ============================================================
    // KHỞI ĐỘNG
    // ============================================================
    async function khoiDong() {
        await kiemTraPhien();
        await Promise.all([
            taiDanhSachBoss(),
            taiDanhSachTieuBoss(),
        ]);
        batDauCapNhatQuota();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    window.taiDanhSachKeyBoss     = taiDanhSachBoss;
    window.taiDanhSachKeyTieuBoss = taiDanhSachTieuBoss;

})();
/* ============================================================
   quan_ly_key.js - Dán + quản lý API Key model
   ------------------------------------------------------------
   ĐÃ SỬA: Cho phép chế độ KHÁCH dán key.
     - Khách  : lưu vào localStorage (đóng tab mất).
     - Tài khoản: gửi server lưu kho 1 (vĩnh viễn).
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const oKey     = document.getElementById('o-key-model-2');
    const nutRun   = document.getElementById('nut-run-key-model-2');
    const danhSach = document.getElementById('danh-sach-key-model-2');

    if (!oKey || !nutRun || !danhSach) {
        return;
    }

    /* ------------------------------------------------------------
       HẰNG SỐ
       ------------------------------------------------------------ */
    const KHOA_LS = 'rong_than_key_model_khach';
    const THOI_GIAN_CAP_NHAT_QUOTA = 60 * 1000;
    let idHenQuota = null;
    let laKhach = false; // cập nhật từ taiThongTinPhien

    /* ------------------------------------------------------------
       KIỂM TRA PHIÊN
       ------------------------------------------------------------ */
    async function kiemTraPhien() {
        try {
            const ph = await fetch('/api/phien');
            const dl = await ph.json();
            laKhach = !(dl && dl.da_dang_nhap);
        } catch (e) {
            laKhach = true; // nếu lỗi, coi như khách
        }
        return laKhach;
    }

    /* ------------------------------------------------------------
       LOCALSTORAGE — dùng cho khách
       ------------------------------------------------------------ */
    function docLS() {
        try {
            const raw = localStorage.getItem(KHOA_LS);
            if (!raw) return [];
            const ds = JSON.parse(raw);
            return Array.isArray(ds) ? ds : [];
        } catch (e) {
            return [];
        }
    }

    function ghiLS(ds) {
        try {
            localStorage.setItem(KHOA_LS, JSON.stringify(ds || []));
        } catch (e) {}
    }

    /* ------------------------------------------------------------
       NHẬN DIỆN PROVIDER TỪ KEY
       ------------------------------------------------------------ */
    function nhanDienProvider(key) {
        const k = String(key || '').trim();
        if (k.startsWith('gsk_'))   return 'Groq';
        if (k.startsWith('sk-or-')) return 'OpenRouter';
        if (k.startsWith('AIza'))   return 'Gemini';
        return null;
    }

    /* ------------------------------------------------------------
       MÀU QUOTA
       ------------------------------------------------------------ */
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

    /* ------------------------------------------------------------
       TẠO CARD KEY
       ------------------------------------------------------------ */
    function taoTheKey(key, chiSo) {
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

    /* ------------------------------------------------------------
       VẼ DANH SÁCH
       ------------------------------------------------------------ */
    function veDanhSach(ds) {
        danhSach.innerHTML = '';
        if (!Array.isArray(ds) || ds.length === 0) return;
        ds.forEach(function (key, i) {
            danhSach.appendChild(taoTheKey(key, i));
        });
    }

    /* ------------------------------------------------------------
       TẢI DANH SÁCH
       ------------------------------------------------------------ */
    async function taiDanhSach() {
        if (laKhach) {
            veDanhSach(docLS());
            return;
        }
        try {
            const ph = await fetch('/api/danh-sach-key');
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

    /* ------------------------------------------------------------
       LƯU KEY
       ------------------------------------------------------------ */
    async function luuKey() {
        const giaTri = oKey.value.trim();
        if (!giaTri) {
            alert('Vui lòng dán API Key model trước.');
            return;
        }

        nutRun.disabled = true;
        const chuCu = nutRun.textContent;
        nutRun.textContent = '...';

        try {
            if (laKhach) {
                // ====== KHÁCH: lưu localStorage ======
                const provider = nhanDienProvider(giaTri);
                if (!provider) {
                    alert('Không nhận diện được provider. Key phải bắt đầu bằng gsk_ (Groq), sk-or- (OpenRouter) hoặc AIza (Gemini).');
                    return;
                }
                const ds = docLS();
                ds.push({
                    id: 'khach-key-' + Date.now(),
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
                // ====== TÀI KHOẢN: gửi server ======
                const ph = await fetch('/api/luu-key-model', {
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

    /* ------------------------------------------------------------
       XÓA KEY
       ------------------------------------------------------------ */
    function xacNhanXoaKey(key) {
        const ten = nhanProvider(key.provider || key.ten);
        const noiDung = 'Bạn có chắc muốn xóa key ' + ten + '?';

        const hamDongY = async function () {
            try {
                if (laKhach) {
                    const ds = docLS().filter(function (k) { return k.id !== key.id; });
                    ghiLS(ds);
                    await taiDanhSach();
                } else {
                    const ph = await fetch('/api/xoa-key', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: key.id || key.key || key.ten }),
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

    /* ------------------------------------------------------------
       CẬP NHẬT QUOTA
       ------------------------------------------------------------ */
    async function capNhatQuota() {
        if (laKhach) return; // khách không cập nhật quota
        try {
            const ph = await fetch('/api/quota-key');
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

    /* ------------------------------------------------------------
       SỰ KIỆN
       ------------------------------------------------------------ */
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

    /* ------------------------------------------------------------
       KHỞI ĐỘNG
       ------------------------------------------------------------ */
    async function khoiDong() {
        await kiemTraPhien();
        await taiDanhSach();
        batDauCapNhatQuota();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    /* ------------------------------------------------------------
       XUẤT TOÀN CỤC
       ------------------------------------------------------------ */
    window.taiDanhSachKeyModel = taiDanhSach;
    window.veDanhSachKeyModel = veDanhSach;

})();
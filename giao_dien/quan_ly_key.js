/* ============================================================
   quan_ly_key.js - Dán + quản lý API Key model
   ------------------------------------------------------------
   Nhiệm vụ:
     - Lấy key từ ô #o-key-model-2, gửi POST /api/luu-key-model.
     - Tải danh sách key model từ GET /api/danh-sach-key
       → vẽ vào #danh-sach-key-model-2.
     - Vẽ mỗi key là 1 card:
         + Icon 🔥🐉, tên provider, số thứ tự (#1, #2, #3...).
         + Nút [X] xóa key.
         + Thanh quota + % còn lại.
     - Màu quota:
         + Xanh: trên 50%
         + Vàng: 20-50%
         + Đỏ:   dưới 20%
         + Đen:  0%
     - Tự động cập nhật quota mỗi 60 giây.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const oKey       = document.getElementById('o-key-model-2');
    const nutRun     = document.getElementById('nut-run-key-model-2');
    const danhSach   = document.getElementById('danh-sach-key-model-2');

    if (!oKey || !nutRun || !danhSach) {
        return; // Thiếu DOM thì thoát.
    }

    /* ------------------------------------------------------------
       HẰNG SỐ
       ------------------------------------------------------------ */
    const THOI_GIAN_CAP_NHAT_QUOTA = 60 * 1000; // 60 giây
    let idHenQuota = null;

    /* ------------------------------------------------------------
       XÁC ĐỊNH MÀU QUOTA THEO PHẦN TRĂM
       ------------------------------------------------------------ */
    function layClassQuota(phanTram) {
        if (phanTram <= 0)   return 'quota-den';
        if (phanTram < 20)   return 'quota-do';
        if (phanTram < 50)   return 'quota-vang';
        return 'quota-xanh';
    }

    /* ------------------------------------------------------------
       TÊN PROVIDER
       ------------------------------------------------------------ */
    function nhanProvider(ten) {
        const t = String(ten || '').toLowerCase();
        if (t.includes('groq'))       return 'Groq';
        if (t.includes('openrouter')) return 'OpenRouter';
        if (t.includes('gemini'))     return 'Gemini';
        return ten || 'Không rõ';
    }

    /* ------------------------------------------------------------
       TẠO 1 CARD KEY
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
        nutXoa.setAttribute('aria-label', 'Xóa key');
        nutXoa.innerHTML = '&#10005;';
        nutXoa.addEventListener('click', function () {
            xacNhanXoaKey(key);
        });
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
       VẼ DANH SÁCH KEY
       ------------------------------------------------------------ */
    function veDanhSach(danhSachKey) {
        danhSach.innerHTML = '';
        if (!Array.isArray(danhSachKey) || danhSachKey.length === 0) {
            return;
        }
        danhSachKey.forEach(function (key, i) {
            danhSach.appendChild(taoTheKey(key, i));
        });
    }

    /* ------------------------------------------------------------
       TẢI DANH SÁCH KEY TỪ SERVER
       ------------------------------------------------------------ */
    async function taiDanhSach() {
        try {
            const phanHoi = await fetch('/api/danh-sach-key');
            const duLieu = await phanHoi.json();
            if (duLieu && duLieu.thanh_cong && Array.isArray(duLieu.danh_sach)) {
                veDanhSach(duLieu.danh_sach);
            } else {
                veDanhSach([]);
            }
        } catch (e) {
            veDanhSach([]);
        }
    }

    /* ------------------------------------------------------------
       LƯU KEY MỚI
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
            const phanHoi = await fetch('/api/luu-key-model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key: giaTri }),
            });

            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong) {
                oKey.value = '';
                await taiDanhSach();
            } else {
                alert((duLieu && duLieu.loi) || 'Không lưu được key.');
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        } finally {
            nutRun.disabled = false;
            nutRun.textContent = chuCu;
        }
    }

    /* ------------------------------------------------------------
       XÁC NHẬN XÓA KEY
       ------------------------------------------------------------ */
    function xacNhanXoaKey(key) {
        const ten = nhanProvider(key.provider || key.ten);
        const noiDung = 'Bạn có chắc muốn xóa key ' + ten + '?';

        const hamDongY = async function () {
            try {
                const phanHoi = await fetch('/api/xoa-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: key.id || key.key || key.ten }),
                });
                const duLieu = await phanHoi.json();
                if (duLieu && duLieu.thanh_cong) {
                    await taiDanhSach();
                } else {
                    alert((duLieu && duLieu.loi) || 'Không xóa được key.');
                }
            } catch (e) {
                alert('Lỗi kết nối: ' + e.message);
            }
        };

        if (typeof window.moXacNhanXoa === 'function') {
            window.moXacNhanXoa(noiDung, hamDongY);
        } else {
            if (confirm(noiDung)) hamDongY();
        }
    }

    /* ------------------------------------------------------------
       CẬP NHẬT QUOTA ĐỊNH KỲ
       ------------------------------------------------------------ */
    async function capNhatQuota() {
        try {
            const phanHoi = await fetch('/api/quota-key');
            const duLieu = await phanHoi.json();
            if (duLieu && duLieu.thanh_cong && Array.isArray(duLieu.danh_sach)) {
                veDanhSach(duLieu.danh_sach);
            }
        } catch (e) {
            // Im lặng
        }
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
    function khoiDong() {
        taiDanhSach();
        batDauCapNhatQuota();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.taiDanhSachKeyModel = taiDanhSach;
    window.veDanhSachKeyModel = veDanhSach;

})();
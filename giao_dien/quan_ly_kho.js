/* ============================================================
   quan_ly_kho.js - Dán + quản lý URI 2 kho MongoDB
   ------------------------------------------------------------
   Nhiệm vụ:
     - Lấy URI từ ô #o-uri-kho-1-2, gửi POST /api/luu-uri-kho
       với { kho: 1, uri: "..." }.
     - Lấy URI từ ô #o-uri-kho-2-2, gửi POST /api/luu-uri-kho
       với { kho: 2, uri: "..." }.
     - Hiển thị trạng thái kết nối: "Đã kết nối kho 1" / "Lỗi kết nối kho 2"...
     - Khi mở lại trang Key, tự động tải URI cũ (GET /api/lay-uri-kho)
       và hiển thị trong ô input, che bớt ký tự giữa.
     - Không hiển thị danh sách URI đã lưu (khác với key).
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const oKho1     = document.getElementById('o-uri-kho-1-2');
    const oKho2     = document.getElementById('o-uri-kho-2-2');
    const nutKho1   = document.getElementById('nut-run-kho-1-2');
    const nutKho2   = document.getElementById('nut-run-kho-2-2');

    if (!oKho1 || !oKho2 || !nutKho1 || !nutKho2) {
        return; // Thiếu DOM thì thoát.
    }

    /* ------------------------------------------------------------
       HÀM CHE BỚT URI (hiển thị cho an toàn)
       Ví dụ:
         mongodb+srv://user:pass@cluster.mongodb.net/db
         → mongodb+srv://user:***@cluster.mongodb.net/db
       ------------------------------------------------------------ */
    function cheUri(uri) {
        if (typeof uri !== 'string' || !uri) return '';

        // Che phần mật khẩu giữa "://user:" và "@host"
        // Định dạng: scheme://user:password@host
        const regex = /^([a-zA-Z][\w+.-]*:\/\/[^:]+:)([^@]+)(@.+)$/;
        const khop = uri.match(regex);
        if (khop) {
            const matKhauDai = khop[2].length;
            const sao = '*'.repeat(Math.min(matKhauDai, 8));
            return khop[1] + sao + khop[3];
        }

        // Nếu không có mật khẩu, che giữa chuỗi
        if (uri.length > 40) {
            return uri.slice(0, 20) + '...' + uri.slice(-15);
        }
        return uri;
    }

    /* ------------------------------------------------------------
       HIỂN THỊ TRẠNG THÁI KẾT NỐI
       ------------------------------------------------------------ */
    function hienTrangThai(nut, chu, mau) {
        // Lưu chữ gốc lần đầu
        if (!nut.dataset.chuGoc) {
            nut.dataset.chuGoc = nut.textContent;
        }
        const chuGoc = nut.dataset.chuGoc;

        nut.textContent = chu;
        nut.style.color = mau || '';

        setTimeout(function () {
            nut.textContent = chuGoc;
            nut.style.color = '';
        }, 2500);
    }

    /* ------------------------------------------------------------
       LƯU URI KHO
       ------------------------------------------------------------ */
    async function luuKho(soKho, oNhap, nut) {
        const uri = oNhap.value.trim();
        if (!uri) {
            hienTrangThai(nut, 'Trống', 'var(--do)');
            return;
        }

        nut.disabled = true;
        nut.textContent = '...';

        try {
            const phanHoi = await fetch('/api/luu-uri-kho', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ kho: soKho, uri: uri }),
            });

            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong) {
                // Hiển thị lại URI đã che
                oNhap.value = cheUri(uri);
                hienTrangThai(nut, 'Đã kết nối', 'var(--chu-rong)');
            } else {
                hienTrangThai(nut, 'Lỗi', 'var(--do)');
                alert((duLieu && duLieu.loi) || 'Không lưu được URI kho ' + soKho + '.');
            }
        } catch (e) {
            hienTrangThai(nut, 'Lỗi', 'var(--do)');
            alert('Lỗi kết nối: ' + e.message);
        } finally {
            nut.disabled = false;
            // Nếu chữ đang là "..." thì khôi phục chữ gốc
            if (nut.textContent === '...') {
                nut.textContent = nut.dataset.chuGoc || 'Run';
            }
        }
    }

    /* ------------------------------------------------------------
       TẢI URI CŨ ĐÃ LƯU
       ------------------------------------------------------------ */
    async function taiUriCu() {
        try {
            const phanHoi = await fetch('/api/lay-uri-kho');
            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong) {
                if (duLieu.kho_1) {
                    oKho1.value = cheUri(duLieu.kho_1);
                }
                if (duLieu.kho_2) {
                    oKho2.value = cheUri(duLieu.kho_2);
                }
            }
        } catch (e) {
            // Im lặng — chưa có URI cũng không sao
        }
    }

    /* ------------------------------------------------------------
       SỰ KIỆN
       ------------------------------------------------------------ */
    nutKho1.addEventListener('click', function (e) {
        e.preventDefault();
        luuKho(1, oKho1, nutKho1);
    });

    nutKho2.addEventListener('click', function (e) {
        e.preventDefault();
        luuKho(2, oKho2, nutKho2);
    });

    // Nhấn Enter trong ô → lưu
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

    // Khi focus vào ô đang chứa URI đã che → hiện lại URI gốc đầy đủ
    // (để người dùng có thể sửa hoặc copy)
    // Nhưng vì URI gốc không có ở client, chỉ cho phép dán URI mới.
    [oKho1, oKho2].forEach(function (oNhap) {
        oNhap.addEventListener('focus', function () {
            // Nếu đang chứa chuỗi che (có dấu ***) → xóa để người dùng dán mới
            if (oNhap.value.includes('***')) {
                oNhap.value = '';
            }
        });
    });

    /* ------------------------------------------------------------
       KHỞI ĐỘNG
       ------------------------------------------------------------ */
    function khoiDong() {
        taiUriCu();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.taiUriKho = taiUriCu;
    window.cheUri = cheUri;

})();
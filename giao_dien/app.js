/* ============================================================
   app.js - Khởi động chung giao diện Rồng Thần
   ------------------------------------------------------------
   Nhiệm vụ:
     - Chạy khi tất cả JS khác đã load xong.
     - Kiểm tra môi trường (có đủ các hàm toàn cục không).
     - Kiểm tra kết nối server (GET /api/phien).
     - Hiển thị thông báo hệ thống nếu có vấn đề.
     - Gắn sự kiện bổ sung nếu cần.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       KIỂM TRA CÁC HÀM TOÀN CỤC ĐÃ SẴN SÀNG CHƯA
       ------------------------------------------------------------ */
    function kiemTraMoiTruong() {
        const canCo = [
            'themTinNhanRong',
            'themTinNhanNguoi',
            'themTinNhanHeThong',
            'moXacNhanXoa',
            'hienThiCodeTrongTinNhan',
            'copyCode',
        ];

        const thieu = canCo.filter(function (ten) {
            return typeof window[ten] !== 'function';
        });

        if (thieu.length > 0) {
            console.warn('[Rồng Thần] Thiếu hàm toàn cục:', thieu.join(', '));
        }

        return thieu.length === 0;
    }

    /* ------------------------------------------------------------
       HIỂN THỊ THÔNG BÁO HỆ THỐNG TRONG CHAT
       ------------------------------------------------------------ */
    function thongBaoHeThong(noiDung) {
        if (typeof window.themTinNhanHeThong === 'function') {
            window.themTinNhanHeThong(noiDung);
        } else {
            console.log('[Rồng Thần]', noiDung);
        }
    }

    /* ------------------------------------------------------------
       KIỂM TRA KẾT NỐI SERVER
       ------------------------------------------------------------ */
    async function kiemTraKetNoi() {
        try {
            const phanHoi = await fetch('/api/phien', { method: 'GET' });
            if (!phanHoi.ok && phanHoi.status !== 401) {
                thongBaoHeThong('⚠️ Server phản hồi mã ' + phanHoi.status + '.');
                return false;
            }
            return true;
        } catch (e) {
            thongBaoHeThong('⚠️ Không kết nối được server. Kiểm tra Render đã deploy chưa.');
            return false;
        }
    }

    /* ------------------------------------------------------------
       KIỂM TRA CÁC NÚT CHÍNH CÓ TỒN TẠI KHÔNG
       ------------------------------------------------------------ */
    function kiemTraNutChinh() {
        const nutCanCo = [
            'nut-gui',
            'nut-menu-trai',
            'nut-menu-phai',
            'nut-dinh-kem',
        ];

        const thieu = nutCanCo.filter(function (id) {
            return !document.getElementById(id);
        });

        if (thieu.length > 0) {
            console.warn('[Rồng Thần] Thiếu nút chính:', thieu.join(', '));
        }

        return thieu.length === 0;
    }

    /* ------------------------------------------------------------
       LOG PHIÊN BẢN
       ------------------------------------------------------------ */
    function logPhienBan() {
        console.log(
            '%c🌕🐉 Rồng Thần',
            'color: #4ade80; font-size: 16px; font-weight: bold;'
        );
        console.log('Giao diện đã khởi động.');
    }

    /* ------------------------------------------------------------
       KHỞI ĐỘNG CHÍNH
       ------------------------------------------------------------ */
    async function khoiDong() {
        logPhienBan();

        const moiTruongOK = kiemTraMoiTruong();
        const nutOK = kiemTraNutChinh();

        // Kiểm tra kết nối server (chỉ khi môi trường có fetch)
        if (typeof fetch === 'function') {
            await kiemTraKetNoi();
        }

        if (!moiTruongOK) {
            console.warn('[Rồng Thần] Một số file JS chưa load đúng thứ tự.');
        }
        if (!nutOK) {
            console.warn('[Rồng Thần] Một số nút chính bị thiếu trong HTML.');
        }
    }

    /* ------------------------------------------------------------
       CHẠY KHI DOM SẴN SÀNG
       ------------------------------------------------------------ */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    /* ------------------------------------------------------------
       XỬ LÝ LỖI TOÀN CỤC
       ------------------------------------------------------------ */
    window.addEventListener('error', function (e) {
        console.error('[Rồng Thần] Lỗi:', e.message, e.filename, e.lineno);
    });

    window.addEventListener('unhandledrejection', function (e) {
        console.error('[Rồng Thần] Promise bị từ chối:', e.reason);
    });

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.kiemTraMoiTruong = kiemTraMoiTruong;
    window.thongBaoHeThong = thongBaoHeThong;

})();
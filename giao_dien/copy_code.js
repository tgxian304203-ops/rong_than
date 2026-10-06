/* ============================================================
   copy_code.js - Xử lý nút Copy trong khung code Rồng Thần
   ------------------------------------------------------------
   Nhiệm vụ:
     - Cung cấp hàm window.copyCode(text, nutBam).
     - Ưu tiên dùng Clipboard API (navigator.clipboard).
     - Fallback dùng textarea + execCommand cho trình duyệt cũ.
     - Đổi chữ nút thành "Đã chép" 1.2 giây rồi trả về.
     - Nếu lỗi, đổi thành "Lỗi" 1.2 giây rồi trả về.
   ============================================================ */

(function () {
    'use strict';

    const THOI_GIAN_THONG_BAO = 1200; // ms

    /* ------------------------------------------------------------
       HÀM HIỂN THỊ THÔNG BÁO TẠM TRÊN NÚT
       ------------------------------------------------------------ */
    function hienThiTam(nut, chuMoi) {
        if (!nut) return;
        if (nut.dataset.dangThongBao === '1') return;

        const chuCu = nut.textContent;
        nut.dataset.dangThongBao = '1';
        nut.textContent = chuMoi;

        setTimeout(function () {
            nut.textContent = chuCu;
            nut.dataset.dangThongBao = '0';
        }, THOI_GIAN_THONG_BAO);
    }

    /* ------------------------------------------------------------
       COPY BẰNG CLIPBOARD API (cách hiện đại)
       ------------------------------------------------------------ */
    function copyBangClipboard(text, nut) {
        return navigator.clipboard.writeText(text).then(
            function () {
                hienThiTam(nut, 'Đã chép');
                return true;
            },
            function () {
                return false;
            }
        );
    }

    /* ------------------------------------------------------------
       COPY BẰNG execCommand (cách cũ, fallback)
       ------------------------------------------------------------ */
    function copyBangExecCommand(text, nut) {
        const tam = document.createElement('textarea');
        tam.value = text;
        tam.setAttribute('readonly', '');
        tam.style.position = 'fixed';
        tam.style.top = '-9999px';
        tam.style.left = '-9999px';
        tam.style.opacity = '0';
        document.body.appendChild(tam);

        let thanhCong = false;
        try {
            tam.select();
            tam.setSelectionRange(0, tam.value.length);
            thanhCong = document.execCommand('copy');
        } catch (e) {
            thanhCong = false;
        }
        document.body.removeChild(tam);

        if (thanhCong) {
            hienThiTam(nut, 'Đã chép');
        } else {
            hienThiTam(nut, 'Lỗi');
        }
        return thanhCong;
    }

    /* ------------------------------------------------------------
       HÀM CHÍNH: window.copyCode(text, nutBam)
       ------------------------------------------------------------ */
    function copyCode(text, nutBam) {
        if (typeof text !== 'string' || !text.length) {
            hienThiTam(nutBam, 'Trống');
            return;
        }

        // Nếu có Clipboard API
        if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
            copyBangClipboard(text, nutBam).then(function (ok) {
                if (!ok) {
                    // Clipboard API lỗi (ví dụ: không HTTPS) → fallback
                    copyBangExecCommand(text, nutBam);
                }
            });
        } else {
            // Trình duyệt cũ không có Clipboard API
            copyBangExecCommand(text, nutBam);
        }
    }

    /* ------------------------------------------------------------
       TỰ ĐỘNG GẮN SỰ KIỆN CHO CÁC NÚT .nut-copy-code CÓ SẴN
       (Trường hợp nút do HTML tĩnh tạo, không qua tach_code_khoi_tin_nhan.js)
       ------------------------------------------------------------ */
    function ganSuKienChoNutCopyCoSan() {
        const cacNut = document.querySelectorAll('.nut-copy-code:not([data-da-gan])');
        cacNut.forEach(function (nut) {
            nut.setAttribute('data-da-gan', '1');
            nut.addEventListener('click', function () {
                // Tìm khung code cha gần nhất để lấy nội dung
                const khung = nut.closest('.khung-code');
                if (!khung) return;
                const body = khung.querySelector('.khung-code-body');
                if (body) {
                    copyCode(body.textContent, nut);
                }
            });
        });
    }

    /* ------------------------------------------------------------
       XUẤT HÀM RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.copyCode = copyCode;

    /* ------------------------------------------------------------
       KHỞI ĐỘNG
       ------------------------------------------------------------ */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ganSuKienChoNutCopyCoSan);
    } else {
        ganSuKienChoNutCopyCoSan();
    }

    // Cho phép gọi lại khi có khung code mới được thêm vào DOM
    window.ganSuKienChoNutCopyCoSan = ganSuKienChoNutCopyCoSan;

})();
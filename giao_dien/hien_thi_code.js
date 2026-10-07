/* ============================================================
   hien_thi_code.js - Hiển thị khung code riêng trong tin nhắn
   ------------------------------------------------------------
   ĐÃ SỬA:
     - Bỏ tô từ khóa (keyword) → tránh chồng thẻ HTML.
     - Chỉ tô comment + string bằng placeholder tạm.
     - Code còn lại hiển thị text trắng bình thường.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       BẢNG NHÃN NGÔN NGỮ
       ------------------------------------------------------------ */
    const NHAN = {
        html: 'HTML',
        css: 'CSS',
        js: 'JavaScript',
        javascript: 'JavaScript',
        ts: 'TypeScript',
        py: 'Python',
        python: 'Python',
        json: 'JSON',
        sql: 'SQL',
        bash: 'Bash',
        sh: 'Shell',
        text: 'Text',
        code: 'Code',
    };

    function chuanHoaNhan(ngonNgu) {
        if (!ngonNgu) return 'Code';
        return NHAN[String(ngonNgu).toLowerCase()] || String(ngonNgu).toUpperCase();
    }

    /* ------------------------------------------------------------
       TỰ ĐOÁN NGÔN NGỮ TỪ NỘI DUNG
       ------------------------------------------------------------ */
    function doanNgonNgu(code) {
        if (!code || typeof code !== 'string') return 'code';
        const c = code.trim();

        if (/^<!DOCTYPE\s+html/i.test(c)) return 'html';
        if (/<html[\s>]/i.test(c)) return 'html';
        if (/^<[a-z][\s\S]*<\/[a-z]+>$/i.test(c)) return 'html';

        if (/^[\[{][\s\S]*[\]}]$/.test(c)) {
            try {
                JSON.parse(c);
                return 'json';
            } catch (e) {}
        }

        if (/^\s*(def|class|import|from|if __name__)\s/m.test(c)) return 'python';
        if (/^\s*print\s*\(/m.test(c)) return 'python';

        if (/^\s*(function|const|let|var|=>|export|import\s+.*from)/m.test(c)) return 'js';

        if (/^[\s\S]*\{[\s\S]*:[\s\S]*;[\s\S]*\}/.test(c) &&
            /[.#@][\w-]+\s*\{/.test(c)) return 'css';

        if (/^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER)\s/im.test(c)) return 'sql';

        return 'code';
    }

    /* ------------------------------------------------------------
       ESCAPE HTML
       ------------------------------------------------------------ */
    function escapeHTML(s) {
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    /* ------------------------------------------------------------
       TÔ MÀU CÚ PHÁP — CHỈ COMMENT + STRING
       ------------------------------------------------------------
       Dùng placeholder tạm để không chồng thẻ HTML.
       ------------------------------------------------------------ */
    function toMau(nn, code) {
        if (!code) return '';

        // Escape trước
        let s = escapeHTML(code);

        // Mảng tạm giữ các đoạn đã tô
        const mangTam = [];
        const PH = '\x00__PH__';   // placeholder prefix

        function luuTam(html) {
            const idx = mangTam.length;
            mangTam.push(html);
            return PH + idx + '__';
        }

        switch (nn) {
            case 'html':
                // Comment <!-- ... -->
                s = s.replace(/(&lt;!--[\s\S]*?--&gt;)/g, function (m) {
                    return luuTam('<span class="mau-comment">' + m + '</span>');
                });
                break;

            case 'python':
                // Comment # ... (đến cuối dòng)
                s = s.replace(/(#[^\n]*)/g, function (m) {
                    return luuTam('<span class="mau-comment">' + m + '</span>');
                });
                // String "..." hoặc '...'
                s = s.replace(/(&quot;[^&]*?&quot;|&#39;[^&]*?&#39;)/g, function (m) {
                    return luuTam('<span class="mau-string">' + m + '</span>');
                });
                break;

            case 'js':
            case 'javascript':
            case 'ts':
                // Comment // ...
                s = s.replace(/(\/\/[^\n]*)/g, function (m) {
                    return luuTam('<span class="mau-comment">' + m + '</span>');
                });
                // Comment /* ... */
                s = s.replace(/(\/\*[\s\S]*?\*\/)/g, function (m) {
                    return luuTam('<span class="mau-comment">' + m + '</span>');
                });
                // String "..." hoặc '...' hoặc `...`
                s = s.replace(/(&quot;[^&]*?&quot;|&#39;[^&]*?&#39;|`[^`]*?`)/g, function (m) {
                    return luuTam('<span class="mau-string">' + m + '</span>');
                });
                break;

            case 'css':
                // Comment /* ... */
                s = s.replace(/(\/\*[\s\S]*?\*\/)/g, function (m) {
                    return luuTam('<span class="mau-comment">' + m + '</span>');
                });
                break;

            default:
                // Không tô gì
                break;
        }

        // Thay placeholder bằng thẻ HTML thật
        s = s.replace(/\x00__PH__(\d+)__/g, function (_, idx) {
            return mangTam[parseInt(idx, 10)] || '';
        });

        return s;
    }

    /* ------------------------------------------------------------
       TẠO KHUNG CODE
       ------------------------------------------------------------ */
    function taoKhungCode(code, ngonNgu) {
        const nn = (ngonNgu || doanNgonNgu(code) || 'code').toLowerCase();

        const khung = document.createElement('div');
        khung.classList.add('khung-code');

        // Header
        const header = document.createElement('div');
        header.classList.add('khung-code-header');

        const nhan = document.createElement('span');
        nhan.classList.add('khung-code-nhan');
        nhan.textContent = chuanHoaNhan(nn);
        header.appendChild(nhan);

        const nutCopy = document.createElement('button');
        nutCopy.classList.add('nut-copy-code');
        nutCopy.type = 'button';
        nutCopy.textContent = 'Copy';
        nutCopy.addEventListener('click', function () {
            if (typeof window.copyCode === 'function') {
                window.copyCode(code, nutCopy);
            } else if (navigator.clipboard) {
                navigator.clipboard.writeText(code).then(function () {
                    const cu = nutCopy.textContent;
                    nutCopy.textContent = 'Đã chép';
                    setTimeout(function () { nutCopy.textContent = cu; }, 1200);
                });
            }
        });
        header.appendChild(nutCopy);
        khung.appendChild(header);

        // Body — dùng <pre><code> để có thể tô màu
        const body = document.createElement('pre');
        body.classList.add('khung-code-body');

        const codeEl = document.createElement('code');
        codeEl.innerHTML = toMau(nn, code);
        body.appendChild(codeEl);
        khung.appendChild(body);

        return khung;
    }

    /* ------------------------------------------------------------
       HÀM: CHÈN KHUNG CODE VÀO 1 DIV TIN NHẮN
       ------------------------------------------------------------ */
    function chenKhungCodeVao(divTinNhan, code, ngonNgu) {
        if (!divTinNhan) return;
        const khung = taoKhungCode(code, ngonNgu);
        divTinNhan.appendChild(khung);
    }

    /* ------------------------------------------------------------
       HÀM: HIỂN THỊ KHUNG CODE RIÊNG (tin nhắn mới)
       ------------------------------------------------------------ */
    function hienThiKhungCode(code, ngonNgu) {
        const danhSach = document.getElementById('danh-sach-tin-nhan');
        if (!danhSach) return;

        const boc = document.createElement('div');
        boc.classList.add('tin-nhan', 'tin-nhan-rong');

        const khung = taoKhungCode(code, ngonNgu);
        boc.appendChild(khung);

        danhSach.appendChild(boc);

        if (typeof window.cuonXuongCuoi === 'function') {
            window.cuonXuongCuoi();
        }
    }

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.hienThiKhungCode = hienThiKhungCode;
    window.chenKhungCodeVao = chenKhungCodeVao;
    window.taoKhungCodeFull = taoKhungCode;
    window.doanNgonNgu = doanNgonNgu;

})();
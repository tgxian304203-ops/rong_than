/* ============================================================
   hien_thi_code.js - Hiển thị khung code riêng trong tin nhắn
   ------------------------------------------------------------
   Nhiệm vụ:
     - Nhận diện loại code: HTML, Python, JavaScript, CSS, JSON, SQL, ...
       dựa trên ngôn ngữ (nếu server gửi) hoặc tự đoán từ nội dung.
     - Tạo khung code có:
         + Nhãn ngôn ngữ ở header.
         + Nút Copy ở header.
         + Body chứa code nguyên dạng, giữ xuống dòng, cuộn ngang.
     - Hỗ trợ chèn khung code vào 1 div tin nhắn có sẵn
       hoặc tạo tin nhắn mới chỉ chứa khung code.
     - Tô màu cú pháp đơn giản cho HTML, Python, JS, CSS
       (không cần thư viện ngoài).
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
       TỰ ĐOÁN NGÔN NGỮ TỪ NỘI DUNG (nếu server không gửi)
       ------------------------------------------------------------ */
    function doanNgonNgu(code) {
        if (!code || typeof code !== 'string') return 'code';
        const c = code.trim();

        // HTML
        if (/^<!DOCTYPE\s+html/i.test(c)) return 'html';
        if (/<html[\s>]/i.test(c)) return 'html';
        if (/^<[a-z][\s\S]*<\/[a-z]+>$/i.test(c)) return 'html';

        // JSON
        if (/^[\[{][\s\S]*[\]}]$/.test(c)) {
            try {
                JSON.parse(c);
                return 'json';
            } catch (e) {
                // Không phải JSON hợp lệ
            }
        }

        // Python
        if (/^\s*(def|class|import|from|if __name__)\s/m.test(c)) return 'python';
        if (/^\s*print\s*\(/m.test(c)) return 'python';

        // JavaScript
        if (/^\s*(function|const|let|var|=>|export|import\s+.*from)/m.test(c)) return 'js';

        // CSS
        if (/^[\s\S]*\{[\s\S]*:[\s\S]*;[\s\S]*\}/.test(c) &&
            /[.#@][\w-]+\s*\{/.test(c)) return 'css';

        // SQL
        if (/^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER)\s/im.test(c)) return 'sql';

        return 'code';
    }

    /* ------------------------------------------------------------
       TÔ MÀU CÚ PHÁP ĐƠN GIẢN (trả về HTML string)
       - Chỉ tô cho các ngôn ngữ phổ biến.
       - Không tô cho ngôn ngữ lạ.
       - Escape HTML trước, rồi bọc thẻ <span class="...">.
       ------------------------------------------------------------ */

    function escapeHTML(s) {
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function toMauHTML(code) {
        let s = escapeHTML(code);
        // Comment <!-- ... -->
        s = s.replace(/(&lt;!--[\s\S]*?--&gt;)/g, '<span class="mau-comment">$1</span>');
        // Thẻ mở/đóng
        s = s.replace(/(&lt;\/?[a-zA-Z][\w-]*)/g, '<span class="mau-the">$1</span>');
        // Thuộc tính
        s = s.replace(/([a-zA-Z-]+)=(&quot;|&#39;)/g, '<span class="mau-thuoc-tinh">$1</span>=$2');
        return s;
    }

    function toMauPython(code) {
        let s = escapeHTML(code);
        // Comment #
        s = s.replace(/(#[^\n]*)/g, '<span class="mau-comment">$1</span>');
        // String
        s = s.replace(/(&quot;[^&]*?&quot;|&#39;[^&]*?&#39;)/g,
            '<span class="mau-string">$1</span>');
        // Từ khóa
        s = s.replace(/\b(def|class|return|if|elif|else|for|while|in|not|and|or|import|from|as|try|except|finally|with|lambda|yield|None|True|False|self|pass|break|continue|raise|global|nonlocal|assert|del|is)\b/g,
            '<span class="mau-tu-khoa">$1</span>');
        return s;
    }

    function toMauJS(code) {
        let s = escapeHTML(code);
        // Comment // và /* */
        s = s.replace(/(\/\/[^\n]*)/g, '<span class="mau-comment">$1</span>');
        s = s.replace(/(\/\*[\s\S]*?\*\/)/g, '<span class="mau-comment">$1</span>');
        // String
        s = s.replace(/(&quot;[^&]*?&quot;|&#39;[^&]*?&#39;|`[^`]*?`)/g,
            '<span class="mau-string">$1</span>');
        // Từ khóa
        s = s.replace(/\b(function|const|let|var|return|if|else|for|while|do|switch|case|break|continue|new|this|class|extends|super|import|export|from|as|default|try|catch|finally|throw|typeof|instanceof|null|undefined|true|false|async|await|yield|of|in)\b/g,
            '<span class="mau-tu-khoa">$1</span>');
        return s;
    }

    function toMauCSS(code) {
        let s = escapeHTML(code);
        // Comment /* */
        s = s.replace(/(\/\*[\s\S]*?\*\/)/g, '<span class="mau-comment">$1</span>');
        // Selector
        s = s.replace(/^([.#@]?[\w-]+(?:\s*[,>+~]\s*[.#@]?[\w-]+)*)\s*\{/gm,
            '<span class="mau-selector">$1</span> {');
        // Thuộc tính
        s = s.replace(/([\w-]+)\s*:/g, '<span class="mau-thuoc-tinh">$1</span>:');
        return s;
    }

    function toMau(ngonNgu, code) {
        switch (ngonNgu) {
            case 'html':   return toMauHTML(code);
            case 'python': return toMauPython(code);
            case 'js':
            case 'javascript':
            case 'ts':     return toMauJS(code);
            case 'css':    return toMauCSS(code);
            default:       return escapeHTML(code);
        }
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
        // Tô màu bằng innerHTML đã escape
        codeEl.innerHTML = toMau(nn, code);
        body.appendChild(codeEl);
        khung.appendChild(body);

        return khung;
    }

    /* ------------------------------------------------------------
       HÀM CHÍNH 1: HIỂN THỊ KHUNG CODE VÀO 1 DIV CÓ SẴN
       ------------------------------------------------------------ */
    function chenKhungCodeVao(divTinNhan, code, ngonNgu) {
        if (!divTinNhan) return;
        const khung = taoKhungCode(code, ngonNgu);
        divTinNhan.appendChild(khung);
    }

    /* ------------------------------------------------------------
       HÀM CHÍNH 2: TẠO TIN NHẮN MỚI CHỈ CHỨA KHUNG CODE
       (dùng khi server trả code riêng, không lẫn với chữ)
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
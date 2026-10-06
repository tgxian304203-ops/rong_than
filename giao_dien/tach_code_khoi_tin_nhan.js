/* ============================================================
   tach_code_khoi_tin_nhan.js
   ------------------------------------------------------------
   Nhiệm vụ:
     - Nhận 1 div tin nhắn Rồng Thần và nội dung thô.
     - Nhận diện các khối code trong nội dung:
         + Đánh dấu kiểu markdown: ```html ... ```, ```python ... ```
         + Thẻ <code>...</code> đơn giản
     - Phần chữ ở lại trong div tin nhắn.
     - Phần code tách ra thành khung riêng:
         + Có header: nhãn ngôn ngữ + nút Copy.
         + Có body: code nguyên dạng (giữ xuống dòng).
     - Nếu nội dung không có code, chỉ set text bình thường.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       HÀM NHẬN DIỆN KHỐI CODE
       Trả về mảng các đoạn: [{loai:"chu"|"code", noiDung, ngonNgu}]
       ------------------------------------------------------------ */
    function tachDoan(noiDung) {
        const ketQua = [];
        // Regex bắt ```ngon_ngu\n ... \n```
        const regex = /```([a-zA-Z0-9_+-]*)\s*\n?([\s\S]*?)```/g;

        let viTriCuoi = 0;
        let khop;

        while ((khop = regex.exec(noiDung)) !== null) {
            // Phần chữ trước khối code
            if (khop.index > viTriCuoi) {
                const chu = noiDung.slice(viTriCuoi, khop.index);
                if (chu.trim()) {
                    ketQua.push({ loai: 'chu', noiDung: chu.trim() });
                }
            }

            // Khối code
            const ngonNgu = (khop[1] || '').trim().toLowerCase() || 'code';
            const code = khop[2].replace(/^\n+|\n+$/g, '');
            ketQua.push({ loai: 'code', noiDung: code, ngonNgu: ngonNgu });

            viTriCuoi = khop.index + khop[0].length;
        }

        // Phần chữ còn lại sau khối code cuối
        if (viTriCuoi < noiDung.length) {
            const chu = noiDung.slice(viTriCuoi);
            if (chu.trim()) {
                ketQua.push({ loai: 'chu', noiDung: chu.trim() });
            }
        }

        // Không có code nào
        if (ketQua.length === 0) {
            ketQua.push({ loai: 'chu', noiDung: noiDung });
        }

        return ketQua;
    }

    /* ------------------------------------------------------------
       CHUẨN HÓA NHÃN NGÔN NGỮ
       ------------------------------------------------------------ */
    function chuanHoaNhan(ngonNgu) {
        const bang = {
            html: 'HTML',
            css: 'CSS',
            js: 'JavaScript',
            javascript: 'JavaScript',
            py: 'Python',
            python: 'Python',
            json: 'JSON',
            sql: 'SQL',
            bash: 'Bash',
            sh: 'Shell',
            text: 'Text',
            code: 'Code',
        };
        return bang[ngonNgu] || ngonNgu.toUpperCase();
    }

    /* ------------------------------------------------------------
       TẠO KHUNG CODE
       ------------------------------------------------------------ */
    function taoKhungCode(noiDungCode, ngonNgu) {
        const khung = document.createElement('div');
        khung.classList.add('khung-code');

        // Header: nhãn + nút Copy
        const header = document.createElement('div');
        header.classList.add('khung-code-header');

        const nhan = document.createElement('span');
        nhan.classList.add('khung-code-nhan');
        nhan.textContent = chuanHoaNhan(ngonNgu);
        header.appendChild(nhan);

        const nutCopy = document.createElement('button');
        nutCopy.classList.add('nut-copy-code');
        nutCopy.type = 'button';
        nutCopy.textContent = 'Copy';
        nutCopy.addEventListener('click', function () {
            // Gọi hàm copy toàn cục nếu có (copy_code.js), nếu không tự copy.
            if (typeof window.copyCode === 'function') {
                window.copyCode(noiDungCode, nutCopy);
            } else {
                copyTrucTiep(noiDungCode, nutCopy);
            }
        });
        header.appendChild(nutCopy);

        khung.appendChild(header);

        // Body: code nguyên dạng
        const body = document.createElement('pre');
        body.classList.add('khung-code-body');
        body.textContent = noiDungCode;
        khung.appendChild(body);

        return khung;
    }

    /* ------------------------------------------------------------
       COPY TRỰC TIẾP (fallback nếu chưa có copy_code.js)
       ------------------------------------------------------------ */
    function copyTrucTiep(text, nut) {
        const chuCu = nut.textContent;
        const hienThiTam = function (chu) {
            nut.textContent = chu;
            setTimeout(function () {
                nut.textContent = chuCu;
            }, 1200);
        };

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(
                function () { hienThiTam('Đã chép'); },
                function () { hienThiTam('Lỗi'); }
            );
        } else {
            // Cách cũ cho trình duyệt không hỗ trợ clipboard API
            const tam = document.createElement('textarea');
            tam.value = text;
            tam.style.position = 'fixed';
            tam.style.opacity = '0';
            document.body.appendChild(tam);
            tam.select();
            try {
                document.execCommand('copy');
                hienThiTam('Đã chép');
            } catch (e) {
                hienThiTam('Lỗi');
            }
            document.body.removeChild(tam);
        }
    }

    /* ------------------------------------------------------------
       HÀM CHÍNH: HIỂN THỊ NỘI DUNG (CHỮ + CODE) VÀO 1 DIV TIN NHẮN
       ------------------------------------------------------------ */
    function hienThiCodeTrongTinNhan(divTinNhan, noiDung) {
        if (!divTinNhan) return;

        // Xóa nội dung cũ (nếu có)
        divTinNhan.innerHTML = '';

        const cacDoan = tachDoan(noiDung);

        cacDoan.forEach(function (doan) {
            if (doan.loai === 'chu') {
                const khungChu = document.createElement('div');
                khungChu.classList.add('khung-chu-tin-nhan');
                khungChu.textContent = doan.noiDung;
                divTinNhan.appendChild(khungChu);
            } else if (doan.loai === 'code') {
                const khungCode = taoKhungCode(doan.noiDung, doan.ngonNgu);
                divTinNhan.appendChild(khungCode);
            }
        });
    }

    /* ------------------------------------------------------------
       XUẤT HÀM RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.hienThiCodeTrongTinNhan = hienThiCodeTrongTinNhan;
    window.tachDoanCode = tachDoan;
    window.taoKhungCode = taoKhungCode;

    /* ------------------------------------------------------------
       HÀM TIỆN: HIỂN THỊ KHUNG CODE RIÊNG (gọi từ chat.js)
       ------------------------------------------------------------ */
    function hienThiKhungCode(code, ngonNgu) {
        const danhSach = document.getElementById('danh-sach-tin-nhan');
        if (!danhSach) return;

        const boc = document.createElement('div');
        boc.classList.add('tin-nhan', 'tin-nhan-rong');
        boc.appendChild(taoKhungCode(code, ngonNgu || 'code'));
        danhSach.appendChild(boc);

        if (typeof window.cuonXuongCuoi === 'function') {
            window.cuonXuongCuoi();
        }
    }

    window.hienThiKhungCode = hienThiKhungCode;

})();
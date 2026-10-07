/* ============================================================
   xu_ly_file.js - Xử lý file tài liệu đính kèm + modal xem to
   ------------------------------------------------------------
   Nhiệm vụ:
     - Nhận file từ input #input-file-tai-lieu (do xu_ly_anh.js mở).
     - Hiển thị preview trong #khung-preview.
     - Click preview file → mở modal xem toàn màn hình.
     - KHÔNG gửi ngay. Lưu vào window.DANH_SACH_FILE.
     - Khi chat.js gọi uploadTatCaFile() → upload lên server.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const inputFile       = document.getElementById('input-file-tai-lieu');
    const khungPreview    = document.getElementById('khung-preview');
    const modalFile       = document.getElementById('modal-xem-file');
    const modalFileTen    = document.getElementById('modal-file-ten');
    const modalFileBody   = document.getElementById('modal-file-body');
    const modalFileTai    = document.getElementById('modal-file-tai');
    const dongModalFile   = document.getElementById('dong-modal-file');

    if (!inputFile || !khungPreview) {
        return; // Thiếu DOM thì thoát.
    }

    /* ------------------------------------------------------------
       BIẾN TOÀN CỤC
       ------------------------------------------------------------ */
    window.DANH_SACH_FILE = window.DANH_SACH_FILE || [];

    /* ------------------------------------------------------------
       TẠO ID NGẪU NHIÊN
       ------------------------------------------------------------ */
    function taoId() {
        return 'file-' + Date.now() + '-' + Math.floor(Math.random() * 100000);
    }

    /* ------------------------------------------------------------
       LẤY ĐUÔI FILE
       ------------------------------------------------------------ */
    function layDuoi(tenFile) {
        if (!tenFile || tenFile.indexOf('.') < 0) return '';
        return tenFile.split('.').pop().toLowerCase();
    }

    /* ------------------------------------------------------------
       LẤY ICON THEO LOẠI FILE
       ------------------------------------------------------------ */
    function layIconFile(tenFile) {
        const duoi = layDuoi(tenFile);

        const svgMo = '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">';
        const svgDong = '</svg>';

        if (duoi === 'pdf') {
            return svgMo +
                '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
                '<polyline points="14,2 14,8 20,8"/>' +
                '<text x="12" y="18" font-size="6" text-anchor="middle" fill="currentColor" stroke="none">PDF</text>' +
                svgDong;
        }

        if (duoi === 'doc' || duoi === 'docx') {
            return svgMo +
                '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
                '<polyline points="14,2 14,8 20,8"/>' +
                '<text x="12" y="18" font-size="6" text-anchor="middle" fill="currentColor" stroke="none">DOC</text>' +
                svgDong;
        }

        if (duoi === 'xls' || duoi === 'xlsx' || duoi === 'csv') {
            return svgMo +
                '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
                '<polyline points="14,2 14,8 20,8"/>' +
                '<text x="12" y="18" font-size="6" text-anchor="middle" fill="currentColor" stroke="none">XLS</text>' +
                svgDong;
        }

        if (duoi === 'zip' || duoi === 'rar' || duoi === '7z') {
            return svgMo +
                '<path d="M21 8v13H3V8"/>' +
                '<path d="M1 3h22v5H1z"/>' +
                '<path d="M10 12h4"/>' +
                svgDong;
        }

        if (['png','jpg','jpeg','gif','webp','svg','bmp'].indexOf(duoi) >= 0) {
            return svgMo +
                '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>' +
                '<circle cx="8.5" cy="8.5" r="1.5"/>' +
                '<polyline points="21,15 16,10 5,21"/>' +
                svgDong;
        }

        // Mặc định: file text
        return svgMo +
            '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
            '<polyline points="14,2 14,8 20,8"/>' +
            '<line x1="16" y1="13" x2="8" y2="13"/>' +
            '<line x1="16" y1="17" x2="8" y2="17"/>' +
            svgDong;
    }

    /* ------------------------------------------------------------
       CẬP NHẬT KHUNG PREVIEW
       ------------------------------------------------------------ */
    function capNhatKhungPreview() {
        const coAnh  = window.DANH_SACH_ANH  && window.DANH_SACH_ANH.length > 0;
        const coFile = window.DANH_SACH_FILE && window.DANH_SACH_FILE.length > 0;

        if (!coAnh && !coFile) {
            khungPreview.classList.add('an');
        } else {
            khungPreview.classList.remove('an');
        }
    }

    /* ------------------------------------------------------------
       MỞ MODAL XEM FILE TOÀN MÀN HÌNH
       ------------------------------------------------------------ */
    function moModalFile(fileItem) {
        if (!modalFile || !modalFileBody) return;

        const file = fileItem.file;
        const duoi = layDuoi(file.name);
        const urlBlob = URL.createObjectURL(file);

        // Đặt tên file
        if (modalFileTen) modalFileTen.textContent = file.name;

        // Xóa nội dung cũ
        modalFileBody.innerHTML = '';

        // Hiển thị theo loại
        if (duoi === 'pdf') {
            const iframe = document.createElement('iframe');
            iframe.src = urlBlob;
            modalFileBody.appendChild(iframe);
        } else if (['png','jpg','jpeg','gif','webp','svg','bmp'].indexOf(duoi) >= 0) {
            const img = document.createElement('img');
            img.src = urlBlob;
            img.style.maxWidth = '100%';
            img.style.maxHeight = '100%';
            img.style.objectFit = 'contain';
            img.style.display = 'block';
            img.style.margin = '0 auto';
            modalFileBody.appendChild(img);
        } else if (duoi === 'txt' || duoi === 'md' || duoi === 'json' || duoi === 'csv' || duoi === 'log') {
            // Đọc text
            const reader = new FileReader();
            reader.onload = function (e) {
                const pre = document.createElement('pre');
                pre.textContent = e.target.result || '';
                modalFileBody.innerHTML = '';
                modalFileBody.appendChild(pre);
            };
            reader.readAsText(file);
        } else {
            // Loại khác → hiện icon + thông báo
            const div = document.createElement('div');
            div.style.textAlign = 'center';
            div.style.padding = '40px 20px';
            div.style.color = '#9ca3af';
            div.innerHTML = layIconFile(file.name) +
                '<div style="margin-top:12px;font-size:14px;">Không xem trực tiếp được định dạng này.</div>' +
                '<div style="margin-top:6px;font-size:12px;">Bấm "Tải về" để mở bằng ứng dụng khác.</div>';
            modalFileBody.appendChild(div);
        }

        // Nút tải về
        if (modalFileTai) {
            modalFileTai.href = urlBlob;
            modalFileTai.download = file.name;
        }

        // Mở modal
        modalFile.classList.remove('an');
        requestAnimationFrame(function () {
            modalFile.classList.add('dang-mo');
        });

        // Lưu URL để revoke khi đóng
        modalFile.__urlBlob = urlBlob;
    }

    function dongModalFileFn() {
        if (!modalFile) return;
        modalFile.classList.remove('dang-mo');
        const urlBlob = modalFile.__urlBlob;
        setTimeout(function () {
            modalFile.classList.add('an');
            if (modalFileBody) modalFileBody.innerHTML = '';
            if (urlBlob) URL.revokeObjectURL(urlBlob);
            modalFile.__urlBlob = null;
        }, 200);
    }

    /* ------------------------------------------------------------
       TẠO 1 Ô PREVIEW FILE
       ------------------------------------------------------------ */
    function taoPreview(fileItem) {
        const o = document.createElement('div');
        o.classList.add('preview-item');
        o.dataset.id = fileItem.id;

        // Icon
        const icon = document.createElement('div');
        icon.classList.add('preview-icon');
        icon.innerHTML = layIconFile(fileItem.file.name);
        o.appendChild(icon);

        // Tên file (rút gọn)
        const ten = document.createElement('div');
        ten.classList.add('ten-file');
        ten.textContent = fileItem.file.name;
        ten.title = fileItem.file.name;
        o.appendChild(ten);

        // Click vào preview → mở modal
        o.addEventListener('click', function (e) {
            if (e.target.classList.contains('preview-xoa')) return;
            moModalFile(fileItem);
        });

        // Nút [X]
        const nutXoa = document.createElement('button');
        nutXoa.classList.add('preview-xoa');
        nutXoa.type = 'button';
        nutXoa.setAttribute('aria-label', 'Xóa file');
        nutXoa.innerHTML = '&#10005;';
        nutXoa.addEventListener('click', function (e) {
            e.stopPropagation();
            xoaFile(fileItem.id);
        });
        o.appendChild(nutXoa);

        return o;
    }

    /* ------------------------------------------------------------
       VẼ LẠI PREVIEW FILE
       ------------------------------------------------------------ */
    function veLaiPreviewFile() {
        khungPreview.querySelectorAll('.preview-item[data-loai="file"]').forEach(function (el) {
            el.remove();
        });

        window.DANH_SACH_FILE.forEach(function (fileItem) {
            const o = taoPreview(fileItem);
            o.dataset.loai = 'file';
            khungPreview.appendChild(o);
        });

        capNhatKhungPreview();
    }

    /* ------------------------------------------------------------
       THÊM FILE
       ------------------------------------------------------------ */
    function themFile(files) {
        Array.from(files).forEach(function (file) {
            const id = taoId();
            window.DANH_SACH_FILE.push({ file: file, id: id });
        });
        veLaiPreviewFile();
    }

    /* ------------------------------------------------------------
       XÓA 1 FILE
       ------------------------------------------------------------ */
    function xoaFile(id) {
        const viTri = window.DANH_SACH_FILE.findIndex(function (f) { return f.id === id; });
        if (viTri < 0) return;
        window.DANH_SACH_FILE.splice(viTri, 1);
        veLaiPreviewFile();
    }

    /* ------------------------------------------------------------
       XÓA TOÀN BỘ FILE
       ------------------------------------------------------------ */
    function xoaTatCaFile() {
        window.DANH_SACH_FILE = [];
        veLaiPreviewFile();
    }

    /* ------------------------------------------------------------
       UPLOAD FILE LÊN SERVER
       ------------------------------------------------------------ */
    async function uploadTatCaFile() {
        if (window.DANH_SACH_FILE.length === 0) return [];

        const formData = new FormData();
        window.DANH_SACH_FILE.forEach(function (fileItem) {
            formData.append('file', fileItem.file);
        });

        try {
            const phanHoi = await fetch('/api/upload-file', {
                method: 'POST',
                body: formData,
            });
            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong && Array.isArray(duLieu.urls)) {
                return duLieu.urls;
            }
            return [];
        } catch (e) {
            console.error('Lỗi upload file:', e);
            return [];
        }
    }

    /* ------------------------------------------------------------
       SỰ KIỆN
       ------------------------------------------------------------ */
    inputFile.addEventListener('change', function () {
        if (inputFile.files && inputFile.files.length) {
            themFile(inputFile.files);
        }
        inputFile.value = '';
    });

    if (dongModalFile) {
        dongModalFile.addEventListener('click', dongModalFileFn);
    }

    if (modalFile) {
        modalFile.addEventListener('click', function (e) {
            // Bấm ra ngoài modal → đóng
            if (e.target === modalFile) {
                dongModalFileFn();
            }
        });
    }

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.themFile = themFile;
    window.xoaFile = xoaFile;
    window.xoaTatCaFile = xoaTatCaFile;
    window.uploadTatCaFile = uploadTatCaFile;
    window.veLaiPreviewFile = veLaiPreviewFile;
    window.moModalFile = moModalFile;

    /* ------------------------------------------------------------
       KHỞI ĐỘNG
       ------------------------------------------------------------ */
    function khoiDong() {
        capNhatKhungPreview();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

})();
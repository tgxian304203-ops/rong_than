/* ============================================================
   xu_ly_file.js - Xử lý file tài liệu người dùng đính kèm
   ------------------------------------------------------------
   Nhiệm vụ:
     - Nhận file từ input #input-file-tai-lieu (do xu_ly_anh.js mở).
     - Hiển thị preview trong #khung-preview (icon + tên file + nút X).
     - KHÔNG gửi ngay. Chỉ lưu vào biến toàn cục window.DANH_SACH_FILE.
     - Khi bấm [➤] (xử lý ở chat.js) → file sẽ được upload + gửi kèm.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const inputFile    = document.getElementById('input-file-tai-lieu');
    const khungPreview = document.getElementById('khung-preview');

    if (!inputFile || !khungPreview) {
        return; // Thiếu DOM thì thoát.
    }

    /* ------------------------------------------------------------
       BIẾN TOÀN CỤC LƯU FILE CHỜ GỬI
       Mỗi phần tử: { file: File, id: string }
       ------------------------------------------------------------ */
    window.DANH_SACH_FILE = window.DANH_SACH_FILE || [];

    /* ------------------------------------------------------------
       TẠO ID NGẪU NHIÊN
       ------------------------------------------------------------ */
    function taoId() {
        return 'file-' + Date.now() + '-' + Math.floor(Math.random() * 100000);
    }

    /* ------------------------------------------------------------
       LẤY ICON THEO LOẠI FILE (SVG inline)
       ------------------------------------------------------------ */
    function layIconFile(tenFile) {
        const t = String(tenFile || '').toLowerCase();
        const duoi = t.split('.').pop();

        const svgMo = '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">';
        const svgDong = '</svg>';

        // PDF
        if (duoi === 'pdf') {
            return svgMo +
                '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
                '<polyline points="14,2 14,8 20,8"/>' +
                '<text x="12" y="18" font-size="6" text-anchor="middle" fill="currentColor" stroke="none">PDF</text>' +
                svgDong;
        }

        // Word
        if (duoi === 'doc' || duoi === 'docx') {
            return svgMo +
                '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
                '<polyline points="14,2 14,8 20,8"/>' +
                '<text x="12" y="18" font-size="6" text-anchor="middle" fill="currentColor" stroke="none">DOC</text>' +
                svgDong;
        }

        // Excel
        if (duoi === 'xls' || duoi === 'xlsx' || duoi === 'csv') {
            return svgMo +
                '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
                '<polyline points="14,2 14,8 20,8"/>' +
                '<text x="12" y="18" font-size="6" text-anchor="middle" fill="currentColor" stroke="none">XLS</text>' +
                svgDong;
        }

        // Zip / Rar
        if (duoi === 'zip' || duoi === 'rar' || duoi === '7z') {
            return svgMo +
                '<path d="M21 8v13H3V8"/>' +
                '<path d="M1 3h22v5H1z"/>' +
                '<path d="M10 12h4"/>' +
                svgDong;
        }

        // Ảnh (phòng trường hợp người dùng chọn ảnh ở đây)
        if (['png','jpg','jpeg','gif','webp','svg','bmp'].includes(duoi)) {
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
       CẬP NHẬT TRẠNG THÁI KHUNG PREVIEW
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
       VẼ LẠI TOÀN BỘ PREVIEW FILE
       ------------------------------------------------------------ */
    function veLaiPreviewFile() {
        // Xóa các preview file cũ
        khungPreview.querySelectorAll('.preview-item[data-loai="file"]').forEach(function (el) {
            el.remove();
        });

        // Vẽ lại file
        window.DANH_SACH_FILE.forEach(function (fileItem) {
            const o = taoPreview(fileItem);
            o.dataset.loai = 'file';
            khungPreview.appendChild(o);
        });

        capNhatKhungPreview();
    }

    /* ------------------------------------------------------------
       THÊM FILE VÀO DANH SÁCH CHỜ
       ------------------------------------------------------------ */
    function themFile(files) {
        Array.from(files).forEach(function (file) {
            const id = taoId();
            window.DANH_SACH_FILE.push({ file: file, id: id });
        });

        veLaiPreviewFile();
    }

    /* ------------------------------------------------------------
       XÓA 1 FILE KHỎI DANH SÁCH CHỜ
       ------------------------------------------------------------ */
    function xoaFile(id) {
        const viTri = window.DANH_SACH_FILE.findIndex(function (f) { return f.id === id; });
        if (viTri < 0) return;

        window.DANH_SACH_FILE.splice(viTri, 1);
        veLaiPreviewFile();
    }

    /* ------------------------------------------------------------
       XÓA TOÀN BỘ FILE (dùng sau khi gửi xong)
       ------------------------------------------------------------ */
    function xoaTatCaFile() {
        window.DANH_SACH_FILE = [];
        veLaiPreviewFile();
    }

    /* ------------------------------------------------------------
       UPLOAD FILE LÊN SERVER
       Trả về mảng URL server để gắn vào tin nhắn.
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
        inputFile.value = ''; // cho phép chọn lại cùng file
    });

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.themFile = themFile;
    window.xoaFile = xoaFile;
    window.xoaTatCaFile = xoaTatCaFile;
    window.uploadTatCaFile = uploadTatCaFile;
    window.veLaiPreviewFile = veLaiPreviewFile;

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
/* ============================================================
   xu_ly_anh.js - Xử lý ảnh người dùng đính kèm
   ------------------------------------------------------------
   Nhiệm vụ:
     - Lắng nghe nút [+] (#nut-dinh-kem) → mở hộp chọn ảnh.
     - Khi người dùng chọn ảnh → hiển thị preview trong #khung-preview.
     - Mỗi preview có nút [X] để xóa ảnh khỏi danh sách chờ gửi.
     - KHÔNG gửi ảnh ngay. Chỉ lưu vào biến toàn cục window.DANH_SACH_ANH.
     - Khi bấm [➤] (xử lý ở chat.js) → ảnh sẽ được upload + gửi kèm.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const nutDinhKem = document.getElementById('nut-dinh-kem');
    const inputAnh   = document.getElementById('input-file-anh');
    const khungPreview = document.getElementById('khung-preview');

    if (!nutDinhKem || !inputAnh || !khungPreview) {
        return; // Thiếu DOM thì thoát.
    }

    /* ------------------------------------------------------------
       BIẾN TOÀN CỤC LƯU ẢNH CHỜ GỬI
       Mỗi phần tử: { file: File, url: string, id: string }
       ------------------------------------------------------------ */
    window.DANH_SACH_ANH = window.DANH_SACH_ANH || [];

    /* ------------------------------------------------------------
       TẠO ID NGẪU NHIÊN
       ------------------------------------------------------------ */
    function taoId() {
        return 'anh-' + Date.now() + '-' + Math.floor(Math.random() * 100000);
    }

    /* ------------------------------------------------------------
       CẬP NHẬT TRẠNG THÁI KHUNG PREVIEW
       Ẩn khi rỗng, hiện khi có ảnh.
       ------------------------------------------------------------ */
    function capNhatKhungPreview() {
        if (window.DANH_SACH_ANH.length === 0 && 
            (!window.DANH_SACH_FILE || window.DANH_SACH_FILE.length === 0)) {
            khungPreview.classList.add('an');
        } else {
            khungPreview.classList.remove('an');
        }
    }

    /* ------------------------------------------------------------
       TẠO 1 Ô PREVIEW ẢNH
       ------------------------------------------------------------ */
    function taoPreview(anh) {
        const o = document.createElement('div');
        o.classList.add('preview-item');
        o.dataset.id = anh.id;

        const img = document.createElement('img');
        img.src = anh.url;
        img.alt = anh.file.name;
        o.appendChild(img);

        // Nút [X] xóa
        const nutXoa = document.createElement('button');
        nutXoa.classList.add('preview-xoa');
        nutXoa.type = 'button';
        nutXoa.setAttribute('aria-label', 'Xóa ảnh');
        nutXoa.innerHTML = '&#10005;';
        nutXoa.addEventListener('click', function (e) {
            e.stopPropagation();
            xoaAnh(anh.id);
        });
        o.appendChild(nutXoa);

        return o;
    }

    /* ------------------------------------------------------------
       VẼ LẠI TOÀN BỘ PREVIEW ẢNH
       ------------------------------------------------------------ */
    function veLaiPreviewAnh() {
        // Xóa các preview ảnh cũ (giữ lại preview file nếu có)
        khungPreview.querySelectorAll('.preview-item[data-loai="anh"]').forEach(function (el) {
            el.remove();
        });

        // Vẽ lại ảnh
        window.DANH_SACH_ANH.forEach(function (anh) {
            const o = taoPreview(anh);
            o.dataset.loai = 'anh';
            khungPreview.appendChild(o);
        });

        capNhatKhungPreview();
    }

    /* ------------------------------------------------------------
       THÊM ẢNH VÀO DANH SÁCH CHỜ
       ------------------------------------------------------------ */
    function themAnh(files) {
        Array.from(files).forEach(function (file) {
            if (!file.type.startsWith('image/')) return;

            const id = taoId();
            const url = URL.createObjectURL(file);

            window.DANH_SACH_ANH.push({ file: file, url: url, id: id });
        });

        veLaiPreviewAnh();
    }

    /* ------------------------------------------------------------
       XÓA 1 ẢNH KHỎI DANH SÁCH CHỜ
       ------------------------------------------------------------ */
    function xoaAnh(id) {
        const viTri = window.DANH_SACH_ANH.findIndex(function (a) { return a.id === id; });
        if (viTri < 0) return;

        const anh = window.DANH_SACH_ANH[viTri];
        // Giải phóng URL
        if (anh.url) URL.revokeObjectURL(anh.url);

        window.DANH_SACH_ANH.splice(viTri, 1);
        veLaiPreviewAnh();
    }

    /* ------------------------------------------------------------
       XÓA TOÀN BỘ ẢNH (dùng sau khi gửi xong)
       ------------------------------------------------------------ */
    function xoaTatCaAnh() {
        window.DANH_SACH_ANH.forEach(function (anh) {
            if (anh.url) URL.revokeObjectURL(anh.url);
        });
        window.DANH_SACH_ANH = [];
        veLaiPreviewAnh();
    }

    /* ------------------------------------------------------------
       UPLOAD ẢNH LÊN SERVER
       Trả về mảng URL server để gắn vào tin nhắn.
       ------------------------------------------------------------ */
    async function uploadTatCaAnh() {
        if (window.DANH_SACH_ANH.length === 0) return [];

        const formData = new FormData();
        window.DANH_SACH_ANH.forEach(function (anh) {
            formData.append('anh', anh.file);
        });

        try {
            const phanHoi = await fetch('/api/upload-anh', {
                method: 'POST',
                body: formData,
            });
            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong && Array.isArray(duLieu.urls)) {
                return duLieu.urls;
            }
            return [];
        } catch (e) {
            console.error('Lỗi upload ảnh:', e);
            return [];
        }
    }

    /* ------------------------------------------------------------
       SỰ KIỆN
       ------------------------------------------------------------ */
    nutDinhKem.addEventListener('click', function (e) {
        e.preventDefault();
        // Nếu có ảnh + file thì mở menu chọn? Hiện tại chỉ mở ảnh.
        // File tài liệu được xử lý riêng — có thể nhấn giữ.
        inputAnh.click();
    });

    // Nhấn giữ nút [+] để chọn file tài liệu
    let idGiu = null;
    nutDinhKem.addEventListener('pointerdown', function () {
        idGiu = setTimeout(function () {
            // Nhấn giữ 500ms → mở chọn file tài liệu
            const inputFile = document.getElementById('input-file-tai-lieu');
            if (inputFile) inputFile.click();
            idGiu = null;
        }, 500);
    });

    ['pointerup', 'pointerleave', 'pointercancel'].forEach(function (ev) {
        nutDinhKem.addEventListener(ev, function () {
            if (idGiu) {
                clearTimeout(idGiu);
                idGiu = null;
            }
        });
    });

    inputAnh.addEventListener('change', function () {
        if (inputAnh.files && inputAnh.files.length) {
            themAnh(inputAnh.files);
        }
        inputAnh.value = ''; // cho phép chọn lại cùng file
    });

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.themAnh = themAnh;
    window.xoaAnh = xoaAnh;
    window.xoaTatCaAnh = xoaTatCaAnh;
    window.uploadTatCaAnh = uploadTatCaAnh;
    window.veLaiPreviewAnh = veLaiPreviewAnh;
    window.capNhatKhungPreview = capNhatKhungPreview;

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
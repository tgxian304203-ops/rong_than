/* ============================================================
   xu_ly_anh.js - Xử lý ảnh đính kèm + menu chọn Ảnh/File/Camera
   ------------------------------------------------------------
   Nhiệm vụ:
     - Bấm nút [+] (#nut-dinh-kem) → hiện menu 3 mục:
         🖼 Máy ảnh  → mở camera chụp ảnh
         🖼 Hình     → chọn ảnh từ thư viện
         🖼 Tệp      → chọn file tài liệu
     - Ảnh chọn xong → preview trong #khung-preview.
     - Click preview ảnh → mở modal xem toàn màn hình.
     - Lưu vào window.DANH_SACH_ANH, chờ chat.js upload.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const nutDinhKem    = document.getElementById('nut-dinh-kem');
    const inputAnh      = document.getElementById('input-file-anh');
    const inputFile     = document.getElementById('input-file-tai-lieu');
    const inputCamera   = document.getElementById('input-camera');
    const khungPreview  = document.getElementById('khung-preview');
    const modalAnh      = document.getElementById('modal-xem-anh');
    const modalAnhImg   = document.getElementById('modal-anh-img');
    const dongModalAnh  = document.getElementById('dong-modal-anh');

    if (!nutDinhKem || !inputAnh || !khungPreview) {
        return; // Thiếu DOM thì thoát.
    }

    /* ------------------------------------------------------------
       BIẾN TOÀN CỤC
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
       MỞ MODAL XEM ẢNH TOÀN MÀN HÌNH
       ------------------------------------------------------------ */
    function moModalAnh(urlAnh) {
        if (!modalAnh || !modalAnhImg) return;
        modalAnhImg.src = urlAnh;
        modalAnh.classList.remove('an');
        // trigger animation
        requestAnimationFrame(function () {
            modalAnh.classList.add('dang-mo');
        });
    }

    function dongModalAnhFn() {
        if (!modalAnh) return;
        modalAnh.classList.remove('dang-mo');
        setTimeout(function () {
            modalAnh.classList.add('an');
            if (modalAnhImg) modalAnhImg.src = '';
        }, 200);
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

        // Click vào ảnh → mở modal
        o.addEventListener('click', function (e) {
            // Nếu click vào nút X → không mở modal
            if (e.target.classList.contains('preview-xoa')) return;
            moModalAnh(anh.url);
        });

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
        khungPreview.querySelectorAll('.preview-item[data-loai="anh"]').forEach(function (el) {
            el.remove();
        });

        window.DANH_SACH_ANH.forEach(function (anh) {
            const o = taoPreview(anh);
            o.dataset.loai = 'anh';
            khungPreview.appendChild(o);
        });

        capNhatKhungPreview();
    }

    /* ------------------------------------------------------------
       THÊM ẢNH
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
       XÓA 1 ẢNH
       ------------------------------------------------------------ */
    function xoaAnh(id) {
        const viTri = window.DANH_SACH_ANH.findIndex(function (a) { return a.id === id; });
        if (viTri < 0) return;
        const anh = window.DANH_SACH_ANH[viTri];
        if (anh.url) URL.revokeObjectURL(anh.url);
        window.DANH_SACH_ANH.splice(viTri, 1);
        veLaiPreviewAnh();
    }

    /* ------------------------------------------------------------
       XÓA TOÀN BỘ ẢNH
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
       SVG ICON
       ------------------------------------------------------------ */
    const SVG_CAMERA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>';

    const SVG_HINH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21,15 16,10 5,21"/></svg>';

    const SVG_TEP = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>';

    /* ------------------------------------------------------------
       MENU CHỌN ĐÍNH KÈM
       ------------------------------------------------------------ */
    let menuDangMo = null;

    function dongMenu() {
        if (menuDangMo) {
            menuDangMo.remove();
            menuDangMo = null;
        }
    }

    function moMenuChon() {
        dongMenu();

        const menu = document.createElement('div');
        menu.className = 'menu-chon-dinh-kem';

        // Nút Máy ảnh
        const nutCamera = document.createElement('button');
        nutCamera.type = 'button';
        nutCamera.className = 'menu-chon-item';
        nutCamera.innerHTML = SVG_CAMERA + '<span>Máy ảnh</span>';
        nutCamera.addEventListener('click', function (e) {
            e.stopPropagation();
            dongMenu();
            if (inputCamera) inputCamera.click();
        });
        menu.appendChild(nutCamera);

        // Nút Hình
        const nutHinh = document.createElement('button');
        nutHinh.type = 'button';
        nutHinh.className = 'menu-chon-item';
        nutHinh.innerHTML = SVG_HINH + '<span>Hình</span>';
        nutHinh.addEventListener('click', function (e) {
            e.stopPropagation();
            dongMenu();
            inputAnh.click();
        });
        menu.appendChild(nutHinh);

        // Nút Tệp
        const nutTep = document.createElement('button');
        nutTep.type = 'button';
        nutTep.className = 'menu-chon-item';
        nutTep.innerHTML = SVG_TEP + '<span>Tệp</span>';
        nutTep.addEventListener('click', function (e) {
            e.stopPropagation();
            dongMenu();
            if (inputFile) inputFile.click();
        });
        menu.appendChild(nutTep);

        // Đặt vị trí trên nút [+]
        const rect = nutDinhKem.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.left = rect.left + 'px';
        menu.style.bottom = (window.innerHeight - rect.top + 8) + 'px';
        menu.style.zIndex = '9999';

        document.body.appendChild(menu);
        menuDangMo = menu;

        // Bấm ra ngoài → đóng
        setTimeout(function () {
            document.addEventListener('click', dongMenu, { once: true });
        }, 0);
    }

    /* ------------------------------------------------------------
       SỰ KIỆN
       ------------------------------------------------------------ */
    nutDinhKem.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        moMenuChon();
    });

    inputAnh.addEventListener('change', function () {
        if (inputAnh.files && inputAnh.files.length) {
            themAnh(inputAnh.files);
        }
        inputAnh.value = '';
    });

    if (inputCamera) {
        inputCamera.addEventListener('change', function () {
            if (inputCamera.files && inputCamera.files.length) {
                themAnh(inputCamera.files);
            }
            inputCamera.value = '';
        });
    }

    if (dongModalAnh) {
        dongModalAnh.addEventListener('click', dongModalAnhFn);
    }

    if (modalAnh) {
        modalAnh.addEventListener('click', function (e) {
            // Bấm ra ngoài ảnh → đóng
            if (e.target === modalAnh || e.target.id === 'modal-anh-noi-dung') {
                dongModalAnhFn();
            }
        });
    }

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.themAnh = themAnh;
    window.xoaAnh = xoaAnh;
    window.xoaTatCaAnh = xoaTatCaAnh;
    window.uploadTatCaAnh = uploadTatCaAnh;
    window.veLaiPreviewAnh = veLaiPreviewAnh;
    window.capNhatKhungPreview = capNhatKhungPreview;
    window.moModalAnh = moModalAnh;

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
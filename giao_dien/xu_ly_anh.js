/* ============================================================
   xu_ly_anh.js - Xử lý ảnh đính kèm + menu Ảnh/File/Camera
   ------------------------------------------------------------
   ĐÃ SỬA:
     - Upload ngay khi chọn ảnh (không chờ bấm gửi).
     - Hiện vòng tròn quay trong lúc upload.
     - Lỗi upload → hiện ⚠️.
     - Lưu URL server vào window.DANH_SACH_ANH.
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
        return;
    }

    /* ------------------------------------------------------------
       BIẾN TOÀN CỤC
       Mỗi phần tử: { file, url (blob tạm), url_server (sau upload),
                      id, dangTai, loi }
       ------------------------------------------------------------ */
    window.DANH_SACH_ANH = window.DANH_SACH_ANH || [];

    /* ------------------------------------------------------------
       TẠO ID
       ------------------------------------------------------------ */
    function taoId() {
        return 'anh-' + Date.now() + '-' + Math.floor(Math.random() * 100000);
    }

    /* ------------------------------------------------------------
       CẬP NHẬT KHUNG PREVIEW
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
       MODAL XEM ẢNH
       ------------------------------------------------------------ */
    function moModalAnh(urlAnh) {
        if (!modalAnh || !modalAnhImg) return;
        modalAnhImg.src = urlAnh;
        modalAnh.classList.remove('an');
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
       TẠO PREVIEW ẢNH (dựa trên trạng thái: đang tải, lỗi, xong)
       ------------------------------------------------------------ */
    function taoPreview(anh) {
        const o = document.createElement('div');
        o.classList.add('preview-item');
        o.dataset.id = anh.id;

        // Đang upload → vòng tròn quay
        if (anh.dangTai) {
            const vong = document.createElement('div');
            vong.className = 'vong-quay';
            o.appendChild(vong);
        }
        // Lỗi upload → ⚠️
        else if (anh.loi) {
            const loiIcon = document.createElement('div');
            loiIcon.className = 'preview-loi';
            loiIcon.textContent = '⚠️';
            o.appendChild(loiIcon);
        }
        // Xong → hiện ảnh
        else {
            const img = document.createElement('img');
            img.src = anh.url;
            img.alt = anh.file ? anh.file.name : 'ảnh';
            o.appendChild(img);

            o.addEventListener('click', function (e) {
                if (e.target.classList.contains('preview-xoa')) return;
                moModalAnh(anh.url);
            });
        }

        // Nút X
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
        capNhatTrangThaiNutGui();
    }

    /* ------------------------------------------------------------
       KIỂM TRA CÓ ĐANG UPLOAD KHÔNG
       ------------------------------------------------------------ */
    function dangUploadAnh() {
        return window.DANH_SACH_ANH.some(function (a) { return a.dangTai === true; });
    }

    function dangUploadFile() {
        if (!window.DANH_SACH_FILE) return false;
        return window.DANH_SACH_FILE.some(function (f) { return f.dangTai === true; });
    }

    function coLoiUpload() {
        const loiAnh = window.DANH_SACH_ANH.some(function (a) { return a.loi === true; });
        const loiFile = (window.DANH_SACH_FILE || []).some(function (f) { return f.loi === true; });
        return loiAnh || loiFile;
    }

    function capNhatTrangThaiNutGui() {
        const nutGui = document.getElementById('nut-gui');
        const nutGuiDuAn = document.getElementById('nut-gui-du-an');
        const coUploadDangChay = dangUploadAnh() || dangUploadFile();
        const coLoi = coLoiUpload();

        if (nutGui) {
            nutGui.disabled = coUploadDangChay || coLoi;
        }
        if (nutGuiDuAn) {
            nutGuiDuAn.disabled = coUploadDangChay || coLoi;
        }
    }

    /* ------------------------------------------------------------
       UPLOAD 1 ẢNH
       ------------------------------------------------------------ */
    async function uploadMotAnh(anh) {
        const formData = new FormData();
        formData.append('anh', anh.file);

        // Gửi kèm id_tro_chuyen + id_du_an nếu đang chat dự án
        const idTro = window.__ID_TRO_CHUYEN_DANG_CHAT;
        const idDuAn = window.__ID_DU_AN_DANG_CHAT;
        if (idTro) formData.append('id_tro_chuyen', idTro);
        if (idDuAn) formData.append('id_du_an', idDuAn);

        try {
            const phanHoi = await fetch('/api/upload-anh', {
                method: 'POST',
                body: formData,
            });
            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong && Array.isArray(duLieu.urls) && duLieu.urls.length > 0) {
                anh.url_server = duLieu.urls[0];
                anh.dangTai = false;
                anh.loi = false;
            } else {
                anh.dangTai = false;
                anh.loi = true;
            }
        } catch (e) {
            console.error('Lỗi upload ảnh:', e);
            anh.dangTai = false;
            anh.loi = true;
        }

        veLaiPreviewAnh();
    }

    /* ------------------------------------------------------------
       THÊM ẢNH — UPLOAD NGAY
       ------------------------------------------------------------ */
    function themAnh(files) {
        Array.from(files).forEach(function (file) {
            if (!file.type.startsWith('image/')) return;

            const id = taoId();
            const url = URL.createObjectURL(file);

            const anh = {
                file: file,
                url: url,
                url_server: null,
                id: id,
                dangTai: true,
                loi: false,
            };
            window.DANH_SACH_ANH.push(anh);
        });

        veLaiPreviewAnh();

        // Upload song song từng ảnh
        window.DANH_SACH_ANH.forEach(function (anh) {
            if (anh.dangTai) {
                uploadMotAnh(anh);
            }
        });
    }

    /* ------------------------------------------------------------
       XÓA ẢNH
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
       XÓA TẤT CẢ ẢNH
       ------------------------------------------------------------ */
    function xoaTatCaAnh() {
        window.DANH_SACH_ANH.forEach(function (anh) {
            if (anh.url) URL.revokeObjectURL(anh.url);
        });
        window.DANH_SACH_ANH = [];
        veLaiPreviewAnh();
    }

    /* ------------------------------------------------------------
       LẤY DANH SÁCH URL SERVER (dùng trong chat.js)
       ------------------------------------------------------------ */
    function layUrlsAnhDaUpload() {
        return window.DANH_SACH_ANH
            .filter(function (a) { return a.url_server && !a.loi; })
            .map(function (a) { return a.url_server; });
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

        const rect = nutDinhKem.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.left = rect.left + 'px';
        menu.style.bottom = (window.innerHeight - rect.top + 8) + 'px';
        menu.style.zIndex = '9999';

        document.body.appendChild(menu);
        menuDangMo = menu;

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
    window.veLaiPreviewAnh = veLaiPreviewAnh;
    window.capNhatKhungPreview = capNhatKhungPreview;
    window.capNhatTrangThaiNutGui = capNhatTrangThaiNutGui;
    window.dangUploadAnh = dangUploadAnh;
    window.dangUploadFile = dangUploadFile;
    window.coLoiUpload = coLoiUpload;
    window.moModalAnh = moModalAnh;
    window.layUrlsAnhDaUpload = layUrlsAnhDaUpload;

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
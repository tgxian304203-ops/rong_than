/* ============================================================
   chat.js - Gửi/nhận tin nhắn (chat chính + chat trong dự án)
   ------------------------------------------------------------
   ĐÃ SỬA:
     - Upload ảnh + file trước khi gửi tin nhắn.
     - Hiển thị thumbnail ảnh + icon file trong tin nhắn.
     - Click ảnh/file trong chat → mở modal xem toàn màn hình.
     - Xóa preview sau khi gửi thành công.
     - Cập nhật tên chat nhanh sau tin nhắn đầu.
     - Lưu tin nhắn khách vào localStorage.
   ============================================================ */

(function () {
    'use strict';

    const oNhap = document.getElementById('o-nhap');
    const nutGui = document.getElementById('nut-gui');
    const danhSach = document.getElementById('danh-sach-tin-nhan');
    const khungChat = document.getElementById('khung-chat');

    const oNhapDuAn = document.getElementById('o-nhap-du-an');
    const nutGuiDuAn = document.getElementById('nut-gui-du-an');
    const danhSachDuAn = document.getElementById('danh-sach-tin-nhan-du-an');
    const khungChatDuAn = document.getElementById('khung-chat-du-an');

    const CHIEU_CAO_DONG = 24;
    const SO_DONG_TOI_DA = 6;
    const CHIEU_CAO_TOI_DA = CHIEU_CAO_DONG * SO_DONG_TOI_DA;

    let dangGui = false;
    let dangGuiDuAn = false;

    /* ============================================================
       TIỆN ÍCH
       ============================================================ */
    function cuonXuongCuoi(khung) {
        if (khung) khung.scrollTop = khung.scrollHeight;
    }

    function tuDongGian(o) {
        if (!o) return;
        o.style.height = 'auto';
        const cao = Math.min(o.scrollHeight, CHIEU_CAO_TOI_DA);
        o.style.height = cao + 'px';
    }

    /* ------------------------------------------------------------
       LẤY ĐUÔI FILE
       ------------------------------------------------------------ */
    function layDuoi(tenFile) {
        if (!tenFile || tenFile.indexOf('.') < 0) return '';
        return tenFile.split('.').pop().toLowerCase();
    }

    /* ------------------------------------------------------------
       SVG ICON CHO FILE TRONG CHAT
       ------------------------------------------------------------ */
    function layIconFileChat(tenFile) {
        const duoi = layDuoi(tenFile);
        const svgMo = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">';
        const svgDong = '</svg>';

        if (duoi === 'pdf' || duoi === 'doc' || duoi === 'docx' ||
            duoi === 'xls' || duoi === 'xlsx' || duoi === 'csv' ||
            duoi === 'txt' || duoi === 'md') {
            return svgMo +
                '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
                '<polyline points="14,2 14,8 20,8"/>' +
                '<line x1="16" y1="13" x2="8" y2="13"/>' +
                '<line x1="16" y1="17" x2="8" y2="17"/>' +
                svgDong;
        }

        if (duoi === 'zip' || duoi === 'rar' || duoi === '7z') {
            return svgMo +
                '<path d="M21 8v13H3V8"/>' +
                '<path d="M1 3h22v5H1z"/>' +
                '<path d="M10 12h4"/>' +
                svgDong;
        }

        return svgMo +
            '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
            '<polyline points="14,2 14,8 20,8"/>' +
            svgDong;
    }

    /* ============================================================
       TẠO TIN NHẮN
       ============================================================ */
    function taoTinNhan(noiDung, loai) {
        const div = document.createElement('div');
        div.classList.add('tin-nhan');
        if (loai === 'rong') {
            div.classList.add('tin-nhan-rong');
        } else if (loai === 'nguoi') {
            div.classList.add('tin-nhan-nguoi');
        } else {
            div.classList.add('tin-nhan-he-thong');
        }
        if (noiDung) {
            div.textContent = noiDung;
        }
        return div;
    }

    /* ------------------------------------------------------------
       TẠO TIN NHẮN CÓ ĐÍNH KÈM (ảnh + file)
       urlsAnh: mảng URL ảnh đã upload
       urlsFile: mảng URL file đã upload
       tenFiles: mảng tên file (để hiện icon + tên)
       ------------------------------------------------------------ */
    function taoTinNhanCoDinhKem(noiDung, loai, urlsAnh, urlsFile, tenFiles) {
        const div = taoTinNhan(noiDung, loai);

        if ((urlsAnh && urlsAnh.length > 0) || (urlsFile && urlsFile.length > 0)) {
            const khungDinhKem = document.createElement('div');
            khungDinhKem.classList.add('tin-nhan-dinh-kem');

            // Ảnh
            if (urlsAnh && urlsAnh.length > 0) {
                urlsAnh.forEach(function (url) {
                    const img = document.createElement('img');
                    img.classList.add('tin-nhan-anh');
                    img.src = url;
                    img.alt = 'Ảnh đính kèm';
                    img.addEventListener('click', function () {
                        if (typeof window.moModalAnh === 'function') {
                            window.moModalAnh(url);
                        }
                    });
                    khungDinhKem.appendChild(img);
                });
            }

            // File
            if (urlsFile && urlsFile.length > 0) {
                urlsFile.forEach(function (url, i) {
                    const tenFile = (tenFiles && tenFiles[i]) ? tenFiles[i] : url.split('/').pop();

                    const khoiFile = document.createElement('div');
                    khoiFile.classList.add('tin-nhan-file');
                    khoiFile.innerHTML = layIconFileChat(tenFile) +
                        '<span class="ten-file-chat">' + tenFile + '</span>';

                    khoiFile.addEventListener('click', function () {
                        // Mở link trong tab mới (ảnh/PDF xem được, khác tải về)
                        window.open(url, '_blank');
                    });

                    khungDinhKem.appendChild(khoiFile);
                });
            }

            div.appendChild(khungDinhKem);
        }

        return div;
    }

    function themTinNhanRong(noiDung) {
        if (!danhSach) return;
        danhSach.appendChild(taoTinNhan(noiDung, 'rong'));
        cuonXuongCuoi(khungChat);
    }

    function themTinNhanNguoi(noiDung) {
        if (!danhSach) return;
        danhSach.appendChild(taoTinNhan(noiDung, 'nguoi'));
        cuonXuongCuoi(khungChat);
    }

    function themTinNhanHeThong(noiDung) {
        if (!danhSach) return;
        danhSach.appendChild(taoTinNhan(noiDung, 'he-thong'));
        cuonXuongCuoi(khungChat);
    }

    /* ============================================================
       ĐANG TRẢ LỜI
       ============================================================ */
    function hienDangTraLoi(khung, idThem) {
        const div = document.createElement('div');
        div.classList.add('tin-nhan', 'tin-nhan-rong');
        div.id = idThem;
        div.textContent = '🌕🐉 Đang suy nghĩ...';
        if (khung) khung.appendChild(div);
        if (khung && khung.parentElement) {
            khung.parentElement.scrollTop = khung.parentElement.scrollHeight;
        }
        return div;
    }

    function xoaDangTraLoi(idThem) {
        const el = document.getElementById(idThem);
        if (el) el.remove();
    }

    /* ============================================================
       ĐẾM SỐ TIN NHẮN ĐÃ GỬI TRONG CHAT NHANH HIỆN TẠI
       ============================================================ */
    function demTinNhanNguoiTrongChatChinh() {
        if (!danhSach) return 0;
        let dem = 0;
        for (let i = 0; i < danhSach.children.length; i++) {
            if (danhSach.children[i].classList.contains('tin-nhan-nguoi')) {
                dem++;
            }
        }
        return dem;
    }

    /* ============================================================
       UPLOAD ẢNH + FILE TRƯỚC KHI GỬI
       Trả về { urls_anh, urls_file, ten_files }
       ============================================================ */
    async function uploadDinhKem() {
        let urls_anh = [];
        let urls_file = [];
        let ten_files = [];

        // Ảnh
        try {
            if (typeof window.uploadTatCaAnh === 'function' &&
                window.DANH_SACH_ANH && window.DANH_SACH_ANH.length > 0) {
                urls_anh = await window.uploadTatCaAnh();
            }
        } catch (e) {
            console.error('Lỗi upload ảnh:', e);
        }

        // File
        try {
            if (typeof window.uploadTatCaFile === 'function' &&
                window.DANH_SACH_FILE && window.DANH_SACH_FILE.length > 0) {
                // Lưu tên file trước khi upload (vì xóaTatCaFile sẽ xóa)
                ten_files = window.DANH_SACH_FILE.map(function (f) { return f.file.name; });
                urls_file = await window.uploadTatCaFile();
            }
        } catch (e) {
            console.error('Lỗi upload file:', e);
        }

        return { urls_anh: urls_anh, urls_file: urls_file, ten_files: ten_files };
    }

    function xoaHetPreview() {
        if (typeof window.xoaTatCaAnh === 'function') window.xoaTatCaAnh();
        if (typeof window.xoaTatCaFile === 'function') window.xoaTatCaFile();
    }

    /* ============================================================
       GỬI TIN NHẮN — CHAT CHÍNH
       ============================================================ */
    async function guiTinNhanChinh() {
        if (dangGui) return;

        const noiDung = oNhap.value.trim();
        const coAnh = window.DANH_SACH_ANH && window.DANH_SACH_ANH.length > 0;
        const coFile = window.DANH_SACH_FILE && window.DANH_SACH_FILE.length > 0;

        if (!noiDung && !coAnh && !coFile) return;

        dangGui = true;
        nutGui.disabled = true;

        // Đếm số tin nhắn người dùng TRƯỚC KHI thêm tin mới
        const soTinNguoiTruoc = demTinNhanNguoiTrongChatChinh();
        const laTinDauTien = (soTinNguoiTruoc === 0);

        // Lưu tên file trước khi preview bị xóa
        const tenFilesTruoc = coFile
            ? window.DANH_SACH_FILE.map(function (f) { return f.file.name; })
            : [];

        // URL blob của ảnh local (để hiển thị ngay)
        const urlsAnhLocal = coAnh
            ? window.DANH_SACH_ANH.map(function (a) { return a.url; })
            : [];

        // Hiển thị tin nhắn người (có ảnh/file)
        let tinNhanEl;
        if (coAnh || coFile) {
            tinNhanEl = taoTinNhanCoDinhKem(noiDung, 'nguoi', urlsAnhLocal, [], tenFilesTruoc);
            danhSach.appendChild(tinNhanEl);
            cuonXuongCuoi(khungChat);
        } else {
            themTinNhanNguoi(noiDung);
        }

        oNhap.value = '';
        tuDongGian(oNhap);

        // Cập nhật tên chat nhanh
        if (laTinDauTien) {
            const idChat = window.__ID_CHAT_NHANH_HIEN_TAI;
            const tenChat = noiDung || 'Chat có đính kèm';
            if (idChat && typeof window.capNhatTenChatNhanh === 'function') {
                window.capNhatTenChatNhanh(idChat, tenChat);
            }
        }

        hienDangTraLoi(danhSach, 'tin-nhan-dang-tra-loi');

        try {
            // Upload ảnh/file
            const dinhKem = await uploadDinhKem();

            // Gửi tin nhắn
            const phanHoi = await fetch('/api/gui-tin-nhan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    noi_dung: noiDung,
                    urls_anh: dinhKem.urls_anh,
                    urls_file: dinhKem.urls_file,
                }),
            });
            const duLieu = await phanHoi.json();
            xoaDangTraLoi('tin-nhan-dang-tra-loi');

            if (duLieu && duLieu.thanh_cong && duLieu.tra_loi) {
                themTinNhanRong(duLieu.tra_loi);
                xoaHetPreview();
            } else if (duLieu && duLieu.loi) {
                themTinNhanHeThong('⚠️ ' + duLieu.loi);
            } else {
                themTinNhanHeThong('⚠️ Không nhận được phản hồi.');
            }
        } catch (e) {
            xoaDangTraLoi('tin-nhan-dang-tra-loi');
            themTinNhanHeThong('⚠️ Lỗi kết nối: ' + e.message);
        } finally {
            dangGui = false;
            nutGui.disabled = false;
            oNhap.focus();
        }
    }

    /* ============================================================
       GỬI TIN NHẮN — CHAT TRONG DỰ ÁN
       ============================================================ */
    async function guiTinNhanDuAn() {
        if (dangGuiDuAn) return;

        const noiDung = oNhapDuAn.value.trim();
        if (!noiDung) return;

        const idDuAn = window.__ID_DU_AN_DANG_CHAT;
        const idTroChuyen = window.__ID_TRO_CHUYEN_DANG_CHAT;

        if (!idDuAn || !idTroChuyen) {
            alert('Chưa chọn trò chuyện.');
            return;
        }

        dangGuiDuAn = true;
        nutGuiDuAn.disabled = true;

        danhSachDuAn.appendChild(taoTinNhan(noiDung, 'nguoi'));
        cuonXuongCuoi(khungChatDuAn);

        oNhapDuAn.value = '';
        tuDongGian(oNhapDuAn);

        // Lưu tin nhắn khách vào localStorage
        const laKhachHienTai = window.__LA_KHACH === true || !document.getElementById('ten-nguoi-dung');
        if (laKhachHienTai && typeof window.luuTinNhanKhach === 'function') {
            window.luuTinNhanKhach(idDuAn, idTroChuyen, 'nguoi', noiDung);
        }

        hienDangTraLoi(danhSachDuAn, 'tin-nhan-dang-tra-loi-du-an');

        try {
            const phanHoi = await fetch('/api/gui-tin-nhan-du-an', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    noi_dung: noiDung,
                    id_du_an: idDuAn,
                    id_tro_chuyen: idTroChuyen,
                }),
            });
            const duLieu = await phanHoi.json();
            xoaDangTraLoi('tin-nhan-dang-tra-loi-du-an');

            let traLoi = '';
            if (duLieu && duLieu.thanh_cong && duLieu.tra_loi) {
                traLoi = duLieu.tra_loi;
            } else if (duLieu && duLieu.loi) {
                traLoi = '⚠️ ' + duLieu.loi;
            } else {
                traLoi = '⚠️ Không nhận được phản hồi.';
            }

            danhSachDuAn.appendChild(taoTinNhan(traLoi, 'rong'));
            cuonXuongCuoi(khungChatDuAn);

            if (laKhachHienTai && typeof window.luuTinNhanKhach === 'function') {
                window.luuTinNhanKhach(idDuAn, idTroChuyen, 'rong', traLoi);
            }
        } catch (e) {
            xoaDangTraLoi('tin-nhan-dang-tra-loi-du-an');
            const loi = '⚠️ Lỗi kết nối: ' + e.message;
            danhSachDuAn.appendChild(taoTinNhan(loi, 'he-thong'));
            cuonXuongCuoi(khungChatDuAn);
        } finally {
            dangGuiDuAn = false;
            nutGuiDuAn.disabled = false;
            oNhapDuAn.focus();
        }
    }

    /* ============================================================
       GẮN SỰ KIỆN
       ============================================================ */
    if (oNhap) {
        oNhap.addEventListener('input', function () { tuDongGian(oNhap); });
        oNhap.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                guiTinNhanChinh();
            }
        });
    }
    if (nutGui) {
        nutGui.addEventListener('click', function (e) {
            e.preventDefault();
            guiTinNhanChinh();
        });
    }

    if (oNhapDuAn) {
        oNhapDuAn.addEventListener('input', function () { tuDongGian(oNhapDuAn); });
        oNhapDuAn.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                guiTinNhanDuAn();
            }
        });
    }
    if (nutGuiDuAn) {
        nutGuiDuAn.addEventListener('click', function (e) {
            e.preventDefault();
            guiTinNhanDuAn();
        });
    }

    /* ============================================================
       XUẤT RA TOÀN CỤC
       ============================================================ */
    window.themTinNhanRong = themTinNhanRong;
    window.themTinNhanNguoi = themTinNhanNguoi;
    window.themTinNhanHeThong = themTinNhanHeThong;
    window.cuonXuongCuoi = cuonXuongCuoi;
    window.guiTinNhanDuAn = guiTinNhanDuAn;

    /* ============================================================
       LỜI CHÀO
       ============================================================ */
    if (danhSach && !danhSach.children.length) {
        themTinNhanRong('Nói điều ước đi 🌕🐉');
    }

})();
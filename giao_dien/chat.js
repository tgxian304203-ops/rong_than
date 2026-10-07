/* ============================================================
   chat.js - Gửi/nhận tin nhắn (chat chính + chat trong dự án)
   ------------------------------------------------------------
   ĐÃ SỬA:
     - Upload ảnh + file trước khi gửi tin nhắn.
     - Gửi kèm urls_anh và urls_file trong body API.
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
        div.textContent = noiDung;
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
       LOCALSTORAGE CHO KHÁCH
       ============================================================ */
    function docLS(khoa) {
        try {
            const raw = localStorage.getItem(khoa);
            if (!raw) return [];
            const ds = JSON.parse(raw);
            return Array.isArray(ds) ? ds : [];
        } catch (e) { return []; }
    }

    function ghiLS(khoa, ds) {
        try { localStorage.setItem(khoa, JSON.stringify(ds || [])); } catch (e) {}
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
       Trả về { urls_anh: [...], urls_file: [...] }
       ============================================================ */
    async function uploadDinhKem() {
        let urls_anh = [];
        let urls_file = [];

        try {
            if (typeof window.uploadTatCaAnh === 'function' &&
                window.DANH_SACH_ANH && window.DANH_SACH_ANH.length > 0) {
                urls_anh = await window.uploadTatCaAnh();
            }
        } catch (e) {
            console.error('Lỗi upload ảnh:', e);
        }

        try {
            if (typeof window.uploadTatCaFile === 'function' &&
                window.DANH_SACH_FILE && window.DANH_SACH_FILE.length > 0) {
                urls_file = await window.uploadTatCaFile();
            }
        } catch (e) {
            console.error('Lỗi upload file:', e);
        }

        return { urls_anh: urls_anh, urls_file: urls_file };
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

        // Hiển thị tin nhắn người (kèm ghi chú nếu có ảnh/file)
        let hienThi = noiDung;
        if (coAnh || coFile) {
            const phan = [];
            if (coAnh) phan.push(`${window.DANH_SACH_ANH.length} ảnh`);
            if (coFile) phan.push(`${window.DANH_SACH_FILE.length} file`);
            hienThi = (noiDung ? noiDung + '\n' : '') + '📎 ' + phan.join(', ');
        }
        themTinNhanNguoi(hienThi || '📎 (đính kèm)');
        oNhap.value = '';
        tuDongGian(oNhap);

        // Cập nhật tên chat nhanh nếu là tin đầu tiên
        if (laTinDauTien) {
            const idChat = window.__ID_CHAT_NHANH_HIEN_TAI;
            const tenChat = noiDung || 'Chat có đính kèm';
            if (idChat && typeof window.capNhatTenChatNhanh === 'function') {
                window.capNhatTenChatNhanh(idChat, tenChat);
            }
        }

        hienDangTraLoi(danhSach, 'tin-nhan-dang-tra-loi');

        try {
            // Upload ảnh/file trước
            const dinhKem = await uploadDinhKem();

            // Gửi tin nhắn kèm URL đính kèm
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
/* ============================================================
   chat.js - Gửi/nhận tin nhắn (chat chính + chat trong dự án)
   ------------------------------------------------------------
   ĐÃ SỬA: Thêm xử lý gửi tin trong trò chuyện dự án.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM — CHAT CHÍNH
       ------------------------------------------------------------ */
    const oNhap = document.getElementById('o-nhap');
    const nutGui = document.getElementById('nut-gui');
    const danhSach = document.getElementById('danh-sach-tin-nhan');
    const khungChat = document.getElementById('khung-chat');

    /* ------------------------------------------------------------
       THAM CHIẾU DOM — CHAT TRONG DỰ ÁN
       ------------------------------------------------------------ */
    const oNhapDuAn = document.getElementById('o-nhap-du-an');
    const nutGuiDuAn = document.getElementById('nut-gui-du-an');
    const danhSachDuAn = document.getElementById('danh-sach-tin-nhan-du-an');
    const khungChatDuAn = document.getElementById('khung-chat-du-an');

    /* ------------------------------------------------------------
       HẰNG SỐ
       ------------------------------------------------------------ */
    const CHIEU_CAO_DONG = 24;
    const SO_DONG_TOI_DA = 6;
    const CHIEU_CAO_TOI_DA = CHIEU_CAO_DONG * SO_DONG_TOI_DA;

    const KHOA_LS_TIN_NHAN = 'rong_than_tin_nhan_khach';

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

        if (loai === 'rong' && typeof window.hienThiCodeTrongTinNhan === 'function') {
            window.hienThiCodeTrongTinNhan(div, noiDung);
        } else {
            div.textContent = noiDung;
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
        cuonXuongCuoi(khung.parentElement || khung);
        return div;
    }

    function xoaDangTraLoi(idThem) {
        const el = document.getElementById(idThem);
        if (el) el.remove();
    }

    /* ============================================================
       XỬ LÝ LOCALSTORAGE CHO KHÁCH (chat trong dự án)
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

    function luuTinNhanKhach(idDuAn, idTroChuyen, vaiTro, noiDung) {
        const ds = docLS(KHOA_LS_TIN_NHAN);
        ds.push({
            id_du_an: idDuAn,
            id_tro_chuyen: idTroChuyen,
            vai_tro: vaiTro,
            noi_dung: noiDung,
            thoi_gian: Date.now(),
        });
        ghiLS(KHOA_LS_TIN_NHAN, ds);
    }

    /* ============================================================
       GỬI TIN NHẮN — CHAT CHÍNH
       ============================================================ */
    async function guiTinNhanChinh() {
        if (dangGui) return;
        const noiDung = oNhap.value.trim();
        if (!noiDung) return;

        dangGui = true;
        nutGui.disabled = true;

        themTinNhanNguoi(noiDung);
        oNhap.value = '';
        tuDongGian(oNhap);

        hienDangTraLoi(danhSach, 'tin-nhan-dang-tra-loi');

        try {
            const phanHoi = await fetch('/api/gui-tin-nhan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ noi_dung: noiDung }),
            });
            const duLieu = await phanHoi.json();
            xoaDangTraLoi('tin-nhan-dang-tra-loi');

            if (duLieu && duLieu.thanh_cong && duLieu.tra_loi) {
                themTinNhanRong(duLieu.tra_loi);
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

        // Thêm tin nhắn người dùng
        danhSachDuAn.appendChild(taoTinNhan(noiDung, 'nguoi'));
        cuonXuongCuoi(khungChatDuAn);

        oNhapDuAn.value = '';
        tuDongGian(oNhapDuAn);

        // Lưu localStorage nếu là khách
        const laKhachHienTai = window.__LA_KHACH === true;
        if (laKhachHienTai) {
            luuTinNhanKhach(idDuAn, idTroChuyen, 'nguoi', noiDung);
        }

        // Hiện đang trả lời
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

            // Lưu localStorage nếu là khách
            if (laKhachHienTai) {
                luuTinNhanKhach(idDuAn, idTroChuyen, 'rong', traLoi);
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
       GẮN SỰ KIỆN — CHAT CHÍNH
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

    /* ============================================================
       GẮN SỰ KIỆN — CHAT TRONG DỰ ÁN
       ============================================================ */
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
       LỜI CHÀO KHI MỞ TRANG
       ============================================================ */
    if (danhSach && !danhSach.children.length) {
        themTinNhanRong('Nói điều ước đi 🌕🐉');
    }

})();
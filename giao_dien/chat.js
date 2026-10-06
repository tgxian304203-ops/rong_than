/* ============================================================
   chat.js - Gửi/nhận tin nhắn trong giao diện Rồng Thần
   ------------------------------------------------------------
   Nhiệm vụ:
     - Lắng nghe sự kiện gõ và gửi tin.
     - Tự động giãn ô input theo nội dung (tối đa 6 dòng).
     - Enter xuống dòng, KHÔNG gửi. Chỉ gửi khi bấm nút [➤].
     - Khi gửi: tự động upload ảnh + file trước (nếu có).
     - Gửi tin lên server qua POST /api/gui-tin-nhan.
     - Hiển thị tin nhắn Rồng Thần / Người dùng / Hệ thống.
     - Tự động cuộn xuống tin nhắn mới nhất.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const oNhap = document.getElementById('o-nhap');
    const nutGui = document.getElementById('nut-gui');
    const danhSach = document.getElementById('danh-sach-tin-nhan');
    const khungChat = document.getElementById('khung-chat');

    if (!oNhap || !nutGui || !danhSach) {
        return;
    }

    /* ------------------------------------------------------------
       HẰNG SỐ
       ------------------------------------------------------------ */
    const CHIEU_CAO_DONG = 24;
    const SO_DONG_TOI_DA = 6;
    const CHIEU_CAO_TOI_DA = CHIEU_CAO_DONG * SO_DONG_TOI_DA;

    let dangGui = false;

    /* ------------------------------------------------------------
       TIỆN ÍCH
       ------------------------------------------------------------ */
    function cuonXuongCuoi() {
        if (khungChat) {
            khungChat.scrollTop = khungChat.scrollHeight;
        }
    }

    function tuDongGian() {
        oNhap.style.height = 'auto';
        const cao = Math.min(oNhap.scrollHeight, CHIEU_CAO_TOI_DA);
        oNhap.style.height = cao + 'px';
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

        danhSach.appendChild(div);
        cuonXuongCuoi();
        return div;
    }

    function themTinNhanRong(noiDung) {
        return taoTinNhan(noiDung, 'rong');
    }

    function themTinNhanNguoi(noiDung) {
        return taoTinNhan(noiDung, 'nguoi');
    }

    function themTinNhanHeThong(noiDung) {
        return taoTinNhan(noiDung, 'he-thong');
    }

    /* ------------------------------------------------------------
       HIỂN THỊ "ĐANG TRẢ LỜI..."
       ------------------------------------------------------------ */
    function hienDangTraLoi() {
        const div = document.createElement('div');
        div.classList.add('tin-nhan', 'tin-nhan-rong');
        div.id = 'tin-nhan-dang-tra-loi';
        div.textContent = '🌕🐉 Đang suy nghĩ...';
        danhSach.appendChild(div);
        cuonXuongCuoi();
        return div;
    }

    function xoaDangTraLoi() {
        const el = document.getElementById('tin-nhan-dang-tra-loi');
        if (el) el.remove();
    }

    /* ------------------------------------------------------------
       GỬI TIN NHẮN (đã tích hợp upload ảnh + file)
       ------------------------------------------------------------ */
    async function guiTinNhan() {
        if (dangGui) return;

        const noiDung = oNhap.value.trim();

        // Có ảnh hoặc file chờ gửi không?
        const coAnh  = window.DANH_SACH_ANH  && window.DANH_SACH_ANH.length > 0;
        const coFile = window.DANH_SACH_FILE && window.DANH_SACH_FILE.length > 0;

        // Không có gì để gửi
        if (!noiDung && !coAnh && !coFile) return;

        dangGui = true;
        nutGui.disabled = true;

        // Hiển thị tin nhắn người dùng (nếu có chữ)
        if (noiDung) {
            themTinNhanNguoi(noiDung);
        }

        // Xóa ô nhập
        oNhap.value = '';
        oNhap.style.height = 'auto';
        tuDongGian();

        // Upload ảnh + file (nếu có)
        let urlAnh = [];
        let urlFile = [];

        try {
            if (coAnh && typeof window.uploadTatCaAnh === 'function') {
                urlAnh = await window.uploadTatCaAnh();
            }
            if (coFile && typeof window.uploadTatCaFile === 'function') {
                urlFile = await window.uploadTatCaFile();
            }
        } catch (e) {
            console.error('Lỗi upload:', e);
        }

        // Xóa preview sau khi upload
        if (typeof window.xoaTatCaAnh === 'function') window.xoaTatCaAnh();
        if (typeof window.xoaTatCaFile === 'function') window.xoaTatCaFile();

        // Hiện đang trả lời
        hienDangTraLoi();

        try {
            const phanHoi = await fetch('/api/gui-tin-nhan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    noi_dung: noiDung,
                    anh: urlAnh,
                    file: urlFile,
                }),
            });

            const duLieu = await phanHoi.json();

            xoaDangTraLoi();

            if (duLieu && duLieu.thanh_cong && duLieu.tra_loi) {
                themTinNhanRong(duLieu.tra_loi);

                if (duLieu.code && typeof window.hienThiKhungCode === 'function') {
                    window.hienThiKhungCode(duLieu.code, duLieu.ngon_ngu || 'python');
                }
            } else if (duLieu && duLieu.loi) {
                themTinNhanHeThong('⚠️ ' + duLieu.loi);
            } else {
                themTinNhanHeThong('⚠️ Không nhận được phản hồi từ Rồng Thần.');
            }
        } catch (e) {
            xoaDangTraLoi();
            themTinNhanHeThong('⚠️ Lỗi kết nối: ' + e.message);
        } finally {
            dangGui = false;
            nutGui.disabled = false;
            oNhap.focus();
        }
    }

    /* ------------------------------------------------------------
       SỰ KIỆN
       ------------------------------------------------------------ */
    oNhap.addEventListener('input', tuDongGian);

    oNhap.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            guiTinNhan();
        }
    });

    nutGui.addEventListener('click', function (e) {
        e.preventDefault();
        guiTinNhan();
    });

    /* ------------------------------------------------------------
       XUẤT HÀM RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.themTinNhanRong = themTinNhanRong;
    window.themTinNhanNguoi = themTinNhanNguoi;
    window.themTinNhanHeThong = themTinNhanHeThong;
    window.cuonXuongCuoi = cuonXuongCuoi;

    /* ------------------------------------------------------------
       KHỞI ĐỘNG: HIỂN THỊ LỜI CHÀO
       ------------------------------------------------------------ */
    function hienLoiChao() {
        themTinNhanRong('Nói điều ước đi 🌕🐉');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            tuDongGian();
            if (!danhSach.children.length) hienLoiChao();
        });
    } else {
        tuDongGian();
        if (!danhSach.children.length) hienLoiChao();
    }

})();
/* ============================================================
   chat.js - Gửi/nhận tin nhắn (chat chính + chat trong dự án)
   ------------------------------------------------------------
   ĐÃ SỬA (CÁCH 3):
     - Bỏ client-side sandbox (không dùng Pyodide/LiveCodes).
     - Backend chạy code → trả ket_qua_chay (stdout, stderr).
     - Client chỉ hiển thị code + kết quả từ backend.
     - Giữ nguyên các hàm render tin nhắn.
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

    function layDuoi(tenFile) {
        if (!tenFile || tenFile.indexOf('.') < 0) return '';
        return tenFile.split('.').pop().toLowerCase();
    }

    function layTenFileTuUrl(url) {
        if (!url) return 'file';
        const phan = url.split('/');
        return phan[phan.length - 1] || 'file';
    }

    function layIconFileChat(tenFile) {
        const duoi = layDuoi(tenFile);
        const svgMo = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">';
        const svgDong = '</svg>';

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
            '<line x1="16" y1="13" x2="8" y2="13"/>' +
            '<line x1="16" y1="17" x2="8" y2="17"/>' +
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

    function taoKhungDinhKem(urlsAnh, urlsFile, tenFiles) {
        const khung = document.createElement('div');
        khung.classList.add('tin-nhan-dinh-kem');

        if (urlsAnh && urlsAnh.length > 0) {
            urlsAnh.forEach(function (url) {
                const img = document.createElement('img');
                img.classList.add('tin-nhan-anh');
                img.src = url;
                img.alt = 'Ảnh đính kèm';
                img.addEventListener('click', function () {
                    if (typeof window.moModalAnh === 'function') {
                        window.moModalAnh(url);
                    } else {
                        window.open(url, '_blank');
                    }
                });
                khung.appendChild(img);
            });
        }

        if (urlsFile && urlsFile.length > 0) {
            urlsFile.forEach(function (url, i) {
                const tenFile = (tenFiles && tenFiles[i]) ? tenFiles[i] : layTenFileTuUrl(url);

                const khoiFile = document.createElement('div');
                khoiFile.classList.add('tin-nhan-file');
                khoiFile.innerHTML = layIconFileChat(tenFile) +
                    '<span class="ten-file-chat">' + tenFile + '</span>';

                khoiFile.addEventListener('click', function () {
                    window.open(url, '_blank');
                });

                khung.appendChild(khoiFile);
            });
        }

        return khung;
    }

    function taoTinNhanCoDinhKem(noiDung, loai, urlsAnh, urlsFile, tenFiles) {
        const div = taoTinNhan(noiDung, loai);
        if ((urlsAnh && urlsAnh.length > 0) || (urlsFile && urlsFile.length > 0)) {
            div.appendChild(taoKhungDinhKem(urlsAnh, urlsFile, tenFiles));
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
       LẤY URL ĐÃ UPLOAD SẴN
       ============================================================ */
    function layDinhKemDaUpload() {
        let urls_anh = [];
        let urls_file = [];
        let ten_files = [];

        if (typeof window.layUrlsAnhDaUpload === 'function') {
            urls_anh = window.layUrlsAnhDaUpload();
        }
        if (typeof window.layUrlsFileDaUpload === 'function') {
            urls_file = window.layUrlsFileDaUpload();
        }
        if (typeof window.layTenFilesDaUpload === 'function') {
            ten_files = window.layTenFilesDaUpload();
        }

        return { urls_anh: urls_anh, urls_file: urls_file, ten_files: ten_files };
    }

    function xoaHetPreview() {
        if (typeof window.xoaTatCaAnh === 'function') window.xoaTatCaAnh();
        if (typeof window.xoaTatCaFile === 'function') window.xoaTatCaFile();
    }

    /* ============================================================
       HIỂN THỊ KẾT QUẢ CODE TỪ BACKEND (CÁCH 3)
       ============================================================ */
    function hienThiKetQuaChay(ketQuaChay) {
        if (!ketQuaChay) return;

        // Nếu backend đã tự sửa → thông báo
        if (ketQuaChay.da_sua) {
            let thongBao = '🔧 Đã tự sửa lỗi';
            if (ketQuaChay.so_lan_sua) {
                thongBao += ` (${ketQuaChay.so_lan_sua} lần)`;
            }
            if (ketQuaChay.cach_sua) {
                thongBao += `:\n${ketQuaChay.cach_sua}`;
            }
            if (ketQuaChay.nguon_sua) {
                thongBao += `\n(nguồn: ${ketQuaChay.nguon_sua})`;
            }
            themTinNhanHeThong(thongBao);
        }

        // Hiển thị stdout (kết quả)
        if (ketQuaChay.stdout) {
            const dong = document.createElement('div');
            dong.classList.add('tin-nhan', 'tin-nhan-rong');
            const pre = document.createElement('pre');
            pre.classList.add('sandbox-ket-qua');
            pre.textContent = ketQuaChay.stdout;
            dong.appendChild(pre);
            danhSach.appendChild(dong);
            cuonXuongCuoi(khungChat);
        }

        // Hiển thị stderr (lỗi)
        if (ketQuaChay.stderr && !ketQuaChay.da_sua) {
            const dong = document.createElement('div');
            dong.classList.add('tin-nhan', 'tin-nhan-he-thong');
            const pre = document.createElement('pre');
            pre.classList.add('sandbox-loi');
            pre.textContent = '⚠️ Lỗi:\n' + ketQuaChay.stderr;
            dong.appendChild(pre);
            danhSach.appendChild(dong);
            cuonXuongCuoi(khungChat);
        } else if (ketQuaChay.stderr && ketQuaChay.da_sua) {
            // Đã sửa nhưng vẫn còn lỗi
            if (!ketQuaChay.thanh_cong) {
                const dong = document.createElement('div');
                dong.classList.add('tin-nhan', 'tin-nhan-he-thong');
                const pre = document.createElement('pre');
                pre.classList.add('sandbox-loi');
                pre.textContent = '⚠️ Vẫn còn lỗi sau khi sửa:\n' + ketQuaChay.stderr;
                dong.appendChild(pre);
                danhSach.appendChild(dong);
                cuonXuongCuoi(khungChat);
            }
        }
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

        if (typeof window.dangUploadAnh === 'function' && window.dangUploadAnh()) return;
        if (typeof window.dangUploadFile === 'function' && window.dangUploadFile()) return;
        if (typeof window.coLoiUpload === 'function' && window.coLoiUpload()) return;

        dangGui = true;
        nutGui.disabled = true;

        const soTinNguoiTruoc = demTinNhanNguoiTrongChatChinh();
        const laTinDauTien = (soTinNguoiTruoc === 0);

        const dinhKem = layDinhKemDaUpload();

        let tinNhanEl;
        if (coAnh || coFile) {
            tinNhanEl = taoTinNhanCoDinhKem(
                noiDung, 'nguoi', dinhKem.urls_anh, dinhKem.urls_file, dinhKem.ten_files
            );
        } else {
            tinNhanEl = taoTinNhan(noiDung, 'nguoi');
        }
        danhSach.appendChild(tinNhanEl);
        cuonXuongCuoi(khungChat);

        xoaHetPreview();

        oNhap.value = '';
        tuDongGian(oNhap);

        const idChat = window.__ID_CHAT_NHANH_HIEN_TAI || '';

        if (laTinDauTien && idChat) {
            const tenChat = noiDung || 'Chat có đính kèm';
            if (typeof window.capNhatTenChatNhanh === 'function') {
                window.capNhatTenChatNhanh(idChat, tenChat);
            }
        }

        hienDangTraLoi(danhSach, 'tin-nhan-dang-tra-loi');

        try {
            const phanHoi = await fetch('/api/gui-tin-nhan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    noi_dung: noiDung,
                    urls_anh: dinhKem.urls_anh,
                    urls_file: dinhKem.urls_file,
                    id_chat: idChat,
                }),
            });
            const duLieu = await phanHoi.json();
            xoaDangTraLoi('tin-nhan-dang-tra-loi');

            if (duLieu && duLieu.thanh_cong && duLieu.tra_loi) {
                themTinNhanRong(duLieu.tra_loi);

                // CÁCH 3: Nếu backend đã chạy code → hiển thị kết quả
                if (duLieu.ket_qua_chay) {
                    hienThiKetQuaChay(duLieu.ket_qua_chay);
                }
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
            if (typeof window.capNhatTrangThaiNutGui === 'function') {
                window.capNhatTrangThaiNutGui();
            } else {
                nutGui.disabled = false;
            }
            oNhap.focus();
        }
    }

    /* ============================================================
       GỬI TIN NHẮN — CHAT TRONG DỰ ÁN
       ============================================================ */
    async function guiTinNhanDuAn() {
        if (dangGuiDuAn) return;

        const noiDung = oNhapDuAn.value.trim();
        const coAnh = window.DANH_SACH_ANH && window.DANH_SACH_ANH.length > 0;
        const coFile = window.DANH_SACH_FILE && window.DANH_SACH_FILE.length > 0;

        if (!noiDung && !coAnh && !coFile) return;

        if (typeof window.dangUploadAnh === 'function' && window.dangUploadAnh()) return;
        if (typeof window.dangUploadFile === 'function' && window.dangUploadFile()) return;
        if (typeof window.coLoiUpload === 'function' && window.coLoiUpload()) return;

        const idDuAn = window.__ID_DU_AN_DANG_CHAT;
        const idTroChuyen = window.__ID_TRO_CHUYEN_DANG_CHAT;

        if (!idDuAn || !idTroChuyen) {
            alert('Chưa chọn trò chuyện.');
            return;
        }

        dangGuiDuAn = true;
        nutGuiDuAn.disabled = true;

        const laKhachHienTai = window.__LA_KHACH === true || !document.getElementById('ten-nguoi-dung');

        const dinhKem = layDinhKemDaUpload();

        let tinNhanEl;
        if (coAnh || coFile) {
            tinNhanEl = taoTinNhanCoDinhKem(
                noiDung, 'nguoi', dinhKem.urls_anh, dinhKem.urls_file, dinhKem.ten_files
            );
        } else {
            tinNhanEl = taoTinNhan(noiDung, 'nguoi');
        }
        danhSachDuAn.appendChild(tinNhanEl);
        cuonXuongCuoi(khungChatDuAn);

        xoaHetPreview();

        oNhapDuAn.value = '';
        tuDongGian(oNhapDuAn);

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
                    urls_anh: dinhKem.urls_anh,
                    urls_file: dinhKem.urls_file,
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
            if (typeof window.capNhatTrangThaiNutGui === 'function') {
                window.capNhatTrangThaiNutGui();
            } else {
                nutGuiDuAn.disabled = false;
            }
            oNhapDuAn.focus();
        }
    }

    /* ============================================================
       RENDER TIN NHẮN CŨ — CHAT NHANH
       ============================================================ */
    function renderTinNhanChatNhanh(danh_sach) {
        if (!danhSach) return;
        danhSach.innerHTML = '';

        (danh_sach || []).forEach(function (tin) {
            const vaiTro = (tin.vai_tro === 'rong_than' || tin.vai_tro === 'rong') ? 'rong' : 'nguoi';
            const noiDung = tin.noi_dung || '';
            const urlsAnh = tin.urls_anh || tin.anh || [];
            const urlsFile = tin.urls_file || tin.file || [];

            if (urlsAnh.length > 0 || urlsFile.length > 0) {
                danhSach.appendChild(
                    taoTinNhanCoDinhKem(noiDung, vaiTro, urlsAnh, urlsFile)
                );
            } else {
                danhSach.appendChild(taoTinNhan(noiDung, vaiTro));
            }
        });

        cuonXuongCuoi(khungChat);
    }

    /* ============================================================
       RENDER TIN NHẮN CŨ — DỰ ÁN
       ============================================================ */
    function renderTinNhanCu(danh_sach) {
        if (!danhSachDuAn) return;
        danhSachDuAn.innerHTML = '';

        (danh_sach || []).forEach(function (tin) {
            const vaiTro = (tin.vai_tro === 'rong' || tin.vai_tro === 'rong_than') ? 'rong' : 'nguoi';
            const noiDung = tin.noi_dung || '';
            const urlsAnh = tin.urls_anh || [];
            const urlsFile = tin.urls_file || [];

            if (urlsAnh.length > 0 || urlsFile.length > 0) {
                danhSachDuAn.appendChild(
                    taoTinNhanCoDinhKem(noiDung, vaiTro, urlsAnh, urlsFile)
                );
            } else {
                danhSachDuAn.appendChild(taoTinNhan(noiDung, vaiTro));
            }
        });

        cuonXuongCuoi(khungChatDuAn);
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
    window.renderTinNhanCu = renderTinNhanCu;
    window.renderTinNhanChatNhanh = renderTinNhanChatNhanh;
    window.hienThiKetQuaChay = hienThiKetQuaChay;

    /* ============================================================
       LỜI CHÀO
       ============================================================ */
    if (danhSach && !danhSach.children.length) {
        themTinNhanRong('Nói điều ước đi 🌕🐉');
    }

})();
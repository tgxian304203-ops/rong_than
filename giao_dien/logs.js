/* ============================================================
   logs.js - Hiển thị + lọc + quản lý logs Rồng Thần
   ------------------------------------------------------------
   ĐÃ SỬA:
     - FIX 1: Dùng thoi_gian_hien_thi (giờ VN từ server).
     - FIX 2: Đảo ngược thứ tự log — MỚI NHẤT ở DƯỚI CÙNG.
     - FIX 3: Không tự động nhảy xuống khi user đang cuộn lên xem log cũ.
              Chỉ nhảy xuống khi có log MỚI hoặc user đang ở gần cuối.
   ============================================================ */

(function () {
    'use strict';

    const trangLogs  = document.getElementById('trang-logs');
    const danhSach   = document.getElementById('danh-sach-log');
    const nutXoaLog  = document.getElementById('nut-xoa-log');
    const nutTaiLog  = document.getElementById('nut-tai-log');
    const cacNutLoc  = document.querySelectorAll('.nut-loc');

    if (!trangLogs || !danhSach) {
        return;
    }

    const THOI_GIAN_CAP_NHAT = 3 * 1000;
    const SO_LOG_TOI_DA = 500;
    const KHOANG_CACH_DAY = 80; // px — coi như đang ở cuối

    let idHen = null;
    let boLocHienTai = 'tat-ca';

    // FIX 3: Lưu id log cuối cùng để phát hiện log mới
    let idLogCuoiCung = null;

    const NHAN_LOAI = {
        'dai-nao':  'Đại não',
        'tieu-nao': 'Tiểu não',
        'tra-web':  'Tra web',
        'sandbox':  'Sandbox',
        'loi':      'Lỗi',
    };

    function chuanHoaLoai(loai) {
        if (!loai) return 'khac';
        const t = String(loai).toLowerCase().trim();

        if (t.includes('đại') || t.includes('dai'))     return 'dai-nao';
        if (t.includes('tiểu') || t.includes('tieu'))   return 'tieu-nao';
        if (t.includes('tra') || t.includes('web'))     return 'tra-web';
        if (t.includes('sandbox') || t.includes('box')) return 'sandbox';
        if (t.includes('lỗi') || t.includes('loi') || t.includes('error')) return 'loi';

        return 'khac';
    }

    function dinhDangThoiGian(log) {
        if (log.thoi_gian_hien_thi) {
            return log.thoi_gian_hien_thi;
        }

        const tg = log.thoi_gian;
        if (!tg) return '';

        try {
            const d = new Date(tg * 1000);
            const gio  = String(d.getHours()).padStart(2, '0');
            const phut = String(d.getMinutes()).padStart(2, '0');
            const giay = String(d.getSeconds()).padStart(2, '0');
            return gio + ':' + phut + ':' + giay;
        } catch (e) {
            return String(tg);
        }
    }

    function taoDongLog(log) {
        const dong = document.createElement('div');
        dong.classList.add('log-dong');

        const tg = document.createElement('span');
        tg.classList.add('log-thoi-gian');
        tg.textContent = dinhDangThoiGian(log);
        dong.appendChild(tg);

        const loai = document.createElement('span');
        const loaiChuan = chuanHoaLoai(log.loai);
        loai.classList.add('log-loai');
        if (loaiChuan !== 'khac') {
            loai.classList.add(loaiChuan);
        }
        loai.textContent = NHAN_LOAI[loaiChuan] || (log.loai || 'Khác');
        dong.appendChild(loai);

        const noiDung = document.createElement('span');
        noiDung.classList.add('log-noi-dung');
        noiDung.textContent = log.noi_dung || '';
        dong.appendChild(noiDung);

        return dong;
    }

    /* FIX 3: Kiểm tra user đang ở gần cuối không */
    function dangOGanCuoi() {
        const cachDay = danhSach.scrollHeight - danhSach.scrollTop - danhSach.clientHeight;
        return cachDay < KHOANG_CACH_DAY;
    }

    /* FIX 3: Lấy id của log cuối cùng (mới nhất trong danh sách gốc) */
    function layIdLogMoiNhat(danhSachLog) {
        if (!Array.isArray(danhSachLog) || danhSachLog.length === 0) {
            return null;
        }
        // Mảng gốc từ server: log mới nhất ở đầu (index 0) nếu server trả DESC
        // Hoặc ở cuối nếu server trả ASC
        // → Lấy id của log có thoi_gian lớn nhất
        let idMax = null;
        let tgMax = -1;
        danhSachLog.forEach(function (log) {
            const tg = log.thoi_gian || 0;
            if (tg > tgMax) {
                tgMax = tg;
                idMax = log.id || String(tg);
            }
        });
        return idMax;
    }

    /* FIX 3: Vẽ danh sách — có logic giữ vị trí cuộn */
    function veDanhSach(danhSachLog) {
        const dangOGanCuoiTruoc = dangOGanCuoi();

        // Phát hiện có log mới không
        const idMoiNhat = layIdLogMoiNhat(danhSachLog);
        const coLogMoi = (idLogCuoiCung !== null && idMoiNhat !== null && idMoiNhat !== idLogCuoiCung);

        danhSach.innerHTML = '';

        if (!Array.isArray(danhSachLog) || danhSachLog.length === 0) {
            idLogCuoiCung = null;
            return;
        }

        const cat = danhSachLog.slice(-SO_LOG_TOI_DA);
        const daoNguoc = cat.slice().reverse();

        daoNguoc.forEach(function (log) {
            danhSach.appendChild(taoDongLog(log));
        });

        // Cập nhật id log cuối cùng
        idLogCuoiCung = idMoiNhat;

        // Chỉ tự nhảy xuống khi:
        // 1. User đang ở gần cuối TRƯỚC KHI vẽ lại, HOẶC
        // 2. Có log mới xuất hiện (và user đang ở gần cuối)
        if (dangOGanCuoiTruoc || (coLogMoi && dangOGanCuoiTruoc)) {
            danhSach.scrollTop = danhSach.scrollHeight;
        }
        // Còn nếu user đang cuộn lên xem log cũ → giữ nguyên vị trí cuộn
    }

    function locLog(danhSachLog, loai) {
        if (loai === 'tat-ca') return danhSachLog;
        return danhSachLog.filter(function (log) {
            return chuanHoaLoai(log.loai) === loai;
        });
    }

    async function taiLog() {
        try {
            const url = boLocHienTai === 'tat-ca'
                ? '/api/logs'
                : '/api/logs/loc?loai=' + encodeURIComponent(boLocHienTai);

            const phanHoi = await fetch(url);
            const duLieu = await phanHoi.json();

            let ds = [];
            if (duLieu && duLieu.thanh_cong && Array.isArray(duLieu.danh_sach)) {
                ds = duLieu.danh_sach;
            }

            if (boLocHienTai !== 'tat-ca' && duLieu && !duLieu.da_loc) {
                ds = locLog(ds, boLocHienTai);
            }

            veDanhSach(ds);
        } catch (e) {
            // Im lặng
        }
    }

    function batDauCapNhat() {
        if (idHen) return;
        idHen = setInterval(function () {
            if (trangLogs.classList.contains('dang-mo')) {
                taiLog();
            }
        }, THOI_GIAN_CAP_NHAT);
    }

    function dungCapNhat() {
        if (idHen) {
            clearInterval(idHen);
            idHen = null;
        }
    }

    function ganSuKienLoc() {
        cacNutLoc.forEach(function (nut) {
            nut.addEventListener('click', function () {
                cacNutLoc.forEach(function (n) {
                    n.classList.remove('dang-chon');
                });
                nut.classList.add('dang-chon');

                boLocHienTai = nut.dataset.loc || 'tat-ca';
                idLogCuoiCung = null; // reset khi đổi bộ lọc
                taiLog();
            });
        });
    }

    async function xoaLog() {
        const hamDongY = async function () {
            try {
                const phanHoi = await fetch('/api/logs/xoa', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                });
                const duLieu = await phanHoi.json();
                if (duLieu && duLieu.thanh_cong) {
                    idLogCuoiCung = null;
                    veDanhSach([]);
                } else {
                    alert((duLieu && duLieu.loi) || 'Không xóa được log.');
                }
            } catch (e) {
                alert('Lỗi kết nối: ' + e.message);
            }
        };

        if (typeof window.moXacNhanXoa === 'function') {
            window.moXacNhanXoa('Bạn có chắc muốn xóa toàn bộ log?', hamDongY);
        } else {
            if (confirm('Bạn có chắc muốn xóa toàn bộ log?')) hamDongY();
        }
    }

    function taiLogVeMay() {
        const cacDong = danhSach.querySelectorAll('.log-dong');
        if (!cacDong.length) {
            alert('Chưa có log để tải.');
            return;
        }

        let noiDung = '';
        cacDong.forEach(function (dong) {
            noiDung += dong.textContent + '\n';
        });

        const blob = new Blob([noiDung], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const thoiGian = new Date().toISOString().replace(/[:.]/g, '-');
        a.href = url;
        a.download = 'rong-than-logs-' + thoiGian + '.log';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    if (nutXoaLog) nutXoaLog.addEventListener('click', xoaLog);
    if (nutTaiLog) nutTaiLog.addEventListener('click', taiLogVeMay);

    const observer = new MutationObserver(function () {
        if (trangLogs.classList.contains('dang-mo')) {
            // Khi mở trang lần đầu → reset để nhảy xuống cuối
            idLogCuoiCung = null;
            taiLog();
        }
    });
    observer.observe(trangLogs, { attributes: true, attributeFilter: ['class'] });

    function khoiDong() {
        ganSuKienLoc();
        batDauCapNhat();
        if (trangLogs.classList.contains('dang-mo')) {
            taiLog();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    window.taiLog = taiLog;
    window.veDanhSachLog = veDanhSach;
    window.dungCapNhatLog = dungCapNhat;

})();
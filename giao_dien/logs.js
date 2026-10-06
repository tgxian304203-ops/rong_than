/* ============================================================
   logs.js - Hiển thị + lọc + quản lý logs Rồng Thần
   ------------------------------------------------------------
   Nhiệm vụ:
     - Tải logs từ GET /api/logs.
     - Vẽ từng dòng log: thời gian + loại + nội dung.
     - Bộ lọc theo loại: Tất cả / Đại não / Tiểu não / Tra web
       / Sandbox / Lỗi.
     - Cập nhật realtime mỗi 3 giây (chỉ khi trang Logs đang mở).
     - Nút Xóa log: xóa toàn bộ log trên server.
     - Nút Tải log: tải file .log về máy.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const trangLogs  = document.getElementById('trang-logs');
    const danhSach   = document.getElementById('danh-sach-log');
    const nutXoaLog  = document.getElementById('nut-xoa-log');
    const nutTaiLog  = document.getElementById('nut-tai-log');
    const cacNutLoc  = document.querySelectorAll('.nut-loc');

    if (!trangLogs || !danhSach) {
        return; // Thiếu DOM thì thoát.
    }

    /* ------------------------------------------------------------
       HẰNG SỐ
       ------------------------------------------------------------ */
    const THOI_GIAN_CAP_NHAT = 3 * 1000; // 3 giây
    const SO_LOG_TOI_DA = 500;           // tránh lag nếu log quá dài

    let idHen = null;
    let boLocHienTai = 'tat-ca';

    /* ------------------------------------------------------------
       BẢNG NHÃN LOẠI LOG
       ------------------------------------------------------------ */
    const NHAN_LOAI = {
        'dai-nao':  'Đại não',
        'tieu-nao': 'Tiểu não',
        'tra-web':  'Tra web',
        'sandbox':  'Sandbox',
        'loi':      'Lỗi',
    };

    /* ------------------------------------------------------------
       HÀM CHUẨN HÓA LOẠI LOG
       Nhận nhiều dạng khác nhau từ server, đưa về 1 trong 5 loại.
       ------------------------------------------------------------ */
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

    /* ------------------------------------------------------------
       TẠO 1 DÒNG LOG
       ------------------------------------------------------------ */
    function taoDongLog(log) {
        const dong = document.createElement('div');
        dong.classList.add('log-dong');

        const tg = document.createElement('span');
        tg.classList.add('log-thoi-gian');
        tg.textContent = log.thoi_gian || '';
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

    /* ------------------------------------------------------------
       VẼ DANH SÁCH LOG
       ------------------------------------------------------------ */
    function veDanhSach(danhSachLog) {
        danhSach.innerHTML = '';

        if (!Array.isArray(danhSachLog) || danhSachLog.length === 0) {
            return; // CSS tự hiển thị "Chưa có log"
        }

        // Giới hạn số log để tránh lag
        const cat = danhSachLog.slice(-SO_LOG_TOI_DA);

        cat.forEach(function (log) {
            danhSach.appendChild(taoDongLog(log));
        });

        // Cuộn xuống cuối
        danhSach.scrollTop = danhSach.scrollHeight;
    }

    /* ------------------------------------------------------------
       LỌC LOG THEO LOẠI
       ------------------------------------------------------------ */
    function locLog(danhSachLog, loai) {
        if (loai === 'tat-ca') return danhSachLog;
        return danhSachLog.filter(function (log) {
            return chuanHoaLoai(log.loai) === loai;
        });
    }

    /* ------------------------------------------------------------
       TẢI LOG TỪ SERVER
       ------------------------------------------------------------ */
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

            // Nếu server trả full log (không lọc), tự lọc ở client
            if (boLocHienTai !== 'tat-ca' && duLieu && !duLieu.da_loc) {
                ds = locLog(ds, boLocHienTai);
            }

            veDanhSach(ds);
        } catch (e) {
            // Im lặng — không spam lỗi mỗi 3s
        }
    }

    /* ------------------------------------------------------------
       CẬP NHẬT ĐỊNH KỲ (chỉ khi trang Logs đang mở)
       ------------------------------------------------------------ */
    function batDauCapNhat() {
        if (idHen) return; // đã chạy rồi
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

    /* ------------------------------------------------------------
       GẮN SỰ KIỆN LỌC
       ------------------------------------------------------------ */
    function ganSuKienLoc() {
        cacNutLoc.forEach(function (nut) {
            nut.addEventListener('click', function () {
                cacNutLoc.forEach(function (n) {
                    n.classList.remove('dang-chon');
                });
                nut.classList.add('dang-chon');

                boLocHienTai = nut.dataset.loc || 'tat-ca';
                taiLog();
            });
        });
    }

    /* ------------------------------------------------------------
       XÓA LOG
       ------------------------------------------------------------ */
    async function xoaLog() {
        const hamDongY = async function () {
            try {
                const phanHoi = await fetch('/api/logs/xoa', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                });
                const duLieu = await phanHoi.json();
                if (duLieu && duLieu.thanh_cong) {
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

    /* ------------------------------------------------------------
       TẢI LOG VỀ MÁY
       ------------------------------------------------------------ */
    function taiLogVeMay() {
        // Lấy nội dung log hiện tại từ DOM, ghi ra file .log
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

    /* ------------------------------------------------------------
       SỰ KIỆN
       ------------------------------------------------------------ */
    if (nutXoaLog) nutXoaLog.addEventListener('click', xoaLog);
    if (nutTaiLog) nutTaiLog.addEventListener('click', taiLogVeMay);

    // Khi trang Logs mở → tải log ngay
    // Dùng MutationObserver theo dõi class "dang-mo"
    const observer = new MutationObserver(function () {
        if (trangLogs.classList.contains('dang-mo')) {
            taiLog();
        }
    });
    observer.observe(trangLogs, { attributes: true, attributeFilter: ['class'] });

    /* ------------------------------------------------------------
       KHỞI ĐỘNG
       ------------------------------------------------------------ */
    function khoiDong() {
        ganSuKienLoc();
        batDauCapNhat();
        // Nếu trang Logs đang mở sẵn thì tải luôn
        if (trangLogs.classList.contains('dang-mo')) {
            taiLog();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.taiLog = taiLog;
    window.veDanhSachLog = veDanhSach;
    window.dungCapNhatLog = dungCapNhat;

})();
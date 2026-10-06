/* ============================================================
   hien_thi_cay.js - Vẽ cây quyết định Rồng Thần
   ------------------------------------------------------------
   Nhiệm vụ:
     - Tải cây từ GET /api/cay.
     - Vẽ cây dạng phân cấp có thể mở/đóng từng nhánh.
     - Mỗi node hiển thị: tên + score + số lần thử.
     - Nút "Tải lại cây" làm mới dữ liệu.
     - Hiển thị thông tin tổng quan ở đầu trang.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const trangCay = document.getElementById('trang-cay');
    const khungCay = document.getElementById('khung-cay');
    const thongTin = document.getElementById('cay-thong-tin');
    const nutTaiLai = document.getElementById('nut-tai-lai-cay');

    if (!trangCay || !khungCay) {
        return; // Thiếu DOM thì thoát.
    }

    /* ------------------------------------------------------------
       ĐẾM SỐ NODE TRONG CÂY
       ------------------------------------------------------------ */
    function demNode(node) {
        if (!node || typeof node !== 'object') return 0;
        let dem = 1;
        const con = node.nhanh_con || node.con || node.children || [];
        if (Array.isArray(con)) {
            con.forEach(function (n) {
                dem += demNode(n);
            });
        }
        return dem;
    }

    /* ------------------------------------------------------------
       TẠO 1 NODE CÂY (đệ quy)
       ------------------------------------------------------------ */
    function taoNode(node) {
        const boc = document.createElement('div');
        boc.classList.add('cay-node');

        const hang = document.createElement('div');
        hang.classList.add('cay-node-hang');

        // Nút mở/đóng
        const nutToggle = document.createElement('span');
        nutToggle.classList.add('cay-toggle');

        const con = node.nhanh_con || node.con || node.children || [];
        const coCon = Array.isArray(con) && con.length > 0;

        if (coCon) {
            nutToggle.textContent = '▶';
        } else {
            nutToggle.textContent = '•';
            nutToggle.classList.add('trong');
        }
        hang.appendChild(nutToggle);

        // Tên node
        const ten = document.createElement('span');
        ten.classList.add('cay-node-ten');
        ten.textContent = node.ten || node.id || 'Không tên';
        hang.appendChild(ten);

        // Thông tin node: score + số lần thử
        const info = document.createElement('span');
        info.classList.add('cay-node-info');

        if (typeof node.score === 'number') {
            const elScore = document.createElement('span');
            elScore.classList.add('cay-info-muc', 'cay-info-score');
            elScore.textContent = '★ ' + node.score.toFixed(2);
            info.appendChild(elScore);
        }

        const soLanThu = node.so_lan_thu;
        if (typeof soLanThu === 'number') {
            const elThu = document.createElement('span');
            elThu.classList.add('cay-info-muc');
            elThu.textContent = 'Thử: ' + soLanThu;
            info.appendChild(elThu);
        }

        hang.appendChild(info);

        boc.appendChild(hang);

        // Nhánh con
        if (coCon) {
            const khungCon = document.createElement('div');
            khungCon.classList.add('cay-con');

            con.forEach(function (n) {
                khungCon.appendChild(taoNode(n));
            });

            boc.appendChild(khungCon);

            // Sự kiện mở/đóng
            hang.addEventListener('click', function () {
                const dangMo = khungCon.classList.toggle('mo');
                nutToggle.classList.toggle('mo', dangMo);
            });
        }

        return boc;
    }

    /* ------------------------------------------------------------
       VẼ CÂY
       ------------------------------------------------------------ */
    function veCay(duLieuCay) {
        khungCay.innerHTML = '';

        if (!duLieuCay) {
            if (thongTin) thongTin.innerHTML = 'Chưa có dữ liệu cây.';
            return;
        }

        // Nếu cây là 1 object có nhiều nhánh con
        const goc = duLieuCay.root || duLieuCay.goc || duLieuCay;
        const conGoc = goc.nhanh_con || goc.con || goc.children || [];

        // Thông tin tổng quan
        if (thongTin) {
            const tong = demNode(goc);
            thongTin.innerHTML =
                'Tổng số node: <strong>' + tong + '</strong> · ' +
                'Nhánh gốc: <strong>' + (Array.isArray(conGoc) ? conGoc.length : 0) + '</strong>';
        }

        // Vẽ node gốc
        khungCay.appendChild(taoNode(goc));

        // Mở sẵn node gốc cấp 1
        const cacNodeCap1 = khungCay.querySelectorAll('.cay-node > .cay-con');
        cacNodeCap1.forEach(function (el, i) {
            if (i === 0) {
                el.classList.add('mo');
                const toggle = el.parentElement.querySelector('.cay-toggle');
                if (toggle) toggle.classList.add('mo');
            }
        });
    }

    /* ------------------------------------------------------------
       TẢI CÂY TỪ SERVER
       ------------------------------------------------------------ */
    async function taiCay() {
        if (thongTin) thongTin.textContent = 'Đang tải cây...';

        try {
            const phanHoi = await fetch('/api/cay');
            const duLieu = await phanHoi.json();

            if (duLieu && duLieu.thanh_cong && duLieu.cay) {
                veCay(duLieu.cay);
            } else if (duLieu && duLieu.cay) {
                // Trường hợp server trả về cay trực tiếp
                veCay(duLieu.cay);
            } else {
                veCay(null);
                if (thongTin) {
                    thongTin.textContent = (duLieu && duLieu.loi) || 'Không tải được cây.';
                }
            }
        } catch (e) {
            veCay(null);
            if (thongTin) {
                thongTin.textContent = 'Lỗi kết nối: ' + e.message;
            }
        }
    }

    /* ------------------------------------------------------------
       SỰ KIỆN
       ------------------------------------------------------------ */
    if (nutTaiLai) {
        nutTaiLai.addEventListener('click', function (e) {
            e.preventDefault();
            taiCay();
        });
    }

    // Tự tải khi mở trang cây (dùng MutationObserver)
    const observer = new MutationObserver(function () {
        if (trangCay.classList.contains('dang-mo')) {
            taiCay();
        }
    });
    observer.observe(trangCay, { attributes: true, attributeFilter: ['class'] });

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.taiCay = taiCay;
    window.veCay = veCay;

})();
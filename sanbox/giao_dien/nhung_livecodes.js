/* ============================================================
   nhung_livecodes.js - Nhúng LiveCodes SDK vào Sandbox Rồng Thần
   ------------------------------------------------------------
   Nhiệm vụ:
     - Tải LiveCodes SDK từ CDN.
     - Tạo playground trong #livecodes-container.
     - Gắn sự kiện cho 4 nút: Chạy, Dừng, Copy, Xóa.
     - Gắn sự kiện cho 6 nút ngôn ngữ.
     - Gắn sự kiện cho 4 nút chế độ xem.
     - Bắt console output qua watch('console').
     - Bắt test results qua watch('tests').
     - Hiển thị trạng thái.
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       HẰNG SỐ
       ------------------------------------------------------------ */
    const LIVECODES_CDN = 'https://cdn.jsdelivr.net/npm/livecodes@0.14.1';
    const TIMEOUT_MS = 10000;

    /* ------------------------------------------------------------
       BIẾN TOÀN CỤC
       ------------------------------------------------------------ */
    let playground = null;
    let ngonNguHienTai = 'html';
    let cheDoHienTai = 'result';
    let dangChay = false;

    /* ------------------------------------------------------------
       THAM CHIẾU DOM
       ------------------------------------------------------------ */
    const container = document.getElementById('livecodes-container');
    const nutChay = document.getElementById('nut-chay');
    const nutDung = document.getElementById('nut-dung');
    const nutCopy = document.getElementById('nut-copy');
    const nutXoa = document.getElementById('nut-xoa');
    const trangThaiSandbox = document.getElementById('trang-thai-sandbox');
    const stdoutEl = document.getElementById('sandbox-stdout');
    const stderrEl = document.getElementById('sandbox-stderr');
    const testsEl = document.getElementById('sandbox-tests');
    const infoNgonNgu = document.getElementById('info-ngon-ngu');
    const infoDong = document.getElementById('info-dong');
    const infoKyTu = document.getElementById('info-ky-tu');
    const trangThaiNgan = document.getElementById('trang-thai-ngan');
    const trangThaiChu = document.getElementById('trang-thai-chu');
    const thoiGianChay = document.getElementById('thoi-gian-chay');

    /* ------------------------------------------------------------
       CẬP NHẬT TRẠNG THÁI
       ------------------------------------------------------------ */
    function capNhatTrangThai(chu, mau) {
        if (trangThaiSandbox) trangThaiSandbox.textContent = chu;
        if (trangThaiChu) trangThaiChu.textContent = chu;
        if (trangThaiNgan) {
            trangThaiNgan.style.color = mau || '#9ca3af';
        }
    }

    function capNhatThongTin(code) {
        if (!code) return;
        const soDong = code.split('\n').length;
        const soKyTu = code.length;
        if (infoDong) infoDong.textContent = soDong + ' dòng';
        if (infoKyTu) infoKyTu.textContent = soKyTu + ' ký tự';
    }

    /* ------------------------------------------------------------
       KHỞI TẠO PLAYGROUND
       ------------------------------------------------------------ */
    async function khoiTaoPlayground() {
        if (!container) {
            console.error('Không tìm thấy container.');
            return;
        }

        capNhatTrangThai('Đang tải LiveCodes...', '#facc15');

        try {
            // Import SDK từ CDN
            const { createPlayground } = await import(LIVECODES_CDN);

            // Tạo playground
            playground = await createPlayground(container, {
                config: {
                    markup: {
                        language: 'html',
                        content: '<h1>Hello Rồng Thần 🐉</h1>\n<p>Chạy code HTML/CSS/JS tại đây.</p>',
                    },
                },
                view: 'result',
                loading: 'eager',
            });

            // Gắn watcher console
            playground.watch('console', ({ method, args }) => {
                const dong = '[' + method + '] ' + args.join(' ');
                if (method === 'error' || method === 'warn') {
                    if (stderrEl) stderrEl.textContent += dong + '\n';
                } else {
                    if (stdoutEl) stdoutEl.textContent += dong + '\n';
                }
            });

            // Gắn watcher tests
            playground.watch('tests', ({ results, error }) => {
                if (error) {
                    if (testsEl) testsEl.textContent = 'Lỗi: ' + error + '\n';
                    return;
                }
                if (results && testsEl) {
                    testsEl.textContent = results.map(function (r) {
                        return '[' + r.status + '] ' + r.testPath.join(' > ');
                    }).join('\n');
                }
            });

            capNhatTrangThai('Sẵn sàng.', '#4ade80');
        } catch (e) {
            capNhatTrangThai('Lỗi tải SDK: ' + e.message, '#ef4444');
            if (container) container.textContent = 'Lỗi tải LiveCodes: ' + e.message;
        }
    }

    /* ------------------------------------------------------------
       CHẠY CODE
       ------------------------------------------------------------ */
    async function chayCode() {
        if (!playground || dangChay) return;

        dangChay = true;
        capNhatTrangThai('Đang chạy...', '#facc15');
        if (stdoutEl) stdoutEl.textContent = '';
        if (stderrEl) stderrEl.textContent = '';
        if (testsEl) testsEl.textContent = '';

        const batDau = Date.now();

        try {
            await playground.run();
            const thoiGian = ((Date.now() - batDau) / 1000).toFixed(2);
            if (thoiGianChay) thoiGianChay.textContent = thoiGian + 's';
            capNhatTrangThai('Chạy xong (' + thoiGian + 's).', '#4ade80');
        } catch (e) {
            capNhatTrangThai('Lỗi: ' + e.message, '#ef4444');
        } finally {
            dangChay = false;
        }
    }

    /* ------------------------------------------------------------
       DỪNG
       ------------------------------------------------------------ */
    function dungCode() {
        if (!playground) return;
        capNhatTrangThai('Đã dừng.', '#9ca3af');
    }

    /* ------------------------------------------------------------
       COPY CODE
       ------------------------------------------------------------ */
    async function copyCode() {
        if (!playground) return;

        try {
            const code = await playground.getCode();
            let noiDung = '';

            if (code.markup && code.markup.content) {
                noiDung += code.markup.content;
            }
            if (code.style && code.style.content) {
                noiDung += '\n<style>\n' + code.style.content + '\n</style>';
            }
            if (code.script && code.script.content) {
                noiDung += '\n<script>\n' + code.script.content + '\n</script>';
            }

            if (navigator.clipboard) {
                await navigator.clipboard.writeText(noiDung);
                capNhatTrangThai('Đã copy code.', '#4ade80');
            }
        } catch (e) {
            capNhatTrangThai('Lỗi copy: ' + e.message, '#ef4444');
        }
    }

    /* ------------------------------------------------------------
       XÓA OUTPUT
       ------------------------------------------------------------ */
    function xoaOutput() {
        if (stdoutEl) stdoutEl.textContent = '';
        if (stderrEl) stderrEl.textContent = '';
        if (testsEl) testsEl.textContent = '';
        capNhatTrangThai('Đã xóa output.', '#9ca3af');
    }

    /* ------------------------------------------------------------
       ĐỔI NGÔN NGỮ
       ------------------------------------------------------------ */
    async function doiNgonNgu(ngonNgu) {
        if (!playground) return;

        ngonNguHienTai = ngonNgu;
        if (infoNgonNgu) infoNgonNgu.textContent = ngonNgu.toUpperCase();

        const configMoi = {
            markup: { language: 'html', content: '' },
            style: { language: 'css', content: '' },
            script: { language: 'javascript', content: '' },
        };

        if (ngonNgu === 'html') {
            configMoi.markup.content = '<h1>Hello Rồng Thần 🐉</h1>';
        } else if (ngonNgu === 'python') {
            configMoi.script.language = 'python';
            configMoi.script.content = 'print("Hello Rồng Thần 🐉")';
            configMoi.markup.content = '';
        } else if (ngonNgu === 'javascript') {
            configMoi.script.language = 'javascript';
            configMoi.script.content = 'console.log("Hello Rồng Thần 🐉");';
            configMoi.markup.content = '';
        } else if (ngonNgu === 'typescript') {
            configMoi.script.language = 'typescript';
            configMoi.script.content = 'const x: string = "Hello Rồng Thần 🐉";\nconsole.log(x);';
            configMoi.markup.content = '';
        } else if (ngonNgu === 'css') {
            configMoi.style.content = 'body { color: #4ade80; }';
            configMoi.markup.content = '<h1>Hello Rồng Thần 🐉</h1>';
        } else if (ngonNgu === 'markdown') {
            configMoi.markup.language = 'markdown';
            configMoi.markup.content = '# Hello Rồng Thần 🐉\n\nSandbox đa ngôn ngữ.';
        }

        try {
            await playground.setConfig(configMoi);
            capNhatTrangThai('Đã đổi sang ' + ngonNgu.toUpperCase(), '#4ade80');
        } catch (e) {
            capNhatTrangThai('Lỗi đổi ngôn ngữ: ' + e.message, '#ef4444');
        }
    }

    /* ------------------------------------------------------------
       ĐỔI CHẾ ĐỘ XEM
       ------------------------------------------------------------ */
    async function doiCheDo(cheDo) {
        if (!playground) return;

        cheDoHienTai = cheDo;

        try {
            if (cheDo === 'result') {
                await playground.show('result');
            } else if (cheDo === 'editor') {
                await playground.show('editor');
            } else if (cheDo === 'console') {
                await playground.show('console');
            } else if (cheDo === 'tests') {
                await playground.show('tests');
            }
            capNhatTrangThai('Chế độ: ' + cheDo, '#4ade80');
        } catch (e) {
            capNhatTrangThai('Lỗi đổi chế độ: ' + e.message, '#ef4444');
        }
    }

    /* ------------------------------------------------------------
       GẮN SỰ KIỆN
       ------------------------------------------------------------ */
    function ganSuKien() {
        // Nút chính
        if (nutChay) nutChay.addEventListener('click', chayCode);
        if (nutDung) nutDung.addEventListener('click', dungCode);
        if (nutCopy) nutCopy.addEventListener('click', copyCode);
        if (nutXoa) nutXoa.addEventListener('click', xoaOutput);

        // Nút ngôn ngữ
        document.querySelectorAll('.nut-ngon-ngu').forEach(function (nut) {
            nut.addEventListener('click', function () {
                document.querySelectorAll('.nut-ngon-ngu').forEach(function (n) {
                    n.classList.remove('dang-chon');
                });
                nut.classList.add('dang-chon');
                doiNgonNgu(nut.dataset.ngonNgu);
            });
        });

        // Nút chế độ
        document.querySelectorAll('.nut-che-do').forEach(function (nut) {
            nut.addEventListener('click', function () {
                document.querySelectorAll('.nut-che-do').forEach(function (n) {
                    n.classList.remove('dang-chon');
                });
                nut.classList.add('dang-chon');
                doiCheDo(nut.dataset.cheDo);
            });
        });
    }

    /* ------------------------------------------------------------
       KHỞI ĐỘNG
       ------------------------------------------------------------ */
    function khoiDong() {
        ganSuKien();
        khoiTaoPlayground();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', khoiDong);
    } else {
        khoiDong();
    }

    /* ------------------------------------------------------------
       XUẤT RA TOÀN CỤC
       ------------------------------------------------------------ */
    window.sandboxChay = chayCode;
    window.sandboxDung = dungCode;
    window.sandboxCopy = copyCode;
    window.sandboxXoa = xoaOutput;
    window.sandboxDoiNgonNgu = doiNgonNgu;
    window.sandboxDoiCheDo = doiCheDo;
})();
# HƯỚNG DẪN CÀI ĐẶT RỒNG THẦN

## 1. Môi trường làm việc

- Spck điện thoại (bản free) để soạn code.
- Đẩy lên GitHub.
- Deploy lên Render.

**Lưu ý quan trọng:**

- Spck Free chỉ là trình soạn thảo, KHÔNG chạy được Python.
- Spck Free chỉ có JS Console để test snippet nhỏ, không có Terminal.
- Render mới là nơi chạy Python thật.
- Không test được code trên Spck, phải đẩy lên Render để test.

---

## 2. Bước 1 — Tạo file trên Spck

1. Mở Spck Editor trên điện thoại.
2. Tạo từng file theo sơ đồ thư mục.
3. Viết code Python cho từng file.
4. Viết code HTML/JS cho từng file.
5. Lưu lại.

Spck Free có Git tích hợp, dùng để đẩy code lên GitHub.

---

## 3. Bước 2 — Đẩy GitHub

1. Trong Spck, dùng tính năng Git.
2. Kết nối với tài khoản GitHub.
3. Clone repo hoặc tạo repo mới.
4. Commit code.
5. Push lên repository GitHub.

---

## 4. Bước 3 — Deploy Render

1. Vào Render Dashboard.
2. Tạo Web Service mới.
3. Kết nối với repository GitHub vừa push.
4. Chọn runtime Python.
5. Build Command: `pip install -r yeu_cau.txt`
6. Start Command: theo Procfile.
7. Chọn gói Free.
8. Bấm Deploy.

Sau khi deploy xong, Render cung cấp 1 URL công khai (VD: `https://rong-than.onrender.com`).

---

## 5. Bước 4 — Kiểm tra và fix lỗi

Sau khi deploy:

1. Mở link Render.
2. Kiểm tra giao diện có hiển thị không.
3. Kiểm tra chat có hoạt động không.
4. Kiểm tra dán URI kho có lưu không.
5. Kiểm tra dán key có lưu không.
6. Kiểm tra quota có cập nhật không.
7. Kiểm tra sandbox có chạy code không.
8. Kiểm tra logs có ghi không.

Nếu có lỗi:

1. Xem log Render (tab Logs).
2. Sửa lỗi trong Spck.
3. Push lại GitHub.
4. Render tự động deploy lại.

---

## 6. Đăng ký API Key model

### Groq

1. Vào https://console.groq.com/keys
2. Đăng nhập bằng Google hoặc GitHub.
3. Bấm Create API Key.
4. Đặt tên cho key.
5. Copy key (bắt đầu bằng `gsk_`).
6. Dán vào giao diện Rồng Thần.

### OpenRouter

1. Vào https://openrouter.ai
2. Đăng ký tài khoản free.
3. Vào mục API Keys.
4. Tạo key mới.
5. Copy key.
6. Dán vào giao diện Rồng Thần.

### Gemini

1. Vào https://ai.dev
2. Đăng nhập bằng Gmail.
3. Bấm Get API Key.
4. Tạo key mới.
5. Copy key.
6. Dán vào giao diện Rồng Thần.

---

## 7. Đăng ký API Key tra web

### SERPJET

1. Vào trang chủ SERPJET.
2. Đăng ký tài khoản free.
3. Lấy API key.
4. Dán vào giao diện Rồng Thần.

### Tavily

1. Vào trang chủ Tavily.
2. Đăng ký tài khoản free.
3. Lấy API key.
4. Dán vào giao diện Rồng Thần.

### Bright Data

1. Vào trang chủ Bright Data.
2. Đăng ký tài khoản free.
3. Lấy API key.
4. Dán vào giao diện Rồng Thần.

---

## 8. Đăng ký MongoDB Atlas

Rồng Thần cần 2 kho MongoDB:

- Kho 1: `rong_than_user` — dữ liệu người dùng.
- Kho 2: `rong_than_cay` — cây quyết định.

### Tạo kho 1

1. Vào https://www.mongodb.com/cloud/atlas
2. Đăng ký tài khoản free.
3. Tạo cluster M0 (free).
4. Tạo database `rong_than_user`.
5. Tạo user database.
6. Lấy URI kết nối.
7. Dán vào giao diện Rồng Thần (ô URI kho 1).

### Tạo kho 2

1. Đăng ký tài khoản MongoDB Atlas **thứ 2** (dùng email khác).
2. Tạo cluster M0 (free).
3. Tạo database `rong_than_cay`.
4. Tạo user database.
5. Lấy URI kết nối.
6. Dán vào giao diện Rồng Thần (ô URI kho 2).

---

## 9. UptimeRobot — Giữ Render không ngủ

Render Free sẽ ngủ sau 15 phút không có request. Khi ngủ, lần request tiếp theo phải chờ khoảng 1 phút để khởi động lại.

Để tránh, dùng UptimeRobot ping định kỳ.

1. Vào https://uptimerobot.com
2. Đăng ký tài khoản free.
3. Bấm Add New Monitor.
4. Monitor Type: HTTP(s).
5. Friendly Name: Rồng Thần.
6. URL: link Render của Rồng Thần.
7. Monitoring Interval: 5 phút.
8. Bấm Create Monitor.

UptimeRobot sẽ ping link mỗi 5 phút, giữ Render không ngủ.

---

## 10. Keep-alive MongoDB

MongoDB Atlas Free sẽ tạm dừng sau 60 ngày không có truy cập. Để tránh:

- Ping cả 2 kho mỗi 12 giờ.
- Dùng UptimeRobot hoặc cron job.

---

## 11. Backup

Gói free MongoDB không có backup tự động.

Tự chạy `mongodump` định kỳ:

```

mongodump --uri="mongodb+srv://..." --out=./backup

```

Backup kho 2 quan trọng hơn kho 1.

---

## 12. Các lỗi thường gặp

### Lỗi 1: Render báo "Build failed"

- Kiểm tra `yeu_cau.txt` có đủ thư viện không.
- Kiểm tra `Procfile` đúng cú pháp không.

### Lỗi 2: App chạy nhưng chat không hoạt động

- Kiểm tra URI kho 1 và kho 2 đã dán chưa.
- Kiểm tra kết nối MongoDB.

### Lỗi 3: Tiểu não không sinh được node

- Kiểm tra key model đã dán chưa.
- Kiểm tra quota còn không.
- Kiểm tra log Render xem lỗi gì.

### Lỗi 4: Tra web không hoạt động

- Kiểm tra key tra web đã dán chưa.
- Kiểm tra quota 3 API.

### Lỗi 5: Sandbox không chạy code

- Kiểm tra LiveCodes đã nhúng đúng chưa.
- Kiểm tra kết nối mạng (LiveCodes cần mạng để tải).

### Lỗi 6: Ảnh/file upload không lưu

- Kiểm tra GridFS có bật không.
- Kiểm tra dung lượng kho 1 còn không.

---

## 13. Checklist trước khi deploy

- [ ] Đã tạo đủ 6 file gốc.
- [ ] Đã tạo đủ 25 file Đại não.
- [ ] Đã tạo đủ 15 file Tiểu não.
- [ ] Đã tạo đủ 11 file Tra web.
- [ ] Đã tạo đủ 8 file Sandbox.
- [ ] Đã tạo đủ 30 file Giao diện.
- [ ] Đã tạo đủ 4 file Logs.
- [ ] Đã tạo đủ 14 file Dữ liệu (bao gồm .gitkeep).
- [ ] Đã tạo đủ 10 file Kiểm thử.
- [ ] Đã tạo đủ 12 file Tài liệu.
- [ ] `yeu_cau.txt` đã liệt kê hết thư viện.
- [ ] `Procfile` đã đúng cú pháp.
- [ ] `.gitignore` đã chặn file nhạy cảm.
- [ ] `README.md` đã mô tả dự án.

---

## 14. Sau khi deploy xong

1. Mở link Render.
2. Vào menu phải.
3. Dán URI kho 1 → Run.
4. Dán URI kho 2 → Run.
5. Dán API key model (Groq, OpenRouter, Gemini) → Run.
6. Dán API key tra web (SERPJET, Tavily, Bright Data) → Run.
7. Test chat: nhập "Xin chào".
8. Test sandbox: nhập "chạy print('hello')".
9. Test tra web: nhập "giá vàng hôm nay".
10. Test tạo tài khoản: ấn Đăng ký.

Nếu tất cả hoạt động → Rồng Thần đã sẵn sàng.

---

## 15. Cập nhật code

Sau khi deploy lần đầu, mỗi lần sửa code:

1. Sửa trên Spck.
2. Commit.
3. Push GitHub.
4. Render tự động deploy lại (mất ~1-2 phút).

Không cần bấm Deploy thủ công.
```

---

Lưu.

---

✅ HOÀN TẤT TOÀN BỘ DỰ ÁN RỒNG THẦN

Đã gửi đủ:

· File gốc: 6 file ✅
· dai_nao/: 25 file ✅
· tieu_nao/: 15 file ✅
· tra_web/: 11 file ✅
· sanbox/: 8 file ✅
· giao_dien/: 30 file ✅
· logs/: 4 file ✅
· du_lieu/: 15 file (14 + 2 .gitkeep) ✅
· kiem_thu/: 11 mục ✅
· tai_lieu/: 12 file ✅

Tổng cộng: 137 file.
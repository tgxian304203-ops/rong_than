# GIAO DIỆN RỒNG THẦN

## 1. Tổng quan

Giao diện Rồng Thần gồm 7 phần chính:

1. Màn hình chat chính.
2. Menu trái.
3. Menu phải.
4. Sandbox (nằm trong chat).
5. Trang cài đặt.
6. Trang quản lý key.
7. Trang logs.

Tất cả dùng chung 1 style: nền đen, kính mờ 45%, viền bo góc tròn, auto co giãn mọi màn hình điện thoại.

---

## 2. Màn hình chat chính

- Nền: màu đen toàn bộ.
- Kích thước: auto co giãn theo màn hình.
- Viền: tất cả bo góc tròn.

### Header

- Không có thanh ngang.
- Chỉ có logo 🔥🐉 ở giữa.
- Chỉ có nút menu trái ở bên trái.
- Không có nút menu phải.
- Các logo trong chat chính là logo SVG.

### Vùng chat

- Tin nhắn Rồng Thần: bên trái, icon SVG, chữ xanh lá.
- Tin nhắn Người dùng: bên phải, chữ trắng.
- Khung chat: trong suốt 50%.
- Thông báo hệ thống: ở giữa.
- Tin nhắn chào: "Nói điều ước đi 🔥🐉", bên trái, chữ xanh lá.
- Khi Rồng Thần trả lời kèm code, phần code tách khỏi chữ.
- Code hiển thị trong khung riêng, nền tối hơn, bo góc, có nút Copy.

### Khung input

- Nút [+] đính kèm file/ảnh, nằm trong khung.
- Ô nhập văn bản, placeholder "Nhập...".
- Nút [➤] gửi tin nhắn, nằm trong khung.
- Không có mic.
- Ô input mở rộng hướng lên tối đa 6 dòng.
- Nếu chữ dài quá 6 dòng, ô input tự cuộn.
- Ô input cách bàn phím điện thoại 1mm.
- Enter trên bàn phím = xuống dòng (không gửi).

### Sơ đồ

```

┌─────────────────────────────────────────────┐
│  [☰]             🔥🐉                       │
│                                             │
│  ╭─────────────────────────╮                │
│  │ 🐉 Nói điều ước đi 🔥🐉  │                │
│  ╰─────────────────────────╯                │
│                                             │
│  ╭───────────────────────────────╮          │
│  │ 👤 Làm web bán hàng           │          │
│  ╰───────────────────────────────╯          │
│                                             │
│  ╭───────────────────────────────────────╮  │
│  │ 🐉 Đây là code HTML bạn cần:          │  │
│  ╰───────────────────────────────────────╯  │
│                                             │
│  ╭───────────────────────────────────────╮  │
│  │  HTML                         [Copy]  │  │
│  │  <html>                               │  │
│  │    <body><h1>Web bán hàng</h1></body> │  │
│  │  </html>                              │  │
│  ╰───────────────────────────────────────╯  │
├─────────────────────────────────────────────┤
│  ╭───────────────────────────────────────╮  │
│  │  [+]  Nhập...                  [➤]   │  │
│  ╰───────────────────────────────────────╯  │
│         (cách bàn phím 1mm)                 │
└─────────────────────────────────────────────┘

```

---

## 3. Menu trái

- Nền: kính trong suốt 45%.
- Bo viền, bo góc tròn.
- Auto co giãn.
- Logo SVG.

### Cấu trúc

- Header: logo 🐉, nút [←] đóng menu.
- Mục + New Chat: tạo cuộc trò chuyện mới.
- Mục Tạo dự án: tạo dự án mới, không giới hạn.
- Mục Share: chia sẻ chat/dự án.
- Mục DỰ ÁN: danh sách dự án, thanh cuộn, mỗi dự án có nút [X] xóa.
- Mục GẦN ĐÂY: lịch sử trò chuyện, thanh cuộn, mỗi chat có nút [X] xóa.
- Mục Chế độ sáng tối: đổi giao diện.
- Mục Cài đặt.
- Mục Người dùng: tùy chế độ.

### 2 chế độ ở mục Người dùng

- Chế độ tài khoản (đã đăng nhập): hiển thị tên người dùng, nút Đăng xuất.
- Chế độ khách (chưa đăng nhập): hiển thị nút Đăng ký, nút Đăng nhập.

### 2 loại trò chuyện

- Trò chuyện nhanh: tạo bằng nút + New Chat, không thuộc dự án, lưu trong GẦN ĐÂY, dùng cho chat lẻ.
- Trò chuyện dự án: tạo trong dự án, thuộc dự án, lưu trong DỰ ÁN, có ngữ cảnh riêng.

### Xác nhận xóa

Khi ấn nút [X] xóa dự án hoặc xóa chat, hiện hộp thoại xác nhận:
- Câu hỏi: "Bạn có chắc muốn xóa dự án này?"
- Nút: Xóa, Hủy.

---

## 4. Menu phải

- Nền: kính trong suốt 45%.
- Bo viền, bo góc tròn.

### Cấu trúc

- Header: nút [← BACK], logo 🥚 🐉.
- Ô dán URI kho 1 + nút Run.
- Ô dán URI kho 2 + nút Run.
- Ô dán API Key model + nút Run.
- Ô dán API Key tra web (SERPJET, Tavily, Bright Data) + nút Run.
- Mục KEY ĐÃ LƯU.
- Mục Logs.

### Mỗi key là 1 card

- Icon 🔥🐉.
- Tên provider: Groq, OpenRouter, Gemini, SERPJET, Tavily, Bright Data.
- Số thứ tự: #1, #2, #3.
- Nút [X] xóa key.
- Thanh quota.
- Phần trăm còn lại.

### Màu sắc quota

- Xanh: trên 50% (an toàn).
- Vàng: 20-50% (cảnh báo).
- Đỏ: dưới 20% (nguy hiểm).
- Đen: 0% (hết quota).

### Cách lấy quota

- Groq: đọc header x-ratelimit-remaining-requests.
- OpenRouter: gọi endpoint /api/v1/key.
- Gemini: đếm RPM/RPD.
- SERPJET: đếm lượt tìm kiếm còn lại.
- Tavily: đếm lượt tìm kiếm còn lại.
- Bright Data: đếm credit còn lại.

Cập nhật mỗi 60 giây.

---

## 5. Trang cài đặt

- Vị trí: menu trái, ấn Cài đặt mở ra.
- Nền: kính trong suốt 45%, bo viền, bo góc tròn.

### Cấu trúc

- Mục Key 🗝: quản lý key đã lưu.
- Mục Đổi mật khẩu: chỉ hiện khi đang đăng nhập.

### Sơ đồ chế độ tài khoản

```

╭─────────────────────────────────────────────╮
│  ⚙️  CÀI ĐẶT                            [←] │
│                                             │
│  ╭───────────────────────────────────────╮  │
│  │  🗝  Key                              │  │
│  ╰───────────────────────────────────────╯  │
│                                             │
│  ╭───────────────────────────────────────╮  │
│  │  🔑  Đổi mật khẩu                     │  │
│  ╰───────────────────────────────────────╯  │
╰─────────────────────────────────────────────╯

```

### Sơ đồ chế độ khách

```

╭─────────────────────────────────────────────╮
│  ⚙️  CÀI ĐẶT                            [←] │
│                                             │
│  ╭───────────────────────────────────────╮  │
│  │  🗝  Key                              │  │
│  ╰───────────────────────────────────────╯  │
╰─────────────────────────────────────────────╯

```

---

## 6. Trang quản lý key

- Vị trí: trong Cài đặt, ấn Key mở ra.
- Nền: kính trong suốt 45%, bo viền, bo góc tròn.

### Cấu trúc

- Header: nút [←] quay lại Cài đặt, tiêu đề "Quản lý Key".
- Ô dán URI kho 1.
- Ô dán URI kho 2.
- Ô dán API Key model: Groq, OpenRouter, Gemini + nút Run.
- Ô dán API Key tra web: SERPJET, Tavily, Bright Data + nút Run.
- Danh sách key đã lưu.

---

## 7. Trang logs

- Vị trí: menu phải, ấn Logs mở ra.
- Nền: kính trong suốt 45%, bo viền, bo góc tròn.
- Tiêu đề: Logs. Không có logo.

### Cấu trúc

- Header: nút [←] quay lại menu phải.
- Bộ lọc: Tất cả, Đại não, Tiểu não, Tra web, Sandbox, Lỗi.
- Danh sách log: mỗi dòng có thời gian, loại, nội dung.
- Thanh kéo trượt.
- Nút xóa log, nút tải log về máy.

---

## 8. Sandbox

Đã mô tả trong `sanbox.md`.

---

## 9. Nút bấm và chức năng

Tất cả nút phải có chức năng thật, không nút chết:

- Menu trái: New Chat, Tạo dự án, Share, DỰ ÁN (X, mở), GẦN ĐÂY (X, mở), Sáng tối, Cài đặt, Người dùng.
- Menu phải: BACK, Run (4 ô), Logs, X (key).
- Cài đặt: Key, Đổi mật khẩu.
- Key: Back, Run, X.
- Logs: Back, filter, Xóa log, Tải log.
- Chat: [+], [➤], Copy code.
- Sandbox: Chạy, Copy.

---

## 10. Các file giao diện

- index.html — Khung chính
- app.py — Flask app
- routes.py — Định nghĩa route
- chat.js — Xử lý chat
- hien_thi_cay.js — Hiển thị cây
- hien_thi_code.js — Hiển thị code
- copy_code.js — Nút copy
- tach_code_khoi_tin_nhan.js — Tách code khỏi chat
- quan_ly_key.js — Quản lý key model
- quan_ly_key_web.js — Quản lý key tra web
- quan_ly_kho.js — Quản lý URI kho
- quan_ly_menu.js — Quản lý menu
- quan_ly_cai_dat.js — Quản lý cài đặt
- logs.js — Hiển thị logs
- xu_ly_anh.js — Xử lý ảnh
- xu_ly_file.js — Xử lý file
- dang_ky.js — Đăng ký
- dang_nhap.js — Đăng nhập
- app.js — Khởi động app
- style.css — Style chung
- xac_thuc.py — Xác thực server
- session.py — Session
- phien_dang_nhap.py — Phiên đăng nhập
- luu_key.py — Lưu key
- luu_key_web.py — Lưu key web
- luu_uri_kho.py — Lưu URI kho
- doi_mat_khau.py — Đổi mật khẩu
- upload.py — Upload file/ảnh
- gui_tin_nhan.py — Gửi tin nhắn

---

## 11. Quy tắc giao diện

1. Tất cả nút phải hoạt động, không nút chết.
2. Tất cả hiển thị lấy dữ liệu thật, không hard-code.
3. Tất cả viền bo góc tròn.
4. Auto co giãn mọi màn hình điện thoại.
5. Không dùng bên thứ 3 để đăng nhập.

---

## 12. Responsive

- Mobile (< 768px): menu trái và menu phải trượt từ 2 bên, chat chiếm toàn màn hình.
- Tablet (768-1024px): chat chiếm 70%, menu trượt.
- Desktop (> 1024px): chat ở giữa, 2 menu có thể mở song song.
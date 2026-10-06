# LOGS — NHẬT KÝ HOẠT ĐỘNG

## 1. Vai trò

Logs ghi lại mọi hoạt động của Rồng Thần để debug và theo dõi.

---

## 2. Vị trí hiển thị

- Nằm trong menu phải.
- Tiêu đề: Logs.
- Không có logo.
- Nền: kính trong suốt 45%, bo viền, bo góc tròn.

---

## 3. Cấu trúc trang Logs

- Header: nút [←] quay lại menu phải, tiêu đề "Logs".
- Bộ lọc: Tất cả, Đại não, Tiểu não, Tra web, Sandbox, Lỗi.
- Danh sách log: mỗi dòng có thời gian, loại, nội dung.
- Thanh kéo trượt.
- Nút Xóa log, nút Tải log về máy.

Sơ đồ:

```

╭─────────────────────────────────────────────╮
│  [←]  LOGS                                  │
│                                             │
│  ╭──────╮ ╭──────╮ ╭──────╮ ╭──────╮       │
│  │ Tất  │ │ Đại  │ │ Tiểu │ │ Tra  │       │
│  │ cả   │ │ não  │ │ não  │ │ web  │       │
│  ╰──────╯ ╰──────╯ ╰──────╯ ╰──────╯       │
│  ╭──────╮ ╭──────╮                          │
│  │Sandbox│ │ Lỗi  │                         │
│  ╰──────╯ ╰──────╯                          │
│                                             │
│  ╭───────────────────────────────────────╮  │
│  │ 10:00:01  Đại não                     │  │
│  │ Nhận task: "Tạo web bán hàng"         │  │
│  ╰───────────────────────────────────────╯  │
│                                             │
│  ╭───────────────────────────────────────╮  │
│  │ 10:00:02  Đại não                     │  │
│  │ Phân loại: code, tạo mới, web         │  │
│  ╰───────────────────────────────────────╯  │
│                                             │
│  ╭───────────────────────────────────────╮  │
│  │ 10:00:03  Tiểu não                    │  │
│  │ Gọi Groq #1, sinh node mới            │  │
│  ╰───────────────────────────────────────╯  │
│                                             │
│  ╭───────────────────────────────────────╮  │
│  │ 10:00:04  Sandbox                     │  │
│  │ Chạy code, stdout: OK                 │  │
│  ╰───────────────────────────────────────╯  │
│                                             │
│  ╭───────────────────────────────────────╮  │
│  │ 10:00:05  Lỗi                         │  │
│  │ Groq #1 hết quota, chuyển Groq #2     │  │
│  ╰───────────────────────────────────────╯  │
│                                             │
│  ╭───────────────╮   ╭───────────────╮     │
│  │  Xóa log      │   │  Tải log      │     │
│  ╰───────────────╯   ╰───────────────╯     │
╰─────────────────────────────────────────────╯

```

---

## 4. 6 loại log

### Log Đại não

- Task nhận vào.
- Phân loại.
- Duyệt cây.
- Chọn nhánh.
- Score.
- Kết quả.

Ví dụ:
```

10:00:01  Đại não  Nhận task: "Tạo web bán hàng"
10:00:02  Đại não  Phân loại: code, tạo mới, web
10:00:03  Đại não  Duyệt cây, chọn node nut-code-web-0001 (score 0.95)

```

### Log Tiểu não

- Key dùng.
- Model gọi.
- Quota.
- Node sinh ra.

Ví dụ:
```

10:00:03  Tiểu não  Gọi Groq #1
10:00:04  Tiểu não  Sinh node nut-code-web-moi-0001

```

### Log Tra web

- API dùng.
- Query.
- Kết quả.
- Quota.

Ví dụ:
```

10:00:05  Tra web  SERPJET query "giá iPhone 15"
10:00:06  Tra web  10 kết quả, còn quota 950

```

### Log Sandbox

- Code chạy.
- stdout.
- stderr.
- Thời gian.

Ví dụ:
```

10:00:07  Sandbox  Chạy code Python, stdout: Hello
10:00:08  Sandbox  Thời gian: 0.5s

```

### Log Lỗi

- Lỗi gì.
- Ở đâu.
- Thời gian.

Ví dụ:
```

10:00:09  Lỗi  Groq #1 hết quota (429), chuyển Groq #2

```

### Log Hệ thống

- Khởi động.
- Kết nối MongoDB.
- Tải cây.
- Lưu dữ liệu.

Ví dụ:
```

10:00:00  Hệ thống  Rồng Thần khởi động
10:00:00  Hệ thống  Kết nối kho 1: OK
10:00:00  Hệ thống  Kết nối kho 2: OK
10:00:01  Hệ thống  Tải cây: 5 file, 500 node

```

---

## 5. Định dạng mỗi dòng log

```

[YYYY-MM-DD HH:MM:SS] [LOẠI] [NỘI DUNG]

```

Loại:

- `DAI_NAO`
- `TIEU_NAO`
- `TRA_WEB`
- `SANDBOX`
- `LOI`
- `HE_THONG`

---

## 6. Cập nhật realtime

Log cập nhật realtime qua WebSocket hoặc polling mỗi 2 giây.

Người dùng không cần refresh trang.

---

## 7. Bộ lọc

- Tất cả: hiển thị mọi loại log.
- Đại não: chỉ log Đại não.
- Tiểu não: chỉ log Tiểu não.
- Tra web: chỉ log Tra web.
- Sandbox: chỉ log Sandbox.
- Lỗi: chỉ log Lỗi.

Ấn 1 filter, danh sách log lọc theo.

---

## 8. Nút xóa log

Ấn Xóa log → hiện hộp thoại xác nhận.

Câu hỏi: "Bạn có chắc muốn xóa toàn bộ log?"

Nút: Xóa, Hủy.

- Ấn Xóa → xóa sạch log trong DB và UI.
- Ấn Hủy → đóng hộp thoại.

---

## 9. Nút tải log

Ấn Tải log → tải file `.log` về máy.

File có tên `nhat_ky_YYYY-MM-DD.log`.

Nội dung: toàn bộ log hiện tại.

---

## 10. Giới hạn log

- Tối đa 10.000 dòng log lưu trong DB.
- Khi vượt 10.000 dòng, log cũ nhất tự xóa.
- Log lưu trong collection riêng hoặc file `nhat_ky.log`.

---

## 11. Các file module

- `logs/ghi_log.py` — Ghi log mới
- `logs/doc_log.py` — Đọc log
- `logs/loc_log.py` — Lọc log theo loại
- `giao_dien/logs.js` — Hiển thị log phía client
- `du_lieu/nhat_ky.log` — File log local

---

## 12. Ví dụ log đầy đủ 1 task

```

10:00:00  Hệ thống  Rồng Thần khởi động
10:00:00  Hệ thống  Kết nối kho 1: OK
10:00:01  Hệ thống  Tải cây: 5 file, 500 node
10:00:02  Đại não  Nhận task: "Tạo web bán hàng"
10:00:02  Đại não  Chuẩn hóa: "tạo web bán hàng"
10:00:02  Đại não  Trích xuất 5 yếu tố: OK
10:00:03  Đại não  Phân loại: code, tạo mới, web
10:00:03  Đại não  Duyệt cây: ROOT → code → tạo mới → web
10:00:03  Đại não  Chọn node nut-code-web-0001 (score 0.95)
10:00:04  Đại não  Ghép code từ node
10:00:04  Sandbox  Chạy code HTML
10:00:05  Sandbox  Output: <html>...
10:00:05  Đại não  Trả kết quả cho người dùng
10:00:05  Đại não  Lưu node vào MongoDB
10:00:05  Hệ thống  Cập nhật cây: thành_cong += 1

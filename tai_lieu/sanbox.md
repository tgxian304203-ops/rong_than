# SANDBOX — CHẠY THỬ CODE

## 1. Vai trò

Sandbox chạy thử code do Đại não sinh ra.

- Chạy client-side (trên trình duyệt người dùng), không cần server riêng.
- Hỗ trợ Python (Pyodide) và HTML (iframe).
- Miễn phí vĩnh viễn, không cần tài khoản.
- Không ảnh hưởng hệ thống.

---

## 2. LiveCodes là gì

LiveCodes là một môi trường chạy code trực tuyến mã nguồn mở, hỗ trợ hơn 90 ngôn ngữ lập trình, bao gồm Python (qua Pyodide — WebAssembly) và HTML/CSS/JS.

- Được nhúng vào giao diện Rồng Thần, giống như nhúng video YouTube vào blog.
- Người dùng mở trang web Rồng Thần, LiveCodes tự tải và hiện ra khu vực chạy code.
- Người dùng không cần cài gì, không cần đăng nhập, không cần mở tab khác.

---

## 3. Cách hoạt động

Đại não sinh code (Python hoặc HTML).
Đại não gửi code đến Sandbox.
Sandbox nhúng code vào LiveCodes.
LiveCodes chạy code trên trình duyệt người dùng.
LiveCodes trả stdout, stderr, thời gian chạy.
Sandbox định dạng kết quả.
Sandbox trả kết quả cho Đại não.
Đại não đọc kết quả, quyết định bước tiếp theo.

---

## 4. Hỗ trợ ngôn ngữ

| Ngôn ngữ | Công nghệ | Ghi chú |
|----------|-----------|---------|
| Python | Pyodide (WebAssembly) | Chạy được hầu hết thư viện Python phổ biến |
| HTML | iframe | Render trực tiếp, chạy JS inline |
| JavaScript | iframe | Chạy trong sandbox |
| CSS | iframe | Áp dụng cho HTML |
| SQL | sql.js | Chạy SQL trên trình duyệt |
| Markdown | marked.js | Render markdown |

Ưu tiên: Python và HTML (theo yêu cầu dự án).

---

## 5. Cấu trúc giao diện Sandbox

Vị trí: nằm trong giao diện chat chính, là khu vực chạy code.

- Nền: màu kính trong suốt 45%.
- Bo viền, bo góc tròn.
- Kích thước: auto co giãn phù hợp mọi màn hình điện thoại.

Cấu trúc:

- Khung code bên trái.
- Khung output bên phải.
- Hai nút Chạy và Copy nằm ở trên, phía bên phải.
- Không có nút Xóa.
- Code hiển thị phải cách ra khỏi phần chữ trả lời của Rồng Thần.
- Code nằm trong khung riêng, có nền tối hơn, viền bo góc tròn.
- Phần chữ trả lời và phần code cách nhau một khoảng.

Sơ đồ:

```

╭─────────────────────────────────────────────╮
│  Sandbox Rồng Thần                          │
│                                             │
│                     ╭───────╮  ╭───────╮   │
│                     │ Chạy  │  │ Copy  │   │
│                     ╰───────╯  ╰───────╯   │
│                                             │
│  ╭─────────────────────╮  ╭──────────────╮ │
│  │  # Code Python/HTML │  │  Output:     │ │
│  │  print("Hello")     │  │  Hello       │ │
│  ╰─────────────────────╯  ╰──────────────╯ │
│                                             │
╰─────────────────────────────────────────────╯

```

---

## 6. Cấu trúc kết quả trả về

Sau khi chạy, Sandbox trả cho Đại não:

```

{
"thanh_cong": true,
"stdout": "Hello",
"stderr": "",
"thoi_gian": 0.5,
"ngon_ngu": "python",
"co_loi": false
}

```

Nếu lỗi:

```

{
"thanh_cong": false,
"stdout": "",
"stderr": "SyntaxError: invalid syntax",
"thoi_gian": 0.1,
"ngon_ngu": "python",
"co_loi": true,
"loai_loi": "SyntaxError"
}

```

---

## 7. Các file module Sandbox

- chay_python.py — Chạy code Python qua Pyodide
- chay_html.py — Render HTML qua iframe
- kiem_tra_loi.py — Kiểm tra code có lỗi không
- tra_ket_qua.py — Định dạng kết quả
- nhung_vao_chat.py — Nhúng kết quả vào chat

Thư mục con giao_dien/:

- index.html — Khung sandbox
- nhung_livecodes.js — Script nhúng LiveCodes
- style.css — Style cho sandbox

---

## 8. Ví dụ

### Chạy code Python

Code:

```

print("Hello Rồng Thần")
print(2 + 3)

```

Kết quả:

```

Hello Rồng Thần
5

```

### Chạy code Python lỗi

Code:

```

print("Hello"

```

Kết quả:

```

SyntaxError: '(' was never closed

```

### Chạy code HTML

Code:

```

<html>
  <body>
    <h1>Xin chào</h1>
  </body>
</html>
```

Kết quả: hiển thị iframe với tiêu đề "Xin chào".

---

9. Quy tắc hiển thị

· Nếu code có cả HTML và Python (task vừa web vừa AI) thì hiển thị 2 khung riêng, có nhãn riêng.
· Nếu code chỉ có HTML thì hiển thị 1 khung với nhãn HTML.
· Nếu code chỉ có Python thì hiển thị 1 khung với nhãn Python.
· Nếu không rõ loại code thì Đại não hỏi lại người dùng muốn HTML hay Python.

---

10. Bảo mật

· Code chạy trên trình duyệt người dùng, không ảnh hưởng server.
· Không truy cập file hệ thống.
· Không truy cập mạng (trừ khi người dùng cho phép).
· Timeout mặc định 30 giây — code chạy quá lâu thì tự dừng.
· Bộ nhớ tối đa 512MB — tránh treo trình duyệt.

---

11. Giới hạn

· Không chạy được code cần GPU.
· Không chạy được code cần kết nối database thật.
· Không chạy được code cần đọc file hệ thống.
· Không chạy được code cần thư viện nặng (tensorflow, pytorch full).
· Đối với các trường hợp trên, Đại não phải báo người dùng giới hạn của Sandbox.

---

12. Ghi log

Mỗi lần Sandbox chạy code, ghi log:

· Thời gian chạy.
· Ngôn ngữ.
· Code chạy.
· stdout.
· stderr.
· Thời gian thực thi.

Log này hiển thị trong menu Logs, filter "Sandbox".
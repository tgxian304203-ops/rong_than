# TÀI KHOẢN

## 1. Vai trò

Tài khoản cho phép người dùng lưu dữ liệu vĩnh viễn. Không cần đăng nhập vẫn dùng được (chế độ khách).

---

## 2. Hai chế độ

### Chế độ khách

- Không cần đăng ký, không cần đăng nhập.
- Dùng ngay.
- Dữ liệu tạm.
- Xóa khi đóng trình duyệt.

### Chế độ tài khoản

- Đăng ký hoặc đăng nhập.
- Dữ liệu lưu vĩnh viễn.
- Lưu vào kho 1.

---

## 3. Đăng ký

### Luồng

Mở web.
Ấn Đăng ký (trong menu trái, mục Người dùng).
Nhập tên đăng nhập.
Nhập mật khẩu (muốn nhập gì cũng được).
Kiểm tra tên đã tồn tại chưa.
Nếu chưa thì tạo tài khoản.
Lưu vào kho 1.

### Quy tắc tên đăng nhập

- Độ dài: 3-30 ký tự.
- Cho phép: chữ cái, số, dấu gạch dưới.
- Không cho phép: khoảng trắng, ký tự đặc biệt.
- Không phân biệt hoa thường.

### Quy tắc mật khẩu

- Muốn nhập gì cũng được (theo Phần 4).
- Mật khẩu được hash trước khi lưu (không lưu plaintext).

---

## 4. Đăng nhập

### Luồng

Mở web.
Ấn Đăng nhập (trong menu trái, mục Người dùng).
Nhập tên đăng nhập.
Nhập mật khẩu.
Kiểm tra với kho 1.
Nếu đúng thì tạo session.

---

## 5. Session

Sau khi đăng nhập thành công:

- Tạo session ID.
- Lưu vào collection `phien_dang_nhap`.
- Session có TTL 7 ngày.
- Sau 7 ngày, session tự xóa.
- Người dùng phải đăng nhập lại.

---

## 6. Đăng xuất

Ấn Đăng xuất.
Xóa session hiện tại.
Quay về chế độ khách.

---

## 7. Đổi mật khẩu

- Chỉ hiện khi đang đăng nhập.
- Nhập mật khẩu cũ.
- Nhập mật khẩu mới.
- Nhập lại mật khẩu mới.
- Ấn Đổi mật khẩu.
- Hệ thống kiểm tra mật khẩu cũ.
- Nếu đúng thì cập nhật mật khẩu mới.

---

## 8. Giới hạn 50 tài khoản

- Max 50 tài khoản trong kho 1.
- Khi tạo tài khoản mới, nếu đủ 50:
  - Tìm tài khoản cũ nhất (sắp xếp theo `ngay_tao` tăng dần).
  - Xóa tài khoản đó và mọi thứ liên quan trong kho 1.
  - Xóa sạch: `tai_khoan`, `phien_dang_nhap`, `lich_su_chat`, `du_an`, `key_da_luu`, `cau_hinh_kho`, `anh_file`, `noi_dung_da_trich_xuat`, `lich_su_gui`, GridFS.
- Kho 2 không liên quan, không đụng đến.

---

## 9. Không dùng bên thứ 3

Không đăng nhập bằng Google, GitHub, Facebook.

Chỉ đăng ký/đăng nhập bằng tên đăng nhập + mật khẩu.

---

## 10. Dữ liệu lưu trong kho 1

- Tài khoản (collection `tai_khoan`).
- Phiên đăng nhập (collection `phien_dang_nhap`).
- Lịch sử chat (collection `lich_su_chat`).
- Dự án (collection `du_an`).
- Key đã lưu (collection `key_da_luu`).
- URI kho (collection `cau_hinh_kho`).
- Ảnh/file (collection `anh_file` + GridFS).
- Nội dung đã đọc từ ảnh/file (collection `noi_dung_da_trich_xuat`).
- Lịch sử gửi file (collection `lich_su_gui`).

---

## 11. Cấu trúc tài khoản

Mỗi tài khoản có dạng:

```

{
"id": "user-abc123",
"ten_dang_nhap": "nguoidung1",
"mat_khau_hash": "sha256$...",
"ngay_tao": 1234567890,
"lan_dang_nhap_cuoi": 1234567890
}

```

---

## 12. Cấu trúc phiên đăng nhập

Mỗi phiên có dạng:

```

{
"id": "phien-xyz",
"session_id": "sess-abc",
"nguoi_dung": "user-abc123",
"ngay_tao": 1234567890,
"het_han": 1234567890
}

```

TTL 7 ngày = 604800 giây.

---

## 13. Bảo mật

- Mật khẩu được hash (SHA256 + salt).
- Session ID ngẫu nhiên (không đoán được).
- Cookie HttpOnly, Secure.
- HTTPS khi deploy Render.
- Không lưu mật khẩu plaintext.
- Không log mật khẩu.

---

## 14. Khôi phục mật khẩu

Không hỗ trợ khôi phục tự động (vì không dùng email).

Nếu quên mật khẩu:
- Tạo tài khoản mới.
- Hoặc chờ reset hệ thống (nếu có).

---

## 15. Các file module

- `giao_dien/xac_thuc.py` — Xác thực server
- `giao_dien/session.py` — Session
- `giao_dien/phien_dang_nhap.py` — Phiên đăng nhập
- `giao_dien/dang_ky.js` — Đăng ký (client)
- `giao_dien/dang_nhap.js` — Đăng nhập (client)
- `giao_dien/doi_mat_khau.py` — Đổi mật khẩu
- `du_lieu/tai_khoan.json` — Bản local backup
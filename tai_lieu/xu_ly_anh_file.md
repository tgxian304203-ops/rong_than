# XỬ LÝ ẢNH VÀ FILE

## 1. Vai trò

Xử lý ảnh/file cho phép người dùng gửi ảnh hoặc file cho Rồng Thần. Ảnh/file thật lưu trong GridFS của kho 1.

---

## 2. Luồng xử lý

Người dùng gửi ảnh hoặc file.
Upload lên server.
Lưu vào GridFS của kho 1.
Đại não nhận URL.
Đại não phân loại ảnh hoặc file.
Đại não xử lý theo loại.
Đại não trả kết quả.

---

## 3. Phân loại ảnh

Đại não phân loại ảnh thành 3 loại:

### Ảnh lỗi (anh_loi)

- Là ảnh chụp màn hình lỗi code.
- Đại não đọc lỗi từ ảnh (OCR).
- Đại não xử lý như người dùng báo lỗi.

### Ảnh code (anh_code)

- Là ảnh chụp màn hình code.
- Đại não đọc code từ ảnh (OCR).
- Đại não xử lý như người dùng gửi code.

### Ảnh thường (anh_thuong)

- Là ảnh không liên quan đến code.
- Đại não phân tích nội dung ảnh nếu cần.

---

## 4. Phân loại file

Đại não phân loại file thành 4 loại:

### File code (file_code)

- Đuôi: .py, .js, .html, .css, .java, .cpp, .sql
- Đại não đọc code, xử lý như người dùng gửi code.

### File tài liệu (file_tai_lieu)

- Đuôi: .pdf, .doc, .docx, .md, .txt
- Đại não đọc nội dung, xử lý.

### File dữ liệu (file_du_lieu)

- Đuôi: .csv, .json, .xlsx, .xls
- Đại não đọc dữ liệu, phân tích.

### File văn bản (file_van_ban)

- Đuôi: .txt, .log
- Đại não đọc nội dung.

---

## 5. Định dạng được phép

### Ảnh

- .jpg, .jpeg, .png, .gif, .webp, .bmp

### File

- .txt, .pdf, .doc, .docx, .xls, .xlsx, .csv, .json, .md
- .py, .js, .html, .css, .java, .cpp, .sql

### Bị chặn

- .exe, .sh, .bat, .dll, .so, .zip, .rar

---

## 6. Giới hạn

- Kích thước tối đa 1 file: 10MB.
- Tổng dung lượng kho 1: 500MB.
- Đã dùng: ~370MB (ước tính).
- Còn dư: ~142MB.

Nếu vượt 500MB, Đại não báo người dùng không thể upload thêm.

---

## 7. GridFS

Ảnh/file thật lưu trong GridFS của kho 1 (MongoDB Atlas).

GridFS chia file thành 2 collection:

- `fs.files`: metadata (tên file, kích thước, ngày tạo).
- `fs.chunks`: nội dung file chia thành các chunk 255KB.

Khi cần đọc file, GridFS ghép các chunk lại.

---

## 8. Cấu trúc metadata

Mỗi ảnh/file upload có 1 document trong collection `anh_file`:

```

{
"id": "anh-abc123",
"file_id": "gridfs-id-xyz",
"ten_file": "screenshot.png",
"loai": "anh_loi",
"kich_thuoc": 102400,
"dinh_dang": "png",
"nguoi_dung": "user1",
"du_an": "du_an-001",
"phien_chat": "chat-xyz",
"noi_dung_da_doc": "Traceback: NameError...",
"ngay_tao": 1234567890
}

```

---

## 9. Các file module

- `giao_dien/upload.py` — Xử lý upload
- `giao_dien/xu_ly_anh.js` — Xử lý ảnh phía client
- `giao_dien/xu_ly_file.js` — Xử lý file phía client
- `dai_nao/phan_biet_code.py` — Phân loại ảnh/file

---

## 10. OCR đọc ảnh

Để đọc chữ từ ảnh, dùng 1 trong các cách:

- Thư viện `pytesseract` (Python).
- API OCR miễn phí (nếu có).
- Tiểu não gọi model đa phương thức (Gemini Vision).

Ưu tiên: Tiểu não gọi Gemini Vision (miễn phí) vì Gemini hỗ trợ đọc ảnh.

---

## 11. Nén ảnh

Trước khi lưu vào GridFS:

- Nếu ảnh > 500KB → nén xuống còn ~200KB.
- Giữ nguyên tỷ lệ.
- Chất lượng 80%.
- Định dạng: JPEG.

Mục đích: tiết kiệm dung lượng kho 1.

---

## 12. Ví dụ

### Gửi ảnh lỗi

Người dùng chụp màn hình lỗi NameError, gửi cho Rồng Thần.
Upload lên GridFS.
Đại não nhận URL.
Đại não phân loại: `anh_loi`.
Đại não OCR đọc lỗi: "NameError: name 'x' is not defined".
Đại não tra từ điển lỗi: có NameError.
Đại não tự sửa.
Đại não trả code đã sửa.

### Gửi file code

Người dùng gửi file `main.py`.
Upload lên GridFS.
Đại não nhận URL.
Đại não phân loại: `file_code`.
Đại não đọc code.
Đại não review code.
Đại não trả nhận xét.

### Gửi file CSV

Người dùng gửi file `data.csv`.
Upload lên GridFS.
Đại não nhận URL.
Đại não phân loại: `file_du_lieu`.
Đại não đọc dữ liệu.
Đại não phân tích (thống kê, biểu đồ).
Đại não trả kết quả.
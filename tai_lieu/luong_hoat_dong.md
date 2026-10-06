# LUỒNG HOẠT ĐỘNG RỒNG THẦN

## 1. LUỒNG TỔNG QUÁT

```

Người dùng gửi task
↓
Đại não nhận task
↓
Đại não chuẩn hóa input
↓
Đại não trích xuất 5 yếu tố
↓
Đủ 5 yếu tố?
├── KHÔNG → Hỏi lại người dùng
└── CÓ → Phân loại task
↓
Đại não duyệt cây quyết định
↓
Có nhánh khớp?
├── KHÔNG → Gọi Tiểu não
└── CÓ → Chấm điểm, chọn nhánh tốt nhất
↓
Kiểm tra failed_paths
↓
Có lỗi cũ?
├── CÓ → Bỏ qua nhánh
└── KHÔNG → Dùng nhánh
↓
Đại não thực thi nhánh
↓
Gửi code đến Sandbox
↓
Sandbox chạy code, trả kết quả
↓
Đại não nhận kết quả
↓
Thành công?
├── KHÔNG → Gọi Tiểu não (sinh nhánh mới)
└── CÓ → Trả kết quả cho người dùng
↓
Lưu cây vào MongoDB

```

**Luồng gọi Tiểu não:**

```

Tiểu não kiểm kê key
↓
Tiểu não dò model
↓
Tiểu não ép model viết trường chuẩn
↓
Tiểu não sinh nhánh mới
↓
Đại não thêm nhánh vào cây
↓
Đại não thử lại task
↓
Thành công?
├── KHÔNG → Gọi Tiểu não lại
└── CÓ → Trả kết quả

```

---

## 2. LUỒNG TRA WEB

```

Đại não cần thông tin ngoài
↓
Đại não gọi Tra web
↓
Tra web gọi SERPJET trước
↓
Hết quota SERPJET?
├── CÓ → Gọi Tavily
└── KHÔNG → Dùng kết quả SERPJET
↓
Hết quota Tavily?
├── CÓ → Gọi Bright Data
└── KHÔNG → Dùng kết quả Tavily
↓
Hết quota Bright Data?
├── CÓ → Báo Đại não hết API
└── KHÔNG → Dùng kết quả Bright Data
↓
Tra web nhận kết quả (tiêu đề, mô tả, URL)
↓
Tra web lấy nội dung từ URL nếu cần
↓
Tra web tổng hợp
↓
Tra web trả kết quả cho Đại não
↓
Đại não xử lý, trả người dùng

```

**Quy tắc:** Tra web không lưu gì vào cây.

---

## 3. LUỒNG XỬ LÝ KHI NGƯỜI DÙNG BÁO LỖI

```

Người dùng báo lỗi
↓
Đại não nhận phản hồi
↓
Đại não tự chạy lại code
↓
Sandbox chạy code
↓
Đại não tự đọc lỗi
↓
Đại não tự phân tích lỗi
↓
Lỗi có trong từ điển?
├── CÓ → Đại não tự sửa
└── KHÔNG → Gọi Tiểu não
↓
Đại não thử lại
↓
Thành công?
├── KHÔNG → Gọi Tiểu não lại
└── CÓ → Trả code mới
↓
Cập nhật cây

```

---

## 4. LUỒNG XỬ LÝ ẢNH VÀ FILE

```

Người dùng gửi ảnh hoặc file
↓
Upload lên server
↓
Lưu vào GridFS của kho 1
↓
Đại não nhận URL
↓
Đại não phân loại ảnh/file
↓
Là ảnh lỗi?    → Đọc lỗi, xử lý như người dùng báo lỗi
Là ảnh code?   → Đọc code, xử lý như người dùng gửi code
Là file code?  → Đọc code, xử lý
Là file tài liệu? → Đọc nội dung, xử lý
Là file dữ liệu? → Đọc dữ liệu, phân tích
↓
Đại não trả kết quả

```

---

## 5. LUỒNG XỬ LÝ TÀI KHOẢN

### Chế độ khách

```

Mở web → Dùng ngay → Dữ liệu tạm → Xóa khi đóng trình duyệt

```

### Chế độ tài khoản

```

Mở web → Đăng ký hoặc Đăng nhập → Dùng → Dữ liệu lưu kho 1

```

**Quy tắc:**
- Max 50 tài khoản.
- Khi tạo tài khoản mới, nếu đủ 50 → xóa tài khoản cũ nhất và mọi thứ liên quan trong kho 1.
- Kho 2 không liên quan, không đụng đến.

---

## 6. SƠ ĐỒ TỔNG HỢP

```

┌───────────┐   ┌───────────┐   ┌───────────┐
│  SANDBOX  │   │  TIỂU NÃO │   │  TRA WEB  │
└─────┬─────┘   └─────┬─────┘   └─────┬─────┘
│               │               │
│         Sinh node mới         │
│         cho cây quyết định    │
│               │               │
│               ▼               │
│       ┌───────────────┐       │
│       │ CÂY QUYẾT ĐỊNH│       │
│       │ (bộ nhớ của   │       │
│       │  Đại não)     │       │
│       └───────┬───────┘       │
│               │               │
│               ▼               │
│       ┌───────────────┐       │
│       │   MONGODB     │       │
│       │  (kho 2)      │       │
│       └───────────────┘       │
│               │               │
└───────────────┼───────────────┘
│
▼
┌───────────────┐
│ Trả kết quả   │
│ cho Đại não   │
└───────────────┘
│
▼
┌───────────────┐
│ Đại não trả   │
│ kết quả cho   │
│ người dùng    │
└───────────────┘

```

---

## 7. LUỒNG HỌC (không học vẹt)

```

Task mới
↓
Đại não duyệt cây
↓
Không có nhánh khớp
↓
Gọi Tiểu não sinh nhánh
↓
Tiểu não sinh quy tắc + thuật toán + cách giải
(KHÔNG sinh kết quả cụ thể)
↓
Đại não thêm nhánh vào cây
↓
Lần sau gặp task tương tự → dùng nhánh đó
↓
Càng dùng, cây càng lớn, Đại não càng mạnh

```

---

## 8. LUỒNG CHỐNG LẶP SAI

```

Task mới
↓
So khớp với failed_paths
↓
Giống hơn 80%?
├── CÓ → Bỏ qua nhánh đó
└── KHÔNG → Dùng nhánh
↓
Node fail 3 lần?
├── CÓ → Blacklist node
└── KHÔNG → Tiếp tục dùng
↓
Node fail hơn 50%?
├── CÓ → Giảm score
└── KHÔNG → Giữ score

```

---

## 9. LUỒNG MƯỢN NHÁNH

```

Không có nhánh khớp hoàn toàn
↓
Tìm nhánh gần giống nhất
↓
Score >= 0.5?
├── CÓ → Mượn cấu trúc, thích nghi
│         (luôn tạo nhánh mới, không sửa nhánh cũ)
└── KHÔNG → Gọi Tiểu não sinh nhánh mới

```

---

## 10. LUỒNG CHIA SẺ NHÁNH

Node cùng quy tắc chia sẻ cho nhau. Ví dụ:
- Cộng ↔ Nhân
- Chia ↔ Trừ
- Lũy thừa ↔ Nhân
- Giai thừa ↔ Nhân

Cách hoạt động: node A có `chia_se_voi: [node_B]` → khi node B cần, dùng quy tắc của node A.
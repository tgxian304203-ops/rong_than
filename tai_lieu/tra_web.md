# TRA WEB — LẤY THÔNG TIN TỪ INTERNET

## 1. Vai trò

Tra web lấy thông tin từ internet khi Đại não cần. Tra web không phải là não, không học, chỉ lấy dữ liệu về cho Đại não.

Tra web dùng 3 API miễn phí có reset hàng tháng: SERPJET, Tavily, Bright Data.

---

## 2. 3 API tra web

### SERPJET

- 1.000 lượt tìm kiếm/tháng.
- Reset ngày 1 hàng tháng.
- Không cần thẻ tín dụng.
- Trả kết quả Google dạng JSON.

### Tavily

- 1.000 lượt tìm kiếm/tháng.
- Reset ngày 1 hàng tháng.
- Không cần thẻ tín dụng.
- Thiết kế riêng cho AI agent.

### Bright Data

- 5.000 credit/tháng.
- Reset ngày 1 hàng tháng.
- Không cần thẻ tín dụng.
- Dùng chung cho SERP API và Web Unlocker.
- Mạnh về truy cập trang web khó.

---

## 3. Cách hoạt động

Đại não nhận task cần tra web.
Đại não gọi tra web.
Tra web gọi SERPJET trước. Nếu hết quota, gọi Tavily. Nếu hết quota, gọi Bright Data. Nếu tất cả hết quota, báo Đại não.
Tra web nhận kết quả: tiêu đề, mô tả, URL.
Tra web lấy nội dung từ URL nếu cần.
Tra web tổng hợp.
Tra web trả kết quả cho Đại não.
Đại não xử lý, trả người dùng.
Tra web không lưu gì vào cây.

---

## 4. Khi nào Đại não gọi Tra web

- Cần thông tin thời gian thực (tin tức, giá cả, thời tiết).
- Cần tra cứu kiến thức ngoài cây.
- Cần xác minh thông tin.
- Người dùng yêu cầu rõ ràng.

Ngoài các trường hợp trên, Đại não dùng cây quyết định trước.

---

## 5. Cấu trúc kết quả trả về

Mỗi kết quả có dạng:

```

{
"tieu_de": "Tiêu đề trang",
"mo_ta": "Mô tả ngắn",
"url": "https://example.com",
"nguon": "serpjet"
}

```

Sau khi tổng hợp, Tra web trả cho Đại não:

```

{
"thanh_cong": true,
"api_dung": "serpjet",
"so_ket_qua": 10,
"danh_sach": [...],
"tong_hop": "Đoạn văn tóm tắt kết quả",
"thoi_gian": 1.5
}

```

---

## 6. Quản lý quota

Mỗi API có bộ đếm quota riêng:

- serpjet: con_lai / tong / lan_reset_cuoi / lan_dung_cuoi
- tavily: con_lai / tong / lan_reset_cuoi / lan_dung_cuoi
- brightdata: con_lai / tong / lan_reset_cuoi / lan_dung_cuoi

Quy tắc:

- Mỗi lần gọi API thành công thì con_lai giảm 1.
- Khi con_lai = 0 thì đánh dấu hết quota, chuyển API khác.
- Ngày 1 hàng tháng thì reset con_lai về tong.

---

## 7. Xử lý lỗi API

- 429 (quá nhiều request): đánh dấu hết quota, chuyển API.
- 401 (key sai): báo Đại não lỗi key.
- 402 (hết quota): đánh dấu hết quota, chuyển API.
- 403 (bị chặn): thử API khác.
- 500 (lỗi server): retry 3 lần, sau đó chuyển API.
- Timeout: retry 3 lần.
- Lỗi mạng: báo Đại não.

---

## 8. Các file module Tra web

- tim_kiem.py — Gọi API tìm kiếm
- lay_noi_dung.py — Lấy nội dung từ URL
- tong_hop.py — Tổng hợp kết quả
- xoay_api.py — Chọn API theo quota
- quan_ly_quota.py — Quản lý quota từng API
- xu_ly_loi_api.py — Xử lý lỗi từ API

Thư mục con api/:

- serpjet.py — Wrapper gọi SERPJET
- tavily.py — Wrapper gọi Tavily
- brightdata.py — Wrapper gọi Bright Data

---

## 9. Ví dụ

Task: "Giá iPhone 15 hiện tại bao nhiêu"

Đại não phân loại: tra cứu, giá cả.
Đại não kiểm tra cây: không có node "giá iPhone".
Đại não gọi Tra web.
Tra web gọi SERPJET.
SERPJET trả 10 kết quả.
Tra web lấy nội dung 3 URL đầu.
Tra web tổng hợp: "iPhone 15 hiện có giá từ 19.990.000đ...".
Tra web trả Đại não.
Đại não trả người dùng.
Tra web KHÔNG lưu gì vào cây.

---

## 10. Quy tắc

1. Tra web không lưu gì vào cây — đó là việc của Đại não.
2. Tra web không quyết định dùng kết quả nào — đó là việc của Đại não.
3. Tra web chỉ lấy dữ liệu thô, không phân tích.
4. Tra web tự xoay API khi hết quota — Đại não không cần biết.
5. Tra web ghi log mỗi lần gọi API (để hiển thị trong menu Logs).

---

## 11. Giới hạn

- Tổng tối đa 7.000 lượt/tháng (1.000 SERPJET + 1.000 Tavily + 5.000 Bright Data).
- Nếu hết cả 3 API thì Tra web báo Đại não "hết quota tra web".
- Đại não có thể chọn: trả lời bằng cây, hoặc hỏi người dùng chờ reset quota.

---

## 12. Bảo mật

- Key API tra web lưu trong kho 1 (collection key_da_luu).
- Key chỉ dán 1 lần qua giao diện, không hard-code.
- Key không được ghi vào log.
- Key không được gửi sang provider khác.
# ĐẠI NÃO — NÃO CHÍNH CỦA RỒNG THẦN

## 1. Vai trò

Đại não là não chính, xử lý mọi task, duyệt cây quyết định.

- Chạy local, không cần gọi API → nhanh và miễn phí.
- Làm được: đọc lỗi, so khớp từ điển, duyệt cây, chấm điểm, ghép code, sửa lỗi đơn giản, chạy sandbox, lưu cây.
- Chỉ gọi Tiểu não khi: task hoàn toàn mới, lỗi lạ, task mơ hồ, code phức tạp, dịch ngôn ngữ.
- Đặc điểm: Càng dùng càng mạnh.

---

## 2. 12 quy tắc bắt buộc

1. Không đoán bừa. Nếu độ tin cậy dưới 95%, không ra lệnh, phải hỏi lại.
2. Hiểu đúng yêu cầu. Xác nhận 5 yếu tố trước khi làm: hành động, đối tượng, thuộc tính, ràng buộc, ngữ cảnh. Thiếu 1 yếu tố thì hỏi lại.
3. Hiểu đúng ngữ cảnh. Kiểm tra 10 loại ngữ cảnh trước khi làm.
4. Ra lệnh có cấu trúc. Lệnh có 6 phần: hành động, đối tượng, thuộc tính, ràng buộc, ngữ cảnh, độ tin cậy.
5. Kiểm tra trước khi làm. Task đã từng làm chưa, nhánh đã fail chưa, nhánh có bị blacklist không, score có đủ cao không.
6. Kiểm tra sau khi làm. Kết quả đúng yêu cầu chưa, có lỗi không, có cần sửa không.
7. Lưu lại để học. Lưu task, nhánh, kết quả, score, thời gian.
8. Hỏi lại nếu mơ hồ. Task có từ mơ hồ như "cái đó", "nó", "kia" thì hỏi lại.
9. Xác nhận trước khi làm task lớn. Tóm tắt kế hoạch cho người dùng xác nhận.
10. Báo lỗi rõ ràng. Nói rõ làm đến đâu, lỗi gì, cần gì để tiếp tục.
11. Tự chạy lại code khi người dùng báo lỗi. Không hỏi lỗi ở đâu, tự chạy lại, tự đọc lỗi, tự phân tích, tự sửa hoặc gọi Tiểu não.
12. Đọc lỗi theo từ điển. Có từ điển lỗi phổ biến: NameError, TypeError, ValueError, ImportError, SyntaxError, IndexError, KeyError, AttributeError. Lỗi nào có trong từ điển thì tự sửa. Lỗi nào không có thì gọi Tiểu não.

---

## 3. 10 bước chuẩn hóa input

1. Tách câu.
2. Sửa viết tắt:
   lm thành làm, ko thành không, dc thành được, vs thành với, wep thành web, hang thành hàng, j thành gì, ntn thành như thế nào, bn thành bao nhiêu, mk thành mình, nx thành nữa, cx thành cũng, đc thành được, bth thành bình thường, bt thành biết, hk thành không, tl thành trả lời, ib thành inbox, rep thành reply, ng thành người, nc thành nước, qá thành quá, wá thành quá, k thành không.
3. Sửa chính tả. Dùng so khớp gần đúng: nếu từ giống từ đúng hơn 90% thì sửa. Nếu giống dưới 90% thì không sửa, hỏi lại.
4. Sửa dấu tiếng Việt. Dùng ngữ cảnh để chọn đúng. Nếu ngữ cảnh không đủ rõ, hỏi lại.
5. Bỏ từ đệm: đi, ạ, nhé, nha, đấy, ấy, thì, mà, là. Nhưng cẩn thận: "thì" trong "nếu... thì..." là từ nối, không bỏ.
6. Sửa dấu câu.
7. Chuẩn hóa viết hoa.
8. Kiểm tra lại. So sánh với input gốc xem ý có bị đổi không. Nếu ý bị đổi, làm lại từ bước 1.
9. Ghi log.
10. Chuyển sang bước trích xuất 5 yếu tố.

---

## 4. 5 yếu tố trích xuất

1. Hành động — task yêu cầu làm gì (tạo, sửa, tính, giải thích).
2. Đối tượng — làm cho cái gì (web, hàm, phương trình).
3. Thuộc tính — đặc điểm của đối tượng (màu, kích thước, ngôn ngữ).
4. Ràng buộc — giới hạn (trong 5 phút, ngắn gọn, đơn giản).
5. Ngữ cảnh — bối cảnh (cho học sinh, bằng Python, trên mobile).

Thiếu 1 yếu tố thì hỏi lại người dùng.

---

## 5. 10 loại ngữ cảnh

1. Ngữ cảnh hội thoại: những gì đã nói trước đó.
2. Ngữ cảnh dự án: dự án hiện tại người dùng đang làm.
3. Ngữ cảnh file: file người dùng đang mở hoặc vừa nhắc.
4. Ngữ cảnh task trước: task vừa làm xong.
5. Ngữ cảnh lĩnh vực: lĩnh vực đang làm việc.
6. Ngữ cảnh ngôn ngữ: ngôn ngữ lập trình đang dùng.
7. Ngữ cảnh môi trường: môi trường chạy (local, Render, sandbox).
8. Ngữ cảnh ràng buộc: yêu cầu đặc biệt đã nói trước.
9. Ngữ cảnh thời gian: thời điểm task được gửi.
10. Ngữ cảnh cảm xúc: thái độ của người dùng (vui, bực, gấp).

---

## 6. Ngưỡng độ tin cậy

- Trên 95%: ra lệnh luôn.
- 90-95%: ra lệnh + ghi chú.
- 70-90%: hỏi lại 1 câu.
- Dưới 70%: hỏi lại nhiều câu.

---

## 7. 6 phần của lệnh

Khi Đại não ra lệnh, lệnh phải có đủ 6 phần:

1. Hành động — làm gì.
2. Đối tượng — làm cho cái gì.
3. Thuộc tính — đặc điểm.
4. Ràng buộc — giới hạn.
5. Ngữ cảnh — bối cảnh.
6. Độ tin cậy — 0-1.

---

## 8. Các file module Đại não

- nhan_task.py — Nhận task từ giao diện
- xu_ly_task.py — Điều phối xử lý task
- phan_loai.py — Phân loại task theo 12 lĩnh vực
- chuan_hoa.py — Chuẩn hóa input 10 bước
- trich_xuat.py — Trích xuất 5 yếu tố
- cay_quyet_dinh.py — Load/quản lý cây
- duyet_cay.py — Duyệt cây tìm nhánh
- cham_diem.py — Chấm điểm node
- chia_se_nhanh.py — Chia sẻ nhánh
- muon_nhanh.py — Mượn nhánh
- chong_lap_sai.py — Chống lặp sai
- doc_loi.py — Đọc lỗi từ stderr
- phan_tich_loi.py — Phân tích lỗi
- tu_sua_loi.py — Tự sửa lỗi
- cap_nhat_tu_dien_loi.py — Cập nhật từ điển lỗi
- tao_code.py — Ghép code từ node
- phan_biet_code.py — Phân biệt HTML/Python
- su_dung_model.py — Gọi model khi cần
- xu_ly_user_bao_loi.py — Xử lý user báo lỗi
- xu_ly_tra_web.py — Điều phối tra web
- goi_tra_web.py — Gọi module tra web
- ghi_nho.py — Lưu cây vào MongoDB
- uu_tien.py — Xếp hạng ưu tiên
- ngu_canh.py — Quản lý 10 loại ngữ cảnh

---

## 9. Luồng xử lý task

1. Nhận task
2. Chuẩn hóa input (10 bước)
3. Trích xuất 5 yếu tố
4. Đủ 5 yếu tố? Không thì hỏi lại
5. Phân loại task (12 lĩnh vực)
6. Duyệt cây quyết định
7. Có nhánh khớp? Không thì gọi Tiểu não
8. Chấm điểm, chọn nhánh tốt nhất
9. Kiểm tra failed_paths
10. Thực thi nhánh
11. Gửi code đến Sandbox
12. Nhận kết quả
13. Thành công? Không thì gọi Tiểu não
14. Trả kết quả cho người dùng
15. Lưu cây vào MongoDB

---

## 10. Khi nào gọi Tiểu não

Đại não tự xử lý phần lớn task. Chỉ gọi Tiểu não khi:

- Task hoàn toàn mới (không có node trong cây).
- Lỗi lạ (không có trong từ điển).
- Task mơ hồ (độ tin cậy dưới 70%).
- Code phức tạp (thuật toán mới, design pattern).
- Dịch ngôn ngữ (Python sang JavaScript).

---

## 11. Khi nào gọi Tra web

- Cần thông tin thời gian thực (tin tức, giá cả).
- Cần tra cứu kiến thức ngoài cây.
- Cần xác minh thông tin.
- Người dùng yêu cầu rõ ràng.

---

## 12. Khi nào gọi Sandbox

- Có code cần chạy thử.
- Có HTML cần render.
- Cần kiểm tra lỗi runtime.
- Cần verify kết quả tính toán.
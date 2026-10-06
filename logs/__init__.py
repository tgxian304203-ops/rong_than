"""
logs - Package Logs Rồng Thần.

Log ghi lại mọi hoạt động của Rồng Thần để:
    - Người dùng xem trong trang Logs.
    - Hệ thống debug khi có lỗi.
    - Phân tích hiệu suất theo thời gian.

Đặc điểm:
    - Ghi vào file + kho 1 (MongoDB).
    - Có 5 loại: Đại não, Tiểu não, Tra web, Sandbox, Lỗi.
    - Cập nhật realtime.
    - Có bộ lọc theo loại.
    - Tự động xóa log cũ sau 30 ngày.

Gồm 4 file:
    - __init__.py: đánh dấu package.
    - ghi_log.py: ghi log hoạt động.
    - doc_log.py: đọc log cho giao diện.
    - loc_log.py: lọc log theo loại.

5 loại log (theo Phần 4):
    1. dai-nao    — task nhận vào, phân loại, duyệt cây, chọn nhánh.
    2. tieu-nao   — key dùng, model gọi, quota, node sinh ra.
    3. tra-web    — API dùng, query, kết quả, quota.
    4. sandbox    — code chạy, stdout, stderr, thời gian.
    5. loi        — lỗi gì, ở đâu, thời gian.

Mỗi dòng log có:
    - thoi_gian: timestamp.
    - loai: 1 trong 5 loại.
    - noi_dung: mô tả hoạt động.

Tầng dữ liệu: dai_nao/ghi_nho.py (kho 1).
"""
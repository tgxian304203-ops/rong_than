"""
tra_web - Package Tra web Rồng Thần.

Tra web lấy thông tin từ internet khi Đại não cần.
Không lưu gì vào cây — chỉ lấy dữ liệu về cho Đại não.

Đặc điểm:
    - Trung lập, nhanh, không lưu gì.
    - Dùng 3 API free có reset hàng tháng:
        + SERPJET: 1.000 lượt tìm kiếm/tháng.
        + Tavily: 1.000 lượt tìm kiếm/tháng.
        + Bright Data: 5.000 credit/tháng.
    - Tự xoay API khi hết quota.
    - Không lưu kết quả vào cây.

Gồm 8 file chính + 3 file API:
    - __init__.py: đánh dấu package.
    - dieu_phoi_tra_web.py: điều phối tra web.
    - tim_kiem.py: gọi API tìm kiếm.
    - lay_noi_dung.py: lấy nội dung trang web.
    - tong_hop.py: tổng hợp kết quả.
    - xoay_api.py: quản lý xoay API.
    - quan_ly_quota.py: theo dõi quota.
    - xu_ly_loi_api.py: xử lý lỗi API.
    - api/__init__.py: đánh dấu sub-package.
    - api/serpjet.py: kết nối SERPJET.
    - api/tavily.py: kết nối Tavily.
    - api/brightdata.py: kết nối Bright Data.

Luồng hoạt động:
    Đại não cần tra web
        ↓
    Gọi dieu_phoi_tra_web
        ↓
    tim_kiem → xoay API: SERPJET → Tavily → Bright Data
        ↓
    Nhận kết quả → tong_hop
        ↓
    Trả cho Đại não

Tầng dữ liệu: Không (Tra web không lưu).
"""
"""
tra_web - Package Tra web Rồng Thần.

Tra web lấy thông tin từ internet khi Đại não cần.
Không lưu gì vào cây quyết định — chỉ lấy dữ liệu về cho Đại não.

Đặc điểm:
    - Trung lập, nhanh, không lưu gì.
    - Dùng 3 API free có reset hàng tháng:
        + SERPJET: 1.000 lượt tìm kiếm/tháng, reset ngày 1 hàng tháng.
        + Tavily: 1.000 lượt tìm kiếm/tháng, reset ngày 1 hàng tháng.
        + Bright Data: 5.000 credit/tháng, reset ngày 1 hàng tháng.
    - Tự xoay API khi hết quota.
    - Không lưu kết quả vào cây.

Gồm 11 file:
    - __init__.py: đánh dấu package.
    - tim_kiem.py: gọi API tìm kiếm.
    - lay_noi_dung.py: lấy nội dung trang web.
    - tong_hop.py: tổng hợp kết quả.
    - xoay_api.py: quản lý xoay API.
    - quan_ly_quota.py: theo dõi quota từng API.
    - xu_ly_loi_api.py: xử lý khi API trả về lỗi.
    - api/__init__.py: đánh dấu sub-package.
    - api/serpjet.py: kết nối SERPJET.
    - api/tavily.py: kết nối Tavily.
    - api/brightdata.py: kết nối Bright Data.

Luồng hoạt động:
    Đại não cần tra web
        ↓
    Gọi Tra web (tra_web/tim_kiem.py)
        ↓
    Xoay API: SERPJET → Tavily → Bright Data
        ↓
    Nhận kết quả → tổng hợp
        ↓
    Trả cho Đại não

Tầng dữ liệu: Không (Tra web không lưu).
"""
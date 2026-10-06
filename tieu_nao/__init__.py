"""
tieu_nao - Package Tiểu não Rồng Thần.

Tiểu não sinh nhánh mới cho cây quyết định khi Đại não bí.
Dùng API free: Groq, OpenRouter, Gemini.

Đặc điểm:
    - Chăm chỉ, tò mò.
    - Chấp nhận chậm hơn để học được cái mới.
    - Không học, chỉ sinh nhánh — Đại não mới là bên học.
    - Dùng API free, xoay key khi hết quota.

Gồm 15 file:
    - __init__.py: đánh dấu package.
    - kiem_ke_key.py: bước 1 — đếm key, liệt kê model.
    - lay_danh_sach_model.py: lấy danh sách model từ API.
    - do_model.py: bước 2 — dò model, xoay quota.
    - xoay_key.py: quản lý xoay vòng key, quota hồi.
    - quan_ly_quota.py: theo dõi quota từng key.
    - quan_ly_loi.py: blacklist model lỗi 3 lần.
    - het_quota.py: xử lý khi hết quota.
    - ep_viet_truong.py: bước 3 — ép model viết JSON.
    - schema_node.py: schema các trường bắt buộc.
    - tao_nhanh.py: sinh nhánh mới.
    - api_groq.py: kết nối Groq.
    - api_openrouter.py: kết nối OpenRouter.
    - api_gemini.py: kết nối Gemini.
    - api_chung.py: interface chung.

3 bước chính (theo Phần 4):
    Bước 1 — Kiểm kê key: đếm key, liệt kê model.
    Bước 2 — Dò model: gọi lần lượt theo thứ tự, xoay quota.
    Bước 3 — Ép model viết trường: sinh node theo JSON schema.

Tầng dữ liệu: dai_nao/ghi_nho.py (dùng chung).
"""
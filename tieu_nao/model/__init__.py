"""
tieu_nao.model - Package bộ dò + gọi Model (Tiểu não).

Nhiệm vụ:
    - Dò Model khả dụng (key còn quota).
    - Gọi Model (Groq/OpenRouter/Gemini).
    - Xoay key khi hết quota.
    - Quản lý quota.
    - Kiểm kê key.

Gồm 12 file:
    - __init__.py: đánh dấu package.
    - do_model.py: dò Model khả dụng.
    - goi_model.py: gọi Model suy luận.
    - xoay_key_model.py: xoay key khi hết quota.
    - quan_ly_quota_model.py: theo dõi quota.
    - het_quota_model.py: xử lý khi hết quota.
    - kiem_ke_key_model.py: kiểm kê key.
    - lay_model_kha_dung.py: alias lấy model từ cau_hinh_model.
    - api/__init__.py: đánh dấu sub-package.
    - api/groq_model.py: kết nối Groq.
    - api/openrouter_model.py: kết nối OpenRouter.
    - api/gemini_model.py: kết nối Gemini.

Nguyên tắc:
    - Model dùng key riêng (không dùng chung key với Boss).
    - Cùng 1 provider → cùng 1 model.
    - Model khai báo ở luu_tru/cau_hinh_model.py.
"""
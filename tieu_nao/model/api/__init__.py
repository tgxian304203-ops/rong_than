"""
model.api - Sub-package kết nối API Model (Tiểu não).

Gồm 4 file:
    - __init__.py: đánh dấu sub-package.
    - groq_model.py: kết nối Groq.
    - openrouter_model.py: kết nối OpenRouter.
    - gemini_model.py: kết nối Gemini.

Mỗi file cung cấp:
    - goi_<tên>_model(key, du_lieu): gọi API.
    - kiem_tra_key_<tên>_model(key): kiểm tra key.

Nguyên tắc:
    - Model dùng key riêng (không dùng chung key với Boss).
    - KHÔNG hardcode model — gọi lay_model_kha_dung().
    - Cùng 1 provider → cùng 1 model.
"""
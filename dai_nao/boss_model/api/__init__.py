"""
boss_model.api - Sub-package kết nối API Boss.

Gồm 4 file:
    - __init__.py: đánh dấu sub-package.
    - groq_boss.py: kết nối Groq.
    - openrouter_boss.py: kết nối OpenRouter.
    - gemini_boss.py: kết nối Gemini.

Mỗi file cung cấp:
    - goi_<tên>_boss(key, du_lieu): gọi API.
    - kiem_tra_key_<tên>_boss(key): kiểm tra key.

Thứ tự ưu tiên: Groq → OpenRouter → Gemini.

Nguyên tắc:
    - Boss dùng key riêng (không dùng chung key với Model).
    - Cùng 1 provider → cùng 1 model.
    - Key hết quota → xoay key khác.
"""
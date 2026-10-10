"""
luu_tru - Package tầng dữ liệu Rồng Thần.

Nhiệm vụ:
    - Kết nối 2 kho MongoDB Atlas.
    - Cung cấp hàm CRUD cho toàn dự án.
    - Lưu trữ hợp đồng + tiến độ cho Cây linh hồn.
    - Quản lý trạng thái key (Boss / Model / Tra web).

Gồm 5 file:
    - __init__.py: đánh dấu package.
    - ghi_nho.py: kết nối 2 kho + CRUD chính.
    - hop_dong.py: schema hợp đồng (kho 2).
    - tien_do.py: schema tiến độ (kho 2).
    - trang_thai_key.py: quản lý trạng thái key.

2 kho MongoDB:
    - KHO 1 (rong_than_user): tài khoản, phiên, chat, key, ảnh/file.
    - KHO 2 (rong_than_cay): hợp đồng, hướng dẫn, node, code, tiến độ.

Nguyên tắc:
    - Mọi collection kho 2 đều gắn chu_so_huu + id_chat.
    - Cây linh hồn LÀ CỦA RIÊNG mỗi chat.
    - Không tự sập nếu MongoDB chưa kết nối.
"""
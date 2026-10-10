"""
cay_linh_hon - Package Cây linh hồn Rồng Thần.

Cây linh hồn là bộ nhớ trung tâm + cầu nối của dự án.
Nằm ở KHO 2 — LÀ CỦA RIÊNG MỖI CHAT (gắn chu_so_huu + id_chat).

Nhiệm vụ:
    - Quản lý hợp đồng (đang làm gì, tới đâu, tiếp theo).
    - Quản lý hướng dẫn (nên làm gì để không sai).
    - Quản lý kế hoạch.
    - Quản lý tiến độ.
    - Lưu code đã viết (GIỮ MÃI MÃI).
    - Lưu kết quả + lỗi.
    - Liệt kê / xóa dự án.
    - Kết nối Đại não ↔ Boss ↔ Tiểu não ↔ Model.

Gồm 12 file:
    - __init__.py: đánh dấu package.
    - hop_dong.py: quản lý hợp đồng.
    - huong_dan.py: quản lý hướng dẫn.
    - ke_hoach.py: quản lý kế hoạch.
    - tien_do.py: quản lý tiến độ.
    - luu_code.py: lưu code đã viết.
    - doc_code.py: đọc code đã viết.
    - luu_ket_qua.py: lưu kết quả.
    - luu_loi.py: lưu lỗi.
    - liet_ke_du_an.py: liệt kê dự án.
    - xoa_du_an.py: xóa dự án.
    - ket_noi.py: cầu nối Đại não ↔ Boss ↔ Tiểu não ↔ Model.

5 collection kho 2:
    - hop_dong: đang làm gì, tới đâu, tiếp theo.
    - huong_dan: nên làm gì, blacklist, thông tin mới.
    - node: node của cây (nếu cần).
    - code_da_viet: code đã viết (GIỮ MÃI).
    - tien_do: tiến độ + lịch sử bước.
"""
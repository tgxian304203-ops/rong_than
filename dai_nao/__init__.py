"""
dai_nao - Package Đại não Rồng Thần.

Đại não là não chính, xử lý mọi task. Chạy local, không cần API.
Là bên duyệt cây quyết định.

Gồm 25 file:
    - __init__.py: đánh dấu package.
    - nhan_task.py: nhận task từ giao diện.
    - xu_ly_task.py: trung tâm điều phối.
    - phan_loai.py: phân loại task.
    - chuan_hoa.py: chuẩn hóa input (10 bước).
    - trich_xuat.py: trích xuất 5 yếu tố.
    - cay_quyet_dinh.py: cấu trúc cây (Nut, Cay).
    - duyet_cay.py: thuật toán duyệt cây.
    - cham_diem.py: tính score.
    - chia_se_nhanh.py: cơ chế chia sẻ nhánh.
    - muon_nhanh.py: cơ chế mượn nhánh.
    - chong_lap_sai.py: failed_paths, blacklist.
    - doc_loi.py: đọc lỗi, từ điển lỗi.
    - phan_tich_loi.py: phân tích nguyên nhân lỗi.
    - tu_sua_loi.py: tự sửa lỗi có trong từ điển.
    - cap_nhat_tu_dien_loi.py: cập nhật từ điển lỗi.
    - tao_code.py: ghép code từ node.
    - phan_biet_code.py: phân biệt HTML/Python.
    - su_dung_model.py: gọi Tiểu não khi bí.
    - xu_ly_user_bao_loi.py: tự chạy lại khi user báo lỗi.
    - xu_ly_tra_web.py: xử lý task tra web.
    - goi_tra_web.py: gọi tra web.
    - ghi_nho.py: đọc/ghi MongoDB (kho 1 + kho 2).
    - uu_tien.py: xếp hạng ưu tiên.
    - ngu_canh.py: quản lý 10 loại ngữ cảnh.

Tầng dữ liệu: dai_nao/ghi_nho.py (kết nối 2 kho MongoDB Atlas).
"""
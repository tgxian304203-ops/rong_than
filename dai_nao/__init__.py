"""
dai_nao - Package Đại não Rồng Thần.

Đại não là bộ não chính — code logic thuần, KHÔNG tự suy luận.
Suy luận do Boss đảm nhiệm (Boss là model AI).

Nhiệm vụ:
    - Nhận yêu cầu từ giao diện.
    - Phân loại đơn giản / dự án.
    - Phân loại loại: code / toán / văn / khác.
    - Gọi Boss để suy luận.
    - Ghi hợp đồng vào Cây linh hồn (lần đầu).
    - Cập nhật hợp đồng sau mỗi sự kiện.
    - ÉP Boss THẾ đọc hợp đồng trước khi làm.
    - Điều phối Sandbox khi cần verify code.
    - Trả kết quả cuối cho user.

Gồm 10 file:
    - __init__.py: đánh dấu package.
    - nhan_yeu_cau.py: nhận yêu cầu từ giao diện.
    - dieu_phoi.py: điều phối toàn bộ luồng.
    - phan_loai.py: phân loại đơn giản / dự án.
    - ghi_hop_dong.py: ghi / cập nhật hợp đồng.
    - ep_boss_doc.py: ép Boss THẾ đọc hợp đồng.
    - kiem_tra_boss.py: kiểm tra Boss đã đọc chưa.
    - luu_ket_qua.py: lưu kết quả.
    - kiem_tra_loi.py: kiểm tra lỗi.
    - tra_ket_qua.py: trả kết quả cuối cho giao diện.

Luồng:
    User → giao diện → nhan_yeu_cau → dieu_phoi
        → phan_loai → ghi_hop_dong → gọi Boss
        → Boss gọi Model → verify → trả user

Nguyên tắc:
    - Đại não KHÔNG tự suy luận.
    - Đại não CHỈ code logic + điều phối.
    - Mọi suy luận → gọi Boss.
"""
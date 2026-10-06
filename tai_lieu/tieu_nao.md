# TIỂU NÃO — SINH NHÁNH MỚI CHO CÂY

## 1. Vai trò

Tiểu não sinh nhánh mới cho cây khi Đại não bí.

- Tiểu não không học, chỉ sinh nhánh.
- Đại não mới là bên học.
- Tiểu não dùng API free: Groq, OpenRouter, Gemini.
- Chấp nhận chậm hơn để học được cái mới.

---

## 2. Khi nào Tiểu não được gọi

Đại não gọi Tiểu não khi:

- Task hoàn toàn mới (không có node trong cây).
- Lỗi lạ (không có trong từ điển).
- Task mơ hồ (độ tin cậy dưới 70%).
- Code phức tạp (thuật toán mới, design pattern).
- Dịch ngôn ngữ (Python sang JavaScript).

Ngoài các trường hợp trên, Đại não tự xử lý.

---

## 3. Ba bước chính của Tiểu não

### Bước 1: Kiểm kê key

Xác định:

- Có bao nhiêu key.
- Key đó thuộc provider nào (Groq, OpenRouter, Gemini).
- Key đó dùng được model nào.
- Key nào còn quota, key nào hết quota.

Ví dụ: 2 key Groq, 3 key OpenRouter, 1 key Gemini.

### Bước 2: Dò model

Gọi lần lượt theo thứ tự, không gọi cùng lúc.

Ví dụ có 3 key Groq, 2 key OpenRouter, 2 key Gemini:

```

Groq #1
Groq #2
Groq #3
OpenRouter #1
OpenRouter #2
Gemini #1
Gemini #2

```

Quy tắc:

- Key nào hết quota thì nhảy key tiếp theo.
- Hết tất cả thì quay lại key #1 nếu hồi quota.
- Key nào hồi quota thì quay lại dùng key đó.
- Model nào lỗi 3 lần thì blacklist.

### Bước 3: Ép model viết trường

- Tạo prompt yêu cầu model sinh node theo JSON schema.
- Gửi đến model.
- Validate JSON.
- Sai thì retry 3 lần.
- Vẫn sai thì báo lỗi.
- Đúng thì trả node về Đại não.

---

## 4. 10 nhóm trường model phải sinh

### Nhóm định danh
- id
- ten
- phien_ban

### Nhóm phân loại
- linh_vuc
- nhom
- loai
- ngu_canh

### Nhóm điều kiện
- task chứa gì (dieu_kien.chua)
- input dạng gì
- không dùng khi nào

### Nhóm quy tắc
- mo_ta
- pham_vi

### Nhóm thuật toán
- ten
- mo_ta
- do_phuc_tap

### Nhóm cách giải
- mo_ta
- vi_du
- ket_qua_mong_doi

### Nhóm hành động
- code_mau
- ngon_ngu

### Nhóm đánh giá
- do_kho
- thoi_gian_uoc_tinh
- uu_tien

### Nhóm phụ thuộc
- phu_thuoc (cần node nào trước)

### Nhóm sandbox
- co_can_chay (True/False)
- ngon_ngu
- test_case
- timeout

---

## 5. Quy tắc vàng

Không lưu kết quả cụ thể (2+3=5), chỉ lưu quy tắc, thuật toán, cách giải. Node phải áp dụng được cho mọi task cùng loại.

Ví dụ đúng:

```

{
"ten": "Cộng số nguyên",
"quy_tac": "a + b",
"thuat_toan": {"ten": "cong", "mo_ta": "a + b"}
}

```

Ví dụ sai:

```

{
"ten": "Cộng 2 và 3",
"ket_qua": "5"
}

```

Node sai chỉ dùng được cho 2+3, không áp dụng cho 5+7.

---

## 6. Các file module Tiểu não

- kiem_ke_key.py — Kiểm kê key có sẵn
- lay_danh_sach_model.py — Lấy danh sách model từ provider
- do_model.py — Dò model theo thứ tự
- xoay_key.py — Xoay key khi hết quota
- quan_ly_quota.py — Quản lý quota từng key
- quan_ly_loi.py — Quản lý lỗi từ model
- het_quota.py — Xử lý khi hết quota toàn bộ
- ep_viet_truong.py — Ép model viết trường chuẩn
- schema_node.py — Schema 25 trường của node
- tao_nhanh.py — Sinh nhánh mới từ model
- api_groq.py — Gọi API Groq
- api_openrouter.py — Gọi API OpenRouter
- api_gemini.py — Gọi API Gemini
- api_chung.py — Interface chung cho 3 API

---

## 7. Quy tắc xoay key

Thứ tự gọi mặc định:

```

1. Groq #1
2. Groq #2
3. Groq #3
4. OpenRouter #1
5. OpenRouter #2
6. Gemini #1
7. Gemini #2

```

Quy tắc chi tiết:

- Nếu key đang gọi trả về lỗi 429 (too many requests) thì đánh dấu hết quota.
- Nhảy sang key tiếp theo.
- Sau khi hết tất cả, chờ 60 giây rồi quay lại key #1.
- Key nào hồi quota (dựa vào thời gian reset) thì quay lại dùng key đó.
- Model nào lỗi 3 lần thì đưa vào blacklist.

---

## 8. Quản lý lỗi

Tiểu não phân loại lỗi:

| Mã lỗi | Ý nghĩa | Hành động |
|--------|---------|-----------|
| 429 | Quá nhiều request | Xoay key |
| 401 | Key sai | Xóa key, báo lỗi |
| 402 | Hết quota | Xoay key |
| 500 | Lỗi server | Retry sau 5 giây |
| Timeout | Quá thời gian | Xoay key |
| Lỗi mạng | Không có mạng | Retry 3 lần |

---

## 9. Ép model viết trường chuẩn

Prompt mẫu gửi model:

```

Bạn là module sinh nhánh cho cây quyết định Rồng Thần.

Nhiệm vụ: Sinh 1 node JSON cho cây quyết định.

Thông tin:

· Tên node: {ten}
· Lĩnh vực: {linh_vuc}
· Loại vấn đề: {loai_van_de}
· Ngữ cảnh: {ngu_canh}

Yêu cầu:

1. Trả về DUY NHẤT 1 object JSON, không kèm text giải thích.
2. Node phải có đủ các trường sau: id, ten, phien_ban, dieu_kien, quy_tac, thuat_toan, cach_giai, hanh_dong, score, do_kho, thoi_gian_uoc_tinh, uu_tien, nhanh_con, phu_thuoc, chia_se_voi, muon_tu, failed_paths, blacklist, linh_vuc, loai_van_de, cach_giai_phap, ngu_canh_node, ngay_tao, lan_dung_cuoi.
3. KHÔNG lưu kết quả cụ thể. CHỈ lưu quy tắc, thuật toán, cách giải.
4. Node phải áp dụng được cho mọi task cùng loại.

Ví dụ trả về:
{
"id": "nut-toan-cong-phan-so-0001",
"ten": "Cộng phân số",
"phien_ban": 1,
"dieu_kien": {"chua": ["cộng phân số", "1/2 + 1/3"], "yeu_to_can": ["hanh_dong"]},
"quy_tac": "a/b + c/d = (ad + bc) / (b*d)",
"thuat_toan": {"ten": "cong_phan_so", "mo_ta": "Quy đồng mẫu số", "do_phuc_tap": "O(1)"},
"cach_giai": {"mo_ta": "Dùng Fraction để cộng", "cac_buoc": ["Trích 2 phân số", "Quy đồng", "Cộng tử"], "vi_du": "1/2 + 1/3 = 5/6"},
"hanh_dong": {"loai": "chay_code", "code": "from fractions import Fraction\ndef cong_phan_so(a,b,c,d):\n    return Fraction(a,b)+Fraction(c,d)", "ngon_ngu": "python"},
"score": 0.85, "do_kho": 0.3, "thoi_gian_uoc_tinh": 1, "uu_tien": 85,
"nhanh_con": [], "phu_thuoc": [], "chia_se_voi": [], "muon_tu": "",
"failed_paths": [], "blacklist": false,
"linh_vuc": "toán", "loai_van_de": "số học", "cach_giai_phap": "phân số", "ngu_canh_node": "",
"ngay_tao": 0, "lan_dung_cuoi": 0
}

```

---

## 10. Validate node

Sau khi model trả về, Tiểu não validate:

1. Parse JSON thành công chưa.
2. Có đủ 25 trường bắt buộc chưa.
3. `id` có đúng format `nut-...-XXXX` chưa.
4. `linh_vuc` có nằm trong 12 lĩnh vực chưa.
5. `nhanh_con` có phải mảng không.
6. `blacklist` có phải boolean không.

Nếu sai trường nào → retry với prompt bổ sung.

Nếu sai cả 3 lần → báo Đại não lỗi.

---

## 11. Sinh nhiều nhánh (batch)

Nếu cần sinh nhiều node cùng lúc:

1. Sinh từng node một, không sinh cùng lúc.
2. Node sau có thể dùng `phu_thuoc` để tham chiếu node trước.
3. Các node cùng `loai_van_de` có thể chia sẻ `chia_se_voi`.

---

## 12. Giới hạn

Tiểu não có 3 giới hạn:

1. Không được sửa cây — chỉ được thêm nhánh mới.
2. Không được xóa nhánh cũ.
3. Không được gọi API khi Đại não chưa yêu cầu.

Đại não là bên quyết định cuối cùng có thêm nhánh vào cây hay không.
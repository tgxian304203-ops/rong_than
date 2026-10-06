# CÂY QUYẾT ĐỊNH — BỘ NHỚ DÀI HẠN CỦA ĐẠI NÃO

## 1. Vai trò

Cây quyết định là bộ nhớ dài hạn của Đại não.

- Cây thuộc về Đại não.
- Đại não duyệt cây.
- Tiểu não sinh nhánh mới thêm vào cây.
- Cây không viết sẵn từ đầu — cây mọc dần qua từng task.

---

## 2. Cấu trúc 4 tầng

Tầng 1: LĨNH VỰC (12 lĩnh vực)
Tầng 2: LOẠI VẤN ĐỀ (nhóm con)
Tầng 3: CÁCH GIẢI (phương pháp cụ thể)
Tầng 4: NGỮ CẢNH (biến thể theo ngữ cảnh)

Ví dụ cây:

```

ROOT
├── toán
│   ├── số học
│   │   ├── cộng
│   │   ├── trừ
│   │   ├── nhân
│   │   └── chia
│   ├── đại số
│   │   ├── phương trình bậc 1
│   │   ├── phương trình bậc 2
│   │   └── hệ phương trình
│   └── lượng giác
│       ├── sin
│       ├── cos
│       └── tan
├── văn
│   ├── viết đoạn văn
│   ├── tóm tắt
│   └── dịch
├── code
│   ├── tạo mới
│   ├── sửa
│   ├── tối ưu
│   └── thuật toán
└── bug
├── syntax
├── logic
├── runtime
└── payment

```

---

## 3. 12 lĩnh vực chính

1. toán — số học, đại số, hình học, giải tích, lượng giác, xác suất
2. văn — viết, email, tiểu luận, phân tích, nghị luận, tóm tắt, dịch, thơ, kể chuyện
3. code — tạo mới, sửa, tối ưu, review, giải thích, chuyển đổi, thuật toán, docker, deploy
4. bug — syntax, name, type, value, index, key, attribute, import, runtime, zerodivision, recursion, memory, file, permission, connection, timeout, unicode, assertion, network, security, performance, payment, database, config
5. khoa học — vật lý, hóa học, sinh học, thiên văn, địa lý, môi trường, y học, tâm lý, xã hội, lịch sử
6. đời sống — sức khỏe, nấu ăn, du lịch, tài chính, tâm lý, mối quan hệ, thể thao, thời trang, nuôi con, thú cưng
7. kinh doanh — marketing, bán hàng, quản lý, khởi nghiệp, tài chính DN, đầu tư, tmđt, nhân sự, thương hiệu, logistics
8. sáng tạo — viết truyện, làm thơ, thiết kế, âm nhạc, kịch bản, ý tưởng, vẽ, nhiếp ảnh, video, content
9. học tập — giải thích, hướng dẫn, luyện tập, kiểm tra, tóm tắt bài, flashcard, mindmap, ghi nhớ, ôn thi, đọc hiểu
10. tra cứu — định nghĩa, so sánh, lịch sử, tin tức, danh nhân, sự kiện, thống kê, địa chỉ, giá cả, review
11. kỹ thuật — điện, cơ khí, xây dựng, ô tô, điện tử, robot, nhiệt, thủy lực, vật liệu, in 3D
12. luật - hành chính — dân sự, hình sự, lao động, hợp đồng, thủ tục, thuế, bảo hiểm, SHTT, hôn nhân, đất đai

---

## 4. 25 trường của mỗi node

Nhóm định danh (3 trường):
- id — ID duy nhất, dạng nut-linhvuc-loai-XXXX
- ten — tên node
- phien_ban — phiên bản (mặc định 1)

Nhóm phân loại (4 trường):
- linh_vuc — 1 trong 12 lĩnh vực
- loai_van_de — nhóm con
- cach_giai_phap — phương pháp cụ thể
- ngu_canh_node — ngữ cảnh

Nhóm điều kiện (1 trường gộp):
- dieu_kien — object gồm: chua (mảng từ khóa), yeu_to_can (mảng yếu tố)

Nhóm quy tắc (1 trường):
- quy_tac — mô tả quy tắc xử lý

Nhóm thuật toán (1 trường gộp):
- thuat_toan — object gồm: ten, mo_ta, do_phuc_tap

Nhóm cách giải (1 trường gộp):
- cach_giai — object gồm: mo_ta, cac_buoc, vi_du

Nhóm hành động (1 trường gộp):
- hanh_dong — object gồm: loai, code, ngon_ngu

Nhóm đánh giá (7 trường):
- score — điểm tổng hợp (0-1)
- so_lan_thu — số lần thử
- thanh_cong — số lần thành công
- that_bai — số lần thất bại
- do_kho — độ khó (0-1)
- thoi_gian_uoc_tinh — thời gian ước tính (giây)
- uu_tien — ưu tiên (0-100)

Nhóm quan hệ (4 trường):
- phu_thuoc — mảng node ID phụ thuộc
- nhanh_con — mảng node con
- chia_se_voi — mảng node ID chia sẻ quy tắc
- muon_tu — node ID mượn

Nhóm trạng thái (4 trường):
- failed_paths — mảng vết sai
- blacklist — node bị chặn (True/False)
- ngay_tao — timestamp tạo
- lan_dung_cuoi — timestamp dùng cuối

Tổng: 3 + 4 + 1 + 1 + 1 + 1 + 1 + 7 + 4 + 4 = 27 trường thực tế. Schema lưu 25 trường chuẩn, một số trường gộp.

---

## 5. Ví dụ duyệt cây

### Task "2 + 3"

```

Phân loại: toán, cộng, số nguyên, 2 số
Duyệt cây: ROOT → toán → số học → cộng
Tìm nhánh con "số nguyên, 2 số"
Kiểm tra điều kiện: task chứa "cộng", input số nguyên, có 2 số
Kiểm tra failed_paths: chưa từng fail → dùng được
Chấm điểm: 0.95 → chọn
Thực thi: áp dụng quy tắc "a + b"
Sandbox chạy: 2 + 3 = 5
Cập nhật node: so_lan_thu += 1, thanh_cong += 1

```

### Task "1/2 + 1/3"

```

Phân loại: toán, cộng, phân số
Duyệt cây: ROOT → toán → số học → cộng
Tìm nhánh con "phân số" → KHÔNG có
Gọi Tiểu não
Tiểu não sinh node mới "cộng phân số"
Gắn vào cây
Thử lại → thành công

```

### Task "999999 + 999999"

```

Duyệt cây: toán, số học, cộng, số nguyên, 2 số
Khớp node cũ → dùng luôn
KHÔNG cần Tiểu não

```

---

## 6. Chia sẻ nhánh

Node cùng quy tắc chia sẻ cho nhau:

- cộng ↔ nhân (phép toán 2 số)
- chia ↔ trừ (phép toán ngược)
- lũy thừa ↔ nhân (nhân liên tiếp)
- giai thừa ↔ nhân (nhân dãy số)

Cách hoạt động: node A có trường chia_se_voi: [node_B_id] → khi node B cần, tra quy tắc của A.

---

## 7. Mượn nhánh

```

Task mới không có nhánh khớp hoàn toàn
Tìm nhánh gần giống nhất
Score >= 0.5?
CÓ → Mượn cấu trúc, thích nghi
(LUÔN tạo nhánh mới, KHÔNG sửa nhánh cũ)
KHÔNG → Gọi Tiểu não

```

---

## 8. Tránh lặp sai

Mỗi node lưu failed_paths — danh sách vết sai.

Quy tắc:
- Task mới giống failed_path hơn 80% → bỏ qua node.
- Node fail 3 lần → blacklist node.
- Node fail hơn 50% → giảm score.

---

## 9. Chấm điểm

Công thức:

```

score = tỷ_lệ_thành_công × 0.4
+ độ_tin_cậy × 0.2
+ ưu_tiên × 0.2
+ độ_khó × 0.2

```

- tỷ_lệ_thành_công = thanh_cong / (thanh_cong + that_bai)
- độ_tin_cậy — score gốc khi sinh nhánh
- ưu_tiên — từ 0-100, chia 100 để về 0-1
- độ_khó — từ 0-1

---

## 10. Học bản chất, không học vẹt

Quy tắc vàng:
- KHÔNG lưu kết quả cụ thể (2+3=5).
- CHỈ lưu quy tắc (a+b), thuật toán, cách giải.
- Node phải áp dụng được cho mọi task cùng loại.

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

## 11. Cây mọc dần

```

Task 1: "2+3" → dùng node có sẵn
Task 2: "1/2+1/3" → Tiểu não sinh "cộng phân số"
Task 3: "sin(30°)" → Tiểu não sinh "sin"
Task 4: "2+3" → dùng node có sẵn (nhanh hơn)
Task 5: "1/4+1/5" → dùng node "cộng phân số" đã có
Sau 1000 task: cây có ~500 node → Đại não rất mạnh

```

---

## 12. File lưu cây

Cây được chia thành 5 file JSON trong du_lieu/:

- cay_quyet_dinh.json — Node gốc ROOT + 12 lĩnh vực
- cay_toan.json — Cây Toán (đầy đủ)
- cay_code.json — Cây Code (đầy đủ)
- cay_bug.json — Cây Bug (đầy đủ)
- cay_khac.json — 9 lĩnh vực còn lại

Khi Rồng Thần khởi động, ghi_nho.py tự gộp 5 file thành 1 cây trong bộ nhớ.
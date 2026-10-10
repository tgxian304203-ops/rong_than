# 🌕🐉 RỒNG THẦN

**AI Agent tự trị — Kiến trúc 2 não**

---

## TỔNG QUAN

Rồng Thần là AI Agent tự trị, hoạt động theo kiến trúc 2 não:

- **Đại não** — Code logic thuần, KHÔNG tự suy luận. Điều phối toàn bộ luồng.
- **Tiểu não** — Cầu nối giữa Cây linh hồn và Model.
- **Boss** — Trí tuệ của Đại não (model AI riêng).
- **Model** — Công cụ của Tiểu não (model AI riêng).
- **Cây linh hồn** — Bộ nhớ trung tâm, của riêng mỗi chat.
- **Sandbox** — Chạy code (LiveCodes, client-side).

---

## KIẾN TRÚC

```
User
  ↓
Giao diện (HTML/CSS/JS)
  ↓
Đại não (code logic)
  ├── Gọi Boss (suy luận)
  ├── Ghi hợp đồng vào Cây linh hồn
  ↓
Cây linh hồn (kho 2, của riêng mỗi chat)
  ↓
Tiểu não (cầu nối)
  ├── ÉP Model làm việc
  ↓
Model
  ↓
VERIFY:
  ├── Code → Sandbox
  ├── Toán/Văn → Boss tự verify
  ↓
Boss verify cuối
  ↓
Trả user
```

---

## 2 KHO MONGODB

**KHO 1** — `rong_than_user` (dữ liệu người dùng):
- `tai_khoan`, `phien_dang_nhap`, `du_an`, `lich_su_chat`,
  `key_da_luu`, `cau_hinh_kho`, `anh_file`,
  `noi_dung_da_trich_xuat`, `lich_su_gui`, `chat_nhanh`,
  `tro_chuyen`, `tin_nhan`, `logs`.

**KHO 2** — `rong_than_cay` (cây linh hồn):
- `hop_dong`, `huong_dan`, `node`, `code_da_viet`, `tien_do`,
  `trang_thai_key`.
- Mọi collection đều gắn `chu_so_huu` + `id_chat`.

---

## CÀI ĐẶT

### 1. Cài thư viện

```
pip install -r yeu_cau.txt
```

### 2. Cấu hình URI 2 kho

Tạo file `du_lieu/cau_hinh_kho.json`:

```json
{
  "uri_kho_1": "mongodb+srv://...",
  "uri_kho_2": "mongodb+srv://..."
}
```

### 3. Chạy local

```
python khoi_dong.py
```

Mở trình duyệt: `http://localhost:5000`

### 4. Chạy Render

- Build Command: `pip install -r yeu_cau.txt`
- Start Command: `gunicorn khoi_dong:ung_dung --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`

---

## CẤU TRÚC THƯ MỤC

```
rong_than/
├── khoi_dong.py
├── cau_hinh.py
├── Procfile
├── runtime.txt
├── yeu_cau.txt
├── README.md
├── .gitignore
│
├── dai_nao/            # Đại não
│   ├── nhan_yeu_cau.py
│   ├── dieu_phoi.py
│   ├── phan_loai.py
│   ├── ghi_hop_dong.py
│   ├── ep_boss_doc.py
│   ├── kiem_tra_boss.py
│   ├── luu_ket_qua.py
│   ├── kiem_tra_loi.py
│   ├── tra_ket_qua.py
│   ├── boss_model/     # Boss
│   └── tra_web/        # Tra web
│
├── cay_linh_hon/       # Cây linh hồn
├── tieu_nao/           # Tiểu não
│   ├── model/          # Model
│   └── sanbox/         # Sandbox
├── luu_tru/            # Tầng dữ liệu
├── giao_dien/          # Giao diện
├── logs/               # Logs
├── du_lieu/            # Dữ liệu
└── tai_lieu/           # Tài liệu
```

---

## MODEL ĐANG DÙNG

Cấu hình tại `luu_tru/cau_hinh_model.py`.

| Provider | Model mạnh nhất | Model dự phòng |
|----------|-----------------|----------------|
| **Groq** | `qwen/qwen3.8-27b` | `openai/gpt-oss-120b` |
| **OpenRouter** | `deepseek/deepseek-v4-flash:free` | `qwen/qwen3.8-27b:free` |
| **Gemini** | `gemini-3.1-flash-lite` | — |

**Lưu ý:** Nhà cung cấp đổi model → chỉ sửa `luu_tru/cau_hinh_model.py`.

---

## TÍNH NĂNG

- ✅ Chat với AI (nhiều model free).
- ✅ Sinh code, sửa code, chạy sandbox.
- ✅ Tra web (SERPJET/Tavily/Bright Data).
- ✅ Quản lý dự án + trò chuyện.
- ✅ Upload ảnh + file.
- ✅ Cây linh hồn (nhớ dài hạn).
- ✅ Đa tài khoản, đa key (bể quota).
- ✅ Logs realtime.
- ✅ Đa ngôn ngữ code (Python, JS, HTML, CSS, ...).

---

## BẢO MẬT

- Mật khẩu băm bằng SHA-256 + salt.
- Phiên đăng nhập 7 ngày.
- Giới hạn 50 tài khoản.
- Xóa tài khoản → xóa hết dữ liệu liên quan.
- Key/URI lưu ở kho riêng, che mật khẩu khi hiển thị.

---

## GIẤY PHÉP

Dự án cá nhân — không có giấy phép thương mại.

---

**🌕🐉 Chúc bạn dùng Rồng Thần vui vẻ!**
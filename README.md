# 🌕🐉 Rồng Thần

> **AI Agent tự trị — Kiến trúc 2 não — Càng dùng càng thông minh**

---

## 📖 Giới thiệu

**Rồng Thần** là AI agent tự trị với kiến trúc 2 não, có khả năng tự học, tự sửa lỗi, tự mở rộng kiến thức mà không cần lập trình viên can thiệp.

Khác với chatbot thường (chỉ trả lời rồi quên), Rồng Thần **tự xây dựng bộ não của mình qua từng task**. Càng dùng, càng thông minh.

---

## 🧠 Kiến trúc

```

┌─────────────────────────────────────────────────────────┐
│                     NGƯỜI DÙNG                          │
└────────────────────────┬────────────────────────────────┘
│
▼
┌───────────────────┐
│    GIAO DIỆN      │
│  (HTML + JS)      │
└─────────┬─────────┘
│
▼
┌───────────────────┐
│     ĐẠI NÃO       │
│   (xử lý chính)   │
│   Chạy local      │
└──┬─────┬─────┬────┘
│     │     │
┌────────┘     │     └────────┐
▼              ▼              ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│ SANDBOX │   │TIỂU NÃO │   │ TRA WEB │
│LiveCodes│   │ API free│   │ 3 APIs  │
└────┬────┘   └────┬────┘   └────┬────┘
│             │             │
│        Sinh nhánh         │
│             │             │
│             ▼             │
│      ┌────────────┐       │
│      │CÂY QUYẾT   │       │
│      │  ĐỊNH      │       │
│      └─────┬──────┘       │
│            │              │
│            ▼              │
│      ┌────────────┐       │
│      │  MONGODB   │       │
│      │  2 kho     │       │
│      └────────────┘       │
│                           │
└───────────┬───────────────┘
│
▼
┌───────────────┐
│  TRẢ KẾT QUẢ  │
└───────────────┘

```

---

## ✨ Đặc điểm

### 🧠 Đại não (não chính)
- Xử lý mọi task, chạy local, không cần API.
- Duyệt cây quyết định, chấm điểm, chọn nhánh tốt nhất.
- Không bao giờ đoán bừa — độ tin cậy < 95% thì hỏi lại.
- Tự sửa lỗi có trong từ điển.

### 🧠🧠 Tiểu não (sinh nhánh)
- Sinh nhánh mới khi Đại não bí.
- Dùng API free: Groq, OpenRouter, Gemini.
- Tự xoay key khi hết quota.
- Blacklist model lỗi 3 lần.

### 🌐 Tra web
- 3 API free: SERPJET (1.000/tháng), Tavily (1.000/tháng), Bright Data (5.000/tháng).
- Tự xoay API khi hết quota.
- Không lưu gì vào cây.

### 🧪 Sandbox
- Chạy code client-side qua LiveCodes + Pyodide.
- Hỗ trợ Python 3.13, HTML, JavaScript, CSS, và 90+ ngôn ngữ khác.
- Không cần server riêng.

### 🌳 Cây quyết định
- Bộ nhớ dài hạn của Đại não.
- 12 lĩnh vực chính, mọc dần qua từng task.
- Chống học vẹt — chỉ lưu quy tắc, thuật toán, cách giải.
- Chia sẻ nhánh: cộng ↔ nhân, trừ ↔ chia, lũy thừa ↔ nhân.

---

## 🎯 12 lĩnh vực chính

| # | Lĩnh vực | Ví dụ |
|---|----------|-------|
| 1 | **Toán** | số học, đại số, hình học, giải tích, lượng giác, xác suất |
| 2 | **Văn** | viết đoạn văn, email, tiểu luận, dịch, thơ |
| 3 | **Code** | web, API, mobile, AI, script, database, game |
| 4 | **Bug** | syntax, runtime, logic, network, security, payment |
| 5 | **Khoa học** | vật lý, hóa học, sinh học, thiên văn, y học |
| 6 | **Đời sống** | sức khỏe, nấu ăn, du lịch, tài chính, tâm lý |
| 7 | **Kinh doanh** | marketing, bán hàng, quản lý, khởi nghiệp |
| 8 | **Sáng tạo** | viết truyện, làm thơ, thiết kế, âm nhạc |
| 9 | **Học tập** | giải thích, hướng dẫn, luyện tập, kiểm tra |
| 10 | **Tra cứu** | định nghĩa, so sánh, lịch sử, tin tức |
| 11 | **Kỹ thuật** | điện, cơ khí, xây dựng, ô tô, điện tử |
| 12 | **Luật - Hành chính** | luật, hợp đồng, thủ tục, thuế, bảo hiểm |

---

## 🚀 Cài đặt

### Yêu cầu
- Python 3.10+
- Tài khoản MongoDB Atlas (free)
- Tài khoản Render (free)
- API key model: Groq / OpenRouter / Gemini (free)
- API key tra web: SERPJET / Tavily / Bright Data (free)

### Cài đặt local

```bash
# 1. Clone repo
git clone https://github.com/your-username/rong-than.git
cd rong-than

# 2. Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# 3. Cài thư viện
pip install -r yeu_cau.txt

# 4. Sinh cây quyết định (lần đầu)
python du_lieu/sinh_cay.py

# 5. Chạy server
python khoi_dong.py
```

Mở trình duyệt: http://localhost:5000

Deploy lên Render

1. Đẩy code lên GitHub.
2. Vào Render Dashboard → New Web Service.
3. Kết nối repo GitHub.
4. Cấu hình:
   · Runtime: Python 3
   · Build Command: pip install -r yeu_cau.txt
   · Start Command: (đọc từ Procfile)
5. Bấm Deploy.

---

📝 Hướng dẫn sử dụng

Bước 1: Lấy API key

Groq: https://console.groq.com/keys
OpenRouter: https://openrouter.ai/keys
Gemini: https://ai.dev
SERPJET: https://serpjet.io
Tavily: https://tavily.com
Bright Data: https://brightdata.com

Bước 2: Dán key vào giao diện

1. Mở web Rồng Thần.
2. Bấm ☰ (menu trái) → Cài đặt → Key.
3. Dán API key model (Groq/OpenRouter/Gemini) → Run.
4. Dán API key tra web (SERPJET/Tavily/Bright Data) → Run.
5. Dán URI 2 kho MongoDB → Run.

Bước 3: Dùng

Gõ task vào ô chat → bấm ➤ để gửi.

Ví dụ:

· Tính 2 + 3
· Làm web bán hàng
· Viết hàm Python tính giai thừa
· Sửa lỗi NameError này giúp mình
· Giá vàng hôm nay bao nhiêu?

---

📂 Cấu trúc thư mục

```
rong_than/
├── khoi_dong.py              # File khởi động chính
├── cau_hinh.py               # Cấu hình trung tâm
├── yeu_cau.txt               # Thư viện cần cài
├── Procfile                  # Cấu hình deploy Render
├── .gitignore                # Bỏ qua file không đẩy GitHub
├── README.md                 # File này
│
├── dai_nao/                  # Đại não (25 file)
├── tieu_nao/                 # Tiểu não (15 file)
├── tra_web/                  # Tra web (11 file)
├── sanbox/                   # Sandbox (5 file + giao diện)
├── giao_dien/                # Giao diện (30 file)
├── logs/                     # Logs (4 file)
├── du_lieu/                  # Dữ liệu local
├── kiem_thu/                 # Kiểm thử
└── tai_lieu/                 # Tài liệu
```

---

🔧 Công nghệ

Thành phần Công nghệ
Backend Python 3.10+, Flask
Database MongoDB Atlas (2 kho free)
Sandbox LiveCodes + Pyodide
Model API Groq, OpenRouter, Gemini
Tra web API SERPJET, Tavily, Bright Data
Deploy Render (free tier)
Keep-alive UptimeRobot (ping 5 phút)
Font-end HTML, CSS, JavaScript thuần

---

📊 Quota free tier

Dịch vụ Giới hạn
MongoDB Atlas 512MB/kho
Render 750 giờ/tháng, ngủ sau 15 phút
Groq 30 RPM, 1.000 RPD
OpenRouter 20 RPM, 50 RPD (free)
Gemini RPM/RPD theo model
SERPJET 1.000 lượt/tháng
Tavily 1.000 credit/tháng
Bright Data 5.000 credit/tháng

---

🎓 Cách Rồng Thần học

1. Nhận task từ người dùng.
2. Chuẩn hóa input (10 bước).
3. Trích xuất 5 yếu tố: hành động, đối tượng, thuộc tính, ràng buộc, ngữ cảnh.
4. Phân loại task vào 12 lĩnh vực.
5. Duyệt cây quyết định.
6. Chấm điểm nhánh.
7. Thực thi nhánh tốt nhất.
8. Nếu bí → gọi Tiểu não sinh nhánh mới.
9. Lưu nhánh vào cây.
10. Lần sau gặp task tương tự → dùng luôn, không cần model.

Kết quả: Càng dùng, càng ít phụ thuộc API, càng thông minh.

---

🐛 Xử lý sự cố

Server không khởi động

· Kiểm tra log Render.
· Đảm bảo đã dán URI 2 kho MongoDB.
· Đảm bảo yeu_cau.txt có đủ thư viện.

Không gọi được model

· Kiểm tra API key đã dán chưa.
· Kiểm tra quota còn không.
· Xem log Tiểu não.

Không tra web được

· Kiểm tra API key tra web.
· Kiểm tra quota tháng.
· Xem log Tra web.

Sandbox không chạy

· Kiểm tra kết nối internet.
· Đảm bảo LiveCodes CDN không bị chặn.
· Xem console trình duyệt (F12).

---

📄 License

MIT License — Xem file LICENSE để biết thêm.

---

🙏 Cảm ơn

· Flask — Web framework
· MongoDB Atlas — Database
· LiveCodes — Sandbox
· Pyodide — Python trong trình duyệt
· Groq / OpenRouter / Google Gemini — Model API
· SERPJET / Tavily / Bright Data — Web search API

---

<div align="center">

🌕🐉 Nói điều ước đi 🔥🐉

Made with ❤️ in Vietnam

</div>
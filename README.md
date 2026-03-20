# 🏆 CodePTITclone — Online Judge System

Hệ thống chấm bài tự động (Online Judge) dành cho sinh viên PTIT luyện tập lập trình.  
**Live Demo:** [codeptit-emt0147.onrender.com](https://codeptit-emt0147.onrender.com)

---

## ✨ Tính năng chính

### 👩‍💻 Người dùng
- **Giao diện kiểu LeetCode** — Code editor tích hợp (CodeMirror) với syntax highlighting, auto-save, chọn theme
- **Nộp bài & Chấm tự động** — Hỗ trợ **Python 3**, **C++ 17**, **C** với giới hạn thời gian/bộ nhớ riêng cho từng bài
- **Chấm song song** — Các test case được chấm đồng thời bằng multi-threading, giảm đáng kể thời gian chờ
- **Kết quả real-time** — Tự động cập nhật trạng thái từng test case mà không cần reload trang
- **Phân loại theo Môn học** — 6 danh mục: C++, Tin học CS2, DSA, OOP, Python, Thuật toán nâng cao
- **Phân chia dạng bài** — Mỗi môn có các sub-categories giúp lọc bài theo chủ đề
- **Tìm kiếm & Lọc** — Theo mã bài, tên bài, độ khó (Easy/Medium/Hard)
- **Bảng xếp hạng** — Top 100 người dùng theo số bài AC
- **Ghi nhớ phân trang** — Hệ thống nhớ trang bạn đang xem, quay lại đúng vị trí

### 🔑 Quản trị (Admin)
- **Quản lý bài tập** — Thêm bài mới với mô tả Markdown, điều chỉnh time/memory limit
- **Quản lý Test Cases** — Thêm/sửa/xóa từng test case, thêm hàng loạt (bulk) qua paste hoặc JSON
- **Tự sinh Test Case** — Viết script generator + solution, hệ thống tự chạy và lưu kết quả
- **AI sinh Test Case** — Tích hợp Gemini AI để tự động tạo generator và solution từ đề bài
- **Import từ PDF** — Trích xuất hàng loạt bài tập từ file PDF theo format chuẩn

---

## 🚀 Cài đặt & Chạy (Local)

### 1. Clone & cài dependencies

```bash
git clone https://github.com/emt0147t/codeptit.emt0147.git
cd codeptit.emt0147
pip install -r requirements.txt
```

### 2. Khởi tạo Database

```bash
python init_db.py
```

Tạo database SQLite, tài khoản admin (`admin`/`admin123`) và import bài tập mẫu.

### 3. Chạy server

```bash
python main.py
```

Truy cập: **http://localhost:8000**

---

## 🌐 Deploy lên Render

1. Push code lên GitHub
2. Tạo **Web Service** trên [render.com](https://render.com)
3. Thiết lập:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run_online.py`
4. Thêm Environment Variables:
   - `DATABASE_URL` — PostgreSQL connection string (dùng Supabase hoặc Render Postgres)
   - `SECRET_KEY` — Khóa bí mật cho session
   - `GEMINI_API_KEY` — *(tùy chọn)* API key để dùng chức năng AI sinh test case

---

## 📁 Cấu trúc Project

```
├── main.py                  # FastAPI entry point
├── run_online.py            # Production startup (Render)
├── config.py                # Cấu hình hệ thống, danh mục môn học
├── database.py              # Database engine setup (SQLite / PostgreSQL)
├── models.py                # SQLAlchemy models (Problem, Submission, TestCase, User, SubmissionResult)
├── init_db.py               # Khởi tạo DB, admin, import bài tập
├── Dockerfile               # Docker deployment
├── render.yaml              # Render deploy config
│
├── routers/
│   ├── auth.py              # Đăng nhập, đăng ký, phân quyền
│   ├── problems.py          # CRUD bài tập, test cases, AI generation
│   └── submissions.py       # Nộp bài, kết quả, bảng xếp hạng
│
├── judge/
│   └── executor.py          # Engine chấm bài (compile + run + compare, multi-threaded)
│
├── templates/               # Jinja2 HTML (Tailwind CSS)
│   ├── base.html            # Layout chính, navbar, dropdown môn học
│   ├── index.html            # Trang chủ
│   ├── problems.html        # Danh sách bài tập
│   ├── problem_detail.html  # Chi tiết bài + Code editor (LeetCode-style)
│   ├── submission_detail.html # Kết quả chấm bài real-time
│   ├── submissions.html     # Lịch sử bài nộp
│   ├── ranking.html         # Bảng xếp hạng
│   ├── login.html / register.html
│   └── admin/
│       ├── add_problem.html     # Form thêm bài
│       ├── testcases.html       # Quản lý test cases (manual/bulk/AI)
│       └── edit_testcase.html   # Chỉnh sửa test case
│
├── tools/
│   ├── pdf_parser.py            # Import bài tập từ PDF
│   ├── testcase_runner.py       # Chạy generator + solution để sinh test
│   ├── auto_testcase_gen.py     # AI sinh test case tự động (Gemini)
│   ├── import_readme.py         # Import bài từ README
│   └── ...                      # Các script phân tích, kiểm tra khác
│
└── static/                  # Assets tĩnh (logo, CSS)
```

---

## 🛠️ Tech Stack

| Thành phần | Công nghệ |
|-----------|-----------|
| Backend | **FastAPI** (Python 3.10+) |
| Database | **SQLite** (local) / **PostgreSQL** (production) |
| ORM | **SQLAlchemy** |
| Frontend | **Jinja2** + **Tailwind CSS** + **CodeMirror** |
| Judge Engine | **subprocess** + **ThreadPoolExecutor** |
| AI | **Google Gemini API** (tùy chọn) |
| Deploy | **Render** / **Docker** |

## 🗣️ Ngôn ngữ chấm bài

| Ngôn ngữ | Compiler/Runtime | Phiên bản |
|-----------|-----------|-----------|
| Python 3 | `python` | 3.8+ |
| C++ 17 | `g++` | GCC / MinGW |
| C | `gcc` | GCC / MinGW |

---

## ⚠️ Lưu ý bảo mật

Hệ thống được thiết kế cho **sử dụng cá nhân/nhóm nhỏ**.  
Nếu triển khai public, cần bổ sung:
- Docker sandbox cho code execution
- HTTPS
- Đổi `SECRET_KEY` trong environment variables

---

## 📜 License

MIT License — Sử dụng tự do cho mục đích học tập.

"""
Configuration for the Online Judge system.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

import urllib.parse

# Database Configuration
env_db_url = os.getenv("DATABASE_URL")

if env_db_url:
    # Render/Supabase use postgres://, SQLAlchemy requires postgresql://
    if env_db_url.startswith("postgres://"):
        env_db_url = env_db_url.replace("postgres://", "postgresql://", 1)
    
    # Simple timeout additions
    if "?" not in env_db_url:
        env_db_url += "?connect_timeout=30"
    else:
        env_db_url += "&connect_timeout=30"
        
    DATABASE_URL = env_db_url
else:
    # 2. Render Free Tier fallback
    if os.path.exists("/data"):
        DATABASE_URL = "sqlite:////data/online_judge.db"
    # 3. Default: Local SQLite for development
    else:
        DATABASE_URL = f"sqlite:///{BASE_DIR / 'online_judge.db'}"

# Secret key for session
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-2024")

# Judge settings
JUDGE_TIMEOUT = 5
JUDGE_MEMORY_LIMIT = 256
SUPPORTED_LANGUAGES = {
    "python": {"name": "Python 3", "extension": ".py", "compile_cmd": None, "run_cmd": "python {source}"},
    "cpp": {"name": "C++ 17", "extension": ".cpp", "compile_cmd": "g++ -std=c++17 -O2 -o {output} {source}", "run_cmd": "{output}"},
    "c": {"name": "C", "extension": ".c", "compile_cmd": "gcc -std=c11 -O2 -o {output} {source}", "run_cmd": "{output}"},
}

TESTCASE_DIR = BASE_DIR / "testcases"
PROBLEMS_PER_PAGE = 20
SUBMISSIONS_PER_PAGE = 20

# Categories (slug -> display info)
CATEGORIES = {
    "ngon-ngu-lap-trinh-cpp": {"name": "Ngôn ngữ lập trình C++", "short": "C++", "color": "blue", "description": "Lập trình cơ bản đến nâng cao với C++"},
    "tin-hoc-co-so-2": {"name": "Tin học cơ sở 2", "short": "THCS2", "color": "green", "description": "Bài tập môn Tin học cơ sở 2"},
    "cau-truc-du-lieu-giai-thuat": {"name": "Cấu trúc dữ liệu và giải thuật (DSA)", "short": "DSA", "color": "purple", "description": "Thuật toán sinh, sắp xếp, tìm kiếm"},
    "lap-trinh-huong-doi-tuong": {"name": "Lập trình hướng đối tượng", "short": "OOP", "color": "orange", "description": "Lập trình OOP với Java"},
    "lap-trinh-voi-python": {"name": "Lập trình với Python", "short": "Python", "color": "yellow", "description": "Lập trình Python từ cơ bản đến nâng cao"},
    "thuat-toan-nang-cao": {"name": "Thuật toán nâng cao - 2024", "short": "Advanced", "color": "red", "description": "Đồ thị, quy hoạch động, nâng cao"},
}

SUB_CATEGORIES = {
    "tin-hoc-co-so-2": [
        {"prefix": "C01", "name": "Cơ bản"}, {"prefix": "C02", "name": "Vòng lặp"}, {"prefix": "C03", "name": "Mảng 1 chiều"},
        {"prefix": "C04", "name": "Mảng 2 chiều"}, {"prefix": "C05", "name": "Xâu ký tự"}, {"prefix": "C06", "name": "Cấu trúc"},
        {"prefix": "C07", "name": "File"}, {"prefix": "CTEST", "name": "Bài kiểm tra"}, {"prefix": "LAB", "name": "Thực hành"},
        {"prefix": "TEST", "name": "Luyện tập"},
    ],
    "ngon-ngu-lap-trinh-cpp": [
        {"prefix": "CPP01", "name": "Cơ bản"}, {"prefix": "CPP02", "name": "Mảng 1 chiều"}, {"prefix": "CPP03", "name": "Xâu ký tự"},
        {"prefix": "CPP04", "name": "Mảng 2 chiều"}, {"prefix": "CPP05", "name": "Cấu trúc"}, {"prefix": "CPP06", "name": "Lớp và đối tượng"},
        {"prefix": "CPP07", "name": "Lớp và đối tượng (Nâng cao)"}, {"prefix": "CPP08", "name": "File"},
        {"prefix": "CHELLO", "name": "Hello World"}, {"prefix": "OLP", "name": "Olympic"},
    ],
    "cau-truc-du-lieu-giai-thuat": [
        {"prefix": "DSA01", "name": "Sinh kế tiếp"}, {"prefix": "DSA02", "name": "Quay lui - Nhánh cận"}, {"prefix": "DSA03", "name": "Tham lam"},
        {"prefix": "DSA04", "name": "Chia và trị"}, {"prefix": "DSA05", "name": "Quy hoạch động"}, {"prefix": "DSA06", "name": "Sắp xếp - Tìm kiếm"},
        {"prefix": "DSA07", "name": "Ngăn xếp"}, {"prefix": "DSA08", "name": "Hàng đợi"}, {"prefix": "DSA09", "name": "Đồ thị"},
        {"prefix": "DSA10", "name": "Cây"}, {"prefix": "DSA11", "name": "Cây nhị phân"}, {"prefix": "DSAKT", "name": "Kiểm tra"},
        {"prefix": "CTDL", "name": "Cấu trúc dữ liệu"},
    ],
    "lap-trinh-huong-doi-tuong": [
        {"prefix": "J01", "name": "Cơ bản"}, {"prefix": "J02", "name": "Mảng"}, {"prefix": "J03", "name": "Xâu ký tự"},
        {"prefix": "J04", "name": "Lớp và đối tượng"}, {"prefix": "J05", "name": "Sắp xếp danh sách"}, {"prefix": "J06", "name": "Kế thừa đa hình"},
        {"prefix": "J07", "name": "Vào ra File"}, {"prefix": "J08", "name": "Collections"}, {"prefix": "JKT", "name": "Kiểm tra"},
        {"prefix": "TN", "name": "Luyện tập"}, {"prefix": "HELLO", "name": "Xin chào"},
    ],
    "lap-trinh-voi-python": [
        {"prefix": "PY01", "name": "Cơ bản"}, {"prefix": "PY02", "name": "Cấu trúc dữ liệu"}, {"prefix": "PY03", "name": "Hàm và Module"},
        {"prefix": "PY04", "name": "Lớp và đối tượng"}, {"prefix": "PYKT", "name": "Kiểm tra"}, {"prefix": "ICPC", "name": "Luyện tập ICPC"},
    ],
    "thuat-toan-nang-cao": [
        {"prefix": "CP01", "name": "Quy hoạch động"}, {"prefix": "CP02", "name": "Đồ thị nâng cao"}, {"prefix": "CP03", "name": "Toán học / Hình học"},
        {"prefix": "CP04", "name": "Cấu trúc dữ liệu nâng cao"}, {"prefix": "S0", "name": "Thực hành quy hoạch động"},
        {"prefix": "S1", "name": "Thực hành đồ thị"}, {"prefix": "S2", "name": "Hình học nâng cao"}, {"prefix": "S3", "name": "Bài toán tối ưu"},
    ]
}

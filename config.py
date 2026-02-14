"""
Configuration for the Online Judge system.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_URL = f"sqlite:///{BASE_DIR / 'online_judge.db'}"

# Secret key for session
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-2024")

# Judge settings
JUDGE_TIMEOUT = 5  # seconds per test case
JUDGE_MEMORY_LIMIT = 256  # MB
SUPPORTED_LANGUAGES = {
    "python": {
        "name": "Python 3",
        "extension": ".py",
        "compile_cmd": None,
        "run_cmd": "python {source}",
    },
    "cpp": {
        "name": "C++ 17",
        "extension": ".cpp",
        "compile_cmd": "g++ -std=c++17 -O2 -o {output} {source}",
        "run_cmd": "{output}",
    },
    "c": {
        "name": "C",
        "extension": ".c",
        "compile_cmd": "gcc -std=c11 -O2 -o {output} {source}",
        "run_cmd": "{output}",
    },
}

# Testcase directory
TESTCASE_DIR = BASE_DIR / "testcases"

# Pagination
PROBLEMS_PER_PAGE = 20
SUBMISSIONS_PER_PAGE = 20

# Categories (slug -> display info)
CATEGORIES = {
    "ngon-ngu-lap-trinh-cpp": {
        "name": "Ngôn ngữ lập trình C++",
        "short": "C++",
        "icon": "💻",
        "color": "blue",
        "description": "Các bài tập lập trình cơ bản đến nâng cao với C++",
    },
    "tin-hoc-co-so-2": {
        "name": "Tin học cơ sở 2",
        "short": "THCS2",
        "icon": "📘",
        "color": "green",
        "description": "Bài tập môn Tin học cơ sở 2",
    },
    "cau-truc-du-lieu-giai-thuat": {
        "name": "Cấu trúc dữ liệu và giải thuật (DSA)",
        "short": "DSA",
        "icon": "🧩",
        "color": "purple",
        "description": "Cấu trúc dữ liệu, thuật toán sinh, sắp xếp, tìm kiếm",
    },
    "lap-trinh-huong-doi-tuong": {
        "name": "Lập trình hướng đối tượng",
        "short": "OOP",
        "icon": "☕",
        "color": "orange",
        "description": "Lập trình OOP với Java",
    },
    "lap-trinh-voi-python": {
        "name": "Lập trình với Python",
        "short": "Python",
        "icon": "🐍",
        "color": "yellow",
        "description": "Lập trình Python từ cơ bản đến nâng cao",
    },
    "thuat-toan-nang-cao": {
        "name": "Thuật toán nâng cao - 2024",
        "short": "Advanced",
        "icon": "🏆",
        "color": "red",
        "description": "Thuật toán đồ thị, quy hoạch động, nâng cao",
    },
}

# Map from source folder name to slug
CATEGORY_FOLDER_MAP = {
    "Ngôn ngữ lập trình C++": "ngon-ngu-lap-trinh-cpp",
    "Tin học cơ sở 2": "tin-hoc-co-so-2",
    "Cấu trúc dữ liệu và giải thuật (DSA)": "cau-truc-du-lieu-giai-thuat",
    "Lập trình hướng đối tượng": "lap-trinh-huong-doi-tuong",
    "Lập trình với Python": "lap-trinh-voi-python",
    "Thuật toán nâng cao - 2024": "thuat-toan-nang-cao",
}

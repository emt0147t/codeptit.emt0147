"""
Configuration for the Online Judge system.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database Configuration
# 1. First priority: Use custom PostgreSQL URI if provided in environment (e.g. Supabase, Render, Neon)
env_db_url = os.getenv("DATABASE_URL")
if env_db_url:
    parts = env_db_url.split("://", 1)
    if len(parts) == 2:
        scheme, remainder = parts
        scheme = "postgresql" # Force postgresql dialect
        if "@" in remainder:
            credentials, rest = remainder.split("@", 1)
            if ":" in credentials:
                user, pwd = credentials.split(":", 1)
                user = user.replace(".", "%2E")  # Fix Supabase pooler username parsing bug
                env_db_url = f"{scheme}://{user}:{pwd}@{rest}"
            else:
                user = credentials.replace(".", "%2E")
                env_db_url = f"{scheme}://{user}@{rest}"
        else:
            env_db_url = f"{scheme}://{remainder}"
    DATABASE_URL = env_db_url
# 2. Render Free Tier fallback: Persistent disks are currently unsupported on free tier. 
# Leaving /data logic here as a premium backup.
elif os.path.exists("/data"):
    DATABASE_URL = "sqlite:////data/online_judge.db"
# 3. Default: Local SQLite for development
else:
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
        "icon": '<svg class="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>',
        "color": "blue",
        "description": "Các bài tập lập trình cơ bản đến nâng cao với C++",
    },
    "tin-hoc-co-so-2": {
        "name": "Tin học cơ sở 2",
        "short": "THCS2",
        "icon": '<svg class="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>',
        "color": "green",
        "description": "Bài tập môn Tin học cơ sở 2",
    },
    "cau-truc-du-lieu-giai-thuat": {
        "name": "Cấu trúc dữ liệu và giải thuật (DSA)",
        "short": "DSA",
        "icon": '<svg class="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"/></svg>',
        "color": "purple",
        "description": "Cấu trúc dữ liệu, thuật toán sinh, sắp xếp, tìm kiếm",
    },
    "lap-trinh-huong-doi-tuong": {
        "name": "Lập trình hướng đối tượng",
        "short": "OOP",
        "icon": '<svg class="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v1a2 2 0 01-2 2H5a2 2 0 01-2-2v-1a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>',
        "color": "orange",
        "description": "Lập trình OOP với Java",
    },
    "lap-trinh-voi-python": {
        "name": "Lập trình với Python",
        "short": "Python",
        "icon": '<svg class="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
        "color": "yellow",
        "description": "Lập trình Python từ cơ bản đến nâng cao",
    },
    "thuat-toan-nang-cao": {
        "name": "Thuật toán nâng cao - 2024",
        "short": "Advanced",
        "icon": '<svg class="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/></svg>',
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

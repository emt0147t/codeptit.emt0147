"""
Initialize the database and create an admin account.
Run this once before starting the server.

Usage:
    python init_db.py
"""
from database import init_db, SessionLocal
from models import User
import bcrypt as _bcrypt


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')


def create_admin():
    """Create default admin user."""
    db = SessionLocal()

    existing = db.query(User).filter(User.username == "admin").first()
    if existing:
        print("Admin account already exists.")
        db.close()
        return

    admin = User(
        username="admin",
        email="admin@onlinejudge.local",
        password_hash=hash_password("admin123"),
        is_admin=True
    )
    db.add(admin)
    db.commit()
    print("✅ Admin account created!")
    print("   Username: admin")
    print("   Password: admin123")
    print("   (Hãy đổi mật khẩu sau khi đăng nhập)")
    db.close()


def add_sample_problems():
    """Add some sample problems for testing."""
    from models import Problem, TestCase

    db = SessionLocal()

    # Check if problems already exist
    if db.query(Problem).count() > 0:
        print("Database already has problems. Skipping samples.")
        db.close()
        return

    sample_problems = [
        {
            "code": "CPP0101",
            "title": "Tính tổng 1 đến N",
            "description": "Cho số nguyên dương N.\nHãy tính S = 1 + 2 + ... + N",
            "input_description": "Dòng đầu ghi số bộ test, không quá 10\nMỗi dòng ghi một số nguyên dương N, không quá 10^9",
            "output_description": "Với mỗi test, ghi kết quả trên một dòng.",
            "sample_input": "2\n10\n20",
            "sample_output": "55\n210",
            "difficulty": "Easy",
            "time_limit": 1.0,
            "testcases": [
                {"input": "2\n10\n20", "output": "55\n210", "is_sample": True},
                {"input": "3\n1\n100\n1000", "output": "1\n5050\n500500", "is_sample": False},
                {"input": "1\n1000000000", "output": "500000000500000000", "is_sample": False},
            ]
        },
        {
            "code": "CPP0102",
            "title": "Số chẵn hay lẻ",
            "description": "Cho số nguyên N. Hãy kiểm tra N là số chẵn hay số lẻ.",
            "input_description": "Một dòng chứa số nguyên N (|N| ≤ 10^9)",
            "output_description": "In ra 'Even' nếu N chẵn, 'Odd' nếu N lẻ.",
            "sample_input": "4",
            "sample_output": "Even",
            "difficulty": "Easy",
            "time_limit": 1.0,
            "testcases": [
                {"input": "4", "output": "Even", "is_sample": True},
                {"input": "7", "output": "Odd", "is_sample": False},
                {"input": "0", "output": "Even", "is_sample": False},
                {"input": "-3", "output": "Odd", "is_sample": False},
            ]
        },
        {
            "code": "CPP0103",
            "title": "Tính giai thừa",
            "description": "Cho số nguyên dương N (N ≤ 20). Hãy tính N! = 1 × 2 × 3 × ... × N.",
            "input_description": "Một dòng chứa số nguyên dương N (1 ≤ N ≤ 20)",
            "output_description": "In ra giá trị N!",
            "sample_input": "5",
            "sample_output": "120",
            "difficulty": "Easy",
            "time_limit": 1.0,
            "testcases": [
                {"input": "5", "output": "120", "is_sample": True},
                {"input": "1", "output": "1", "is_sample": False},
                {"input": "10", "output": "3628800", "is_sample": False},
                {"input": "20", "output": "2432902008176640000", "is_sample": False},
            ]
        },
    ]

    for p_data in sample_problems:
        problem = Problem(
            code=p_data["code"],
            title=p_data["title"],
            description=p_data["description"],
            input_description=p_data["input_description"],
            output_description=p_data["output_description"],
            sample_input=p_data["sample_input"],
            sample_output=p_data["sample_output"],
            difficulty=p_data["difficulty"],
            time_limit=p_data["time_limit"],
        )
        db.add(problem)
        db.commit()
        db.refresh(problem)

        for tc_data in p_data["testcases"]:
            tc = TestCase(
                problem_id=problem.id,
                input_data=tc_data["input"],
                expected_output=tc_data["output"],
                is_sample=tc_data["is_sample"],
                order=0
            )
            db.add(tc)

        db.commit()
        print(f"  ✅ {p_data['code']} - {p_data['title']}")

    db.close()
    print(f"\n✅ Added {len(sample_problems)} sample problems")


if __name__ == "__main__":
    print("🔧 Initializing database...")
    init_db()
    print("✅ Database tables created\n")

    print("👤 Creating admin account...")
    create_admin()

    print("\n📋 Adding sample problems...")
    add_sample_problems()

    print("\n🎉 Setup complete! Run the server with:")
    print("   python main.py")

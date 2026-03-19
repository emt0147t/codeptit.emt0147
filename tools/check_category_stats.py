import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from database import SessionLocal
from models import Problem, TestCase

def check_stats():
    db = SessionLocal()
    CATEGORY_SLUG = "tin-hoc-co-so-2"
    problems = db.query(Problem).filter(Problem.category == CATEGORY_SLUG).all()
    
    total_problems = len(problems)
    done_problems = 0
    partial_problems = 0
    zero_problems = 0
    
    results = []
    
    for p in problems:
        count = db.query(TestCase).filter(TestCase.problem_id == p.id).count()
        if count >= 10:
            done_problems += 1
        elif count > 0:
            partial_problems += 1
            results.append(f"{p.code}({count})")
        else:
            zero_problems += 1
            results.append(f"{p.code}(0)")
            
    print(f"Total problems in category: {total_problems}")
    print(f"Problems with >= 10 testcases: {done_problems}")
    print(f"Problems with 1-9 testcases: {partial_problems}")
    print(f"Problems with 0 testcases: {zero_problems}")
    print(f"Total testcases: {db.query(TestCase).join(Problem).filter(Problem.category == CATEGORY_SLUG).count()}")
    
    if results:
        print("\nSome problems missing testcases:")
        print(", ".join(results[:30]))
    
    db.close()

if __name__ == "__main__":
    check_stats()

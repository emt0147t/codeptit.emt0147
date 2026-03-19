import os
import sys
import psycopg2

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from database import SessionLocal as LocalSession
from models import Problem, TestCase

# Supabase URL - Exactly as provided by user
DB_HOST = "aws-1-ap-northeast-1.pooler.supabase.com"
DB_PORT = 6543
DB_NAME = "postgres"
DB_USER = "postgres.isbbxkdjdnrggezwdkbz"
DB_PASS = "0yBXkSzodsyT01C6"

def sync_psycopg2():
    print("Initializing Debug Synchronization (Fix Syntax)...")
    
    local_db = LocalSession()
    CATEGORY_SLUG = "tin-hoc-co-so-2"
    
    try:
        # Load local problems
        local_problems = local_db.query(Problem).filter(Problem.category == CATEGORY_SLUG).all()
        print(f"Found {len(local_problems)} local problems.")
        
        # Connect to remote via direct parameters
        remote_conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            sslmode="require"
        )
        remote_cur = remote_conn.cursor()
        
        # Load remote problem map
        remote_cur.execute("SELECT id, code FROM problems")
        remote_map = {code: pid for pid, code in remote_cur.fetchall()}
        
        synced_count = 0
        problem_count = 0
        
        for lp in local_problems:
            if lp.code not in remote_map:
                continue
            
            remote_p_id = remote_map[lp.code]
            local_tcs = local_db.query(TestCase).filter(TestCase.problem_id == lp.id).all()
            if not local_tcs:
                continue
            
            print(f"  Syncing {lp.code} ({len(local_tcs)} TCs)...", end=" ", flush=True)
            
            try:
                # 1. Check current TCs and their child counts
                remote_cur.execute("SELECT id FROM testcases WHERE problem_id = %s", (remote_p_id,))
                tc_ids = [row[0] for row in remote_cur.fetchall()]
                
                total_child_count = 0
                for tid in tc_ids:
                    remote_cur.execute("SELECT count(*) FROM submission_results WHERE testcase_id = %s", (tid,))
                    total_child_count += remote_cur.fetchone()[0]
                
                print(f"(Found {len(tc_ids)} TCs, {total_child_count} children)...", end=" ")
                
                # 2. DELETE Submission Results
                remote_cur.execute(
                    "DELETE FROM submission_results WHERE testcase_id IN (SELECT id FROM testcases WHERE problem_id = %s)",
                    (remote_p_id,)
                )
                del_results = remote_cur.rowcount
                remote_conn.commit()
                
                # 3. DELETE Testcases
                remote_cur.execute("DELETE FROM testcases WHERE problem_id = %s", (remote_p_id,))
                del_tcs = remote_cur.rowcount
                remote_conn.commit()
                
                # 5. INSERT New Testcases
                for tc in local_tcs:
                    remote_cur.execute(
                        'INSERT INTO testcases (problem_id, input_data, expected_output, is_sample, "order") VALUES (%s, %s, %s, %s, %s)',
                        (remote_p_id, tc.input_data, tc.expected_output, bool(tc.is_sample), int(tc.order) if tc.order is not None else 0)
                    )
                
                remote_conn.commit()
                synced_count += len(local_tcs)
                problem_count += 1
                print(f"Done (Deleted {del_tcs} TCs, {del_results} SRs).")
            except Exception as e:
                remote_conn.rollback()
                print(f"Failed! Error: {e}")
                # CONTINUE with next problem
                continue
                
        remote_cur.close()
        remote_conn.close()
        print(f"\nFinal SUCCESS! Problems: {problem_count}, Testcases: {synced_count}")
        
    except Exception as e:
        print(f"\nFatal Error: {e}")
    finally:
        local_db.close()

if __name__ == "__main__":
    sync_psycopg2()

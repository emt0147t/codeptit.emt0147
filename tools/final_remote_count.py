import sys
import psycopg2

# Supabase URL directly
RAW_URL = "postgresql://postgres.isbbxkdjdnrggezwdkbz:0yBXkSzodsyT01C6@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def final_count():
    try:
        conn = psycopg2.connect(RAW_URL)
        cur = conn.cursor()
        
        # Count all testcases in the specific category
        query = """
            SELECT count(tc.id) 
            FROM testcases tc 
            JOIN problems p ON tc.problem_id = p.id 
            WHERE p.category = 'tin-hoc-co-so-2'
        """
        cur.execute(query)
        cnt = cur.fetchone()[0]
        
        print(f"REPORT: Total Testcases for 'tin-hoc-co-so-2' on Supabase = {cnt}")
        
        # Also check top 5 problems to see if they have 10+
        cur.execute("""
            SELECT p.code, count(tc.id) 
            FROM testcases tc 
            JOIN problems p ON tc.problem_id = p.id 
            WHERE p.category = 'tin-hoc-co-so-2'
            GROUP BY p.code
            ORDER BY count(tc.id) DESC
            LIMIT 10
        """)
        print("\nTop synchronized problems:")
        for code, c in cur.fetchall():
            print(f"  {code}: {c} testcases")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_count()

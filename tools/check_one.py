import psycopg2

RAW_URL = "postgresql://postgres.isbbxkdjdnrggezwdkbz:0yBXkSzodsyT01C6@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def check_one():
    conn = psycopg2.connect(RAW_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT id FROM problems WHERE code = 'C01014'")
    remote_id = cur.fetchone()[0]
    
    cur.execute("SELECT count(*) FROM testcases WHERE problem_id = %s", (remote_id,))
    count = cur.fetchone()[0]
    
    print(f"Problem C01014 (ID {remote_id}) has {count} testcases on Supabase.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_one()

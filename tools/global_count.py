import psycopg2

RAW_URL = "postgresql://postgres.isbbxkdjdnrggezwdkbz:0yBXkSzodsyT01C6@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def global_count():
    conn = psycopg2.connect(RAW_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT count(*) FROM testcases")
    count = cur.fetchone()[0]
    
    print(f"GLOBAL Total Testcases on Supabase: {count}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    global_count()

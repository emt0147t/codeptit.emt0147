import psycopg2

RAW_URL = "postgresql://postgres.isbbxkdjdnrggezwdkbz:0yBXkSzodsyT01C6@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def check_categories():
    conn = psycopg2.connect(RAW_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT category, count(*) FROM problems GROUP BY category")
    results = cur.fetchall()
    
    print("Categories on Supabase:")
    for cat, count in results:
        print(f"  '{cat}': {count} problems")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_categories()

import psycopg2

RAW_URL = "postgresql://postgres.isbbxkdjdnrggezwdkbz:0yBXkSzodsyT01C6@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def check_duplicates():
    conn = psycopg2.connect(RAW_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT code, count(*), array_agg(id) FROM problems GROUP BY code HAVING count(*) > 1")
    dupes = cur.fetchall()
    
    if dupes:
        print(f"Found {len(dupes)} duplicate problem codes:")
        for code, count, ids in dupes:
            print(f"  {code}: {count} occurrences (IDs: {ids})")
    else:
        print("No duplicate problem codes found.")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_duplicates()

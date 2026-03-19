import psycopg2

RAW_URL = "postgresql://postgres.isbbxkdjdnrggezwdkbz:0yBXkSzodsyT01C6@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def check_fks():
    conn = psycopg2.connect(RAW_URL)
    cur = conn.cursor()
    
    # Query to find all foreign keys pointing to 'testcases'
    query = """
        SELECT
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND ccu.table_name='testcases';
    """
    cur.execute(query)
    results = cur.fetchall()
    
    print("Tables referencing 'testcases':")
    for row in results:
        print(f"  {row[0]}.{row[1]} -> {row[2]}.{row[3]}")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_fks()

from database import get_connection

conn = get_connection()
if conn:
    print("✅ Connected successfully!")
    cur = conn.cursor()
    cur.execute("SHOW TABLES;")
    for row in cur.fetchall():
        print(row)
    conn.close()
else:
    print("❌ Connection failed")

import sqlite3
import os

db_path = 'data/nongsan_v2.sqlite3'
if not os.path.exists(db_path):
    db_path = 'nongsan_v2.sqlite3'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT username, email FROM users WHERE username='admin'")
row = cursor.fetchone()
if row:
    print(f"User: {row[0]}, Email: {row[1]}")
else:
    print("Không tìm thấy tài khoản admin")
conn.close()

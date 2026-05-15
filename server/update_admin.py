import sqlite3
import os

db_path = 'data/nongsan_v2.sqlite3'
if not os.path.exists(db_path):
    db_path = 'nongsan_v2.sqlite3'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("UPDATE users SET email='nhumothacker@gmail.com' WHERE username='admin'")
conn.commit()
if cursor.rowcount > 0:
    print("Success: Updated Admin email to nhumothacker@gmail.com")
else:
    print("Error: Admin user not found")
conn.close()

import sqlite3
import os

db_path = 'data/nongsan_v2.sqlite3'
if not os.path.exists(db_path):
    db_path = 'nongsan_v2.sqlite3'

print(f"Connecting to database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add otp_code column
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN otp_code TEXT")
        print("Success: Added 'otp_code' column.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Info: 'otp_code' already exists.")
        else:
            print(f"Error adding 'otp_code': {e}")

    # Add otp_expiry column
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN otp_expiry DATETIME")
        print("Success: Added 'otp_expiry' column.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Info: 'otp_expiry' already exists.")
        else:
            print(f"Error adding 'otp_expiry': {e}")

    conn.commit()
    conn.close()
    print("Database migration completed.")
except Exception as e:
    print(f"General error: {e}")

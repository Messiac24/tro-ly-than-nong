import sys
import os
from pathlib import Path
import bcrypt

# Force UTF-8 encoding for standard output/error to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Thiết lập đường dẫn để tìm thấy các module trong thư mục server
BASE_DIR = Path(__file__).resolve().parent
SERVER_DIR = BASE_DIR / "server"

# Thêm SERVER_DIR vào đầu sys.path để Python tìm thấy database.py và models.py
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from server.database import SessionLocal
    from server import models
    print("Kết nối module thành công!")
except ImportError as e:
    print(f"Lỗi nạp module: {e}")
    sys.exit(1)

db = SessionLocal()
user = db.query(models.User).filter(models.User.username == "admin").first()
if user:
    is_correct = bcrypt.checkpw("123".encode('utf-8'), user.hashed_password.encode('utf-8'))
    print(f"Password '123' verification: {is_correct}")
else:
    print("User 'admin' NOT found!")
db.close()

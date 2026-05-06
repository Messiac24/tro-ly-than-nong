import sys
import os
from pathlib import Path

# Cấu hình đường dẫn tuyệt đối tới thư mục server
BASE_DIR = Path(__file__).resolve().parent
SERVER_DIR = BASE_DIR / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

try:
    try:
        from server.database import SessionLocal
        from server import models
    except ImportError:
        from database import SessionLocal
        import models
    print("Nap module database va models thanh cong!")
except ImportError as e:
    print(f"Loi nap module: {e}")
    sys.exit(1)

db = SessionLocal()
user = db.query(models.User).filter(models.User.username == "admin").first()
if user:
    print(f"User found: {user.username}, Role: {user.role}, Email: {user.email}")
else:
    print("User 'admin' NOT found!")
db.close()

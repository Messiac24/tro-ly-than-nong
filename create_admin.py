
import sys
import os
from pathlib import Path

# Đưa thư mục server vào đầu danh sách tìm kiếm của Python
# Cách này giúp script luôn tìm thấy database.py và models.py dù bà con chạy từ đâu
BASE_DIR = Path(__file__).resolve().parent
SERVER_DIR = BASE_DIR / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

# Force UTF-8 encoding for standard output/error to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')



from database import SessionLocal
import models
import bcrypt

def create_admin():
    db = SessionLocal()
    try:
        # Kiểm tra xem admin đã tồn tại chưa
        admin_username = "admin"
        admin_email = "admin@thannong.ai"
        existing_admin = db.query(models.User).filter(models.User.username == admin_username).first()
        
        if existing_admin:
            print(f"Tài khoản {admin_username} đã tồn tại. Đang cập nhật mật khẩu và quyền admin...")
            existing_admin.role = "admin"
            existing_admin.email = admin_email
            salt = bcrypt.gensalt()
            existing_admin.hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), salt).decode('utf-8')
            db.commit()
            print("Cập nhật thành công!")
        else:
            print(f"Đang tạo tài khoản admin mới: {admin_username}")
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), salt).decode('utf-8')
            
            new_admin = models.User(
                username=admin_username,
                email=admin_email,
                full_name="Administrator",
                hashed_password=hashed_password,
                role="admin",
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            print("Tạo tài khoản Admin thành công!")
            
    except Exception as e:
        print(f"Lỗi: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

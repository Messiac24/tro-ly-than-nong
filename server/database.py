from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Đường dẫn tới file SQLite bên trong thư mục server/data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Logic tìm nơi lưu trữ database có quyền ghi
def get_database_url():
    # 1. Ưu tiên biến môi trường nếu có
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    
    # 2. Thử ghi vào thư mục data local
    local_db_path = os.path.join(DATA_DIR, "nongsan_v2.sqlite3")
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        # Test quyền ghi bằng cách tạo file tạm
        test_file = os.path.join(DATA_DIR, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return f"sqlite:///{local_db_path}"
    except Exception:
        # 3. Fallback sang /tmp nếu local bị chặn (thường gặp trên Hugging Face)
        print("⚠️ Local directory is read-only, falling back to /tmp")
        return "sqlite:////tmp/nongsan_v2.sqlite3"

SQLALCHEMY_DATABASE_URL = get_database_url()
print(f"📡 Database URL: {SQLALCHEMY_DATABASE_URL}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency để lấy DB session cho mỗi request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

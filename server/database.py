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
        print(f"📡 Using database URL from environment: {env_url}")
        # Đảm bảo thư mục cha tồn tại nếu là sqlite
        if env_url.startswith("sqlite:///"):
            db_path = env_url.replace("sqlite:///", "")
            # Xử lý trường hợp 4 slashes (absolute path trên Unix)
            if db_path.startswith("/"):
                parent_dir = os.path.dirname(db_path)
                if parent_dir and not os.path.exists(parent_dir):
                    try:
                        os.makedirs(parent_dir, exist_ok=True)
                    except: pass
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
    except Exception as e:
        # 3. Fallback sang /tmp nếu local bị chặn (thường gặp trên Hugging Face)
        print(f"⚠️ Local directory {DATA_DIR} is read-only or error: {e}")
        print("🚀 Falling back to /tmp/nongsan_v2.sqlite3")
        # Đảm bảo /tmp tồn tại (thường luôn có trên Linux)
        return "sqlite:////tmp/nongsan_v2.sqlite3"

SQLALCHEMY_DATABASE_URL = get_database_url()
print(f"📡 Final Database URL: {SQLALCHEMY_DATABASE_URL}")

# Cấu hình engine với chế độ pool_pre_ping để tránh lỗi 'unable to open database' khi file bị khóa
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
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

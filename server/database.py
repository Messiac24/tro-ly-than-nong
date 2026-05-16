from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Đường dẫn tới file SQLite bên trong thư mục server/data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Logic tìm nơi lưu trữ database có quyền ghi
def get_database_url():
    # 1. Xác định đường dẫn nguồn và đích
    local_src_path = os.path.join(DATA_DIR, "nongsan_v2.sqlite3")
    env_url = os.getenv("DATABASE_URL")
    
    # 2. Xác định URL cuối cùng
    final_url = None
    
    if env_url:
        print(f"📡 Using database URL from environment: {env_url}")
        final_url = env_url
    else:
        # Thử ghi vào thư mục data local
        local_db_path = os.path.join(DATA_DIR, "nongsan_v2.sqlite3")
        try:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR, exist_ok=True)
            # Test quyền ghi bằng cách tạo file tạm
            test_file = os.path.join(DATA_DIR, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            final_url = f"sqlite:///{local_db_path}"
        except Exception as e:
            print(f"⚠️ Local directory {DATA_DIR} is read-only or error: {e}")
            final_url = "sqlite:////tmp/nongsan_v2.sqlite3"

    # 3. Logic sao chép dữ liệu (Pre-fill)
    # Nếu URL là sqlite và trỏ tới /tmp, hãy kiểm tra để copy từ nguồn local
    if final_url.startswith("sqlite:///"):
        db_path = final_url.replace("sqlite:///", "")
        
        # Đảm bảo thư mục cha tồn tại
        parent_dir = os.path.dirname(db_path)
        if parent_dir and not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except: pass
            
        # Nếu đích là /tmp và chưa có file, nhưng local có file thì copy sang
        if "/tmp/" in db_path and not os.path.exists(db_path):
            if os.path.exists(local_src_path):
                try:
                    import shutil
                    shutil.copy2(local_src_path, db_path)
                    # Cấp quyền cho file vừa copy
                    os.chmod(db_path, 0o777)
                    print(f"✅ Pre-filled database copied to {db_path}")
                except Exception as copy_err:
                    print(f"❌ Failed to copy pre-filled database: {copy_err}")
    
    return final_url

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

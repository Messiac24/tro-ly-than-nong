from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Đường dẫn tới file SQLite bên trong thư mục server/data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Ưu tiên lấy đường dẫn từ biến môi trường (cho Production/Docker), nếu không có mới dùng mặc định local
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"sqlite:///{os.path.join(DATA_DIR, 'nongsan_v2.sqlite3')}"
)

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

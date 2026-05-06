"""
🌾 AI Dự Báo Kế Hoạch Canh Tác Mùa Vụ & Giá Nông Sản
Entry point - FastAPI Application

Hệ thống AI hỗ trợ nông dân Lâm Đồng (B'Lao, Xuân Trường)
dự báo giá, đánh giá rủi ro, và khuyến nghị canh tác.
"""

import sys
import os

# Thêm thư mục hiện tại vào path để import các module local
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from fastapi.staticfiles import StaticFiles

# Force UTF-8 encoding for standard output/error to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# ── Khởi tạo ứng dụng ──────────────────────────────────────
app = FastAPI(
    title="Trợ Lý Thần Nông - Dự Báo Canh Tác & Giá",
    description=(
        "Hệ thống AI dự báo kế hoạch canh tác mùa vụ "
        "và giá nông sản cho nông dân Lâm Đồng."
    ),
    version="1.0.0",
)

# Khởi tạo database
models.Base.metadata.create_all(bind=engine)

# Tự động tạo Admin nếu chưa có
from database import SessionLocal
import bcrypt
def init_admin():
    db = SessionLocal()
    try:
        admin_username = "admin"
        existing = db.query(models.User).filter(models.User.username == admin_username).first()
        if not existing:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw("admin123".encode('utf-8'), salt).decode('utf-8')
            new_admin = models.User(
                username=admin_username,
                email="admin@thannong.ai",
                full_name="Administrator",
                hashed_password=hashed,
                role="admin",
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            print("🌾 [System] Đã tạo tài khoản Admin mặc định.")
    except Exception as e:
        print(f"❌ [Error] Lỗi khởi tạo Admin: {e}")
    finally:
        db.close()

init_admin()

# ── Cấu hình CORS ──────────────────────────────────────────
# Cho phép Frontend kết nối (sẽ cập nhật domain cụ thể khi deploy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Thay bằng domain Frontend khi deploy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers import predict, chat, auth, admin

# ── Cấu hình Rate Limiting ───────────────────────────────
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Cấu hình Routers ──────────────────────────────────────────
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(chat.router)
app.include_router(admin.router)

# ── Phục vụ giao diện Frontend ──────────────────────────────
# Mount thư mục client để truy cập trực tiếp từ root /
client_path = os.path.join(os.path.dirname(current_dir), "client")
if os.path.exists(client_path):
    app.mount("/", StaticFiles(directory=client_path, html=True), name="client")


@app.get("/", tags=["Health"])
async def root():
    """Chuyển hướng về trang chủ index.html."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/index.html")


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint kiểm tra sức khỏe hệ thống."""
    return {"status": "healthy"}

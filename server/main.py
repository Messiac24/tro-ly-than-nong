"""
Tro Ly Than Nong - API Server
"""

import sys
import os

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from fastapi.staticfiles import StaticFiles

# Encoding fix for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

app = FastAPI(
    title="Trợ Lý Thần Nông",
    version="1.0.0",
)

# Init db
models.Base.metadata.create_all(bind=engine)

# Default admin
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
            print("System: Created default admin account.")
    except Exception as e:
        print(f"Error initializing admin: {e}")
    finally:
        db.close()

init_admin()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost", 
        "http://localhost:80", 
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from routers import predict, chat, auth, admin

def get_real_ip(request: Request):
    return request.headers.get("X-Forwarded-For", request.client.host)

# Rate limiting
limiter = Limiter(key_func=get_real_ip)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(chat.router)
app.include_router(admin.router)

# Static files
client_path = os.path.join(os.path.dirname(current_dir), "client")
if os.path.exists(client_path):
    app.mount("/", StaticFiles(directory=client_path, html=True), name="client")


@app.get("/", tags=["Health"])
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/index.html")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

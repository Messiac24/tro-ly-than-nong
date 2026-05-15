# Project Architecture

> Tổng hợp kiến thức về Kiến trúc, Bảo mật và Tối ưu Backend trong dự án Trợ Lý Thần Nông.
> Cập nhật lần cuối: 2026-05-13

---

## Architecture

### FastAPI & ML Backend
- **Ngày**: 2026-05-13
- **Chi tiết**: Kết hợp FastAPI (REST), SQLite (dữ liệu quan hệ, người dùng) và ChromaDB (Vector Search cho RAG). Cấu trúc tách biệt `server` và `client`, giao tiếp qua API.
- **Files liên quan**: `server/main.py`, `server/database.py`, `server/ml/rag_engine.py`

### Domain-Specific Decision Engine
- **Ngày**: 2026-05-15
- **Chi tiết**: Tích hợp tầng logic chuyên gia (Expert Rules) để kiểm soát kết quả AI. Decision Engine tính toán ROI, năng suất thực tế dựa trên các biến số môi trường (độ cao, nhiệt độ, lượng mưa) và kịch bản canh tác (Kiến thiết vs Kinh doanh).
- **Files liên quan**: `server/ml/decision_engine.py`, `server/ml/expert_rules.py`


### Docker Compose Deployment
- **Ngày**: 2026-05-13
- **Chi tiết**: Dùng docker-compose chạy song song 2 container: Backend (Uvicorn) port 8000 và Frontend (Nginx) port 80. Toàn bộ state (SQLite, ChromaDB) phải được mount ra volume ngoài ở `/app/server/data` để không mất dữ liệu.
- **Files liên quan**: `docker-compose.yml`, `Dockerfile`

---

## Bugs & Solutions

### Docker Image quá lớn do PyTorch CUDA
- **Ngày**: 2026-05-13
- **Vấn đề**: Khi cài `torch` qua requirements.txt, pip tải mặc định bản CUDA nặng hơn 2.5GB.
- **Root cause**: Docker không tự nhận biết hệ thống deploy chỉ có CPU (như Hugging Face Spaces free tier).
- **Fix**: Thêm lệnh cài bản CPU-only: `RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu` ngay trước bước cài requirements.
- **Files liên quan**: `Dockerfile`

### HuggingFace Model bị tải lại liên tục
- **Ngày**: 2026-05-13
- **Vấn đề**: Khởi động lại container bị chậm do RAG model (`all-MiniLM-L6-v2`) bị tải lại từ đầu.
- **Root cause**: Model lưu mặc định ở `~/.cache/huggingface` (không được mount).
- **Fix**: Cấu hình biến môi trường `HF_HOME=/app/server/data/hf_cache` trong compose file để cache được mount cùng thư mục data.
- **Files liên quan**: `docker-compose.yml`

### Rate Limiting chặn sai IP qua Proxy
- **Ngày**: 2026-05-13
- **Vấn đề**: `slowapi` chặn tất cả users nếu một người bị limit.
- **Root cause**: Hàm `get_remote_address` trả về IP của Docker Gateway (hoặc Nginx) thay vì IP thực.
- **Fix**: Viết custom key_func lấy IP từ header `X-Forwarded-For`.
- **Files liên quan**: `server/main.py`

### Lỗ hổng CORS & Deprecation
- **Ngày**: 2026-05-13
- **Vấn đề**: `allow_origins=["*"]` + `allow_credentials=True` gây lỗi ở trình duyệt bảo mật cao; `datetime.utcnow()` báo lỗi deprecation ở Python 3.12.
- **Fix**: Chỉ định origins cụ thể `["http://localhost"]` và thay thế thành `datetime.now(timezone.utc)`.
- **Files liên quan**: `server/main.py`, `server/routers/auth.py`

---

## How-To

### Setup Rate Limiter an toàn với Proxy
- **Ngày**: 2026-05-13
- **Bước thực hiện**:
  1. Tạo hàm extract IP: `def get_real_ip(req): return req.headers.get("X-Forwarded-For", req.client.host)`
  2. Khởi tạo Limiter: `limiter = Limiter(key_func=get_real_ip)`
  3. Gán vào FastAPI: `app.state.limiter = limiter`
  4. Đăng ký exception handler: `app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)`
- **Files liên quan**: `server/main.py`

---

## Patterns

### JWT Token Generation (Python 3.12+)
- **Ngày**: 2026-05-13
- **Chi tiết**: Chuẩn hóa cách lấy thời gian UTC an toàn, tránh bị deprecation thay thế cho `datetime.utcnow()`.
- **Ví dụ code**:
  ```python
  from datetime import datetime, timezone, timedelta
  expire = datetime.now(timezone.utc) + timedelta(minutes=15)
  ```
- **Files liên quan**: `server/routers/auth.py`

### Singleton for Resource-Heavy Services
- **Ngày**: 2026-05-15
- **Chi tiết**: Các service nặng như `KnowledgeBaseRetrieval` (RAG Engine) sử dụng pattern Singleton và Lazy Loading để tránh việc load lại model Embeddings (300MB+) nhiều lần gây tốn RAM.
- **Files liên quan**: `server/ml/rag_engine.py`


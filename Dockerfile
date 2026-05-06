# ── Stage 1: Build/Run Backend ──
FROM python:3.11-slim

WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài đặt dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn backend
COPY server/ ./server/

# Port FastAPI
EXPOSE 8000

# Chạy server
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Stage 1: Build/Run ──
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

# Copy toàn bộ mã nguồn
COPY server/ ./server/
COPY client/ ./client/

RUN mkdir -p /app/server/data

# Quan trọng: Không dùng EXPOSE cố định, Render sẽ tự quản lý
# Dùng shell form cho CMD để nhận được biến môi trường $PORT
CMD uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-8000}

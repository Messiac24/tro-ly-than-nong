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

# Tạo thư mục data để lưu SQLite
RUN mkdir -p /app/server/data && chmod 777 /app/server/data

# Hugging Face Spaces mặc định dùng port 7860
ENV PORT=7860
EXPOSE 7860

# Chạy server
CMD uvicorn server.main:app --host 0.0.0.0 --port 7860

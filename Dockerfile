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
# Chúng ta copy cả server và client để FastAPI có thể phục vụ file tĩnh
COPY server/ ./server/
COPY client/ ./client/

# Tạo thư mục data để lưu SQLite nếu chưa có
RUN mkdir -p /app/server/data

# Port FastAPI (Render sẽ tự nhận diện port này)
EXPOSE 8000

# Chạy server
# Chú ý: Render cần host 0.0.0.0
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]

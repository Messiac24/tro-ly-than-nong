# ── Stage 1: Build/Run ──
FROM python:3.11-slim

# Tạo User mới theo yêu cầu của Hugging Face
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết (phải dùng quyền root tạm thời)
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*
USER user

# Copy requirements và cài đặt dependencies
COPY --chown=user server/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy toàn bộ mã nguồn
COPY --chown=user server/ ./server/
COPY --chown=user client/ ./client/

# Tạo thư mục data
RUN mkdir -p /app/server/data && chmod 777 /app/server/data

# Hugging Face Spaces mặc định dùng port 7860
ENV PORT=7860
EXPOSE 7860

# Chạy server
CMD uvicorn server.main:app --host 0.0.0.0 --port 7860

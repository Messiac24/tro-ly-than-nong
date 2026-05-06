# 🌾 Trợ Lý Thần Nông (Agricultural AI Assistant)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Trợ Lý Thần Nông** là một hệ thống AI tiên tiến được thiết kế để hỗ trợ nông dân (đặc biệt tại khu vực Lâm Đồng) trong việc tối ưu hóa quy trình canh tác, dự báo rủi ro sinh thái và phân tích thị trường nông sản. Hệ thống kết hợp sức mạnh của công nghệ **RAG (Retrieval-Augmented Generation)** và **Hệ chuyên gia (Expert Rules)** để đưa ra những lời khuyên chính xác và đáng tin cậy.

---

## 🚀 Tính Năng Cốt Lõi

### 1. Tư Vấn Tri Thức Nông Nghiệp (RAG-based Chat)
*   Sử dụng công nghệ RAG để truy xuất thông tin từ kho tài liệu kỹ thuật chính thống (PDF).
*   Hỗ trợ chuyên sâu các loại cây trồng chủ lực: **Cà phê, Sầu riêng, Chè**.
*   Đảm bảo câu trả lời có tính chính xác cao, trích dẫn trực tiếp từ sổ tay kỹ thuật.

### 2. Công Cụ Dự Báo & Giả Lập Tài Chính (Decision Engine)
*   **Cảnh báo rủi ro sinh thái**: Áp dụng Expert Rules về độ cao, lượng mưa và nhiệt độ theo từng vùng.
*   **Dự báo giá nông sản**: Sử dụng các mô hình Machine Learning (XGBoost/TFT) để dự báo xu hướng thị trường.
*   **Tính toán ROI**: Hỗ trợ nông dân giả lập vốn đầu tư và dự báo lợi nhuận thực tế.

### 3. Dashboard Quản Trị Thông Minh
*   Trực quan hóa dữ liệu thống kê theo vùng địa lý và loại cây trồng.
*   **Knowledge Ingestion**: Giao diện cho phép Admin upload tài liệu PDF mới, tự động Vector hóa và cập nhật vào kho tri thức của AI.
*   Quản lý lịch sử hội thoại và phân tích hành vi người dùng.

### 4. Hàng Rào Bảo Mật (Safety Guardrails)
*   Tích hợp bộ lọc từ khóa nhạy cảm.
*   Cơ chế chống Prompt Injection để bảo vệ tính toàn vẹn của mô hình.

---

## 🛠 Tech Stack

### Backend (Core Logic)
*   **FastAPI**: Framework hiệu năng cao cho Python.
*   **ChromaDB**: Vector Database phục vụ lưu trữ và truy vấn tri thức (RAG).
*   **Machine Learning**: XGBoost, Temporal Fusion Transformer (TFT) cho dự báo chuỗi thời gian.
*   **SQLite**: Lưu trữ dữ liệu quan hệ và lịch sử người dùng.

### Frontend (User Interface)
*   **Vanilla JS & HTML5/CSS3**: Đảm bảo tốc độ tải trang nhanh và tương thích tốt trên thiết bị di động.
*   **Chart.js**: Hiển thị biểu đồ thống kê trực quan trên Dashboard.

### DevOps & Deployment
*   **Docker & Docker Compose**: Đóng gói ứng dụng dưới dạng container, dễ dàng triển khai trên mọi môi trường.
*   **Nginx**: Reverse Proxy và phục vụ static files cho Frontend.

---

## 📦 Hướng Dẫn Cài Đặt

### 1. Yêu Cầu Hệ Thống
*   Docker & Docker Compose đã được cài đặt.
*   Git.

### 2. Triển Khai Nhanh
```bash
# Clone repository
git clone https://github.com/Messiac24/tro-ly-than-nong.git
cd tro-ly-than-nong

# Khởi chạy bằng Docker Compose
docker-compose up -d --build
```

### 3. Truy Cập Ứng Dụng
*   **Giao diện người dùng**: [http://localhost](http://localhost)
*   **Backend API (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Trang quản trị**: [http://localhost/login.html](http://localhost/login.html)
    *   *Tài khoản mặc định:* `admin` / `admin123`

---

## 📂 Cấu Trúc Thư Mục
```text
├── client/              # Giao diện người dùng (HTML, CSS, JS)
├── server/              # Mã nguồn Backend (FastAPI, AI Logic)
│   ├── data/            # Cơ sở dữ liệu (SQLite, ChromaDB)
│   ├── routers/         # Định nghĩa các API endpoints
│   └── ai_models/       # Các mô hình ML và logic RAG
├── Dockerfile           # Docker configuration cho Backend
├── docker-compose.yml   # Orchestration cho toàn bộ hệ thống
└── PRD_Than_Nong.md     # Tài liệu yêu cầu sản phẩm chi tiết
```

---

## 📝 Giấy Phép
Dự án được phát hành dưới giấy phép [MIT](LICENSE).

---
**Phát triển bởi [Messiac24](https://github.com/Messiac24)**
*Mục tiêu hiện đại hóa nông nghiệp Việt Nam thông qua Trí Tuệ Nhân Tạo.*

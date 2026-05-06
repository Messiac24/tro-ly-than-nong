# ĐẶC TẢ DỰ ÁN - TRỢ LÝ THẦN NÔNG

## 1. Mục tiêu
Xây dựng hệ thống hỗ trợ nông dân Lâm Đồng tra cứu kỹ thuật canh tác (RAG), dự báo rủi ro sinh thái và biến động giá nông sản.

## 2. Tính năng chính
- **Tra cứu kỹ thuật (Chat RAG):** Trả lời câu hỏi dựa trên file PDF hướng dẫn kỹ thuật.
- **Giả lập canh tác:** Nhập vốn, diện tích, vùng trồng để nhận cảnh báo rủi ro và dự báo lợi nhuận (ROI).
- **Admin Dashboard:** Quản lý lịch sử chat, thống kê và upload thêm tài liệu kỹ thuật.
- **Bảo mật:** Filter nội dung không phù hợp và chặn prompt injection cơ bản.

## 3. Thông tin hệ thống
- **Techstack:** FastAPI, SQLite, ChromaDB, Gemini LLM.
- **Tài khoản test:** `admin` / `admin123`.
- **Cổng:** 8000 (Backend), 80 (Frontend).


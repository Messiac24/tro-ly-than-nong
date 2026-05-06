# PRODUCT REQUIREMENTS DOCUMENT (PRD) - TRỢ LÝ THẦN NÔNG

## 1. Tổng quan sản phẩm
**Tên dự án:** Trợ Lý Thần Nông (Agricultural AI Assistant).
**Mục tiêu:** Hệ thống AI hỗ trợ nông dân Lâm Đồng dự báo rủi ro canh tác, giá nông sản và tư vấn tri thức kỹ thuật thông qua công nghệ RAG (Retrieval-Augmented Generation).

## 2. Các tính năng cốt lõi (Core Features)

### 2.1. Tư vấn tri thức nông nghiệp (RAG Chat)
- Người dùng hỏi về kỹ thuật canh tác (Cà phê, Sầu riêng, Chè).
- AI trích xuất thông tin từ kho tri thức PDF (Sổ tay kỹ thuật) và trả lời.
- **Yêu cầu:** Trả lời chính xác, không ảo giác, chỉ tập trung vào nông nghiệp.

### 2.2. Công cụ Dự báo & Giả lập tài chính (Decision Engine)
- Người dùng nhập số vốn, diện tích và chọn loại cây/vùng trồng.
- Hệ thống áp dụng **Bộ luật chuyên gia (Expert Rules)** về độ cao và thời tiết để cảnh báo rủi ro sinh thái.
- Hệ thống dùng ML (XGBoost/TFT) để dự báo giá và tính toán ROI (Lợi nhuận).

### 2.3. Dashboard Quản trị (Admin Dashboard)
- Hiển thị biểu đồ thống kê các loại cây trồng và vùng địa lý.
- Tính năng nạp thêm tri thức (Knowledge Ingestion): Upload PDF và Vector hóa tự động.
- Quản lý người dùng và lịch sử hội thoại.

### 2.4. Hàng rào bảo mật (Safety Guardrails)
- Chặn các từ khóa nhạy cảm (Chính trị, tôn giáo).
- Chống Prompt Injection (Yêu cầu AI quên quy tắc).

## 3. Đối tượng người dùng & Môi trường
- **Người dùng:** Nông dân, HTX nông nghiệp, Quản trị viên.
- **Môi trường:** Web App (Responsive trên di động và máy tính).
- **Cổng kết nối:** 80 (Frontend), 8000 (Backend API).

## 4. Tài khoản kiểm thử (Test Accounts)
- **Admin:** `admin` / `admin123`
- **URL trang chủ:** `http://localhost/index.html`
- **URL đăng nhập:** `http://localhost/login.html`

---
title: Trợ Lý Thần Nông - Agricultural AI Assistant
emoji: 🌾
colorFrom: green
colorTo: yellow
sdk: docker
pinned: true
app_port: 7860
---

# 🌾 Trợ Lý Thần Nông (Agricultural AI Assistant)

Hệ thống hỗ trợ nông nghiệp thông minh dành riêng cho khu vực Lâm Đồng, tích hợp AI đa mô hình để hỗ trợ bà con nông dân trong việc dự báo giá, đánh giá rủi ro và tư vấn kỹ thuật canh tác.

## 🚀 Tính Năng Cốt Lõi

### 1. Hệ Thống RAG (Retrieval-Augmented Generation)

- **Tri thức chuyên sâu:** Nạp dữ liệu từ hơn 1,500 trang tài liệu kỹ thuật (VietGAP, Sổ tay canh tác WASI, quy trình phòng trừ sâu bệnh CropLife).
- **AI Engine:** Sử dụng mô hình ngôn ngữ lớn **Llama-3.3-70B-Instruct** kết hợp với **ChromaDB** và **HuggingFace Embeddings** (`all-MiniLM-L6-v2`) để cung cấp phản hồi chính xác, bám sát thực tế địa phương.
- **Xử lý ngôn ngữ:** Hỗ trợ tiếng Việt tự nhiên, phong cách gần gũi với nông dân nhưng vẫn đảm bảo tính khoa học.

### 2. Dự Báo Giá & Phân Tích Tài Chính

- **Mô hình dự báo:**
  - **TFT (Temporal Fusion Transformer):** Dự báo giá Cà phê dựa trên dữ liệu lịch sử và các biến số thời tiết toàn cầu.
  - **XGBoost:** Dự báo biến động giá Sầu riêng và Chè Ô Long.
- **ROI Analysis:** Tính toán lợi nhuận dự kiến, thời gian thu hồi vốn và phân bổ chi phí vật tư (phân bón, nhân công, hạt giống).

### 3. Đánh Giá Rủi Ro Sinh Thái

- **Real-time Weather:** Tích hợp dữ liệu thời tiết trực tiếp để cảnh báo sương muối (tại Đà Lạt) hoặc mưa lớn gây thối rễ sầu riêng (tại Bảo Lộc).
- **Expert Rules:** Hệ thống luật chuyên gia đánh giá mức độ rủi ro dựa trên độ cao (elevation), thổ nhưỡng và chu kỳ sinh trưởng của cây trồng.

### 4. Giao Diện Hiện Đại & Trực Quan

- **Thiết kế Glassmorphism:** Trải nghiệm người dùng cao cấp, hỗ trợ cả Dark Mode.
- **Biểu đồ tương tác:** Sử dụng **Chart.js** để trực quan hóa biến động giá và biểu đồ tài chính.

## 🛠 Công Nghệ Sử Dụng

| Thành phần           | Công nghệ                                   |
| -------------------- | ------------------------------------------- |
| **Backend**          | FastAPI (Python 3.11), SQLAlchemy, Pydantic |
| **Database**         | SQLite (App data), ChromaDB (Vector store)  |
| **LLM SDK**          | OpenAI SDK (via OpenRouter)                 |
| **Machine Learning** | PyTorch, XGBoost, Scikit-learn, Pandas      |
| **Frontend**         | Vanilla Javascript, Vanilla CSS, Chart.js   |
| **Deployment**       | Docker, Hugging Face Spaces                 |

## 📦 Cài Đặt Local

1. **Clone repository:**

   ```bash
   git clone https://github.com/Messiac24/tro-ly-than-nong.git
   cd tro-ly-than-nong
   ```

2. **Cấu hình biến môi trường:**
   Tạo file `.env` trong thư mục `server/`:

   ```env
   OPENROUTER_API_KEY=your_key_here
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///./data/nongsan_v2.sqlite3
   ```

3. **Chạy bằng Docker (Khuyên dùng):**

   ```bash
   docker build -t tro-ly-than-nong .
   docker run -p 8000:8000 tro-ly-than-nong
   ```

4. **Chạy thủ công:**
   ```bash
   cd server
   pip install -r requirements.txt
   python main.py
   ```

## 📂 Cấu Trúc Thư Mục

- `/server`: Chứa mã nguồn API, logic AI và xử lý dữ liệu.
  - `/ml`: Các mô hình Machine Learning và RAG Engine.
  - `/data`: Cơ sở dữ liệu và kho tài liệu PDF.
- `/client`: Giao diện người dùng (HTML, CSS, JS).

## 📄 Giấy Phép & Bản Quyền

Dự án được phát triển nhằm hỗ trợ cộng đồng nông nghiệp. Mọi đóng góp vui lòng gửi Pull Request hoặc tạo Issue trên GitHub.

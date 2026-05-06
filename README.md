# 🌾 Trợ Lý Thần Nông (Agricultural Assistant)

Hệ thống hỗ trợ nông nghiệp kết hợp **RAG (Retrieval-Augmented Generation)** và **Expert Rules** để cung cấp hướng dẫn canh tác và quản lý rủi ro cho khu vực Lâm Đồng.

## Tính năng chính

- **Tư vấn dựa trên tài liệu (RAG)**: Truy xuất thông tin từ các sổ tay kỹ thuật (PDF) để trả lời câu hỏi của nông dân.
- **Hệ thống luật chuyên gia**: Cảnh báo rủi ro sinh thái dựa trên cao độ, thổ nhưỡng và thời tiết.
- **Dự báo giá**: Sử dụng ML (XGBoost/TFT) để giả lập ROI và dự báo xu hướng giá nông sản.
- **Quản lý tri thức**: Dashboard cho phép upload PDF để cập nhật kiến thức cho hệ thống.

## Công nghệ sử dụng

- **Backend**: FastAPI, SQLAlchemy (SQLite), LangChain.
- **AI Core**: Gemini 1.5 Flash / 2.0 (qua Google AI hoặc OpenRouter).
- **Vector DB**: ChromaDB.
- **Frontend**: Vanilla JS, TailwindCSS, Chart.js.
- **Deployment**: Docker, Nginx.

## Cài đặt nhanh

### Chạy bằng Docker
```bash
git clone https://github.com/Messiac24/tro-ly-than-nong.git
cd tro-ly-than-nong
docker-compose up -d --build
```

### Sử dụng API
Hệ thống cung cấp Swagger UI tại `http://localhost:8000/docs`.

Ví dụ gọi API tư vấn:
```python
import requests

payload = {"question": "Kỹ thuật bón phân sầu riêng mùa mưa?"}
res = requests.post("http://localhost:8000/api/chat", json=payload)
print(res.json()["answer"])
```

## Lưu ý kỹ thuật
- Hệ thống ưu tiên dữ liệu từ RAG để đảm bảo tính chính xác.
- Hỗ trợ đổi model linh hoạt qua cấu hình API Key (Gemini/OpenRouter).
- Dữ liệu hội thoại được lưu local tại SQLite.

---
**Phát triển bởi [Messiac24](https://github.com/Messiac24)**


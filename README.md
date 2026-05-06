# 🌾 Trợ Lý Thần Nông (Agricultural AI Assistant)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://www.docker.com/)

**Trợ Lý Thần Nông** is a specialized AI system designed for agriculture, combining **RAG (Retrieval-Augmented Generation)** and **Expert Rules** to provide precise cultivation guidance and ecological risk management.

---

## 🚀 Key Features

✔️ **RAG-based Consultation**: Retrieves information directly from official technical manuals (PDFs), eliminating AI hallucinations.

✔️ **Expert Rules Engine**: Provides risk alerts based on real-world data including elevation, soil types, and weather patterns in the Lam Dong region.

✔️ **Market Forecasting**: Utilizes Machine Learning (XGBoost/TFT) to simulate ROI and predict agricultural price trends.

✔️ **Smart Administration**: Intuitive dashboard with seamless knowledge ingestion—update the AI's knowledge base by simply uploading a PDF.

✔️ **Safety Guardrails**: Integrated protection against prompt injection and content filtering for inappropriate topics.

---

## 🛠 Tech Stack

### AI & Data Architecture
| Component | Technology | Purpose |
|:---|:---|:---|
| **LLM Core** | Gemini 1.5 Flash / 2.0 | Natural Language Processing via OpenRouter / Google AI. |
| **Vector DB** | **ChromaDB** | Storing and querying agricultural knowledge as vectors. |
| **ML Engine** | XGBoost & TFT | Time-series forecasting for prices and yields. |
| **Expert System** | Python Logic | Executing agronomic hard rules and ecological constraints. |

### System & Deployment
- **Backend**: FastAPI (Asynchronous, High Performance).
- **Frontend**: Vanilla JS, HTML5, CSS3 (Lightweight & Mobile Responsive).
- **Containerization**: Docker & Docker Compose.
- **Reverse Proxy**: Nginx.

---

## 📂 Module Structure

| Module | Primary Function |
|:---|:---|
| `server/ai_models` | RAG logic, vector processing, and forecasting models. |
| `server/routers` | API endpoints (Chat, Predict, Admin, Auth). |
| `server/data` | Persistent storage for `nongsan.db` (SQLite) and `chroma_db`. |
| `client/` | Web interface optimized for both Desktop and Mobile devices. |

---

## 📦 Quick Start

### 1. Deployment with Docker
```bash
git clone https://github.com/Messiac24/tro-ly-than-nong.git
cd tro-ly-than-nong
docker-compose up -d --build
```

### 2. API Usage (For Developers)
The system provides a Swagger UI for testing endpoints at `http://localhost:8000/docs`:

```python
# Example: Calling the Consultation API
import requests

payload = {"question": "Best fertilization technique for coffee during the rainy season?"}
response = requests.post("http://localhost:8000/api/chat", json=payload)
print(response.json()["answer"])
```

---

## 💡 Technical Notes

*   **Why RAG instead of Fine-tuning?** RAG allows for immediate knowledge updates by uploading PDFs without retraining the model. It also ensures the AI (Gemini 1.5/2.0) provides verifiable citations from the source material.
*   **Multi-model Support**: The system is designed to work with **OpenRouter**, allowing easy switching between different Gemini versions or other LLMs if needed.
*   **Data Privacy**: All conversation history and simulation data are stored locally in SQLite, ensuring farmer data remains private and secure.
*   **Performance**: The backend is built with an asynchronous (Async) architecture, enabling it to handle high concurrency without performance degradation.

---
**Developed by [Messiac24](https://github.com/Messiac24)**
_Modernizing Vietnamese Agriculture through Artificial Intelligence._

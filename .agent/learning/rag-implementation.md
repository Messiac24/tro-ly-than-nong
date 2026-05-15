# RAG Implementation

> Tổng hợp kiến thức về hệ thống Retrieval-Augmented Generation (RAG) để tư vấn kỹ thuật canh tác.
> Cập nhật lần cuối: 2026-05-15

---

## Architecture

### RAG Pipeline (Local Embeddings + ChromaDB)
- **Ngày**: 2026-05-15
- **Chi tiết**: Sử dụng `all-MiniLM-L6-v2` cho local embeddings và `ChromaDB` làm vector store. Hệ thống được thiết kế Singleton để tối ưu bộ nhớ khi load model embeddings (lazy loading).
- **Files liên quan**: `server/ml/rag_engine.py`, `server/ingest_kb.py`

---

## How-To

### Quy trình Ingestion tài liệu PDF
- **Ngày**: 2026-05-15
- **Bước thực hiện**:
  1. `PyPDFLoader` đọc file từ thư mục `data/knowledge_base`.
  2. Làm sạch văn bản (Xóa số trang, tiêu đề lặp lại, nối các dòng bị ngắt bởi dấu xuống dòng không đúng chỗ).
  3. Chia nhỏ văn bản (Chunking) bằng `RecursiveCharacterTextSplitter` với `chunk_size=1000`, `overlap=200`.
  4. Lưu vào ChromaDB.
- **Files liên quan**: `server/ingest_kb.py`

### Tối ưu Context cho LLM
- **Ngày**: 2026-05-15
- **Bước thực hiện**:
  1. Truy xuất top_k đoạn văn bản tương đồng.
  2. Lọc theo `MIN_RELEVANCE_SCORE` (mặc định 0.22).
  3. Kiểm tra và loại bỏ nội dung rác (Mục lục, citations PDF).
  4. Giới hạn tổng ký tự ngữ cảnh (MAX_CONTEXT_CHARS=4000) để tránh tràn token LLM.
- **Files liên quan**: `server/ml/rag_engine.py`

---

## Patterns

### PDF Artifact Cleaning
- **Ngày**: 2026-05-15
- **Chi tiết**: Sử dụng Regex để loại bỏ các "rác" đặc thù của PDF như citation nguồn hình ảnh `(Nguồn: ...)`, số trang, và các đoạn văn bản boilerplate lặp lại ở đầu mỗi trang.
- **Files liên quan**: `server/ml/rag_engine.py`

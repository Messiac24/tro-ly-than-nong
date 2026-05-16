from dotenv import load_dotenv
load_dotenv()

import os
import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Logic tìm đường dẫn Vector DB
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# Nếu thư mục local tồn tại (đã được tạo lúc build), ưu tiên dùng nó
if os.path.exists(LOCAL_CHROMA_DIR):
    CHROMA_DIR = LOCAL_CHROMA_DIR
else:
    # Fallback sang /tmp cho môi trường ephemeral
    CHROMA_DIR = "/tmp/chroma_db"

# Ngưỡng điểm tương đồng tối thiểu để giữ kết quả
MIN_RELEVANCE_SCORE = 0.22
# Giới hạn ký tự tối đa cho toàn bộ ngữ cảnh gửi lên LLM (tránh tràn Token)
MAX_CONTEXT_CHARS = 4000 

# Sử dụng /tmp cho HF Cache
HF_CACHE_DIR = "/tmp/hf_cache"

class KnowledgeBaseRetrieval:
    _instance = None
    _embeddings = None
    _vectorstore = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KnowledgeBaseRetrieval, cls).__new__(cls)
        return cls._instance

    @property
    def embeddings(self):
        """Lazy load embeddings model."""
        if self._embeddings is None:
            print(f"🚀 Loading Embedding Model (all-MiniLM-L6-v2) to {HF_CACHE_DIR}...")
            if not os.path.exists(HF_CACHE_DIR):
                os.makedirs(HF_CACHE_DIR, exist_ok=True)
            try:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name="all-MiniLM-L6-v2",
                    cache_folder=HF_CACHE_DIR
                )
            except Exception as e:
                print(f"❌ Lỗi khởi tạo Embeddings: {e}")
                # Fallback to local model path if needed or re-raise
                raise e
        return self._embeddings

    @property
    def vectorstore(self):
        """Lazy load vector database."""
        if self._vectorstore is None:
            if not os.path.exists(CHROMA_DIR):
                print(f"⚠️ Cảnh báo: Thư mục Vector DB không tồn tại tại {CHROMA_DIR}")
                return None
            
            self._vectorstore = Chroma(
                persist_directory=CHROMA_DIR,
                embedding_function=self.embeddings
            )
        return self._vectorstore

    def _clean_content(self, text: str) -> str:
        """Làm sạch văn bản chuyên sâu, xóa rác PDF và nối dòng."""
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'(Trang|Page)\s*\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'SỔ TAY HƯỚNG DẪN KỸ THUẬT CANH TÁC CÂY SẦU RIÊNG THEO VIETGAP', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Sổ tay canh tác cà phê Lâm Đồng', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Quy trình kỹ thuật chè ô long', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b\d+[\.\d]*\b', '', text) 
        text = re.sub(r'(Phụ lục|Chương|Mục)\s*\d+[\.\d]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'/uni[0-9A-F]{4}', '', text)
        boilerplate = ["LỜI CẢM ƠN", "Nhóm tác giả", "Văn phòng tổ chức", "Cục Trồng trọt", "Chi cục Trồng trọt", "Bộ Nông nghiệp"]
        for bp in boilerplate: text = text.replace(bp, "")
        text = re.sub(r'(?<![.:!?])\n', ' ', text)
        text = re.sub(r'\.{3,}', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _clean_pdf_artifacts(self, text: str) -> str:
        """Loại bỏ citations, tên hình ảnh, nguồn tham khảo thô từ PDF."""
        text = re.sub(r'\((?:[Nn]guồn|[Ss]ource):?\s*[^)]*\)', '', text)
        text = re.sub(r'Hình\s*\d+[\.:]\s*[^\n.]*[.\n]?', '', text)
        text = re.sub(r'Bảng\s*\d+[\.:]\s*[^\n.]*[.\n]?', '', text)
        text = re.sub(r'Ảnh:\s*[^\n.]*[.\n]?', '', text)
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
        text = re.sub(r'(?:Trang|trang)\s*\d+', '', text)
        text = re.sub(r'\b\d+\s*\|\s*Sổ tay[^\n]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    def _is_toc_content(self, text: str) -> bool:
        dot_sequences = len(re.findall(r'\.{3,}', text))
        if dot_sequences >= 3: return True
        list_patterns = len(re.findall(r'\(\d+\)|\b\d+\.', text))
        if list_patterns >= 5 and len(text) < 600: return True
        digits = sum(c.isdigit() for c in text)
        if len(text) > 0 and digits / len(text) > 0.2: return True
        return False

    def get_relevant_context(self, query: str, top_k: int = 3) -> str:
        """Tìm kiếm tài liệu và giới hạn Token bằng MAX_CONTEXT_CHARS."""
        if not self.vectorstore: return ""
        try:
            results = self.vectorstore.similarity_search_with_relevance_scores(query, k=top_k + 2)
            context_list = []
            current_length = 0
            
            for doc, score in results:
                if score < MIN_RELEVANCE_SCORE: continue
                content = self._clean_pdf_artifacts(self._clean_content(doc.page_content))
                
                if self._is_toc_content(content): continue
                
                # Cắt ngắn từng đoạn nếu quá dài
                if len(content) > 1200: content = content[:1200] + "..."
                
                # Kiểm tra giới hạn tổng ngữ cảnh
                if current_length + len(content) > MAX_CONTEXT_CHARS:
                    # Cố gắng lấy thêm một phần nhỏ nếu còn chỗ
                    remaining = MAX_CONTEXT_CHARS - current_length
                    if remaining > 100:
                        context_list.append(content[:remaining] + "...")
                    break
                
                context_list.append(content)
                current_length += len(content)
                
            return "\n\n".join(context_list)
        except Exception as e:
            print(f"❌ Lỗi truy xuất RAG: {e}")
            return ""

# Instance duy nhất (Singleton)
rag_engine = KnowledgeBaseRetrieval()

import os
import re
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")

# Ngưỡng điểm tương đồng tối thiểu để giữ kết quả
# (Chroma cosine distance → relevance score: cao hơn = liên quan hơn)
MIN_RELEVANCE_SCORE = 0.15


class KnowledgeBaseRetrieval:
    def __init__(self):
        """Khởi tạo engine truy xuất kiến thức nông nghiệp (Local)."""
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        if not os.path.exists(CHROMA_DIR):
            print(f"Cảnh báo: Thư mục Vector DB không tồn tại tại {CHROMA_DIR}")
            self.vectorstore = None
        else:
            self.vectorstore = Chroma(
                persist_directory=CHROMA_DIR,
                embedding_function=self.embeddings
            )

    def _clean_content(self, text: str) -> str:
        """Làm sạch văn bản chuyên sâu, xóa rác PDF và nối dòng."""
        # 1. Xóa các con số đứng một mình ở đầu/cuối dòng (Xóa số trang)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'(Trang|Page)\s*\d+', '', text, flags=re.IGNORECASE)
        
        # 2. Xóa tiêu đề tài liệu phổ biến và số chương mục loằng ngoằng
        text = re.sub(r'SỔ TAY HƯỚNG DẪN KỸ THUẬT CANH TÁC CÂY SẦU RIÊNG THEO VIETGAP', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Sổ tay canh tác cà phê Lâm Đồng', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Quy trình kỹ thuật chè ô long', '', text, flags=re.IGNORECASE)
        
        # Xóa các số chương mục dạng: 11.2.3, 4 11.2.3, Phụ lục 4...
        text = re.sub(r'\b\d+[\.\d]*\b', '', text) 
        text = re.sub(r'(Phụ lục|Chương|Mục)\s*\d+[\.\d]*', '', text, flags=re.IGNORECASE)
        
        # Xóa các mã Unicode lỗi dạng /uni1EF1...
        text = re.sub(r'/uni[0-9A-F]{4}', '', text)

        # Xóa các đoạn văn bản rác, lời cảm ơn, mục lục
        boilerplate = [
            "LỜI CẢM ƠN", "Nhóm tác giả", "Văn phòng tổ chức", "Cục Trồng trọt", 
            "Chi cục Trồng trọt", "Bộ Nông nghiệp", "HƯỚNG DẪN KỸ THUẬT CANH TÁC", 
            "SỔ TAY", "Mục lục", "Tài liệu tham khảo"
        ]
        for bp in boilerplate:
            text = text.replace(bp, "")
        
        # 4. NỐI DÒNG: Đổi dấu xuống dòng (\n) thành dấu cách, trừ khi nó kết thúc bằng dấu câu (. ! ?)
        text = re.sub(r'(?<![.:!?])\n', ' ', text)
        
        # 5. Xóa khoảng trắng thừa (nhiều dấu cách liền nhau)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _clean_pdf_artifacts(self, text: str) -> str:
        """Loại bỏ citations, tên hình ảnh, nguồn tham khảo thô từ PDF.
        
        Ví dụ loại bỏ:
        - (Nguồn: SOFRI, 2023)
        - Hình 56. Rễ sầu riêng bị thối rễ (Nguồn: SOFRI, 2023)
        - Bảng 1. Liều lượng phân bón
        - Ảnh: Tác giả chụp
        """
        # Loại bỏ "(Nguồn: ...)" hoặc "(nguồn: ...)"
        text = re.sub(r'\((?:[Nn]guồn|[Ss]ource):?\s*[^)]*\)', '', text)
        # Loại bỏ "Hình XX. Mô tả..." (cả dòng caption hình)
        text = re.sub(r'Hình\s*\d+[\.:]\s*[^\n.]*[.\n]?', '', text)
        # Loại bỏ "Bảng XX. Mô tả..." (caption bảng)
        text = re.sub(r'Bảng\s*\d+[\.:]\s*[^\n.]*[.\n]?', '', text)
        # Loại bỏ "Ảnh: ..."
        text = re.sub(r'Ảnh:\s*[^\n.]*[.\n]?', '', text)
        # Loại bỏ tham khảo dạng "[1]", "[2,3]"
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
        # Loại bỏ "Trang XX" ở cuối
        text = re.sub(r'(?:Trang|trang)\s*\d+', '', text)
        # Loại bỏ header/footer chứa số trang và tên sách (VD: "36 | Sổ tay Hướng dẫn...")
        text = re.sub(r'\b\d+\s*\|\s*Sổ tay[^\n]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Sổ tay[^\n]*\|\s*\d+\b', '', text, flags=re.IGNORECASE)
        # Loại bỏ gạch đứng hoặc dấu gạch ngang vô nghĩa ở cuối
        text = re.sub(r'\s*[|\-]\s*$', '', text)
        # Loại bỏ URL
        text = re.sub(r'https?://\S+', '', text)
        # Chuẩn hóa lại khoảng trắng sau khi xóa
        text = re.sub(r'\s{2,}', ' ', text)
        
        return text.strip()

    def _is_toc_content(self, text: str) -> bool:
        """Kiểm tra nếu đoạn văn bản chủ yếu là mục lục."""
        # Đếm số dãy dấu chấm (TOC indicators)
        dot_sequences = len(re.findall(r'\.{3,}', text))
        # Nếu có nhiều hơn 3 dãy dấu chấm, coi như mục lục
        if dot_sequences >= 3:
            return True
        # Nếu tỷ lệ chữ số / ký tự quá cao (dấu hiệu trang số)
        digits = sum(c.isdigit() for c in text)
        if len(text) > 0 and digits / len(text) > 0.15:
            return True
        return False

    def _is_low_quality(self, text: str) -> bool:
        """Kiểm tra nếu đoạn text chất lượng thấp (quá nhiều ký tự đặc biệt, 
        danh sách tên hóa chất, v.v.)."""
        if len(text) < 30:
            return True
        
        # Tỷ lệ ký tự đặc biệt (/, ;, +) quá cao → danh sách hóa chất / bảng
        special_chars = sum(1 for c in text if c in '/;+|{}[]()%')
        if len(text) > 0 and special_chars / len(text) > 0.08:
            return True
        
        # Quá nhiều dấu phẩy liên tiếp → liệt kê thô
        if text.count(',') > 15 and len(text) < 300:
            return True
            
        return False

    def get_relevant_context(self, query: str, top_k: int = 3) -> str:
        """
        Tìm kiếm các đoạn tài liệu liên quan nhất đến câu hỏi.
        Trả về NỘI DUNG ĐÃ LÀM SẠCH, KHÔNG kèm thông tin nguồn.
        Dùng cho chế độ Rule-based (chat tự nhiên).
        
        Args:
            query (str): Câu hỏi của người dùng.
            top_k (int): Số lượng đoạn văn bản cần lấy.
            
        Returns:
            str: Chuỗi văn bản chứa ngữ cảnh từ các tài liệu (đã làm sạch).
        """
        if not self.vectorstore:
            return ""

        try:
            # Dùng similarity_search_with_relevance_scores để lọc kết quả kém
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query, k=top_k + 4
            )
            
            context_list = []
            for doc, score in results:
                if len(context_list) >= top_k:
                    break
                
                # Bỏ qua kết quả có điểm tương đồng quá thấp
                if score < MIN_RELEVANCE_SCORE:
                    continue
                    
                content = doc.page_content.replace("\n", " ")
                
                # Bỏ qua nội dung mục lục
                if self._is_toc_content(content):
                    continue
                
                # Làm sạch nội dung cơ bản
                content = self._clean_content(content)
                
                # Loại bỏ artifacts từ PDF (citations, hình, bảng)
                content = self._clean_pdf_artifacts(content)
                
                # Bỏ qua nội dung chất lượng thấp
                if self._is_low_quality(content):
                    continue
                
                # Giới hạn độ dài mỗi đoạn
                if len(content) > 500:
                    # Cắt tại câu hoàn chỉnh gần vị trí 500
                    cut_pos = content.rfind('.', 0, 500)
                    if cut_pos > 200:
                        content = content[:cut_pos + 1]
                    else:
                        content = content[:500] + "..."
                
                context_list.append(content)
            
            if not context_list:
                return ""
            
            return "\n\n".join(context_list)
            
        except Exception as e:
            print(f"Lỗi khi truy xuất RAG: {e}")
            return ""

    def get_relevant_context_with_sources(self, query: str, top_k: int = 3) -> str:
        """
        Tìm kiếm tài liệu KÈM thông tin nguồn.
        Dùng cho chế độ Agent (khi có LLM).
        
        Returns:
            str: Chuỗi văn bản kèm metadata nguồn.
        """
        if not self.vectorstore:
            return "Không có dữ liệu kiến thức chuyên môn."

        try:
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query, k=top_k + 3
            )
            
            context_list = []
            idx = 1
            for doc, score in results:
                if idx > top_k:
                    break
                
                if score < MIN_RELEVANCE_SCORE:
                    continue
                    
                source = os.path.basename(doc.metadata.get('source', 'Tài liệu'))
                page = doc.metadata.get('page', '?')
                content = doc.page_content.replace("\n", " ")
                
                if self._is_toc_content(content):
                    continue
                
                content = self._clean_content(content)
                content = self._clean_pdf_artifacts(content)
                
                if self._is_low_quality(content):
                    continue
                
                if len(content) > 500:
                    cut_pos = content.rfind('.', 0, 500)
                    if cut_pos > 200:
                        content = content[:cut_pos + 1]
                    else:
                        content = content[:500] + "..."
                
                context_list.append(f"[{idx}] (Nguồn: {source}, Trang: {page}): {content}")
                idx += 1
            
            if not context_list:
                return "Không có dữ liệu phù hợp trong kiến thức chuyên môn."
            
            return "\n\n".join(context_list)
        except Exception as e:
            print(f"Lỗi khi truy xuất RAG: {e}")
            return "Có lỗi xảy ra khi tra cứu kiến thức chuyên môn."


# Instance duy nhất để sử dụng trong toàn bộ app
rag_engine = KnowledgeBaseRetrieval()

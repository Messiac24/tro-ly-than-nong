import os
import re
import glob
import sys
from dotenv import load_dotenv

# Force UTF-8 encoding for standard output/error to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

KB_DIR = os.path.join(os.path.dirname(__file__), "data", "knowledge_base")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma_db")

def clean_rag_text(text):
    """Làm sạch văn bản từ PDF theo yêu cầu người dùng."""
    # 1. Xóa các con số đứng một mình ở đầu/cuối dòng (Xóa số trang)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'(Trang|Page)\s*\d+', '', text, flags=re.IGNORECASE)
    
    # 2. Xóa tiêu đề tài liệu phổ biến (có thể mở rộng thêm)
    titles_to_remove = [
        "Sổ tay canh tác cà phê Lâm Đồng",
        "Kỹ thuật canh tác sầu riêng",
        "Quy trình kỹ thuật chè ô long"
    ]
    for title in titles_to_remove:
        text = text.replace(title, "")
    
    # 3. NỐI DÒNG: Đổi dấu xuống dòng (\n) thành dấu cách, trừ khi nó kết thúc bằng dấu câu (. ! ?)
    # Điều này giúp các đoạn văn bị ngắt dòng trong PDF trở nên liền mạch
    text = re.sub(r'(?<![.:!?])\n', ' ', text)
    
    # 4. Xóa khoảng trắng thừa (nhiều dấu cách liền nhau)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def ingest_documents():
    # Xóa database cũ để nạp mới hoàn toàn, tránh xung đột và dữ liệu rác
    import shutil
    if os.path.exists(CHROMA_DIR):
        print(f"Đang làm sạch bộ nhớ cũ tại {CHROMA_DIR}...")
        try:
            shutil.rmtree(CHROMA_DIR)
        except Exception as e:
            print(f"Không thể xóa bộ nhớ cũ (có thể đang bị khóa): {e}")

    print(f"Bắt đầu đọc tài liệu từ: {KB_DIR}")
    pdf_files = glob.glob(os.path.join(KB_DIR, "*.pdf"))
    
    if not pdf_files:
        print("Không tìm thấy file PDF nào trong thư mục knowledge_base.")
        return

    documents = []
    for pdf_path in pdf_files:
        print(f"Đang đọc: {os.path.basename(pdf_path)}...")
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            
            # Làm sạch nội dung từng trang ngay sau khi load
            for doc in docs:
                doc.page_content = clean_rag_text(doc.page_content)
                
            documents.extend(docs)
            print(f"  -> Đã đọc và làm sạch {len(docs)} trang từ {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"  -> Lỗi khi đọc {os.path.basename(pdf_path)}: {e}")

    if not documents:
        print("Không có nội dung nào được đọc.")
        return

    print(f"\nTổng cộng đọc được {len(documents)} trang tài liệu. Bắt đầu chia nhỏ (chunking)...")
    
    # Text splitter config
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Đã chia thành {len(chunks)} chunks.")
    
    # Initialize Local Embeddings (all-MiniLM-L6-v2)
    print("Khởi tạo Local Embeddings (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Save to Chroma
    print(f"Đang lưu vào vector database (Chroma) tại {CHROMA_DIR}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    print("Hoàn tất! Database đã được lưu thành công.")

if __name__ == "__main__":
    ingest_documents()

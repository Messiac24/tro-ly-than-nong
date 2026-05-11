
from langchain_huggingface import HuggingFaceEmbeddings
import sys

try:
    print("Đang kiểm tra kết nối tới Hugging Face Hub...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    test_vec = embeddings.embed_query("Xin chào")
    print("✅ Kết nối Hugging Face thành công! Model đã sẵn sàng.")
except Exception as e:
    print(f"❌ Lỗi kết nối Hugging Face: {e}")
    print("\nGợi ý: Hãy kiểm tra kết nối Internet hoặc thử bật/tắt VPN (nếu có).")

import os
import sys
import io
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CHROMA_DIR = r"D:\AI_nong_san\server\data\chroma_db"
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

if not os.path.exists(CHROMA_DIR):
    print(f"Chroma directory not found at {CHROMA_DIR}")
else:
    vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    query = "Phòng bệnh rỉ sắt"
    results = vectorstore.similarity_search_with_relevance_scores(query, k=5)
    
    print(f"\n--- Search results for '{query}' ---")
    for i, (doc, score) in enumerate(results):
        print(f"[{i+1}] Score: {score:.4f}")
        print(f"Source: {doc.metadata.get('source')}")
        content = doc.page_content.replace('\n', ' ')
        print(f"Content: {content[:300]}...")
        print("-" * 30)

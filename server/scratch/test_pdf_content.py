import os
import sys
import io
from langchain_community.document_loaders import PyPDFLoader

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf_path = r"D:\AI_nong_san\server\data\knowledge_base\so_tay_ca_phe.pdf"
if os.path.exists(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    found = False
    for i, page in enumerate(pages):
        content = page.page_content.lower()
        if "rỉ sắt" in content or "ri sat" in content:
            print(f"Found match on page {i+1}:")
            print(page.page_content[:500])
            print("-" * 50)
            found = True
            # Check for multiple pages
            if i > 5: break 
    if not found:
        print("Keyword not found.")
else:
    print("File not found.")

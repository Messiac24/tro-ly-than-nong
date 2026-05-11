import os
import sys
import io
import glob
from langchain_community.document_loaders import PyPDFLoader

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KB_DIR = r"D:\AI_nong_san\server\data\knowledge_base"
pdf_files = glob.glob(os.path.join(KB_DIR, "*.pdf"))

print(f"Searching in {len(pdf_files)} files...")
for pdf_path in pdf_files:
    print(f"Checking {os.path.basename(pdf_path)}...")
    loader = PyPDFLoader(pdf_path)
    try:
        pages = loader.load()
        for i, page in enumerate(pages):
            content = page.page_content.lower()
            if "rỉ sắt" in content or "ri sat" in content:
                print(f"  [MATCH] Found on page {i+1}")
                # print(page.page_content[:200])
    except:
        print(f"  [ERROR] Could not read {pdf_path}")

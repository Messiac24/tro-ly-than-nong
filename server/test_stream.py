import requests
import json

url = "http://127.0.0.1:8000/api/chat/stream"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "dev-key-ai-nong-san-2026"
}
data = {
    "message": "Cách bón phân cho sầu riêng Ri6 thế nào cho tốt?"
}

print("--- Đang kết nối tới Server (Streaming) ---")
try:
    with requests.post(url, headers=headers, json=data, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=None):
            if chunk:
                print(chunk.decode('utf-8'), end='', flush=True)
except Exception as e:
    print(f"\n❌ Lỗi: {e}")
print("\n--- Kết thúc stream ---")

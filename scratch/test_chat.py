
import requests
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_chat():
    url = "http://127.0.0.1:8000/api/chat"
    # Dùng API Key và Token admin để test
    headers = {
        "X-API-Key": "dev-key-ai-nong-san-2026",
        "Authorization": "Bearer admin_token_here", # Chúng ta sẽ test endpoint public hoặc giả lập user
        "Content-Type": "application/json"
    }
    
    # Để test nhanh, tôi sẽ dùng tài khoản admin vừa tạo
    # Bước 1: Login lấy token
    login_url = "http://127.0.0.1:8000/api/auth/login"
    login_data = {"username": "admin@thannong.ai", "password": "123"}
    login_res = requests.post(login_url, data=login_data)
    token = login_res.json()["access_token"]
    
    headers["Authorization"] = f"Bearer {token}"
    
    payload = {
        "message": "Kỹ thuật chăm sóc sầu riêng?",
        "context": {
            "location": "Phường B'Lao",
            "crop": "Sầu riêng Ri6"
        }
    }
    
    print("--- Đang gửi câu hỏi test tới AI ---")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("\n[AI TRẢ LỜI]:")
        print(result["answer"])
        print("\n--- Kiểm tra định dạng ---")
        answer = result["answer"]
        if answer.startswith("Dạ"):
            print("✅ Có câu chào đầu dòng.")
        if any(char in answer for char in ['|', '*', '+']):
            print("❌ Vẫn còn ký tự rác!")
        else:
            print("✅ Đã sạch ký tự rác.")
            
    else:
        print(f"❌ Lỗi kết nối: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_chat()

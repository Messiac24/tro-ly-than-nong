
import requests
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_chat_history():
    base_url = "http://127.0.0.1:8000/api"
    
    # 1. Đăng nhập
    login_data = {"username": "admin@thannong.ai", "password": "123"}
    login_res = requests.post(f"{base_url}/auth/login", data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-API-Key": "dev-key-ai-nong-san-2026"}
    
    # 2. Gửi tin nhắn mới
    test_msg = "Kiểm tra lưu lịch sử chat " + str(json.dumps(login_data))[:10] # Thêm chút random
    print(f"--- Đang gửi tin nhắn test: '{test_msg}' ---")
    
    chat_payload = {
        "message": test_msg,
        "context": {"location": "Phường B'Lao", "crop": "Cà phê"}
    }
    requests.post(f"{base_url}/chat", json=chat_payload, headers=headers)
    
    # 3. Lấy lịch sử
    print("--- Đang truy xuất lịch sử chat từ Database ---")
    history_res = requests.get(f"{base_url}/chat/history", headers=headers)
    history = history_res.json()
    
    if len(history) > 0:
        last_chat = history[-1]
        print(f"\n✅ Thành công! Tìm thấy {len(history)} tin nhắn trong lịch sử.")
        print(f"Tin nhắn cuối cùng: Q: {last_chat['question']} | A: {last_chat['answer'][:50]}...")
        
        if last_chat['question'] == test_msg:
            print("✨ XÁC NHẬN: Hệ thống đã lưu đúng tin nhắn vừa gửi!")
        else:
            print("⚠️ Cảnh báo: Tin nhắn cuối cùng không khớp!")
    else:
        print("❌ Lỗi: Không tìm thấy lịch sử chat trong Database!")

if __name__ == "__main__":
    test_chat_history()

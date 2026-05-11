import requests
import json
import sys
import io

# Setup UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api"
API_KEY = "dev-key-ai-nong-san-2026"

def run_tests():
    print("🚀 Bắt đầu Master Test cho dự án Trợ Lý Thần Nông...\n")
    
    # 1. Login
    print("--- 1. Kiểm tra Đăng nhập ---")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    # OAuth2PasswordRequestForm expects data as form-data
    r_login = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if r_login.status_code != 200:
        print(f"❌ Đăng nhập thất bại: {r_login.text}")
        return
    
    token = r_login.json()["access_token"]
    print("✅ Đăng nhập thành công!")
    
    headers = {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 2. Predict API
    print("\n--- 2. Kiểm tra Dự báo (Predict) ---")
    predict_data = {
        "location": "Phường B'Lao",
        "crop": "Cà phê Robusta",
        "mode": "Kinh doanh",
        "capital": 500000000,
        "area_ha": 2.5
    }
    r_predict = requests.post(f"{BASE_URL}/predict", headers=headers, json=predict_data)
    if r_predict.status_code == 200:
        res = r_predict.json()
        print(f"✅ Predict thành công!")
        print(f"   Vùng: {res['location_info']['name']}")
        print(f"   Mức rủi ro: {res['action_plan']['level']}")
        if "price_forecast" in res:
            print(f"   Dự báo giá ngày mai: {res['price_forecast']['forecast_30_days'][0]['predicted']:,.0f} VND")
    else:
        print(f"❌ Predict thất bại: {r_predict.text}")

    # 3. Chat API
    print("\n--- 3. Kiểm tra Chat RAG ---")
    chat_data = {
        "message": "Cách bón phân cho cà phê vối?",
        "history": [],
        "context": predict_data
    }
    r_chat = requests.post(f"{BASE_URL}/chat", headers=headers, json=chat_data)
    if r_chat.status_code == 200:
        res = r_chat.json()
        print(f"✅ Chat thành công!")
        print(f"   AI trả lời: {res['answer'][:150]}...")
    else:
        print(f"❌ Chat thất bại: {r_chat.text}")

    # 4. Admin API
    print("\n--- 4. Kiểm tra Admin Dashboard ---")
    r_stats = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
    if r_stats.status_code == 200:
        print(f"✅ Admin Stats thành công!")
        print(f"   Stats: {r_stats.json()}")
    else:
        print(f"❌ Admin Stats thất bại: {r_stats.text}")

    print("\n🎉 Hoàn tất kiểm tra!")

if __name__ == "__main__":
    run_tests()

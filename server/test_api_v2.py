import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "dev-key-ai-nong-san-2026"

def test_prediction():
    # 1. Login
    login_url = f"{BASE_URL}/api/auth/login"
    login_data = {"username": "admin", "password": "admin123"}
    resp = requests.post(login_url, data=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} - {resp.text}")
        return
    
    token = resp.json()["access_token"]
    print("Login success, token acquired.")

    # 2. Predict
    predict_url = f"{BASE_URL}/api/predict"
    headers = {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "location": "Phường B'Lao",
        "crop": "Sầu riêng Ri6",
        "capital": 500000000,
        "area_ha": 2.5,
        "mode": "Kinh doanh"
    }
    
    print(f"Sending prediction request for {payload['crop']} at {payload['location']}...")
    resp = requests.post(predict_url, headers=headers, json=payload)
    
    if resp.status_code == 200:
        print("✅ Prediction success!")
        result = resp.json()
        print(f"Status: {result['status']}")
        print(f"Risk Level: {result['action_plan']['level']}")
        print(f"Recommendation: {result['production_decision']['recommendation']}")
    else:
        print(f"❌ Prediction failed: {resp.status_code}")
        print(f"Error: {resp.text}")

if __name__ == "__main__":
    test_prediction()

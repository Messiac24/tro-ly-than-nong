import requests
import json

url = "http://localhost:8000/api/predict"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "dev-key-ai-nong-san-2026"
}
data = {
    "location": "Phường B'Lao",
    "crop": "Chè Ô Long",
    "mode": "Kinh doanh",
    "capital": 1000000000,
    "area_ha": 2.0
}

response = requests.post(url, headers=headers, json=data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

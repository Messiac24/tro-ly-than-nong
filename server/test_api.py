import requests
import json

url = "http://127.0.0.1:8000/api/auth/forgot-password"
data = {"email": "hoanglocdalat@gmail.com"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

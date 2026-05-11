import os
import sys
import io
import requests
import json
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GOOGLE_API_KEY")
url = "https://openrouter.ai/api/v1/chat/completions"

models_to_test = [
    "google/gemini-flash-1.5",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-pro-1.5",
    "google/gemini-flash-1.5-8b"
]

print(f"Testing OpenRouter with Key: {api_key[:15]}...")

for model in models_to_test:
    print(f"\n--- Testing model: {model} ---")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Tro Ly Than Nong",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "OK"}]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        if response.status_code == 200:
            print(f"SUCCESS: {model} is working!")
            print(f"Response: {response.json()['choices'][0]['message']['content']}")
        else:
            print(f"FAILED: {model} returned {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

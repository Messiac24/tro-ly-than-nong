import os
import sys
import io
import requests
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GOOGLE_API_KEY")
url = "https://openrouter.ai/api/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}"
}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        models = response.json().get('data', [])
        print(f"Total models available: {len(models)}")
        # Filter for gemini or llama
        found = [m['id'] for m in models if "gemini" in m['id'].lower() or "llama" in m['id'].lower()]
        for f in found[:20]:
            print(f"- {f}")
    else:
        print(f"FAILED: {response.status_code}")
except Exception as e:
    print(f"ERROR: {e}")

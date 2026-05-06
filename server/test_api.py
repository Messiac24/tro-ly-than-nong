# -*- coding: utf-8 -*-
"""Test API endpoint trực tiếp"""
import sys, io, json, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API = "http://localhost:8000/api/predict"
HEADERS = {"X-API-Key": "dev-key-ai-nong-san-2026", "Content-Type": "application/json"}

def test_api(desc, body):
    print(f"\n{'='*60}")
    print(f"TEST: {desc}")
    print(f"{'='*60}")
    r = requests.post(API, headers=HEADERS, json=body)
    data = r.json()
    
    # Chỉ in phần quan trọng
    if "action_plan" in data:
        ap = data["action_plan"]
        print(f"  Level: {ap['level']}")
        print(f"  Risk Score: {ap['risk_score']}")
        print(f"  Message: {ap['message']}")
        if ap.get('reasoning'):
            print(f"  Reasoning: {ap['reasoning'][:200]}...")
    if data.get("crop_alternatives"):
        print(f"  Cây thay thế: {data['crop_alternatives']}")
    if data.get("production_decision"):
        print(f"  Khuyến nghị: {data['production_decision']['recommendation']}")
    print()

# Test 1: Robusta + Xuân Trường (1500m) → PHẢI ĐỎ
test_api("Robusta + Xuân Trường (1500m) → PHẢI BÁO ĐỎ", {
    "location": "Phường Xuân Trường",
    "crop": "Cà phê Robusta",
    "capital": 500000000,
    "area_ha": 2.0
})

# Test 2: Sầu riêng + Xuân Trường → PHẢI ĐỎ  
test_api("Sầu riêng + Xuân Trường (1500m) → PHẢI BÁO ĐỎ", {
    "location": "Phường Xuân Trường",
    "crop": "Sầu riêng Ri6",
    "capital": 500000000,
    "area_ha": 2.0
})

# Test 3: Arabica + B'Lao → PHẢI ĐỎ
test_api("Arabica + B'Lao (800m) → PHẢI BÁO ĐỎ", {
    "location": "Phường B'Lao",
    "crop": "Cà phê Arabica",
    "capital": 500000000,
    "area_ha": 2.0
})

# Test 4: Chè Ô Long + B'Lao → PHẢI VÀNG
test_api("Chè Ô Long + B'Lao (800m) → PHẢI BÁO VÀNG", {
    "location": "Phường B'Lao",
    "crop": "Chè Ô Long",
    "capital": 500000000,
    "area_ha": 2.0
})

# Test 5: Robusta + B'Lao → AN TOÀN
test_api("Robusta + B'Lao (800m) → AN TOÀN", {
    "location": "Phường B'Lao",
    "crop": "Cà phê Robusta",
    "capital": 500000000,
    "area_ha": 2.0
})

# Test 6: Arabica + Xuân Trường → AN TOÀN  
test_api("Arabica + Xuân Trường (1500m) → AN TOÀN", {
    "location": "Phường Xuân Trường",
    "crop": "Cà phê Arabica",
    "capital": 500000000,
    "area_ha": 2.0
})

print("\n✅ Tất cả API tests đã chạy xong!")

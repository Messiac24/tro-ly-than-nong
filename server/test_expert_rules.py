# -*- coding: utf-8 -*-
"""Test expert rules"""
import sys
import io
import json

# Fix encoding trên Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, '.')
from ml.expert_rules import run_expert_check

print("=" * 60)
print("TEST 1: Robusta ở Xuân Trường (1500m) → PHẢI BÁO ĐỎ")
print("=" * 60)
result = run_expert_check(
    crop_name="Cà phê Robusta",
    location_name="Phường Xuân Trường",
    elevation=1500,
    temp_max=28.5, temp_min=19.0, precipitation=15.0
)
print(json.dumps(result, ensure_ascii=False, indent=2))

print("\n" + "=" * 60)
print("TEST 2: Sầu riêng ở Xuân Trường (1500m) → PHẢI BÁO ĐỎ")
print("=" * 60)
result2 = run_expert_check(
    crop_name="Sầu riêng Ri6",
    location_name="Phường Xuân Trường",
    elevation=1500,
    temp_max=22.0, temp_min=12.0, precipitation=15.0
)
print(json.dumps(result2, ensure_ascii=False, indent=2))

print("\n" + "=" * 60)
print("TEST 3: Arabica ở B'Lao (800m) → PHẢI BÁO ĐỎ/VÀNG")
print("=" * 60)
result3 = run_expert_check(
    crop_name="Cà phê Arabica",
    location_name="Phường B'Lao",
    elevation=800,
    temp_max=30.0, temp_min=22.0, precipitation=15.0
)
print(json.dumps(result3, ensure_ascii=False, indent=2))

print("\n" + "=" * 60)
print("TEST 4: Chè Ô Long ở B'Lao (800m) → PHẢI BÁO VÀNG")
print("=" * 60)
result4 = run_expert_check(
    crop_name="Chè Ô Long",
    location_name="Phường B'Lao",
    elevation=800,
    temp_max=30.0, temp_min=22.0, precipitation=15.0
)
print(json.dumps(result4, ensure_ascii=False, indent=2))

print("\n" + "=" * 60)
print("TEST 5: Robusta ở B'Lao (800m) → AN TOÀN ✓")
print("=" * 60)
result5 = run_expert_check(
    crop_name="Cà phê Robusta",
    location_name="Phường B'Lao",
    elevation=800,
    temp_max=28.5, temp_min=19.0, precipitation=15.0
)
print(json.dumps(result5, ensure_ascii=False, indent=2))

print("\n" + "=" * 60)
print("TEST 6: Arabica ở Xuân Trường (1500m) → AN TOÀN ✓")
print("=" * 60)
result6 = run_expert_check(
    crop_name="Cà phê Arabica",
    location_name="Phường Xuân Trường",
    elevation=1500,
    temp_max=22.0, temp_min=12.0, precipitation=15.0
)
print(json.dumps(result6, ensure_ascii=False, indent=2))

print("\n" + "=" * 60)
print("TEST 7: Sầu riêng ở B'Lao + Mưa lớn 80mm → Cảnh báo nấm rễ")
print("=" * 60)
result7 = run_expert_check(
    crop_name="Sầu riêng Ri6",
    location_name="Phường B'Lao",
    elevation=800,
    temp_max=28.0, temp_min=22.0, precipitation=80.0
)
print(json.dumps(result7, ensure_ascii=False, indent=2))

print("\n✅ Tất cả test cases đã chạy xong!")

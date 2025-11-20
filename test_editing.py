#!/usr/bin/env python3
"""Test editing flow"""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

def step(name, message):
    print(f"\n{'='*60}\n{name}\n{'='*60}")
    r = requests.post(f"{BASE_URL}/api/listing/start", json={
        "user_id": USER_ID,
        "message": message,
        "platform": "web"
    })
    result = r.json()
    print(f"Type: {result.get('type')}")
    print(f"Message: {result.get('message', '')[:200]}...")
    return result

print("🧪 Testing Editing Flow\n")

# 1. Create listing
step("1️⃣ Create listing", "Endüstriyel rotor satmak istiyorum")

# 2. Request edit
step("2️⃣ Request edit", "Düzenle")

# 3. Edit title
result = step("3️⃣ Edit title", "başlığı daha çekici yap")

# Check if edit worked
if result.get('type') == 'listing_preview':
    print("\n✅ Editing flow SUCCESS!")
    print(f"\nNew title: {result.get('data', {}).get('title', 'N/A')}")
else:
    print(f"\n❌ Editing failed: {result.get('type')}")

print("\n" + "="*60)

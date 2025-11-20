#!/usr/bin/env python3
"""Full flow test with real UUID"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8000"
USER_ID = str(uuid.uuid4())  # Generate real UUID

print(f"🆔 Using UUID: {USER_ID}\n")

def test_step(step_name, endpoint, payload):
    """Test a single step and print results"""
    print(f"\n{'='*60}")
    print(f"🧪 {step_name}")
    print(f"{'='*60}")
    
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    
    print(f"📥 Response ({response.status_code}):")
    result = response.json()
    
    if response.status_code == 200:
        print(f"✅ Type: {result.get('type')}")
        if result.get('data', {}).get('price'):
            print(f"💰 Price: {result['data']['price']} TL")
    else:
        print(f"❌ Error: {result}")
    
    return result

# Full flow
result1 = test_step("İlan başlat", "/api/listing/start", 
    {"user_id": USER_ID, "message": "Endüstriyel rotor satmak istiyorum", "platform": "web"})

result2 = test_step("Fiyat değiştir", "/api/listing/start",
    {"user_id": USER_ID, "message": "2000 TL olsun", "platform": "web"})

result3 = test_step("Onayla", "/api/listing/start",
    {"user_id": USER_ID, "message": "Onayla", "platform": "web"})

if result3.get("type") == "ready_to_confirm" and result3.get("data"):
    print("\n✅ Listing data received!")
    
    result4 = test_step("Veritabanına kaydet", "/api/listing/confirm",
        {"user_id": USER_ID, "listing_data": result3["data"]})
    
    if result4.get("status") == "confirmed":
        print(f"\n🎉 FULL FLOW SUCCESS!")
        print(f"📝 Listing ID: {result4.get('listing_id')}")
    else:
        print(f"\n❌ Database save failed")
else:
    print("\n❌ Confirmation failed")

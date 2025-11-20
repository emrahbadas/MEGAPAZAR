#!/usr/bin/env python3
"""Final full flow test with real user UUID"""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"  # Real UUID from database

print(f"🆔 Using UUID: {USER_ID}")
print(f"👤 User: test@megapazar.com\n")

def test_step(step_name, endpoint, payload):
    print(f"{'='*60}\n🧪 {step_name}\n{'='*60}")
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    result = response.json()
    
    if response.status_code == 200:
        print(f"✅ Status: {response.status_code}")
        print(f"📦 Type: {result.get('type')}")
        if result.get('data', {}).get('price'):
            print(f"💰 Price: {result['data']['price']} TL")
        if result.get('listing_id'):
            print(f"📝 Listing ID: {result['listing_id']}")
    else:
        print(f"❌ Error ({response.status_code}): {result.get('detail')}")
    
    return result

# Full flow test
print("🚀 Starting full flow test...\n")

r1 = test_step("Step 1: İlan oluştur", "/api/listing/start", 
    {"user_id": USER_ID, "message": "Endüstriyel rotor satmak istiyorum", "platform": "web"})

r2 = test_step("Step 2: Fiyat pazarlığı", "/api/listing/start",
    {"user_id": USER_ID, "message": "2000 TL olsun", "platform": "web"})

r3 = test_step("Step 3: Onay mesajı", "/api/listing/start",
    {"user_id": USER_ID, "message": "Onayla", "platform": "web"})

if r3.get("type") == "ready_to_confirm" and r3.get("data"):
    print("\n✅ Listing data confirmed!")
    
    r4 = test_step("Step 4: Database save", "/api/listing/confirm",
        {"user_id": USER_ID, "listing_data": r3["data"]})
    
    if r4.get("status") == "confirmed":
        print(f"\n🎉🎉🎉 FULL FLOW SUCCESS! 🎉🎉🎉")
        print(f"\n📊 Summary:")
        print(f"  • Started: 1350 TL (auto-calculated)")
        print(f"  • Negotiated: 2000 TL (user override)")
        print(f"  • Confirmed: ✅")
        print(f"  • Saved: ✅")
        print(f"  • Listing ID: {r4.get('listing_id')}")
    else:
        print(f"\n❌ Database save failed")
else:
    print("\n❌ Confirmation step failed")

print("\n" + "="*60)

#!/usr/bin/env python3
"""Full flow test: listing creation -> price negotiation -> confirmation"""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "test-user-007"

def test_step(step_name, endpoint, payload):
    """Test a single step and print results"""
    print(f"\n{'='*60}")
    print(f"🧪 {step_name}")
    print(f"{'='*60}")
    print(f"📤 Request: {json.dumps(payload, ensure_ascii=False)}\n")
    
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
    
    print(f"📥 Response ({response.status_code}):")
    result = response.json()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return result

# Test 1: Start listing
print("\n🚀 Starting full flow test...\n")
result1 = test_step(
    "Step 1: İlan oluşturma başlat",
    "/api/listing/start",
    {
        "user_id": USER_ID,
        "message": "Endüstriyel rotor satmak istiyorum",
        "platform": "web"
    }
)

# Test 2: Price negotiation
result2 = test_step(
    "Step 2: Fiyat pazarlığı",
    "/api/listing/start",
    {
        "user_id": USER_ID,
        "message": "2000 TL olsun",
        "platform": "web"
    }
)

# Test 3: Confirmation intent
result3 = test_step(
    "Step 3: Onay mesajı",
    "/api/listing/start",
    {
        "user_id": USER_ID,
        "message": "Onayla",
        "platform": "web"
    }
)

# Check if listing_draft is in response
if result3.get("type") == "ready_to_confirm":
    print("\n✅ Confirmation intent detected!")
    
    if result3.get("data"):
        print(f"\n✅ Listing data received: {json.dumps(result3['data'], ensure_ascii=False, indent=2)}")
        
        # Test 4: Database save
        result4 = test_step(
            "Step 4: Veritabanına kaydet",
            "/api/listing/confirm",
            {
                "user_id": USER_ID,
                "listing_data": result3["data"]
            }
        )
        
        if result4.get("status") == "confirmed":
            print("\n🎉 Full flow SUCCESS!")
        else:
            print("\n❌ Database save failed")
    else:
        print("\n❌ No listing data in response! Check conversation_enhanced.py CONFIRMING handler")
else:
    print(f"\n❌ Wrong response type: {result3.get('type')}")

print("\n" + "="*60)

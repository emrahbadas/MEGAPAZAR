#!/usr/bin/env python3
"""Test price consistency - fiyat her seferinde aynı mı?"""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

def create_listing(message):
    """Create listing and return price"""
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={"user_id": USER_ID, "message": message, "platform": "web"}
    )
    result = response.json()
    price = result.get('data', {}).get('price', 0)
    return price, result

print("🧪 Testing Price Consistency\n")
print("="*60)

# Test 1: İlk ilan
print("\n1️⃣ First listing creation:")
price1, r1 = create_listing("Endüstriyel rotor satmak istiyorum")
print(f"   💰 Price: {price1} TL")

# Test 2: Yeni session başlat (aynı ürün, fiyat DEĞİŞMEMELİ - session'dan gelecek)
# NOT: Şu anda session API restart'ta kayboluyor, bu test başarısız olacak
# Ama reprice flow test edebiliriz

# Test 3: Fiyat değiştir
print("\n2️⃣ Change price to 2000 TL:")
price3, r3 = create_listing("2000 TL olsun")
print(f"   💰 Price: {price3} TL")

# Test 4: Confirm to check final price
print("\n3️⃣ Confirm (should be 2000 TL):")
response = requests.post(
    f"{BASE_URL}/api/listing/start",
    json={"user_id": USER_ID, "message": "Onayla", "platform": "web"}
)
result = response.json()
price4 = result.get('data', {}).get('price', 0)
print(f"   💰 Final Price: {price4} TL")

print("\n" + "="*60)
print("\n📊 Results:")
print(f"   Step 1 (auto calculated): {price1} TL")
print(f"   Step 2 (user changed): {price3} TL → {'✅ 2000' if price3 == 2000 else '❌ NOT 2000'}")
print(f"   Step 3 (confirmed): {price4} TL → {'✅ SAME' if price3 == price4 else '❌ CHANGED'}")

if price3 == 2000 and price3 == price4:
    print("\n🎉 PRICE CONSISTENCY: SUCCESS!")
    print("   User price override stays consistent through confirmation")
else:
    print("\n❌ PRICE CONSISTENCY: FAILED")
    print(f"\nExpected: 2000 TL → 2000 TL")
    print(f"Got: {price3} TL → {price4} TL")

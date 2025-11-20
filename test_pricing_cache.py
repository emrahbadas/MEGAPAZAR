#!/usr/bin/env python3
"""Test: Aynı session'da pricing agent birden fazla çağrılınca fiyat değişir mi?"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

def test_multiple_listings_same_session():
    """Aynı kullanıcı birden fazla listing oluşturursa fiyat tutarlı mı?"""
    USER_ID = str(uuid.uuid4())  # Yeni user
    
    print(f"🆔 User: {USER_ID[:8]}...\n")
    print("="*60)
    
    # İlk ilan: Endüstriyel rotor
    print("\n📝 Creating first listing...")
    r1 = requests.post(f"{BASE_URL}/api/listing/start", json={
        "user_id": USER_ID,
        "message": "Endüstriyel rotor satmak istiyorum",
        "platform": "web"
    })
    price1 = r1.json().get('data', {}).get('price', 0)
    print(f"   💰 Price: {price1} TL")
    
    # İkinci ilan: Aynı ürün tekrar (session'da pricing OLMALI)
    print("\n📝 Creating second listing (same product)...")
    r2 = requests.post(f"{BASE_URL}/api/listing/start", json={
        "user_id": USER_ID,
        "message": "Yine endüstriyel rotor var",
        "platform": "web"
    })
    price2 = r2.json().get('data', {}).get('price', 0)
    print(f"   💰 Price: {price2} TL")
    
    # Üçüncü ilan: Tamamen farklı ürün (pricing YOK, yeni hesaplama yapmalı)
    print("\n📝 Creating third listing (different product)...")
    r3 = requests.post(f"{BASE_URL}/api/listing/start", json={
        "user_id": USER_ID,
        "message": "Hidrolik pres satıyorum",
        "platform": "web"
    })
    price3 = r3.json().get('data', {}).get('price', 0)
    print(f"   💰 Price: {price3} TL")
    
    print("\n" + "="*60)
    print("\n📊 Analysis:")
    print(f"   Listing 1 (rotor): {price1} TL")
    print(f"   Listing 2 (rotor again): {price2} TL")
    print(f"   Listing 3 (different): {price3} TL")
    
    # BUG: İdeal davranış şu olmalı:
    # - Listing 1-2: Aynı fiyat (session'da pricing cached)
    # - Listing 3: Farklı fiyat (yeni ürün, yeni pricing)
    
    # AMA şu anda ne oluyor?
    # Session her yeni listing başlattığında RESET edilmiyor
    # Yani pricing her zaman session'da kalıyor
    
    if price1 == price2:
        print("\n✅ Same product → Same price (GOOD)")
    else:
        print(f"\n⚠️  Same product but different prices: {price1} vs {price2}")
        print("   → PricingAgent cache working, but maybe product changed?")
    
    if price1 != price3:
        print("✅ Different product → Different price (GOOD)")
    else:
        print("❌ Different product but same price!")
        print("   → BUG: Session pricing not cleared for new product")

if __name__ == "__main__":
    print("\n🧪 Testing: Pricing consistency across multiple listings\n")
    test_multiple_listings_same_session()

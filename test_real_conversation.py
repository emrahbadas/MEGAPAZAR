import requests
import json
import time

BASE_URL = "http://localhost:8000"
USER_ID = "+905551234567"

def send_message(message: str):
    """n8n gibi mesaj gönder"""
    response = requests.post(
        f"{BASE_URL}/conversation",
        json={
            "user_id": USER_ID,
            "message": message,
            "platform": "whatsapp"
        }
    )
    
    result = response.json()
    print(f"\n👤 Kullanıcı: {message}")
    print(f"🤖 Bot: {result.get('message', 'Yanıt yok')}")
    print(f"   Intent: {result.get('intent', 'unknown')}")
    print(f"   Response Type: {result.get('response_type', 'N/A')}")
    
    if result.get('data'):
        print(f"   Data: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
    
    return result

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 GERÇEK KONUŞMA TESTİ")
    print("=" * 60)
    
    # Konuşma akışı
    messages = [
        "Ürün satmak istiyorum",
        "Laptop bilgisayar",
        "2.el hp marka satın aldığım sene 2020",
        "Ben 10 bin tl istiyorum ama piyasa fiyatına göre karar vericem"
    ]
    
    for msg in messages:
        send_message(msg)
        time.sleep(1)  # Rate limiting için
    
    print("\n" + "=" * 60)
    print("✅ Test tamamlandı!")
    print("=" * 60)

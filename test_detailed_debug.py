import requests
import time

API_URL = "http://localhost:8000/conversation"
USER_ID = "+905551234567"

messages = [
    "Ürün satmak istiyorum",
    "Laptop bilgisayar",
    "2.el hp marka satın aldığım sene 2020",
    "Ben 10 bin tl istiyorum ama piyasa fiyatına göre karar vericem"
]

print("=" * 60)
print("🧪 DETAILED DEBUG TEST")
print("=" * 60)
print()

# Delete session first
import os
session_file = f"sessions/session_{USER_ID}.pkl"
if os.path.exists(session_file):
    os.remove(session_file)
    print(f"✅ Deleted old session: {session_file}\n")

for i, msg in enumerate(messages, 1):
    print(f"👤 Message {i}: {msg}")
    
    response = requests.post(API_URL, json={
        "user_id": USER_ID,
        "message": msg
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"🤖 Bot: {data.get('message', 'NO MESSAGE')}")
        print(f"   Intent: {data.get('intent')}")
        print(f"   Response Type: {data.get('response_type')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    print()
    time.sleep(0.5)

print("=" * 60)
print("✅ Test complete")
print("=" * 60)

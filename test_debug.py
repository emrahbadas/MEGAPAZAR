import requests

r = requests.post(
    'http://localhost:8000/conversation',
    json={
        'user_id': '+905551234567',
        'message': 'Ürün satmak istiyorum',
        'platform': 'whatsapp'
    }
)

result = r.json()
print(f"\n✅ Response Type: {result.get('response_type')}")
print(f"✅ Intent: {result.get('intent')}")
print(f"✅ Message: {result.get('message')[:100]}...")

"""
Minimal test endpoint - agent olmadan
"""
import requests

r = requests.post(
    'http://localhost:8000/test-simple',
    json={
        'user_id': '+905551234567',
        'message': 'Ürün satmak istiyorum',
        'platform': 'whatsapp'
    }
)

print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")

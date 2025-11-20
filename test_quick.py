import requests
import traceback

try:
    response = requests.post(
        "http://localhost:8000/conversation",
        json={
            "user_id": "+905551234567",
            "message": "Ürün satmak istiyorum",
            "platform": "whatsapp"
        },
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    traceback.print_exc()

import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "+905551234567"

def send_message(message: str):
    """Test single message"""
    response = requests.post(
        f"{BASE_URL}/conversation",
        json={
            "user_id": USER_ID,
            "message": message,
            "platform": "whatsapp"
        }
    )
    
    result = response.json()
    print(f"\n👤 USER: {message}")
    print(f"🤖 BOT: {result.get('message', 'No response')}")
    print(f"   Intent: {result.get('intent', 'unknown')}")
    print(f"   Response Type: {result.get('response_type', 'N/A')}")
    
    if result.get('data'):
        print(f"   Data: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
    
    return result

if __name__ == "__main__":
    message = input("Enter message: ")
    send_message(message)

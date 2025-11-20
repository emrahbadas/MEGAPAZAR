import requests
import json
import os

# Clear session via API
clear_response = requests.post("http://localhost:8000/debug/clear-session", params={"user_id": "+905551234567"})
print(f"Clear session: {clear_response.json()}\n")

session_file = "sessions/session__905551234567.pkl"  # Actual filename used

# Send first message
response = requests.post("http://localhost:8000/conversation", json={
    "user_id": "+905551234567",
    "message": "Ürün satmak istiyorum"
})

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Bot: {data.get('message')}")
    print(f"Intent: {data.get('intent')}")
    print(f"Response Type: {data.get('response_type')}")
else:
    print(f"Error: {response.text}")

print("\n--- Checking session file ---")
if os.path.exists(session_file):
    import pickle
    with open(session_file, 'rb') as f:
        session = pickle.load(f)
    print(f"Stage: {session.stage}")
    print(f"Intent: {session.intent}")
    print(f"Product Info: {session.product_info}")
    print(f"Missing Fields: {session.missing_fields}")
else:
    print("❌ Session file not found!")

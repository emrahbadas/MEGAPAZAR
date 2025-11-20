"""
End-to-end session persistence test with API
"""
import requests
import time

BASE_URL = "http://localhost:8000"
USER_ID = "persistence-test-user"

def test_e2e_persistence():
    print("E2E SESSION PERSISTENCE TEST")
    print("=" * 60)
    
    # Step 1: Start a conversation
    print("\nStep 1: Start conversation")
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "Araba satmak istiyorum"
        }
    )
    data = response.json()
    print(f"Response: {data['message'][:100]}...")
    
    # Step 2: Provide first answer
    print("\nStep 2: Provide brand")
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "Mercedes"
        }
    )
    data = response.json()
    print(f"Response: {data['message'][:100]}...")
    
    print("\n" + "=" * 60)
    print("API will now restart. Session should persist.")
    print("Please restart the API manually, then press Enter to continue...")
    input()
    
    # Step 3: Continue conversation after restart
    print("\nStep 3: Continue after restart")
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "C180 2015 model"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Response received: {data['message'][:100]}...")
        
        # Check if context was preserved
        if "Mercedes" in str(data) or "C180" in str(data):
            print("\nSUCCESS: Session context preserved after restart!")
        else:
            print("\nWARNING: Context might be lost, but API responded")
    else:
        print(f"ERROR: API returned {response.status_code}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")

if __name__ == "__main__":
    try:
        test_e2e_persistence()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

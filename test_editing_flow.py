"""
Test script for editing flow
"""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

def test_editing_flow():
    print("🧪 EDITING FLOW TEST")
    print("=" * 60)
    
    # Step 1: Create listing
    print("\n📝 Step 1: Creating listing...")
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "Endüstriyel rotor satmak istiyorum"
        }
    )
    data = response.json()
    print(f"✅ Response: {data['response'][:100]}...")
    print(f"📊 Stage: {data['stage']}")
    
    # Step 2: Get preview
    print("\n👀 Step 2: Getting preview...")
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "Önizle"
        }
    )
    data = response.json()
    print(f"✅ Response: {data['response'][:150]}...")
    print(f"📊 Stage: {data['stage']}")
    
    # Step 3: Edit - request to edit title
    print("\n✏️ Step 3: Requesting to edit title...")
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "Düzenle"
        }
    )
    data = response.json()
    print(f"✅ Response: {data['response'][:150]}...")
    print(f"📊 Stage: {data['stage']}")
    
    # Step 4: Specify edit
    print("\n🔧 Step 4: Specifying edit - make title more attractive...")
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "başlığı daha çekici yap"
        }
    )
    data = response.json()
    print(f"✅ Response: {data['response'][:200]}...")
    print(f"📊 Stage: {data['stage']}")
    
    # Step 5: Check new preview
    print("\n🎯 Step 5: Checking new preview...")
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "Önizle"
        }
    )
    data = response.json()
    print(f"✅ Response: {data['response'][:200]}...")
    print(f"📊 Stage: {data['stage']}")
    
    # Step 6: Test price editing
    print("\n💰 Step 6: Testing price edit...")
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "Düzenle"
        }
    )
    print(f"✅ Response: {data['response'][:100]}...")
    
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "fiyatı 3000 TL yap"
        }
    )
    data = response.json()
    print(f"✅ Response: {data['response'][:200]}...")
    print(f"📊 Stage: {data['stage']}")
    
    # Final preview
    print("\n✨ Final Preview:")
    response = requests.post(
        f"{BASE_URL}/api/listing/start",
        json={
            "user_id": USER_ID,
            "message": "Önizle"
        }
    )
    data = response.json()
    print(f"✅ {data['response']}")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETED!")

if __name__ == "__main__":
    try:
        test_editing_flow()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

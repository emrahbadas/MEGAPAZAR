"""
Test price monitoring system
"""
import requests
import time

BASE_URL = "http://localhost:8000"
USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

def test_price_monitoring():
    print("PRICE MONITORING TEST")
    print("=" * 60)
    
    # Step 1: Manually trigger price check
    print("\nStep 1: Trigger price check (admin endpoint)")
    response = requests.post(f"{BASE_URL}/api/admin/check-prices")
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Price check completed")
        print(f"   Result: {data.get('result')}")
    else:
        print(f"ERROR: {response.status_code}")
        print(f"   {response.text}")
        return
    
    # Step 2: Wait a bit for processing
    print("\nStep 2: Waiting for notifications...")
    time.sleep(2)
    
    # Step 3: Get notifications
    print("\nStep 3: Get user notifications")
    response = requests.get(
        f"{BASE_URL}/api/notifications",
        params={"user_id": USER_ID}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Found {data['count']} notifications ({data['unread_count']} unread)")
        
        for notif in data['notifications'][:3]:  # Show first 3
            print(f"\n   📬 {notif['title']}")
            print(f"      Type: {notif['type']}")
            print(f"      Read: {'✅' if notif['is_read'] else '❌'}")
            if notif.get('metadata'):
                meta = notif['metadata']
                print(f"      User price: {meta.get('user_price')} TL")
                print(f"      Market price: {meta.get('market_price')} TL")
                print(f"      Difference: {meta.get('difference_percent')}%")
    else:
        print(f"ERROR: {response.status_code}")
        print(f"   {response.text}")
        return
    
    # Step 4: Mark first notification as read
    if data['notifications'] and not data['notifications'][0]['is_read']:
        notif_id = data['notifications'][0]['id']
        print(f"\nStep 4: Mark notification as read")
        response = requests.post(
            f"{BASE_URL}/api/notifications/{notif_id}/mark-read",
            params={"user_id": USER_ID}
        )
        
        if response.status_code == 200:
            print(f"OK Notification marked as read")
        else:
            print(f"ERROR: {response.status_code}")
    
    # Step 5: Get only unread notifications
    print("\nStep 5: Get unread notifications only")
    response = requests.get(
        f"{BASE_URL}/api/notifications",
        params={"user_id": USER_ID, "unread_only": True}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Found {data['count']} unread notifications")
    else:
        print(f"ERROR: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("\nNote: Check Supabase notifications table for full data")

if __name__ == "__main__":
    try:
        test_price_monitoring()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

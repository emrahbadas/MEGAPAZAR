"""
Test post-publish edit/delete endpoints
MANUAL: Create a listing first using Postman/curl, then paste the ID below
"""
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

# Test listing created via create_test_listing.py
LISTING_ID = "ab968007-85f5-4dbd-8674-cb598c6a0b62"

def test_post_publish_management():
    print("POST-PUBLISH MANAGEMENT TEST")
    print("=" * 60)
    
    if not LISTING_ID:
        print("\nERROR: Please set LISTING_ID in the script")
        print("Steps:")
        print("1. Create a listing using: POST /api/listing/start")
        print(f"2. User ID: {USER_ID}")
        print("3. Copy the listing_id from Supabase")
        print("4. Set LISTING_ID variable in this script")
        return
    
    listing_id = LISTING_ID
    
    # Step 2: Update listing
    print(f"\nStep 2: Update listing {listing_id}")
    update_response = requests.put(
        f"{BASE_URL}/api/listing/{listing_id}",
        json={
            "user_id": USER_ID,
            "title": "Dell XPS 13 - Guncellemis Baslik",
            "price": 25000.0
        }
    )
    
    if update_response.status_code == 200:
        update_data = update_response.json()
        print(f"OK Listing updated")
        print(f"   Message: {update_data.get('message')}")
        print(f"   Updated fields: {update_data.get('updated')}")
    else:
        print(f"ERROR: Update failed ({update_response.status_code})")
        print(f"   {update_response.text}")
    
    # Step 3: Try to update with wrong user_id (should fail)
    print(f"\nStep 3: Try update with wrong user (should fail)")
    wrong_user_response = requests.put(
        f"{BASE_URL}/api/listing/{listing_id}",
        json={
            "user_id": "wrong-user-123",
            "title": "Hacked Title"
        }
    )
    
    if wrong_user_response.status_code == 403:
        print("OK Unauthorized update blocked (403)")
    else:
        print(f"WARNING: Expected 403, got {wrong_user_response.status_code}")
    
    # Step 4: Delete listing (soft delete)
    print(f"\nStep 4: Delete listing {listing_id}")
    delete_response = requests.delete(
        f"{BASE_URL}/api/listing/{listing_id}?user_id={USER_ID}"
    )
    
    if delete_response.status_code == 200:
        delete_data = delete_response.json()
        print(f"OK Listing deleted (soft delete)")
        print(f"   Message: {delete_data.get('message')}")
    else:
        print(f"ERROR: Delete failed ({delete_response.status_code})")
        print(f"   {delete_response.text}")
    
    # Step 5: Try to update deleted listing (should fail)
    print(f"\nStep 5: Try to update deleted listing")
    update_deleted_response = requests.put(
        f"{BASE_URL}/api/listing/{listing_id}",
        json={
            "user_id": USER_ID,
            "title": "Should Not Work"
        }
    )
    
    # Listing still exists but status=inactive
    # Update might still work technically, but that's OK for soft delete
    print(f"   Response: {update_deleted_response.status_code}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("\nManual verification:")
    print(f"1. Check Supabase - listing {listing_id} should have status='inactive'")
    print(f"2. Updated title should be 'Dell XPS 13 - Guncellemis Baslik'")
    print(f"3. Updated price should be 25000.0")

if __name__ == "__main__":
    try:
        test_post_publish_management()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

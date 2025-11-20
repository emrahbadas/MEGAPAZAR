"""
Test GET /api/listings/my endpoint
"""
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

def test_get_my_listings():
    print("GET MY LISTINGS TEST")
    print("=" * 60)
    
    # Test 1: Get active listings
    print("\nTest 1: Get active listings")
    response = requests.get(
        f"{BASE_URL}/api/listings/my",
        params={
            "user_id": USER_ID,
            "status": "active"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Found {data['count']} active listings")
        for listing in data['listings'][:3]:  # Show first 3
            print(f"   - {listing['title']} | {listing['price']} TL | {listing['status']}")
    else:
        print(f"ERROR: {response.status_code}")
        print(f"   {response.text}")
    
    # Test 2: Get inactive listings
    print("\nTest 2: Get inactive listings")
    response = requests.get(
        f"{BASE_URL}/api/listings/my",
        params={
            "user_id": USER_ID,
            "status": "inactive"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Found {data['count']} inactive listings")
        for listing in data['listings'][:3]:
            print(f"   - {listing['title']} | {listing['price']} TL | {listing['status']}")
    else:
        print(f"ERROR: {response.status_code}")
    
    # Test 3: Get all listings
    print("\nTest 3: Get all listings")
    response = requests.get(
        f"{BASE_URL}/api/listings/my",
        params={
            "user_id": USER_ID,
            "status": "all"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Found {data['count']} total listings")
        
        # Count by status
        active = sum(1 for l in data['listings'] if l['status'] == 'active')
        inactive = sum(1 for l in data['listings'] if l['status'] == 'inactive')
        print(f"   Active: {active}, Inactive: {inactive}")
    else:
        print(f"ERROR: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")

if __name__ == "__main__":
    test_get_my_listings()

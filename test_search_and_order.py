"""
Test search and order endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

def test_search():
    print("SEARCH TEST")
    print("=" * 60)
    
    # Test 1: Simple search
    print("\nTest 1: Simple search - 'rotor'")
    response = requests.post(
        f"{BASE_URL}/api/search",
        json={
            "user_id": USER_ID,
            "query": "rotor"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Found {data['count']} products")
        print(f"\nMessage:\n{data['message']}")
    else:
        print(f"ERROR: {response.status_code}")
        print(f"   {response.text}")
    
    # Test 2: Search with price filter
    print("\n" + "=" * 60)
    print("\nTest 2: Search with filters - '3000 TL altı rotor'")
    response = requests.post(
        f"{BASE_URL}/api/search",
        json={
            "user_id": USER_ID,
            "query": "3000 TL altı rotor"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Found {data['count']} products")
        print(f"Filters applied: {data.get('filters', {})}")
        
        if data['results']:
            print(f"\nFirst result:")
            first = data['results'][0]
            print(f"   {first['title']}")
            print(f"   Price: {first['price']} TL")
    else:
        print(f"ERROR: {response.status_code}")
    
    # Test 3: Search with category
    print("\n" + "=" * 60)
    print("\nTest 3: Search - 'Elektronik kategori laptop'")
    response = requests.post(
        f"{BASE_URL}/api/search",
        json={
            "user_id": USER_ID,
            "query": "Elektronik kategori laptop"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Found {data['count']} products")
    else:
        print(f"ERROR: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("SEARCH TEST COMPLETED")

def test_order():
    print("\n\nORDER TEST")
    print("=" * 60)
    
    # First, get a listing ID from search
    print("\nStep 1: Finding a product to order...")
    search_response = requests.post(
        f"{BASE_URL}/api/search",
        json={
            "user_id": USER_ID,
            "query": "rotor"
        }
    )
    
    if search_response.status_code != 200 or not search_response.json().get('results'):
        print("ERROR: No products found to test order")
        return
    
    listing_id = search_response.json()['results'][0]['id']
    listing_title = search_response.json()['results'][0]['title']
    listing_price = search_response.json()['results'][0]['price']
    
    print(f"OK Found product: {listing_title} ({listing_price} TL)")
    
    # Test: Create order
    print(f"\nStep 2: Creating order...")
    response = requests.post(
        f"{BASE_URL}/api/order/create",
        json={
            "buyer_id": USER_ID,
            "listing_id": listing_id,
            "quantity": 1
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"OK Order created!")
        print(f"\nOrder details:")
        print(f"   Order ID: {data['order_id']}")
        print(f"   Total: {data['order_data']['total_price']} TL")
        print(f"   Commission: {data['order_data']['commission']} TL")
        print(f"   Seller receives: {data['order_data']['seller_receives']} TL")
        
        # Test: Get order details
        order_id = data['order_id']
        print(f"\nStep 3: Fetching order details...")
        get_response = requests.get(
            f"{BASE_URL}/api/order/{order_id}",
            params={"user_id": USER_ID}
        )
        
        if get_response.status_code == 200:
            print(f"OK Order details retrieved")
        else:
            print(f"ERROR: {get_response.status_code}")
    else:
        print(f"ERROR: {response.status_code}")
        print(f"   {response.text}")
    
    print("\n" + "=" * 60)
    print("ORDER TEST COMPLETED")

if __name__ == "__main__":
    try:
        test_search()
        test_order()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

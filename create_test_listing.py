"""
Quick script to create a test listing via direct Supabase insert
"""
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
import uuid

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

# Create test listing
listing_data = {
    "id": str(uuid.uuid4()),
    "user_id": USER_ID,
    "title": "Test Laptop Dell XPS 13",
    "description": "Test listing for post-publish management",
    "price": 20000.0,
    "category": "Elektronik",
    "status": "active",
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat()
}

result = supabase.table("listings").insert(listing_data).execute()

print(f"✅ Test listing created")
print(f"   ID: {listing_data['id']}")
print(f"   Title: {listing_data['title']}")
print(f"   Price: {listing_data['price']} TL")
print(f"\nUse this ID in test_post_publish.py:")
print(f'LISTING_ID = "{listing_data["id"]}"')

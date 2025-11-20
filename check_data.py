"""Check embeddings in database"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Check embeddings
result = supabase.table('product_embeddings').select('id,listing_id').execute()
print(f'\n📊 Embeddings count: {len(result.data)}\n')

if result.data:
    for i, e in enumerate(result.data, 1):
        print(f"{i}. {e['listing_id']}")
else:
    print("❌ No embeddings found!")

# Check listings
listings_result = supabase.table('listings').select('id,title').execute()
print(f'\n📊 Listings count: {len(listings_result.data)}\n')

if listings_result.data:
    for i, l in enumerate(listings_result.data, 1):
        print(f"{i}. {l['id']} - {l['title']}")

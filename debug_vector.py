"""Test raw vector search without RPC function"""
import os
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get embedding for "rotor"
print("Getting embedding for 'rotor'...")
response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input="rotor"
)
embedding = response.data[0].embedding
print(f"✅ Embedding generated: {len(embedding)} dimensions\n")

# First, check if embeddings exist
print("Checking product_embeddings table...")
result = supabase.table('product_embeddings').select('id,listing_id').limit(3).execute()
print(f"Found {len(result.data)} embeddings")
if result.data:
    for i, e in enumerate(result.data, 1):
        print(f"  {i}. {e['listing_id'][:8]}...")

print("\n" + "="*60)
print("RPC function might not exist or have wrong signature.")
print("Check Supabase Dashboard → SQL Editor:")
print("\nRun this to check if function exists:")
print("SELECT proname, pg_get_functiondef(oid) FROM pg_proc WHERE proname='match_products';")
print("\n" + "="*60)

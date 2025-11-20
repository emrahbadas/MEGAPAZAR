"""Test match_products function directly"""
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
print(f"✅ Embedding generated: {len(embedding)} dimensions")

# Test with different thresholds
thresholds = [0.5, 0.6, 0.7, 0.8]

for threshold in thresholds:
    print(f"\n--- Testing threshold {threshold} ---")
    
    result = supabase.rpc(
        'match_products',
        {
            'query_embedding': embedding,
            'match_threshold': threshold,
            'match_count': 10
        }
    ).execute()
    
    print(f"Results: {len(result.data) if result.data else 0}")
    
    if result.data:
        for i, r in enumerate(result.data[:3], 1):
            print(f"  {i}. Listing: {r['listing_id'][:8]}... Similarity: {r['similarity']:.3f}")

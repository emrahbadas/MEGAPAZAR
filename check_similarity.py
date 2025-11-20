"""Check actual similarity scores"""
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

# Test different queries
queries = ["rotor", "laptop", "macbook", "elektronik"]

for query in queries:
    print(f"\n{'='*60}")
    print(f"Query: '{query}'")
    print('='*60)
    
    # Get embedding
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    embedding = response.data[0].embedding
    
    # Search with threshold 0
    result = supabase.rpc(
        'match_products',
        {
            'query_embedding': embedding,
            'match_threshold': 0.0,
            'match_count': 10
        }
    ).execute()
    
    if result.data:
        # Get listing titles
        listing_ids = [r['listing_id'] for r in result.data]
        listings = supabase.table('listings').select('id,title').in_('id', listing_ids).execute()
        
        title_map = {l['id']: l['title'] for l in listings.data}
        
        for i, r in enumerate(result.data, 1):
            title = title_map.get(r['listing_id'], 'Unknown')
            print(f"{i}. {title}")
            print(f"   Similarity: {r['similarity']:.4f}")
    else:
        print("No results")

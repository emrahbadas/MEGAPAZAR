"""Direct test of BuyerSearchAgent"""
import os
from dotenv import load_dotenv
load_dotenv()

from agents.buyer_search import BuyerSearchAgent

# Create agent
agent = BuyerSearchAgent()

# Test search
state = {
    "search_query": "rotor"
}

print("Testing BuyerSearchAgent...")
print("=" * 60)
print(f"Query: {state['search_query']}")
print()

result = agent(state)

print(f"Results: {result.get('search_count', 0)} products found")
print()

if result.get('search_results'):
    for i, product in enumerate(result['search_results'][:3], 1):
        print(f"{i}. {product['title']}")
        print(f"   {product['price']} TL")
        print()

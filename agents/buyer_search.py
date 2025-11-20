"""
BuyerSearchAgent - Alıcı için ürün arama
Semantic search + filters
"""
from agents.base import BaseAgent
from utils.supabase_client import get_supabase_admin
from utils.openai_client import get_llm
from typing import Dict, Any, List
import json
import openai
from config import get_settings

class BuyerSearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("BuyerSearchAgent")
        self.supabase = get_supabase_admin()
        self.llm = get_llm(model="gpt-4o-mini", temperature=0)
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search products based on user query
        Uses semantic search + filters
        """
        query = state.get("search_query", "")
        filters = state.get("search_filters", {})
        
        self.log(f"Searching for: {query}")
        
        try:
            # Parse query for filters if not provided
            if not filters:
                filters = self._extract_filters(query)
                self.log(f"Extracted filters: {filters}")
            
            # Get embedding for semantic search
            embedding = self._get_embedding(query)
            
            # Vector search
            self.log(f"Calling match_products RPC...")
            vector_results = self.supabase.rpc(
                'match_products',
                {
                    'query_embedding': embedding,
                    'match_threshold': 0.3,  # Adjusted based on test data
                    'match_count': 50
                }
            ).execute()
            
            self.log(f"Vector results: {len(vector_results.data) if vector_results.data else 0} matches")
            
            if not vector_results.data:
                self.log("No vector search results")
                state["search_results"] = []
                state["search_count"] = 0
                return state
            
            listing_ids = [r['listing_id'] for r in vector_results.data]
            
            # Get full listing data with filters
            query_builder = self.supabase.table('listings')\
                .select('*')\
                .in_('id', listing_ids)\
                .eq('status', 'active')
            
            # Apply filters
            if filters.get('category'):
                query_builder = query_builder.eq('category', filters['category'])
            
            if filters.get('min_price'):
                query_builder = query_builder.gte('price', filters['min_price'])
            
            if filters.get('max_price'):
                query_builder = query_builder.lte('price', filters['max_price'])
            
            if filters.get('location'):
                query_builder = query_builder.ilike('location', f"%{filters['location']}%")
            
            # Sort by similarity (maintain vector search order)
            results = query_builder.execute()
            
            # Preserve similarity order
            similarity_map = {r['listing_id']: r['similarity'] for r in vector_results.data}
            sorted_results = sorted(
                results.data, 
                key=lambda x: similarity_map.get(x['id'], 0), 
                reverse=True
            )
            
            # Add similarity score to results
            for item in sorted_results:
                item['similarity_score'] = similarity_map.get(item['id'], 0)
            
            state["search_results"] = sorted_results[:20]  # Top 20
            state["search_count"] = len(sorted_results)
            
            self.log(f"Found {len(sorted_results)} matching products")
            
        except Exception as e:
            self.log(f"Search failed: {str(e)}", "error")
            state["search_results"] = []
            state["search_count"] = 0
        
        return state
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filters from natural language query using LLM"""
        prompt = f"""Kullanıcının arama sorgusundan filtreleri çıkar:

Query: "{query}"

Şunları belirle:
- category: Kategori (örn: "Elektronik", "Mobilya", "Endüstriyel Malzemeler")
- min_price: Minimum fiyat (TL)
- max_price: Maximum fiyat (TL)
- location: Konum (şehir)
- condition: Durum ("new", "used", "damaged")

JSON döndür:
{{
    "category": "string | null",
    "min_price": number | null,
    "max_price": number | null,
    "location": "string | null",
    "condition": "string | null"
}}

Örnek:
Query: "İstanbul'da 1000-5000 TL arası ikinci el laptop"
→ {{"category": "Elektronik", "min_price": 1000, "max_price": 5000, "location": "İstanbul", "condition": "used"}}

Sadece JSON döndür."""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            filters = json.loads(content)
            
            # Remove null values
            return {k: v for k, v in filters.items() if v is not None}
            
        except Exception as e:
            self.log(f"Filter extraction failed: {str(e)}", "warning")
            return {}
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for semantic search"""
        settings = get_settings()
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        
        return response.data[0].embedding
    
    def format_results(self, results: List[Dict]) -> str:
        """Format search results for user display"""
        if not results:
            return "Aramanıza uygun ürün bulunamadı. 😞"
        
        message = f"🔍 {len(results)} ürün bulundu:\n\n"
        
        for i, item in enumerate(results[:5], 1):  # Show top 5
            message += f"{i}. **{item['title']}**\n"
            message += f"   💰 {item['price']:,.0f} TL\n"
            message += f"   📍 {item.get('location', 'Belirtilmemiş')}\n"
            
            if item.get('similarity_score'):
                similarity_percent = int(item['similarity_score'] * 100)
                message += f"   🎯 Eşleşme: %{similarity_percent}\n"
            
            message += "\n"
        
        if len(results) > 5:
            message += f"... ve {len(results) - 5} ürün daha.\n"
        
        return message

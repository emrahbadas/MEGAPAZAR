from agents.base import BaseAgent
from tools.product_match_tools import search_similar_products, get_product_price_range
from typing import Dict, Any

class ProductMatchAgent(BaseAgent):
    """Supabase'de benzer ürün arayan agent (with tools)"""
    
    def __init__(self):
        super().__init__("ProductMatchAgent")
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        product_info = state.get("product_info")
        if not product_info:
            state["internal_stats"] = {}
            state["similar_products"] = []
            return state
        
        product_type = product_info.get("product_type", "")
        category = product_info.get("category", "")
        
        self.log(f"🔍 Searching for similar products: {product_type}")
        
        # TOOL: Vector search
        query_text = f"{product_type} {category}"
        result = search_similar_products(
            query_text=query_text,
            threshold=0.7,
            limit=20
        )
        
        # State'e ekle
        state["internal_stats"] = {
            "similar_count": result["stats"]["count"],
            "avg_price": result["stats"]["avg_price"],
            "min_price": result["stats"]["min_price"],
            "max_price": result["stats"]["max_price"]
        }
        state["similar_products"] = result["similar_products"][:5]  # İlk 5'ini sakla
        
        if result["stats"]["count"] > 0:
            self.log(f"✅ Found {result['stats']['count']} similar products, avg: {result['stats']['avg_price']:.2f} TL")
        else:
            self.log("⚠️ No similar products found")
        
        return state

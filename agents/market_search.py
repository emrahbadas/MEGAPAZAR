from agents.base import BaseAgent
from utils.openai_client import get_llm
from typing import Dict, Any
import json

class MarketSearchAgent(BaseAgent):
    """Web'de fiyat araştırması yapan agent"""
    
    def __init__(self):
        super().__init__("MarketSearchAgent")
        self.llm = get_llm(model="gpt-4o", temperature=0)
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        product_info = state.get("product_info")
        if not product_info:
            state["external_stats"] = {}
            return state
        
        product_type = product_info.get("product_type", "")
        self.log(f"Searching web for: {product_type}")
        
        # Tavily API kullanımı (opsiyonel)
        try:
            from config import get_settings
            settings = get_settings()
            
            if settings.tavily_api_key:
                self._search_with_tavily(state, product_info)
            else:
                # Tavily yoksa LLM ile tahmin
                self._estimate_price(state, product_info)
                
        except Exception as e:
            self.log(f"Market search failed: {str(e)}", "error")
            state["external_stats"] = {}
        
        return state
    
    def _search_with_tavily(self, state: Dict[str, Any], product_info: Dict[str, Any]):
        """Tavily ile web search"""
        try:
            from tavily import TavilyClient
            from config import get_settings
            
            settings = get_settings()
            tavily = TavilyClient(api_key=settings.tavily_api_key)
            
            query = f"{product_info['product_type']} fiyat Türkiye"
            results = tavily.search(query, max_results=5)
            
            # LLM ile fiyat analizi
            prompt = f"""Aşağıdaki web arama sonuçlarından {product_info['product_type']} için fiyat bilgisi çıkar:

{json.dumps(results, ensure_ascii=False)}

JSON döndür:
{{
    "external_avg_price": 3000,
    "external_min_price": 2500,
    "external_max_price": 3800,
    "sources_checked": ["trendyol", "amazon"]
}}

Sadece JSON döndür."""
            
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            external_stats = json.loads(content)
            state["external_stats"] = external_stats
            
            self.log(f"Web search complete, avg: {external_stats.get('external_avg_price', 0):.2f} TL")
            
        except Exception as e:
            self.log(f"Tavily search failed: {str(e)}", "error")
            self._estimate_price(state, product_info)
    
    def _estimate_price(self, state: Dict[str, Any], product_info: Dict[str, Any]):
        """Tavily yoksa LLM ile fiyat tahmini"""
        prompt = f"""Türkiye piyasasında {product_info['product_type']} ürünü için ortalama fiyat aralığı tahmin et.

Ürün kategorisi: {product_info.get('category', 'Bilinmiyor')}
Durum: {product_info.get('condition', 'used')}

JSON döndür:
{{
    "external_avg_price": 0,
    "external_min_price": 0,
    "external_max_price": 0,
    "sources_checked": ["tahmin"]
}}

Mantıklı bir fiyat aralığı ver. Sadece JSON döndür."""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            state["external_stats"] = json.loads(content)
            self.log("Price estimated (no Tavily API)")
            
        except Exception as e:
            self.log(f"Price estimation failed: {str(e)}", "error")
            state["external_stats"] = {}

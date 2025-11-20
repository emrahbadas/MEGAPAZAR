from agents.base import BaseAgent
from agents.vision import VisionAgent
from agents.text_parser import TextParserAgent
from agents.product_match import ProductMatchAgent
from agents.market_search import MarketSearchAgent
from agents.pricing import PricingAgent
from agents.listing_writer import ListingWriterAgent
from typing import Dict, Any

class ListingCoordinator(BaseAgent):
    """İlan verme sürecini orkestre eden agent"""
    
    def __init__(self):
        super().__init__("ListingCoordinator")
        
        # Alt agent'ları başlat
        self.vision_agent = VisionAgent()
        self.text_parser = TextParserAgent()
        self.product_match = ProductMatchAgent()
        self.market_search = MarketSearchAgent()
        self.pricing_agent = PricingAgent()
        self.listing_writer = ListingWriterAgent()
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Starting listing coordination...")
        
        # 1. Ürün bilgisi çıkarma (fotoğraf veya metin)
        if state.get("image_url"):
            self.log("Using vision analysis...")
            state = self.vision_agent(state)
        else:
            self.log("Using text parsing...")
            state = self.text_parser(state)
        
        # Ürün bilgisi yoksa hata
        if not state.get("product_info"):
            state["response_type"] = "ask_question"
            state["ai_response"] = "Ürünü tam olarak anlayamadım. Biraz daha detay verebilir misiniz? Örneğin ürünün adı, markası veya kullanım alanı..."
            return state
        
        # 2. İç piyasa araştırması
        self.log("Searching internal market...")
        state = self.product_match(state)
        
        # 3. Dış piyasa araştırması
        self.log("Searching external market...")
        state = self.market_search(state)
        
        # 4. Fiyat hesaplama
        self.log("Calculating pricing...")
        state = self.pricing_agent(state)
        
        # 5. İlan metni yazma
        self.log("Writing listing...")
        state = self.listing_writer(state)
        
        # 6. Son cevap
        if state.get("listing_draft"):
            state["response_type"] = "listing_preview"
            state["ai_response"] = self._format_preview(state["listing_draft"], state.get("internal_stats", {}))
        else:
            state["response_type"] = "error"
            state["ai_response"] = "İlan oluşturulurken bir sorun oluştu. Lütfen tekrar deneyin."
        
        self.log("Listing coordination complete")
        return state
    
    def _format_preview(self, draft: Dict[str, Any], stats: Dict[str, Any]) -> str:
        """İlan önizleme mesajı"""
        price = draft.get('price', 0)
        
        # Piyasa karşılaştırması
        market_info = ""
        if stats and stats.get('similar_count', 0) > 0:
            avg_price = stats.get('avg_price', 0)
            if avg_price > 0:
                diff = price - avg_price
                diff_percent = (diff / avg_price) * 100
                if diff_percent > 5:
                    market_info = f"\n💡 Benzer ürünler ortalama {avg_price:.0f} TL'ye satılıyor (sizinki %{abs(diff_percent):.0f} daha pahalı)"
                elif diff_percent < -5:
                    market_info = f"\n💡 Benzer ürünler ortalama {avg_price:.0f} TL'ye satılıyor (sizinki %{abs(diff_percent):.0f} daha ucuz)"
                else:
                    market_info = f"\n✅ Fiyatınız piyasa ortalamasına ({avg_price:.0f} TL) çok yakın"
        
        return f"""✅ İlanınız hazır!

📋 **{draft['title']}**

💰 Fiyat: {price:.2f} TL
📦 Kategori: {draft['category']}{market_info}

📝 Açıklama:
{draft['description'][:300]}{"..." if len(draft['description']) > 300 else ""}

---
İlanı yayınlamak için "Onayla" yazın.
Değişiklik yapmak için "Düzenle" yazın."""

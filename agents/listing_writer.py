from agents.base import BaseAgent
from utils.openai_client import get_llm
from typing import Dict, Any
import json

class ListingWriterAgent(BaseAgent):
    """İlan metni yazan agent"""
    
    def __init__(self):
        super().__init__("ListingWriterAgent")
        self.llm = get_llm(model="gpt-4o", temperature=0.8)
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        product_info = state.get("product_info", {})
        pricing = state.get("pricing", {})
        user_location = state.get("user_location", "Türkiye")
        
        self.log("Writing listing content...")
        
        # Fiyatı al - hem suggested_price hem recommended_price destekle
        price = pricing.get('recommended_price') or pricing.get('suggested_price', 0)
        
        self.log(f"Using price: {price} TL (from pricing: {pricing})")
        
        prompt = f"""Sen PazarGlobal için çalışan bir İlan Yazma ve Düzenleme Ajanısın.

Görevin, kullanıcının verdiği ham bilgileri kullanarak:
- Net bir başlık (max 80 karakter)
- Akıcı bir açıklama (3-4 paragraf)
- Kısa bir özet (1 cümle)
üretmektir.

📋 Ürün Bilgisi:
{json.dumps(product_info, ensure_ascii=False)}

💰 Fiyat: {price} TL
📍 Konum: {user_location}

✨ TARZ REHBERİ:
- Kısa, net, abartısız
- Satış dili doğal ama "yalan / aşırı iddia" YOK
- Türkçe imla ve noktalama doğru
- SEO uyumlu, anahtar kelimeler içeren
- Profesyonel ama samimi ton

⚠️ KURALLAR:
- SADECE belirtilen alanları doldur
- Ekstra alan EKLEME
- Yorum, açıklama, cümle EKLEME
- Sadece JSON döndür

JSON formatı:
{{
    "title": "string (max 80 karakter)",
    "description": "string (3-4 paragraf)",
    "short_summary": "string (1 cümle)"
}}

SADECE JSON DÖNDÜR:"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            listing_data = json.loads(content)
            
            # ListingDraft oluştur
            # Fiyatı al - hem recommended_price hem suggested_price destekle
            final_price = pricing.get("recommended_price") or pricing.get("suggested_price", 0)
            
            listing_draft = {
                "title": listing_data["title"],
                "description": listing_data["description"],
                "short_summary": listing_data["short_summary"],
                "price": final_price,
                "category": product_info.get("category", "Diğer"),
                "product_info": product_info
            }
            
            self.log(f"✅ Listing created with price: {final_price} TL")
            
            state["listing_draft"] = listing_draft
            self.log(f"Listing written: {listing_data['title'][:30]}...")
            
        except Exception as e:
            self.log(f"Listing writing failed: {str(e)}", "error")
            state["listing_draft"] = None
        
        return state

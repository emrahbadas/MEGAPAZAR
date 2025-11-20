from agents.base import BaseAgent
from utils.openai_client import get_llm
from typing import Dict, Any
import json

class PricingAgent(BaseAgent):
    """Fiyat hesaplayan agent"""
    
    def __init__(self):
        super().__init__("PricingAgent")
        self.llm = get_llm(model="gpt-4o", temperature=0)
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Session'da pricing varsa kullan (tutarlılık için)
        if state.get("pricing"):
            self.log(f"Using cached price: {state['pricing'].get('suggested_price', 0)} TL")
            return state
        
        product_info = state.get("product_info", {})
        internal_stats = state.get("internal_stats", {})
        external_stats = state.get("external_stats", {})
        user_given_price = state.get("user_price", 0)
        
        self.log("Calculating price recommendation...")
        
        # Eğer kullanıcı fiyat verdiyse, kontrol et
        if user_given_price and user_given_price > 0:
            return self._validate_user_price(state, user_given_price, product_info, internal_stats, external_stats)
        
        # Normal fiyat hesaplama
        prompt = f"""Sen PazarGlobal'ın Fiyat Analiz ve Öneri Ajanısın.

Görevin:
1. İç ve dış piyasa verilerini analiz et
2. Ürün durumunu (yeni/ikinci el) göz önüne al
3. Psikolojik fiyatlandırma uygula (2990, 2750, 4500 gibi)
4. Mantıklı bir fiyat aralığı belirle

📊 Ürün Bilgisi:
{json.dumps(product_info, ensure_ascii=False)}

🏪 İç Piyasa (Megapazar):
{json.dumps(internal_stats, ensure_ascii=False)}

🌐 Dış Piyasa (Web):
{json.dumps(external_stats, ensure_ascii=False)}

JSON döndür:
{{
    "suggested_price": 2750,
    "min_reasonable_price": 2500,
    "max_reasonable_price": 3200,
    "reason": "İç pazarda ortalama 2800 TL, dış piyasada 3000 TL. Ürün ikinci el olduğu için %10 düşük fiyat öneriyorum."
}}

SADECE JSON DÖNDÜR:"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            pricing_data = json.loads(content)
            pricing_data["action"] = "accept"  # Default action
            state["pricing"] = pricing_data
            
            self.log(f"Price calculated: {pricing_data.get('suggested_price', 0):.2f} TL")
            
        except Exception as e:
            self.log(f"Pricing failed: {str(e)}", "error")
            # Fallback fiyat
            state["pricing"] = {
                "action": "accept",
                "suggested_price": 1000,
                "min_price": 800,
                "max_price": 1200,
                "reason": "Fiyat hesaplanamadı, tahmin edildi."
            }
        
        return state
    
    def _validate_user_price(self, state: Dict[str, Any], user_price: float, 
                            product_info: Dict, internal_stats: Dict, external_stats: Dict) -> Dict[str, Any]:
        """
        Kullanıcının verdiği fiyatı kontrol et (ChatGPT-5 recommendation)
        """
        self.log(f"Validating user price: {user_price} TL")
        
        prompt = f"""Sen PazarGlobal'ın Fiyat Analiz Ajanısın.

Kullanıcı şu ürün için {user_price} TL fiyat belirledi.

📋 Ürün Bilgisi:
{json.dumps(product_info, ensure_ascii=False)}

🏪 İç Piyasa:
{json.dumps(internal_stats, ensure_ascii=False)}

🌐 Dış Piyasa:
{json.dumps(external_stats, ensure_ascii=False)}

Görevin:
1. Kullanıcının verdiği fiyat mantıklı mı?
2. Çok düşük (dolandırıcılık izlenimi) veya çok yüksek (satılmayacak) mı?
3. Gerekirse alternatif bir fiyat aralığı öner

JSON döndür:
{{
    "action": "accept" veya "suggest",
    "given_price": {user_price},
    "suggested_price": null veya alternatif fiyat,
    "reason": "Kısa açıklama"
}}

Kurallar:
- Kullanıcı fiyatı piyasa ortalamasının ±30% içindeyse → "accept"
- Çok düşük/yüksekse → "suggest" + alternatif fiyat
- Dolandırıcılık şüphesi (örn: iPhone 5 TL) → "suggest" + gerçekçi fiyat

SADECE JSON DÖNDÜR:"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            validation_result = json.loads(content)
            
            if validation_result.get("action") == "accept":
                # Kullanıcı fiyatı kabul et
                state["pricing"] = {
                    "action": "accept",
                    "suggested_price": user_price,
                    "given_price": user_price,
                    "reason": validation_result.get("reason", "Fiyat makul görünüyor.")
                }
                self.log(f"✅ User price accepted: {user_price} TL")
            else:
                # Alternatif öner
                suggested = validation_result.get("suggested_price", user_price)
                state["pricing"] = {
                    "action": "suggest",
                    "given_price": user_price,
                    "suggested_price": suggested,
                    "reason": validation_result.get("reason", "Fiyat ayarlaması önerildi.")
                }
                state["ai_response"] = f"""⚠️ Fiyat Uyarısı

Belirlediğiniz fiyat: {user_price} TL
Önerilen fiyat: {suggested} TL

Sebep: {validation_result.get('reason')}

Fiyatı değiştirmek ister misiniz?"""
                state["response_type"] = "price_warning"
                self.log(f"⚠️ User price questioned: {user_price} TL → Suggest: {suggested} TL")
            
        except Exception as e:
            self.log(f"Price validation failed: {str(e)}", "error")
            # Hata durumunda kullanıcı fiyatını kabul et
            state["pricing"] = {
                "action": "accept",
                "suggested_price": user_price,
                "given_price": user_price,
                "reason": "Fiyat kontrolü yapılamadı, kullanıcı fiyatı kabul edildi."
            }
        
        return state
    
    def get_market_price(self, title: str, category: str) -> float:
        """
        Get market price for a product (for price monitoring)
        Returns only the suggested price as float
        """
        prompt = f"""Aşağıdaki ürün için piyasa fiyatı araştır ve öner:

Ürün: {title}
Kategori: {category}

Web'de benzer ürünlerin fiyatlarını araştır (Sahibinden, Letgo, Hepsiburada vb.)
Ortalama piyasa fiyatını hesapla.

JSON döndür:
{{
    "suggested_price": 15000,
    "reason": "Web araştırmasına göre benzer ürünler 14000-16000 TL arasında."
}}

Sadece JSON döndür."""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            pricing_data = json.loads(content)
            return float(pricing_data.get("suggested_price", 0))
            
        except Exception as e:
            self.log(f"Market price lookup failed: {str(e)}", "error")
            return 0.0

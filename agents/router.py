"""
RouterAgent - PazarGlobal_Router_Prompt_v1
Intent detection + field extraction in single call
Based on ChatGPT-5 recommendations
"""
from agents.base import BaseAgent
from utils.openai_client import get_llm
from typing import Dict, Any
import json
import re

class RouterAgent(BaseAgent):
    """
    Intent yönlendirici ve alan doldurucu agent
    Tek çağrıda: intent + field extraction + missing fields
    """
    
    def __init__(self):
        super().__init__("RouterAgent")
        self.llm = get_llm(model="gpt-4o", temperature=0.3)
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Single-shot intent detection and field extraction
        """
        message = state.get("message", "")
        has_image = bool(state.get("image_url"))
        
        self.log(f"Routing message: {message[:50]}...")
        
        prompt = self._build_router_prompt(message, has_image)
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            result = json.loads(content)
            
            # State'e aktar
            state["intent"] = result.get("intent", "unknown")
            state["query"] = result.get("query")
            state["listing_reference"] = result.get("listing_reference", {})
            
            # Create listing intent'i varsa alanları doldur
            if result.get("intent") == "create_listing":
                create_listing_data = result.get("create_listing", {})
                state["router_extracted_listing"] = create_listing_data
                state["missing_fields"] = result.get("missing_fields", [])
            
            # Meta bilgileri
            state["router_meta"] = result.get("meta", {})
            
            self.log(f"Intent: {state['intent']}, Missing: {state.get('missing_fields', [])}")
            
        except Exception as e:
            self.log(f"Router failed: {str(e)}", "error")
            # Fallback: basit intent detection
            state["intent"] = self._simple_intent_detection(message, has_image)
            state["router_extracted_listing"] = {}
            state["missing_fields"] = []
        
        return state
    
    def _build_router_prompt(self, message: str, has_image: bool) -> str:
        """RouterAgent prompt (ChatGPT-5 recommendation)"""
        
        image_note = "[Kullanıcı fotoğraf ekledi]" if has_image else ""
        
        return f"""Sen PazarGlobal için çalışan bir Niyet Yönlendirici (Router Agent) ve alan doldurucu ajansın.

Görevin:
1. Kullanıcı mesajını analiz edip niyetini (intent) belirlemek
2. Gerekli alanları mümkün olduğunca doldurmak
3. Backend'in anlayacağı katı JSON formatında çıktı üretmek

PazarGlobal, kullanıcıların ürün aradığı, ilan verdiği ve ilanları yönettiği bir pazaryeri asistandır.

SADECE aşağıdaki intent'lerden birini seçebilirsin:
- product_search: Kullanıcı bir ürünü arıyor, sonuç listesi görmek istiyor
- create_listing: Kullanıcı bir ürünü satmak / ilan vermek istiyor
- get_listing_details: Kullanıcı daha önce gösterilen sonuçlardaki belirli bir ilan hakkında detay istiyor
- listing_management: Kullanıcı kendi ilanlarını görmek / düzenlemek / silmek istiyor
- help: Kullanıcı sistemin nasıl çalıştığını soruyor veya ne yazacağını bilmiyor
- small_talk: Selamlaşma, sohbet, platform dışı genel muhabbet
- unknown: Niyet net değil veya PazarGlobal ile ilgili değil

Eğer kullanıcı ilan oluşturmak istiyorsa ve metin içinde başlık, fiyat, açıklama ve kategoriye dair bilgi varsa, bunları create_listing intent'i altındaki alanlara doldur.
Eksik alan varsa, yine create_listing intent'i kullan ama eksik alanları missing_fields listesinde belirt.

ÖNEMLİ KURALLAR:
- Çıktın SADECE JSON olmalı. Asla düz metin yazma.
- Fazladan alan ekleme.
- Yorum, cümle, açıklama ekleme.
- Tahmin yaparken mantıklı ol ama UYDURMA.

ZORUNLU JSON FORMAT:
{{
  "intent": "product_search | create_listing | get_listing_details | listing_management | help | small_talk | unknown",
  "query": "string or null",
  "listing_reference": {{
    "index": null,
    "id": null,
    "price_hint": null
  }},
  "create_listing": {{
    "title": null,
    "description": null,
    "price": null,
    "category": null,
    "condition": null,
    "city": null,
    "currency": "TRY"
  }},
  "missing_fields": [],
  "meta": {{
    "language": "tr",
    "raw_text": "kullanıcının orijinal mesajı"
  }}
}}

ALAN AÇIKLAMALARI:
- query: product_search için aranacak kelime(ler)
- listing_reference: "1. ürün", "2500 TL olan ürün" gibi referanslar için
- create_listing.price: Noktasız tam sayı (örn: 160000)
- missing_fields: ["price", "category"] gibi eksikler (boş ise [])

KULLANICI MESAJI:
"{message}" {image_note}

SADECE JSON DÖNDÜR:"""
    
    def _simple_intent_detection(self, message: str, has_image: bool) -> str:
        """Fallback basit intent detection"""
        msg_lower = message.lower()
        
        # İlan verme
        listing_keywords = ["ilan", "sat", "satmak", "satacağım", "ürün ver", "ekle"]
        if any(kw in msg_lower for kw in listing_keywords) or has_image:
            return "create_listing"
        
        # Arama
        search_keywords = ["ara", "bul", "arıyorum", "var mı"]
        if any(kw in msg_lower for kw in search_keywords):
            return "product_search"
        
        # Yardım
        help_keywords = ["nasıl", "yardım", "ne yapmalıyım"]
        if any(kw in msg_lower for kw in help_keywords):
            return "help"
        
        # Selamlaşma
        greeting_keywords = ["merhaba", "selam", "hey", "günaydın"]
        if any(kw in msg_lower for kw in greeting_keywords):
            return "small_talk"
        
        return "unknown"

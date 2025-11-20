from agents.base import BaseAgent
from utils.openai_client import get_vision_llm
from typing import Dict, Any
import json

class VisionAgent(BaseAgent):
    """Fotoğraftan ürün bilgisi çıkaran agent"""
    
    def __init__(self):
        super().__init__("VisionAgent")
        self.llm = get_vision_llm()
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        image_url = state.get("image_url")
        if not image_url:
            self.log("No image URL provided", "error")
            state["product_info"] = None
            return state
        
        self.log(f"Analyzing image: {image_url[:50]}...")
        
        prompt = """Bu fotoğraftaki ürünü detaylı analiz et.

Şunları belirle:
- Ürün tipi nedir? (örn: "Endüstriyel Rotor Gövdesi", "iPhone 13", "Koltuk Takımı")
- Marka tahmin edebiliyor musun?
- Kategori nedir? (örn: "Endüstriyel Malzemeler", "Elektronik", "Mobilya")
- Durum: yeni mi, ikinci el mi, hasarlı mı?
- Fiziksel özellikler (materyal, boyut, renk vb.)

⚠️ ÖNEMLİ KURALLAR:
- Markayı SADECE fotoğrafta NET olarak görüyorsan yaz, yoksa null
- Model adını UYDURMA, emin değilsen genel ifade kullan
- Kesin olmadığın bilgileri null bırak
- Sadece JSON döndür, açıklama veya yorum ekleme

JSON formatında döndür:
{
    "product_type": "string",
    "brand": "string | null",
    "category": "string",
    "condition": "new/used/damaged",
    "estimated_attributes": {
        "material": "string | null",
        "size": "string | null",
        "color": "string | null"
    }
}

SADECE JSON DÖNDÜR:"""
        
        try:
            response = self.llm.invoke([
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ])
            
            # JSON parse et
            content = response.content.strip()
            
            # Markdown code block varsa temizle
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            product_data = json.loads(content)
            
            state["product_info"] = product_data
            self.log(f"Product identified: {product_data.get('product_type', 'Unknown')}")
            
        except json.JSONDecodeError as e:
            self.log(f"JSON parse error: {str(e)}", "error")
            self.log(f"Response was: {response.content[:200]}", "error")
            state["product_info"] = None
        except Exception as e:
            self.log(f"Vision analysis failed: {str(e)}", "error")
            state["product_info"] = None
        
        return state

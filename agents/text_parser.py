from agents.base import BaseAgent
from utils.openai_client import get_llm
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
import json

class TextParserAgent(BaseAgent):
    """Kullanıcı metninden ürün bilgisi çıkaran agent"""
    
    def __init__(self):
        super().__init__("TextParserAgent")
        self.llm = get_llm(model="gpt-4o", temperature=0)
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raw_text = state.get("message", "")
        self.log(f"Parsing text: {raw_text[:50]}...")
        
        prompt = f"""Kullanıcının aşağıdaki metninden ürün bilgisini çıkar:

"{raw_text}"

Şunları belirle:
- Ürün tipi (detaylı, örn: "Endüstriyel Karbon Alaşımlı Rotor Gövdesi")
- Kategori
- Marka (varsa)
- Adet
- Durum (yeni/ikinci el/hasarlı)
- Ekstra notlar

JSON formatında döndür:
{{
    "product_type": "string",
    "brand": "string | null",
    "category": "string",
    "condition": "new/used/damaged",
    "quantity": 1,
    "extra_notes": "string"
}}

⚠️ ÖNEMLİ:
Tahmin yapman gerekiyorsa en mantıklı tahmini ver ama BİLGİ UYDURMA.
Emin olmadığın alanları null bırak.

SADECE JSON DÖNDÜR:"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Markdown code block varsa temizle
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            product_data = json.loads(content)
            state["product_info"] = product_data
            self.log(f"Product parsed: {product_data.get('product_type', 'Unknown')}")
            
        except json.JSONDecodeError as e:
            self.log(f"JSON parse error: {str(e)}", "error")
            self.log(f"Response was: {response.content[:200]}", "error")
            state["product_info"] = None
        except Exception as e:
            self.log(f"Text parsing failed: {str(e)}", "error")
            state["product_info"] = None
        
        return state

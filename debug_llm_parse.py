"""Debug LLM parse"""
import json
from langchain_core.prompts import ChatPromptTemplate
from utils.openai_client import get_llm

llm = get_llm(model="gpt-4o")

listing_draft = {
    "title": "Endüstriyel Rotor",
    "price": 2990,
    "description": "Test description"
}

prompt = ChatPromptTemplate.from_messages([
    ("system", """Kullanıcı ilanında değişiklik yapmak istiyor.
Mevcut ilan bilgileri:
{listing_draft}

Kullanıcının mesajından:
1. Hangi alanı değiştirmek istiyor? (title, description, price, category)
2. Ne değişiklik istiyor? (kısa açıklama)

JSON döndür:
{{
    "field": "title" veya "description" veya "price" veya "category",
    "change_description": "Kullanıcının istediği değişiklik",
    "new_value": "Direkt değer varsa (örn: yeni başlık metni, yeni fiyat)"
}}

Örnekler:
- "başlığı değiştir" → {{"field": "title", "change_description": "Başlık değiştirilecek", "new_value": null}}
- "fiyatı 1500 TL yap" → {{"field": "price", "change_description": "Fiyat 1500 TL olacak", "new_value": "1500"}}
- "açıklamayı daha kısa yap" → {{"field": "description", "change_description": "Açıklama kısaltılacak", "new_value": null}}"""),
    ("human", "{message}")
])

message = "fiyatı 3500 TL yap"

response = llm.invoke(prompt.format_messages(
    listing_draft=json.dumps(listing_draft, ensure_ascii=False),
    message=message
))

print("LLM Response:")
print(response.content)

try:
    content = response.content.strip()
    if content.startswith("```json"):
        content = content.replace("```json", "").replace("```", "").strip()
    
    edit_info = json.loads(content)
    print("\nParsed:")
    print(json.dumps(edit_info, indent=2, ensure_ascii=False))
    
    print(f"\nField: {edit_info.get('field')}")
    print(f"New value: {edit_info.get('new_value')}")
    print(f"Description: {edit_info.get('change_description')}")
except Exception as e:
    print(f"\nParse error: {e}")

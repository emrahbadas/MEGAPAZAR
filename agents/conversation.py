from agents.base import BaseAgent
from utils.openai_client import get_llm
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any

class ConversationAgent(BaseAgent):
    """Kullanıcı ile konuşan ve niyet tespit eden agent"""
    
    def __init__(self):
        super().__init__("ConversationAgent")
        self.llm = get_llm(model="gpt-4o", temperature=0.7)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Sen Megapazar'ın yardımcı asistanısın.

Görevin kullanıcının niyetini anlamak:
- İlan vermek mi istiyor? (anahtar kelimeler: "ilan ver", "satmak istiyorum", "satacağım", "ürün ekle")
- Ürün mü arıyor? (anahtar kelimeler: "ara", "bul", "arıyorum", "fiyat", "ne kadar")
- Satın alma mı yapıyor? (anahtar kelimeler: "satın al", "sipariş", "almak istiyorum")

Kısa, sade, samimi Türkçe konuş.
Kullanıcıya rehberlik et ama çok fazla soru sorma.
Eğer fotoğraf eklemişse bunu fark et."""),
            ("human", "{input}")
        ])
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        message = state.get("message", "")
        self.log(f"Processing message: {message[:50]}...")
        
        # Fotoğraf var mı kontrol et
        has_image = bool(state.get("image_url"))
        if has_image:
            message += " [Kullanıcı fotoğraf ekledi]"
        
        # LLM'den cevap al
        try:
            response = self.llm.invoke(
                self.prompt.format_messages(input=message)
            )
            
            # Intent tespit et
            intent = self._detect_intent(state.get("message", ""), response.content, has_image)
            
            state["intent"] = intent
            state["ai_response"] = response.content
            
            # Conversation history güncelle
            if "conversation_history" not in state:
                state["conversation_history"] = []
            
            state["conversation_history"].append({
                "role": "assistant",
                "content": response.content
            })
            
            self.log(f"Detected intent: {intent}")
            
        except Exception as e:
            self.log(f"Error in conversation: {str(e)}", "error")
            state["intent"] = "conversation"
            state["ai_response"] = "Üzgünüm, bir hata oluştu. Tekrar dener misiniz?"
        
        return state
    
    def _detect_intent(self, user_message: str, ai_response: str, has_image: bool) -> str:
        """Kullanıcı niyetini tespit et"""
        msg_lower = user_message.lower()
        
        # İlan verme kelimeleri
        listing_keywords = ["ilan", "sat", "satmak", "satacağım", "ürün ver", "ekle", "yükle"]
        if any(kw in msg_lower for kw in listing_keywords) or has_image:
            return "listing"
        
        # Arama kelimeleri
        search_keywords = ["ara", "bul", "arıyorum", "fiyat", "kaç para", "ne kadar", "var mı"]
        if any(kw in msg_lower for kw in search_keywords):
            return "search"
        
        # Satın alma kelimeleri
        order_keywords = ["satın al", "sipariş", "almak istiyorum", "sepet", "siparişimi"]
        if any(kw in msg_lower for kw in order_keywords):
            return "order"
        
        # Default: conversation
        return "conversation"

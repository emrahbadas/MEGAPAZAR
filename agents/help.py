"""
HelpAgent - Yardım ve Rehberlik
ChatGPT-5 recommendation
"""
from agents.base import BaseAgent
from utils.openai_client import get_llm
from typing import Dict, Any

class HelpAgent(BaseAgent):
    """
    Kullanıcı yardım ve rehberlik agent'ı
    Platform kullanımını açıklar
    """
    
    def __init__(self):
        super().__init__("HelpAgent")
        self.llm = get_llm(model="gpt-4o-mini", temperature=0.7)
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Yardım mesajı döndür"""
        message = state.get("message", "")
        
        self.log(f"Providing help for: {message[:50]}...")
        
        # Eğer genel yardım istiyorsa direkt template döndür
        if self._is_general_help(message):
            state["ai_response"] = self._get_general_help()
            state["response_type"] = "help"
            return state
        
        # Spesifik soru varsa LLM'e sor
        prompt = self._build_help_prompt(message)
        
        try:
            response = self.llm.invoke(prompt)
            state["ai_response"] = response.content
            state["response_type"] = "help"
            
        except Exception as e:
            self.log(f"Help generation failed: {str(e)}", "error")
            state["ai_response"] = self._get_general_help()
            state["response_type"] = "help"
        
        return state
    
    def _is_general_help(self, message: str) -> bool:
        """Genel yardım mı yoksa spesifik soru mu?"""
        msg_lower = message.lower()
        
        general_keywords = [
            "nasıl kullanılır",
            "nasıl çalışır",
            "ne yapabilirim",
            "yardım",
            "help",
            "neler yapabilirim"
        ]
        
        return any(kw in msg_lower for kw in general_keywords)
    
    def _get_general_help(self) -> str:
        """Genel yardım template'i"""
        return """👋 **PazarGlobal'e Hoş Geldiniz!**

Ben size yardımcı olmak için buradayım. İşte yapabilecekleriniz:

📦 **İlan Vermek İçin:**
• "Ürün satmak istiyorum" yazın
• Veya direkt fotoğraf gönderin
• Örnek: "iPhone 13 satmak istiyorum, 15.000 TL"

🔍 **Ürün Aramak İçin:**
• Aradığınız ürünü yazın
• Örnek: "İstanbul'da 3000 TL altı laptop arıyorum"

📋 **İlanlarınızı Görmek İçin:**
• "İlanlarımı göster" yazın

💡 **İpuçları:**
• Fotoğraf eklediğinizde otomatik analiz yapıyorum
• Fiyat önerimiz piyasa araştırmasına dayalı
• İlan önizlemesinden önce fiyat pazarlığı yapabilirsiniz

Başka sorunuz varsa sormaktan çekinmeyin! 😊"""
    
    def _build_help_prompt(self, message: str) -> str:
        """Spesifik soru için LLM prompt'u"""
        return f"""Sen PazarGlobal platformunun yardım asistanısın.

Platform Özellikleri:
- Kullanıcılar ürün ilanı verebilir (fotoğraf veya metin ile)
- AI ile otomatik fiyat önerisi (piyasa araştırması yapılır)
- Benzer ürünlerle karşılaştırma
- Ürün arama ve filtreleme
- Sipariş yönetimi ve komisyon sistemi (%2.5)

Görevin:
Kullanıcının sorusuna kısa, net ve yardımcı cevap ver.

Tarzın:
- Samimi ama profesyonel
- Maddeli liste kullan (daha okunabilir)
- Adım adım anlatım
- Gerekirse örnek ver

Kullanıcı Sorusu:
"{message}"

Cevabın (Türkçe):"""

"""
Enhanced Conversation Agent
Multi-turn conversation, eksik bilgi toplama, müzakere yapabilir
"""
from agents.base import BaseAgent
from utils.openai_client import get_llm
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from models.conversation_state import ConversationStage, UserIntent
import json

class EnhancedConversationAgent(BaseAgent):
    """
    Gelişmiş konuşma agent'ı
    - Intent detection
    - Eksik bilgi tespit ve soru sorma
    - Fiyat müzakeresi
    - Düzenleme istekleri
    - İptal/reset
    """
    
    def __init__(self):
        super().__init__("EnhancedConversationAgent")
        self.llm = get_llm(model="gpt-4o", temperature=0.7)
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        State'e göre conversation yönetimi
        """
        from models.conversation_state import session_manager
        
        user_id = state.get("user_id")
        message = state.get("message", "")
        
        self.log(f"🚀 __call__ started - User: {user_id}, Message: '{message[:50]}'")
        
        # Session getir veya oluştur
        session = session_manager.get_or_create_session(
            user_id=user_id,
            platform=state.get("platform", "web")
        )
        
        self.log(f"📋 Session loaded - Stage: {session.stage}, Intent: {session.intent}")
        
        # Kullanıcı mesajını ekle
        session.add_message("user", message)
        
        # Stage'e göre işlem yap
        stage = session.stage
        self.log(f"Current stage: {stage}, Message: {message[:50]}...")
        
        # Intent detection (SADECE INITIAL'de veya UNKNOWN ise - sonrası conversation flow'a devam)
        if stage == ConversationStage.INITIAL or session.intent == UserIntent.UNKNOWN:
            intent = self._detect_intent(message, session)
            session.intent = intent
            state["intent"] = intent.value
            self.log(f"🎯 Intent detected: {intent.value} from message: '{message[:50]}'")
            
            # Session'ı hemen güncelle (intent kaydedilsin)
            session_manager.update_session(session)
        else:
            self.log(f"⏩ Skipping intent detection - stage: {stage}, existing intent: {session.intent}")
        
        # PREVIEW stage'de price negotiation için özel kontrol
        if stage == ConversationStage.PREVIEW:
            # Fiyat müzakeresi intent'i tekrar kontrol et
            if self._detect_intent(message, session) == UserIntent.NEGOTIATING:
                session.intent = UserIntent.NEGOTIATING
                state["intent"] = UserIntent.NEGOTIATING.value
        
        # Stage'e özel processing
        if stage == ConversationStage.INITIAL:
            response = self._handle_initial(message, session, state)
            # Stage değişmiş olabilir - hemen kaydet
            session_manager.update_session(session)
        
        elif stage == ConversationStage.GATHERING_INFO:
            response = self._handle_gathering_info(message, session, state)
            # Stage değişmiş olabilir - hemen kaydet
            session_manager.update_session(session)
        
        elif stage == ConversationStage.ANALYZING:
            # Analiz aşaması - workflow'a yönlendir
            self.log("📊 ANALYZING stage - redirecting to workflow...")
            state["response_type"] = "start_listing_flow"
            response = "Bilgilerinizi analiz ediyorum... 🔍"
        
        elif stage == ConversationStage.PREVIEW:
            response = self._handle_preview(message, session, state)
            session_manager.update_session(session)
        
        elif stage == ConversationStage.NEGOTIATION:
            response = self._handle_negotiation(message, session, state)
            session_manager.update_session(session)
        
        elif stage == ConversationStage.EDITING:
            response = self._handle_editing(message, session, state)
            session_manager.update_session(session)
        
        else:
            response = self._handle_general(message, session, state)
        
        # Response'u session'a ekle
        session.add_message("assistant", response)
        
        # Final update - conversation history kaydedilsin
        session_manager.update_session(session)
        
        # State'i güncelle
        state["ai_response"] = response
        state["session_state"] = session.dict()
        state["conversation_history"] = session.conversation_history
        
        self.log(f"Response: {response[:100]}...")
        
        return state
    
    def _detect_intent(self, message: str, session) -> UserIntent:
        """Intent detection"""
        msg_lower = message.lower()
        
        # 🎯 CRITICAL FIX: Teknik kullanıcı - marka+model+özellik varsa direkt LISTING
        technical_keywords = ["snapdragon", "ram", "gb", "işlemci", "ekran", "kamera", "mp", "amoled", "ssd"]
        has_brand = any(brand in msg_lower for brand in ["iphone", "samsung", "hp", "dell", "lenovo", "mercedes", "bmw", "s23", "c180"])
        has_technical = any(keyword in msg_lower for keyword in technical_keywords)
        
        if has_brand and has_technical:
            self.log("🎯 TECHNICAL USER detected: brand + technical specs → LISTING")
            return UserIntent.LISTING
        
        # Fiyat müzakeresi (ÖNCE kontrol et - PREVIEW stage'de sayı+TL varsa)
        if session.stage == ConversationStage.PREVIEW:
            import re
            # "2000 TL", "1500 lira", "fiyat 2000" gibi formatlar
            price_patterns = [r'\d+[\.,]?\d*\s*tl', r'\d+[\.,]?\d*\s*lira', r'fiyat.*\d+']
            if any(re.search(pattern, msg_lower) for pattern in price_patterns):
                return UserIntent.NEGOTIATING
            
            # "pahalı", "ucuz" gibi kelimeler
            if any(word in msg_lower for word in ["pahalı", "ucuz", "indirim", "düşür"]):
                return UserIntent.NEGOTIATING
        
        # İptal
        if any(word in msg_lower for word in ["iptal", "vazgeç", "bırak", "kapat"]):
            return UserIntent.CANCELLING
        
        # Onaylama
        if any(word in msg_lower for word in ["onayla", "tamam", "kabul", "evet", "olur", "onay"]):
            return UserIntent.CONFIRMING
        
        # Düzenleme
        if any(word in msg_lower for word in ["düzenle", "değiştir", "güncelle", "edit"]):
            return UserIntent.EDITING
        
        # İlan verme (SADECE açık niyet varsa) - genişletilmiş keywords
        has_image = bool(session.image_url)
        listing_keywords = [
            "ilan ver", "ilan vereceğim", "satmak istiyorum", "satacağım", "satış yap",
            "satmayı düşünüyorum", "satmak istiyordum", "ilan oluştur",
            "kurtulmak istiyorum", "satabilirim", "fiyat öğrenmem lazım"
        ]
        
        # 🎯 CRITICAL FIX: Eğer brand veya teknik detay varsa + fiyat sorusu → LISTING intent
        has_brand = any(brand in msg_lower for brand in ["iphone", "samsung", "hp", "dell", "lenovo", "mercedes", "bmw"])
        has_price_question = any(word in msg_lower for word in ["düşük mü", "çok mu", "kaç", "fiyat", "tl", "lira"])
        
        if has_brand and has_price_question:
            self.log("🎯 LISTING intent detected: brand + price question")
            return UserIntent.LISTING
        
        if any(keyword in msg_lower for keyword in listing_keywords) or has_image:
            return UserIntent.LISTING
        
        # 🛑 CRITICAL FIX: Search sadece AÇIKÇA arama niyeti varsa tetiklensin
        # "premium cihaz", "kategori var mı" gibi → QUESTION (help)
        # Sadece "arıyorum", "bul" gibi → SEARCH
        explicit_search_keywords = ["arıyorum", "bul", "ara bana", "listele"]
        if any(keyword in msg_lower for keyword in explicit_search_keywords):
            return UserIntent.SEARCHING
        
        # Soru - search yerine help dönsün
        if "?" in message or any(word in msg_lower for word in ["nasıl", "neden", "nedir", "ne", "kim", "kategori", "premium"]):
            return UserIntent.QUESTION
        
        return UserIntent.UNKNOWN
    
    def _handle_initial(self, message: str, session, state: Dict) -> str:
        """İlk mesaj işleme - conversation_history'ye bakarak context-aware yanıt"""
        intent = session.intent
        conversation_history = session.conversation_history
        
        self.log(f"🔍 _handle_initial called - Intent: {intent} (type: {type(intent)}), History length: {len(conversation_history)}")
        
        # Conversation history varsa context oluştur
        history_text = ""
        self.log(f"📜 Conversation history length: {len(conversation_history)}")
        if len(conversation_history) > 1:  # En son mesaj zaten message değişkeninde
            self.log(f"⚠️ History has {len(conversation_history)} messages - using context")
            history_text = "\n".join([
                f"{'Kullanıcı' if msg['role'] == 'user' else 'Asistan'}: {msg['content']}"
                for msg in conversation_history[:-1]  # Son mesajı dahil etme (zaten yeni mesaj olarak gelecek)
            ])
        
        # Intent enum karşılaştırması - hem enum hem string desteği
        if intent == UserIntent.LISTING or (isinstance(intent, str) and intent == "listing"):
            # Stage'i GATHERING_INFO'ya al
            session.set_stage(ConversationStage.GATHERING_INFO)
            
            # BASIT YAKLAŞIM: İlk mesajda sadece akışı başlat, detaylı extraction gathering_info'da yap
            # Eğer mesajda açıkça ürün bilgisi yoksa basit cevap ver
            msg_lower = message.lower()
            has_product_mention = any(keyword in msg_lower for keyword in ["telefon", "laptop", "iphone", "samsung", "bilgisayar", "araba", "ev", "kanepe"])
            
            if not has_product_mention:
                state["response_type"] = "gathering_info"
                return "Harika! Hangi ürünü satmak istiyorsunuz? 📸"
            
            # Eğer conversation history'de ürün hakkında bilgi varsa LLM ile yakalayalım
            # AMA sadece history varsa - yoksa basit cevap ver
            if history_text and len(conversation_history) > 2:
                # LLM ile context-aware bilgi çıkar
                prompt = ChatPromptTemplate.from_messages([
                    ("system", f"""Kullanıcı ürün satmak istiyor.

ÖNCEKİ KONUŞMA:
{history_text}

SON MESAJ: {message}

Kullanıcının TÜM mesajlarından (önceki ve son mesaj dahil) ürün hakkında bilgi topla.

⚠️ KURALLAR:
1. Kullanıcı BELİRTMEDİYSE null bırak
2. Kararsızsa (iPhone 14 mi 13 Pro mu?) → brand'i al, model null
3. Teknik detay geçiyorsa (Snapdragon, AMOLED, 512GB) → sadece brand/model yakala, teknik detayları IGNORE et
4. "iPhone" → brand: "Apple"
5. Fiyat bahsedildiyse çıkar (50 bin → 50000)

Sadece bu alanları doldur:
- brand (marka)
- model (model) 
- condition (yeni/sıfır/2.el/kullanılmış)
- year (yıl)
- color (renk)
- price (fiyat - sayı olarak)

JSON:
{{
    "product_info": {{"brand": "...", "model": "...", "condition": "...", "year": "...", "price": ...}},
    "missing_fields": ["field1", ...]
}}

ÖRNEKLER:
"Laptop" → {{"product_info": {{"brand": null, "model": null}}, "missing_fields": ["brand","model","condition"]}}
"iPhone 14 mi 13 Pro mu?" → {{"product_info": {{"brand": "Apple", "model": null}}, "missing_fields": ["model","condition"]}}
"Samsung S23 Ultra 512GB Snapdragon" → {{"product_info": {{"brand": "Samsung", "model": "S23 Ultra"}}, "missing_fields": ["condition"]}}
"50 bin TL" → {{"product_info": {{"price": 50000}}, "missing_fields": ["brand","model","condition"]}}
"""),
                    ("human", "Bilgileri çıkar")
                ])
                
                try:
                    response = self.llm.invoke(prompt.format_messages())
                    content = response.content.strip()
                    if content.startswith("```json"):
                        content = content.replace("```json", "").replace("```", "").strip()
                    
                    result = json.loads(content)
                    
                    product_info = result.get("product_info", {})
                    missing = result.get("missing_fields", [])
                    
                    print(f"\n🔍 DEBUG _handle_initial extraction:")
                    print(f"   LLM returned product_info: {product_info}")
                    print(f"   LLM returned missing: {missing}")
                    print(f"   History was used: {len(history_text) > 0}")
                    print(f"   Conversation history length: {len(conversation_history)}\n")
                    
                    # Product info'yu session'a ekle
                    if product_info:
                        session.update_product_info(product_info)
                        state["product_info"] = product_info
                        self.log(f"Extracted product info: {product_info}")
                    
                    # Minimum gerekli alanlar kontrolü - sadece bunları kontrol et!
                    # Model opsiyonel olabilir - brand ve condition yeterli
                    required_fields = ["brand", "condition"]
                    # None, null, empty string = missing
                    actual_missing = [f for f in required_fields if not product_info.get(f) or product_info.get(f) == "null"]
                    
                    self.log(f"Required fields check: {required_fields}, Missing: {actual_missing}, Product: {product_info}")
                    
                    # Sadece required fields'ı missing olarak işaretle
                    missing = actual_missing
                    
                    # Eksik alan var mı kontrol et
                    if missing:
                        session.set_missing_fields(missing)
                        state["response_type"] = "gathering_info"
                        
                        # Toplanan bilgileri özetle + sonraki soruyu sor
                        summary = ", ".join([f"{k}: {v}" for k, v in product_info.items() if v])
                        field_tr = {"brand": "Marka", "model": "Model", "condition": "Durum (yeni/2.el)", "year": "Yıl", "price": "Fiyat"}
                        next_field = field_tr.get(missing[0], missing[0])
                        return f"Anladım: {summary}.\n\n{next_field} nedir? 🤔"
                    else:
                        # Bilgiler tam! Workflow'a git
                        session.set_stage(ConversationStage.ANALYZING)
                        state["response_type"] = "start_listing_flow"
                        return "Harika! Tüm bilgiler tam. İlanınızı hazırlıyorum... 🚀"
                
                except Exception as e:
                    self.log(f"Product info extraction failed: {str(e)}", "error")
                    # LLM hatası durumunda basit keyword extraction yap
                    simple_info = {}
                    msg_with_history = (history_text + "\n" + message).lower()
                    
                    # ENHANCED: Marka tespiti - belirsiz ifadeleri de yakala
                    brands = [
                        ("iphone", "Apple"), ("apple", "Apple"), ("macbook", "Apple"),
                        ("samsung", "Samsung"), ("huawei", "Huawei"), ("xiaomi", "Xiaomi"),
                        ("hp", "HP"), ("dell", "Dell"), ("lenovo", "Lenovo"), 
                        ("asus", "Asus"), ("acer", "Acer"), ("mercedes", "Mercedes"),
                        ("bmw", "BMW"), ("audi", "Audi")
                    ]
                    for keyword, brand_name in brands:
                        if keyword in msg_with_history:
                            simple_info["brand"] = brand_name
                            self.log(f"🔍 Simple extraction found brand: {brand_name} from keyword: {keyword}")
                            break
                    
                    # Durum tespiti
                    if any(word in msg_with_history for word in ["2.el", "ikinci el", "kullanılmış"]):
                        simple_info["condition"] = "2.el"
                    elif any(word in msg_with_history for word in ["yeni", "sıfır", "kutulu"]):
                        simple_info["condition"] = "yeni"
                    
                    # Basit info varsa kaydet
                    if simple_info:
                        session.update_product_info(simple_info)
                        state["product_info"] = simple_info
                        self.log(f"Simple keyword extraction: {simple_info}")
            
            # History yoksa VEYA extraction başarısız olduysa - ilk mesaj fallback
            # Ama mesajda zaten ürün bilgisi varsa ona göre cevap ver
            if any(keyword in msg_lower for keyword in ["telefon", "laptop", "bilgisayar", "iphone", "samsung"]):
                state["response_type"] = "gathering_info"
                # Stage'i gathering_info'ya çek
                session.set_stage(ConversationStage.GATHERING_INFO)
                # Basit extraction yap
                if "iphone" in msg_lower or "telefon" in msg_lower:
                    return "Hangi marka ve model? Durumu nedir? (yeni/2.el)"
                elif "laptop" in msg_lower or "bilgisayar" in msg_lower:
                    return "Hangi marka ve model laptop? Durumu nedir? (yeni/2.el)"
                else:
                    return "Ürününüzün marka, model ve durumunu (yeni/2.el) belirtir misiniz?"
            else:
                state["response_type"] = "gathering_info"
                return "Harika! Hangi ürünü satmak istiyorsunuz? Fotoğraf gönderebilir veya ürün detaylarını yazabilirsiniz. 📸"
        
        # Check if it's a price-related question with product details
        msg_lower = message.lower()
        has_brand = any(brand in msg_lower for brand in ["iphone", "samsung", "hp", "dell", "lenovo", "mercedes", "bmw"])
        has_price_question = any(word in msg_lower for word in ["düşük mü", "çok mu", "kaç", "fiyat", "tl", "lira"])
        
        if intent == UserIntent.LISTING and has_brand and has_price_question:
            # 🎯 LISTING with price question - PricingAgent'a yönlendir
            from agents.pricing import PricingAgent
            self.log("💰 LISTING with price question - calling PricingAgent")
            
            # Product info session'dan al
            product_info = session.product_info or {}
            
            # Eğer product info yoksa basit extraction yap
            if not product_info.get("brand"):
                msg_lower = message.lower()
                brands = [
                    ("iphone", "Apple"), ("apple", "Apple"), ("samsung", "Samsung"),
                    ("hp", "HP"), ("dell", "Dell"), ("lenovo", "Lenovo")
                ]
                for keyword, brand in brands:
                    if keyword in msg_lower:
                        product_info["brand"] = brand
                        break
            
            # PricingAgent çağır
            pricing_agent = PricingAgent()
            pricing_state = {
                "user_id": session.user_id,
                "product_info": product_info,
                "internal_stats": session.internal_stats or {},
                "external_stats": session.external_stats or {}
            }
            
            try:
                result = pricing_agent(pricing_state)
                pricing = result.get("pricing", {})
                recommended = pricing.get("recommended_price", 0)
                
                if recommended > 0:
                    state["response_type"] = "pricing_response"
                    return f"💰 Piyasa fiyatlarına göre {int(recommended)} TL civarında satabilirsiniz."
                else:
                    state["response_type"] = "conversation"
                    return "Fiyat analizi için ürün marka ve modelini belirtir misiniz?"
            except Exception as e:
                self.log(f"Pricing agent failed: {str(e)}", "error")
                state["response_type"] = "conversation"
                return "Fiyat analizi için önce ürün bilgilerini tamamlayalım."
        
        elif intent == UserIntent.SEARCHING or (isinstance(intent, str) and intent == "searching"):
            session.set_stage(ConversationStage.ANALYZING)
            state["response_type"] = "start_search_flow"
            return "Ürün arıyorsunuz, hemen bakıyorum... 🔍"
        
        elif intent == UserIntent.QUESTION or (isinstance(intent, str) and intent == "question"):
            state["response_type"] = "question_response"
            return self._answer_question(message, session)
        
        else:
            state["response_type"] = "conversation"
            
            # Eğer önceki konuşma varsa context-aware yanıt ver
            if history_text:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", f"""Sen Megapazar asistanısın.

ÖNCEKİ KONUŞMA:
{history_text}

Kullanıcının yeni mesajına göre devam et. Eğer ürün satmaktan bahsediyorsa, önceki mesajlarındaki ürün bilgilerini akılda tut.

Kısa, sade, yardımsever Türkçe konuş."""),
                    ("human", "{message}")
                ])
                
                response = self.llm.invoke(prompt.format_messages(message=message))
                return response.content
            
            # İlk sefer - welcome mesajı
            return """Merhaba! 👋

PazarGlobal'e hoş geldiniz! Size nasıl yardımcı olabilirim?

• İlan vermek için: "Ürün satmak istiyorum" yazın veya fotoğraf gönderin
• Ürün aramak için: "... arıyorum" yazın
• Sorularınız için: Sorunuzu yazabilirsiniz"""
    
    def _handle_gathering_info(self, message: str, session, state: Dict) -> str:
        """Eksik bilgi toplama"""
        missing_fields = session.missing_fields or []
        current_product_info = session.product_info or {}
        conversation_history = session.conversation_history
        
        self.log(f"Gathering info - Missing fields: {missing_fields}, Product info: {current_product_info}")
        
        # Conversation history'yi context'e ekle
        history_context = ""
        if len(conversation_history) > 2:  # Son 2 mesajdan fazlaysa context ekle
            history_context = "\n\nÖNCEKİ MESAJLAR:\n" + "\n".join([
                f"{'Kullanıcı' if msg['role'] == 'user' else 'Asistan'}: {msg['content']}"
                for msg in conversation_history[-6:-1]  # Son 5 mesaj (en son hariç)
            ])
        
        # LLM ile kullanıcı cevabını parse et
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Kullanıcıdan ürün bilgisi topluyorsun.

Mevcut ürün bilgileri:
{current_info}{history_context}

Eksik bilgiler: {missing_fields}

Kullanıcının SON mesajından bu eksik bilgileri çıkar. DİKKATLİ OKU ve her bilgiyi yakala.

⚠️ ÖNEMLİ KURALLAR:
- "iphone", "iPhone 12", "iPhone 13 Pro" → {{"brand": "Apple", "model": "iPhone 12/13 Pro"}}
- "samsung", "S23 Ultra", "Samsung Galaxy" → {{"brand": "Samsung", "model": "..."}}
- "hp", "dell", "lenovo", "asus" → {{"brand": "HP/Dell/Lenovo/Asus"}}
- "2.el", "ikinci el", "kullanılmış", "çizik", "ekran değişmiş" → {{"condition": "2.el"}}
- "yeni", "sıfır", "kutulu" → {{"condition": "yeni"}}
- "2020", "satın aldığım sene 2020" → {{"year": "2020"}}
- "Snapdragon 8 Gen 2", "12GB RAM", "512GB" gibi teknik detaylar varsa ekle

🎯 KRITIK: "iPhone 12 sanırım", "S23 Ultra satıyorum" gibi BELİRSİZ ifadelerde bile markayı MUTLAKA yakala!

JSON döndür:
{{
    "extracted": {{"field_name": "extracted_value"}},  // Kullanıcının verdiği bilgiler
    "still_missing": ["field1", "field2"],  // Hala eksik olanlar
    "next_question": "Sıradaki soru metni"  // Eğer hala eksik varsa
}}

Örnekler:
Kullanıcı: "iPhone 12 sanırım, ama emin değilim"
→ {{"extracted": {{"brand": "Apple", "model": "iPhone 12"}}, "still_missing": ["condition"], "next_question": "Durumu nedir? Yeni mi, 2.el mi?"}}

Kullanıcı: "Samsung S23 Ultra satıyorum. Snapdragon 8 Gen 2"
→ {{"extracted": {{"brand": "Samsung", "model": "S23 Ultra"}}, "still_missing": ["condition"], "next_question": "Durumu nedir?"}}"""),
            ("human", "{message}")
        ])
        
        try:
            response = self.llm.invoke(prompt.format_messages(
                current_info=json.dumps(current_product_info, ensure_ascii=False),
                history_context=history_context,
                missing_fields=', '.join(missing_fields) if missing_fields else "Hiçbiri (tüm bilgiler tam)",
                message=message
            ))
            
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(content)
            extracted = result.get("extracted", {})
            still_missing = result.get("still_missing", [])
            next_question = result.get("next_question")
            
            self.log(f"Extracted: {extracted}, Still missing: {still_missing}")
            
            # Product info'yu güncelle
            # Quick heuristic: if brand is missing and user replied with a short single-word answer,
            # treat the whole message as the brand (helps WhatsApp short replies like "Barracuda")
            if ("brand" in (still_missing or missing_fields or [])):
                maybe_brand = message.strip()
                # If user replied with 1-3 words and no punctuation, assume it's brand
                if maybe_brand and len(maybe_brand.split()) <= 3 and all(c.isalnum() or c.isspace() for c in maybe_brand):
                    extracted = extracted or {}
                    extracted.setdefault("brand", maybe_brand)

            if extracted:
                current_product_info.update(extracted)
                session.update_product_info(current_product_info)
                # ensure session persisted
                from models.conversation_state import session_manager as _sm
                _sm.update_session(session)
            
            # Minimum gerekli alanlar kontrolü - LLM'nin still_missing'ini override et
            required_fields = ["brand", "condition"]
            actual_still_missing = [f for f in required_fields if not current_product_info.get(f) or current_product_info.get(f) == "null"]
            
            self.log(f"Required fields: {required_fields}, Actual missing: {actual_still_missing}")
            
            # 🚨 STOP CONDITION: Hala eksik var mı?
            if actual_still_missing:
                session.set_missing_fields(actual_still_missing)
                state["response_type"] = "gathering_info"
                field_tr = {"brand": "Marka", "model": "Model", "condition": "Durum (yeni/2.el)", "year": "Yıl"}
                next_field_tr = field_tr.get(actual_still_missing[0], actual_still_missing[0])
                return next_question if next_question and actual_still_missing[0] in next_question else f"{next_field_tr} nedir?"
            else:
                # ✅ STOP CONDITION MET: Tüm gerekli bilgiler toplandı!
                self.log("✅ All required fields collected! Forcing transition to ANALYZING stage.")
                session.set_missing_fields([])
                session.set_stage(ConversationStage.ANALYZING)
                session.intent = UserIntent.LISTING  # Force intent
                state["response_type"] = "start_listing_flow"
                state["product_info"] = current_product_info
                state["intent"] = "listing"  # Override intent for workflow
                return "Mükemmel! Şimdi piyasa araştırması yapıyorum... 🔍"
                
        except Exception as e:
            self.log(f"Gathering info parsing failed: {str(e)}", "error")
            # Hata durumunda eksik alanları manuel belirle
            if missing_fields:
                state["response_type"] = "gathering_info"
                field_tr = {"brand": "Marka", "model": "Model", "condition": "Durum (yeni/2.el)", "year": "Yıl"}
                next_field = field_tr.get(missing_fields[0], missing_fields[0])
                
                # 🎯 FALLBACK SORU: Brand karışıklığında alternatif soru sor
                if missing_fields[0] == "brand" and any(word in message.lower() for word in ["unuttum", "karışık", "galiba", "muydu"]):
                    return "Markayı tam hatırlamıyorsanız sorun değil! Ürünün rengini, ekran boyutunu veya başka bir özelliğini söyleyebilir misiniz? Böylece bulabilirim. 🔍"
                
                return f"{next_field} nedir? 🤔"
            else:
                state["response_type"] = "gathering_info"
                return "Ürününüzün marka, model ve durumunu (yeni/2.el) belirtir misiniz?"
    
    def _handle_preview(self, message: str, session, state: Dict) -> str:
        """Preview aşamasında kullanıcı yanıtı"""
        intent = session.intent
        if intent == UserIntent.CONFIRMING:
            # Kullanıcı onayladı - doğrudan Supabase'e kaydetmeye çalış
            session.set_stage(ConversationStage.CONFIRMING)
            state["response_type"] = "ready_to_confirm"

            # Session'dan listing bilgilerini al
            draft = session.listing_draft or {}
            state["listing_draft"] = draft

            try:
                # Save to Supabase using admin client (service role) to avoid RLS/permission issues
                from utils.supabase_client import get_supabase_admin
                supabase = get_supabase_admin()

                # Prepare payload - ensure keys match listings table
                payload = {
                    "title": draft.get("title", ""),
                    "description": draft.get("description", ""),
                    "category": draft.get("category", "Diğer"),
                    "price": draft.get("price", 0),
                    "images": draft.get("images", []),
                    "user_id": session.user_id,
                    "status": "active"
                }

                # Log payload for debugging (will appear in server logs)
                try:
                    import json as _json
                    self.log(f"Supabase insert payload: {_json.dumps(payload, ensure_ascii=False)}", "debug")
                except Exception:
                    self.log(f"Supabase insert payload (repr): {repr(payload)}", "debug")

                res = supabase.table("listings").insert(payload).execute()

                # Robustly inspect response for errors/data (client versions vary)
                data = None
                error = None
                try:
                    data = getattr(res, "data", None) or (res[0] if isinstance(res, (list, tuple)) and res else None) or (res.get("data") if isinstance(res, dict) else None)
                except Exception:
                    data = None

                try:
                    error = getattr(res, "error", None) or (res.get("error") if isinstance(res, dict) else None)
                except Exception:
                    error = None

                # Log full raw response for diagnostics
                try:
                    self.log(f"Supabase insert raw response: {repr(res)}", "debug")
                except Exception:
                    pass

                if error:
                    self.log(f"Supabase insert error detail: {error}", "error")
                    return "Üzgünüm, ilanınızı kaydederken bir sorun oldu. Lütfen daha sonra tekrar deneyin."

                # If there is returned data, capture inserted id and mark session completed
                if data:
                    try:
                        # data may be a list of inserted rows
                        row = data[0] if isinstance(data, (list, tuple)) and data else data
                        inserted_id = row.get("id") if isinstance(row, dict) else None
                        if inserted_id:
                            session.listing_id = inserted_id
                            self.log(f"Inserted listing id: {inserted_id}")
                    except Exception:
                        pass

                # Mark session completed and persist
                session.set_stage(ConversationStage.COMPLETED)
                from models.conversation_state import session_manager as _sm
                _sm.update_session(session)

                return "✅ İlanınız başarıyla yayınlandı! Teşekkürler."

            except Exception as e:
                self.log(f"Failed to save listing to Supabase: {e}", "error")
                return "Üzgünüm, ilanınızı kaydederken bir hata oluştu. Lütfen daha sonra tekrar deneyin."
        
        elif intent == UserIntent.EDITING:
            session.set_stage(ConversationStage.EDITING)
            state["response_type"] = "editing_mode"
            return "Ne değiştirmek istersiniz? (başlık, açıklama, fiyat, kategori)"
        
        elif intent == UserIntent.NEGOTIATING:
            # Fiyat müzakeresi
            price = self._extract_price(message)
            if price:
                session.set_user_price(price)
                state["response_type"] = "reprice_listing"  # ← FIX: workflow'da bu isim kullanılıyor
                state["user_price"] = price
                return f"Anladım, fiyatı {price} TL olarak değiştiriyorum. İlan tekrar hazırlanıyor... 💰"
            else:
                return "Fiyatı kaç TL olarak belirlemek istersiniz?"
        
        elif intent == UserIntent.CANCELLING:
            session.reset()
            state["response_type"] = "cancelled"
            return "İlan iptal edildi. Yeni bir ilan vermek ister misiniz?"
        
        else:
            return """İlanınız hazır! Ne yapmak istersiniz?

✅ Onayla - İlanı yayınla
✏️ Düzenle - Değişiklik yap
💰 Fiyat değiştir - "1500 TL olsun" gibi
❌ İptal - İptal et"""
    
    def _handle_negotiation(self, message: str, session, state: Dict) -> str:
        """Fiyat müzakeresi"""
        price = self._extract_price(message)
        
        if price:
            session.set_user_price(price)
            state["response_type"] = "reprice_listing"
            state["user_price"] = price
            return f"Tamam, fiyatı {price} TL yapıyorum. İlan güncelleniyor... 💰"
        
        elif session.intent == UserIntent.CONFIRMING:
            session.set_stage(ConversationStage.CONFIRMING)
            state["response_type"] = "confirm_listing"
            return "İlanınız yayınlanıyor... ✅"
        
        else:
            return "Fiyatı kaç TL olarak belirlemek istersiniz?"
    
    def _handle_editing(self, message: str, session, state: Dict) -> str:
        """Düzenleme modu"""
        # LLM ile hangi field'ı düzenlemek istediğini ve nasıl düzenleyeceğini tespit et
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
        
        try:
            response = self.llm.invoke(prompt.format_messages(
                listing_draft=json.dumps(session.listing_draft or {}, ensure_ascii=False),
                message=message
            ))
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            edit_info = json.loads(content)
            
            # Debug
            self.log(f"Parsed edit_info: {edit_info}")
            
            state["response_type"] = "edit_field"
            state["edit_field"] = edit_info.get("field")
            state["edit_value"] = edit_info.get("new_value")
            state["edit_description"] = edit_info.get("change_description")
            
            # Debug
            self.log(f"State updated - field: {state['edit_field']}, value: {state['edit_value']}")
            
            field_names = {
                "title": "Başlık",
                "description": "Açıklama",
                "price": "Fiyat",
                "category": "Kategori"
            }
            
            field_tr = field_names.get(edit_info.get("field"), "Alan")
            return f"{field_tr} düzenleniyor... ✏️"
            
        except Exception as e:
            self.log(f"Edit parsing failed: {str(e)}", "error")
            state["response_type"] = "conversation"
            return "Ne değiştirmek istersiniz? Örnek: 'başlığı değiştir', 'açıklamayı kısalt', 'fiyatı 1500 TL yap'"
    
    def _handle_general(self, message: str, session, state: Dict) -> str:
        """Genel conversation"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Sen Megapazar asistanısın.
Kısa, sade, yardımsever Türkçe konuş.
Kullanıcıya rehberlik et."""),
            ("human", "{message}")
        ])
        
        response = self.llm.invoke(prompt.format_messages(message=message))
        state["response_type"] = "conversation"
        return response.content
    
    def _answer_question(self, message: str, session) -> str:
        """Soru cevaplama - KISA ve ÖZ"""
        msg_lower = message.lower()
        
        # 🎯 KRITIK: "laptop satacaktım" gibi ifadeler listing'e dönmeli
        if any(word in msg_lower for word in ["satacak", "satmak", "satacağım", "satmayı"]):
            # Bu aslında listing niyeti - intent override
            self.log("🔄 QUESTION intent override: detected listing keywords in question")
            session.intent = UserIntent.LISTING
            session.set_stage(ConversationStage.GATHERING_INFO)
            return "Harika! Hangi ürünü satmak istiyorsunuz? 📸"
        
        # Kısa help responses
        if "kategori" in msg_lower or "premium" in msg_lower:
            return """Premium ürünler Elektronik › Üst Seviye kategorisinde listelenir.
            
Ne yapmak istersiniz?
• Ürün satmak → "Satmak istiyorum" yazın
• Ürün aramak → "Arıyorum" yazın"""
        
        if "nasıl" in msg_lower or "nedir" in msg_lower:
            return """PazarGlobal'de ürün satmak çok kolay:
1. Ürün bilgilerinizi paylaşın
2. AI otomatik fiyat önerisi sunar
3. İlanınız hazır!

"Ürün satmak istiyorum" yazarak başlayabilirsiniz."""
        
        # Generic kısa help
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Sen Megapazar asistanısın. 

KISA VE ÖZ cevap ver (max 3-4 cümle).
Platform özellikleri: ilan verme, AI fiyat önerisi, ürün arama."""),
            ("human", "{question}")
        ])
        
        response = self.llm.invoke(prompt.format_messages(question=message))
        return response.content
    
    def _extract_price(self, message: str) -> float:
        """Mesajdan fiyat çıkar"""
        import re
        
        self.log(f"Extracting price from: '{message}'")
        
        # "2000 TL", "1500 TL", "1.500 TL", "1500tl" gibi formatları yakala
        patterns = [
            r'(\d+[\.,]?\d*)\s*tl',
            r'(\d+[\.,]?\d*)\s*lira',
            r'fiyat[ı]?\s*(\d+[\.,]?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                price_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    price = float(price_str)
                    self.log(f"✅ Price extracted: {price} TL")
                    return price
                except:
                    continue
        
        self.log("⚠️ No price found in message")
        return None
    
    def _check_missing_info(self, product_info: Dict) -> List[str]:
        """Eksik bilgileri kontrol et"""
        required_fields = {
            "product_type": "Ürün tipi",
            "category": "Kategori",
            "condition": "Durumu (sıfır/ikinci el)",
            "quantity": "Adet"
        }
        
        missing = []
        for field, label in required_fields.items():
            if not product_info.get(field):
                missing.append(label)
        
        return missing

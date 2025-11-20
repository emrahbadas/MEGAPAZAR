"""
Enhanced Listing Workflow
Multi-turn conversation, müzakere, düzenleme destekli workflow
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict
from models.conversation_state import ConversationStage, UserIntent, session_manager
import json

# State tanımı
class EnhancedWorkflowState(TypedDict):
    user_id: str
    message: str
    image_url: str
    platform: str
    user_location: str
    
    # Session bilgisi
    session_state: Dict[str, Any]
    
    # Workflow control
    intent: str
    response_type: str  # conversation, start_listing_flow, confirm_listing, etc.
    
    # Agent outputs
    ai_response: str
    conversation_history: list
    product_info: Dict[str, Any]
    internal_stats: Dict[str, Any]
    external_stats: Dict[str, Any]
    pricing: Dict[str, Any]
    listing_draft: Dict[str, Any]
    
    # Special actions
    user_price: float  # Kullanıcının belirlediği fiyat
    edit_field: str    # Düzenlenecek alan
    edit_value: str    # Düzenleme değeri (direkt değer varsa, örn: "3500")
    edit_description: str  # Düzenleme açıklaması

def create_enhanced_listing_workflow():
    """
    Enhanced workflow with multi-turn conversation
    """
    from agents.conversation_enhanced import EnhancedConversationAgent
    from agents.text_parser import TextParserAgent
    from agents.product_match import ProductMatchAgent
    from agents.market_search import MarketSearchAgent
    from agents.pricing import PricingAgent
    from agents.listing_writer import ListingWriterAgent
    
    # Agents
    conversation_agent = EnhancedConversationAgent()
    text_parser = TextParserAgent()
    product_match = ProductMatchAgent()
    market_search = MarketSearchAgent()
    pricing_agent = PricingAgent()
    listing_writer = ListingWriterAgent()
    
    # Nodes
    def conversation_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
        """Conversation management"""
        return conversation_agent(state)
    
    def check_response_type(state: EnhancedWorkflowState) -> str:
        """Response type'a göre routing"""
        response_type = state.get("response_type", "conversation")
        
        if response_type == "start_listing_flow":
            return "text_parser"
        elif response_type == "ready_to_confirm":
            # Kullanıcı "onayla" dedi - /api/listing/confirm'e yönlendirilecek
            return "end"
        elif response_type == "reprice_listing":
            # Fiyat müzakeresi - reprice node'a git
            return "reprice"
        elif response_type == "edit_field":
            return "edit"
        elif response_type == "cancelled":
            return "end"
        else:
            return "end"
    
    def text_parser_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
        """Text parsing"""
        result = text_parser(state)
        
        # Session'ı güncelle
        session = session_manager.get_session(state["user_id"])
        if session:
            session.update_product_info(result.get("product_info", {}))
            session.set_stage(ConversationStage.ANALYZING)
            session_manager.update_session(session)
        
        return result
    
    def check_product_info(state: EnhancedWorkflowState) -> str:
        """Ürün bilgisi yeterli mi kontrol et - RECURSION GUARD"""
        from utils.openai_client import get_llm
        from utils.logger import setup_logger
        
        logger = setup_logger("check_product_info")
        product_info = state.get("product_info", {})
        product_type = product_info.get("product_type", "")
        category = product_info.get("category", "")
        brand = product_info.get("brand", "")
        condition = product_info.get("condition", "")
        
        logger.info(f"🔍 Checking product_info: type={product_type}, category={category}, brand={brand}, condition={condition}")
        
        # 🚨 CRITICAL STOP CONDITION: Minimum gerekli alanlar var mı?
        # Brand + condition varsa devam et (product_type/category opsiyonel olabilir)
        if brand and condition:
            logger.info("✅ STOP CONDITION MET: brand and condition present, proceeding to product_match")
            return "product_match"
        
        # Temel alanlar mutlaka olmalı
        if not product_type or not category:
            missing = []
            if not product_type:
                missing.append("product_type")
            if not category:
                missing.append("category")
            
            session = session_manager.get_session(state["user_id"])
            if session:
                session.set_missing_fields(missing)
                session.set_stage(ConversationStage.GATHERING_INFO)
                session_manager.update_session(session)
            
            logger.warning(f"⚠️ Missing critical fields: {missing}, returning to conversation")
            state["response_type"] = "gathering_info"
            state["ai_response"] = f"Birkaç detay daha öğrenebilir miyim?"
            return "conversation"
        
        # LLM ile dinamik eksik alan tespiti
        llm = get_llm(model="gpt-4o", temperature=0.3)
        
        prompt = f"""Bir kullanıcı "{product_type}" kategorisinde "{category}" ürünü satmak istiyor.

Mevcut bilgiler:
{json.dumps(product_info, ensure_ascii=False, indent=2)}

Bu ürün için MUTLAKA olması gereken kritik bilgiler neler?
Sadece listing kalitesi için ZORUNLU olanları belirt.

JSON döndür:
{{
    "critical_missing": ["field1", "field2"],  // Eksik kritik alanlar (boş array ise yeterli)
    "reason": "Neden bu alanlar kritik?"
}}

Örnekler:
- Araba: marka, model, yıl, km (kritik)
- Laptop: marka, model, RAM, işlemci (kritik)
- Kanepe: kişi sayısı, durum (yeterli, marka isteğe bağlı)
- Endüstriyel rotor: ürün tipi belli (yeterli)

SADECE gerçekten kritik olanları belirt! Opsiyonel bilgileri ekleme."""

        try:
            response = llm.invoke(prompt)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(content)
            critical_missing = result.get("critical_missing", [])
            
            if critical_missing:
                # Kritik bilgi eksik
                session = session_manager.get_session(state["user_id"])
                if session:
                    session.set_missing_fields(critical_missing)
                    session.set_stage(ConversationStage.GATHERING_INFO)
                    session_manager.update_session(session)
                
                state["response_type"] = "gathering_info"
                
                # İlk soruyu oluştur
                first_field = critical_missing[0]
                state["ai_response"] = f"{first_field} nedir?"
                return "conversation"
            
            # Bilgi yeterli, devam et
            return "product_match"
            
        except Exception as e:
            # LLM hatası - güvenli tarafta kal, devam et
            from utils.logger import setup_logger
            logger = setup_logger("check_product_info")
            logger.error(f"Dynamic check failed: {e}, continuing...")
            return "product_match"
    
    def product_match_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
        """Product matching"""
        return product_match(state)
    
    def market_search_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
        """Market search"""
        return market_search(state)
    
    def pricing_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
        """Pricing calculation"""
        # Session'da pricing varsa kullan (tutarlılık için)
        session = session_manager.get_session(state["user_id"])
        if session and session.pricing:
            state["pricing"] = session.pricing
            return state
        
        # İlk kez hesaplama yapılacak
        result = pricing_agent(state)
        
        # Session'a kaydet (bir daha hesaplamayacak)
        if session:
            session.pricing = result.get("pricing")
            session.set_stage(ConversationStage.PRICING)
            session_manager.update_session(session)
        
        return result
    
    def check_user_price(state: EnhancedWorkflowState) -> str:
        """Kullanıcı özel fiyat belirtti mi?"""
        session = session_manager.get_session(state["user_id"])
        
        if session and session.user_price_preference:
            # Kullanıcının fiyatını kullan
            state["pricing"] = {
                "recommended_price": session.user_price_preference,
                "source": "user_defined"
            }
            return "listing_writer"
        
        return "listing_writer"
    
    def listing_writer_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
        """Listing writing"""
        result = listing_writer(state)
        
        # Session'ı güncelle
        session = session_manager.get_session(state["user_id"])
        if session:
            session.update_listing_draft(result.get("listing_draft", {}))
            session.set_stage(ConversationStage.PREVIEW)
            session_manager.update_session(session)
        
        # Preview mesajı ekle
        draft = result.get("listing_draft", {})
        result["response_type"] = "listing_preview"
        result["ai_response"] = f"""✅ İlanınız hazır!

📋 **{draft.get('title', 'Başlık')}**

💰 Fiyat: {draft.get('price', 0)} TL
📦 Kategori: {draft.get('category', 'Kategori')}

📝 Açıklama:
{draft.get('description', 'Açıklama')[:200]}...

---
İlanı yayınlamak için "Onayla" yazın.
Fiyatı değiştirmek için "1500 TL olsun" yazın.
Değişiklik yapmak için "Düzenle" yazın.
"""
        
        return result
    
    def reprice_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
        """Fiyatı değiştir ve tekrar listing yaz"""
        user_price = state.get("user_price")
        
        if user_price:
            state["pricing"] = {
                "recommended_price": user_price,
                "source": "user_override"
            }
            
            # Session'dan mevcut product_info'yu al
            session = session_manager.get_session(state["user_id"])
            if session and session.product_info:
                state["product_info"] = session.product_info
            if session and session.internal_stats:
                state["internal_stats"] = session.internal_stats
            if session and session.external_stats:
                state["external_stats"] = session.external_stats
        
        # Direkt listing writer çağır
        return listing_writer_node(state)
    
    def edit_node(state: EnhancedWorkflowState) -> EnhancedWorkflowState:
        """Alan düzenle"""
        from utils.openai_client import get_llm
        
        edit_field = state.get("edit_field")
        edit_value = state.get("edit_value")
        edit_description = state.get("edit_description", "")
        
        session = session_manager.get_session(state["user_id"])
        if not session or not session.listing_draft:
            state["ai_response"] = "Düzenlenecek ilan bulunamadı."
            state["response_type"] = "conversation"
            return state
        
        listing_draft = session.listing_draft.copy()
        
        # Debug log
        from utils.logger import setup_logger
        logger = setup_logger("edit_node")
        logger.info(f"Edit field: {edit_field}, Edit value: {edit_value}, Description: {edit_description}")
        
        # Eğer direkt yeni değer verilmişse (fiyat gibi)
        if edit_field == "price" and edit_value:
            try:
                new_price = float(edit_value)
                listing_draft["price"] = new_price
                state["ai_response"] = f"✅ Fiyat {new_price} TL olarak güncellendi."
            except Exception as e:
                logger.error(f"Price conversion failed: {e}")
                state["ai_response"] = "Geçersiz fiyat değeri."
                state["response_type"] = "conversation"
                return state
        
        # LLM ile field düzenle (title, description, category)
        elif edit_field in ["title", "description", "category"]:
            llm = get_llm(model="gpt-4o", temperature=0.7)
            
            field_names = {
                "title": "başlık",
                "description": "açıklama",
                "category": "kategori"
            }
            
            prompt = f"""Aşağıdaki ilan {field_names[edit_field]} alanını düzenle.

Mevcut değer:
{listing_draft.get(edit_field, '')}

Değişiklik talebi: {edit_description}

Kurallar:
- {field_names[edit_field]} alanını kullanıcının isteğine göre düzenle
- Doğal ve profesyonel Türkçe kullan
- Sadece yeni {field_names[edit_field]} metnini döndür, açıklama yapma

Yeni {field_names[edit_field]}:"""
            
            response = llm.invoke(prompt)
            new_value = response.content.strip()
            
            listing_draft[edit_field] = new_value
            state["ai_response"] = f"✅ {field_names[edit_field].capitalize()} güncellendi."
        
        else:
            state["ai_response"] = "Geçersiz düzenleme alanı."
            state["response_type"] = "conversation"
            return state
        
        # Session'ı güncelle
        session.update_listing_draft(listing_draft)
        session.set_stage(ConversationStage.PREVIEW)
        session_manager.update_session(session)
        
        # State'i güncelle ve yeni preview göster
        state["listing_draft"] = listing_draft
        state["response_type"] = "listing_preview"
        
        # Preview mesajı
        state["ai_response"] = f"""✅ Değişiklik yapıldı!

📋 **{listing_draft.get('title', 'Başlık')}**

💰 Fiyat: {listing_draft.get('price', 0)} TL
📦 Kategori: {listing_draft.get('category', 'Kategori')}

📝 Açıklama:
{listing_draft.get('description', 'Açıklama')[:200]}...

---
İlanı yayınlamak için "Onayla" yazın.
Başka değişiklik için "Düzenle" yazın."""
        
        return state
    
    # Graph oluştur
    workflow = StateGraph(EnhancedWorkflowState)
    
    # Nodes ekle
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("text_parser", text_parser_node)
    workflow.add_node("product_match", product_match_node)
    workflow.add_node("market_search", market_search_node)
    workflow.add_node("pricing", pricing_node)
    workflow.add_node("listing_writer", listing_writer_node)
    workflow.add_node("reprice", reprice_node)
    workflow.add_node("edit", edit_node)
    
    # Entry point
    workflow.set_entry_point("conversation")
    
    # Edges
    workflow.add_conditional_edges(
        "conversation",
        check_response_type,
        {
            "text_parser": "text_parser",
            "reprice": "reprice",
            "edit": "edit",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "text_parser",
        check_product_info,
        {
            "product_match": "product_match",
            "conversation": "conversation"
        }
    )
    
    workflow.add_edge("product_match", "market_search")
    workflow.add_edge("market_search", "pricing")
    
    workflow.add_conditional_edges(
        "pricing",
        check_user_price,
        {
            "listing_writer": "listing_writer"
        }
    )
    
    workflow.add_edge("listing_writer", END)
    workflow.add_edge("reprice", END)
    workflow.add_edge("edit", END)
    
    # 🛡️ RECURSION GUARD: Increase limit and add checkpointer
    return workflow.compile(
        checkpointer=None,  # Can add MemorySaver() for debugging
        debug=False
    )

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import ListingRequest, AgentResponse, SearchRequest
from workflows.listing_flow_enhanced import create_enhanced_listing_workflow
from utils.logger import setup_logger
from config import get_settings
import uvicorn

# Settings ve logger
settings = get_settings()
logger = setup_logger("main")

# FastAPI uygulaması
app = FastAPI(
    title="Megapazar Agent API",
    description="AI-powered listing and search platform with enhanced conversation",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domainler ekleyin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced Workflow başlat
try:
    listing_workflow = create_enhanced_listing_workflow()
    logger.info("✅ Enhanced listing workflow initialized")
except Exception as e:
    logger.error(f"❌ Workflow initialization failed: {str(e)}")
    listing_workflow = None

# Background tasks başlat (session cleanup)
scheduler = None
try:
    from utils.background_tasks import start_background_tasks
    scheduler = start_background_tasks()
    logger.info("✅ Background tasks started")
except Exception as e:
    logger.warning(f"⚠️ Background tasks initialization failed: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Uygulama kapanırken cleanup"""
    if scheduler:
        scheduler.shutdown()
        logger.info("Background tasks stopped")

@app.get("/")
async def root():
    """Ana endpoint - health check"""
    return {
        "service": "Megapazar Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "listing": "/api/listing/start",
            "search": "/api/search",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {
        "status": "healthy",
        "workflow_ready": listing_workflow is not None
    }

@app.post("/test-simple")
async def test_simple_endpoint(request: dict):
    """Test endpoint - agent olmadan"""
    try:
        user_id = request.get("user_id", "unknown")
        message = request.get("message", "")
        
        msg_lower = message.lower()
        listing_keywords = ["ilan ver", "ilan vereceğim", "satmak istiyorum", "satacağım", "satış yap"]
        
        if any(keyword in msg_lower for keyword in listing_keywords):
            return {
                "message": "✅ Intent: LISTING detected!",
                "intent": "listing",
                "response_type": "test"
            }
        else:
            return {
                "message": "❌ Intent: UNKNOWN",
                "intent": "unknown",
                "response_type": "test"
            }
    except Exception as e:
        logger.exception(e)
        return {"error": str(e)}

@app.post("/debug/clear-session")
async def clear_session(user_id: str):
    """Debug endpoint to clear a session"""
    from models.conversation_state import session_manager
    session_file = session_manager._get_session_file(user_id)
    if session_file.exists():
        session_file.unlink()
    if user_id in session_manager.sessions:
        del session_manager.sessions[user_id]
    return {"message": f"Session cleared for {user_id}"}

@app.post("/conversation")
async def conversation_endpoint(request: dict):
    """
    n8n WhatsApp Bridge endpoint
    Multi-turn conversation handler with session persistence
    
    Body:
    - user_id: Phone number (from WhatsApp)
    - message: User message
    - platform: 'whatsapp' or 'web'
    """
    try:
        user_id = request.get("user_id", "unknown")
        message = request.get("message", "")
        platform = request.get("platform", "whatsapp")
        
        logger.info(f"📞 Conversation from {user_id}: {message[:50]}...")
        
        try:
            # Enhanced Conversation Agent kullan (multi-turn + session management)
            from agents.conversation_enhanced import EnhancedConversationAgent
            from agents.help import HelpAgent
            from models.conversation_state import session_manager, ConversationStage, UserIntent
            logger.info("✅ Imports successful")
        except Exception as import_error:
            logger.error(f"❌ Import error: {str(import_error)}")
            logger.exception(import_error)
            raise
        
        # Session kontrolü
        logger.info("🔄 Getting or creating session...")
        session = session_manager.get_or_create_session(user_id, platform)
        logger.info(f"📋 Session stage: {session.stage}, Intent: {session.intent}")
        logger.info(f"📜 Conversation history: {len(session.conversation_history)} messages")
        
        # BASIT INTENT DETECTION (agent çağırmadan önce)
        msg_lower = message.lower()
        detected_intent = "unknown"
        
        listing_keywords = ["ilan ver", "ilan vereceğim", "satmak istiyorum", "satacağım", "satış yap"]
        if any(keyword in msg_lower for keyword in listing_keywords):
            detected_intent = "listing"
            logger.info(f"🎯 Quick intent detection: LISTING")
        
        # State hazırla (session'dan tüm bilgileri aktar)
        conv_state = {
            "user_id": user_id,
            "message": message,
            "platform": platform,
            "image_url": session.image_url or "",
            "intent": detected_intent,  # Basit intent detection sonucu
            "response_type": "",
            "session_state": session.dict(),
            "conversation_history": session.conversation_history,  # GEÇMİŞ MESAJLAR
            "product_info": session.product_info or {},
            "internal_stats": session.internal_stats or {},
            "external_stats": session.external_stats or {},
            "pricing": session.pricing or {},
            "listing_draft": session.listing_draft or {},
            "user_price": session.user_price_preference or 0.0,
            "edit_field": "",
            "ai_response": "",
            "missing_fields": session.missing_fields or []
        }
        
        # EnhancedConversationAgent çalıştır
        logger.info("🤖 Calling EnhancedConversationAgent...")
        conversation_agent = EnhancedConversationAgent()
        logger.info("✅ Agent created, invoking...")
        result = conversation_agent(conv_state)
        logger.info(f"✅ Agent returned - response_type: {result.get('response_type')}, intent: {result.get('intent')}")
        
        response_type = result.get("response_type", "conversation")
        intent = result.get("intent", "unknown")
        ai_response = result.get("ai_response", "")
        
        logger.info(f"🎯 Response type: {response_type}, Intent: {intent}")
        
        # Response type'a göre işlem yap
        if response_type == "start_listing_flow":
            # Workflow'a yönlendir
            if not listing_workflow:
                raise HTTPException(status_code=500, detail="Workflow not initialized")
            
            logger.info("🚀 Starting listing workflow...")
            
            # Workflow state
            workflow_state = {
                "user_id": user_id,
                "message": message,
                "image_url": "",
                "platform": platform,
                "user_location": "",
                "intent": intent,
                "response_type": "",
                "session_state": result.get("session_state", {}),
                "conversation_history": result.get("conversation_history", []),
                "product_info": result.get("product_info", {}),
                "internal_stats": {},
                "external_stats": {},
                "pricing": {},
                "listing_draft": {},
                "user_price": 0.0,
                "edit_field": "",
                "ai_response": ""
            }
            
            # Workflow çalıştır
            workflow_result = listing_workflow.invoke(workflow_state)
            
            return {
                "message": workflow_result.get("ai_response", "İlan hazırlanıyor..."),
                "intent": intent,
                "response_type": workflow_result.get("response_type"),
                "data": workflow_result.get("listing_draft")
            }
        
        elif response_type == "start_search_flow":
            # Search agent
            from agents.buyer_search import BuyerSearchAgent
            
            search_agent = BuyerSearchAgent()
            search_state = {
                "search_query": message,
                "search_filters": {}
            }
            
            search_result = search_agent(search_state)
            response_message = search_agent.format_results(search_result.get("search_results", []))
            
            return {
                "message": response_message,
                "intent": "search",
                "count": search_result.get("search_count", 0)
            }
        
        elif response_type == "question_response":
            # Soru cevabı - HelpAgent kullan
            help_agent = HelpAgent()
            help_result = help_agent(result)
            
            return {
                "message": help_result.get("ai_response"),
                "intent": "help"
            }
        
        elif response_type == "ready_to_confirm":
            # İlan onay aşaması
            return {
                "message": ai_response,
                "intent": "confirming",
                "data": result.get("listing_draft")
            }
        
        elif response_type == "reprice_listing":
            # Fiyat değişikliği - workflow'a git
            if not listing_workflow:
                raise HTTPException(status_code=500, detail="Workflow not initialized")
            
            workflow_state = {
                "user_id": user_id,
                "message": message,
                "image_url": "",
                "platform": platform,
                "user_location": "",
                "intent": "listing",
                "response_type": "reprice_listing",
                "session_state": result.get("session_state", {}),
                "conversation_history": result.get("conversation_history", []),
                "product_info": result.get("product_info", {}),
                "internal_stats": result.get("internal_stats", {}),
                "external_stats": result.get("external_stats", {}),
                "pricing": result.get("pricing", {}),
                "listing_draft": result.get("listing_draft", {}),
                "user_price": result.get("user_price", 0.0),
                "edit_field": "",
                "ai_response": ""
            }
            
            workflow_result = listing_workflow.invoke(workflow_state)
            
            return {
                "message": workflow_result.get("ai_response"),
                "intent": "listing",
                "data": workflow_result.get("listing_draft")
            }
        
        else:
            # Normal conversation response
            return {
                "message": ai_response,
                "intent": intent,
                "response_type": response_type
            }
        
    except Exception as e:
        logger.error(f"❌ Conversation error: {str(e)}")
        logger.exception(e)
        return {
            "message": "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.",
            "intent": "error"
        }

@app.post("/api/listing/start", response_model=AgentResponse)
async def start_listing(request: ListingRequest):
    """
    İlan verme akışını başlat (Enhanced multi-turn conversation)
    
    Body:
    - user_id: Kullanıcı ID
    - message: Kullanıcı mesajı
    - image_url: Opsiyonel fotoğraf URL'i
    - platform: 'web' veya 'whatsapp'
    - user_location: Opsiyonel konum
    """
    try:
        logger.info(f"📝 New listing request from user: {request.user_id}")
        logger.info(f"💬 Message: {request.message}")
        
        if not listing_workflow:
            raise HTTPException(status_code=500, detail="Workflow not initialized")
        
        # Initial state (enhanced)
        initial_state = {
            "user_id": request.user_id,
            "message": request.message,
            "image_url": request.image_url or "",
            "platform": request.platform,
            "user_location": request.user_location or "",
            "intent": "",
            "response_type": "",
            "session_state": {},
            "conversation_history": [],
            "product_info": {},
            "internal_stats": {},
            "external_stats": {},
            "pricing": {},
            "listing_draft": {},
            "user_price": 0.0,
            "edit_field": "",
            "ai_response": ""
        }
        
        # Workflow çalıştır
        logger.info("🚀 Running enhanced listing workflow...")
        result = listing_workflow.invoke(initial_state)
        
        # Response oluştur
        response = AgentResponse(
            type=result.get("response_type", "conversation"),
            message=result.get("ai_response", ""),
            data=result.get("listing_draft") if result.get("listing_draft") else None,
            next_action="await_user_input"
        )
        
        logger.info(f"✅ Listing flow completed: {response.type}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Listing flow error: {str(e)}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/listing/confirm")
async def confirm_listing(listing_data: dict):
    """
    İlanı onayla ve Supabase'e kaydet
    
    TODO: Implement after Supabase setup
    """
    try:
        from utils.supabase_client import get_supabase_admin
        supabase = get_supabase_admin()
        
        logger.info(f"💾 Confirming listing for user: {listing_data.get('user_id')}")
        
        # İlanı kaydet (images kolonu kaldırıldı - product_images tablosu kullanılıyor)
        # listing_data yapısı: {"user_id": "...", "listing_data": {...}} veya direk data içinde
        listing_info = listing_data.get("listing_data", {})
        
        # Eğer listing_data yoksa, data field'ını dene (listing/start response'undan geliyorsa)
        if not listing_info or not listing_info.get("title"):
            listing_info = listing_data.get("data", {})
        
        # Hala yoksa direkt listing_data kullan
        if not listing_info or not listing_info.get("title"):
            listing_info = listing_data
        
        user_id = listing_data.get("user_id") or listing_info.get("user_id")
        
        # Validation
        if not listing_info.get("title"):
            raise HTTPException(status_code=400, detail="Missing required field: title")
        
        result = supabase.table('listings').insert({
            "user_id": user_id,
            "title": listing_info.get("title"),
            "description": listing_info.get("description"),
            "price": listing_info.get("price"),
            "category": listing_info.get("category"),
            "location": listing_info.get("location"),
            "stock": listing_info.get("stock", 1),
            "status": "active",
            "market_price_at_publish": listing_info.get("suggested_price")  # Save market price from PricingAgent
        }).execute()
        
        listing_id = result.data[0]['id'] if result.data else None
        
        # Embedding oluştur ve kaydet
        try:
            from utils.openai_client import get_openai_client
            
            # Title + description ile embedding oluştur
            text_for_embedding = f"{listing_info.get('title')} {listing_info.get('description')}"
            client = get_openai_client()
            
            embedding_response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text_for_embedding
            )
            embedding = embedding_response.data[0].embedding
            
            # product_embeddings tablosuna kaydet
            supabase.table('product_embeddings').insert({
                "listing_id": listing_id,
                "embedding": embedding
            }).execute()
            
            logger.info(f"✅ Embedding created for listing {listing_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create embedding: {str(e)}")
        
        logger.info(f"✅ Listing saved with ID: {listing_id}")
        
        return {
            "status": "confirmed",
            "listing_id": listing_id,
            "message": "İlanınız başarıyla yayınlandı! 🎉"
        }
        
    except Exception as e:
        logger.error(f"❌ Listing confirmation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def test_agents():
    """
    Agent'ları test et (development only)
    """
    try:
        return {
            "status": "ok",
            "message": "Use POST /api/listing/start to test agents",
            "example": {
                "user_id": "test-123",
                "message": "4 adet endüstriyel rotor satmak istiyorum",
                "platform": "web"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/listings/{listing_id}/images")
async def get_listing_images_endpoint(listing_id: str):
    """
    İlanın resimlerini getir
    """
    try:
        from utils.storage_helper import get_listing_images
        
        images = get_listing_images(listing_id)
        
        return {
            "listing_id": listing_id,
            "images": images,
            "count": len(images)
        }
        
    except Exception as e:
        logger.error(f"❌ Get images error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/listings/{listing_id}/images/upload-from-url")
async def upload_image_endpoint(listing_id: str, image_url: str, is_primary: bool = False):
    """
    URL'den resim yükle
    
    Args:
        listing_id: İlan ID
        image_url: Resim URL'i
        is_primary: Ana resim mi?
    """
    try:
        from utils.storage_helper import upload_image_from_url
        
        logger.info(f"📸 Uploading image from URL for listing {listing_id}")
        
        result = upload_image_from_url(
            listing_id=listing_id,
            image_url=image_url,
            is_primary=is_primary
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Image upload failed")
        
        return {
            "success": True,
            "image": result
        }
        
    except Exception as e:
        logger.error(f"❌ Image upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/listing/{listing_id}")
async def update_listing(listing_id: str, request: dict):
    """
    İlan güncelle
    
    Body:
    - user_id: Kullanıcı ID (ownership validation)
    - title, description, price, category, status (optional)
    """
    try:
        from utils.supabase_client import get_supabase_admin
        supabase = get_supabase_admin()
        
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id required")
        
        logger.info(f"📝 Update listing {listing_id} by user {user_id}")
        
        # Ownership validation
        existing = supabase.table('listings').select('user_id').eq('id', listing_id).execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        if existing.data[0]['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit this listing")
        
        # Update fields
        update_data = {}
        if 'title' in request:
            update_data['title'] = request['title']
        if 'description' in request:
            update_data['description'] = request['description']
        if 'price' in request:
            update_data['price'] = request['price']
        if 'category' in request:
            update_data['category'] = request['category']
        if 'status' in request:
            update_data['status'] = request['status']
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_data['updated_at'] = 'now()'
        
        result = supabase.table('listings').update(update_data).eq('id', listing_id).execute()
        
        logger.info(f"✅ Listing {listing_id} updated")
        
        return {
            "status": "success",
            "listing_id": listing_id,
            "message": "İlan güncellendi",
            "updated": update_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update listing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/listing/{listing_id}")
async def delete_listing(listing_id: str, user_id: str):
    """
    İlan sil (soft delete)
    
    Query params:
    - user_id: Kullanıcı ID (ownership validation)
    """
    try:
        from utils.supabase_client import get_supabase_admin
        supabase = get_supabase_admin()
        
        logger.info(f"🗑️ Delete listing {listing_id} by user {user_id}")
        
        # Ownership validation
        existing = supabase.table('listings').select('user_id').eq('id', listing_id).execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        if existing.data[0]['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
        
        # Soft delete (is_active=false yerine status='inactive')
        supabase.table('listings').update({
            'status': 'inactive',
            'updated_at': 'now()'
        }).eq('id', listing_id).execute()
        
        logger.info(f"✅ Listing {listing_id} deleted (soft delete)")
        
        return {
            "status": "success",
            "listing_id": listing_id,
            "message": "İlan silindi"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete listing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/listings/my")
async def get_my_listings(
    user_id: str = Query(..., description="User ID"),
    status: str = Query("active", description="Status filter: active/inactive/all")
):
    """
    Kullanıcının ilanlarını listele
    
    Query params:
    - user_id: Kullanıcı ID (required)
    - status: Durum filtresi - active/inactive/all (default: active)
    
    Response:
    - listings: List of {id, title, description, price, category, status, created_at, updated_at}
    """
    try:
        from utils.supabase_client import get_supabase_admin
        supabase = get_supabase_admin()
        
        logger.info(f"📋 Get my listings - user_id: {user_id}, status: {status}")
        
        # Build query
        query = supabase.table('listings').select(
            'id, title, description, price, category, status, created_at, updated_at'
        ).eq('user_id', user_id).order('created_at', desc=True)
        
        # Apply status filter
        if status != "all":
            query = query.eq('status', status)
        
        result = query.execute()
        
        logger.info(f"✅ Found {len(result.data)} listings for user {user_id}")
        
        return {
            "status": "success",
            "count": len(result.data),
            "listings": result.data
        }
        
    except Exception as e:
        logger.error(f"❌ Get my listings error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notifications")
async def get_notifications(
    user_id: str = Query(..., description="User ID"),
    unread_only: bool = Query(False, description="Only unread notifications"),
    limit: int = Query(50, description="Maximum number of notifications")
):
    """
    Get user notifications
    Query params:
        - user_id: User ID (required)
        - unread_only: Only return unread notifications (default: false)
        - limit: Max results (default: 50)
    """
    try:
        from utils.supabase_client import get_supabase_admin
        supabase = get_supabase_admin()
        
        query = supabase.table("notifications")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)
        
        if unread_only:
            query = query.eq("is_read", False)
        
        result = query.execute()
        
        return {
            "status": "success",
            "count": len(result.data),
            "unread_count": sum(1 for n in result.data if not n.get("is_read")),
            "notifications": result.data
        }
        
    except Exception as e:
        logger.error(f"❌ Get notifications error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notifications/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: str,
    user_id: str = Query(..., description="User ID for ownership validation")
):
    """Mark a notification as read"""
    try:
        from utils.supabase_client import get_supabase_admin
        supabase = get_supabase_admin()
        
        # Ownership validation
        existing = supabase.table("notifications")\
            .select("user_id")\
            .eq("id", notification_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        if existing.data[0]["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Mark as read
        from datetime import datetime
        supabase.table("notifications")\
            .update({"is_read": True, "read_at": datetime.now().isoformat()})\
            .eq("id", notification_id)\
            .execute()
        
        return {
            "status": "success",
            "message": "Notification marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Mark notification read error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/check-prices")
async def trigger_price_check():
    """
    Manually trigger price check (admin endpoint)
    In production, add authentication
    """
    try:
        from utils.price_monitor import check_prices
        result = check_prices()
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"❌ Price check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_products(request: dict):
    """
    Search for products
    Request body:
        - user_id: str
        - query: str (e.g., "laptop 5000 TL altı")
        - filters: dict (optional, e.g., {"category": "Elektronik", "max_price": 5000})
    """
    try:
        from agents.buyer_search import BuyerSearchAgent
        
        user_id = request.get("user_id")
        query = request.get("query", "")
        filters = request.get("filters", {})
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        logger.info(f"🔍 Search request from {user_id}: {query}")
        
        # Run search agent
        search_agent = BuyerSearchAgent()
        state = {
            "search_query": query,
            "search_filters": filters
        }
        
        result = search_agent(state)
        
        # Format response
        response_message = search_agent.format_results(result.get("search_results", []))
        
        return {
            "status": "success",
            "query": query,
            "filters": filters,
            "count": result.get("search_count", 0),
            "results": result.get("search_results", [])[:10],  # Top 10
            "message": response_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/order/create")
async def create_order(request: dict):
    """
    Create an order
    Request body:
        - buyer_id: str
        - listing_id: str
        - quantity: int (optional, default: 1)
    """
    try:
        from agents.order import OrderAgent
        
        buyer_id = request.get("buyer_id")
        listing_id = request.get("listing_id")
        quantity = request.get("quantity", 1)
        
        if not buyer_id or not listing_id:
            raise HTTPException(status_code=400, detail="buyer_id and listing_id are required")
        
        logger.info(f"📦 Order request: buyer={buyer_id}, listing={listing_id}, qty={quantity}")
        
        # Run order agent
        order_agent = OrderAgent()
        state = {
            "buyer_id": buyer_id,
            "listing_id": listing_id,
            "quantity": quantity
        }
        
        result = order_agent(state)
        
        if result.get("order_status") == "success":
            return {
                "status": "success",
                "order_id": result.get("order_id"),
                "order_data": result.get("order_data"),
                "message": result.get("order_message")
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=result.get("order_message", "Order creation failed")
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Order creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/order/{order_id}")
async def get_order(order_id: str, user_id: str = Query(..., description="User ID for auth")):
    """Get order details"""
    try:
        from agents.order import OrderAgent
        
        order_agent = OrderAgent()
        order_data = order_agent.get_order_status(order_id)
        
        if not order_data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Verify user is buyer or seller
        if order_data['buyer_id'] != user_id and order_data['seller_id'] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        return {
            "status": "success",
            "order": order_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get order error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 Starting Megapazar Agent API...")
    logger.info(f"📍 Host: {settings.host}:{settings.port}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False  # Reload'u kapat
    )

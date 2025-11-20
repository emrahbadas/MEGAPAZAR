from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ListingRequest(BaseModel):
    """İlan verme isteği"""
    user_id: str
    message: str
    image_url: Optional[str] = None
    platform: str = "web"  # 'web' or 'whatsapp'
    user_location: Optional[str] = None

class ProductInfo(BaseModel):
    """Ürün bilgileri"""
    product_type: str
    brand: Optional[str] = None
    category: str
    condition: str = "used"  # 'new', 'used', 'damaged'
    quantity: int = 1
    estimated_attributes: Dict[str, Any] = {}

class PricingInfo(BaseModel):
    """Fiyatlandırma bilgileri"""
    suggested_price: float
    min_price: float
    max_price: float
    reason: str

class ListingDraft(BaseModel):
    """İlan taslağı"""
    title: str
    description: str
    short_summary: str
    price: float
    category: str
    product_info: ProductInfo

class AgentResponse(BaseModel):
    """Agent cevabı"""
    type: str  # 'ask_question', 'listing_preview', 'listing_complete', 'conversation'
    message: str
    data: Optional[Dict[str, Any]] = None
    next_action: Optional[str] = None

class SearchRequest(BaseModel):
    """Ürün arama isteği"""
    user_id: str
    query: str
    filters: Optional[Dict[str, Any]] = None

class OrderRequest(BaseModel):
    """Sipariş isteği"""
    listing_id: str
    buyer_id: str
    quantity: int = 1

class UpdateListingRequest(BaseModel):
    """İlan güncelleme isteği"""
    user_id: str
    listing_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    status: Optional[str] = None  # 'active', 'sold', 'inactive'

class DeleteListingRequest(BaseModel):
    """İlan silme isteği"""
    user_id: str
    listing_id: str

class NotificationResponse(BaseModel):
    """Bildirim cevabı"""
    id: str
    user_id: str
    listing_id: Optional[str] = None
    type: str  # 'price_alert', 'info', 'warning'
    title: str
    message: str
    metadata: Optional[Dict[str, Any]] = None
    is_read: bool = False
    created_at: datetime
    read_at: Optional[datetime] = None

class MegapazarState(BaseModel):
    """LangGraph state modeli"""
    user_id: str
    message: str
    image_url: Optional[str] = None
    platform: str = "web"
    user_location: Optional[str] = None
    intent: Optional[str] = None
    conversation_history: List[Dict[str, str]] = []
    product_info: Optional[Dict[str, Any]] = None
    internal_stats: Dict[str, Any] = {}
    external_stats: Dict[str, Any] = {}
    pricing: Optional[Dict[str, Any]] = None
    listing_draft: Optional[Dict[str, Any]] = None
    response_type: Optional[str] = None
    ai_response: str = ""
    
    class Config:
        arbitrary_types_allowed = True

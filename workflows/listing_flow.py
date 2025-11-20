from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict, Any
from agents.conversation import ConversationAgent
from agents.listing_coordinator import ListingCoordinator

class MegapazarState(TypedDict):
    """LangGraph state tipi"""
    user_id: str
    message: str
    image_url: Optional[str]
    platform: str
    user_location: Optional[str]
    intent: Optional[str]
    conversation_history: List[Dict[str, str]]
    product_info: Optional[Dict[str, Any]]
    internal_stats: Dict[str, Any]
    external_stats: Dict[str, Any]
    pricing: Optional[Dict[str, Any]]
    listing_draft: Optional[Dict[str, Any]]
    response_type: Optional[str]
    ai_response: str

def create_listing_workflow():
    """İlan verme workflow'unu oluştur"""
    
    # Agent'ları başlat
    conversation_agent = ConversationAgent()
    listing_coordinator = ListingCoordinator()
    
    # Graph oluştur
    workflow = StateGraph(MegapazarState)
    
    # Node'ları ekle
    workflow.add_node("conversation", conversation_agent)
    workflow.add_node("listing", listing_coordinator)
    
    # Başlangıç noktası
    workflow.set_entry_point("conversation")
    
    # Conditional routing fonksiyonu
    def route_by_intent(state: MegapazarState) -> str:
        """Intent'e göre yönlendirme"""
        intent = state.get("intent", "conversation")
        
        if intent == "listing":
            return "listing"
        elif intent == "search":
            # TODO: BuyerSearchAgent eklenecek
            return END
        elif intent == "order":
            # TODO: OrderAgent eklenecek
            return END
        else:
            return END
    
    # Conversation'dan sonra intent'e göre yönlendir
    workflow.add_conditional_edges(
        "conversation",
        route_by_intent,
        {
            "listing": "listing",
            END: END
        }
    )
    
    # Listing'den sonra bitir
    workflow.add_edge("listing", END)
    
    return workflow.compile()

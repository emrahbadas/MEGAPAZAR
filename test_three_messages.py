from agents.conversation_enhanced import EnhancedConversationAgent
from models.conversation_state import session_manager, ConversationStage, UserIntent

# Clear and create session
user_id = "+905551234567"
session_file = session_manager._get_session_file(user_id)
if session_file.exists():
    session_file.unlink()
if user_id in session_manager.sessions:
    del session_manager.sessions[user_id]

agent = EnhancedConversationAgent()

# Message 1
session = session_manager.get_or_create_session(user_id, "whatsapp")
state1 = {
    "user_id": user_id,
    "message": "Ürün satmak istiyorum",
    "platform": "whatsapp",
    "intent": "listing",
    "response_type": "",
    "session_state": session.model_dump(),
    "conversation_history": session.conversation_history,
    "product_info": session.product_info or {},
    "missing_fields": session.missing_fields or []
}
result1 = agent(state1)
print(f"Message 1: {result1['ai_response']}\n")

# Message 2
session = session_manager.get_or_create_session(user_id, "whatsapp")
state2 = {
    "user_id": user_id,
    "message": "Laptop bilgisayar",
    "platform": "whatsapp",
    "intent": "unknown",
    "response_type": "",
    "session_state": session.model_dump(),
    "conversation_history": session.conversation_history,
    "product_info": session.product_info or {},
    "missing_fields": session.missing_fields or []
}
result2 = agent(state2)
print(f"Message 2: {result2['ai_response']}\n")

# Message 3
session = session_manager.get_or_create_session(user_id, "whatsapp")
state3 = {
    "user_id": user_id,
    "message": "2.el hp marka satın aldığım sene 2020",
    "platform": "whatsapp",
    "intent": "unknown",
    "response_type": "",
    "session_state": session.model_dump(),
    "conversation_history": session.conversation_history,
    "product_info": session.product_info or {},
    "missing_fields": session.missing_fields or []
}
try:
    result3 = agent(state3)
    print(f"Message 3: {result3['ai_response']}")
    print(f"Response Type: {result3['response_type']}")
    print(f"Product Info: {result3['product_info']}")
except Exception as e:
    print(f"❌ Error on message 3: {e}")
    import traceback
    traceback.print_exc()

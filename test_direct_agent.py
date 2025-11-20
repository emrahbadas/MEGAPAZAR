from agents.conversation_enhanced import EnhancedConversationAgent
from models.conversation_state import session_manager

# Clear session
user_id = "+905551234567"
session_file = session_manager._get_session_file(user_id)
if session_file.exists():
    session_file.unlink()
    print(f"✅ Deleted session file\n")

if user_id in session_manager.sessions:
    del session_manager.sessions[user_id]
    print(f"✅ Cleared from memory\n")

# Create fresh session
session = session_manager.get_or_create_session(user_id, "whatsapp")
print(f"📋 Session created")
print(f"   Stage: {session.stage}")
print(f"   Intent: {session.intent}")
print(f"   History: {len(session.conversation_history)} messages\n")

# Call agent
agent = EnhancedConversationAgent()
state = {
    "user_id": user_id,
    "message": "Ürün satmak istiyorum",
    "platform": "whatsapp",
    "intent": "listing",
    "response_type": "",
    "session_state": session.dict(),
    "conversation_history": session.conversation_history,
    "product_info": session.product_info or {},
    "missing_fields": session.missing_fields or []
}

print("🤖 Calling agent...")
result = agent(state)

print(f"\n📤 Agent response:")
print(f"   AI Response: {result.get('ai_response')}")
print(f"   Intent: {result.get('intent')}")
print(f"   Response Type: {result.get('response_type')}")
print(f"   Product Info: {result.get('product_info')}")

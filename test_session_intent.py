"""
Basit test - agent olmadan intent detection
"""
from models.conversation_state import session_manager, UserIntent

# Session oluştur
session = session_manager.get_or_create_session("+905551234567", "whatsapp")
print(f"Session created - Stage: {session.stage}, Intent: {session.intent}")

# Mesaj ekle
session.add_message("user", "Ürün satmak istiyorum")
print(f"Message added - History: {len(session.conversation_history)}")

# Intent detection (basit keyword matching)
message = "Ürün satmak istiyorum"
msg_lower = message.lower()

listing_keywords = ["ilan ver", "ilan vereceğim", "satmak istiyorum", "satacağım", "satış yap"]
if any(keyword in msg_lower for keyword in listing_keywords):
    detected_intent = UserIntent.LISTING
else:
    detected_intent = UserIntent.UNKNOWN

print(f"\n✅ Detected Intent: {detected_intent}")
print(f"✅ Intent value: {detected_intent.value}")

# Session'a kaydet
session.intent = detected_intent
session_manager.update_session(session)
print(f"✅ Session updated")

# Tekrar yükle
session2 = session_manager.get_session("+905551234567")
print(f"\n📋 Reloaded Session - Intent: {session2.intent}")

"""
Basit editing flow test - API olmadan
"""
from models.conversation_state import session_manager, ConversationStage, UserIntent
from agents.conversation_enhanced import EnhancedConversationAgent
from workflows.listing_flow_enhanced import create_enhanced_listing_workflow

def test_editing_without_api():
    print("EDITING FLOW TEST (Direct workflow)")
    print("=" * 60)
    
    user_id = "test-user-123"
    
    # Workflow başlat
    workflow = create_enhanced_listing_workflow()
    print("OK Workflow initialized")
    
    # Step 1: Create listing
    print("\nStep 1: Creating listing...")
    state = {
        "user_id": user_id,
        "message": "Endüstriyel rotor satmak istiyorum",
        "image_url": "",
        "platform": "web",
        "user_location": "",
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
    
    result = workflow.invoke(state)
    print(f"OK Response: {result['ai_response'][:150]}...")
    print(f"Response Type: {result.get('response_type')}")
    
    # Step 2: Get preview
    print("\nStep 2: Getting preview...")
    session = session_manager.get_session(user_id)
    if session:
        print(f"Stage: {session.stage}")
        print(f"Draft exists: {bool(session.listing_draft)}")
    
    state2 = {
        **state,
        "message": "Önizle"
    }
    result2 = workflow.invoke(state2)
    print(f"OK Response: {result2['ai_response'][:200]}...")
    print(f"Response Type: {result2.get('response_type')}")
    
    # Step 3: Start editing
    print("\nStep 3: Requesting to edit...")
    state3 = {
        **state,
        "message": "Düzenle"
    }
    result3 = workflow.invoke(state3)
    print(f"OK Response: {result3['ai_response'][:150]}...")
    print(f"Response Type: {result3.get('response_type')}")
    
    session = session_manager.get_session(user_id)
    if session:
        print(f"Stage: {session.stage}")
    
    # Step 4: Edit title
    print("\nStep 4: Editing title...")
    state4 = {
        **state,
        "message": "başlığı daha çekici yap"
    }
    result4 = workflow.invoke(state4)
    print(f"OK Response: {result4['ai_response'][:200]}...")
    print(f"Response Type: {result4.get('response_type')}")
    
    if result4.get('listing_draft'):
        print(f"\nNew Title: {result4['listing_draft'].get('title')}")
    
    # Step 5: Edit price
    print("\nStep 5: Editing price...")
    state5 = {
        **result4,  # Use previous result to maintain state
        "message": "Düzenle"
    }
    result5 = workflow.invoke(state5)
    print(f"Response Type: {result5.get('response_type')}")
    
    state6 = {
        **result5,  # Maintain state chain
        "message": "fiyatı 3500 TL yap"
    }
    result6 = workflow.invoke(state6)
    print(f"OK Response: {result6['ai_response'][:200]}...")
    print(f"Response Type: {result6.get('response_type')}")
    
    if result6.get('listing_draft'):
        print(f"\nNew Price: {result6['listing_draft'].get('price')} TL")
    else:
        print(f"\nWARNING: No listing draft in result6")
        session_check = session_manager.get_session(user_id)
        if session_check and session_check.listing_draft:
            print(f"Price from session: {session_check.listing_draft.get('price')} TL")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED!")

if __name__ == "__main__":
    try:
        test_editing_without_api()
    except Exception as e:
        print(f"ERROR Test failed: {e}")
        import traceback
        traceback.print_exc()

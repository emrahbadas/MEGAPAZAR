"""
Test script for gathering info flow
"""
from models.conversation_state import session_manager, ConversationStage
from workflows.listing_flow_enhanced import create_enhanced_listing_workflow

def test_gathering_info():
    print("GATHERING INFO TEST")
    print("=" * 60)
    
    user_id = "test-user-gathering"
    workflow = create_enhanced_listing_workflow()
    print("OK Workflow initialized")
    
    # Test Case 1: Araba (critical info eksik)
    print("\n" + "=" * 60)
    print("TEST CASE 1: Araba satmak istiyorum (eksik bilgi)")
    print("=" * 60)
    
    state = {
        "user_id": user_id,
        "message": "Araba satmak istiyorum",
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
        "edit_value": "",
        "edit_description": "",
        "ai_response": ""
    }
    
    # Step 1: Initial message
    print("\nStep 1: User says 'Araba satmak istiyorum'")
    result1 = workflow.invoke(state)
    print(f"Agent: {result1['ai_response'][:200]}...")
    print(f"Response Type: {result1.get('response_type')}")
    
    session = session_manager.get_session(user_id)
    if session:
        print(f"Stage: {session.stage}")
        print(f"Missing fields: {session.missing_fields}")
    
    # Step 2: Answer first question
    if result1.get('response_type') == 'gathering_info':
        print("\nStep 2: User answers first question")
        state2 = {
            **result1,
            "message": "Mercedes"
        }
        result2 = workflow.invoke(state2)
        print(f"Agent: {result2['ai_response'][:200]}...")
        print(f"Response Type: {result2.get('response_type')}")
        
        session = session_manager.get_session(user_id)
        if session:
            print(f"Stage: {session.stage}")
            print(f"Missing fields: {session.missing_fields}")
            print(f"Product info: {session.product_info}")
        
        # Step 3: Answer second question
        if result2.get('response_type') == 'gathering_info':
            print("\nStep 3: User provides more details")
            state3 = {
                **result2,
                "message": "C180 2015 model 120bin km"
            }
            result3 = workflow.invoke(state3)
            print(f"Agent: {result3['ai_response'][:200]}...")
            print(f"Response Type: {result3.get('response_type')}")
            
            session = session_manager.get_session(user_id)
            if session:
                print(f"Stage: {session.stage}")
                print(f"Missing fields: {session.missing_fields}")
                print(f"Product info: {session.product_info}")
            
            # Should transition to listing flow now
            if result3.get('response_type') == 'start_listing_flow':
                print("\nOK Transitioned to listing flow!")
            elif result3.get('response_type') == 'listing_preview':
                print("\nOK Listing created!")
                if result3.get('listing_draft'):
                    draft = result3['listing_draft']
                    print(f"Title: {draft.get('title')}")
                    print(f"Price: {draft.get('price')} TL")
    
    # Test Case 2: Endüstriyel rotor (yeterli bilgi)
    print("\n" + "=" * 60)
    print("TEST CASE 2: Endüstriyel rotor (yeterli bilgi)")
    print("=" * 60)
    
    user_id2 = "test-user-rotor"
    state_rotor = {
        "user_id": user_id2,
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
        "edit_value": "",
        "edit_description": "",
        "ai_response": ""
    }
    
    print("\nStep 1: User says 'Endüstriyel rotor satmak istiyorum'")
    result_rotor = workflow.invoke(state_rotor)
    print(f"Agent: {result_rotor['ai_response'][:200]}...")
    print(f"Response Type: {result_rotor.get('response_type')}")
    
    session_rotor = session_manager.get_session(user_id2)
    if session_rotor:
        print(f"Stage: {session_rotor.stage}")
        print(f"Missing fields: {session_rotor.missing_fields}")
    
    # Should NOT ask for more info - endüstriyel rotor is specific enough
    if result_rotor.get('response_type') in ['listing_preview', 'start_listing_flow']:
        print("\nOK No gathering needed for endüstriyel rotor!")
    elif result_rotor.get('response_type') == 'gathering_info':
        print("\nINFO Gathering info requested (this might be correct depending on LLM decision)")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED!")

if __name__ == "__main__":
    try:
        test_gathering_info()
    except Exception as e:
        print(f"ERROR Test failed: {e}")
        import traceback
        traceback.print_exc()

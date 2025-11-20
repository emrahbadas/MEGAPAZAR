"""
Test session persistence
"""
from models.conversation_state import SessionManager, ConversationStage
import time
import os
import shutil

def test_session_persistence():
    print("SESSION PERSISTENCE TEST")
    print("=" * 60)
    
    # Test dizini temizle
    test_dir = "test_sessions"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # SessionManager oluştur
    manager = SessionManager(persist_dir=test_dir)
    print(f"OK SessionManager created with persist_dir: {test_dir}")
    
    # Test 1: Session oluştur ve kaydet
    print("\nTest 1: Create and save session")
    user_id = "test-user-123"
    session = manager.get_or_create_session(user_id)
    print(f"OK Session created: {session.session_id}")
    print(f"   Stage: {session.stage}")
    
    # Session'a veri ekle
    session.add_message("user", "Araba satmak istiyorum")
    session.set_stage(ConversationStage.GATHERING_INFO)
    session.update_product_info({"product_type": "Araba", "brand": "Mercedes"})
    manager.update_session(session)
    print(f"OK Session updated with data")
    print(f"   Stage: {session.stage}")
    print(f"   Product info: {session.product_info}")
    print(f"   Messages: {len(session.conversation_history)}")
    
    # Dosya oluştu mu kontrol et
    session_file = manager._get_session_file(user_id)
    print(f"\nChecking persistence...")
    print(f"   File exists: {session_file.exists()}")
    print(f"   File path: {session_file}")
    
    # Test 2: Manager'ı yeniden oluştur (simulating API restart)
    print("\nTest 2: Simulate API restart (new SessionManager)")
    manager2 = SessionManager(persist_dir=test_dir)
    print("OK New SessionManager created")
    
    # Session'ı yükle
    loaded_session = manager2.get_or_create_session(user_id)
    print(f"OK Session loaded from disk")
    print(f"   Session ID: {loaded_session.session_id}")
    print(f"   Stage: {loaded_session.stage}")
    print(f"   Product info: {loaded_session.product_info}")
    print(f"   Messages: {len(loaded_session.conversation_history)}")
    
    # Veriler korunmuş mu?
    assert loaded_session.stage == ConversationStage.GATHERING_INFO, "Stage mismatch!"
    assert loaded_session.product_info.get("brand") == "Mercedes", "Product info lost!"
    assert len(loaded_session.conversation_history) == 1, "Messages lost!"
    print("\nOK All data preserved after restart!")
    
    # Test 3: Update ve tekrar yükle
    print("\nTest 3: Update session and reload")
    loaded_session.add_message("assistant", "Mercedesin hangi modeli?")
    loaded_session.update_product_info({"model": "C180"})
    manager2.update_session(loaded_session)
    print("OK Session updated")
    
    # Yeni manager ile yükle
    manager3 = SessionManager(persist_dir=test_dir)
    session3 = manager3.get_or_create_session(user_id)
    print(f"OK Session reloaded")
    print(f"   Product info: {session3.product_info}")
    print(f"   Messages: {len(session3.conversation_history)}")
    
    assert session3.product_info.get("model") == "C180", "New data not persisted!"
    assert len(session3.conversation_history) == 2, "New message not persisted!"
    print("\nOK Updates persisted correctly!")
    
    # Test 4: Session silme
    print("\nTest 4: Delete session")
    manager3.delete_session(user_id)
    print("OK Session deleted")
    
    # Dosya silindi mi?
    print(f"   File exists after delete: {session_file.exists()}")
    assert not session_file.exists(), "File not deleted!"
    
    # Yeniden yüklemeye çalış
    manager4 = SessionManager(persist_dir=test_dir)
    new_session = manager4.get_or_create_session(user_id)
    print(f"OK New session created after delete")
    print(f"   Stage: {new_session.stage}")
    print(f"   Product info: {new_session.product_info}")
    
    assert new_session.stage == ConversationStage.INITIAL, "Not a fresh session!"
    assert new_session.product_info is None, "Old data still present!"
    print("\nOK Fresh session created!")
    
    # Test 5: Multiple users
    print("\nTest 5: Multiple users")
    manager5 = SessionManager(persist_dir=test_dir)
    
    user1 = "user-1"
    user2 = "user-2"
    user3 = "user-3"
    
    s1 = manager5.get_or_create_session(user1)
    s1.update_product_info({"product": "Laptop"})
    manager5.update_session(s1)
    
    s2 = manager5.get_or_create_session(user2)
    s2.update_product_info({"product": "Araba"})
    manager5.update_session(s2)
    
    s3 = manager5.get_or_create_session(user3)
    s3.update_product_info({"product": "Kanepe"})
    manager5.update_session(s3)
    
    print(f"OK Created 3 user sessions")
    
    # Dosya sayısı kontrol
    files = list(Path(test_dir).glob("session_*.pkl"))
    print(f"   Files on disk: {len(files)}")
    
    # Yeni manager ile tümünü yükle
    manager6 = SessionManager(persist_dir=test_dir)
    loaded1 = manager6.get_or_create_session(user1)
    loaded2 = manager6.get_or_create_session(user2)
    loaded3 = manager6.get_or_create_session(user3)
    
    print(f"OK All 3 sessions loaded")
    print(f"   User 1: {loaded1.product_info.get('product')}")
    print(f"   User 2: {loaded2.product_info.get('product')}")
    print(f"   User 3: {loaded3.product_info.get('product')}")
    
    assert loaded1.product_info.get('product') == "Laptop"
    assert loaded2.product_info.get('product') == "Araba"
    assert loaded3.product_info.get('product') == "Kanepe"
    print("\nOK All user data persisted correctly!")
    
    # Cleanup
    print("\nCleaning up test directory...")
    shutil.rmtree(test_dir)
    print("OK Test directory removed")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")

if __name__ == "__main__":
    try:
        from pathlib import Path
        test_session_persistence()
    except Exception as e:
        print(f"ERROR Test failed: {e}")
        import traceback
        traceback.print_exc()

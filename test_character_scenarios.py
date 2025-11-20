"""
🧪 KARAKTER BAZLI KONUŞMA TESTLERİ
ChatGPT'nin hazırladığı gerçek kullanıcı karakterleri ile test

Test Karakterleri:
1. Kararsız, çekingen kullanıcı
2. Agresif, aceleci kullanıcı
3. Çok konuşkan, konu dışına çıkan kullanıcı
4. Burnu havada, seçici müşteri
5. Aşırı bilgili, teknik detay düşkünü
6. Dolambaçlı konuşan kullanıcı
7. BONUS: Karmaşık, çok adımlı kullanıcı
"""

import requests
import time
import os

API_URL = "http://localhost:8000/conversation"

def clear_session(user_id: str):
    """Session'ı temizle"""
    try:
        response = requests.post(f"http://localhost:8000/debug/clear-session", params={"user_id": user_id})
        return response.status_code == 200
    except:
        return False

def test_conversation(character_name: str, user_id: str, messages: list):
    """Bir karakter için konuşma testi"""
    print("=" * 80)
    print(f"🎭 {character_name.upper()}")
    print("=" * 80)
    print()
    
    # Session temizle
    clear_session(user_id)
    time.sleep(0.5)
    
    for i, msg in enumerate(messages, 1):
        print(f"👤 Mesaj {i}: {msg}")
        
        try:
            response = requests.post(API_URL, json={
                "user_id": user_id,
                "message": msg
            })
            
            if response.status_code == 200:
                data = response.json()
                bot_msg = data.get('message', 'NO RESPONSE')
                intent = data.get('intent', 'unknown')
                response_type = data.get('response_type', 'none')
                
                print(f"🤖 Bot: {bot_msg}")
                print(f"   Intent: {intent} | Type: {response_type}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
        time.sleep(0.5)
    
    print("─" * 80)
    print()


# ==================== TEST SENARYOLARI ====================

# 🟩 1) Kararsız, çekingen, kendine güveni düşük kullanıcı
test_1_messages = [
    "Merhaba… Ben bir şey satmak istiyordum ama nasıl yapılıyor pek bilmiyorum… Zor mu acaba?",
    "Yani bir telefon satacağım ama önce fiyatlara bakmam lazım sanırım? Bilmiyorum doğru mu düşünüyorum.",
    "Modeli iPhone 12 sanırım, ama emin değilim… rengini de unuttum. Zaten fiyatını da bilemiyorum… zor mu olur?"
]

# 🟦 2) Agresif, aceleci, sabırsız kullanıcı
test_2_messages = [
    "Kardeşim hızlı ol. Telefon satacağım. Modeli sor falan uğraştırma, hemen ilan aç.",
    "Bak beni oyalama. iPhone 14 Pro satıyorum işte ne var? Fiyat 50 bin. Direkt ilanı oluştur.",
    "Ne demek daha bilgi lazım? Yaz işte fiyatını modelini koy gitsin."
]

# 🟧 3) Çok konuşkan, konu dışına çıkan kullanıcı
test_3_messages = [
    "Ayyy selam! Nasılsın? PazarGlobal nasıl gidiyor? İşler yolunda mı?",
    "Bu arada ben geçen gün marketten elma alırken kasiyer ne kadar pahalı dedi… neyse konudan saptım.",
    "Ben bir laptop satacaktım ama önce sorayım dedim nasıl satılıyor burada?",
    "Benimki Lenovo'ydu galiba… yok yok Asus muydu… unuttum yine…"
]

# 🟨 4) Burnu havada, çok seçici müşteri
test_4_messages = [
    "Burada premium cihazlar için ayrı bir kategori var mı? Kaliteli ürünlerimi ucuz cihazlarla yan yana koymak istemiyorum.",
    "Ben iPhone 15 Pro Max 1TB satacağım. Kutulu. Çok temiz. 90.000 çok mu düşük kaç yazılır?",
    "Açıklama metnini estetik yaz. Sıradan ilan istemiyorum."
]

# 🟪 5) Aşırı bilgili, teknik detay düşkünü kullanıcı
test_5_messages = [
    "Bir adet Samsung S23 Ultra satıyorum. Snapdragon 8 Gen 2 işlemcili olan model. 12GB RAM, 512GB depolama.",
    "Ekran hafif çizik ama AMOLED olduğundan fark edilmiyor. Kamera 200MP sensörlü.",
    "Bunları teknik olarak doğru şekilde yazabilir misin? Ayrıca fiyat analizi istiyorum: 53.000 mantıklı mı?"
]

# 🟫 6) Dolambaçlı konuşan, direkt söylemeyen kullanıcı
test_6_messages = [
    "Hani geçen bahsettiğim o eşyayı var ya… işte ondan kurtulmak istiyorum sanırım.",
    "Yani satabilirim… aslında belki takas da ederim… bilmiyorum.",
    "Telefon işte… modeli falan karışık. Ama bende durması anlamsız.",
    "Ne kadar eder acaba? Ona göre karar vereceğim…"
]

# 🟧 BONUS: Karmaşık, kararsız, çok adımlı kullanıcı
test_bonus_messages = [
    "Selam ya… şey bir ürün satmak istiyordum ama tam emin değilim, yani satayım mı satmayayım mı bilmiyorum. Bir de önce fiyatlara falan bakmam lazım sanırım.",
    "Telefon satmayı düşünüyordum aslında ama modelini nasıl yazmam gerekiyor onu da bilmiyorum, iPhone 14 müydü yoksa 13 Pro muydu karıştırıyorum. Kutusu falan var ama tam açılmış mıydı hatırlamıyorum.",
    "Gerçi belki önce fiyat öğrenmem lazım… 32.000 çok mu az çok mu fazla bilmiyorum, piyasayı da takip etmiyorum. Acaba sen ilan oluşturmadan önce bana yardımcı olur musun?",
    "Yani şöyle bir şey: iPhone 13 Pro olabilir, maviydi sanırım, kutusu duruyor ama içinden kulaklık çıkmamıştı zaten. Temiz kullanılmıştı ama bir kere ekran değişmiş olabilir emin değilim. Buna kaç yazılır ki?",
    "Neyse, ilan oluştur oradan devam edelim istersen… Ama açıklama falan nasıl yazılıyor bilmiyorum, sen düzenleyebilir misin? Uğraştırmasın beni."
]


if __name__ == "__main__":
    import sys
    import io
    
    # Fix encoding for Windows console
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("\n")
    print("=" * 80)
    print("KARAKTER BAZLI KONUSMA TESTLERI BASLIYOR")
    print("=" * 80)
    print("\n")
    
    # Test 1: Kararsız kullanıcı
    test_conversation(
        "Test 1: Kararsız, Çekingen Kullanıcı",
        "test_user_001",
        test_1_messages
    )
    
    # Test 2: Agresif kullanıcı
    test_conversation(
        "Test 2: Agresif, Aceleci Kullanıcı",
        "test_user_002",
        test_2_messages
    )
    
    # Test 3: Konuşkan kullanıcı
    test_conversation(
        "Test 3: Çok Konuşkan, Konu Dışına Çıkan",
        "test_user_003",
        test_3_messages
    )
    
    # Test 4: Seçici müşteri
    test_conversation(
        "Test 4: Burnu Havada, Seçici Müşteri",
        "test_user_004",
        test_4_messages
    )
    
    # Test 5: Teknik kullanıcı
    test_conversation(
        "Test 5: Aşırı Bilgili, Teknik Detay Düşkünü",
        "test_user_005",
        test_5_messages
    )
    
    # Test 6: Dolambaçlı kullanıcı
    test_conversation(
        "Test 6: Dolambaçlı Konuşan, Direkt Söylemeyen",
        "test_user_006",
        test_6_messages
    )
    
    # Test Bonus: Karmaşık kullanıcı
    test_conversation(
        "BONUS: Karmaşık, Kararsız, Çok Adımlı",
        "test_user_bonus",
        test_bonus_messages
    )
    
    print("=" * 80)
    print("TAMAMLANDI - TUM KARAKTER TESTLERI BITTI!")
    print("=" * 80)

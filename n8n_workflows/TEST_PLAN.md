# MEGAPAZAR WhatsApp Integration - Test Plan

## Test Ortamı

### Gereksinimler
- [x] n8n çalışır durumda (http://localhost:5678)
- [x] Backend API aktif (http://localhost:8000)
- [x] Twilio WhatsApp Sandbox kurulu
- [x] ngrok ile n8n expose edilmiş
- [x] Test kullanıcı hesabı (phone: +905551234567)

### Test Kullanıcıları

| Rol | Telefon | user_id |
|-----|---------|---------|
| Alıcı 1 | +905551234567 | buyer-1 |
| Satıcı 1 | +905559876543 | seller-1 |
| Test Admin | +905550000000 | admin-test |

---

## 1️⃣ Temel İletişim Testleri

### Test 1.1: Welcome Message
**Amaç**: Bot'un ilk karşılama mesajını test et

```
User → Bot: Merhaba

Beklenen Cevap:
🎉 Hoş geldin MEGAPAZAR'a!
Ben senin AI asistanınım...
```

**Başarı Kriterleri**:
- [x] Mesaj geldi
- [x] Format doğru (emoji + metin)
- [x] Komutlar listelenmiş

**n8n Workflow**: `megapazar_main_router` → `Send Welcome Message` node

---

### Test 1.2: Help Menu
**Amaç**: Yardım menüsünü göster

```
User → Bot: yardım

Beklenen:
📚 MEGAPAZAR Yardım Menüsü
...
```

**Başarı Kriterleri**:
- [x] Yardım menüsü gösterildi
- [x] Tüm komutlar listelendi

---

### Test 1.3: Unknown Command
**Amaç**: Bilinmeyen komut nasıl handle ediliyor

```
User → Bot: asdfghjkl

Beklenen:
❌ Üzgünüm, ne demek istediğini anlayamadım.
"yardım" yazarak komutları görebilirsin.
```

**Başarı Kriterleri**:
- [x] Hata mesajı net
- [x] Yardım önerisi var

---

## 2️⃣ İlan Verme Akışı (Listing Flow)

### Test 2.1: Basit İlan (Text Only)
**Amaç**: Kullanıcı sadece metin ile ilan verebilsin

```
User: ilan vermek istiyorum
Bot: Harika! Hangi ürünü satmak istiyorsun?

User: rotor
Bot: Anladım, rotor. Kaç TL'ye satıyorsun?

User: 150
Bot: Ürünün durumu nedir? (yeni/ikinci el/hasarlı)

User: ikinci el
Bot: Nerede bulunuyor ürün?

User: Istanbul Kadıköy
Bot: Açıklama eklemek ister misin? (veya "geçir" yaz)

User: çalışır durumda
Bot: Fotoğraf gönderebilir misin? (veya "fotoğraf yok" yaz)

User: fotoğraf yok
Bot: ✅ İlan başarıyla yayınlandı!
     İlan ID: [id]
```

**Başarı Kriterleri**:
- [x] Tüm adımlar tamamlandı
- [x] İlan DB'ye kaydedildi (status: active)
- [x] n8n execution başarılı
- [x] Backend `/conversation` endpoint çağrıldı

**Verification**:
```sql
SELECT * FROM listings WHERE user_id = 'buyer-1' ORDER BY created_at DESC LIMIT 1;
```

---

### Test 2.2: İlan + Fotoğraf
**Amaç**: Kullanıcı fotoğraf gönderebilsin

```
User: rotor satmak istiyorum 150 TL
Bot: Harika! Ürünün durumu nedir?

User: [fotoğraf gönderir]
Bot: Fotoğraf işleniyor...
Bot: Gördüm! İkinci el görünüyor. Nerede bulunuyor?

User: Kadıköy
Bot: ✅ İlan yayınlandı!
```

**Başarı Kriterleri**:
- [x] Fotoğraf Twilio'dan indirildi
- [x] Base64 encode edildi
- [x] Vision Agent analiz etti
- [x] Supabase Storage'a yüklendi
- [x] image_url DB'ye kaydedildi

**Verification**:
```sql
SELECT image_url FROM listings WHERE user_id = 'buyer-1' ORDER BY created_at DESC LIMIT 1;
```

---

### Test 2.3: Hatalı Fiyat
**Amaç**: Geçersiz fiyat girilirse düzeltsin

```
User: ilan vermek istiyorum
Bot: Hangi ürünü satmak istiyorsun?

User: rotor 0 TL
Bot: Geçersiz fiyat. Lütfen 1 TL veya üzeri bir fiyat gir.
```

**Başarı Kriterleri**:
- [x] Fiyat validasyonu çalışıyor
- [x] Kullanıcıya açık hata mesajı

---

## 3️⃣ Arama Akışı (Search Flow)

### Test 3.1: Basit Arama
**Amaç**: Kullanıcı ürün arayabilsin

```
User: rotor arıyorum

Beklenen:
🔍 "rotor" için 3 sonuç buldum:

*1. Rotor*
💰 150 TL
📍 Istanbul Kadıköy
🔧 İkinci el
✅ %85 eşleşme

*2. Rotor Kompresör*
💰 200 TL
...
```

**Başarı Kriterleri**:
- [x] Backend `/search` endpoint çağrıldı
- [x] Vector search çalıştı (similarity threshold: 0.3)
- [x] Sonuçlar formatlandı
- [x] En az 1 sonuç döndü

**Verification**:
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"user_id": "buyer-1", "query": "rotor", "limit": 5}'
```

---

### Test 3.2: Sonuç Bulunamadı
**Amaç**: Sonuç yoksa net mesaj

```
User: zxcvbnm arıyorum

Beklenen:
❌ Üzgünüm, "zxcvbnm" için sonuç bulunamadı.
Başka bir arama yapmak ister misin?
```

**Başarı Kriterleri**:
- [x] Empty results handle edildi
- [x] Mesaj net

---

### Test 3.3: Fiyat Filtreli Arama
**Amaç**: "100 TL'ye kadar rotor" şeklinde arama

```
User: 100 TL'ye kadar rotor arıyorum

Beklenen:
🔍 "rotor" için 2 sonuç buldum (100 TL altı):
...
```

**Başarı Kriterleri**:
- [x] Query'den fiyat parse edildi
- [x] Backend'e `max_price` parametresi gönderildi
- [x] Sadece 100 TL altı sonuçlar döndü

---

## 4️⃣ Sipariş Akışı (Order Flow)

### Test 4.1: Basit Sipariş
**Amaç**: Kullanıcı arama sonucundan sipariş versin

```
# Önce arama yap
User: rotor arıyorum
Bot: [3 sonuç gösterir]

# Sipariş ver
User: 1 numaralı ilana sipariş vermek istiyorum

Beklenen:
✅ Siparişin başarıyla oluşturuldu!

📦 Ürün: Rotor
💰 Fiyat: 150 TL
📊 Adet: 1
💵 Toplam: 150 TL

🆔 Sipariş No: [order-id]
```

**Başarı Kriterleri**:
- [x] Backend `/orders` endpoint çağrıldı
- [x] Order DB'ye kaydedildi
- [x] Commission hesaplandı (2.5%)
- [x] Alıcıya onay mesajı gönderildi
- [x] Satıcıya bildirim gönderildi

**Verification**:
```sql
SELECT * FROM orders WHERE buyer_user_id = 'buyer-1' ORDER BY created_at DESC LIMIT 1;
```

---

### Test 4.2: Satıcıya Bildirim
**Amaç**: Satıcı sipariş bildirimini alsın

```
Satıcıya giden mesaj:
🔔 Yeni Sipariş Geldi!

📦 İlan: Rotor
💰 Fiyat: 150 TL
📊 Adet: 1
💵 Toplam: 150 TL

👤 Alıcı: +905551234567
🆔 Sipariş No: [order-id]

✅ Siparişi onaylamak için: "[order-id] onaylıyorum"
❌ Reddetmek için: "[order-id] reddediyorum"
```

**Başarı Kriterleri**:
- [x] Twilio Send Message node çalıştı
- [x] Satıcının telefon numarasına mesaj gitti
- [x] Onay/red butonları var

---

### Test 4.3: Sipariş Onaylama
**Amaç**: Satıcı siparişi onaylasın

```
Satıcı: [order-id] onaylıyorum

Satıcıya:
✅ Sipariş onaylandı! Alıcı bilgilendirildi.

Alıcıya:
🎉 Siparişin onaylandı!
Satıcı: +905559876543
İletişime geç ve ödeme yap.
```

**Başarı Kriterleri**:
- [x] Order status: confirmed
- [x] Her iki tarafa bildirim gitti

---

## 5️⃣ Edge Cases & Error Handling

### Test 5.1: Backend Down
**Amaç**: Backend çalışmazsa ne olur?

```
User: ilan vermek istiyorum

Beklenen:
❌ Şu an teknik sorun var. Lütfen biraz sonra tekrar dene.
```

**Nasıl Test Edilir**:
1. Backend'i durdur: `Ctrl+C`
2. WhatsApp'tan mesaj gönder
3. n8n error handling devreye girmeli

---

### Test 5.2: Rate Limiting
**Amaç**: Aynı kullanıcı 10 mesaj/dakika gönderirse

```
User: [10+ mesaj hızlıca gönderir]

Beklenen:
⚠️ Çok hızlı mesaj gönderiyorsun. 1 dakika bekle.
```

**Başarı Kriterleri**:
- [x] n8n'de rate limit node eklenmeli
- [x] Redis/Memory cache kullan

---

### Test 5.3: Session Timeout
**Amaç**: 24 saat sonra session expire olur

```
# 24 saat önce başladı
User: ilan vermek istiyorum
Bot: Hangi ürünü?

# 24 saat sonra
User: rotor

Beklenen:
⏰ Session süresi doldu. Tekrar başlayalım.
İlan vermek için "ilan ver" yaz.
```

**Başarı Kriterleri**:
- [x] Backend session cleanup çalışıyor
- [x] Expired session handle edildi

---

## 6️⃣ Performance Tests

### Test 6.1: Response Time
**Amaç**: Bot ne kadar hızlı cevap veriyor?

| İşlem | Hedef | Gerçek |
|-------|-------|--------|
| Welcome message | <500ms | ? |
| Conversation endpoint | <1s | ? |
| Search endpoint | <2s | ? |
| Order creation | <1s | ? |
| Media upload | <3s | ? |

**Nasıl Ölçülür**:
- n8n execution time
- Backend logs (`uvicorn` output)

---

### Test 6.2: Concurrent Users
**Amaç**: 10 kullanıcı aynı anda mesaj gönderirse?

**Test Senaryosu**:
1. 10 farklı WhatsApp numarası (veya test script)
2. Hepsi aynı anda "merhaba" gönderir
3. n8n ve Backend handle edebiliyor mu?

**Başarı Kriterleri**:
- [x] Hiçbir mesaj kaybolmadı
- [x] Response time <2s
- [x] Backend crash olmadı

---

## 7️⃣ Production Checklist

### Before Go-Live

- [ ] **Twilio Production Number**: Sandbox'tan çık, gerçek numara al
- [ ] **ngrok → Production Domain**: ngrok yerine gerçek domain kullan
- [ ] **n8n Production Mode**: Docker prod ortamında çalıştır
- [ ] **Rate Limiting**: n8n'de rate limit node ekle
- [ ] **Monitoring**: n8n + Backend logları izle (Sentry/DataDog)
- [ ] **Backup Workflow**: n8n workflow'ları GitHub'a push
- [ ] **Error Alerting**: Hata olursa Slack/Email bildirimi
- [ ] **Load Testing**: 100+ concurrent user test et

---

## Test Sonuçları

| Test | Durum | Tarih | Notlar |
|------|-------|-------|--------|
| 1.1 Welcome | ❌ | - | Henüz test edilmedi |
| 1.2 Help | ❌ | - | - |
| 2.1 Listing | ❌ | - | - |
| 2.2 Photo | ❌ | - | - |
| 3.1 Search | ❌ | - | - |
| 4.1 Order | ❌ | - | - |

**Legend**:
- ✅ Passed
- ❌ Not Tested
- ⚠️ Partial
- 🔴 Failed

---

## Çalıştırma

```bash
# Backend başlat
cd megapazar-agent-api
uvicorn main:app --reload

# n8n başlat
docker start n8n

# ngrok başlat
ngrok http 5678

# Testlere başla!
```

---

**Tester**: Emrah  
**Tarih**: 2025-01-17  
**Versiyon**: v1.0 - WhatsApp Integration

# MEGAPAZAR WhatsApp - Listing Flow

Bu workflow, kullanıcıların WhatsApp üzerinden ilan vermesini sağlar.

## Akış

1. Kullanıcı "ilan vermek istiyorum" der
2. Backend API `/conversation` endpoint'i ile konuşma başlar
3. Agent sırayla bilgi toplar:
   - Ürün adı
   - Fiyat
   - Durum (yeni/ikinci el)
   - Konum
   - Fotoğraf (opsiyonel)
4. Tüm bilgiler toplandığında ilan yayınlanır

## Session Yönetimi

- Her kullanıcı için telefon numarasına göre session oluşturulur
- Session backend'de saklanır
- 24 saat inaktivite sonrası expire olur

## Media Upload

WhatsApp'tan gelen fotoğraflar:
1. Twilio'dan `MediaUrl` ile alınır
2. n8n ile download edilir
3. Base64'e encode edilir
4. Backend API'ye `/conversation` ile gönderilir
5. Vision agent analiz eder
6. Supabase Storage'a yüklenir

## Örnek Diyalog

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
Bot: Harika! Ürünün bir fotoğrafını gönderebilir misin? 
     (veya "fotoğraf yok" yaz)

User: [fotoğraf gönderir]
Bot: ✅ İlan başarıyla yayınlandı!
     
     📦 Rotor
     💰 150 TL
     📍 Istanbul Kadıköy
     🔧 İkinci el
     
     İlan ID: abc-123
     Link: [ilan detay URL]
```

## Hata Durumları

- Geçersiz fiyat (0 TL, negatif) → "Lütfen geçerli bir fiyat gir"
- Fotoğraf upload hatası → "Fotoğraf yüklenemedi, tekrar dene"
- Backend API down → "Şu an teknik sorun var, lütfen biraz sonra dene"

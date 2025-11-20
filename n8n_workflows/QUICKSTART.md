# n8n WhatsApp Integration - Quick Start

## 📦 Hazır Dosyalar

✅ **3 ana workflow** oluşturuldu:
- `megapazar_main_router.json` - Ana mesaj yöneticisi
- `megapazar_search_flow.json` - Ürün arama
- `megapazar_order_flow.json` - Sipariş yönetimi

✅ **Dokümantasyon**:
- `README.md` - Genel bakış
- `SETUP_GUIDE.md` - Detaylı kurulum
- `LISTING_FLOW.md` - İlan verme akışı

## 🚀 5 Dakikada Kurulum

### 1. n8n Başlat

```bash
docker run -d --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

Aç: http://localhost:5678

### 2. Twilio Hesabı

1. https://www.twilio.com/try-twilio
2. WhatsApp Sandbox aktif et
3. Account SID ve Auth Token kopyala

### 3. Workflow'ları İçe Aktar

n8n'de:
1. **Import from File** → `megapazar_main_router.json`
2. Credentials → **Twilio** ekle (SID + Token)
3. Workflow'u **Active** yap

### 4. ngrok ile Expose Et

```bash
ngrok http 5678
```

Çıkan URL'yi Twilio webhook'a yaz:
```
https://abc123.ngrok.io/webhook/whatsapp-webhook
```

### 5. Test Et!

WhatsApp'tan Twilio sandbox'a:
```
Merhaba
```

Bot cevap verirse ✅ **BAŞARILI!**

## 📱 Kullanım Örnekleri

### İlan Verme
```
User: ilan vermek istiyorum
Bot: Harika! Hangi ürünü satmak istiyorsun?
User: rotor 150 TL
Bot: Ürünün durumu nedir?
User: ikinci el
Bot: ✅ İlan yayınlandı!
```

### Arama
```
User: rotor arıyorum
Bot: 🔍 3 sonuç buldum:
     1. Rotor - 150 TL - Kadıköy
     2. Rotor Kompresör - 200 TL - Beşiktaş
     ...
```

### Sipariş
```
User: 1 numaralı ilana sipariş vermek istiyorum
Bot: ✅ Siparişin oluşturuldu!
     Satıcıya bildirim gönderildi.
```

## 🔧 Backend Entegrasyonu

Main router, şu endpoint'leri kullanıyor:

```bash
POST http://localhost:8000/conversation  # İlan verme
POST http://localhost:8000/search        # Arama
POST http://localhost:8000/orders        # Sipariş
```

Backend çalıştır:
```bash
cd megapazar-agent-api
uvicorn main:app --reload
```

## 🎯 Sonraki Adımlar

- [ ] Media upload (fotoğraf yükleme)
- [ ] My listings (kullanıcının ilanları)
- [ ] Notifications (fiyat değişiklikleri)
- [ ] Production deployment (Heroku/Railway)

## 📚 Daha Fazla Bilgi

Detaylı kurulum için: [SETUP_GUIDE.md](./SETUP_GUIDE.md)

## 🆘 Sorun mu Var?

**"Webhook not found"** → Workflow aktif mi? ngrok URL doğru mu?  
**"Backend bağlanamadı"** → `uvicorn main:app --reload` çalıştır  
**"Mesaj gelmiyor"** → Twilio webhook URL'yi kontrol et

---

Hazır! 🎉 Artık WhatsApp'tan MEGAPAZAR kullanabilirsin!

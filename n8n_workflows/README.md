# n8n WhatsApp Integration

Bu klasör, MEGAPAZAR'ın WhatsApp Business API entegrasyonu için n8n workflow'larını içerir.

## 🎯 Amaç

Kullanıcıların WhatsApp üzerinden:
- İlan vermesini
- Ürün aramasını
- Sipariş vermesini
- Bildirim almasını sağlamak

## 📋 Önkoşullar

### 1. n8n Kurulumu

```bash
# Docker ile (önerilen)
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# veya npm ile
npm install n8n -g
n8n start
```

### 2. WhatsApp Business API

Aşağıdaki sağlayıcılardan birini seçin:

#### Option A: Twilio (En popüler)
- https://www.twilio.com/whatsapp
- Hemen başlayabilirsiniz (test numarası ücretsiz)
- Account SID ve Auth Token alın
- WhatsApp Sandbox numarasını aktif edin

#### Option B: 360Dialog (Daha ucuz, ölçeklendirme için)
- https://www.360dialog.com/
- API key alın
- Resmi WhatsApp Business API erişimi

#### Option C: Meta (Cloud API)
- https://developers.facebook.com/docs/whatsapp/cloud-api
- Ücretsiz 1000 mesaj/ay
- Daha karmaşık setup

## 🏗️ Workflow Yapısı

### 1. Main Router (megapazar_main_router.json)
- Tüm WhatsApp mesajlarını karşılar
- Kullanıcı intent'ini belirler
- İlgili sub-workflow'a yönlendirir

### 2. Listing Flow (megapazar_listing_flow.json)
- İlan verme sürecini yönetir
- `/conversation` endpoint'i ile konuşur
- Görselleri işler ve yükler

### 3. Search Flow (megapazar_search_flow.json)
- Ürün aramalarını yönetir
- `/search` endpoint'ini kullanır
- Sonuçları formatlayıp gönderir

### 4. Order Flow (megapazar_order_flow.json)
- Sipariş işlemlerini yönetir
- `/orders` endpoint'i ile çalışır

### 5. Notification Handler (megapazar_notifications.json)
- Background job'lardan gelen bildirimleri iletir
- Fiyat değişikliği, sipariş güncellemesi vb.

## 🚀 Kurulum Adımları

### Adım 1: n8n Credentials Ekle

n8n'de şu credential'ları ekleyin:

1. **Twilio** (WhatsApp için)
   - Name: `Twilio WhatsApp Prod`
   - Account SID: `ACxxxxx`
   - Auth Token: `xxxxx`

2. **HTTP Request Auth** (Backend API için)
   - Name: `MEGAPAZAR API`
   - Auth Type: `None` (şimdilik)
   - Base URL: `http://localhost:8000`

### Adım 2: Workflow'ları İçe Aktar

1. n8n arayüzünde `Import from File` seçin
2. Her JSON dosyasını sırayla içe aktarın
3. Credential'ları bağlayın

### Adım 3: Webhook URL'lerini Kaydet

1. `megapazar_main_router` workflow'unu aktif edin
2. Webhook node'una tıklayın
3. Production URL'yi kopyalayın
4. Twilio Console'da bu URL'yi `Messaging Webhook URL` olarak ayarlayın

### Adım 4: Test Et

WhatsApp'tan test numaranıza şu mesajı gönderin:
```
join [sandbox-code]
```

Ardından:
```
Merhaba
```

Bot size karşılama mesajı göndermelidir.

## 📱 Kullanıcı Komutları

| Komut | Açıklama |
|-------|----------|
| `ilan ver`, `satmak istiyorum` | İlan verme başlatır |
| `ara`, `arıyorum`, `[ürün adı]` | Ürün arama yapar |
| `ilanlarım`, `listem` | Kullanıcının ilanlarını listeler |
| `siparişlerim` | Siparişleri gösterir |
| `yardım`, `help` | Yardım menüsünü gösterir |

## 🔧 Yapılandırma

### Ortam Değişkenleri

`.env` dosyanıza ekleyin:

```env
# n8n
N8N_HOST=0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=https
N8N_WEBHOOK_URL=https://your-domain.com

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Backend API
BACKEND_API_URL=http://localhost:8000
BACKEND_API_KEY=optional-if-auth-enabled
```

## 🧪 Test Senaryoları

### Senaryo 1: İlan Verme
1. WhatsApp: `ilan vermek istiyorum`
2. Bot: `Harika! Hangi ürünü satmak istiyorsun?`
3. Kullanıcı: `rotor 150 tl`
4. Bot: `Ürünün fotoğrafını gönderir misin?`
5. Kullanıcı: [Fotoğraf gönderir]
6. Bot: `İlan yayında! ID: [listing_id]`

### Senaryo 2: Ürün Arama
1. WhatsApp: `rotor arıyorum`
2. Bot: [3 sonuç gösterir]
3. Kullanıcı: `1 numaralı ilana sipariş vermek istiyorum`
4. Bot: `Sipariş oluşturuldu! Satıcı ile iletişime geçildi.`

### Senaryo 3: Bildirim
1. Backend price monitoring job çalışır
2. Fiyat düşüşü tespit edilir
3. n8n notification handler tetiklenir
4. Kullanıcıya WhatsApp bildirimi gider

## 📊 Metrikler

n8n üzerinden izlenebilecek metrikler:
- Günlük mesaj sayısı
- Başarılı/başarısız workflow çalıştırmaları
- Ortalama yanıt süresi
- En çok kullanılan komutlar

## 🔒 Güvenlik

- [ ] Webhook'lara rate limiting ekle
- [ ] User authentication (telefon no. doğrulama)
- [ ] Sensitive data loglama
- [ ] n8n'i production mode'da çalıştır
- [ ] HTTPS kullan (Let's Encrypt)

## 🚧 Bilinen Sorunlar

1. **Media Upload Delays**: WhatsApp'tan gelen görseller bazen geç işlenir
2. **Session Timeout**: 24 saat sonra session expire oluyor, yeni konuşma başlatılmalı
3. **Rate Limits**: Twilio Sandbox'ta günlük mesaj limiti var

## 📚 Referanslar

- [n8n Documentation](https://docs.n8n.io/)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [MEGAPAZAR Backend API](../README.md)

## 🆘 Sorun Giderme

### "Webhook not found" hatası
- Workflow'un aktif olduğundan emin olun
- Production webhook URL'yi kontrol edin

### "401 Unauthorized" hatası (Backend API)
- `BACKEND_API_URL` doğru mu?
- API çalışıyor mu? (`uvicorn main:app --reload`)

### Mesajlar gelmiyor
- Twilio Console'da webhook URL'yi kontrol edin
- n8n loglarına bakın (`Executions` tab)
- WhatsApp Sandbox'a join olduğunuzdan emin olun

## 📞 Destek

Sorularınız için:
- GitHub Issues: https://github.com/emrahbadas/MEGAPAZAR/issues
- E-posta: support@megapazar.com (placeholder)

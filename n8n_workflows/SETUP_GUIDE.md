# n8n Kurulum Rehberi - MEGAPAZAR WhatsApp Entegrasyonu

## 🎯 Bu Rehber Neyi Anlatıyor?

Bu dokümanda:
1. n8n'i nasıl kuracağınızı
2. WhatsApp Business API'yi nasıl bağlayacağınızı
3. İlk workflow'u nasıl test edeceğinizi öğreneceksiniz

**Süre**: ~30 dakika  
**Zorluk**: Orta

---

## 📋 Gereksinimler

- [ ] Docker Desktop yüklü (veya Node.js 18+)
- [ ] Twilio hesabı (ücretsiz başlangıç)
- [ ] Backend API çalışır durumda (`uvicorn main:app --reload`)

---

## 1️⃣ n8n Kurulumu

### Seçenek A: Docker ile (Önerilen)

```bash
# n8n'i Docker ile başlat
docker run -d --restart=always \
  --name n8n \
  -p 5678:5678 \
  -e N8N_HOST=0.0.0.0 \
  -e N8N_PORT=5678 \
  -e N8N_PROTOCOL=http \
  -e WEBHOOK_URL=http://localhost:5678/ \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Çalıştığını kontrol et
docker ps | grep n8n
```

**Tarayıcıda aç**: http://localhost:5678

### Seçenek B: npm ile

```bash
# n8n'i global olarak kur
npm install n8n -g

# Başlat
n8n start
```

### İlk Kurulum

1. Tarayıcıda http://localhost:5678 aç
2. Email ve şifre belirle (admin hesabı)
3. "Get started" tıkla

---

## 2️⃣ Twilio WhatsApp Sandbox Kurulumu

### Adım 1: Twilio Hesabı Oluştur

1. https://www.twilio.com/try-twilio adresine git
2. Ücretsiz hesap oluştur (kredi kartı gerekmez)
3. Telefon numaranı doğrula

### Adım 2: WhatsApp Sandbox'ı Aktif Et

1. Twilio Console'da sol menüden **Messaging** → **Try it out** → **Send a WhatsApp message**
2. **Sandbox numaranı** kopyala (örn: `+1 415 523 8886`)
3. **Join code'u** kopyala (örn: `join remove-pride`)

### Adım 3: Sandbox'a Katıl

1. Kendi WhatsApp uygulamanı aç
2. Twilio'nun sandbox numarasına mesaj gönder: `join [your-code]`
3. Onay mesajı gelecek: "You are all set!"

### Adım 4: Webhook URL Ayarla

1. Twilio Console → **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
2. "When a message comes in" bölümünde şimdilik boş bırak (n8n webhook'u oluşturduktan sonra dolduracağız)

---

## 3️⃣ n8n Credentials Ekleme

### Twilio Credential Ekle

1. n8n'de sağ üst köşeden **Settings** → **Credentials**
2. **"New"** → **"Twilio"** seç
3. Şu bilgileri doldur:
   - **Credential Name**: `Twilio WhatsApp Prod`
   - **Account SID**: Twilio Console'da bulabilirsin (AC ile başlar)
   - **Auth Token**: Twilio Console'da "Show" butonuna tıkla
4. **Save** tıkla

#### Twilio SID ve Token'ı Nerede Bulabilirim?

1. Twilio Console ana sayfasında sağ tarafta **"Account Info"** paneli var
2. **Account SID**: `ACxxxxxxxxxxxxx`
3. **Auth Token**: Gizli, "Show" butonuna tıkla

---

## 4️⃣ İlk Workflow'u Import Et

### Adım 1: Workflow Dosyasını İndir

Workflow dosyası: `n8n_workflows/megapazar_main_router.json`

### Adım 2: n8n'e Import Et

1. n8n ana sayfasında sağ üst **"Import from File"** butonuna tıkla
2. `megapazar_main_router.json` dosyasını seç
3. Workflow açılacak

### Adım 3: Webhook URL'yi Al

1. **"WhatsApp Webhook"** node'una çift tıkla
2. **"Production URL"** kısmını kopyala
   - Örnek: `http://localhost:5678/webhook/whatsapp-webhook`
3. Bu URL'yi şimdilik bir yere kaydet

### Adım 4: Workflow'u Aktif Et

1. Sağ üst köşede **"Inactive"** yazısına tıkla → **"Active"** yap
2. Workflow artık çalışıyor! 🎉

---

## 5️⃣ Twilio'yu n8n Webhook'una Bağla

### Local Test için ngrok Kullan

⚠️ **Önemli**: Twilio, `localhost` URL'lerini kabul etmez. Local test için **ngrok** kullanmalısın.

```bash
# ngrok kur (yoksa)
# Windows: choco install ngrok
# Mac: brew install ngrok

# ngrok ile n8n'i internete aç
ngrok http 5678
```

**Çıktıda göreceksin**:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:5678
```

Bu `https://abc123.ngrok.io` URL'ini kullanacağız!

### Twilio Webhook Ayarla

1. Twilio Console → **Messaging** → **WhatsApp Sandbox Settings**
2. **"When a message comes in"** bölümüne şunu yaz:
   ```
   https://abc123.ngrok.io/webhook/whatsapp-webhook
   ```
3. **Save** tıkla

---

## 6️⃣ İlk Test! 🚀

### Test Mesajı Gönder

WhatsApp'tan Twilio sandbox numarasına şunu yaz:

```
Merhaba
```

**Beklenen Cevap**:

```
🎉 Hoş geldin MEGAPAZAR'a!

Ben senin AI asistanınım. Şunları yapabilirim:

📦 İlan Ver - "ilan vermek istiyorum"
🔍 Ürün Ara - "rotor arıyorum"
📋 İlanlarım - "ilanlarımı göster"
📊 Siparişlerim - "siparişlerimi göster"
❓ Yardım - "yardım"

Hemen başlamak için yukarıdaki komutlardan birini yazabilirsin!
```

### n8n'de Execution'ları Kontrol Et

1. n8n'de sol menüden **"Executions"** tıkla
2. Son çalıştırmayı göreceksin (yeşil ✅ = başarılı)
3. Tıklayıp detayları incele

---

## 7️⃣ Backend API'yi Bağla

### Backend'in Çalıştığından Emin Ol

```bash
cd "C:\Users\emrah badas\OneDrive\Desktop\mega pzar\megapazar-agent-api"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Tarayıcıda test et: http://localhost:8000/docs

### n8n Workflow'unda API URL'yi Güncelle

1. `megapazar_main_router` workflow'unda **"Call Backend API - Conversation"** node'una çift tıkla
2. **URL** kısmını kontrol et: `http://host.docker.internal:8000/conversation`
   - Docker kullanıyorsan: `http://host.docker.internal:8000`
   - npm kullanıyorsan: `http://localhost:8000`
3. **Save** tıkla

---

## 8️⃣ End-to-End Test

### Senaryo: Konuşma API'yi Test Et

1. WhatsApp'tan Twilio'ya yaz:
   ```
   Rotor satmak istiyorum
   ```

2. n8n, mesajı Backend API'ye gönderecek

3. Backend'den gelen cevap WhatsApp'a iletilecek:
   ```
   Harika! Rotor satmak istiyorsun. 
   Kaç TL'ye satmak istersin?
   ```

4. Cevap ver:
   ```
   150 TL
   ```

5. Backend devam edecek...

### Logs Nasıl Kontrol Edilir?

**n8n Logs**:
```bash
docker logs n8n -f
```

**Backend Logs**:
Terminal'de `uvicorn` çalıştırdığın yerde göreceksin.

---

## ✅ Kurulum Tamamlandı!

Artık:
- ✅ n8n çalışıyor
- ✅ Twilio WhatsApp Sandbox aktif
- ✅ n8n ↔ Twilio bağlantısı kuruldu
- ✅ n8n ↔ Backend API bağlantısı kuruldu
- ✅ İlk test başarılı

### Sıradaki Adımlar

1. **Listing Flow** - İlan verme sürecini tamamla
2. **Search Flow** - Ürün arama özelliği ekle
3. **Media Upload** - Fotoğraf yükleme ekle
4. **Order Flow** - Sipariş yönetimi ekle
5. **Notifications** - Background job'lar için bildirimler

---

## 🔧 Sorun Giderme

### "Webhook not found" Hatası

**Sorun**: Twilio'dan mesaj gelmiyor  
**Çözüm**:
- n8n workflow'unun **Active** olduğundan emin ol
- ngrok URL'nin doğru olduğunu kontrol et
- Twilio webhook URL'yi tekrar kaydet

### "Connection Refused" Backend API

**Sorun**: n8n, backend API'ye bağlanamıyor  
**Çözüm**:
- Backend'in çalıştığını kontrol et: `curl http://localhost:8000/docs`
- Docker kullanıyorsan `host.docker.internal` kullan
- Firewall'u kontrol et

### ngrok Session Expired

**Sorun**: ngrok'un ücretsiz versiyonu 2 saat sonra URL değişiyor  
**Çözüm**:
- ngrok'u yeniden başlat
- Yeni URL'yi Twilio'da güncelle
- veya ngrok Pro hesap al (sabit URL)

---

## 📚 Daha Fazla Bilgi

- [n8n Documentation](https://docs.n8n.io/)
- [Twilio WhatsApp Sandbox](https://www.twilio.com/docs/whatsapp/sandbox)
- [ngrok Documentation](https://ngrok.com/docs)

---

## 🎉 Tebrikler!

WhatsApp entegrasyonunun temelini kurdun. Şimdi daha gelişmiş workflow'ları ekleyebilirsin! 🚀

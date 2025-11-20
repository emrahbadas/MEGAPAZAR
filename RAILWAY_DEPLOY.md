# Railway Deployment Guide - MEGAPAZAR Backend

## 🚀 Hızlı Deploy (5 Dakika)

### 1. Railway Hesabı Oluştur
1. https://railway.app/ adresine git
2. **Login with GitHub** butonuna tıkla
3. GitHub hesabınla giriş yap (emrahbadas)

### 2. Yeni Proje Oluştur
1. Dashboard'da **New Project** buton
2. **Deploy from GitHub repo** seç
3. **MEGAPAZAR** reposunu seç
4. **megapazar-agent-api** klasörünü işaret et

### 3. Environment Variables Ekle
Railway dashboard'da **Variables** sekmesine git ve şunları ekle:

**ZORUNLU (Bunlar olmadan sistem çalışmaz):**

Lokal `.env` dosyanızdaki tüm değerleri Railway'e kopyalayın:

```env
OPENAI_API_KEY=(lokal .env'den kopyala)
SUPABASE_URL=(lokal .env'den kopyala)
SUPABASE_KEY=(lokal .env'den kopyala)
SUPABASE_SERVICE_KEY=(lokal .env'den kopyala)
TWILIO_ACCOUNT_SID=(lokal .env'den kopyala)
TWILIO_AUTH_TOKEN=(lokal .env'den kopyala)
N8N_WEBHOOK_URL=(lokal .env'den kopyala)
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

> ⚠️ **KRITIK**: Twilio ve n8n credentials **ZORUNLU**! Sistem n8n üzerinden WhatsApp ile çalışıyor.

> 💡 **Nasıl Yapılır**: Lokal `.env` dosyanızı açın → Her satırı Railway Variables sekmesine kopyalayın (Key=Value formatında)

### 4. Deploy Başlat
1. **Deploy** butonuna tıkla
2. 2-3 dakika bekle (build süreci)
3. **Deployments** sekmesinden durumu izle

### 5. Public URL Al
1. **Settings** sekmesi → **Networking**
2. **Generate Domain** butonuna tıkla
3. URL'i kopyala (örn: `megapazar-api.up.railway.app`)

---

## 🔧 Deploy Sonrası Adımlar

### n8n Workflow'larını Güncelle

Railway URL'ini aldıktan sonra (örn: `https://megapazar-api.up.railway.app`):

1. **n8n Cloud'a git**: https://emrahbadas7.app.n8n.cloud/

2. **MEGAPAZAR Main Router** workflow'unu aç:
   - "Call Backend API" node'una tıkla
   - URL'i güncelle: `https://megapazar-api.up.railway.app/conversation`
   - Save & Activate

3. **MEGAPAZAR Search Flow** workflow'unu aç:
   - "Call Search API" node'una tıkla
   - URL'i güncelle: `https://megapazar-api.up.railway.app/search`
   - Save & Activate

4. **MEGAPAZAR Order Flow** workflow'unu aç:
   - "Create Order" node'una tıkla
   - URL'i güncelle: `https://megapazar-api.up.railway.app/orders`
   - Save & Activate

### Test Et

Railway dashboard'dan **View Logs** ile kontrol et:

```bash
# Health check
curl https://megapazar-api.up.railway.app/health

# API docs
https://megapazar-api.up.railway.app/docs

# Test conversation
curl -X POST https://megapazar-api.up.railway.app/conversation \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"merhaba","source":"whatsapp"}'
```

---

## 📊 Monitoring

Railway otomatik olarak sağlar:
- **Logs**: Gerçek zamanlı uygulama logları
- **Metrics**: CPU, RAM, Network kullanımı
- **Alerts**: Uygulama çökerse email gönderir

---

## 💰 Maliyet

**Free Tier**:
- $5 ücretsiz kredi/ay
- ~500 saat çalışma süresi
- Kredi kartı gerekmez

**Upgrade Zamanı**:
- Günlük 100+ kullanıcı
- 24/7 uptime gerekli
- Aylık ~$5-10

---

## 🔄 Otomatik Deploy

Railway GitHub'a bağlı. Her `git push` otomatik deploy tetikler:

```bash
# Kod değişikliği yap
git add .
git commit -m "Backend güncellemesi"
git push origin main

# Railway otomatik deploy başlatır (1-2 dakika)
```

---

## 🚨 Sorun Giderme

### Deploy Başarısız

**Hata**: `ModuleNotFoundError`
- **Çözüm**: `requirements.txt` doğru mu kontrol et

**Hata**: `Port already in use`
- **Çözüm**: `railway.json` doğru (`$PORT` kullanıyor mu)

### Uygulama Çöküyor

**Logs'da kontrol et**:
- Environment variables doğru girildi mi?
- Supabase bağlantısı çalışıyor mu?
- OpenAI API key geçerli mi?

### n8n Bağlanamıyor

**Railway URL'i kontrol et**:
- HTTPS ile başlıyor mu?
- `/conversation` endpoint'i erişilebilir mi?
- n8n HTTP Request node'da Method POST mu?

---

## ✅ Deploy Kontrol Listesi

- [ ] Railway hesabı oluşturuldu
- [ ] GitHub repo bağlandı
- [ ] Environment variables eklendi
- [ ] Deploy tamamlandı (yeşil durum)
- [ ] Public URL alındı
- [ ] Health check geçti
- [ ] n8n workflow'ları güncellendi
- [ ] End-to-end test yapıldı

---

**Yardım**: Railway Discord - https://discord.gg/railway

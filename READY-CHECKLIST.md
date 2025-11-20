# 🚀 Megapazar Başlangıç Checklist

## ✅ Tamamlanan İşlemler

### 1. Proje Yapısı
- ✅ Python agent API oluşturuldu
- ✅ 9 adet agent implement edildi (conversation, vision, text_parser, product_match, market_search, pricing, listing_writer, listing_coordinator, base)
- ✅ LangGraph workflow kuruldu
- ✅ FastAPI endpoints hazır
- ✅ Helper utilities (logger, openai_client, supabase_client, storage_helper)

### 2. Veritabanı Yapısı
- ✅ SQL schema oluşturuldu (supabase-schema.sql)
- ✅ 6 tablo tasarlandı: users, listings, product_images, product_embeddings, orders, conversations
- ✅ pgvector extension yapılandırıldı
- ✅ Vector search fonksiyonu (match_products) yazıldı
- ✅ RLS policies tanımlandı
- ✅ Auto-update triggers eklendi
- ✅ Resim yönetimi için product_images tablosu ayrıldı

### 3. Resim Yönetimi
- ✅ Product_images tablosu: storage_path, public_url, is_primary, display_order, metadata
- ✅ storage_helper.py: upload, get, delete, set_primary fonksiyonları
- ✅ API endpoints: GET/POST /api/listings/{id}/images

### 4. Environment Ayarları
- ✅ .env dosyası hazır
- ✅ Supabase credentials eklendi (URL, anon key, service key)

---

## 🔄 Bekleyen İşlemler

### ADIM 1: Supabase SQL Çalıştır ⏳
**Yapılacak:**
1. https://supabase.com/dashboard/project/snovwbffwvmkgjulrtsm adresine git
2. Sol menüden **SQL Editor** → **New Query**
3. `megapazar-agent-api/supabase-schema.sql` dosyasını aç
4. Tüm içeriği kopyala → SQL Editor'a yapıştır
5. **RUN** butonuna tıkla (veya Ctrl+Enter)

**Beklenen Sonuç:**
```
✅ Megapazar veritabanı başarıyla oluşturuldu!
✅ 6 tablo oluşturuldu
✅ pgvector extension yüklendi
✅ Vector search fonksiyonu eklendi
```

**Hata Çıkarsa:**
- "extension pgvector does not exist" → Database Settings'den Vector extension'ı enable et
- "already exists" hatası normal (tekrar çalıştırıldıysa)

---

### ADIM 2: Storage Bucket Oluştur 📦
**Yapılacak:**
1. Supabase Dashboard → **Storage** (sol menü)
2. **New Bucket** butonuna tıkla
3. Bucket adı: `product-images`
4. **Public bucket** seçeneğini işaretle ✅
5. **Create bucket**

**Neden Gerekli:**
- Ürün fotoğrafları burada saklanacak
- product_images tablosundaki storage_path bu bucket'ı referans ediyor
- Public bucket → URL'ler doğrudan erişilebilir olacak

---

### ADIM 3: OpenAI API Key Ekle 🔑
**Yapılacak:**
1. https://platform.openai.com/api-keys adresine git
2. **Create new secret key** → İsim ver (örn: "megapazar-api")
3. Key'i kopyala (sk-proj-... ile başlayan)
4. `megapazar-agent-api/.env` dosyasını aç
5. Şu satırı bul:
   ```
   OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
   ```
6. `YOUR_KEY_HERE` kısmını gerçek key ile değiştir:
   ```
   OPENAI_API_KEY=sk-proj-abcd1234efgh5678...
   ```
7. Dosyayı kaydet

**Model Kullanımı:**
- GPT-4o: Ana agent'lar (pricing, listing writer) → $5.00/1M input tokens
- GPT-4o-mini: Yardımcı işlemler (conversation, text parsing) → $0.15/1M
- GPT-4o-vision: Resim analizi → $10.00/1M input tokens
- text-embedding-3-small: Vector embeddings → $0.02/1M tokens

---

### ADIM 4: Dependencies Yükle 📦
**Yapılacak:**
Terminal'de çalıştır:
```powershell
cd "C:\Users\emrah badas\OneDrive\Desktop\mega pzar\megapazar-agent-api"
python -m pip install -r requirements.txt
```

**Yüklenecek Paketler:**
- fastapi, uvicorn (API server)
- langchain, langgraph (agent framework)
- openai (GPT models)
- supabase (database client)
- pillow (resim işleme)
- httpx, pydantic, python-dotenv (utilities)

**Hata Çıkarsa:**
- Python 3.11+ yüklü olmalı → `python --version`
- pip güncel olmalı → `python -m pip install --upgrade pip`

---

### ADIM 5: API'yi Başlat 🚀
**Yapılacak:**
```powershell
cd "C:\Users\emrah badas\OneDrive\Desktop\mega pzar\megapazar-agent-api"
python main.py
```

**Beklenen Çıktı:**
```
🚀 Starting Megapazar Agent API...
📍 Host: 0.0.0.0:8000
🔧 Debug mode: True
✅ Listing workflow initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Tarayıcıda Test:**
- http://localhost:8000 → Ana sayfa (API bilgileri)
- http://localhost:8000/docs → Swagger UI (tüm endpoints)

---

### ADIM 6: İlk Test Çağrısı 🧪
**Yapılacak:**

#### Test 1: Health Check
```powershell
curl http://localhost:8000/health
```
**Beklenen:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-...",
  "version": "1.0.0"
}
```

#### Test 2: Yeni İlan (Text)
```powershell
$body = @{
    user_id = "test-user-123"
    message = "4 adet ikinci el endüstriyel rotor satmak istiyorum"
    platform = "web"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/listing/start -Body $body -ContentType "application/json"
```

**Beklenen Akış:**
1. ConversationAgent → Intent: "listing"
2. TextParserAgent → Ürün bilgilerini çıkarır
3. ProductMatchAgent → Supabase'de benzer ürünler arar
4. MarketSearchAgent → Piyasa fiyatlarını araştırır (Tavily)
5. PricingAgent → Optimum fiyat hesaplar
6. ListingWriterAgent → İlan metni yazar
7. Response → `listing_preview` ile döner

**Response Örneği:**
```json
{
  "type": "listing_preview",
  "data": {
    "title": "Endüstriyel Rotor - Yüksek Performans, İkinci El",
    "description": "4 adet ikinci el endüstriyel rotor...",
    "price": 85000,
    "category": "Endüstriyel Malzemeler",
    "similar_products": [...],
    "market_comparison": "Piyasa ortalaması: ₺90,000 - Sizin fiyatınız: ₺85,000 (%5.5 avantaj)"
  }
}
```

#### Test 3: Yeni İlan (Resim)
```powershell
$body = @{
    user_id = "test-user-123"
    message = "Bu ürünü satmak istiyorum"
    image_url = "https://example.com/product.jpg"
    platform = "whatsapp"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/listing/start -Body $body -ContentType "application/json"
```

**Beklenen Akış:**
1. ConversationAgent → Intent: "listing"
2. **VisionAgent** → GPT-4o-vision ile resim analizi
3. ProductMatchAgent → Vector search
4. (Geri kalan adımlar aynı)

---

## 🎯 Sonraki Adımlar (POST-MVP)

### 1. n8n Workflow Entegrasyonu
- WhatsApp Webhook setup
- API call node'ları
- Response formatting

### 2. Frontend (Next.js)
- Ürün listeleme sayfası
- Resim upload component
- Real-time preview

### 3. Advanced Features
- BuyerSearchAgent (alıcı tarafı arama)
- OrderProcessingAgent (sipariş yönetimi)
- Webhook notifications
- Analytics dashboard

---

## 📞 Destek

**API Swagger Docs:**
http://localhost:8000/docs

**Log Dosyaları:**
`megapazar-agent-api/logs/megapazar.log`

**Hata Durumunda:**
1. Log dosyasını kontrol et
2. `.env` dosyasındaki credentials doğru mu?
3. Supabase'de tablolar oluştu mu? (Database → Tables)
4. OpenAI API key geçerli mi? (platform.openai.com)

---

## 💰 Maliyet Tahmini

**Aylık ~₺2,100 ($70):**
- OpenAI API: ~₺1,500 ($50) - 1000 ilan/ay için
- Supabase: Ücretsiz (Free tier yeterli)
- n8n: Ücretsiz (self-hosted) veya ~₺600 ($20) Cloud
- Hosting: ~₺0 (local) veya ~₺300-600 ($10-20) Render/Railway

**İlk 3 Ay Test Süreci:**
- Total: ~₺6,300 ($210)
- OpenAI: ~₺4,500 ($150)
- Supabase: ₺0
- n8n: ₺0 (self-hosted test)
- Hosting: ₺1,800 ($60) - Render Pro

---

## ✨ Hazırsın!

Tüm adımları tamamladıktan sonra:

```powershell
cd megapazar-agent-api
python main.py
```

API çalıştı mı? → http://localhost:8000/docs

**Test isteği atabilir, n8n workflow'unu bağlayabilir, frontend'i geliştirebilirsin! 🚀**

# 🚀 MEGAPAZAR AGENT - MASTER PLAN

**Proje Başlangıç**: 16 Kasım 2025  
**Mevcut Durum**: Core conversation flow tamamlandı, editing flow yazıldı (test bekliyor)  
**Kullanılan Stack**: FastAPI, LangChain, LangGraph, OpenAI GPT-4o, Supabase, pgvector

---

## ✅ TAMAMLANAN İŞLER

### 🎯 Phase 1: Core Infrastructure (COMPLETED)
- [x] **Multi-turn Conversation System**
  - SessionState model (ConversationStage, UserIntent enums)
  - SessionManager (in-memory, 30min expiry)
  - EnhancedConversationAgent (stage-based routing)
  
- [x] **Enhanced Listing Workflow**
  - StateGraph architecture
  - conversation → text_parser → product_match → market_search → pricing → listing_writer
  - Conditional routing based on response_type

- [x] **Vector Search & Embeddings**
  - text-embedding-3-small
  - pgvector match_products() function
  - Similarity threshold: 0.7

- [x] **Price Negotiation Flow**
  - Intent detection in PREVIEW stage (regex patterns)
  - reprice_node with user_price override
  - Price key compatibility (recommended_price + suggested_price)
  - Response type routing (reprice_listing)

- [x] **Price Consistency Fix**
  - pricing_node checks session.pricing first
  - PricingAgent bypasses if pricing exists in state
  - Test: 1790 TL → 2000 TL → 2000 TL (consistent) ✅

- [x] **Confirmation Flow**
  - "Onayla" intent detection
  - Listing draft transfer to response.data
  - /api/listing/confirm endpoint with database save
  - Full flow test: Create → Negotiate → Confirm → Save ✅

### 🐛 Phase 2: Bug Fixes (COMPLETED)
- [x] Intent detection PREVIEW stage bug
- [x] Response type mismatch (price_negotiation → reprice_listing)
- [x] Price key mismatch (0 TL bug fixed)
- [x] Listing draft not in confirmation response

---

## 🔨 DEVAM EDEN İŞLER

### 📝 Phase 3: Editing Flow (CODE READY, TESTING PENDING)
- [x] **_handle_editing() implemented**
  - LLM-based field detection (title/description/price/category)
  - Change description parsing
  - JSON structured output
  
- [x] **edit_node() implemented**
  - Price: Direct numeric value set
  - Title/Description/Category: LLM content generation
  - Session update + new preview
  
- [ ] **Testing needed**
  - End-to-end editing flow
  - Multiple field edits
  - Edge cases

---

## 📋 KALAN CORE İŞLER

### Phase 4: Information Gathering
- [ ] **Eksik bilgi toplama flow**
  - _handle_gathering_info() implementation
  - Dynamic question generation via LLM
  - Answer parsing + product_info update
  - "Hangi marka? Kaç adet?" scenarios

### Phase 5: Infrastructure
- [ ] **Session Persistence**
  - Redis integration OR file-based pickle
  - Session recovery after API restart
  - Cleanup expired sessions

---

## 🎯 YENİ ÖZELLİKLER (USER REQUESTS)

### Phase 6: Post-Publish Management
- [ ] **İlan silme ve düzenleme**
  - DELETE /api/listing/{listing_id}
  - PUT /api/listing/{listing_id}
  - User ownership validation
  - Soft delete (is_active=false) vs hard delete

- [ ] **Aktif ilanları listeleme**
  - GET /api/listings/my?user_id={user_id}&status=active
  - Response: title, price, created_at, view_count
  - MY_LISTINGS intent in conversation agent

- [ ] **Piyasa değeri bildirimi**
  - Background job (daily/weekly)
  - Price comparison (current vs market)
  - ±20% threshold for notification
  - n8n webhook / email / WhatsApp integration
  - Database: notifications table

---

## 🌟 WOW ÖZELLİKLERİ (FUTURE ROADMAP)

### 🔥 Tier 1: Quick Wins (Hızlı Impact)
#### 1. **Competitive Intelligence** 
**Açıklama**: Rakip ilanları gerçek zamanlı takip
- "Aynı ürünü satan 3 kişi var, hepsi 2500 TL'ye satıyor"
- "Son 1 haftada bu ürünün fiyatı %15 düştü"
- Otomatik fiyat güncelleme önerisi

**Teknik**:
- Web scraping (BeautifulSoup / Playwright)
- Scheduled jobs (APScheduler)
- Database: competitor_listings table

**Effort**: 2-3 gün  
**Impact**: ⭐⭐⭐⭐⭐

---

#### 2. **Proactive Agent - Satış Takibi**
**Açıklama**: İlan performansını izleyip proaktif aksiyonlar
- "İlanınız 3 gündür görüntülenmiyor, fiyat düşürelim mi?"
- "Bu kategoriden geçen hafta 127 ürün satıldı"
- Automatic price adjustment suggestions

**Teknik**:
- Background job: Daily listing analysis
- View count tracking
- Notification system (n8n webhook)

**Effort**: 2 gün  
**Impact**: ⭐⭐⭐⭐

---

#### 3. **Smart Suggestions (Basic)**
**Açıklama**: Gerçek zamanlı optimizasyon önerileri
- "Bu kategoride ortalama fiyat 2800 TL"
- "Bu kelimeleri eklerseniz %40 daha çok görüntülenir"
- "Pazar günleri bu ürün daha çok satılıyor"

**Teknik**:
- Statistical analysis on existing listings
- GPT-4o for suggestions
- Rule-based + LLM combo

**Effort**: 3 gün  
**Impact**: ⭐⭐⭐⭐

---

#### 4. **Social Proof & Trust Scores**
**Açıklama**: Satıcı güvenilirlik ve trend bilgileri
- "Bu satıcı %98 güvenilir" (geçmiş satışlar, yorumlar)
- "Bu ürün şu an trend, 24 saatte 50 kişi aradı"
- Success stories: "Bu kategoriden geçen hafta 127 ürün satıldı"

**Teknik**:
- User ratings database
- Transaction history analysis
- Trend detection algorithms

**Effort**: 2-3 gün  
**Impact**: ⭐⭐⭐⭐

---

### 🚀 Tier 2: Advanced Features (Orta Efor, Yüksek Impact)

#### 5. **Multi-Modal Understanding**
**Açıklama**: Ses, video, görüntü ile ilan oluşturma
- **Ses ile ilan**: Whisper API transcript → otomatik ilan
- **Video analizi**: Ürün videosundan ekipman tanıma
- **OCR fatura okuma**: Fatura foto → otomatik fiyat/marka/model

**Teknik**:
- OpenAI Whisper API
- GPT-4o Vision API
- Custom OCR pipeline (Tesseract / Cloud Vision)

**Model Requirement**: 
- GPT-4o yeterli (basic)
- **GPT-4.5 Vision** veya **Claude 3.5** için advanced (hasar tespiti, detaylı analiz)

**Effort**: 4-5 gün  
**Impact**: ⭐⭐⭐⭐⭐

---

#### 6. **AI-Powered Negotiation**
**Açıklama**: Otomatik müzakere ve teklif yönetimi
- "Alıcı 2000 TL teklif etti → 2300 TL'de anlaşın (optimal)"
- Seller'ın minimum fiyatı + alıcının budget'ı analizi
- Multi-turn negotiation strategy

**Teknik**:
- Reinforcement learning (optional)
- LLM-based strategy (GPT-4o baseline)
- Negotiation history tracking

**Model Requirement**: 
- GPT-4o (basic counter-offers)
- **Claude 3.5 Sonnet** (strategic reasoning, multi-turn)

**Effort**: 5-7 gün  
**Impact**: ⭐⭐⭐⭐⭐

---

#### 7. **Predictive Selling**
**Açıklama**: Satış tahmini ve fiyat optimizasyonu
- "Bu ilan 3-5 gün içinde satılır (85% olasılık)"
- "100 TL düşürürseniz 2x hızlı satılır"
- Historical data analysis + trend prediction

**Teknik**:
- Time series analysis
- Regression models (sklearn / XGBoost)
- Feature engineering (category, price, photos, description quality)

**Model Requirement**: 
- GPT-4o (basic insights)
- **GPT-4.5 / Claude 3.5** (multi-variable analysis, confidence scores)

**Effort**: 7-10 gün  
**Impact**: ⭐⭐⭐⭐⭐

---

#### 8. **Smart Analytics Dashboard**
**Açıklama**: İlan performans dashboard
- Görüntüleme haritası (hangi şehirlerden bakıldı)
- Engagement timeline (hangi saatlerde tıklanıyor)
- Conversion funnel: Görüntüleme → Favori → Mesaj → Satış

**Teknik**:
- Frontend: React / Next.js + Chart.js
- Backend: Analytics API endpoints
- Database: Click tracking, event logging

**Effort**: 5-7 gün  
**Impact**: ⭐⭐⭐⭐

---

### 💎 Tier 3: Premium Features (Yüksek Efor, WOW Factor)

#### 9. **Automated Workflows**
**Açıklama**: Toplu işlemler ve zamanlama
- **Toplu ilan**: Excel/CSV → 100 ilan birden
- **Zamanlı yayın**: "Bu ilanı Pazar 10:00'da yayınla"
- **A/B testing**: 2 farklı başlık test et, kazananı kullan

**Teknik**:
- Celery background tasks
- CSV parsing + validation
- Scheduled jobs (APScheduler / Celery Beat)

**Effort**: 5-7 gün  
**Impact**: ⭐⭐⭐⭐

---

#### 10. **Gamification System**
**Açıklama**: Satıcı motivasyonu ve rekabet
- Seviye sistemi: Bronze → Silver → Gold → Platinum
- Badges: "Hızlı Satıcı", "Güvenilir Satıcı", "Fiyat Şampiyonu"
- Leaderboard: "Bu haftanın en çok satan 10 kişisi"

**Teknik**:
- Points/XP system
- Achievement tracking
- Leaderboard API

**Effort**: 4-5 gün  
**Impact**: ⭐⭐⭐⭐

---

#### 11. **Integration Hub**
**Açıklama**: Dış platformlar entegrasyonu
- **WhatsApp Business API**: Tüm sohbet WhatsApp'tan
- **Instagram entegrasyonu**: Story/post → otomatik ilan
- **Shopify/WooCommerce sync**: E-ticaret stok senkronizasyonu

**Teknik**:
- WhatsApp Business API (Cloud API / On-Premise)
- Instagram Graph API
- Shopify REST API / WooCommerce REST API

**Effort**: 10-14 gün (per integration)  
**Impact**: ⭐⭐⭐⭐⭐

---

## 🎨 CONTENT GENERATION UPGRADE (FUTURE)

### Listing Writer Agent Enhancement
**Şu an**: GPT-4o (generic ama iyi)  
**Gelecek**: Claude 3.5 Sonnet

**Faydalar**:
- %40 daha çekici başlıklar
- SEO-optimized content
- Psikolojik trigger'lar ("Acil satılık! Son 3 gün!")
- Daha yaratıcı açıklamalar

**Maliyet**: +%30-40  
**Value**: +%200 (CTR artışı)

---

## 📊 MODEL STRATEJİSİ

### Mevcut: GPT-4o Everywhere ✅
- **장점**: Ucuz, hızlı, yeterli
- **단점**: Generic content, basic insights

### Gelecek Plan: Hybrid Architecture 🎯
```python
MODEL_CONFIG = {
    "conversation": "gpt-4o",              # Routine
    "parsing": "gpt-4o",                   # Structured output
    "listing_writer": "gpt-4o",            # Şimdilik yeterli
    "pricing": "gpt-4o",                   # Analitik
    
    # Future upgrades when needed:
    # "listing_writer": "claude-3-5-sonnet",  # Creative content
    # "negotiation": "claude-3-5-sonnet",     # Strategic thinking
    # "predictive": "gpt-4.5-turbo",          # Advanced analytics
}
```

**Karar**: Önce sistem otursun, sonra performansa göre upgrade

---

## 🗓️ TIMELINE TAHMINI

### Sprint 1 (1 hafta): Core Completion
- [ ] Editing flow test + fixes
- [ ] Eksik bilgi toplama
- [ ] Session persistence

### Sprint 2 (1 hafta): Post-Publish Features
- [ ] İlan silme/düzenleme endpoints
- [ ] Aktif ilanları listeleme
- [ ] Piyasa değeri bildirimi (basic)

### Sprint 3 (2 hafta): Quick Win WOW Features
- [ ] Competitive Intelligence
- [ ] Proactive Agent - Satış takibi
- [ ] Smart Suggestions (basic)
- [ ] Social Proof

### Sprint 4+ (4-6 hafta): Advanced Features
- [ ] Multi-Modal Understanding
- [ ] AI Negotiation
- [ ] Predictive Selling
- [ ] Analytics Dashboard

---

## 💰 BUDGET & RESOURCE ESTIMATION

### API Costs (Monthly)
- **GPT-4o**: ~$200-500 (10K-25K listings/month)
- **Embeddings**: ~$50-100
- **Whisper API**: ~$20-50 (if voice feature)
- **Total**: $300-700/month

### Infrastructure
- **Supabase**: Free → Pro ($25/month)
- **Redis**: ~$10-20/month (if needed)
- **Server**: ~$50-100/month

---

## 🎯 SUCCESS METRICS

### Phase 1 (Core)
- ✅ Multi-turn conversation: 3+ turns per session
- ✅ Price negotiation: 60%+ acceptance rate
- ✅ Full flow completion: 80%+ success rate

### Phase 2 (WOW Features)
- [ ] User retention: +40%
- [ ] Listing quality score: +50%
- [ ] Time to list: -60% (avg 2 min → 48 sec)
- [ ] CTR (Click-through rate): +30%

### Phase 3 (Advanced)
- [ ] Negotiation success rate: 70%+
- [ ] Predictive accuracy: 80%+
- [ ] Multi-modal listings: 20% adoption

---

## 📝 NOTLAR

### Teknik Kararlar
- **LangGraph** yerine **pure Python** ile workflow yapılabilirdi ama LangGraph conditional routing için çok iyi
- **pgvector** şu an yeterli, ileride **Pinecone** / **Weaviate** düşünülebilir
- **Session persistence**: Redis ideal ama başlangıç için file-based yeterli

### Performans Optimizations (Future)
- [ ] Response caching (Redis)
- [ ] LLM response streaming
- [ ] Batch processing for bulk operations
- [ ] Database query optimization (indexes)

---

## 🏁 BUGÜNKÜ ÖZET (16 Kasım 2025)

### Tamamlanan
✅ Multi-turn conversation  
✅ Price negotiation (1790 → 2000 TL)  
✅ Full confirmation flow  
✅ Price consistency fix  
✅ Editing flow (code ready)  

### Kalan
⏳ Editing flow test  
⏳ Eksik bilgi toplama  
⏳ Session persistence  
⏳ 3 yeni feature (post-publish management)  

### Sonraki Adım
🎯 Editing flow'u test et → Eksik bilgi toplama → Session persistence

---

**Last Updated**: 16 Kasım 2025, 17:30  
**Next Review**: Sprint 1 completion sonrası

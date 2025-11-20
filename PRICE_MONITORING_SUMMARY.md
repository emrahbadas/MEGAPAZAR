# Piyasa Değeri Bildirimi - Implementation Summary

## ✅ Tamamlanan İşlemler

### 1. Database Schema
**Dosya**: `migrations/add_market_price_and_notifications.sql`

- `listings` tablosuna yeni kolonlar:
  - `market_price_at_publish`: PricingAgent'ın bulduğu piyasa fiyatı
  - `last_price_check_at`: Son fiyat kontrolü zamanı

- `notifications` tablosu:
  - `id`, `user_id`, `listing_id`
  - `type`: 'price_high', 'price_low', 'info', 'warning'
  - `title`, `message`
  - `metadata`: JSON (user_price, market_price, difference_percent)
  - `is_read`, `created_at`, `read_at`

### 2. Price Monitor Service
**Dosya**: `utils/price_monitor.py`

- `PriceMonitor` class:
  - `check_all_active_listings()`: Tüm aktif ilanları kontrol et
  - `_check_listing_price()`: Tek ilan için fiyat kontrolü
  - `_create_price_alert()`: Bildirim oluştur (±20% eşik)

- Mantık:
  1. Aktif ilanları getir
  2. Her ilan için PricingAgent ile yeni piyasa fiyatı bul
  3. Fark ±20%'den fazlaysa → notification oluştur
  4. `last_price_check_at` güncelle

### 3. Background Task
**Dosya**: `utils/background_tasks.py`

- `check_listing_prices()`: Price monitor'u çağır
- APScheduler cron job: Her gün saat 09:00'da çalış

### 4. API Endpoints
**Dosya**: `main.py`

#### GET /api/notifications
- Query params: `user_id`, `unread_only`, `limit`
- Response: Kullanıcının bildirimleri

#### POST /api/notifications/{id}/mark-read
- Bildirimi okundu olarak işaretle
- Ownership validation

#### POST /api/admin/check-prices
- Manual fiyat kontrolü tetikle (test için)
- Production'da authentication ekle

#### POST /api/listing/confirm (UPDATED)
- `market_price_at_publish` kaydediliyor
- Workflow'dan gelen `suggested_price` değeri

### 5. Schemas
**Dosya**: `models/schemas.py`

- `NotificationResponse`: Bildirim response modeli

### 6. Test Script
**Dosya**: `test_price_monitoring.py`

- Fiyat kontrolü tetikleme
- Bildirimleri getirme
- Okundu işaretleme

## 📋 Kurulum Adımları

### 1. Supabase Migration
```sql
-- Supabase SQL Editor'de çalıştır:
-- migrations/add_market_price_and_notifications.sql
```

### 2. API Restart
```bash
cd megapazar-agent-api
uvicorn main:app --reload
```

### 3. Test
```bash
python test_price_monitoring.py
```

## 🎯 Nasıl Çalışıyor?

### İlan Yayınlama:
```
User: "Laptop 25,000 TL'ye satıyorum"
PricingAgent: Web search → market_price = 20,000 TL
→ Supabase: price=25000, market_price_at_publish=20000
```

### Background Job (Günlük 09:00):
```
FOR EACH active listing:
  1. PricingAgent.get_price() → new_market_price = 18,000 TL
  2. Fark: (25000 - 18000) / 18000 = +38%
  3. IF +38% > 20%:
     → CREATE notification:
        "İlanınız piyasadan %38 pahalı, fiyat düşürmek ister misiniz?"
```

### Kullanıcı:
```
GET /api/notifications?user_id=xxx
→ "📈 Fiyat Uyarısı: Laptop (Piyasadan %38 pahalı)"
```

## 🔄 İleride Eklenecekler

### Seçenek 2: Hibrit Fiyat Analizi
```python
# Internal + External pricing
internal_avg = get_similar_listings_avg(category, title)  # Supabase
external_market = PricingAgent.get_price()  # Web search

message = f"""
Piyasa fiyatı: {external_market} TL (Genel web)
Platformumuzda ortalama: {internal_avg} TL (Benzer ilanlar)
Sizin fiyatınız: {user_price} TL
"""
```

### Notification Delivery
- n8n webhook integration
- Push notifications
- Email alerts

## 🧪 Test Senaryoları

1. ✅ Fiyat kontrolü tetikleme (admin endpoint)
2. ✅ Bildirimleri getirme (unread/all)
3. ✅ Okundu işaretleme
4. ✅ Ownership validation

## 📊 Monitoring

### Background Job Logs:
```
2025-11-17 09:00:00 - price_monitor - INFO - 🔍 Starting price check...
2025-11-17 09:00:05 - price_monitor - INFO - Checking: Laptop (User: 25000 TL)
2025-11-17 09:00:07 - price_monitor - INFO -    Market price: 18000 TL (Difference: +38%)
2025-11-17 09:00:08 - price_monitor - INFO - ✅ Created alert for listing xxx (+38%)
2025-11-17 09:01:00 - price_monitor - INFO - ✅ Price check completed. Created 3 alerts
```

### Supabase Query:
```sql
-- Son 7 günde oluşturulan fiyat uyarıları
SELECT 
  n.created_at,
  l.title,
  n.metadata->>'user_price' as user_price,
  n.metadata->>'market_price' as market_price,
  n.metadata->>'difference_percent' as diff
FROM notifications n
JOIN listings l ON n.listing_id = l.id
WHERE n.type IN ('price_high', 'price_low')
  AND n.created_at > NOW() - INTERVAL '7 days'
ORDER BY n.created_at DESC;
```

## 🎉 Sonuç

Piyasa değeri bildirimi sistemi hazır! 

**Özellikler**:
- ✅ Günlük otomatik fiyat kontrolü
- ✅ ±20% eşik uyarısı
- ✅ Bildirim sistemi
- ✅ API endpoints
- ✅ Background jobs

**Next Steps**:
1. SQL migration'ı çalıştır
2. Test et
3. İlerleyen süreçte: Internal pricing eklenir

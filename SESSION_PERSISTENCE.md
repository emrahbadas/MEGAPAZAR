# Session Persistence

## Özellikler

✅ **File-based persistence** (pickle)
✅ **Automatic save/load** - Her update'de disk'e kaydedilir
✅ **Auto-cleanup** - Süresi dolmuş session'lar otomatik temizlenir (10 dakikada bir)
✅ **API restart safe** - API yeniden başlatılsa bile session'lar korunur
✅ **Multi-user support** - Her kullanıcı ayrı dosyada

## Teknik Detaylar

### Storage Location
```
megapazar-agent-api/sessions/
├── session_user-123.pkl
├── session_user-456.pkl
└── session_test-user.pkl
```

### Session Lifecycle
1. **Create**: `get_or_create_session(user_id)` - Memory'de yoksa disk'ten yükler, hiç yoksa yeni oluşturur
2. **Update**: `update_session(session)` - Hem memory hem disk'e yazar
3. **Load**: Otomatik - `get_session()` ve `get_or_create_session()` disk'ten yükler
4. **Delete**: `delete_session(user_id)` - Memory + disk'ten siler
5. **Cleanup**: Her 10 dakikada bir expired session'lar silinir

### TTL (Time To Live)
- Default: **30 dakika** (son mesajdan itibaren)
- Değiştirmek için: `session.is_expired(timeout_minutes=60)`

## Kullanım

### API Restart Sonrası Session Korunur

```python
# İlk request
POST /api/listing/start
{
    "user_id": "user-123",
    "message": "Araba satmak istiyorum"
}
# Response: "Hangi marka?"

# API restart edildi...

# Sonraki request - context korundu
POST /api/listing/start
{
    "user_id": "user-123",
    "message": "Mercedes"
}
# Response: "Mercedes'in hangi modeli?" (context korundu!)
```

### Background Tasks

```python
# main.py'de otomatik başlar
from utils.background_tasks import start_background_tasks

scheduler = start_background_tasks()
# Her 10 dakikada bir cleanup_expired_sessions() çalışır
```

### Manual Cleanup

```python
from models.conversation_state import session_manager

# Tek bir session sil
session_manager.delete_session("user-123")

# Tüm expired session'ları temizle
session_manager.cleanup_expired()
```

## Test

```bash
# Session persistence unit test
python test_session_persistence.py

# E2E test (API ile)
python test_e2e_persistence.py
```

## Production Considerations

### Redis Migration (Future)
Dosya-based sistem development ve small-scale production için yeterli.
Büyük scale için Redis önerilir:

```python
# Redis implementation örneği
class RedisSessionManager(SessionManager):
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def _save_to_disk(self, session):
        # Pickle + Redis SET
        self.redis.setex(
            f"session:{session.user_id}",
            1800,  # 30 min TTL
            pickle.dumps(session)
        )
```

### Disk Space Management
- Her session ~5-50KB (conversation history'ye bağlı)
- 1000 aktif kullanıcı ≈ 5-50MB
- Cleanup job disk kullanımını düşük tutar

### Backup
Sessions klasörünü düzenli yedekleyin:
```bash
# Daily backup
tar -czf sessions_backup_$(date +%Y%m%d).tar.gz sessions/
```

## Monitoring

Session dosyalarını kontrol etmek için:
```bash
# Kaç session var?
ls sessions/ | wc -l

# Toplam boyut
du -sh sessions/

# En son değiştirilen
ls -lht sessions/ | head
```

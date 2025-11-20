# 🚀 Megapazar Agent API

AI-powered listing and search platform backend using LangGraph and OpenAI.

## 📋 Özellikler

- ✅ **Akıllı Fotoğraf Analizi** - GPT-4o Vision ile ürün tanıma
- ✅ **Otomatik İlan Yazımı** - Profesyonel ilan metinleri
- ✅ **Fiyat Önerisi** - İç+dış piyasa analizi
- ✅ **Vector Search** - Benzer ürün bulma
- ✅ **Multi-Agent Orkestrasyon** - LangGraph ile agent yönetimi

## 🏗️ Mimari

```
megapazar-agent-api/
├── agents/              # AI Agent'lar
├── workflows/           # LangGraph workflow'ları
├── models/              # Pydantic modeller
├── utils/               # Yardımcı fonksiyonlar
├── main.py              # FastAPI uygulaması
└── config.py            # Yapılandırma
```

## 🚀 Kurulum

### 1. Virtual Environment Oluştur

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 3. Environment Değişkenlerini Ayarla

```bash
# .env.example'ı kopyala
copy .env.example .env

# .env dosyasını düzenle ve API key'leri ekle
```

**.env dosyası:**
```env
OPENAI_API_KEY=sk-proj-xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGci...
SUPABASE_SERVICE_KEY=eyJhbGci...
```

### 4. Çalıştır

```bash
python main.py
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

## 📡 API Endpoints

### POST /api/listing/start

İlan verme akışını başlat.

**Request:**
```json
{
  "user_id": "user-123",
  "message": "4 adet endüstriyel rotor satmak istiyorum",
  "image_url": "https://example.com/image.jpg",
  "platform": "web",
  "user_location": "İstanbul, Türkiye"
}
```

**Response:**
```json
{
  "type": "listing_preview",
  "message": "✅ İlanınız hazır!\n\n📋 **Endüstriyel Rotor...**",
  "data": {
    "title": "...",
    "description": "...",
    "price": 2750
  },
  "next_action": "await_user_input"
}
```

### POST /api/listing/confirm

İlanı onayla ve Supabase'e kaydet.

### POST /api/search

Ürün ara (TODO).

### GET /health

Sağlık kontrolü.

## 🤖 Agent'lar

| Agent | Görev |
|-------|-------|
| **ConversationAgent** | Kullanıcı ile konuşma, niyet tespiti |
| **ListingCoordinator** | İlan akışını orkestre etme |
| **VisionAgent** | Fotoğraf analizi (GPT-4o Vision) |
| **TextParserAgent** | Metin'den ürün çıkarma |
| **ProductMatchAgent** | Supabase'de benzer ürün arama |
| **MarketSearchAgent** | Web'de fiyat araştırması |
| **PricingAgent** | Fiyat hesaplama |
| **ListingWriterAgent** | İlan metni yazma |

## 🧪 Test

### cURL ile Test

```bash
curl -X POST http://localhost:8000/api/listing/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-123",
    "message": "4 adet endüstriyel rotor gövdesi satmak istiyorum",
    "platform": "web"
  }'
```

### Python ile Test

```python
import requests

response = requests.post(
    "http://localhost:8000/api/listing/start",
    json={
        "user_id": "test-123",
        "message": "iPhone 13 satmak istiyorum",
        "platform": "web"
    }
)

print(response.json())
```

## 🔧 Geliştirme

### Yeni Agent Ekleme

1. `agents/` klasöründe yeni agent dosyası oluştur
2. `BaseAgent` class'ını inherit et
3. `__call__` metodunu implement et
4. `workflows/listing_flow.py`'a ekle

### Log'ları Görüntüleme

Log'lar console'a yazdırılır. Her agent kendi log'larını üretir.

```
2025-11-15 23:45:12 - ConversationAgent - INFO - [ConversationAgent] Processing message: 4 adet endüstriyel...
2025-11-15 23:45:15 - VisionAgent - INFO - [VisionAgent] Product identified: Rotor Gövdesi
```

## 📦 Deployment

### Railway

1. GitHub'a push et
2. Railway → New Project → Deploy from GitHub
3. Environment variables ekle
4. Deploy!

### Docker (TODO)

```bash
docker build -t megapazar-agent-api .
docker run -p 8000:8000 megapazar-agent-api
```

## 🐛 Sorun Giderme

### `ModuleNotFoundError: No module named 'langgraph'`

```bash
pip install --upgrade langchain langgraph
```

### `Supabase connection error`

`.env` dosyasındaki `SUPABASE_URL` ve `SUPABASE_KEY` değerlerini kontrol edin.

### `OpenAI API key error`

`.env` dosyasındaki `OPENAI_API_KEY` değerini kontrol edin.

## 📚 Daha Fazla Bilgi

- [MEGAPAZAR-MASTER-PLAN.md](../MEGAPAZAR-MASTER-PLAN.md) - Tam dokümantasyon
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Docs](https://platform.openai.com/docs)

## 📄 Lisans

MIT License - Megapazar 2025

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

---

**Made with ❤️ for Megapazar**

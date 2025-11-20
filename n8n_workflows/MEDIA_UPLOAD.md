# n8n WhatsApp - Media Upload Handler

Bu workflow, WhatsApp'tan gelen fotoğrafları işler ve backend API'ye gönderir.

## İşleyiş

1. **Fotoğraf Gelir**: Kullanıcı WhatsApp'tan fotoğraf gönderir
2. **Download**: Twilio'dan fotoğraf URL'si alınır ve n8n ile download edilir
3. **Base64 Encode**: Fotoğraf base64'e çevrilir
4. **Backend'e Gönder**: `/conversation` endpoint'ine image_data olarak gönderilir
5. **Vision Agent**: Backend'de Vision Agent fotoğrafı analiz eder
6. **Supabase Upload**: Storage'a yüklenir
7. **Cevap**: Kullanıcıya analiz sonucu gönderilir

## Twilio Media URL Format

```json
{
  "From": "whatsapp:+905551234567",
  "Body": "",
  "NumMedia": "1",
  "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/ACxxx/Messages/MMxxx/Media/MExxx",
  "MediaContentType0": "image/jpeg"
}
```

## n8n Implementation

### Node 1: Download Image from Twilio

```javascript
// HTTP Request node
const mediaUrl = $json.MediaUrl0;
const authToken = $env.TWILIO_AUTH_TOKEN;
const accountSid = $env.TWILIO_ACCOUNT_SID;

return {
  url: mediaUrl,
  method: 'GET',
  auth: {
    user: accountSid,
    password: authToken
  },
  responseType: 'arraybuffer'
};
```

### Node 2: Convert to Base64

```javascript
// Code node
const buffer = Buffer.from($binary.data.data);
const base64 = buffer.toString('base64');
const mimeType = $json.MediaContentType0 || 'image/jpeg';

return {
  json: {
    image_data: `data:${mimeType};base64,${base64}`,
    phoneNumber: $json.From.replace('whatsapp:', ''),
    hasImage: true
  }
};
```

### Node 3: Send to Backend

```javascript
// HTTP Request to /conversation
POST http://localhost:8000/conversation

Body:
{
  "user_id": "{{ $json.phoneNumber }}",
  "message": "fotoğraf gönderiyorum",
  "image_data": "{{ $json.image_data }}"
}
```

## Backend API Response

```json
{
  "response": "Gördüm! Bu bir rotor. Fiyatı ne olacak?",
  "vision_analysis": {
    "detected_product": "rotor",
    "condition": "used",
    "confidence": 0.85
  },
  "session_id": "abc-123"
}
```

## Örnek Akış

```
User: [fotoğraf gönderir - rotor]

n8n:
1. Twilio'dan fotoğrafı indir
2. Base64'e çevir
3. Backend'e gönder

Backend (Vision Agent):
1. GPT-4o Vision ile analiz et
2. "Bu bir rotor, ikinci el görünüyor"
3. Session'a kaydet

Bot: "Gördüm! Rotor satmak istiyorsun. 
      İkinci el görünüyor. Kaç TL olacak?"
```

## Error Handling

### Media Download Hatası

```javascript
if (!$json.MediaUrl0) {
  return {
    error: true,
    message: 'Fotoğraf bulunamadı'
  };
}
```

### Invalid Image Format

```javascript
const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
if (!validTypes.includes($json.MediaContentType0)) {
  return {
    error: true,
    message: 'Sadece JPG, PNG, WEBP formatları destekleniyor'
  };
}
```

### File Size Limit

```javascript
const maxSize = 5 * 1024 * 1024; // 5MB
if (buffer.length > maxSize) {
  return {
    error: true,
    message: 'Fotoğraf çok büyük (max 5MB)'
  };
}
```

## Supabase Storage

Backend'de `storage_helper.py` kullanılarak:

```python
# 1. Upload to Supabase Storage
image_url = await upload_to_storage(
    image_data=image_data,
    bucket='product-images',
    folder='listings'
)

# 2. Save to listing
listing.image_url = image_url
```

## Test

### Manuel Test (curl)

```bash
# 1. Base64 encode local image
base64 -i rotor.jpg -o rotor_base64.txt

# 2. Send to backend
curl -X POST http://localhost:8000/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "message": "fotoğraf",
    "image_data": "data:image/jpeg;base64,..."
  }'
```

### n8n Test

1. Webhook node'una POST request at
2. Body'de `MediaUrl0` ekle (Twilio formatında)
3. Execute workflow
4. Check output

## Performance

- **Download**: ~500ms
- **Base64 Encode**: ~100ms
- **Backend Upload**: ~1s
- **Total**: ~1.5s

Kullanıcıya "Fotoğraf işleniyor..." mesajı göster.

## Optimization

### 1. Resim Boyutunu Küçült

```javascript
// Sharp.js kullan (n8n'de mevcut değil, backend'de yap)
const sharp = require('sharp');
const resized = await sharp(buffer)
  .resize(800, 800, { fit: 'inside' })
  .jpeg({ quality: 80 })
  .toBuffer();
```

### 2. Lazy Upload

- Önce analiz et (GPT-4o Vision)
- İlan yayınlanırsa upload et
- Draft ise beklet

### 3. CDN

- Supabase Storage public URL kullan
- CloudFlare CDN ekle
- Hızlı image serving

## Notlar

- Twilio, medya dosyalarını 5 gün tutar
- n8n'de binary data 10MB'a kadar destekleniyor
- GPT-4o Vision, 20MB'a kadar image kabul ediyor

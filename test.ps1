# Test Script - Megapazar Agent API'yi test et

Write-Host "🧪 Megapazar Agent API Test Başlıyor..." -ForegroundColor Cyan
Write-Host ""

# API çalışıyor mu kontrol et
Write-Host "📡 API bağlantısı kontrol ediliyor..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "   ✅ API çalışıyor!" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "   ❌ API'ye bağlanılamadı!" -ForegroundColor Red
    Write-Host "   Önce 'python main.py' komutu ile API'yi başlatın." -ForegroundColor Yellow
    Write-Host ""
    exit
}

# Test 1: Metin ile ilan verme
Write-Host "📝 Test 1: Metin ile ilan verme..." -ForegroundColor Yellow
$body = @{
    user_id = "test-user-123"
    message = "4 adet endüstriyel rotor gövdesi satmak istiyorum, ikinci el, çalışır durumda"
    platform = "web"
    user_location = "İstanbul, Türkiye"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/listing/start" `
        -Method Post `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "   ✅ Test başarılı!" -ForegroundColor Green
    Write-Host "   Response Type: $($response.type)" -ForegroundColor Cyan
    Write-Host "   Message Preview:" -ForegroundColor Cyan
    Write-Host "   $($response.message.Substring(0, [Math]::Min(200, $response.message.Length)))..." -ForegroundColor White
    Write-Host ""
    
    if ($response.data) {
        Write-Host "   📋 İlan Bilgileri:" -ForegroundColor Cyan
        Write-Host "      Başlık: $($response.data.title)" -ForegroundColor White
        Write-Host "      Fiyat: $($response.data.price) TL" -ForegroundColor White
        Write-Host "      Kategori: $($response.data.category)" -ForegroundColor White
        Write-Host ""
    }
} catch {
    Write-Host "   ❌ Test başarısız!" -ForegroundColor Red
    Write-Host "   Hata: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 2: Farklı bir ürün
Write-Host "📝 Test 2: Elektronik ürün..." -ForegroundColor Yellow
$body2 = @{
    user_id = "test-user-456"
    message = "iPhone 13 Pro Max satıyorum, 256GB, çok temiz"
    platform = "web"
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/listing/start" `
        -Method Post `
        -Body $body2 `
        -ContentType "application/json"
    
    Write-Host "   ✅ Test başarılı!" -ForegroundColor Green
    Write-Host "   Response Type: $($response2.type)" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "   ❌ Test başarısız!" -ForegroundColor Red
    Write-Host ""
}

Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Testler Tamamlandı!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Daha detaylı test için:" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

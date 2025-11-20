# Megapazar Agent API - Quick Start Script
# Bu script projeyi hızlıca kurup çalıştırmanızı sağlar

Write-Host "🚀 Megapazar Agent API - Kurulum Başlıyor..." -ForegroundColor Cyan
Write-Host ""

# 1. Python versiyonu kontrol
Write-Host "📍 Python versiyonu kontrol ediliyor..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "   $pythonVersion" -ForegroundColor Green
Write-Host ""

# 2. Virtual environment oluştur
Write-Host "📦 Virtual environment oluşturuluyor..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ⚠️  venv klasörü zaten var, atlanıyor..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "   ✅ Virtual environment oluşturuldu" -ForegroundColor Green
}
Write-Host ""

# 3. Virtual environment aktifleştir
Write-Host "🔌 Virtual environment aktifleştiriliyor..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "   ✅ Virtual environment aktif" -ForegroundColor Green
Write-Host ""

# 4. Bağımlılıkları yükle
Write-Host "📥 Bağımlılıklar yükleniyor (bu biraz sürebilir)..." -ForegroundColor Yellow
pip install --upgrade pip > $null 2>&1
pip install -r requirements.txt
Write-Host "   ✅ Bağımlılıklar yüklendi" -ForegroundColor Green
Write-Host ""

# 5. .env dosyası kontrol
Write-Host "⚙️  Environment dosyası kontrol ediliyor..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✅ .env dosyası mevcut" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  .env dosyası bulunamadı!" -ForegroundColor Red
    Write-Host "   📝 .env.example dosyasını .env olarak kopyalayıp düzenleyin:" -ForegroundColor Yellow
    Write-Host "      copy .env.example .env" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Gerekli değişkenler:" -ForegroundColor Yellow
    Write-Host "      - OPENAI_API_KEY" -ForegroundColor Cyan
    Write-Host "      - SUPABASE_URL" -ForegroundColor Cyan
    Write-Host "      - SUPABASE_KEY" -ForegroundColor Cyan
    Write-Host "      - SUPABASE_SERVICE_KEY" -ForegroundColor Cyan
    Write-Host ""
}

# 6. Özet
Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Kurulum Tamamlandı!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Sonraki Adımlar:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. .env dosyasını düzenle (API key'leri ekle):" -ForegroundColor Yellow
Write-Host "   notepad .env" -ForegroundColor White
Write-Host ""
Write-Host "2. Uygulamayı başlat:" -ForegroundColor Yellow
Write-Host "   python main.py" -ForegroundColor White
Write-Host ""
Write-Host "3. API dokümantasyonunu görüntüle:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "4. Test et:" -ForegroundColor Yellow
Write-Host "   curl -X POST http://localhost:8000/api/listing/start \" -ForegroundColor White
Write-Host "     -H 'Content-Type: application/json' \" -ForegroundColor White
Write-Host "     -d '{""user_id"":""test-123"",""message"":""rotor satmak istiyorum"",""platform"":""web""}'" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

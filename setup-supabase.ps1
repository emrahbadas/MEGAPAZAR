# Supabase Setup Script
# Bu script SQL şemasını Supabase'e yükler

Write-Host "🗄️  Megapazar Supabase Kurulumu Başlıyor..." -ForegroundColor Cyan
Write-Host ""

# SQL dosyasını kontrol et
if (-not (Test-Path "supabase-schema.sql")) {
    Write-Host "❌ supabase-schema.sql dosyası bulunamadı!" -ForegroundColor Red
    exit
}

Write-Host "📋 SQL şeması dosyası bulundu" -ForegroundColor Green
Write-Host ""

Write-Host "═══════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "📝 MANUEl ADIMLAR - Lütfen Takip Edin:" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Host "1️⃣  Supabase Dashboard'a gidin:" -ForegroundColor Cyan
Write-Host "   https://supabase.com/dashboard/project/snovwbffwvmkgjulrtsm" -ForegroundColor White
Write-Host ""

Write-Host "2️⃣  Sol menüden 'SQL Editor' seçin" -ForegroundColor Cyan
Write-Host ""

Write-Host "3️⃣  'New query' butonuna tıklayın" -ForegroundColor Cyan
Write-Host ""

Write-Host "4️⃣  supabase-schema.sql dosyasının içeriğini kopyalayıp yapıştırın" -ForegroundColor Cyan
Write-Host "   Dosya yolu: $PWD\supabase-schema.sql" -ForegroundColor White
Write-Host ""

Write-Host "5️⃣  'RUN' butonuna basın (veya Ctrl+Enter)" -ForegroundColor Cyan
Write-Host ""

Write-Host "6️⃣  Başarılı mesajını bekleyin:" -ForegroundColor Cyan
Write-Host "   ✅ Megapazar veritabanı başarıyla oluşturuldu!" -ForegroundColor Green
Write-Host ""

Write-Host "═══════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Host "📦 Oluşturulacak Tablolar:" -ForegroundColor Cyan
Write-Host "   • users                 (Kullanıcılar)" -ForegroundColor White
Write-Host "   • listings              (İlanlar)" -ForegroundColor White
Write-Host "   • product_embeddings    (Vector Search)" -ForegroundColor White
Write-Host "   • orders                (Siparişler)" -ForegroundColor White
Write-Host "   • conversations         (Konuşma Geçmişi)" -ForegroundColor White
Write-Host ""

Write-Host "🔧 Ekstra Özellikler:" -ForegroundColor Cyan
Write-Host "   • pgvector extension    (AI Vector Search)" -ForegroundColor White
Write-Host "   • match_products()      (Benzer ürün bulma fonksiyonu)" -ForegroundColor White
Write-Host "   • RLS Policies          (Güvenlik kuralları)" -ForegroundColor White
Write-Host "   • Auto-update triggers  (Otomatik zaman damgası)" -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "💡 Hızlı Erişim:" -ForegroundColor Yellow
Write-Host "   SQL dosyasını açmak için:" -ForegroundColor White
Write-Host "   notepad supabase-schema.sql" -ForegroundColor Cyan
Write-Host ""

Write-Host "   Supabase Dashboard'u açmak için:" -ForegroundColor White
Write-Host "   start https://supabase.com/dashboard/project/snovwbffwvmkgjulrtsm" -ForegroundColor Cyan
Write-Host ""

Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

$response = Read-Host "SQL'leri çalıştırdınız mı? (y/n)"

if ($response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "✅ Harika! Şimdi Storage yapılandırmasına geçelim..." -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 STORAGE BUCKET OLUŞTURMA:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Supabase Dashboard → Storage" -ForegroundColor White
    Write-Host "2. 'New bucket' butonuna tıklayın" -ForegroundColor White
    Write-Host "3. Bucket adı: product-images" -ForegroundColor Yellow
    Write-Host "4. Public bucket: ✅ (işaretli)" -ForegroundColor Yellow
    Write-Host "5. 'Create bucket' tıklayın" -ForegroundColor White
    Write-Host ""
    Write-Host "✅ Tamamlandı!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "👍 Tamam, önce SQL'leri çalıştırın, sonra tekrar bu scripti çalıştırın." -ForegroundColor Yellow
}

Write-Host ""

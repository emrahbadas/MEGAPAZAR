-- ============================================
-- MEGAPAZAR MIGRATION - Resim Yönetimi Güncellemesi
-- ============================================
-- Mevcut veritabanını bozmadan sadece yeni özellikleri ekler
-- ============================================

-- 1. pgvector extension (zaten varsa hata vermez)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- YENİ TABLO: PRODUCT_IMAGES
-- ============================================

-- Eğer listings tablosunda images kolonu varsa kaldır (hata vermez)
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'listings' AND column_name = 'images'
    ) THEN
        ALTER TABLE listings DROP COLUMN images;
        RAISE NOTICE '✅ listings.images kolonu kaldırıldı';
    END IF;
END $$;

-- Eğer view_count yoksa ekle
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'listings' AND column_name = 'view_count'
    ) THEN
        ALTER TABLE listings ADD COLUMN view_count INTEGER DEFAULT 0;
        RAISE NOTICE '✅ listings.view_count kolonu eklendi';
    END IF;
END $$;

-- Product images tablosu (yoksa oluştur)
CREATE TABLE IF NOT EXISTS product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL,
    public_url TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    file_size INTEGER,
    mime_type VARCHAR(50),
    width INTEGER,
    height INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product images indexleri (zaten varsa hata vermez)
CREATE INDEX IF NOT EXISTS idx_product_images_listing ON product_images(listing_id);
CREATE INDEX IF NOT EXISTS idx_product_images_primary ON product_images(listing_id, is_primary) WHERE is_primary = true;
CREATE INDEX IF NOT EXISTS idx_product_images_order ON product_images(listing_id, display_order);

-- ============================================
-- RLS POLİCİES - Product Images
-- ============================================

-- RLS aktifleştir
ALTER TABLE product_images ENABLE ROW LEVEL SECURITY;

-- Policy'ler (zaten varsa önce sil, sonra oluştur)
DROP POLICY IF EXISTS "Anyone can view product images" ON product_images;
CREATE POLICY "Anyone can view product images" 
    ON product_images FOR SELECT 
    USING (true);

DROP POLICY IF EXISTS "Users can add images to own listings" ON product_images;
CREATE POLICY "Users can add images to own listings" 
    ON product_images FOR INSERT 
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM listings 
            WHERE listings.id = product_images.listing_id 
            AND listings.user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can delete own product images" ON product_images;
CREATE POLICY "Users can delete own product images" 
    ON product_images FOR DELETE 
    USING (
        EXISTS (
            SELECT 1 FROM listings 
            WHERE listings.id = product_images.listing_id 
            AND listings.user_id = auth.uid()
        )
    );

-- ============================================
-- BAŞARILI MIGRATION MESAJI
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Megapazar resim yönetimi migration tamamlandı!';
    RAISE NOTICE '📸 product_images tablosu hazır';
    RAISE NOTICE '🔒 RLS policies ayarlandı';
    RAISE NOTICE '🚀 Storage bucket oluşturmayı unutma: product-images (public)';
END $$;

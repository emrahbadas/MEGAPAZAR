-- ============================================
-- MEGAPAZAR SUPABASE SQL ŞEMASI
-- ============================================
-- Bu dosyayı Supabase SQL Editor'da çalıştırın
-- ============================================

-- 1. pgvector extension'ı aktifleştir
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- TABLOLAR
-- ============================================

-- 1. USERS Tablosu
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(20) UNIQUE,
    name VARCHAR(100),
    email VARCHAR(255),
    location TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users indexleri
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

-- ============================================

-- 2. LISTINGS Tablosu
CREATE TABLE IF NOT EXISTS listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    category VARCHAR(50),
    price DECIMAL(10,2),
    stock INTEGER DEFAULT 1,
    location TEXT,
    status VARCHAR(20) DEFAULT 'active',
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Listings indexleri
CREATE INDEX IF NOT EXISTS idx_listings_user_id ON listings(user_id);
CREATE INDEX IF NOT EXISTS idx_listings_category ON listings(category);
CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status);
CREATE INDEX IF NOT EXISTS idx_listings_created_at ON listings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price);

-- ============================================

-- 2b. PRODUCT_IMAGES Tablosu (Resim yönetimi)
CREATE TABLE IF NOT EXISTS product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL, -- Supabase Storage'daki path
    public_url TEXT NOT NULL, -- Tam public URL
    is_primary BOOLEAN DEFAULT false, -- Ana resim mi?
    display_order INTEGER DEFAULT 0, -- Görüntüleme sırası
    file_size INTEGER, -- Bytes cinsinden
    mime_type VARCHAR(50), -- image/jpeg, image/png
    width INTEGER,
    height INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product images indexleri
CREATE INDEX IF NOT EXISTS idx_product_images_listing ON product_images(listing_id);
CREATE INDEX IF NOT EXISTS idx_product_images_primary ON product_images(listing_id, is_primary) WHERE is_primary = true;
CREATE INDEX IF NOT EXISTS idx_product_images_order ON product_images(listing_id, display_order);

-- ============================================

-- 3. PRODUCT_EMBEDDINGS Tablosu (Vector Search)
CREATE TABLE IF NOT EXISTS product_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product embeddings indexleri
CREATE INDEX IF NOT EXISTS idx_embeddings_listing ON product_embeddings(listing_id);

-- Vector similarity index (HNSW - daha hızlı)
CREATE INDEX IF NOT EXISTS idx_embeddings_vector_hnsw 
    ON product_embeddings 
    USING hnsw (embedding vector_cosine_ops);

-- ============================================

-- 4. ORDERS Tablosu
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id),
    buyer_id UUID REFERENCES users(id),
    seller_id UUID REFERENCES users(id),
    price DECIMAL(10,2),
    commission DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Orders indexleri
CREATE INDEX IF NOT EXISTS idx_orders_buyer ON orders(buyer_id);
CREATE INDEX IF NOT EXISTS idx_orders_seller ON orders(seller_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_listing ON orders(listing_id);

-- ============================================

-- 5. CONVERSATIONS Tablosu (WhatsApp/Web chat history)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    platform VARCHAR(20), -- 'whatsapp' or 'web'
    messages JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversations indexleri
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_platform ON conversations(platform);

-- ============================================
-- FONKSIYONLAR
-- ============================================

-- Vector Search Fonksiyonu
CREATE OR REPLACE FUNCTION match_products (
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id uuid,
    listing_id uuid,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        product_embeddings.id,
        product_embeddings.listing_id,
        1 - (product_embeddings.embedding <=> query_embedding) as similarity
    FROM product_embeddings
    WHERE 1 - (product_embeddings.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- ============================================
-- TRIGGERS (Otomatik updated_at güncellemesi)
-- ============================================

-- Updated_at trigger fonksiyonu
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Users tablosu için trigger
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Listings tablosu için trigger
DROP TRIGGER IF EXISTS update_listings_updated_at ON listings;
CREATE TRIGGER update_listings_updated_at 
    BEFORE UPDATE ON listings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Conversations tablosu için trigger
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLİCİES
-- ============================================

-- Users RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own data" 
    ON users FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY "Users can update own data" 
    ON users FOR UPDATE 
    USING (auth.uid() = id);

-- Listings RLS
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view active listings" 
    ON listings FOR SELECT 
    USING (status = 'active');

CREATE POLICY "Users can create own listings" 
    ON listings FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own listings" 
    ON listings FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own listings" 
    ON listings FOR DELETE 
    USING (auth.uid() = user_id);

-- Orders RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own orders" 
    ON orders FOR SELECT 
    USING (auth.uid() = buyer_id OR auth.uid() = seller_id);

-- Conversations RLS
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own conversations" 
    ON conversations FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own conversations" 
    ON conversations FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

-- Product Images RLS
ALTER TABLE product_images ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view product images" 
    ON product_images FOR SELECT 
    USING (true);

CREATE POLICY "Users can add images to own listings" 
    ON product_images FOR INSERT 
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM listings 
            WHERE listings.id = product_images.listing_id 
            AND listings.user_id = auth.uid()
        )
    );

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
-- TEST DATA (Opsiyonel - Development için)
-- ============================================

-- Test kullanıcısı
INSERT INTO users (id, phone, name, email, location) 
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    '+905551234567',
    'Test Kullanıcı',
    'test@megapazar.com',
    'İstanbul, Türkiye'
) ON CONFLICT (phone) DO NOTHING;

-- Test ilanı
INSERT INTO listings (user_id, title, description, category, price, stock, location, status) 
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Endüstriyel Rotor Gövdesi - 4 Adet',
    'Karbon alaşımlı, ikinci el ama çalışır durumda endüstriyel rotor gövdeleri. Fabrika çıkışlı, bakımlı.',
    'Endüstriyel Malzemeler',
    2750.00,
    4,
    'İstanbul, Türkiye',
    'active'
) ON CONFLICT DO NOTHING;

-- Test resmi (örnek - gerçek bucket'tan çekilecek)
INSERT INTO product_images (listing_id, storage_path, public_url, is_primary, display_order)
SELECT 
    id,
    'product-images/test/rotor-1.jpg',
    'https://snovwbffwvmkgjulrtsm.supabase.co/storage/v1/object/public/product-images/test/rotor-1.jpg',
    true,
    1
FROM listings 
WHERE title LIKE 'Endüstriyel Rotor%'
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================
-- BAŞARILI KURULUM MESAJI
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Megapazar veritabanı başarıyla oluşturuldu!';
    RAISE NOTICE '📊 Tablolar: users, listings, product_embeddings, orders, conversations';
    RAISE NOTICE '🔍 Vector search fonksiyonu: match_products()';
    RAISE NOTICE '🔒 Row Level Security aktif';
    RAISE NOTICE '🚀 Test kullanıcısı ve ilanı eklendi';
END $$;

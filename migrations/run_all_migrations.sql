-- ========================================
-- MEGAPAZAR MIGRATIONS
-- Run these in Supabase Dashboard → SQL Editor
-- ========================================

-- MIGRATION 1: Add order fields
-- ========================================
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS seller_receives DECIMAL(10,2);

COMMENT ON COLUMN orders.quantity IS 'Sipariş adedi';
COMMENT ON COLUMN orders.seller_receives IS 'Satıcıya gidecek miktar (komisyon düşülmüş)';

-- MIGRATION 1.5: Add missing listing fields
-- ========================================
ALTER TABLE listings
ADD COLUMN IF NOT EXISTS condition VARCHAR(20) DEFAULT 'new' CHECK (condition IN ('new', 'used', 'refurbished')),
ADD COLUMN IF NOT EXISTS image_url TEXT,
ADD COLUMN IF NOT EXISTS stock INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS location VARCHAR(100);

COMMENT ON COLUMN listings.condition IS 'Ürün durumu: new, used, refurbished';
COMMENT ON COLUMN listings.image_url IS 'Ürün görseli URL';
COMMENT ON COLUMN listings.stock IS 'Stok adedi';
COMMENT ON COLUMN listings.location IS 'Ürün konumu/şehir';

-- MIGRATION 2: Create vector search function
-- ========================================
CREATE OR REPLACE FUNCTION match_products(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 50
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
    ORDER BY product_embeddings.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION match_products IS 'Performs vector similarity search on product embeddings using cosine distance';

-- ========================================
-- Verify migrations
-- ========================================
SELECT 
    'orders.quantity' as column_name,
    EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='orders' AND column_name='quantity'
    ) as exists;

SELECT 
    'match_products' as function_name,
    EXISTS (
        SELECT 1 
        FROM pg_proc 
        WHERE proname='match_products'
    ) as exists;

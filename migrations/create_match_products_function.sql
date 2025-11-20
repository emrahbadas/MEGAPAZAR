-- Create vector search function for product embeddings
-- This function performs cosine similarity search on product embeddings

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

-- Add comment
COMMENT ON FUNCTION match_products IS 'Performs vector similarity search on product embeddings using cosine distance';

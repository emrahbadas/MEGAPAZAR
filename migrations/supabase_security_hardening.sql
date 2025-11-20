-- ========================================
-- SUPABASE SECURITY HARDENING
-- Storage Buckets & RLS Policies
-- ========================================

-- ===========================================
-- PART 1: STORAGE BUCKETS
-- ===========================================
-- Note: Create these in Supabase Dashboard → Storage
-- Bucket 1: product-images (public, for product photos)
-- Bucket 2: user-documents (private, for user verification docs)

-- Alternative: Create via SQL (requires storage extension)
-- INSERT INTO storage.buckets (id, name, public) VALUES 
-- ('product-images', 'product-images', true),
-- ('user-documents', 'user-documents', false);


-- ===========================================
-- PART 2: ENABLE RLS ON ALL TABLES
-- ===========================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_embeddings ENABLE ROW LEVEL SECURITY;


-- ===========================================
-- PART 3: LISTINGS TABLE RLS POLICIES
-- ===========================================

-- Drop existing policies first
DROP POLICY IF EXISTS "Anyone can view active listings" ON listings;
DROP POLICY IF EXISTS "Users can view their own listings" ON listings;
DROP POLICY IF EXISTS "Users can create their own listings" ON listings;
DROP POLICY IF EXISTS "Users can update their own listings" ON listings;
DROP POLICY IF EXISTS "Users can delete their own listings" ON listings;
DROP POLICY IF EXISTS "Service role full access to listings" ON listings;

-- Policy: Anyone can view active listings
CREATE POLICY "Anyone can view active listings"
ON listings FOR SELECT
USING (status = 'active');

-- Policy: Users can view all their own listings (any status)
CREATE POLICY "Users can view their own listings"
ON listings FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can insert their own listings
CREATE POLICY "Users can create their own listings"
ON listings FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own listings
CREATE POLICY "Users can update their own listings"
ON listings FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own listings
CREATE POLICY "Users can delete their own listings"
ON listings FOR DELETE
USING (auth.uid() = user_id);

-- Policy: Service role bypass for background jobs
CREATE POLICY "Service role full access to listings"
ON listings FOR ALL
TO service_role
USING (true)
WITH CHECK (true);


-- ===========================================
-- PART 4: ORDERS TABLE RLS POLICIES
-- ===========================================

-- Drop existing policies first
DROP POLICY IF EXISTS "Users can view orders as buyer" ON orders;
DROP POLICY IF EXISTS "Users can view orders as seller" ON orders;
DROP POLICY IF EXISTS "Users can create orders" ON orders;
DROP POLICY IF EXISTS "Sellers can update order status" ON orders;
DROP POLICY IF EXISTS "Service role full access to orders" ON orders;

-- Policy: Users can view orders where they are buyer
CREATE POLICY "Users can view orders as buyer"
ON orders FOR SELECT
USING (auth.uid() = buyer_id);

-- Policy: Users can view orders where they are seller
CREATE POLICY "Users can view orders as seller"
ON orders FOR SELECT
USING (
    auth.uid() IN (
        SELECT user_id FROM listings WHERE id = orders.listing_id
    )
);

-- Policy: Users can create orders as buyer
CREATE POLICY "Users can create orders"
ON orders FOR INSERT
WITH CHECK (auth.uid() = buyer_id);

-- Policy: Only seller can update order status
CREATE POLICY "Sellers can update order status"
ON orders FOR UPDATE
USING (
    auth.uid() IN (
        SELECT user_id FROM listings WHERE id = orders.listing_id
    )
);

-- Policy: Service role full access to orders
CREATE POLICY "Service role full access to orders"
ON orders FOR ALL
TO service_role
USING (true)
WITH CHECK (true);


-- ===========================================
-- PART 5: NOTIFICATIONS TABLE RLS POLICIES
-- ===========================================

-- Drop existing policies first
DROP POLICY IF EXISTS "Users can view their own notifications" ON notifications;
DROP POLICY IF EXISTS "Users can update their own notifications" ON notifications;
DROP POLICY IF EXISTS "Service role can create notifications" ON notifications;
DROP POLICY IF EXISTS "Service role full access to notifications" ON notifications;

-- Policy: Users can only view their own notifications
CREATE POLICY "Users can view their own notifications"
ON notifications FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can mark their notifications as read
CREATE POLICY "Users can update their own notifications"
ON notifications FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Policy: Service role can create notifications for any user
CREATE POLICY "Service role can create notifications"
ON notifications FOR INSERT
TO service_role
WITH CHECK (true);

-- Policy: Service role full access
CREATE POLICY "Service role full access to notifications"
ON notifications FOR ALL
TO service_role
USING (true)
WITH CHECK (true);


-- ===========================================
-- PART 6: CONVERSATIONS TABLE RLS POLICIES
-- ===========================================

-- Drop existing policies first
DROP POLICY IF EXISTS "Users can view their own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can create their own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can update their own conversations" ON conversations;
DROP POLICY IF EXISTS "Service role full access to conversations" ON conversations;

-- Policy: Users can view their own conversations
CREATE POLICY "Users can view their own conversations"
ON conversations FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can create their own conversations
CREATE POLICY "Users can create their own conversations"
ON conversations FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own conversations
CREATE POLICY "Users can update their own conversations"
ON conversations FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Policy: Service role full access for session management
CREATE POLICY "Service role full access to conversations"
ON conversations FOR ALL
TO service_role
USING (true)
WITH CHECK (true);


-- ===========================================
-- PART 7: USERS TABLE RLS POLICIES
-- ===========================================

-- Drop existing policies first
DROP POLICY IF EXISTS "Anyone can view user profiles" ON users;
DROP POLICY IF EXISTS "Users can update their own profile" ON users;
DROP POLICY IF EXISTS "Service role full access to users" ON users;

-- Policy: Users can view all public user profiles
CREATE POLICY "Anyone can view user profiles"
ON users FOR SELECT
USING (true);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update their own profile"
ON users FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Policy: Service role full access
CREATE POLICY "Service role full access to users"
ON users FOR ALL
TO service_role
USING (true)
WITH CHECK (true);


-- ===========================================
-- PART 8: PRODUCT_EMBEDDINGS TABLE RLS POLICIES
-- ===========================================

-- Drop existing policies first
DROP POLICY IF EXISTS "Anyone can read embeddings" ON product_embeddings;
DROP POLICY IF EXISTS "Service role full access to embeddings" ON product_embeddings;

-- Policy: Anyone can read embeddings (for search)
CREATE POLICY "Anyone can read embeddings"
ON product_embeddings FOR SELECT
USING (true);

-- Policy: Service role full access (embeddings created by backend)
CREATE POLICY "Service role full access to embeddings"
ON product_embeddings FOR ALL
TO service_role
USING (true)
WITH CHECK (true);


-- ===========================================
-- PART 9: STORAGE POLICIES (if using SQL)
-- ===========================================

-- Product Images Bucket Policies (public read, authenticated upload)
-- CREATE POLICY "Anyone can view product images"
-- ON storage.objects FOR SELECT
-- USING (bucket_id = 'product-images');

-- CREATE POLICY "Authenticated users can upload product images"
-- ON storage.objects FOR INSERT
-- WITH CHECK (
--     bucket_id = 'product-images' 
--     AND auth.role() = 'authenticated'
-- );

-- CREATE POLICY "Users can update their product images"
-- ON storage.objects FOR UPDATE
-- USING (bucket_id = 'product-images' AND auth.uid() = owner);

-- CREATE POLICY "Users can delete their product images"
-- ON storage.objects FOR DELETE
-- USING (bucket_id = 'product-images' AND auth.uid() = owner);


-- User Documents Bucket Policies (private, owner only)
-- CREATE POLICY "Users can view their own documents"
-- ON storage.objects FOR SELECT
-- USING (bucket_id = 'user-documents' AND auth.uid() = owner);

-- CREATE POLICY "Users can upload their own documents"
-- ON storage.objects FOR INSERT
-- WITH CHECK (bucket_id = 'user-documents' AND auth.uid() = owner);

-- CREATE POLICY "Users can update their own documents"
-- ON storage.objects FOR UPDATE
-- USING (bucket_id = 'user-documents' AND auth.uid() = owner);

-- CREATE POLICY "Users can delete their own documents"
-- ON storage.objects FOR DELETE
-- USING (bucket_id = 'user-documents' AND auth.uid() = owner);


-- ===========================================
-- VERIFICATION QUERIES
-- ===========================================

-- Check enabled RLS
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'listings', 'orders', 'notifications', 'conversations', 'product_embeddings');

-- List all policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Count policies per table
SELECT tablename, COUNT(*) as policy_count
FROM pg_policies
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY tablename;

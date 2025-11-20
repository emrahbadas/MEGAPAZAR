-- ========================================
-- CLEANUP: Remove existing RLS policies
-- Run this BEFORE running the main hardening script
-- ========================================

-- Drop all existing policies on listings
DROP POLICY IF EXISTS "Anyone can view active listings" ON listings;
DROP POLICY IF EXISTS "Users can view their own listings" ON listings;
DROP POLICY IF EXISTS "Users can create their own listings" ON listings;
DROP POLICY IF EXISTS "Users can update their own listings" ON listings;
DROP POLICY IF EXISTS "Users can delete their own listings" ON listings;
DROP POLICY IF EXISTS "Service role full access to listings" ON listings;

-- Drop all existing policies on orders
DROP POLICY IF EXISTS "Users can view orders as buyer" ON orders;
DROP POLICY IF EXISTS "Users can view orders as seller" ON orders;
DROP POLICY IF EXISTS "Users can create orders" ON orders;
DROP POLICY IF EXISTS "Sellers can update order status" ON orders;
DROP POLICY IF EXISTS "Service role full access to orders" ON orders;

-- Drop all existing policies on notifications
DROP POLICY IF EXISTS "Users can view their own notifications" ON notifications;
DROP POLICY IF EXISTS "Users can update their own notifications" ON notifications;
DROP POLICY IF EXISTS "Service role can create notifications" ON notifications;
DROP POLICY IF EXISTS "Service role full access to notifications" ON notifications;

-- Drop all existing policies on conversations
DROP POLICY IF EXISTS "Users can view their own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can create their own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can update their own conversations" ON conversations;
DROP POLICY IF EXISTS "Service role full access to conversations" ON conversations;

-- Drop all existing policies on users
DROP POLICY IF EXISTS "Anyone can view user profiles" ON users;
DROP POLICY IF EXISTS "Users can update their own profile" ON users;
DROP POLICY IF EXISTS "Service role full access to users" ON users;

-- Drop all existing policies on product_embeddings
DROP POLICY IF EXISTS "Anyone can read embeddings" ON product_embeddings;
DROP POLICY IF EXISTS "Service role full access to embeddings" ON product_embeddings;

-- Verification: Show remaining policies
SELECT tablename, policyname
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Migration: Add market price tracking and notifications
-- Date: 2025-11-17

-- 1. Add market_price_at_publish column to listings table
ALTER TABLE listings 
ADD COLUMN IF NOT EXISTS market_price_at_publish DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS last_price_check_at TIMESTAMP;

COMMENT ON COLUMN listings.market_price_at_publish IS 'Piyasa fiyatı (PricingAgent web search ile bulundu)';
COMMENT ON COLUMN listings.last_price_check_at IS 'Son fiyat kontrolü zamanı (background job)';

-- 2. Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'price_alert', 'info', 'warning'
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB, -- Extra data: old_price, new_price, difference_percent
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_listing_id ON notifications(listing_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);

COMMENT ON TABLE notifications IS 'Kullanıcı bildirimleri - fiyat uyarıları, sistem mesajları';

-- 3. Create function to clean old notifications (90 days)
CREATE OR REPLACE FUNCTION cleanup_old_notifications()
RETURNS void AS $$
BEGIN
    DELETE FROM notifications 
    WHERE created_at < NOW() - INTERVAL '90 days' 
    AND is_read = true;
END;
$$ LANGUAGE plpgsql;

-- Example usage:
-- SELECT cleanup_old_notifications();

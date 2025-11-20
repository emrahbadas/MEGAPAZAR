-- Add seller_receives and quantity columns to orders table

ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS seller_receives DECIMAL(10,2);

COMMENT ON COLUMN orders.quantity IS 'Sipariş adedi';
COMMENT ON COLUMN orders.seller_receives IS 'Satıcıya gidecek miktar (komisyon düşülmüş)';

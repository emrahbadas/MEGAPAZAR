"""
Run Supabase migration for price monitoring
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("Running migration: add_market_price_and_notifications")
print("=" * 60)

# Step 1: Add columns to listings table
print("\n1. Adding columns to listings table...")
try:
    # Note: Supabase Python client doesn't support ALTER TABLE directly
    # Run this SQL in Supabase SQL Editor instead
    sql_file = "migrations/add_market_price_and_notifications.sql"
    print(f"   ⚠️  Please run the SQL file manually in Supabase SQL Editor:")
    print(f"   📁 {sql_file}")
    print(f"   OR use the following commands:\n")
    
    print("   ALTER TABLE listings ADD COLUMN IF NOT EXISTS market_price_at_publish DECIMAL(10,2);")
    print("   ALTER TABLE listings ADD COLUMN IF NOT EXISTS last_price_check_at TIMESTAMP;\n")
    
    print("   ✅ Create notifications table (see migration file)")
    
    print("\n   After running SQL, press Enter to continue...")
    input()
    
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("Migration instructions provided")
print("\nNext steps:")
print("1. Run SQL in Supabase SQL Editor")
print("2. Restart API: uvicorn main:app --reload")
print("3. Run test: python test_price_monitoring.py")

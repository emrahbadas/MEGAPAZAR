"""
Price Monitor Background Job
Checks market prices for active listings and creates alerts if price difference > ±20%
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from supabase import create_client
from agents.pricing import PricingAgent
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger("price_monitor")

class PriceMonitor:
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        self.pricing_agent = PricingAgent()
        self.threshold_percent = 20  # ±20%
    
    def check_all_active_listings(self):
        """Check all active listings for price changes"""
        logger.info("🔍 Starting price check for all active listings...")
        
        try:
            # Get all active listings
            response = self.supabase.table("listings")\
                .select("id, user_id, title, category, price, market_price_at_publish, last_price_check_at")\
                .eq("status", "active")\
                .execute()
            
            listings = response.data
            logger.info(f"Found {len(listings)} active listings to check")
            
            alerts_created = 0
            for listing in listings:
                try:
                    if self._should_check_listing(listing):
                        alert_created = self._check_listing_price(listing)
                        if alert_created:
                            alerts_created += 1
                except Exception as e:
                    logger.error(f"Error checking listing {listing['id']}: {e}")
                    continue
            
            logger.info(f"✅ Price check completed. Created {alerts_created} alerts")
            return {"checked": len(listings), "alerts_created": alerts_created}
        
        except Exception as e:
            logger.error(f"Error in check_all_active_listings: {e}")
            return {"error": str(e)}
    
    def _should_check_listing(self, listing: Dict) -> bool:
        """Check if listing should be checked (not checked in last 24h)"""
        last_check = listing.get("last_price_check_at")
        
        if not last_check:
            return True  # Never checked
        
        # Parse last check time
        last_check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
        now = datetime.now(last_check_time.tzinfo)
        
        # Check if 24 hours passed
        return (now - last_check_time) > timedelta(hours=24)
    
    def _check_listing_price(self, listing: Dict) -> bool:
        """Check single listing price and create alert if needed"""
        listing_id = listing["id"]
        user_id = listing["user_id"]
        title = listing["title"]
        category = listing["category"]
        current_user_price = float(listing["price"])
        old_market_price = listing.get("market_price_at_publish")
        
        logger.info(f"Checking: {title} (User: {current_user_price} TL)")
        
        # Get new market price via PricingAgent
        new_market_price = self.pricing_agent.get_market_price(title, category)
        
        if not new_market_price or new_market_price == 0:
            logger.warning(f"Could not get market price for {listing_id}")
            return False
        
        # Calculate difference
        difference_percent = ((current_user_price - new_market_price) / new_market_price) * 100
        
        logger.info(f"   Market price: {new_market_price} TL (Difference: {difference_percent:+.1f}%)")
        
        # Update last_price_check_at
        self.supabase.table("listings")\
            .update({"last_price_check_at": datetime.now().isoformat()})\
            .eq("id", listing_id)\
            .execute()
        
        # Check if alert needed
        if abs(difference_percent) > self.threshold_percent:
            self._create_price_alert(
                user_id=user_id,
                listing_id=listing_id,
                title=title,
                user_price=current_user_price,
                market_price=new_market_price,
                difference_percent=difference_percent
            )
            return True
        
        return False
    
    def _create_price_alert(
        self, 
        user_id: str, 
        listing_id: str,
        title: str,
        user_price: float,
        market_price: float,
        difference_percent: float
    ):
        """Create price alert notification"""
        
        # Determine message
        if difference_percent > 0:
            alert_type = "price_high"
            emoji = "📈"
            message = (
                f"İlanınız '{title}' piyasa fiyatının üzerinde!\n\n"
                f"Sizin fiyatınız: {user_price:,.0f} TL\n"
                f"Piyasa fiyatı: {market_price:,.0f} TL\n"
                f"Fark: %{difference_percent:+.1f}\n\n"
                f"Fiyatınızı düşürerek daha hızlı satış yapabilirsiniz."
            )
        else:
            alert_type = "price_low"
            emoji = "📉"
            message = (
                f"İlanınız '{title}' piyasa fiyatının altında!\n\n"
                f"Sizin fiyatınız: {user_price:,.0f} TL\n"
                f"Piyasa fiyatı: {market_price:,.0f} TL\n"
                f"Fark: %{difference_percent:+.1f}\n\n"
                f"Fiyatınızı artırarak daha fazla kazanç elde edebilirsiniz."
            )
        
        notification_data = {
            "user_id": user_id,
            "listing_id": listing_id,
            "type": alert_type,
            "title": f"{emoji} Fiyat Uyarısı: {title}",
            "message": message,
            "metadata": {
                "user_price": user_price,
                "market_price": market_price,
                "difference_percent": round(difference_percent, 2),
                "checked_at": datetime.now().isoformat()
            },
            "is_read": False,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            self.supabase.table("notifications").insert(notification_data).execute()
            logger.info(f"✅ Created alert for listing {listing_id} ({difference_percent:+.1f}%)")
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")

# Singleton instance
price_monitor = PriceMonitor()

def check_prices():
    """Background job entry point"""
    return price_monitor.check_all_active_listings()

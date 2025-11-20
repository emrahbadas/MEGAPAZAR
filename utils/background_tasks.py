"""
Background tasks for session management and price monitoring
"""
from apscheduler.schedulers.background import BackgroundScheduler
from models.conversation_state import session_manager
from utils.logger import setup_logger

logger = setup_logger("background_tasks")

def cleanup_expired_sessions():
    """Süresi dolmuş session'ları temizle"""
    try:
        logger.info("Running session cleanup...")
        session_manager.cleanup_expired()
        logger.info("Session cleanup completed")
    except Exception as e:
        logger.error(f"Session cleanup failed: {str(e)}")

def check_listing_prices():
    """Aktif ilanların piyasa fiyatlarını kontrol et"""
    try:
        logger.info("Running price check...")
        from utils.price_monitor import check_prices
        result = check_prices()
        logger.info(f"Price check completed: {result}")
    except Exception as e:
        logger.error(f"Price check failed: {str(e)}")

def start_background_tasks():
    """Background task'ları başlat"""
    scheduler = BackgroundScheduler()
    
    # Her 10 dakikada bir expired session temizle
    scheduler.add_job(
        cleanup_expired_sessions,
        'interval',
        minutes=10,
        id='session_cleanup',
        replace_existing=True
    )
    
    # Her gün saat 09:00'da fiyat kontrolü
    scheduler.add_job(
        check_listing_prices,
        'cron',
        hour=9,
        minute=0,
        id='price_check',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Background tasks started (session cleanup + price monitoring)")
    
    return scheduler

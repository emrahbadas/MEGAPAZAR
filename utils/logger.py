import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """Logger oluştur"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Handler ekle (duplicate olmaması için kontrol)
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

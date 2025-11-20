"""
Tools for ProductMatchAgent
Vector search and product comparison tools
"""

from typing import Dict, Any, List
from utils.supabase_client import get_supabase_admin
from utils.openai_client import get_openai_client
from utils.logger import setup_logger

logger = setup_logger("product_match_tools")

def search_similar_products(
    query_text: str,
    threshold: float = 0.7,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Supabase'de vector similarity ile benzer ürünleri ara
    
    Args:
        query_text: Aranacak metin (ürün tipi + kategori)
        threshold: Benzerlik eşiği (0-1)
        limit: Maksimum sonuç sayısı
        
    Returns:
        {
            "similar_products": [...],
            "stats": {
                "count": int,
                "avg_price": float,
                "min_price": float,
                "max_price": float
            }
        }
    """
    try:
        logger.info(f"🔍 Vector search: {query_text}")
        
        # 1. Embedding oluştur
        client = get_openai_client()
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        embedding = embedding_response.data[0].embedding
        
        # 2. Vector search
        supabase = get_supabase_admin()
        results = supabase.rpc(
            'match_products',
            {
                'query_embedding': embedding,
                'match_threshold': threshold,
                'match_count': limit
            }
        ).execute()
        
        if not results.data or len(results.data) == 0:
            logger.info("No similar products found")
            return {
                "similar_products": [],
                "stats": {
                    "count": 0,
                    "avg_price": 0,
                    "min_price": 0,
                    "max_price": 0
                }
            }
        
        # 3. Listing detaylarını getir
        listing_ids = [r['listing_id'] for r in results.data]
        listings = supabase.table('listings') \
            .select('id, title, price, category, stock, created_at') \
            .in_('id', listing_ids) \
            .eq('status', 'active') \
            .execute()
        
        # 4. İstatistik hesapla
        prices = [float(l['price']) for l in listings.data if l.get('price')]
        
        stats = {
            "count": len(prices),
            "avg_price": sum(prices) / len(prices) if prices else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0
        }
        
        logger.info(f"✅ Found {stats['count']} similar products, avg: {stats['avg_price']:.2f} TL")
        
        return {
            "similar_products": listings.data,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Vector search failed: {str(e)}")
        return {
            "similar_products": [],
            "stats": {
                "count": 0,
                "avg_price": 0,
                "min_price": 0,
                "max_price": 0
            }
        }

def get_product_price_range(category: str) -> Dict[str, float]:
    """
    Belirli kategori için fiyat aralığını getir
    
    Args:
        category: Ürün kategorisi
        
    Returns:
        {"min": float, "max": float, "avg": float}
    """
    try:
        supabase = get_supabase_admin()
        
        listings = supabase.table('listings') \
            .select('price') \
            .eq('category', category) \
            .eq('status', 'active') \
            .execute()
        
        if not listings.data:
            return {"min": 0, "max": 0, "avg": 0}
        
        prices = [float(l['price']) for l in listings.data if l.get('price')]
        
        return {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
            "avg": sum(prices) / len(prices) if prices else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get price range: {str(e)}")
        return {"min": 0, "max": 0, "avg": 0}

def search_by_category(category: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Kategoriye göre ürün ara
    
    Args:
        category: Kategori adı
        limit: Maksimum sonuç
        
    Returns:
        Listing listesi
    """
    try:
        supabase = get_supabase_admin()
        
        results = supabase.table('listings') \
            .select('*') \
            .eq('category', category) \
            .eq('status', 'active') \
            .order('created_at', desc=True) \
            .limit(limit) \
            .execute()
        
        return results.data if results.data else []
        
    except Exception as e:
        logger.error(f"Category search failed: {str(e)}")
        return []

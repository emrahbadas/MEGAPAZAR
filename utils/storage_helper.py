"""
Supabase Storage helper fonksiyonları
Resim upload, URL oluşturma, silme işlemleri
"""

from utils.supabase_client import get_supabase_admin
from utils.logger import setup_logger
import uuid
from typing import List, Dict, Any, Optional
from PIL import Image
import io
import base64

logger = setup_logger("storage_helper")

def upload_product_image(
    listing_id: str,
    image_data: bytes,
    filename: str,
    is_primary: bool = False,
    display_order: int = 0
) -> Optional[Dict[str, Any]]:
    """
    Ürün resmini Supabase Storage'a yükle ve product_images tablosuna kaydet
    
    Args:
        listing_id: İlan ID
        image_data: Resim byte data
        filename: Dosya adı
        is_primary: Ana resim mi?
        display_order: Görüntüleme sırası
        
    Returns:
        Image metadata dict veya None (hata durumunda)
    """
    try:
        supabase = get_supabase_admin()
        
        # Unique dosya adı oluştur
        file_extension = filename.split('.')[-1]
        unique_filename = f"{listing_id}/{uuid.uuid4()}.{file_extension}"
        storage_path = f"product-images/{unique_filename}"
        
        # Storage'a yükle
        result = supabase.storage.from_('product-images').upload(
            path=unique_filename,
            file=image_data,
            file_options={"content-type": f"image/{file_extension}"}
        )
        
        if result:
            # Public URL oluştur
            public_url = supabase.storage.from_('product-images').get_public_url(unique_filename)
            
            # Resim boyutlarını al
            img = Image.open(io.BytesIO(image_data))
            width, height = img.size
            file_size = len(image_data)
            
            # product_images tablosuna kaydet
            image_record = supabase.table('product_images').insert({
                "listing_id": listing_id,
                "storage_path": storage_path,
                "public_url": public_url,
                "is_primary": is_primary,
                "display_order": display_order,
                "file_size": file_size,
                "mime_type": f"image/{file_extension}",
                "width": width,
                "height": height
            }).execute()
            
            logger.info(f"Image uploaded: {unique_filename}")
            return image_record.data[0] if image_record.data else None
            
    except Exception as e:
        logger.error(f"Image upload failed: {str(e)}")
        return None

def get_listing_images(listing_id: str) -> List[Dict[str, Any]]:
    """
    İlan resimlerini getir (sıralı)
    
    Args:
        listing_id: İlan ID
        
    Returns:
        Resim listesi (display_order'a göre sıralı)
    """
    try:
        supabase = get_supabase_admin()
        
        result = supabase.table('product_images') \
            .select('*') \
            .eq('listing_id', listing_id) \
            .order('display_order') \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        logger.error(f"Failed to get listing images: {str(e)}")
        return []

def get_primary_image(listing_id: str) -> Optional[str]:
    """
    İlanın ana resminin URL'ini getir
    
    Args:
        listing_id: İlan ID
        
    Returns:
        Public URL veya None
    """
    try:
        supabase = get_supabase_admin()
        
        result = supabase.table('product_images') \
            .select('public_url') \
            .eq('listing_id', listing_id) \
            .eq('is_primary', True) \
            .limit(1) \
            .execute()
        
        if result.data:
            return result.data[0]['public_url']
        
        # Primary yoksa ilk resmi döndür
        result = supabase.table('product_images') \
            .select('public_url') \
            .eq('listing_id', listing_id) \
            .order('display_order') \
            .limit(1) \
            .execute()
        
        return result.data[0]['public_url'] if result.data else None
        
    except Exception as e:
        logger.error(f"Failed to get primary image: {str(e)}")
        return None

def delete_listing_images(listing_id: str) -> bool:
    """
    İlanın tüm resimlerini sil (Storage + DB)
    
    Args:
        listing_id: İlan ID
        
    Returns:
        Başarılı ise True
    """
    try:
        supabase = get_supabase_admin()
        
        # Önce resim kayıtlarını al
        images = get_listing_images(listing_id)
        
        # Storage'dan sil
        for img in images:
            storage_path = img['storage_path'].replace('product-images/', '')
            supabase.storage.from_('product-images').remove([storage_path])
        
        # DB'den sil
        supabase.table('product_images') \
            .delete() \
            .eq('listing_id', listing_id) \
            .execute()
        
        logger.info(f"Deleted {len(images)} images for listing {listing_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete listing images: {str(e)}")
        return False

def set_primary_image(image_id: str, listing_id: str) -> bool:
    """
    Belirtilen resmi ana resim yap (diğerlerini primary=false yap)
    
    Args:
        image_id: Resim ID
        listing_id: İlan ID
        
    Returns:
        Başarılı ise True
    """
    try:
        supabase = get_supabase_admin()
        
        # Önce tüm resimleri primary=false yap
        supabase.table('product_images') \
            .update({"is_primary": False}) \
            .eq('listing_id', listing_id) \
            .execute()
        
        # Seçili resmi primary=true yap
        supabase.table('product_images') \
            .update({"is_primary": True}) \
            .eq('id', image_id) \
            .execute()
        
        logger.info(f"Set primary image: {image_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to set primary image: {str(e)}")
        return False

def upload_image_from_url(listing_id: str, image_url: str, is_primary: bool = False) -> Optional[Dict[str, Any]]:
    """
    URL'den resim indir ve yükle
    
    Args:
        listing_id: İlan ID
        image_url: Resim URL'i
        is_primary: Ana resim mi?
        
    Returns:
        Image metadata veya None
    """
    try:
        import httpx
        
        # Resmi indir
        response = httpx.get(image_url, timeout=10)
        if response.status_code != 200:
            logger.error(f"Failed to download image: {response.status_code}")
            return None
        
        image_data = response.content
        
        # Dosya adı oluştur
        filename = image_url.split('/')[-1]
        if '?' in filename:
            filename = filename.split('?')[0]
        
        # Yükle
        return upload_product_image(
            listing_id=listing_id,
            image_data=image_data,
            filename=filename,
            is_primary=is_primary
        )
        
    except Exception as e:
        logger.error(f"Failed to upload image from URL: {str(e)}")
        return None

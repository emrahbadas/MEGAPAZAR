from supabase import create_client, Client
from config import get_settings
from functools import lru_cache

@lru_cache()
def get_supabase() -> Client:
    """Normal Supabase client (anon key)"""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_key)

@lru_cache()
def get_supabase_admin() -> Client:
    """Admin Supabase client (service key)"""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)

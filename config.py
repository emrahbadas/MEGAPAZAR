from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    
    # Tavily (Opsiyonel)
    tavily_api_key: str = ""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # n8n (Zorunlu - WhatsApp bridge için)
    n8n_webhook_url: str
    
    # Twilio (Zorunlu - WhatsApp entegrasyonu için)
    twilio_account_sid: str
    twilio_auth_token: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Extra fields izin ver

@lru_cache()
def get_settings() -> Settings:
    return Settings()

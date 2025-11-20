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
        
        # Railway büyük harfle gönderirse, küçük harfle map et
        fields = {
            'openai_api_key': {'env': ['OPENAI_API_KEY', 'openai_api_key']},
            'supabase_url': {'env': ['SUPABASE_URL', 'supabase_url']},
            'supabase_key': {'env': ['SUPABASE_KEY', 'supabase_key']},
            'supabase_service_key': {'env': ['SUPABASE_SERVICE_KEY', 'supabase_service_key']},
            'n8n_webhook_url': {'env': ['N8N_WEBHOOK_URL', 'n8n_webhook_url']},
            'twilio_account_sid': {'env': ['TWILIO_ACCOUNT_SID', 'twilio_account_sid']},
            'twilio_auth_token': {'env': ['TWILIO_AUTH_TOKEN', 'twilio_auth_token']},
            'tavily_api_key': {'env': ['TAVILY_API_KEY', 'tavily_api_key']},
            'host': {'env': ['HOST', 'host']},
            'port': {'env': ['PORT', 'port']},
            'debug': {'env': ['DEBUG', 'debug']},
        }

@lru_cache()
def get_settings() -> Settings:
    return Settings()

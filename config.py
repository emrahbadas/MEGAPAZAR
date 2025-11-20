from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, alias='OPENAI_API_KEY')
    
    # Supabase
    supabase_url: Optional[str] = Field(default=None, alias='SUPABASE_URL')
    supabase_key: Optional[str] = Field(default=None, alias='SUPABASE_KEY')
    supabase_service_key: Optional[str] = Field(default=None, alias='SUPABASE_SERVICE_KEY')
    
    # Tavily (Opsiyonel)
    tavily_api_key: str = Field(default="", alias='TAVILY_API_KEY')
    
    # Server
    host: str = Field(default="0.0.0.0", alias='HOST')
    port: int = Field(default=8000, alias='PORT')
    debug: bool = Field(default=True, alias='DEBUG')
    
    # n8n (Zorunlu - WhatsApp bridge için)
    n8n_webhook_url: Optional[str] = Field(default=None, alias='N8N_WEBHOOK_URL')
    
    # Twilio (Zorunlu - WhatsApp entegrasyonu için)
    twilio_account_sid: Optional[str] = Field(default=None, alias='TWILIO_ACCOUNT_SID')
    twilio_auth_token: Optional[str] = Field(default=None, alias='TWILIO_AUTH_TOKEN')
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

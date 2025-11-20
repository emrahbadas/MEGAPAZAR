from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = Field(validation_alias='OPENAI_API_KEY')
    
    # Supabase
    supabase_url: str = Field(validation_alias='SUPABASE_URL')
    supabase_key: str = Field(validation_alias='SUPABASE_KEY')
    supabase_service_key: str = Field(validation_alias='SUPABASE_SERVICE_KEY')
    
    # Tavily (Opsiyonel)
    tavily_api_key: str = Field(default="", validation_alias='TAVILY_API_KEY')
    
    # Server
    host: str = Field(default="0.0.0.0", validation_alias='HOST')
    port: int = Field(default=8000, validation_alias='PORT')
    debug: bool = Field(default=True, validation_alias='DEBUG')
    
    # n8n (Zorunlu - WhatsApp bridge için)
    n8n_webhook_url: str = Field(validation_alias='N8N_WEBHOOK_URL')
    
    # Twilio (Zorunlu - WhatsApp entegrasyonu için)
    twilio_account_sid: str = Field(validation_alias='TWILIO_ACCOUNT_SID')
    twilio_auth_token: str = Field(validation_alias='TWILIO_AUTH_TOKEN')
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

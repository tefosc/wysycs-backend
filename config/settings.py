from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    environment: str = "development"
    port: int = 8000
    
    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    
    # NASA
    nasa_firms_api_key: str = ""
    
    # Google Earth Engine
    google_credentials: str = ""
    
    # Notificaciones
    resend_api_key: str = ""
    telegram_bot_token: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore" 

@lru_cache()
def get_settings():
    return Settings()
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    environment: str = "development"
    port: int = 8000
    
    # Supabase (SIN valores por defecto - REQUERIDOS)
    supabase_url: str
    supabase_key: str
    
    # NASA (SIN valor por defecto - REQUERIDO)
    nasa_firms_api_key: str
    
    # Google Earth Engine (Opcional)
    google_credentials: str = ""
    
    # Notificaciones (Opcionales)
    resend_api_key: str = ""
    telegram_bot_token: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
"""
Configuration settings using Pydantic
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS settings
    allowed_origin: str = "*"
    
    # Data settings
    cache_ttl_seconds: int = 30
    
    # Environment
    environment: str = "production"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


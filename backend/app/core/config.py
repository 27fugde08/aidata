from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AIOS Enterprise Backend"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://aios:aios@postgres:5432/aios"
    
    # Celery / Redis
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # AI
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-flash-latest"

    # Security (Example)
    SECRET_KEY: str = "supersecretkey" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

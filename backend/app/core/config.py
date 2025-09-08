from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "edupredict"
    
    # Security settings
    SECRET_KEY: str = "your-secure-secret-key-here-change-in-production-12345678901234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*"]
    
    # App settings
    APP_NAME: str = "EduPredict"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = True
    
    # Optional settings (disabled for now to avoid dependency issues)
    HDFS_HOST: str = "localhost"
    HDFS_PORT: int = 9000
    HDFS_USER: str = "hdfs"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

settings = Settings()
"""
Configuration settings for EduPredict application
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "EduPredict"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str
    
    # ML Models
    DROPOUT_MODEL_PATH: str = "app/ml/models/dropout_model.joblib"
    GRADE_MODEL_PATH: str = "app/ml/models/grade_model.joblib"
    
    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instance
settings = Settings()


def get_mongodb_url() -> str:
    return settings.MONGODB_URL

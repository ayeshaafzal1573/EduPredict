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
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # MongoDB (must be in .env)
    MONGODB_URL: str
    MONGODB_DB_NAME: str
    
    # Hadoop/HDFS
    HDFS_HOST: str = "localhost"
    HDFS_PORT: int = 9000
    HDFS_USER: str = "hadoop"
    
    # Impala
    IMPALA_HOST: str = "localhost"
    IMPALA_PORT: int = 21050
    IMPALA_DATABASE: str = "edupredict"
    
    # Email
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@edupredict.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
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


# Database URLs
def get_mongodb_url() -> str:
    return settings.MONGODB_URL


def get_hdfs_url() -> str:
    return f"hdfs://{settings.HDFS_HOST}:{settings.HDFS_PORT}"


def get_impala_connection_params() -> dict:
    return {
        "host": settings.IMPALA_HOST,
        "port": settings.IMPALA_PORT,
        "database": settings.IMPALA_DATABASE
    }

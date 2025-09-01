"""
Configuration settings for EduPredict application
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
 

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
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    CORS_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000",  "http://127.0.0.1:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    # MongoDB
    MONGODB_URL: str = "mongodb+srv://ayeshaafzal1573:bzRBxk5ae4TcuRO7@cluster0.c8tez.mongodb.net/edupredict?retryWrites=true&w=majority&appName=Cluster0"
    MONGODB_DB_NAME: str = "edupredict"
    
    # Hadoop/HDFS
    HDFS_HOST: str = "localhost"
    HDFS_PORT: int = 9000
    HDFS_USER: str = "hadoop"
    
    # Impala
    IMPALA_HOST: str = "localhost"
    IMPALA_PORT: int = 21050
    IMPALA_DATABASE: str = "edupredict"
    
    # Email configuration
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@edupredict.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    
    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379"
    
    # ML Model paths
    DROPOUT_MODEL_PATH: str = "app/ml/models/dropout_model.joblib"
    GRADE_MODEL_PATH: str = "app/ml/models/grade_model.joblib"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Database URLs
def get_mongodb_url() -> str:
    """Get MongoDB connection URL"""
    return settings.MONGODB_URL


def get_hdfs_url() -> str:
    """Get HDFS connection URL"""
    return f"hdfs://{settings.HDFS_HOST}:{settings.HDFS_PORT}"


def get_impala_connection_params() -> dict:
    """Get Impala connection parameters"""
    return {
        "host": settings.IMPALA_HOST,
        "port": settings.IMPALA_PORT,
        "database": settings.IMPALA_DATABASE
    }

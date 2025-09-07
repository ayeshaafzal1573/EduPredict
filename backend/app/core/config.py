from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    MONGODB_URL: str = "mongodb+srv://ayeshaafzal1573:bzRBxk5ae4TcuRO7@cluster0.c8tez.mongodb.net/edupredict?retryWrites=true&w=majority&appName=Cluster0"
    MONGODB_DB: str = "edupredict"
    SECRET_KEY: str = "your-secure-secret-key-here-change-in-production"
    CORS_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*"]
    APP_NAME: str = "EduPredict"
    LOG_LEVEL: str = "INFO"
    
    # Optional settings (removed dependencies that might cause issues)
    HDFS_HOST: str = "localhost"
    HDFS_PORT: int = 9000
    HDFS_USER: str = "hdfs"
    REDIS_URL: str = "redis://localhost:6379/0"
    TABLEAU_SERVER: str = "http://localhost:8000"
    TABLEAU_USERNAME: str = "admin"
    TABLEAU_PASSWORD: str = "password"
    TABLEAU_SITE_NAME: str = "default"
    DROPOUT_MODEL_PATH: str = "app/ml/models/dropout_model.joblib"
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

settings = Settings()
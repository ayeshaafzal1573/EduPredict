from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.base import PyObjectId, MongoBaseModel


class Notification(MongoBaseModel):
    """Notification model"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationCreate(BaseModel):
    """Notification creation model"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    user_id: str
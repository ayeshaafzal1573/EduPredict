from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId
from app.utils.pyobjectid import PyObjectId

class Notification(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    title: str
    message: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class NotificationCreate(BaseModel):
    title: str
    message: str
    user_id: str

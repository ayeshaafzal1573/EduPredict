from typing import List
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
from app.core.database import get_notifications_collection
from app.models.notification import Notification, NotificationCreate
from datetime import datetime

class NotificationService:
    """Service for notification-related operations"""

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_notification(self, notification: NotificationCreate) -> Notification:
        """Create a new notification"""
        try:
            notification_dict = notification.dict()
            notification_dict.update({
                "is_read": False,
                "created_at": datetime.utcnow()
            })
            
            result = await self.collection.insert_one(notification_dict)
            notification_in_db = await self.collection.find_one({"_id": result.inserted_id})
            
            # Convert to Notification model
            notification_data = {
                "id": str(notification_in_db["_id"]),
                "user_id": notification_in_db["user_id"],
                "title": notification_in_db["title"],
                "message": notification_in_db["message"],
                "is_read": notification_in_db["is_read"],
                "created_at": notification_in_db["created_at"]
            }
            
            return Notification(**notification_data)
        except Exception as e:
            logger.error(f"Failed to create notification for user {notification.user_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_user_notifications(self, user_id: str) -> List[Notification]:
        """Retrieve notifications for a user"""
        try:
            notifications = await self.collection.find({"user_id": user_id}).sort("created_at", -1).to_list(length=100)
            
            result = []
            for notif in notifications:
                notification_data = {
                    "id": str(notif["_id"]),
                    "user_id": notif["user_id"],
                    "title": notif["title"],
                    "message": notif["message"],
                    "is_read": notif["is_read"],
                    "created_at": notif["created_at"]
                }
                result.append(Notification(**notification_data))
            
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve notifications for user {user_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_notification_service(
    collection: AsyncIOMotorCollection = Depends(get_notifications_collection)
) -> NotificationService:
    """Dependency for NotificationService"""
    return NotificationService(collection)
import asyncio
from typing import List
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
from app.core.database import get_notifications_collection
from app.models.notification import Notification, NotificationCreate
from redis.asyncio import Redis
from app.core.config import settings

async def get_redis() -> Redis:
    """Dependency for Redis client"""
    return Redis.from_url(settings.REDIS_URL)

class NotificationService:
    """Service for notification-related operations"""

    def __init__(self, collection: AsyncIOMotorCollection, redis_client: Redis):
        self.collection = collection
        self.redis_client = redis_client

    async def create_notification(self, notification: NotificationCreate) -> Notification:
        """Create a new notification"""
        try:
            result = await self.collection.insert_one(notification.dict())
            notification_in_db = await self.collection.find_one({"_id": result.inserted_id})
            # Publish to Redis for real-time delivery
            await self.redis_client.publish(f"notifications:{notification.user_id}", notification.message)
            return Notification(**notification_in_db)
        except Exception as e:
            logger.error(f"Failed to create notification for user {notification.user_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_user_notifications(self, user_id: str) -> List[Notification]:
        """Retrieve notifications for a user"""
        try:
            notifications = await self.collection.find({"user_id": user_id}).to_list(length=1000)
            return [Notification(**n) for n in notifications]
        except Exception as e:
            logger.error(f"Failed to retrieve notifications for user {user_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_notification_service(
    collection: AsyncIOMotorCollection = Depends(get_notifications_collection),
    redis_client: Redis = Depends(get_redis)
) -> NotificationService:
    """Dependency for NotificationService"""
    return NotificationService(collection, redis_client)
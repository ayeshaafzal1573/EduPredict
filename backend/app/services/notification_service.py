from typing import List, Optional
from app.models.notification import Notification, NotificationCreate
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class NotificationService:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        self.collection = self.db["notifications"]

    async def create_notification(self, data: NotificationCreate) -> Notification:
        doc = data.model_dump()
        result = await self.collection.insert_one(doc)
        return await self.get_notification(str(result.inserted_id))

    async def get_notification(self, notif_id: str) -> Optional[Notification]:
        notif = await self.collection.find_one({"_id": notif_id})
        if notif:
            return Notification(**notif)

    async def get_notifications(self, user_id: str, skip: int, limit: int, unread_only: bool) -> List[Notification]:
        query = {"user_id": user_id}
        if unread_only:
            query["is_read"] = False

        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        return [Notification(**doc) async for doc in cursor]

    async def mark_as_read(self, notif_id: str) -> bool:
        result = await self.collection.update_one({"_id": notif_id}, {"$set": {"is_read": True}})
        return result.modified_count > 0

    async def delete_notification(self, notif_id: str) -> bool:
        result = await self.collection.delete_one({"_id": notif_id})
        return result.deleted_count > 0

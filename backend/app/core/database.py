import motor.motor_asyncio
import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from app.core.config import settings, get_mongodb_url


class DatabaseManager:
    """MongoDB connection manager"""

    def __init__(self):
        self.mongodb_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.mongodb_db: Optional[AsyncIOMotorDatabase] = None
        self._is_connected = False

    async def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(get_mongodb_url())
            self.mongodb_db = self.mongodb_client[settings.MONGODB_DB_NAME]

            # Test connection with timeout
            await asyncio.wait_for(
                self.mongodb_client.admin.command('ping'),
                timeout=5.0
            )
            self._is_connected = True
            logger.info("✅ Connected to MongoDB successfully")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.mongodb_client = None
            self.mongodb_db = None
            self._is_connected = False
            return False

    def get_collection(self, collection_name: str):
        """Return MongoDB collection"""
        if not self._is_connected or self.mongodb_db is None:
            raise RuntimeError("MongoDB not connected")
        return self.mongodb_db[collection_name]

    async def close_mongodb(self):
        """Close MongoDB connection"""
        if self.mongodb_client:
            self.mongodb_client.close()
            self._is_connected = False
            logger.info("MongoDB connection closed")

    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        return self._is_connected


# Global database manager instance
db_manager = DatabaseManager()


async def connect_to_mongo():
    """Initialize MongoDB connection"""
    return await db_manager.connect_mongodb()


async def close_mongo_connection():
    """Close MongoDB connection"""
    await db_manager.close_mongodb()


def get_database():
    """Get MongoDB database instance"""
    if not db_manager.is_connected():
        raise RuntimeError("MongoDB not connected")
    return db_manager.mongodb_db


# Collection getters
def get_users_collection():
    return db_manager.get_collection("users")


def get_students_collection():
    return db_manager.get_collection("students")


def get_courses_collection():
    return db_manager.get_collection("courses")


def get_attendance_collection():
    return db_manager.get_collection("attendance")


def get_grades_collection():
    return db_manager.get_collection("grades")


def get_notifications_collection():
    return db_manager.get_collection("notifications")
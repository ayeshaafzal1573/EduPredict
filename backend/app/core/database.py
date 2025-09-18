from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from app.core.config import settings
from loguru import logger
from typing import Optional

client: Optional[AsyncIOMotorClient] = None

async def connect_to_mongo() -> bool:
    """Initialize MongoDB connection"""
    global client
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=1,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            serverSelectionTimeoutMS=5000
        )
        # Test connection
        await client.admin.command('ping')
        logger.info("MongoDB connected successfully")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        logger.error("Please ensure MongoDB is running and accessible")
        return False

async def close_mongo_connection() -> None:
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")
        client = None

async def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """Get MongoDB collection with validation"""
    global client
    if not client:
        connected = await connect_to_mongo()
        if not connected:
            raise Exception("Database connection unavailable")
    
    return client[settings.MONGODB_DB][collection_name]

async def get_students_collection() -> AsyncIOMotorCollection:
    """Get students collection"""
    return await get_collection("students")

async def get_users_collection() -> AsyncIOMotorCollection:
    """Get users collection"""
    return await get_collection("users")

async def get_courses_collection() -> AsyncIOMotorCollection:
    """Get courses collection"""
    return await get_collection("courses")

async def get_attendance_collection() -> AsyncIOMotorCollection:
    """Get attendance collection"""
    return await get_collection("attendance")

async def get_grades_collection() -> AsyncIOMotorCollection:
    """Get grades collection"""
    return await get_collection("grades")

async def get_notifications_collection() -> AsyncIOMotorCollection:
    """Get notifications collection"""
    return await get_collection("notifications")
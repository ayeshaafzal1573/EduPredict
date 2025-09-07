from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from app.core.config import settings
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from fastapi import HTTPException, status

client: AsyncIOMotorClient | None = None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def connect_to_mongo() -> bool:
    """Initialize MongoDB connection with retry logic"""
    global client
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=100,
            minPoolSize=10,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            serverSelectionTimeoutMS=30000
        )
        # Test connection
        await client.admin.command('ping')
        logger.info("MongoDB connected successfully")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
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
    if not client:
        # Try to reconnect
        connected = await connect_to_mongo()
        if not connected:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection unavailable")
    
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
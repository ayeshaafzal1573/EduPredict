"""
Database connections and utilities for MongoDB
"""

import motor.motor_asyncio
import asyncio
from typing import Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from app.core.config import settings, get_mongodb_url


class DatabaseManager:
    """Database connection manager"""

    def __init__(self):
        self.mongodb_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.mongodb_db = None
        
        # In-memory data store for fallback
        self.in_memory_data = {
            'users': [],
            'courses': [],
            'students': [],
            'grades': [],
            'attendance': [],
            'notifications': []
        }
        self.use_in_memory = False
    async def _initialize_in_memory_data(self):
        """Initialize in-memory database with default collections"""
        self.in_memory_data = {
            'users': [],
            'courses': [],
            'students': [],
            'grades': [],
            'attendance': [],
            'notifications': []
        }
        logger.info("🗂️ In-memory database initialized")
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
            logger.info("✅ Connected to MongoDB successfully")
            self.use_in_memory = False
            return True
        except Exception as e:
            logger.warning(f"⚠️ MongoDB unavailable ({e}) - switching to in-memory database")
            self.mongodb_client = None
            self.mongodb_db = None
            self.use_in_memory = True
            await self._initialize_in_memory_data()
            return False

  
    def get_collection(self, collection_name: str):
        """Return collection (MongoDB or in-memory fallback)"""
        if self.use_in_memory:
            return InMemoryCollection(self.in_memory_data, collection_name)
        return self.mongodb_db[collection_name]

    async def close_mongodb(self):
        """Close MongoDB connection"""
        if self.mongodb_client:
            self.mongodb_client.close()
            logger.info("MongoDB connection closed")


# Global database manager instance
db_manager = DatabaseManager()


async def connect_to_mongo():
    """Initialize MongoDB connection"""
    await db_manager.connect_mongodb()


async def close_mongo_connection():
    """Close MongoDB connection"""
    await db_manager.close_mongodb()


def get_database():
    """Get MongoDB database instance"""
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

class InMemoryCollection:
    """Simple in-memory collection that mimics MongoDB operations"""

    def __init__(self, data_store, collection_name):
        self.data_store = data_store
        self.collection_name = collection_name
        if collection_name not in self.data_store:
            self.data_store[collection_name] = []

    async def find(self, query=None, **kwargs):
        data = self.data_store[self.collection_name]
        if query is None:
            return InMemoryCursor(data)
        filtered_data = [doc for doc in data if self._matches_query(doc, query)]
        return InMemoryCursor(filtered_data)

    async def find_one(self, query=None):
        data = self.data_store[self.collection_name]
        if query is None:
            return data[0] if data else None
        for doc in data:
            if self._matches_query(doc, query):
                return doc
        return None

    async def insert_one(self, document):
        import uuid
        if "_id" not in document:
            document["_id"] = str(uuid.uuid4())
        self.data_store[self.collection_name].append(document)
        return type('InsertResult', (), {'inserted_id': document["_id"]})()

    def _matches_query(self, doc, query):
        for key, value in query.items():
            if doc.get(key) != value:
                return False
        return True


class InMemoryCursor:
    def __init__(self, data):
        self.data = data
        self._skip = 0
        self._limit = None

    def skip(self, count):
        self._skip = count
        return self

    def limit(self, count):
        self._limit = count
        return self

    async def to_list(self, length=None):
        start = self._skip
        end = start + (self._limit or len(self.data))
        return self.data[start:end]

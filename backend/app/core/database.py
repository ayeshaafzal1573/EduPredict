"""
Database connections and utilities for MongoDB, HDFS, and Impala
"""

import motor.motor_asyncio
from pymongo import MongoClient
from typing import Optional
import asyncio

# Optional imports for big data components
try:
    from impala.dbapi import connect as impala_connect
    IMPALA_AVAILABLE = True
except ImportError:
    IMPALA_AVAILABLE = False
    impala_connect = None

try:
    import hdfs3
    HDFS_AVAILABLE = True
except ImportError:
    HDFS_AVAILABLE = False
    hdfs3 = None

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from app.core.config import settings, get_mongodb_url, get_hdfs_url, get_impala_connection_params


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self.mongodb_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.mongodb_db = None
        self.hdfs_client: Optional[hdfs3.HDFileSystem] = None
        self.impala_connection = None
    
    async def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(get_mongodb_url())
            self.mongodb_db = self.mongodb_client[settings.MONGODB_DB_NAME]
            # Test connection
            await self.mongodb_client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def connect_hdfs(self):
        """Connect to HDFS"""
        if not HDFS_AVAILABLE:
            logger.warning("HDFS not available - hdfs3 package not installed")
            return

        try:
            self.hdfs_client = hdfs3.HDFileSystem(
                host=settings.HDFS_HOST,
                port=settings.HDFS_PORT,
                user=settings.HDFS_USER
            )
            logger.info("Connected to HDFS successfully")
        except Exception as e:
            logger.error(f"Failed to connect to HDFS: {e}")
            # Don't raise - HDFS might not be available in development
    
    def connect_impala(self):
        """Connect to Impala"""
        if not IMPALA_AVAILABLE:
            logger.warning("Impala not available - impyla package not installed")
            return

        try:
            params = get_impala_connection_params()
            self.impala_connection = impala_connect(**params)
            logger.info("Connected to Impala successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Impala: {e}")
            # Don't raise - Impala might not be available in development
    
    async def close_mongodb(self):
        """Close MongoDB connection"""
        if self.mongodb_client:
            self.mongodb_client.close()
            logger.info("MongoDB connection closed")
    
    def close_hdfs(self):
        """Close HDFS connection"""
        if self.hdfs_client:
            self.hdfs_client.disconnect()
            logger.info("HDFS connection closed")
    
    def close_impala(self):
        """Close Impala connection"""
        if self.impala_connection:
            self.impala_connection.close()
            logger.info("Impala connection closed")


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


def get_hdfs_client():
    """Get HDFS client instance"""
    if not db_manager.hdfs_client:
        db_manager.connect_hdfs()
    return db_manager.hdfs_client


def get_impala_connection():
    """Get Impala connection instance"""
    if not db_manager.impala_connection:
        db_manager.connect_impala()
    return db_manager.impala_connection


# Collection getters
def get_users_collection():
    """Get users collection"""
    return get_database().users


def get_students_collection():
    """Get students collection"""
    return get_database().students


def get_courses_collection():
    """Get courses collection"""
    return get_database().courses


def get_attendance_collection():
    """Get attendance collection"""
    return get_database().attendance


def get_grades_collection():
    """Get grades collection"""
    return get_database().grades


def get_notifications_collection():
    """Get notifications collection"""
    return get_database().notifications

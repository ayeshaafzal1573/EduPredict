import asyncio
from typing import List
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
from app.core.database import get_courses_collection
from app.models.course import Course, CourseCreate, CourseUpdate
from app.core.hdfs_utils import HDFSClient

class CourseService:
    """Service for course-related operations"""

    def __init__(self, collection: AsyncIOMotorCollection, hdfs_client: HDFSClient):
        self.collection = collection
        self.hdfs_client = hdfs_client

    async def create_course(self, course: CourseCreate) -> Course:
        """Create a new course"""
        try:
            existing = await self.collection.find_one({"code": course.code})
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course code already exists")
            result = await self.collection.insert_one(course.dict())
            course_in_db = await self.collection.find_one({"_id": result.inserted_id})
            return Course(**course_in_db)
        except Exception as e:
            logger.error(f"Failed to create course {course.code}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_course(self, course_id: str) -> Course:
        """Retrieve a course by ID"""
        try:
            course = await self.collection.find_one({"code": course_id})
            if not course:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
            return Course(**course)
        except Exception as e:
            logger.error(f"Failed to retrieve course {course_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_all_courses(self) -> List[Course]:
        """Retrieve all courses"""
        try:
            courses = await self.collection.find().to_list(length=1000)
            return [Course(**course) for course in courses]
        except Exception as e:
            logger.error(f"Failed to retrieve courses: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_course_service(collection: AsyncIOMotorCollection = Depends(get_courses_collection)) -> CourseService:
    """Dependency for CourseService"""
    return CourseService(collection, HDFSClient())
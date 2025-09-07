from typing import List
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
from app.core.database import get_courses_collection, get_users_collection
from app.models.course import Course, CourseCreate, CourseUpdate
from datetime import datetime
from bson import ObjectId

class CourseService:
    """Service for course-related operations"""

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_course(self, course: CourseCreate) -> Course:
        """Create a new course"""
        try:
            existing = await self.collection.find_one({"code": course.code})
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course code already exists")
            
            course_dict = course.dict()
            course_dict.update({
                "students": [],
                "student_count": 0,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            result = await self.collection.insert_one(course_dict)
            course_in_db = await self.collection.find_one({"_id": result.inserted_id})
            
            # Convert to Course model
            course_data = {
                "id": str(course_in_db["_id"]),
                "name": course_in_db["name"],
                "code": course_in_db["code"],
                "description": course_in_db.get("description", ""),
                "department": course_in_db.get("department", ""),
                "credits": course_in_db["credits"],
                "semester": course_in_db["semester"],
                "academic_year": course_in_db["academic_year"],
                "schedule": course_in_db.get("schedule", ""),
                "room": course_in_db.get("room", ""),
                "max_students": course_in_db.get("max_students", 30),
                "teacher_id": course_in_db.get("teacher_id", ""),
                "teacher_name": course_in_db.get("teacher_name", ""),
                "students": course_in_db.get("students", []),
                "student_count": course_in_db.get("student_count", 0),
                "is_active": course_in_db.get("is_active", True),
                "created_at": course_in_db["created_at"],
                "updated_at": course_in_db["updated_at"]
            }
            
            return Course(**course_data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to create course {course.code}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_course(self, course_id: str) -> Course:
        """Retrieve a course by ID or code"""
        try:
            # Try to find by ObjectId first, then by code
            query = {}
            if ObjectId.is_valid(course_id):
                query = {"_id": ObjectId(course_id)}
            else:
                query = {"code": course_id}
            
            course = await self.collection.find_one(query)
            if not course:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
            
            # Convert to Course model
            course_data = {
                "id": str(course["_id"]),
                "name": course["name"],
                "code": course["code"],
                "description": course.get("description", ""),
                "department": course.get("department", ""),
                "credits": course["credits"],
                "semester": course["semester"],
                "academic_year": course["academic_year"],
                "schedule": course.get("schedule", ""),
                "room": course.get("room", ""),
                "max_students": course.get("max_students", 30),
                "teacher_id": course.get("teacher_id", ""),
                "teacher_name": course.get("teacher_name", ""),
                "students": course.get("students", []),
                "student_count": len(course.get("students", [])),
                "is_active": course.get("is_active", True),
                "created_at": course.get("created_at"),
                "updated_at": course.get("updated_at")
            }
            
            return Course(**course_data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to retrieve course {course_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_all_courses(self) -> List[Course]:
        """Retrieve all courses"""
        try:
            courses = await self.collection.find().to_list(length=1000)
            result = []
            
            for course in courses:
                course_data = {
                    "id": str(course["_id"]),
                    "name": course["name"],
                    "code": course["code"],
                    "description": course.get("description", ""),
                    "department": course.get("department", ""),
                    "credits": course["credits"],
                    "semester": course["semester"],
                    "academic_year": course["academic_year"],
                    "schedule": course.get("schedule", ""),
                    "room": course.get("room", ""),
                    "max_students": course.get("max_students", 30),
                    "teacher_id": course.get("teacher_id", ""),
                    "teacher_name": course.get("teacher_name", ""),
                    "students": course.get("students", []),
                    "student_count": len(course.get("students", [])),
                    "is_active": course.get("is_active", True),
                    "created_at": course.get("created_at"),
                    "updated_at": course.get("updated_at")
                }
                result.append(Course(**course_data))
            
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve courses: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_course_service(collection: AsyncIOMotorCollection = Depends(get_courses_collection)) -> CourseService:
    """Dependency for CourseService"""
    return CourseService(collection)
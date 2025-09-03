from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import logging

from app.core.database import get_courses_collection, get_users_collection
from app.models.course import Course, CourseCreate, CourseUpdate
from app.services.user_service import UserService

logger = logging.getLogger(__name__)


class CourseService:
    def __init__(self, courses_collection, users_collection, user_service: UserService):
        self.courses_collection = courses_collection
        self.users_collection = users_collection
        self.user_service = user_service

    @property
    def courses_collection(self):
        if self._courses_collection is None:
            self._courses_collection = get_courses_collection()
        return self._courses_collection

    @property
    def users_collection(self):
        if self._users_collection is None:
            self._users_collection = get_users_collection()
        return self._users_collection

    # ----- CRUD Operations -----
    async def create_course(self, course_data: CourseCreate, teacher_id: str) -> Course:
        try:
            existing = await self.courses_collection.find_one({
                "code": course_data.code,
                "semester": course_data.semester,
                "academic_year": course_data.academic_year,
                "is_active": True
            })
            if existing:
                raise ValueError("Course with this code already exists for this semester")

            teacher_name = "Unknown Teacher"
            try:
                teacher = await self.user_service.get_user_by_id(teacher_id)
                if teacher:
                    teacher_name = f"{teacher.first_name} {teacher.last_name}"
            except Exception as e:
                logger.warning(f"Could not get teacher info: {e}")

            course_dict = course_data.model_dump()
            course_dict.update({
                "_id": ObjectId(),
                "teacher_id": teacher_id,
                "teacher_name": teacher_name,
                "students": [],
                "student_count": 0,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

            result = await self.courses_collection.insert_one(course_dict)
            course_dict["_id"] = result.inserted_id
            return Course(**course_dict)

        except Exception as e:
            logger.error(f"Error creating course: {str(e)}")
            raise

    async def get_courses(self, skip: int = 0, limit: int = 100, teacher_id: Optional[str] = None) -> List[Course]:
        try:
            query = {"is_active": True}
            if teacher_id:
                query["teacher_id"] = teacher_id

            cursor = self.courses_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            courses_data = await cursor.to_list(length=limit)

            courses = []
            for c in courses_data:
                c["student_count"] = len(c.get("students", []))
                courses.append(Course(**c))
            return courses

        except Exception as e:
            logger.error(f"Error getting courses: {str(e)}")
            return []

    async def get_course_by_id(self, course_id: str) -> Optional[Course]:
        try:
            course_data = await self.courses_collection.find_one({
                "_id": ObjectId(course_id),
                "is_active": True
            })
            if course_data:
                course_data["student_count"] = len(course_data.get("students", []))
                return Course(**course_data)
            return None
        except Exception as e:
            logger.error(f"Error getting course by ID: {str(e)}")
            return None

    async def update_course(self, course_id: str, course_update: CourseUpdate) -> Course:
        try:
            update_data = {k: v for k, v in course_update.model_dump().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()

            result = await self.courses_collection.update_one(
                {"_id": ObjectId(course_id)},
                {"$set": update_data}
            )
            if result.modified_count == 0:
                raise ValueError("Course not found or no changes made")

            updated_course = await self.get_course_by_id(course_id)
            if not updated_course:
                raise ValueError("Failed to retrieve updated course")

            return updated_course

        except Exception as e:
            logger.error(f"Error updating course: {str(e)}")
            raise

    async def delete_course(self, course_id: str) -> bool:
        try:
            result = await self.courses_collection.update_one(
                {"_id": ObjectId(course_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deleting course: {str(e)}")
            return False

    # ----- Students -----
    async def get_course_students(self, course_id: str) -> List[Dict[str, Any]]:
        try:
            course = await self.courses_collection.find_one({"_id": ObjectId(course_id), "is_active": True})
            if not course:
                raise ValueError("Course not found")

            student_ids = course.get("students", [])
            if not student_ids:
                return []

            students = await self.users_collection.find(
                {"_id": {"$in": [ObjectId(sid) for sid in student_ids]}, "role": "student"}
            ).to_list(length=100)
            return students

        except Exception as e:
            logger.error(f"Error fetching students for course {course_id}: {e}")
            raise

    async def enroll_student(self, course_id: str, student_id: str) -> bool:
        try:
            course = await self.get_course_by_id(course_id)
            if not course:
                raise ValueError("Course not found")

            if student_id in course.students:
                raise ValueError("Student already enrolled")

            if course.max_students and len(course.students) >= course.max_students:
                raise ValueError("Course is at maximum capacity")

            result = await self.courses_collection.update_one(
                {"_id": ObjectId(course_id)},
                {"$addToSet": {"students": student_id}, "$set": {"updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Error enrolling student: {str(e)}")
            return False

    async def unenroll_student(self, course_id: str, student_id: str) -> bool:
        try:
            result = await self.courses_collection.update_one(
                {"_id": ObjectId(course_id)},
                {"$pull": {"students": student_id}, "$set": {"updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error unenrolling student: {str(e)}")
            return False

"""
Course service for EduPredict
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models.course import Course, CourseCreate, CourseUpdate
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

class CourseService:
    def __init__(self):
        self.db = get_database()
        self.user_service = UserService()

    def _get_collection(self):
        """Get courses collection"""
        return self.db.get_collection("courses")

    async def create_course(self, course_data: CourseCreate, teacher_id: str) -> Course:
        """Create a new course"""
        try:
            collection = self._get_collection()
            
            # Check if course code already exists
            existing_course = await collection.find_one({
                "code": course_data.code,
                "semester": course_data.semester,
                "academic_year": course_data.academic_year,
                "is_active": True
            })
            
            if existing_course:
                raise ValueError("Course with this code already exists for this semester")

            # Get teacher information
            teacher = await self.user_service.get_user_by_id(teacher_id)
            if not teacher:
                raise ValueError("Teacher not found")

            course_dict = course_data.model_dump()
            course_dict.update({
                "_id": ObjectId(),
                "teacher_id": teacher_id,
                "teacher_name": f"{teacher.first_name} {teacher.last_name}",
                "students": [],
                "student_count": 0,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

            result = await collection.insert_one(course_dict)
            course_dict["_id"] = result.inserted_id

            return Course(**course_dict)
        except Exception as e:
            logger.error(f"Error creating course: {str(e)}")
            raise

    async def get_courses(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        teacher_id: Optional[str] = None,
        semester: Optional[str] = None
    ) -> List[Course]:
        """Get list of courses with filtering"""
        try:
            collection = self._get_collection()
            
            query = {"is_active": True}
            if teacher_id:
                query["teacher_id"] = teacher_id
            if semester:
                query["semester"] = semester

            cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            courses_data = await cursor.to_list(length=limit)

            courses = []
            for course_data in courses_data:
                course_data["student_count"] = len(course_data.get("students", []))
                courses.append(Course(**course_data))

            return courses
        except Exception as e:
            logger.error(f"Error getting courses: {str(e)}")
            raise

    async def get_student_courses(self, student_id: str, skip: int = 0, limit: int = 100) -> List[Course]:
        """Get courses that a student is enrolled in"""
        try:
            collection = self._get_collection()
            
            query = {
                "students": {"$in": [student_id]},
                "is_active": True
            }

            cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            courses_data = await cursor.to_list(length=limit)

            courses = []
            for course_data in courses_data:
                course_data["student_count"] = len(course_data.get("students", []))
                courses.append(Course(**course_data))

            return courses
        except Exception as e:
            logger.error(f"Error getting student courses: {str(e)}")
            raise

    async def get_course_by_id(self, course_id: str) -> Optional[Course]:
        """Get a course by ID"""
        try:
            collection = self._get_collection()
            
            course_data = await collection.find_one({
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
        """Update a course"""
        try:
            collection = self._get_collection()
            
            update_data = {k: v for k, v in course_update.model_dump().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()

            result = await collection.update_one(
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
        """Delete a course (soft delete)"""
        try:
            collection = self._get_collection()
            
            result = await collection.update_one(
                {"_id": ObjectId(course_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )

            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deleting course: {str(e)}")
            return False

    async def enroll_student(self, course_id: str, student_id: str) -> bool:
        """Enroll a student in a course"""
        try:
            collection = self._get_collection()
            
            # Check if student exists
            student = await self.user_service.get_user_by_id(student_id)
            if not student or student.role != "student":
                raise ValueError("Student not found")

            # Check if course exists and has capacity
            course = await self.get_course_by_id(course_id)
            if not course:
                raise ValueError("Course not found")

            if student_id in course.students:
                raise ValueError("Student already enrolled in this course")

            if course.max_students and len(course.students) >= course.max_students:
                raise ValueError("Course is at maximum capacity")

            # Add student to course
            result = await collection.update_one(
                {"_id": ObjectId(course_id)},
                {
                    "$addToSet": {"students": student_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )

            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error enrolling student: {str(e)}")
            return False

    async def unenroll_student(self, course_id: str, student_id: str) -> bool:
        """Unenroll a student from a course"""
        try:
            collection = self._get_collection()
            
            result = await collection.update_one(
                {"_id": ObjectId(course_id)},
                {
                    "$pull": {"students": student_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )

            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error unenrolling student: {str(e)}")
            return False

    async def get_course_students(self, course_id: str) -> List[Dict[str, Any]]:
        """Get list of students enrolled in a course with their details"""
        try:
            course = await self.get_course_by_id(course_id)
            if not course:
                raise ValueError("Course not found")

            students = []
            for student_id in course.students:
                student = await self.user_service.get_user_by_id(student_id)
                if student:
                    # Get additional student data
                    student_data = {
                        "id": student_id,
                        "name": f"{student.first_name} {student.last_name}",
                        "email": student.email,
                        "enrollment_date": student.created_at.isoformat() if student.created_at else None,
                        "status": "active" if student.is_active else "inactive"
                    }
                    
                    # Add performance data if available
                    performance = await self._get_student_performance(student_id, course_id)
                    student_data.update(performance)
                    
                    students.append(student_data)

            return students
        except Exception as e:
            logger.error(f"Error getting course students: {str(e)}")
            raise

    async def _get_student_performance(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """Get student performance data for a specific course"""
        try:
            grades_collection = self.db.get_collection("grades")
            attendance_collection = self.db.get_collection("attendance")

            # Get grades
            grades = await grades_collection.find({
                "student_id": student_id,
                "course_id": course_id
            }).to_list(None)

            current_grade = "N/A"
            gpa = 0.0
            if grades:
                latest_grade = max(grades, key=lambda x: x.get("created_at", datetime.min))
                current_grade = latest_grade.get("letter_grade", "N/A")
                gpa = sum(g.get("grade_points", 0) for g in grades) / len(grades)

            # Get attendance
            attendance_records = await attendance_collection.find({
                "student_id": student_id,
                "course_id": course_id
            }).to_list(None)

            attendance_rate = 0
            if attendance_records:
                attended = sum(1 for record in attendance_records if record.get("status") == "present")
                attendance_rate = (attended / len(attendance_records)) * 100

            # Determine risk level
            risk_level = "low"
            if gpa < 2.0 or attendance_rate < 60:
                risk_level = "high"
            elif gpa < 2.5 or attendance_rate < 75:
                risk_level = "medium"

            return {
                "current_grade": current_grade,
                "gpa": round(gpa, 2),
                "attendance": round(attendance_rate, 1),
                "risk_level": risk_level
            }
        except Exception as e:
            logger.error(f"Error getting student performance: {str(e)}")
            return {
                "current_grade": "N/A",
                "gpa": 0.0,
                "attendance": 0,
                "risk_level": "unknown"
            }

    async def get_teacher_courses_with_stats(self, teacher_id: str) -> List[Dict[str, Any]]:
        """Get courses for a teacher with additional statistics"""
        try:
            courses = await self.get_courses(teacher_id=teacher_id)
            
            courses_with_stats = []
            for course in courses:
                course_dict = course.model_dump()
                
                # Add statistics
                stats = await self._get_course_statistics(str(course.id))
                course_dict.update(stats)
                
                courses_with_stats.append(course_dict)

            return courses_with_stats
        except Exception as e:
            logger.error(f"Error getting teacher courses with stats: {str(e)}")
            raise

    async def _get_course_statistics(self, course_id: str) -> Dict[str, Any]:
        """Get statistics for a course"""
        try:
            grades_collection = self.db.get_collection("grades")
            attendance_collection = self.db.get_collection("attendance")

            # Get average grade
            grade_pipeline = [
                {"$match": {"course_id": course_id}},
                {"$group": {
                    "_id": None,
                    "avg_grade": {"$avg": "$grade_points"},
                    "total_grades": {"$sum": 1}
                }}
            ]
            grade_stats = await grades_collection.aggregate(grade_pipeline).to_list(1)
            avg_grade = grade_stats[0]["avg_grade"] if grade_stats else 0

            # Get attendance rate
            attendance_pipeline = [
                {"$match": {"course_id": course_id}},
                {"$group": {
                    "_id": None,
                    "total_classes": {"$sum": 1},
                    "attended": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}}
                }}
            ]
            attendance_stats = await attendance_collection.aggregate(attendance_pipeline).to_list(1)
            attendance_rate = 0
            if attendance_stats and attendance_stats[0]["total_classes"] > 0:
                attendance_rate = (attendance_stats[0]["attended"] / attendance_stats[0]["total_classes"]) * 100

            return {
                "average_grade": round(avg_grade, 2),
                "attendance_rate": round(attendance_rate, 1),
                "total_assignments": grade_stats[0]["total_grades"] if grade_stats else 0
            }
        except Exception as e:
            logger.error(f"Error getting course statistics: {str(e)}")
            return {
                "average_grade": 0.0,
                "attendance_rate": 0.0,
                "total_assignments": 0
            }

"""
Production-ready StudentService for EduPredict
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo.errors import PyMongoError
import logging

from app.core.database import get_database
from app.models.student import Student, StudentCreate, StudentUpdate
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

# Custom exceptions
class StudentServiceError(Exception):
    pass

class StudentNotFoundError(StudentServiceError):
    pass


class StudentService:
    def __init__(self, db, user_service: UserService):
        self.db = db
        self.user_service = user_service
        self.collection_name = "students"

    def _get_collection(self):
        if not self.db:
            raise StudentServiceError("Database not available")
        return self.db.get_collection(self.collection_name)

    async def create_student(self, student_data: StudentCreate, created_by: str) -> Student:
        try:
            collection = self._get_collection()
            
            # Check if student already exists
            existing_student = await collection.find_one({"user_id": student_data.user_id})
            if existing_student:
                raise StudentServiceError("Student record already exists for this user")
            
            # Verify user exists and is a student
            user = await self.user_service.get_user_by_id(student_data.user_id)
            if not user:
                raise StudentServiceError("User not found")
            if user.role != "student":
                raise StudentServiceError("User is not a student")
            
            student_dict = student_data.model_dump()
            student_dict.update({
                "_id": ObjectId(),
                "student_name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "enrollment_status": "active",
                "created_by": created_by,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

            result = await collection.insert_one(student_dict)
            student_dict["_id"] = result.inserted_id

            return Student(**student_dict)

        except PyMongoError as e:
            logger.error(f"Database error creating student: {str(e)}")
            raise StudentServiceError("Failed to create student") from e

    async def get_student_by_id(self, student_id: str) -> Student:
        try:
            collection = self._get_collection()
            student_data = await collection.find_one({"_id": ObjectId(student_id)})
            if not student_data:
                raise StudentNotFoundError(f"Student with ID {student_id} not found")
            return Student(**student_data)
        except Exception as e:
            logger.error(f"Error fetching student by ID {student_id}: {str(e)}")
            raise

    async def get_student_by_user_id(self, user_id: str) -> Student:
        try:
            collection = self._get_collection()
            student_data = await collection.find_one({"user_id": user_id})
            if not student_data:
                raise StudentNotFoundError(f"Student with user_id {user_id} not found")
            return Student(**student_data)
        except Exception as e:
            logger.error(f"Error fetching student by user_id {user_id}: {str(e)}")
            raise

    async def get_students(
        self,
        skip: int = 0,
        limit: int = 100,
        enrollment_status: Optional[str] = "active",
        major: Optional[str] = None,
        academic_year: Optional[str] = None
    ) -> List[Student]:
        try:
            collection = self._get_collection()
            query = {}
            if enrollment_status:
                query["enrollment_status"] = enrollment_status
            if major:
                query["major"] = major
            if academic_year:
                query["academic_year"] = academic_year

            cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            students_data = await cursor.to_list(length=limit)
            return [Student(**s) for s in students_data]
        except Exception as e:
            logger.error(f"Error fetching students: {str(e)}")
            raise StudentServiceError("Failed to fetch students")

    async def update_student(self, student_id: str, student_update: StudentUpdate) -> Student:
        try:
            collection = self._get_collection()
            update_data = {k: v for k, v in student_update.model_dump().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            result = await collection.update_one({"_id": ObjectId(student_id)}, {"$set": update_data})
            if result.modified_count == 0:
                raise StudentNotFoundError(f"Student with ID {student_id} not found or no changes made")
            return await self.get_student_by_id(student_id)
        except Exception as e:
            logger.error(f"Error updating student {student_id}: {str(e)}")
            raise

    async def delete_student(self, student_id: str) -> bool:
        try:
            collection = self._get_collection()
            result = await collection.update_one(
                {"_id": ObjectId(student_id)},
                {"$set": {"enrollment_status": "inactive", "updated_at": datetime.utcnow()}}
            )
            if result.modified_count == 0:
                raise StudentNotFoundError(f"Student with ID {student_id} not found")
            return True
        except Exception as e:
            logger.error(f"Error deleting student {student_id}: {str(e)}")
            raise

    async def search_students(self, query: str, limit: int = 20) -> List[Student]:
        try:
            collection = self._get_collection()
            search_query = {
                "$or": [
                    {"student_name": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}},
                    {"student_id": {"$regex": query, "$options": "i"}}
                ]
            }
            cursor = collection.find(search_query).limit(limit)
            students_data = await cursor.to_list(length=limit)
            return [Student(**s) for s in students_data]
        except Exception as e:
            logger.error(f"Error searching students: {str(e)}")
            raise StudentServiceError("Failed to search students")

    async def get_student_statistics(self) -> Dict[str, Any]:
        try:
            collection = self._get_collection()
            total_students = await collection.count_documents({"enrollment_status": "active"})

            year_pipeline = [
                {"$match": {"enrollment_status": "active"}},
                {"$group": {"_id": "$academic_year", "count": {"$sum": 1}}}
            ]
            year_stats = await collection.aggregate(year_pipeline).to_list(None)

            major_pipeline = [
                {"$match": {"enrollment_status": "active"}},
                {"$group": {"_id": "$major", "count": {"$sum": 1}}}
            ]
            major_stats = await collection.aggregate(major_pipeline).to_list(None)

            return {
                "total_active_students": total_students,
                "by_academic_year": {stat["_id"]: stat["count"] for stat in year_stats if stat["_id"]},
                "by_major": {stat["_id"]: stat["count"] for stat in major_stats if stat["_id"]},
            }
        except Exception as e:
            logger.error(f"Error fetching student statistics: {str(e)}")
            raise StudentServiceError("Failed to fetch student statistics")

    # -------------------------------
    # Performance & At-Risk Analysis
    # -------------------------------

    async def get_student_performance_summary(self, student_id: str) -> Dict[str, Any]:
        """Comprehensive student performance summary"""
        try:
            student = await self.get_student_by_id(student_id)
            grades_collection = self.db.get_collection("grades")
            attendance_collection = self.db.get_collection("attendance")
            courses_collection = self.db.get_collection("courses")

            grades = await grades_collection.find({"student_id": student_id}).to_list(None)
            attendance_records = await attendance_collection.find({"student_id": student_id}).to_list(None)

            # GPA
            total_points = sum(g.get("grade_points", 0) * g.get("weight", 1) for g in grades)
            total_weight = sum(g.get("weight", 1) for g in grades)
            current_gpa = total_points / total_weight if total_weight > 0 else 0

            # Attendance
            attended = sum(1 for r in attendance_records if r.get("status") == "present")
            attendance_rate = (attended / len(attendance_records) * 100) if attendance_records else 0

            # Enrolled courses
            enrolled_courses = await courses_collection.count_documents(
                {"students": {"$in": [student_id]}, "is_active": True}
            )

            # Recent performance (last 4 months)
            four_months_ago = datetime.utcnow() - timedelta(days=120)
            recent_grades = [g for g in grades if g.get("created_at", datetime.min) >= four_months_ago]
            semester_gpa = sum(g.get("grade_points", 0) for g in recent_grades) / len(recent_grades) if recent_grades else 0

            return {
                "student_id": student_id,
                "student_name": student.student_name,
                "current_gpa": round(current_gpa, 2),
                "semester_gpa": round(semester_gpa, 2),
                "attendance_rate": round(attendance_rate, 1),
                "enrolled_courses": enrolled_courses,
                "total_credits": getattr(student, "total_credits", 0),
                "completed_credits": getattr(student, "completed_credits", 0),
                "academic_standing": self._determine_academic_standing(current_gpa, attendance_rate),
                "total_assignments": len(grades),
                "recent_performance": self._analyze_recent_performance(recent_grades)
            }

        except Exception as e:
            logger.error(f"Error fetching performance for {student_id}: {str(e)}")
            raise StudentServiceError("Failed to fetch performance summary")

    def _determine_academic_standing(self, gpa: float, attendance_rate: float) -> str:
        if gpa >= 3.5 and attendance_rate >= 90:
            return "excellent"
        elif gpa >= 3.0 and attendance_rate >= 80:
            return "good"
        elif gpa >= 2.5 and attendance_rate >= 70:
            return "satisfactory"
        elif gpa >= 2.0 and attendance_rate >= 60:
            return "probation"
        else:
            return "at_risk"

    def _analyze_recent_performance(self, recent_grades: List[Dict[str, Any]]) -> str:
        if len(recent_grades) < 3:
            return "insufficient_data"
        sorted_grades = sorted(recent_grades, key=lambda x: x.get("created_at", datetime.min))
        mid = len(sorted_grades) // 2
        first_avg = sum(g.get("grade_points", 0) for g in sorted_grades[:mid]) / mid
        second_avg = sum(g.get("grade_points", 0) for g in sorted_grades[mid:]) / (len(sorted_grades) - mid)
        if second_avg > first_avg + 0.3:
            return "improving"
        elif second_avg < first_avg - 0.3:
            return "declining"
        return "stable"

    async def get_at_risk_students(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            collection = self._get_collection()
            students = await collection.find({"enrollment_status": "active"}).to_list(None)

            at_risk = []
            for s in students:
                try:
                    perf = await self.get_student_performance_summary(str(s["_id"]))
                    if perf["academic_standing"] in ["probation", "at_risk"]:
                        at_risk.append({
                            "student_id": str(s["_id"]),
                            "student_name": s.get("student_name", "Unknown"),
                            "gpa": perf["current_gpa"],
                            "attendance_rate": perf["attendance_rate"],
                            "risk_factors": self._identify_risk_factors(perf),
                            "academic_standing": perf["academic_standing"]
                        })
                except Exception as e:
                    logger.warning(f"Error processing student {s.get('_id')}: {str(e)}")
                    continue

            # Sort by GPA ascending then attendance ascending
            at_risk.sort(key=lambda x: (x["gpa"], x["attendance_rate"]))
            return at_risk[:limit]
        except Exception as e:
            logger.error(f"Error fetching at-risk students: {str(e)}")
            raise StudentServiceError("Failed to fetch at-risk students")

    def _identify_risk_factors(self, perf: Dict[str, Any]) -> List[str]:
        factors = []
        if perf["current_gpa"] < 2.0:
            factors.append("Very low GPA")
        elif perf["current_gpa"] < 2.5:
            factors.append("Low GPA")
        if perf["attendance_rate"] < 60:
            factors.append("Very poor attendance")
        elif perf["attendance_rate"] < 75:
            factors.append("Poor attendance")
        if perf["recent_performance"] == "declining":
            factors.append("Declining performance trend")
        if perf["enrolled_courses"] == 0:
            factors.append("Not enrolled in any courses")
        elif perf["enrolled_courses"] < 3:
            factors.append("Low course load")
        return factors

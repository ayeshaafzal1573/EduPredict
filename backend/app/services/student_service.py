"""
Student service for EduPredict
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from app.core.database import get_database
from app.models.student import Student, StudentCreate, StudentUpdate
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

class StudentService:
    def __init__(self):
        self.db = get_database()
        self.user_service = UserService()

    def _get_collection(self):
        """Get students collection"""
        return self.db.get_collection("students")

    async def create_student(self, student_data: StudentCreate, created_by: str) -> Student:
        """Create a new student record"""
        try:
            collection = self._get_collection()
            
            # Check if student already exists
            existing_student = await collection.find_one({"user_id": student_data.user_id})
            if existing_student:
                raise ValueError("Student record already exists for this user")

            # Verify user exists and is a student
            user = await self.user_service.get_user_by_id(student_data.user_id)
            if not user:
                raise ValueError("User not found")
            if user.role != "student":
                raise ValueError("User is not a student")

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
        except Exception as e:
            logger.error(f"Error creating student: {str(e)}")
            raise

    async def get_students(
        self, 
        skip: int = 0, 
        limit: int = 100,
        enrollment_status: Optional[str] = None,
        major: Optional[str] = None,
        academic_year: Optional[str] = None
    ) -> List[Student]:
        """Get list of students with filtering"""
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

            return [Student(**student_data) for student_data in students_data]
        except Exception as e:
            logger.error(f"Error getting students: {str(e)}")
            raise

    async def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Get a student by ID"""
        try:
            collection = self._get_collection()
            
            student_data = await collection.find_one({"_id": ObjectId(student_id)})
            if student_data:
                return Student(**student_data)
            return None
        except Exception as e:
            logger.error(f"Error getting student by ID: {str(e)}")
            return None

    async def get_student_by_user_id(self, user_id: str) -> Optional[Student]:
        """Get a student by user ID"""
        try:
            collection = self._get_collection()
            
            student_data = await collection.find_one({"user_id": user_id})
            if student_data:
                return Student(**student_data)
            return None
        except Exception as e:
            logger.error(f"Error getting student by user ID: {str(e)}")
            return None

    async def update_student(self, student_id: str, student_update: StudentUpdate) -> Student:
        """Update a student record"""
        try:
            collection = self._get_collection()
            
            update_data = {k: v for k, v in student_update.model_dump().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()

            result = await collection.update_one(
                {"_id": ObjectId(student_id)},
                {"$set": update_data}
            )

            if result.modified_count == 0:
                raise ValueError("Student not found or no changes made")

            updated_student = await self.get_student_by_id(student_id)
            if not updated_student:
                raise ValueError("Failed to retrieve updated student")

            return updated_student
        except Exception as e:
            logger.error(f"Error updating student: {str(e)}")
            raise

    async def delete_student(self, student_id: str) -> bool:
        """Delete a student record (soft delete)"""
        try:
            collection = self._get_collection()
            
            result = await collection.update_one(
                {"_id": ObjectId(student_id)},
                {"$set": {"enrollment_status": "inactive", "updated_at": datetime.utcnow()}}
            )

            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deleting student: {str(e)}")
            return False

    async def get_student_performance_summary(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary for a student"""
        try:
            # Get student basic info
            student = await self.get_student_by_id(student_id)
            if not student:
                raise ValueError("Student not found")

            # Get grades
            grades_collection = self.db.get_collection("grades")
            grades = await grades_collection.find({"student_id": student_id}).to_list(None)

            # Get attendance
            attendance_collection = self.db.get_collection("attendance")
            attendance_records = await attendance_collection.find({"student_id": student_id}).to_list(None)

            # Calculate GPA
            current_gpa = 0.0
            if grades:
                total_points = sum(grade.get("grade_points", 0) * grade.get("weight", 1) for grade in grades)
                total_weight = sum(grade.get("weight", 1) for grade in grades)
                current_gpa = total_points / total_weight if total_weight > 0 else 0

            # Calculate attendance rate
            attendance_rate = 0.0
            if attendance_records:
                attended = sum(1 for record in attendance_records if record.get("status") == "present")
                attendance_rate = (attended / len(attendance_records)) * 100

            # Get enrolled courses
            courses_collection = self.db.get_collection("courses")
            enrolled_courses = await courses_collection.count_documents(
                {"students": {"$in": [student_id]}, "is_active": True}
            )

            # Calculate semester GPA (last 4 months)
            four_months_ago = datetime.utcnow() - timedelta(days=120)
            recent_grades = [g for g in grades if g.get("created_at", datetime.min) >= four_months_ago]
            semester_gpa = 0.0
            if recent_grades:
                total_points = sum(grade.get("grade_points", 0) for grade in recent_grades)
                semester_gpa = total_points / len(recent_grades)

            return {
                "student_id": student_id,
                "student_name": student.student_name,
                "current_gpa": round(current_gpa, 2),
                "semester_gpa": round(semester_gpa, 2),
                "attendance_rate": round(attendance_rate, 1),
                "enrolled_courses": enrolled_courses,
                "total_credits": student.total_credits or 0,
                "completed_credits": student.completed_credits or 0,
                "academic_standing": self._determine_academic_standing(current_gpa, attendance_rate),
                "total_assignments": len(grades),
                "recent_performance": self._analyze_recent_performance(recent_grades)
            }
        except Exception as e:
            logger.error(f"Error getting student performance summary: {str(e)}")
            raise

    def _determine_academic_standing(self, gpa: float, attendance_rate: float) -> str:
        """Determine academic standing based on GPA and attendance"""
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
        """Analyze recent performance trend"""
        if len(recent_grades) < 3:
            return "insufficient_data"

        # Sort by date
        sorted_grades = sorted(recent_grades, key=lambda x: x.get("created_at", datetime.min))
        
        # Compare first half vs second half
        mid_point = len(sorted_grades) // 2
        first_half_avg = sum(g.get("grade_points", 0) for g in sorted_grades[:mid_point]) / mid_point
        second_half_avg = sum(g.get("grade_points", 0) for g in sorted_grades[mid_point:]) / (len(sorted_grades) - mid_point)

        if second_half_avg > first_half_avg + 0.3:
            return "improving"
        elif second_half_avg < first_half_avg - 0.3:
            return "declining"
        else:
            return "stable"

    async def get_at_risk_students(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of at-risk students"""
        try:
            collection = self._get_collection()
            
            # Get all active students
            students = await collection.find({"enrollment_status": "active"}).to_list(None)
            
            at_risk_students = []
            for student in students:
                try:
                    performance = await self.get_student_performance_summary(str(student["_id"]))
                    
                    # Determine if student is at risk
                    if (performance["current_gpa"] < 2.5 or 
                        performance["attendance_rate"] < 75 or 
                        performance["academic_standing"] in ["probation", "at_risk"]):
                        
                        at_risk_students.append({
                            "student_id": str(student["_id"]),
                            "student_name": student.get("student_name", "Unknown"),
                            "gpa": performance["current_gpa"],
                            "attendance_rate": performance["attendance_rate"],
                            "risk_factors": self._identify_risk_factors(performance),
                            "academic_standing": performance["academic_standing"]
                        })
                except Exception as e:
                    logger.warning(f"Error processing student {student.get('_id')}: {str(e)}")
                    continue

            # Sort by risk level (lowest GPA and attendance first)
            at_risk_students.sort(key=lambda x: (x["gpa"], x["attendance_rate"]))
            
            return at_risk_students[:limit]
        except Exception as e:
            logger.error(f"Error getting at-risk students: {str(e)}")
            raise

    def _identify_risk_factors(self, performance: Dict[str, Any]) -> List[str]:
        """Identify specific risk factors for a student"""
        risk_factors = []
        
        if performance["current_gpa"] < 2.0:
            risk_factors.append("Very low GPA")
        elif performance["current_gpa"] < 2.5:
            risk_factors.append("Low GPA")
            
        if performance["attendance_rate"] < 60:
            risk_factors.append("Very poor attendance")
        elif performance["attendance_rate"] < 75:
            risk_factors.append("Poor attendance")
            
        if performance["recent_performance"] == "declining":
            risk_factors.append("Declining performance trend")
            
        if performance["enrolled_courses"] == 0:
            risk_factors.append("Not enrolled in any courses")
        elif performance["enrolled_courses"] < 3:
            risk_factors.append("Low course load")

        return risk_factors

    async def search_students(self, query: str, limit: int = 20) -> List[Student]:
        """Search students by name, email, or student ID"""
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

            return [Student(**student_data) for student_data in students_data]
        except Exception as e:
            logger.error(f"Error searching students: {str(e)}")
            raise

    async def get_student_statistics(self) -> Dict[str, Any]:
        """Get overall student statistics"""
        try:
            collection = self._get_collection()
            
            # Basic counts
            total_students = await collection.count_documents({"enrollment_status": "active"})
            
            # Group by academic year
            year_pipeline = [
                {"$match": {"enrollment_status": "active"}},
                {"$group": {"_id": "$academic_year", "count": {"$sum": 1}}}
            ]
            year_stats = await collection.aggregate(year_pipeline).to_list(None)
            
            # Group by major
            major_pipeline = [
                {"$match": {"enrollment_status": "active"}},
                {"$group": {"_id": "$major", "count": {"$sum": 1}}}
            ]
            major_stats = await collection.aggregate(major_pipeline).to_list(None)

            return {
                "total_active_students": total_students,
                "by_academic_year": {stat["_id"]: stat["count"] for stat in year_stats if stat["_id"]},
                "by_major": {stat["_id"]: stat["count"] for stat in major_stats if stat["_id"]},
                "enrollment_trends": []  # This would require historical data
            }
        except Exception as e:
            logger.error(f"Error getting student statistics: {str(e)}")
            raise

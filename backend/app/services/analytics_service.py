"""
Analytics service for EduPredict
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.database import get_database
from app.services.user_service import UserService
from app.services.student_service import StudentService
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.db = get_database()
        self.user_service = UserService()
        self.student_service = StudentService()

    async def get_dashboard_stats(self, role: str, user_id: str) -> Dict[str, Any]:
        """Get dashboard statistics based on user role"""
        try:
            if role == "student":
                return await self._get_student_stats(user_id)
            elif role == "teacher":
                return await self._get_teacher_stats(user_id)
            elif role == "admin":
                return await self._get_admin_stats()
            elif role == "analyst":
                return await self._get_analyst_stats()
            else:
                raise ValueError(f"Invalid role: {role}")
        except Exception as e:
            logger.error(f"Error getting dashboard stats for role {role}: {str(e)}")
            raise

    async def _get_student_stats(self, student_id: str) -> Dict[str, Any]:
        """Get statistics for student dashboard"""
        try:
            # Get student data
            student = await self.student_service.get_student_by_id(student_id)
            if not student:
                raise ValueError("Student not found")

            # Calculate stats from database
            courses_collection = self.db.get_collection("courses")
            grades_collection = self.db.get_collection("grades")
            attendance_collection = self.db.get_collection("attendance")

            # Get enrolled courses
            enrolled_courses = await courses_collection.count_documents(
                {"students": {"$in": [student_id]}}
            )

            # Get recent grades
            recent_grades = await grades_collection.find(
                {"student_id": student_id}
            ).sort("created_at", -1).limit(10).to_list(10)

            # Calculate GPA
            if recent_grades:
                total_points = sum(grade.get("grade_points", 0) for grade in recent_grades)
                gpa = total_points / len(recent_grades)
            else:
                gpa = 0.0

            # Get attendance rate
            total_classes = await attendance_collection.count_documents(
                {"student_id": student_id}
            )
            attended_classes = await attendance_collection.count_documents(
                {"student_id": student_id, "status": "present"}
            )
            
            attendance_rate = (attended_classes / total_classes * 100) if total_classes > 0 else 0

            return {
                "gpa": round(gpa, 2),
                "attendance": round(attendance_rate, 1),
                "courses": enrolled_courses,
                "assignments_due": 3,  # This would come from assignments collection
                "recent_performance": "improving",
                "risk_level": "low"
            }
        except Exception as e:
            logger.error(f"Error getting student stats: {str(e)}")
            raise

    async def _get_teacher_stats(self, teacher_id: str) -> Dict[str, Any]:
        """Get statistics for teacher dashboard"""
        try:
            courses_collection = self.db.get_collection("courses")
            students_collection = self.db.get_collection("students")
            attendance_collection = self.db.get_collection("attendance")

            # Get teacher's courses
            teacher_courses = await courses_collection.find(
                {"teacher_id": teacher_id}
            ).to_list(None)

            course_ids = [str(course["_id"]) for course in teacher_courses]

            # Get total students across all courses
            total_students = 0
            for course in teacher_courses:
                total_students += len(course.get("students", []))

            # Get at-risk students (attendance < 75%)
            at_risk_count = 0
            if course_ids:
                pipeline = [
                    {"$match": {"course_id": {"$in": course_ids}}},
                    {"$group": {
                        "_id": "$student_id",
                        "total_classes": {"$sum": 1},
                        "attended": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}}
                    }},
                    {"$addFields": {
                        "attendance_rate": {"$divide": ["$attended", "$total_classes"]}
                    }},
                    {"$match": {"attendance_rate": {"$lt": 0.75}}}
                ]
                at_risk_students = await attendance_collection.aggregate(pipeline).to_list(None)
                at_risk_count = len(at_risk_students)

            # Calculate average attendance
            if course_ids:
                pipeline = [
                    {"$match": {"course_id": {"$in": course_ids}}},
                    {"$group": {
                        "_id": None,
                        "total_classes": {"$sum": 1},
                        "attended": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}}
                    }}
                ]
                attendance_data = await attendance_collection.aggregate(pipeline).to_list(1)
                if attendance_data:
                    avg_attendance = (attendance_data[0]["attended"] / attendance_data[0]["total_classes"]) * 100
                else:
                    avg_attendance = 0
            else:
                avg_attendance = 0

            return {
                "total_students": total_students,
                "at_risk_students": at_risk_count,
                "average_attendance": round(avg_attendance, 1),
                "classes": len(teacher_courses),
                "recent_activities": 5
            }
        except Exception as e:
            logger.error(f"Error getting teacher stats: {str(e)}")
            raise

    async def _get_admin_stats(self) -> Dict[str, Any]:
        """Get statistics for admin dashboard"""
        try:
            users_collection = self.db.get_collection("users")
            courses_collection = self.db.get_collection("courses")
            
            # Get user counts by role
            total_users = await users_collection.count_documents({"is_active": True})
            total_students = await users_collection.count_documents({"role": "student", "is_active": True})
            total_teachers = await users_collection.count_documents({"role": "teacher", "is_active": True})
            total_courses = await courses_collection.count_documents({"is_active": True})

            # Get recent registrations (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_registrations = await users_collection.count_documents({
                "created_at": {"$gte": thirty_days_ago},
                "is_active": True
            })

            return {
                "total_users": total_users,
                "total_students": total_students,
                "total_teachers": total_teachers,
                "total_courses": total_courses,
                "recent_registrations": recent_registrations,
                "system_health": "good",
                "active_sessions": 45  # This would come from session tracking
            }
        except Exception as e:
            logger.error(f"Error getting admin stats: {str(e)}")
            raise

    async def _get_analyst_stats(self) -> Dict[str, Any]:
        """Get statistics for analyst dashboard"""
        try:
            students_collection = self.db.get_collection("students")
            predictions_collection = self.db.get_collection("predictions")
            
            total_students = await students_collection.count_documents({"is_active": True})
            total_predictions = await predictions_collection.count_documents({})
            
            # Calculate model accuracy (this would be more sophisticated in real implementation)
            accurate_predictions = await predictions_collection.count_documents({"accuracy": {"$gte": 0.8}})
            accuracy_rate = (accurate_predictions / total_predictions * 100) if total_predictions > 0 else 0

            return {
                "total_predictions": total_predictions,
                "accuracy_rate": round(accuracy_rate, 1),
                "models_running": 3,
                "data_points": total_students * 100,  # Approximate data points
                "recent_analyses": 12
            }
        except Exception as e:
            logger.error(f"Error getting analyst stats: {str(e)}")
            raise

    async def get_performance_trends(self, student_id: str) -> Dict[str, Any]:
        """Get performance trends for a student"""
        try:
            grades_collection = self.db.get_collection("grades")
            attendance_collection = self.db.get_collection("attendance")

            # Get grades over time
            grades_pipeline = [
                {"$match": {"student_id": student_id}},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"}
                    },
                    "avg_grade": {"$avg": "$grade_points"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id.year": 1, "_id.month": 1}},
                {"$limit": 12}
            ]

            grade_trends = await grades_collection.aggregate(grades_pipeline).to_list(12)

            # Get attendance trends
            attendance_pipeline = [
                {"$match": {"student_id": student_id}},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$date"},
                        "month": {"$month": "$date"}
                    },
                    "total_classes": {"$sum": 1},
                    "attended": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}}
                }},
                {"$addFields": {
                    "attendance_rate": {"$multiply": [{"$divide": ["$attended", "$total_classes"]}, 100]}
                }},
                {"$sort": {"_id.year": 1, "_id.month": 1}},
                {"$limit": 12}
            ]

            attendance_trends = await attendance_collection.aggregate(attendance_pipeline).to_list(12)

            return {
                "grade_trends": grade_trends,
                "attendance_trends": attendance_trends,
                "trend_analysis": "improving"  # This would be calculated based on trends
            }
        except Exception as e:
            logger.error(f"Error getting performance trends: {str(e)}")
            raise

    async def get_class_analytics(self, class_id: str) -> Dict[str, Any]:
        """Get analytics for a specific class"""
        try:
            courses_collection = self.db.get_collection("courses")
            grades_collection = self.db.get_collection("grades")
            attendance_collection = self.db.get_collection("attendance")

            # Get class info
            course = await courses_collection.find_one({"_id": class_id})
            if not course:
                raise ValueError("Class not found")

            student_ids = course.get("students", [])

            # Get class average grade
            grade_pipeline = [
                {"$match": {"student_id": {"$in": student_ids}, "course_id": class_id}},
                {"$group": {
                    "_id": None,
                    "avg_grade": {"$avg": "$grade_points"},
                    "total_grades": {"$sum": 1}
                }}
            ]

            grade_stats = await grades_collection.aggregate(grade_pipeline).to_list(1)
            avg_grade = grade_stats[0]["avg_grade"] if grade_stats else 0

            # Get class attendance rate
            attendance_pipeline = [
                {"$match": {"student_id": {"$in": student_ids}, "course_id": class_id}},
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
                "class_id": class_id,
                "class_name": course.get("name", "Unknown"),
                "total_students": len(student_ids),
                "average_grade": round(avg_grade, 2),
                "attendance_rate": round(attendance_rate, 1),
                "performance_distribution": {
                    "excellent": 0,  # These would be calculated based on grade ranges
                    "good": 0,
                    "average": 0,
                    "below_average": 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting class analytics: {str(e)}")
            raise

    async def get_institution_analytics(self) -> Dict[str, Any]:
        """Get institution-wide analytics"""
        try:
            users_collection = self.db.get_collection("users")
            courses_collection = self.db.get_collection("courses")
            grades_collection = self.db.get_collection("grades")
            attendance_collection = self.db.get_collection("attendance")

            # Get overall statistics
            total_students = await users_collection.count_documents({"role": "student", "is_active": True})
            total_teachers = await users_collection.count_documents({"role": "teacher", "is_active": True})
            total_courses = await courses_collection.count_documents({"is_active": True})

            # Get institution-wide GPA
            gpa_pipeline = [
                {"$group": {
                    "_id": None,
                    "avg_gpa": {"$avg": "$grade_points"},
                    "total_grades": {"$sum": 1}
                }}
            ]
            gpa_stats = await grades_collection.aggregate(gpa_pipeline).to_list(1)
            institution_gpa = gpa_stats[0]["avg_gpa"] if gpa_stats else 0

            # Get institution-wide attendance
            attendance_pipeline = [
                {"$group": {
                    "_id": None,
                    "total_classes": {"$sum": 1},
                    "attended": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}}
                }}
            ]
            attendance_stats = await attendance_collection.aggregate(attendance_pipeline).to_list(1)
            institution_attendance = 0
            if attendance_stats and attendance_stats[0]["total_classes"] > 0:
                institution_attendance = (attendance_stats[0]["attended"] / attendance_stats[0]["total_classes"]) * 100

            return {
                "total_students": total_students,
                "total_teachers": total_teachers,
                "total_courses": total_courses,
                "institution_gpa": round(institution_gpa, 2),
                "institution_attendance": round(institution_attendance, 1),
                "enrollment_trends": [],  # This would be calculated based on historical data
                "performance_trends": []   # This would be calculated based on historical data
            }
        except Exception as e:
            logger.error(f"Error getting institution analytics: {str(e)}")
            raise

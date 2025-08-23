"""
Attendance service for EduPredict
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from bson import ObjectId
from app.core.database import get_database
from app.models.attendance import Attendance, AttendanceCreate, AttendanceUpdate, AttendanceBulkCreate, AttendanceStats
from app.services.user_service import UserService
from app.services.course_service import CourseService
import logging

logger = logging.getLogger(__name__)

class AttendanceService:
    def __init__(self):
        self.db = get_database()
        self.user_service = UserService()
        self.course_service = CourseService()

    def _get_collection(self):
        """Get attendance collection"""
        return self.db.get_collection("attendance")

    async def create_attendance(self, attendance_data: AttendanceCreate, marked_by: str) -> Attendance:
        """Create a new attendance record"""
        try:
            collection = self._get_collection()
            
            # Check if attendance already exists for this student, course, and date
            existing = await collection.find_one({
                "student_id": attendance_data.student_id,
                "course_id": attendance_data.course_id,
                "date": attendance_data.date
            })
            
            if existing:
                raise ValueError("Attendance already recorded for this student on this date")

            # Get student and course information
            student = await self.user_service.get_user_by_id(attendance_data.student_id)
            course = await self.course_service.get_course_by_id(attendance_data.course_id)
            marker = await self.user_service.get_user_by_id(marked_by)

            if not student:
                raise ValueError("Student not found")
            if not course:
                raise ValueError("Course not found")
            if not marker:
                raise ValueError("Marker not found")

            # Verify student is enrolled in the course
            if attendance_data.student_id not in course.students:
                raise ValueError("Student is not enrolled in this course")

            attendance_dict = attendance_data.model_dump()
            attendance_dict.update({
                "_id": ObjectId(),
                "student_name": f"{student.first_name} {student.last_name}",
                "course_name": course.name,
                "marked_by": marked_by,
                "marked_by_name": f"{marker.first_name} {marker.last_name}",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

            result = await collection.insert_one(attendance_dict)
            attendance_dict["_id"] = result.inserted_id

            return Attendance(**attendance_dict)
        except Exception as e:
            logger.error(f"Error creating attendance record: {str(e)}")
            raise

    async def create_bulk_attendance(self, bulk_data: AttendanceBulkCreate, marked_by: str) -> List[Attendance]:
        """Create multiple attendance records at once"""
        try:
            collection = self._get_collection()
            
            # Get course information
            course = await self.course_service.get_course_by_id(bulk_data.course_id)
            if not course:
                raise ValueError("Course not found")

            marker = await self.user_service.get_user_by_id(marked_by)
            if not marker:
                raise ValueError("Marker not found")

            attendance_records = []
            for record in bulk_data.attendance_records:
                student_id = record.get("student_id")
                status = record.get("status")
                notes = record.get("notes", "")

                # Check if attendance already exists
                existing = await collection.find_one({
                    "student_id": student_id,
                    "course_id": bulk_data.course_id,
                    "date": bulk_data.date
                })
                
                if existing:
                    continue  # Skip if already exists

                # Get student information
                student = await self.user_service.get_user_by_id(student_id)
                if not student:
                    continue  # Skip if student not found

                # Verify student is enrolled
                if student_id not in course.students:
                    continue  # Skip if not enrolled

                attendance_dict = {
                    "_id": ObjectId(),
                    "student_id": student_id,
                    "course_id": bulk_data.course_id,
                    "date": bulk_data.date,
                    "status": status,
                    "notes": notes,
                    "student_name": f"{student.first_name} {student.last_name}",
                    "course_name": course.name,
                    "marked_by": marked_by,
                    "marked_by_name": f"{marker.first_name} {marker.last_name}",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }

                attendance_records.append(attendance_dict)

            if attendance_records:
                result = await collection.insert_many(attendance_records)
                for i, inserted_id in enumerate(result.inserted_ids):
                    attendance_records[i]["_id"] = inserted_id

            return [Attendance(**record) for record in attendance_records]
        except Exception as e:
            logger.error(f"Error creating bulk attendance: {str(e)}")
            raise

    async def get_attendance_records(
        self,
        skip: int = 0,
        limit: int = 100,
        student_id: Optional[str] = None,
        course_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        user_role: str = "student",
        user_id: str = None
    ) -> List[Attendance]:
        """Get attendance records with filtering"""
        try:
            collection = self._get_collection()
            
            query = {}
            
            if student_id:
                query["student_id"] = student_id
            
            if course_id:
                query["course_id"] = course_id
            
            if date_from or date_to:
                date_query = {}
                if date_from:
                    date_query["$gte"] = date_from
                if date_to:
                    date_query["$lte"] = date_to
                query["date"] = date_query

            # Role-based filtering
            if user_role == "teacher":
                # Teachers can only see attendance for their courses
                teacher_courses = await self.course_service.get_courses(teacher_id=user_id)
                course_ids = [str(course.id) for course in teacher_courses]
                if course_id and course_id not in course_ids:
                    return []  # Teacher doesn't have access to this course
                if not course_id:
                    query["course_id"] = {"$in": course_ids}

            cursor = collection.find(query).skip(skip).limit(limit).sort("date", -1)
            attendance_data = await cursor.to_list(length=limit)

            return [Attendance(**record) for record in attendance_data]
        except Exception as e:
            logger.error(f"Error getting attendance records: {str(e)}")
            raise

    async def update_attendance(self, attendance_id: str, attendance_update: AttendanceUpdate) -> Attendance:
        """Update an attendance record"""
        try:
            collection = self._get_collection()
            
            update_data = {k: v for k, v in attendance_update.model_dump().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()

            result = await collection.update_one(
                {"_id": ObjectId(attendance_id)},
                {"$set": update_data}
            )

            if result.modified_count == 0:
                raise ValueError("Attendance record not found or no changes made")

            updated_record = await collection.find_one({"_id": ObjectId(attendance_id)})
            if not updated_record:
                raise ValueError("Failed to retrieve updated attendance record")

            return Attendance(**updated_record)
        except Exception as e:
            logger.error(f"Error updating attendance record: {str(e)}")
            raise

    async def delete_attendance(self, attendance_id: str) -> bool:
        """Delete an attendance record"""
        try:
            collection = self._get_collection()
            
            result = await collection.delete_one({"_id": ObjectId(attendance_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting attendance record: {str(e)}")
            return False

    async def get_student_attendance_stats(
        self, 
        student_id: str, 
        course_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> AttendanceStats:
        """Get attendance statistics for a student"""
        try:
            collection = self._get_collection()
            
            # Set default date range if not provided
            if not date_from:
                date_from = date.today() - timedelta(days=90)  # Last 3 months
            if not date_to:
                date_to = date.today()

            query = {
                "student_id": student_id,
                "date": {"$gte": date_from, "$lte": date_to}
            }
            
            if course_id:
                query["course_id"] = course_id

            # Aggregate attendance data
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": None,
                    "total_classes": {"$sum": 1},
                    "attended": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}},
                    "absent": {"$sum": {"$cond": [{"$eq": ["$status", "absent"]}, 1, 0]}},
                    "late": {"$sum": {"$cond": [{"$eq": ["$status", "late"]}, 1, 0]}},
                    "excused": {"$sum": {"$cond": [{"$eq": ["$status", "excused"]}, 1, 0]}}
                }}
            ]

            result = await collection.aggregate(pipeline).to_list(1)
            
            if result:
                stats = result[0]
                attendance_rate = (stats["attended"] / stats["total_classes"] * 100) if stats["total_classes"] > 0 else 0
                
                return AttendanceStats(
                    total_classes=stats["total_classes"],
                    attended=stats["attended"],
                    absent=stats["absent"],
                    late=stats["late"],
                    excused=stats["excused"],
                    attendance_rate=round(attendance_rate, 2),
                    period_start=date_from,
                    period_end=date_to
                )
            else:
                return AttendanceStats(
                    total_classes=0,
                    attended=0,
                    absent=0,
                    late=0,
                    excused=0,
                    attendance_rate=0.0,
                    period_start=date_from,
                    period_end=date_to
                )
        except Exception as e:
            logger.error(f"Error getting student attendance stats: {str(e)}")
            raise

    async def get_course_attendance_summary(self, course_id: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> Dict[str, Any]:
        """Get attendance summary for a course"""
        try:
            collection = self._get_collection()
            
            # Set default date range if not provided
            if not date_from:
                date_from = date.today() - timedelta(days=30)  # Last month
            if not date_to:
                date_to = date.today()

            query = {
                "course_id": course_id,
                "date": {"$gte": date_from, "$lte": date_to}
            }

            # Get overall course attendance stats
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": None,
                    "total_classes": {"$sum": 1},
                    "total_attended": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}},
                    "total_absent": {"$sum": {"$cond": [{"$eq": ["$status", "absent"]}, 1, 0]}},
                    "unique_students": {"$addToSet": "$student_id"}
                }}
            ]

            overall_stats = await collection.aggregate(pipeline).to_list(1)
            
            # Get per-student stats
            student_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$student_id",
                    "student_name": {"$first": "$student_name"},
                    "total_classes": {"$sum": 1},
                    "attended": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}},
                    "absent": {"$sum": {"$cond": [{"$eq": ["$status", "absent"]}, 1, 0]}}
                }},
                {"$addFields": {
                    "attendance_rate": {"$multiply": [{"$divide": ["$attended", "$total_classes"]}, 100]}
                }},
                {"$sort": {"attendance_rate": 1}}  # Sort by attendance rate (lowest first)
            ]

            student_stats = await collection.aggregate(student_pipeline).to_list(None)

            if overall_stats:
                stats = overall_stats[0]
                overall_rate = (stats["total_attended"] / stats["total_classes"] * 100) if stats["total_classes"] > 0 else 0
                
                return {
                    "course_id": course_id,
                    "period_start": date_from.isoformat(),
                    "period_end": date_to.isoformat(),
                    "overall_attendance_rate": round(overall_rate, 2),
                    "total_classes_held": stats["total_classes"],
                    "total_students": len(stats["unique_students"]),
                    "student_stats": student_stats,
                    "at_risk_students": [s for s in student_stats if s["attendance_rate"] < 75]
                }
            else:
                return {
                    "course_id": course_id,
                    "period_start": date_from.isoformat(),
                    "period_end": date_to.isoformat(),
                    "overall_attendance_rate": 0.0,
                    "total_classes_held": 0,
                    "total_students": 0,
                    "student_stats": [],
                    "at_risk_students": []
                }
        except Exception as e:
            logger.error(f"Error getting course attendance summary: {str(e)}")
            raise

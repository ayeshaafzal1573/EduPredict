"""
Attendance service for EduPredict (clean version)
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
    def __init__(self, db, user_service, course_service):
        self.db = db
        self.user_service = user_service
        self.course_service = course_service


    def _get_collection(self):
        return self.db.get_collection("attendance")

    async def create_attendance(self, attendance_data: AttendanceCreate, marked_by: str) -> Attendance:
        """Create a new attendance record"""
        collection = self._get_collection()

        # Prevent duplicate
        existing = await collection.find_one({
            "student_id": attendance_data.student_id,
            "course_id": attendance_data.course_id,
            "date": attendance_data.date
        })
        if existing:
            raise ValueError("Attendance already recorded for this student on this date")

        # Validate
        student = await self.user_service.get_user_by_id(attendance_data.student_id)
        course = await self.course_service.get_course_by_id(attendance_data.course_id)
        marker = await self.user_service.get_user_by_id(marked_by)

        if not student:
            raise ValueError("Student not found")
        if not course:
            raise ValueError("Course not found")
        if not marker:
            raise ValueError("Marker not found")
        if attendance_data.student_id not in course.students:
            raise ValueError("Student is not enrolled in this course")

        attendance_dict = attendance_data.model_dump()
        attendance_dict.update({
            "_id": ObjectId(),
            "marked_by": marked_by,
            "marked_by_name": f"{marker.first_name} {marker.last_name}",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })

        result = await collection.insert_one(attendance_dict)
        attendance_dict["_id"] = result.inserted_id

        return Attendance(**attendance_dict)

    async def create_bulk_attendance(self, bulk_data: AttendanceBulkCreate, marked_by: str) -> List[Attendance]:
        """Bulk insert attendance"""
        collection = self._get_collection()

        course = await self.course_service.get_course_by_id(bulk_data.course_id)
        if not course:
            raise ValueError("Course not found")

        marker = await self.user_service.get_user_by_id(marked_by)
        if not marker:
            raise ValueError("Marker not found")

        attendance_records = []
        for record in bulk_data.attendance_records:
            student_id = record.get("student_id")

            # Skip duplicates
            exists = await collection.find_one({
                "student_id": student_id,
                "course_id": bulk_data.course_id,
                "date": bulk_data.date
            })
            if exists:
                continue

            student = await self.user_service.get_user_by_id(student_id)
            if not student or student_id not in course.students:
                continue

            attendance_dict = {
                "_id": ObjectId(),
                "student_id": student_id,
                "course_id": bulk_data.course_id,
                "date": bulk_data.date,
                "status": record.get("status"),
                "notes": record.get("notes", ""),
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

        return [Attendance(**r) for r in attendance_records]

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
        """Get attendance with filters"""
        collection = self._get_collection()
        query = {}

        if student_id:
            query["student_id"] = student_id
        if course_id:
            query["course_id"] = course_id
        if date_from or date_to:
            query["date"] = {}
            if date_from:
                query["date"]["$gte"] = date_from
            if date_to:
                query["date"]["$lte"] = date_to

        # Role restriction
        if user_role == "teacher":
            teacher_courses = await self.course_service.get_courses(teacher_id=user_id)
            course_ids = [str(c.id) for c in teacher_courses]
            if course_id and course_id not in course_ids:
                return []
            if not course_id:
                query["course_id"] = {"$in": course_ids}

        cursor = collection.find(query).skip(skip).limit(limit).sort("date", -1)
        data = await cursor.to_list(length=limit)
        return [Attendance(**rec) for rec in data]

    async def update_attendance(self, attendance_id: str, attendance_update: AttendanceUpdate) -> Attendance:
        """Update attendance"""
        collection = self._get_collection()
        update_data = {k: v for k, v in attendance_update.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()

        result = await collection.update_one({"_id": ObjectId(attendance_id)}, {"$set": update_data})
        if result.modified_count == 0:
            raise ValueError("Attendance not found or no changes made")

        updated = await collection.find_one({"_id": ObjectId(attendance_id)})
        return Attendance(**updated)

    async def delete_attendance(self, attendance_id: str) -> bool:
        """Delete attendance"""
        collection = self._get_collection()
        result = await collection.delete_one({"_id": ObjectId(attendance_id)})
        return result.deleted_count > 0

    async def get_student_attendance_stats(self, student_id: str, course_id: Optional[str] = None,
                                           date_from: Optional[date] = None, date_to: Optional[date] = None) -> AttendanceStats:
        """Stats for a student"""
        collection = self._get_collection()
        if not date_from:
            date_from = date.today() - timedelta(days=90)
        if not date_to:
            date_to = date.today()

        query = {"student_id": student_id, "date": {"$gte": date_from, "$lte": date_to}}
        if course_id:
            query["course_id"] = course_id

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

        if not result:
            return AttendanceStats(total_classes=0, attended=0, absent=0, late=0, excused=0,
                                   attendance_rate=0.0, period_start=date_from, period_end=date_to)

        stats = result[0]
        rate = (stats["attended"] / stats["total_classes"] * 100) if stats["total_classes"] > 0 else 0
        return AttendanceStats(
            total_classes=stats["total_classes"],
            attended=stats["attended"],
            absent=stats["absent"],
            late=stats["late"],
            excused=stats["excused"],
            attendance_rate=round(rate, 2),
            period_start=date_from,
            period_end=date_to
        )

    async def get_course_attendance_summary(self, course_id: str,
                                            date_from: Optional[date] = None, date_to: Optional[date] = None) -> Dict[str, Any]:
        """Course-level summary (lean, no names inside DB)"""
        collection = self._get_collection()
        if not date_from:
            date_from = date.today() - timedelta(days=30)
        if not date_to:
            date_to = date.today()

        query = {"course_id": course_id, "date": {"$gte": date_from, "$lte": date_to}}

        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$student_id",
                "total_classes": {"$sum": 1},
                "attended": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}},
                "absent": {"$sum": {"$cond": [{"$eq": ["$status", "absent"]}, 1, 0]}},
            }},
            {"$addFields": {
                "attendance_rate": {"$multiply": [{"$divide": ["$attended", "$total_classes"]}, 100]}
            }},
            {"$sort": {"attendance_rate": 1}}
        ]

        student_stats = await collection.aggregate(pipeline).to_list(None)
        overall_rate = (sum(s["attended"] for s in student_stats) /
                        sum(s["total_classes"] for s in student_stats) * 100) if student_stats else 0

        return {
            "course_id": course_id,
            "period_start": date_from.isoformat(),
            "period_end": date_to.isoformat(),
            "overall_attendance_rate": round(overall_rate, 2),
            "total_classes_held": sum(s["total_classes"] for s in student_stats),
            "total_students": len(student_stats),
            "student_stats": student_stats,
            "at_risk_students": [s for s in student_stats if s["attendance_rate"] < 75]
        }

from typing import List
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
from app.core.database import get_attendance_collection
from app.models.attendance import Attendance, AttendanceCreate, AttendanceUpdate, AttendanceStats
from datetime import datetime

class AttendanceService:
    """Service for attendance-related operations"""

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_attendance(self, attendance: AttendanceCreate) -> Attendance:
        """Create a new attendance record"""
        try:
            attendance_dict = attendance.dict()
            attendance_dict.update({
                "marked_by": "system",  # This should come from current user
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            result = await self.collection.insert_one(attendance_dict)
            attendance_in_db = await self.collection.find_one({"_id": result.inserted_id})
            
            # Convert to Attendance model
            attendance_data = {
                "id": str(attendance_in_db["_id"]),
                "student_id": attendance_in_db["student_id"],
                "course_id": attendance_in_db["course_id"],
                "date": attendance_in_db["date"],
                "status": attendance_in_db["status"],
                "notes": attendance_in_db.get("notes"),
                "marked_by": attendance_in_db["marked_by"],
                "created_at": attendance_in_db["created_at"],
                "updated_at": attendance_in_db["updated_at"]
            }
            
            return Attendance(**attendance_data)
        except Exception as e:
            logger.error(f"Failed to create attendance for student {attendance.student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def generate_attendance_stats(self, student_id: str, course_id: str) -> AttendanceStats:
        """Generate attendance statistics"""
        try:
            records = await self.collection.find({"student_id": student_id, "course_id": course_id}).to_list(length=1000)
            if not records:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attendance records found")
            
            total = len(records)
            attended = len([r for r in records if r["status"] == "present"])
            absent = len([r for r in records if r["status"] == "absent"])
            late = len([r for r in records if r["status"] == "late"])
            excused = len([r for r in records if r["status"] == "excused"])
            
            attendance_rate = (attended / total * 100) if total > 0 else 0.0
            
            # Get date range
            dates = [r["date"] for r in records]
            period_start = min(dates) if dates else datetime.now().date()
            period_end = max(dates) if dates else datetime.now().date()
            
            stats = {
                "total_classes": total,
                "attended": attended,
                "absent": absent,
                "late": late,
                "excused": excused,
                "attendance_rate": round(attendance_rate, 2),
                "period_start": period_start,
                "period_end": period_end,
                "hdfs_path": None
            }
            
            return AttendanceStats(**stats)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to generate attendance stats for student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_attendance_service(collection: AsyncIOMotorCollection = Depends(get_attendance_collection)) -> AttendanceService:
    """Dependency for AttendanceService"""
    return AttendanceService(collection)
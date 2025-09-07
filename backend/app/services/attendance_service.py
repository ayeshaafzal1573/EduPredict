import asyncio
from typing import List
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
from app.core.database import get_attendance_collection
from app.models.attendance import Attendance, AttendanceCreate, AttendanceUpdate, AttendanceStats
from app.core.hdfs_utils import HDFSClient

class AttendanceService:
    """Service for attendance-related operations"""

    def __init__(self, collection: AsyncIOMotorCollection, hdfs_client: HDFSClient):
        self.collection = collection
        self.hdfs_client = hdfs_client

    async def create_attendance(self, attendance: AttendanceCreate) -> Attendance:
        """Create a new attendance record"""
        try:
            result = await self.collection.insert_one(attendance.dict())
            attendance_in_db = await self.collection.find_one({"_id": result.inserted_id})
            return Attendance(**attendance_in_db)
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
            stats = {
                "total_classes": total,
                "attended": sum(1 for r in records if r["status"] == "present"),
                "absent": sum(1 for r in records if r["status"] == "absent"),
                "late": sum(1 for r in records if r["status"] == "late"),
                "excused": sum(1 for r in records if r["status"] == "excused"),
                "attendance_rate": (sum(1 for r in records if r["status"] in ["present", "late"]) / total * 100) if total > 0 else 0.0,
                "period_start": min(r["date"] for r in records),
                "period_end": max(r["date"] for r in records)
            }
            hdfs_path = f"/edupredict/attendance/{student_id}/{course_id}/stats.json"
            self.hdfs_client.save_data(str(stats).encode(), hdfs_path)
            stats["hdfs_path"] = hdfs_path
            return AttendanceStats(**stats)
        except Exception as e:
            logger.error(f"Failed to generate attendance stats for student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_attendance_service(collection: AsyncIOMotorCollection = Depends(get_attendance_collection)) -> AttendanceService:
    """Dependency for AttendanceService"""
    return AttendanceService(collection, HDFSClient())
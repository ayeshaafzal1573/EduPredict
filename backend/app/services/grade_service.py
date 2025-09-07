import asyncio
from typing import List
from fastapi import HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
from app.core.database import get_grades_collection
from app.models.grade import Grade, GradeCreate, GradeUpdate, GradeStats
from app.core.hdfs_utils import HDFSClient

class GradeService:
    """Service for grade-related operations"""

    def __init__(self, collection: AsyncIOMotorCollection, hdfs_client: HDFSClient):
        self.collection = collection
        self.hdfs_client = hdfs_client

    async def create_grade(self, grade: GradeCreate) -> Grade:
        """Create a new grade record"""
        try:
            result = await self.collection.insert_one(grade.dict())
            grade_in_db = await self.collection.find_one({"_id": result.inserted_id})
            return Grade(**grade_in_db)
        except Exception as e:
            logger.error(f"Failed to create grade for student {grade.student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def generate_grade_stats(self, student_id: str, course_id: str) -> GradeStats:
        """Generate grade statistics"""
        try:
            grades = await self.collection.find({"student_id": student_id, "course_id": course_id}).to_list(length=1000)
            if not grades:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No grades found")
            total_assignments = len(grades)
            completed = sum(1 for g in grades if g["percentage"] is not None)
            avg_percentage = sum(g["percentage"] for g in grades if g["percentage"] is not None) / completed if completed > 0 else 0.0
            stats = {
                "total_assignments": total_assignments,
                "completed_assignments": completed,
                "average_percentage": avg_percentage,
                "average_grade_points": sum(g["grade_points"] for g in grades if g["grade_points"] is not None) / completed if completed > 0 else 0.0,
                "current_letter_grade": "A" if avg_percentage >= 90 else "B" if avg_percentage >= 80 else "C" if avg_percentage >= 70 else "F",
                "grade_distribution": {"A": sum(1 for g in grades if g["letter_grade"] == "A")},
                "trend": "Stable"  # Placeholder for ML trend analysis
            }
            hdfs_path = f"/edupredict/grades/{student_id}/{course_id}/stats.json"
            self.hdfs_client.save_data(str(stats).encode(), hdfs_path)
            stats["hdfs_path"] = hdfs_path
            return GradeStats(**stats)
        except Exception as e:
            logger.error(f"Failed to generate grade stats for student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_grade_service(collection: AsyncIOMotorCollection = Depends(get_grades_collection)) -> GradeService:
    """Dependency for GradeService"""
    return GradeService(collection, HDFSClient())
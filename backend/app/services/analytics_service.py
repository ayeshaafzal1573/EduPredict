

from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_students_collection, get_grades_collection, get_attendance_collection
from app.core.hdfs_utils import HDFSClient
from app.models.student import StudentAnalytics
from loguru import logger
import pandas as pd
from typing import Dict

class AnalyticsService:
    """Service for generating student analytics"""

    def __init__(self, students_collection: AsyncIOMotorCollection, grades_collection: AsyncIOMotorCollection, attendance_collection: AsyncIOMotorCollection):
        self.students_collection = students_collection
        self.grades_collection = grades_collection
        self.attendance_collection = attendance_collection
        self.hdfs_client = HDFSClient()

    async def generate_comprehensive_analytics(self, student_id: str) -> StudentAnalytics:
        """
        Generate comprehensive analytics for a student
        
        Args:
            student_id: Unique student ID
        
        Returns:
            StudentAnalytics: Comprehensive analytics data
        
        Raises:
            HTTPException: If student not found
        """
        try:
            student = await self.students_collection.find_one({"student_id": student_id})
            if not student:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
            
            # Fetch grades and attendance
            grades = await self.grades_collection.find({"student_id": student_id}).to_list(length=None)
            attendance = await self.attendance_collection.find({"student_id": student_id}).to_list(length=None)
            
            # Placeholder ML logic
            grades_df = pd.DataFrame(grades)
            attendance_df = pd.DataFrame(attendance)
            performance_score = grades_df["score"].mean() if not grades_df.empty else 0.0
            dropout_risk = 0.1 if attendance_df["status"].eq("present").mean() < 0.8 else 0.05
            
            analytics_data = {
                "student_id": student_id,
                "performance_score": float(performance_score),
                "dropout_risk": float(dropout_risk),
                "hdfs_path": f"/edupredict/analytics/{student_id}_comprehensive.json"
            }
            
            # Save to HDFS
            self.hdfs_client.save_data(
                data=json.dumps(analytics_data).encode(),
                hdfs_path=analytics_data["hdfs_path"]
            )
            
            return StudentAnalytics(**analytics_data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to generate analytics for student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_analytics_service(
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    grades_collection: AsyncIOMotorCollection = Depends(get_grades_collection),
    attendance_collection: AsyncIOMotorCollection = Depends(get_attendance_collection)
) -> AnalyticsService:
    """Dependency for AnalyticsService"""
    return AnalyticsService(students_collection, grades_collection, attendance_collection)

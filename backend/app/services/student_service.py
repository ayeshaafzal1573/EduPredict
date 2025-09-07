
"""
Student service for EduPredict
"""

from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_students_collection
from app.core.hdfs_utils import HDFSClient
from app.models.student import Student, StudentCreate, StudentUpdate, StudentAnalytics
from loguru import logger
from typing import Optional
from datetime import datetime

class StudentService:
    """Service for student-related operations"""

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
        self.hdfs_client = HDFSClient()

    async def create_student(self, student: StudentCreate) -> Student:
        """
        Create a new student
        
        Args:
            student: Student creation data
        
        Returns:
            Student: Created student data
        
        Raises:
            HTTPException: If student ID exists
        """
        try:
            existing = await self.collection.find_one({"student_id": student.student_id})
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student ID already exists")
            student_dict = student.dict()
            student_dict["created_at"] = datetime.utcnow()
            student_dict["updated_at"] = datetime.utcnow()
            result = await self.collection.insert_one(student_dict)
            created_student = await self.collection.find_one({"_id": result.inserted_id})
            return Student(**created_student)
        except Exception as e:
            logger.error(f"Failed to create student {student.student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_student(self, student_id: str) -> Student:
        """
        Retrieve a student by ID
        
        Args:
            student_id: Unique student ID (e.g., STU-1234)
        
        Returns:
            Student: Student data
        
        Raises:
            HTTPException: If student not found
        """
        try:
            student = await self.collection.find_one({"student_id": student_id})
            if not student:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
            return Student(**student)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to retrieve student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def update_student(self, student_id: str, update_data: StudentUpdate) -> Student:
        """
        Update a student's information
        
        Args:
            student_id: Unique student ID
            update_data: Updated student data
        
        Returns:
            Student: Updated student data
        
        Raises:
            HTTPException: If student not found
        """
        try:
            update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
            if not update_dict:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid update data provided")
            update_dict["updated_at"] = datetime.utcnow()
            result = await self.collection.update_one(
                {"student_id": student_id},
                {"$set": update_dict}
            )
            if result.modified_count == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
            updated_student = await self.collection.find_one({"student_id": student_id})
            return Student(**updated_student)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to update student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def generate_analytics(self, student_id: str) -> StudentAnalytics:
        """
        Generate analytics for a student (placeholder for ML)
        
        Args:
            student_id: Unique student ID
        
        Returns:
            StudentAnalytics: Analytics data
        
        Raises:
            HTTPException: If student not found
        """
        try:
            student = await self.collection.find_one({"student_id": student_id})
            if not student:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
            # Placeholder ML logic
            analytics_data = {
                "student_id": student_id,
                "performance_score": 85.0,  # Example
                "dropout_risk": 0.1,       # Example
                "hdfs_path": f"/edupredict/analytics/{student_id}.json"
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

async def get_student_service(collection: AsyncIOMotorCollection = Depends(get_students_collection)) -> StudentService:
    """Dependency for StudentService"""
    return StudentService(collection)

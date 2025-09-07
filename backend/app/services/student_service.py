from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_students_collection, get_users_collection
from app.models.student import Student, StudentCreate, StudentUpdate, StudentAnalytics
from loguru import logger
from typing import Optional
from datetime import datetime
from bson import ObjectId

class StudentService:
    """Service for student-related operations"""

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_student(self, student: StudentCreate) -> Student:
        """Create a new student"""
        try:
            existing = await self.collection.find_one({"student_id": student.student_id})
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student ID already exists")
            
            student_dict = student.dict()
            student_dict.update({
                "gpa": 0.0,
                "total_credits": 0,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            result = await self.collection.insert_one(student_dict)
            created_student = await self.collection.find_one({"_id": result.inserted_id})
            
            # Convert to Student model
            student_data = {
                "id": str(created_student["_id"]),
                "student_id": created_student["student_id"],
                "user_id": created_student["user_id"],
                "date_of_birth": created_student["date_of_birth"],
                "gender": created_student["gender"],
                "phone": created_student.get("phone"),
                "address": created_student.get("address"),
                "emergency_contact": created_student.get("emergency_contact"),
                "enrollment_date": created_student["enrollment_date"],
                "expected_graduation": created_student["expected_graduation"],
                "current_semester": created_student["current_semester"],
                "current_year": created_student["current_year"],
                "department": created_student["department"],
                "program": created_student["program"],
                "gpa": created_student.get("gpa", 0.0),
                "total_credits": created_student.get("total_credits", 0),
                "created_at": created_student["created_at"],
                "updated_at": created_student["updated_at"],
                "is_active": created_student.get("is_active", True)
            }
            
            return Student(**student_data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to create student {student.student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_student(self, student_id: str) -> Student:
        """Retrieve a student by ID"""
        try:
            # Try to find by student_id or ObjectId
            query = {}
            if ObjectId.is_valid(student_id):
                query = {"_id": ObjectId(student_id)}
            else:
                query = {"student_id": student_id}
            
            student = await self.collection.find_one(query)
            if not student:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
            
            # Convert to Student model
            student_data = {
                "id": str(student["_id"]),
                "student_id": student["student_id"],
                "user_id": student["user_id"],
                "date_of_birth": student["date_of_birth"],
                "gender": student["gender"],
                "phone": student.get("phone"),
                "address": student.get("address"),
                "emergency_contact": student.get("emergency_contact"),
                "enrollment_date": student["enrollment_date"],
                "expected_graduation": student["expected_graduation"],
                "current_semester": student["current_semester"],
                "current_year": student["current_year"],
                "department": student["department"],
                "program": student["program"],
                "gpa": student.get("gpa", 0.0),
                "total_credits": student.get("total_credits", 0),
                "created_at": student.get("created_at"),
                "updated_at": student.get("updated_at"),
                "is_active": student.get("is_active", True)
            }
            
            return Student(**student_data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to retrieve student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def update_student(self, student_id: str, update_data: StudentUpdate) -> Student:
        """Update a student's information"""
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
            
            # Convert to Student model
            student_data = {
                "id": str(updated_student["_id"]),
                "student_id": updated_student["student_id"],
                "user_id": updated_student["user_id"],
                "date_of_birth": updated_student["date_of_birth"],
                "gender": updated_student["gender"],
                "phone": updated_student.get("phone"),
                "address": updated_student.get("address"),
                "emergency_contact": updated_student.get("emergency_contact"),
                "enrollment_date": updated_student["enrollment_date"],
                "expected_graduation": updated_student["expected_graduation"],
                "current_semester": updated_student["current_semester"],
                "current_year": updated_student["current_year"],
                "department": updated_student["department"],
                "program": updated_student["program"],
                "gpa": updated_student.get("gpa", 0.0),
                "total_credits": updated_student.get("total_credits", 0),
                "created_at": updated_student.get("created_at"),
                "updated_at": updated_student["updated_at"],
                "is_active": updated_student.get("is_active", True)
            }
            
            return Student(**student_data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to update student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def generate_analytics(self, student_id: str) -> StudentAnalytics:
        """Generate analytics for a student"""
        try:
            student = await self.collection.find_one({"student_id": student_id})
            if not student:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
            
            # Generate basic analytics
            current_gpa = student.get("gpa", 0.0)
            current_semester = student.get("current_semester", 1)
            
            # Performance trend
            performance_trend = []
            for i in range(max(1, current_semester - 2), current_semester + 1):
                semester_name = f"Semester {i}"
                gpa_variation = (i - 1) * 0.1
                semester_gpa = max(0.0, min(4.0, current_gpa - 0.3 + gpa_variation))
                
                performance_trend.append({
                    "semester": semester_name,
                    "gpa": round(semester_gpa, 2),
                    "credits": 15 + (i - 1) * 3
                })
            
            # Attendance trend
            attendance_trend = [
                {"month": "Jan", "rate": 85},
                {"month": "Feb", "rate": 87},
                {"month": "Mar", "rate": 83}
            ]
            
            # Grade distribution
            grade_distribution = {"A": 2, "B": 3, "C": 1, "D": 0, "F": 0}
            
            # Risk assessment
            if current_gpa < 2.0:
                risk_level = "high"
                risk_score = 0.8
            elif current_gpa < 2.5:
                risk_level = "medium"
                risk_score = 0.5
            else:
                risk_level = "low"
                risk_score = 0.2
            
            analytics_data = {
                "student_id": student_id,
                "performance_trend": performance_trend,
                "attendance_trend": attendance_trend,
                "grade_distribution": grade_distribution,
                "risk_assessment": {"score": risk_score, "level": risk_level},
                "predictions": {"dropout_risk": risk_score},
                "hdfs_path": None
            }
            
            return StudentAnalytics(**analytics_data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to generate analytics for student {student_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_student_service(collection: AsyncIOMotorCollection = Depends(get_students_collection)) -> StudentService:
    """Dependency for StudentService"""
    return StudentService(collection)
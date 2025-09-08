from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user, TokenData
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_students_collection, get_users_collection
from app.models.student import Student, StudentCreate, StudentUpdate
from loguru import logger
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/")
async def get_students(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Get list of students"""
    try:
        students = await students_collection.find({}).skip(skip).limit(limit).to_list(length=limit)
        
        result = []
        for student in students:
            user = await users_collection.find_one({"_id": ObjectId(student["user_id"])})
            if user:
                result.append({
                    "id": str(student["_id"]),
                    "student_id": student["student_id"],
                    "user_id": student["user_id"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "email": user["email"],
                    "date_of_birth": student["date_of_birth"],
                    "gender": student["gender"],
                    "department": student["department"],
                    "program": student["program"],
                    "enrollment_date": student["enrollment_date"],
                    "expected_graduation": student["expected_graduation"],
                    "current_semester": student["current_semester"],
                    "current_year": student["current_year"],
                    "gpa": student.get("gpa", 0.0),
                    "total_credits": student.get("total_credits", 0),
                    "is_active": student.get("is_active", True),
                    "created_at": student.get("created_at"),
                    "updated_at": student.get("updated_at")
                })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting students: {e}")
        return []

@router.get("/{student_id}")
async def get_student(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Retrieve a student by ID"""
    try:
        # Try to find by student_id or user_id
        student = None
        if student_id == current_user.user_id:
            # Find by user_id
            student = await students_collection.find_one({"user_id": student_id})
        else:
            # Find by student_id
            student = await students_collection.find_one({"student_id": student_id})
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        user = await users_collection.find_one({"_id": ObjectId(student["user_id"])})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": str(student["_id"]),
            "student_id": student["student_id"],
            "user_id": student["user_id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "date_of_birth": student["date_of_birth"],
            "gender": student["gender"],
            "department": student["department"],
            "program": student["program"],
            "enrollment_date": student["enrollment_date"],
            "expected_graduation": student["expected_graduation"],
            "current_semester": student["current_semester"],
            "current_year": student["current_year"],
            "gpa": student.get("gpa", 0.0),
            "total_credits": student.get("total_credits", 0),
            "is_active": student.get("is_active", True),
            "created_at": student.get("created_at"),
            "updated_at": student.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student: {e}")
        raise HTTPException(status_code=500, detail="Failed to get student")

@router.post("/")
async def create_student(
    student: StudentCreate,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection)
):
    """Create a new student"""
    try:
        existing = await students_collection.find_one({"student_id": student.student_id})
        if existing:
            raise HTTPException(status_code=409, detail="Student ID already exists")
        
        student_dict = student.dict()
        student_dict.update({
            "gpa": 0.0,
            "total_credits": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        result = await students_collection.insert_one(student_dict)
        return {"message": "Student created successfully", "id": str(result.inserted_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating student: {e}")
        raise HTTPException(status_code=500, detail="Failed to create student")
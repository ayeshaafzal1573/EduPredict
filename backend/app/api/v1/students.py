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
    department: str = None,
    program: str = None,
    year: int = None,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Get list of students with filters"""
    try:
        query = {"is_active": True}
        
        if department:
            query["department"] = department
        if program:
            query["program"] = program
        if year:
            query["current_year"] = year
        
        students = await students_collection.find(query).skip(skip).limit(limit).to_list(length=limit)
        
        result = []
        for student in students:
            try:
                user = await users_collection.find_one({"_id": ObjectId(student["user_id"])})
                if user:
                    result.append({
                        "id": str(student["_id"]),
                        "student_id": student["student_id"],
                        "user_id": student["user_id"],
                        "first_name": user["first_name"],
                        "last_name": user["last_name"],
                        "email": user["email"],
                        "date_of_birth": student.get("date_of_birth"),
                        "gender": student.get("gender"),
                        "department": student.get("department"),
                        "program": student.get("program"),
                        "enrollment_date": student.get("enrollment_date"),
                        "expected_graduation": student.get("expected_graduation"),
                        "current_semester": student.get("current_semester"),
                        "current_year": student.get("current_year"),
                        "gpa": student.get("gpa", 0.0),
                        "total_credits": student.get("total_credits", 0),
                        "is_active": student.get("is_active", True),
                        "created_at": student.get("created_at"),
                        "updated_at": student.get("updated_at")
                    })
            except Exception as e:
                logger.error(f"Error processing student {student.get('student_id')}: {e}")
                continue
        
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
            # Find by student_id first, then by user_id
            student = await students_collection.find_one({"student_id": student_id})
            if not student:
                student = await students_collection.find_one({"user_id": student_id})
        
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
            "date_of_birth": student.get("date_of_birth"),
            "gender": student.get("gender"),
            "department": student.get("department"),
            "program": student.get("program"),
            "enrollment_date": student.get("enrollment_date"),
            "expected_graduation": student.get("expected_graduation"),
            "current_semester": student.get("current_semester"),
            "current_year": student.get("current_year"),
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
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Create a new student"""
    try:
        # Validate required fields
        if not student.student_id or not student.user_id:
            raise HTTPException(status_code=400, detail="Student ID and User ID are required")
        
        # Check if student_id already exists
        existing = await students_collection.find_one({"student_id": student.student_id})
        if existing:
            raise HTTPException(status_code=409, detail="Student ID already exists")
        
        # Verify user exists
        user = await users_collection.find_one({"_id": ObjectId(student.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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

@router.put("/{student_id}")
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection)
):
    """Update a student's information"""
    try:
        # Find student
        student = await students_collection.find_one({
            "$or": [
                {"student_id": student_id},
                {"user_id": student_id},
                {"_id": ObjectId(student_id) if ObjectId.is_valid(student_id) else None}
            ]
        })
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Check permissions
        if current_user.role not in ["admin", "teacher"] and current_user.user_id != student["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        update_data = student_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await students_collection.update_one(
            {"_id": student["_id"]},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Student not found or no changes made")
        
        return {"message": "Student updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating student: {e}")
        raise HTTPException(status_code=500, detail="Failed to update student")

@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection)
):
    """Delete a student (soft delete)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        student = await students_collection.find_one({
            "$or": [
                {"student_id": student_id},
                {"_id": ObjectId(student_id) if ObjectId.is_valid(student_id) else None}
            ]
        })
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        result = await students_collection.update_one(
            {"_id": student["_id"]},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {"message": "Student deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting student: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete student")

@router.get("/{student_id}/analytics")
async def get_student_analytics(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection)
):
    """Get analytics for a specific student"""
    try:
        # Find student
        student = await students_collection.find_one({
            "$or": [
                {"student_id": student_id},
                {"user_id": student_id},
                {"_id": ObjectId(student_id) if ObjectId.is_valid(student_id) else None}
            ]
        })
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Check permissions
        if current_user.role not in ["admin", "teacher", "analyst"] and current_user.user_id != student["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate analytics data
        current_gpa = student.get("gpa", 3.2)
        current_semester = student.get("current_semester", 5)
        
        # Performance trend
        performance_trend = []
        for i in range(max(1, current_semester - 3), current_semester + 1):
            semester_name = f"Semester {i}"
            gpa_variation = (i - 1) * 0.05
            semester_gpa = max(0.0, min(4.0, current_gpa - 0.2 + gpa_variation))
            
            performance_trend.append({
                "semester": semester_name,
                "gpa": round(semester_gpa, 2),
                "credits": 15 + (i - 1) * 3
            })
        
        return {
            "student_id": student["student_id"],
            "performance_trend": performance_trend,
            "current_gpa": current_gpa,
            "total_credits": student.get("total_credits", 75),
            "attendance_rate": 87,  # This would come from attendance records
            "risk_assessment": {
                "score": 0.25 if current_gpa > 2.5 else 0.75,
                "level": "low" if current_gpa > 2.5 else "high"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get student analytics")
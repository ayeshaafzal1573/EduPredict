from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import get_current_user, TokenData
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_courses_collection, get_students_collection, get_users_collection
from app.models.course import Course, CourseCreate, CourseUpdate
from loguru import logger
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/")
async def get_all_courses(
    teacher_id: str = None,
    student_id: str = None,
    current_user: TokenData = Depends(get_current_user),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection)
):
    """Retrieve courses with optional filters"""
    try:
        query = {}
        
        if teacher_id:
            query["teacher_id"] = teacher_id
        elif student_id:
            query["students"] = {"$in": [student_id]}
        
        courses = await courses_collection.find(query).to_list(length=None)
        
        result = []
        for course in courses:
            course_data = {
                "id": str(course["_id"]),
                "name": course.get("name", ""),
                "code": course.get("code", ""),
                "description": course.get("description", ""),
                "department": course.get("department", ""),
                "credits": course.get("credits", 3),
                "semester": course.get("semester", ""),
                "academic_year": course.get("academic_year", ""),
                "schedule": course.get("schedule", ""),
                "room": course.get("room", ""),
                "max_students": course.get("max_students", 30),
                "teacher_id": course.get("teacher_id", ""),
                "teacher_name": course.get("teacher_name", ""),
                "students": course.get("students", []),
                "student_count": len(course.get("students", [])),
                "is_active": course.get("is_active", True),
                "created_at": course.get("created_at"),
                "updated_at": course.get("updated_at")
            }
            result.append(course_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        return []

@router.get("/{course_id}/students")
async def get_course_students(
    course_id: str,
    current_user: TokenData = Depends(get_current_user),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Get students enrolled in a course"""
    try:
        # Find course by ID or code
        course = await courses_collection.find_one({
            "$or": [
                {"_id": ObjectId(course_id) if ObjectId.is_valid(course_id) else None},
                {"code": course_id}
            ]
        })
        
        if not course:
            return []
        
        enrolled_student_ids = course.get("students", [])
        students = []
        
        for student_id in enrolled_student_ids:
            student = await students_collection.find_one({"student_id": student_id})
            if student:
                user = await users_collection.find_one({"_id": ObjectId(student["user_id"])})
                if user:
                    students.append({
                        "id": student_id,
                        "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                        "email": user.get("email", ""),
                        "attendance": 85,
                        "gpa": student.get("gpa", 0.0),
                        "risk_level": "low" if student.get("gpa", 0.0) > 2.5 else "high"
                    })
        
        return students
        
    except Exception as e:
        logger.error(f"Error getting course students: {e}")
        return []

@router.post("/{course_id}/enroll/{student_id}")
async def enroll_student(
    course_id: str,
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection)
):
    """Enroll a student in a course"""
    try:
        # Check if course exists
        course = await courses_collection.find_one({
            "$or": [
                {"_id": ObjectId(course_id) if ObjectId.is_valid(course_id) else None},
                {"code": course_id}
            ]
        })
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if student exists
        student = await students_collection.find_one({"student_id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Add student to course
        await courses_collection.update_one(
            {"_id": course["_id"]},
            {
                "$addToSet": {"students": student_id},
                "$inc": {"student_count": 1}
            }
        )
        
        return {"message": "Student enrolled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enrolling student: {e}")
        raise HTTPException(status_code=500, detail="Failed to enroll student")

@router.delete("/{course_id}/enroll/{student_id}")
async def unenroll_student(
    course_id: str,
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection)
):
    """Unenroll a student from a course"""
    try:
        course = await courses_collection.find_one({
            "$or": [
                {"_id": ObjectId(course_id) if ObjectId.is_valid(course_id) else None},
                {"code": course_id}
            ]
        })
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        await courses_collection.update_one(
            {"_id": course["_id"]},
            {
                "$pull": {"students": student_id},
                "$inc": {"student_count": -1}
            }
        )
        
        return {"message": "Student unenrolled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unenrolling student: {e}")
        raise HTTPException(status_code=500, detail="Failed to unenroll student")

@router.post("/", response_model=dict)
async def create_course(
    course: CourseCreate,
    current_user: TokenData = Depends(get_current_user),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection)
):
    """Create a new course"""
    try:
        existing = await courses_collection.find_one({"code": course.code})
        if existing:
            raise HTTPException(status_code=409, detail="Course code already exists")
        
        course_dict = course.dict()
        course_dict.update({
            "students": [],
            "student_count": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        result = await courses_collection.insert_one(course_dict)
        return {"message": "Course created successfully", "id": str(result.inserted_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        raise HTTPException(status_code=500, detail="Failed to create course")

@router.get("/{course_id}")
async def get_course(
    course_id: str,
    current_user: TokenData = Depends(get_current_user),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection)
):
    """Retrieve a course by ID"""
    try:
        course = await courses_collection.find_one({
            "$or": [
                {"_id": ObjectId(course_id) if ObjectId.is_valid(course_id) else None},
                {"code": course_id}
            ]
        })
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {
            "id": str(course["_id"]),
            "name": course.get("name", ""),
            "code": course.get("code", ""),
            "description": course.get("description", ""),
            "department": course.get("department", ""),
            "credits": course.get("credits", 3),
            "semester": course.get("semester", ""),
            "academic_year": course.get("academic_year", ""),
            "schedule": course.get("schedule", ""),
            "room": course.get("room", ""),
            "max_students": course.get("max_students", 30),
            "teacher_id": course.get("teacher_id", ""),
            "teacher_name": course.get("teacher_name", ""),
            "students": course.get("students", []),
            "student_count": len(course.get("students", [])),
            "is_active": course.get("is_active", True),
            "created_at": course.get("created_at"),
            "updated_at": course.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course: {e}")
        raise HTTPException(status_code=500, detail="Failed to get course")
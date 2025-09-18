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
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection)
):
    try:
        query = {}
        
        if teacher_id:
            query["teacher_id"] = teacher_id
        elif student_id:
            if student_id == "me":
                student_doc = await students_collection.find_one({"user_id": current_user.user_id})
                if not student_doc:
                    return []
                student_id = student_doc["student_id"]
            query["students"] = {"$in": [student_id]}
        
        courses = await courses_collection.find(query).to_list(length=None)
        result = []
        for course in courses:
            result.append({
                "id": str(course["_id"]),
                "name": course.get("name", ""),
                "code": course.get("code", ""),
                "description": course.get("description", ""),
                "credits": course.get("credits", 3),
                "teacher_name": course.get("teacher_name", ""),
                "students": course.get("students", []),
                "student_count": len(course.get("students", [])),
                "is_active": course.get("is_active", True),
            })
        
        return result

    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        return []

@router.get("/{course_id}/students")
async def get_course_students(
    course_id: str,
    student_id: str = None,  # optional, could be "me"
    current_user: TokenData = Depends(get_current_user),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """
    Get students enrolled in a course.
    Optionally filter for a specific student ("me" resolves to current user).
    """
    try:
        # Find course by _id or code
        or_conditions = []
        if ObjectId.is_valid(course_id):
            or_conditions.append({"_id": ObjectId(course_id)})
        or_conditions.append({"code": course_id})
        
        course = await courses_collection.find_one({"$or": or_conditions})
        if not course or "students" not in course or not course["students"]:
            return []

        # If student_id="me", resolve to the logged-in student's ID
        if student_id == "me":
            student_doc = await students_collection.find_one({"user_id": current_user.user_id})
            if not student_doc:
                return []
            student_id = student_doc["student_id"]

        # Filter students if student_id is provided
        enrolled_student_ids = course["students"]
        if student_id:
            if student_id not in enrolled_student_ids:
                return []  # student not enrolled
            enrolled_student_ids = [student_id]

        # Convert to ObjectIds if needed
        student_object_ids = [ObjectId(sid) for sid in enrolled_student_ids if ObjectId.is_valid(sid)]

        # Fetch student user info
        students = []
        cursor = users_collection.find({"_id": {"$in": student_object_ids}, "role": "student"})
        async for user in cursor:
            students.append({
                "id": str(user["_id"]),
                "student_id": str(user["_id"]),
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", ""),
                "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                "email": user.get("email", ""),
                "is_active": user.get("is_active", True)
            })

        return students

    except Exception as e:
        logger.error(f"Error fetching enrolled students: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch students")

      
        logger.error(f"Error getting course students: {e}")
        return []
@router.post("/{course_id}/enroll/{student_id}")
async def enroll_student(
    course_id: str,
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)  # users table
):
    """Enroll a student in a course"""
    try:
        # --- Find the course ---
        course = await courses_collection.find_one({
            "$or": [
                {"_id": ObjectId(course_id) if ObjectId.is_valid(course_id) else None},
                {"code": course_id}
            ]
        })
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # --- Find the student in users table ---
        query_student_id = ObjectId(student_id) if ObjectId.is_valid(student_id) else student_id
        student = await users_collection.find_one({"_id": query_student_id, "role": "student"})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # --- Enroll the student ---
        await courses_collection.update_one(
            {"_id": course["_id"]},
            {
                "$addToSet": {"students": student_id},
                "$set": {"updated_at": datetime.utcnow()}
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
                "$set": {"updated_at": datetime.utcnow()}
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
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Create a new course"""
    try:
        existing = await courses_collection.find_one({"code": course.code})
        if existing:
            raise HTTPException(status_code=409, detail="Course code already exists")
        
        # Get teacher name if teacher_id provided
        teacher_name = ""
        if course.teacher_id:
            teacher = await users_collection.find_one({"_id": ObjectId(course.teacher_id)})
            if teacher:
                teacher_name = f"{teacher.get('first_name', '')} {teacher.get('last_name', '')}".strip()
        
        course_dict = course.dict()
        course_dict.update({
            "teacher_name": teacher_name,
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
            "_id": str(course["_id"]),
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

@router.put("/{course_id}")
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: TokenData = Depends(get_current_user),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Update a course"""
    try:
        # Find course
        course = await courses_collection.find_one({
            "$or": [
                {"_id": ObjectId(course_id) if ObjectId.is_valid(course_id) else None},
                {"code": course_id}
            ]
        })
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        update_data = course_update.dict(exclude_unset=True)
        
        # Get teacher name if teacher_id is being updated
        if "teacher_id" in update_data and update_data["teacher_id"]:
            teacher = await users_collection.find_one({"_id": ObjectId(update_data["teacher_id"])})
            if teacher:
                update_data["teacher_name"] = f"{teacher.get('first_name', '')} {teacher.get('last_name', '')}".strip()
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await courses_collection.update_one(
            {"_id": course["_id"]},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Course not found or no changes made")
        
        return {"message": "Course updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating course: {e}")
        raise HTTPException(status_code=500, detail="Failed to update course")

@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    current_user: TokenData = Depends(get_current_user),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection)
):
    """Delete a course"""
    try:
        course = await courses_collection.find_one({
            "$or": [
                {"_id": ObjectId(course_id) if ObjectId.is_valid(course_id) else None},
                {"code": course_id}
            ]
        })
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Soft delete - mark as inactive
        result = await courses_collection.update_one(
            {"_id": course["_id"]},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {"message": "Course deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting course: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete course")
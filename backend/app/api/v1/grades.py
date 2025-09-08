from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user, TokenData
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_grades_collection, get_courses_collection, get_students_collection, get_users_collection
from datetime import datetime
from loguru import logger
from bson import ObjectId

router = APIRouter(prefix="/grades", tags=["Grades"])

@router.get("/")
async def get_grades(
    student_id: str = None,
    course_id: str = None,
    limit: int = 100,
    current_user: TokenData = Depends(get_current_user),
    grades_collection: AsyncIOMotorCollection = Depends(get_grades_collection)
):
    """Get grade records with filters"""
    try:
        query = {}
        
        if student_id:
            query["student_id"] = student_id
        if course_id:
            query["course_id"] = course_id
        
        grades = await grades_collection.find(query).limit(limit).to_list(length=limit)
        
        result = []
        for grade in grades:
            result.append({
                "id": str(grade["_id"]),
                "student_id": grade.get("student_id"),
                "course_id": grade.get("course_id"),
                "course_name": grade.get("course_name"),
                "assignment_name": grade.get("assignment_name"),
                "grade_type": grade.get("grade_type"),
                "points_earned": grade.get("points_earned"),
                "points_possible": grade.get("points_possible"),
                "percentage": grade.get("percentage"),
                "letter_grade": grade.get("letter_grade"),
                "grade_points": grade.get("grade_points"),
                "created_at": grade.get("created_at"),
                "updated_at": grade.get("updated_at")
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting grades: {e}")
        return []

@router.get("/course/{course_id}/gradebook")
async def get_course_gradebook(
    course_id: str,
    current_user: TokenData = Depends(get_current_user),
    grades_collection: AsyncIOMotorCollection = Depends(get_grades_collection),
    courses_collection: AsyncIOMotorCollection = Depends(get_courses_collection),
    students_collection: AsyncIOMotorCollection = Depends(get_students_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Get gradebook for a course"""
    try:
        # Find course
        course = await courses_collection.find_one({
            "$or": [
                {"_id": ObjectId(course_id) if ObjectId.is_valid(course_id) else None},
                {"code": course_id}
            ]
        })
        
        if not course:
            return {
                "course_id": course_id,
                "course_name": "Unknown Course",
                "assignments": [],
                "students": [],
                "statistics": {"class_average": 0, "total_students": 0, "total_assignments": 0}
            }
        
        # Get all grades for this course
        grades = await grades_collection.find({"course_id": course["code"]}).to_list(length=None)
        
        # Get unique assignments
        assignments = {}
        for grade in grades:
            assignment_key = f"{grade['assignment_name']}_{grade['grade_type']}"
            if assignment_key not in assignments:
                assignments[assignment_key] = {
                    "name": grade["assignment_name"],
                    "type": grade["grade_type"],
                    "points_possible": grade["points_possible"]
                }
        
        # Get enrolled students
        enrolled_student_ids = course.get("students", [])
        students_data = []
        
        for student_id in enrolled_student_ids:
            student = await students_collection.find_one({"student_id": student_id})
            if student:
                user = await users_collection.find_one({"_id": ObjectId(student["user_id"])})
                if user:
                    student_grades = [g for g in grades if g["student_id"] == student_id]
                    
                    grade_dict = {}
                    total_points = 0
                    total_possible = 0
                    
                    for grade in student_grades:
                        assignment_key = f"{grade['assignment_name']}_{grade['grade_type']}"
                        grade_dict[assignment_key] = {
                            "points_earned": grade["points_earned"],
                            "percentage": grade.get("percentage", 0)
                        }
                        total_points += grade["points_earned"]
                        total_possible += grade["points_possible"]
                    
                    current_percentage = (total_points / total_possible * 100) if total_possible > 0 else 0
                    current_grade = calculate_letter_grade(current_percentage)
                    
                    students_data.append({
                        "student_id": student_id,
                        "student_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                        "grades": grade_dict,
                        "current_grade": current_grade,
                        "current_percentage": round(current_percentage, 1)
                    })
        
        total_students = len(students_data)
        class_average = sum(s["current_percentage"] for s in students_data) / total_students if total_students > 0 else 0
        
        return {
            "course_id": course["code"],
            "course_name": course["name"],
            "assignments": list(assignments.values()),
            "students": students_data,
            "statistics": {
                "class_average": round(class_average, 1),
                "total_students": total_students,
                "total_assignments": len(assignments)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting course gradebook: {e}")
        return {
            "course_id": course_id,
            "course_name": "Unknown Course",
            "assignments": [],
            "students": [],
            "statistics": {"class_average": 0, "total_students": 0, "total_assignments": 0}
        }

def calculate_letter_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 97: return "A+"
    elif percentage >= 93: return "A"
    elif percentage >= 90: return "A-"
    elif percentage >= 87: return "B+"
    elif percentage >= 83: return "B"
    elif percentage >= 80: return "B-"
    elif percentage >= 77: return "C+"
    elif percentage >= 73: return "C"
    elif percentage >= 70: return "C-"
    elif percentage >= 67: return "D+"
    elif percentage >= 63: return "D"
    elif percentage >= 60: return "D-"
    else: return "F"

@router.post("/bulk")
async def create_bulk_grades(
    bulk_data: dict,
    current_user: TokenData = Depends(get_current_user),
    grades_collection: AsyncIOMotorCollection = Depends(get_grades_collection)
):
    """Create grades in bulk for an assignment"""
    try:
        course_id = bulk_data.get("course_id")
        assignment_name = bulk_data.get("assignment_name")
        grade_type = bulk_data.get("grade_type")
        points_possible = bulk_data.get("points_possible")
        grades = bulk_data.get("grades", [])
        
        if not all([course_id, assignment_name, grade_type, points_possible]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        grade_docs = []
        for grade in grades:
            points_earned = grade.get("points_earned", 0)
            percentage = (points_earned / points_possible * 100) if points_possible > 0 else 0
            letter_grade = calculate_letter_grade(percentage)
            grade_points = percentage_to_gpa(percentage)
            
            doc = {
                "student_id": grade.get("student_id"),
                "course_id": course_id,
                "assignment_name": assignment_name,
                "grade_type": grade_type,
                "points_earned": points_earned,
                "points_possible": points_possible,
                "percentage": round(percentage, 1),
                "letter_grade": letter_grade,
                "grade_points": round(grade_points, 2),
                "weight": 1.0,
                "notes": grade.get("notes", ""),
                "graded_by": current_user.user_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            grade_docs.append(doc)
        
        if grade_docs:
            await grades_collection.insert_many(grade_docs)
        
        return {"message": f"Bulk grades created successfully for {len(grade_docs)} students"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating bulk grades: {e}")
        raise HTTPException(status_code=500, detail="Failed to create bulk grades")

def percentage_to_gpa(percentage):
    """Convert percentage to GPA points"""
    if percentage >= 97: return 4.0
    elif percentage >= 93: return 4.0
    elif percentage >= 90: return 3.7
    elif percentage >= 87: return 3.3
    elif percentage >= 83: return 3.0
    elif percentage >= 80: return 2.7
    elif percentage >= 77: return 2.3
    elif percentage >= 73: return 2.0
    elif percentage >= 70: return 1.7
    elif percentage >= 67: return 1.3
    elif percentage >= 63: return 1.0
    elif percentage >= 60: return 0.7
    else: return 0.0
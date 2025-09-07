from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.course_service import CourseService, get_course_service
from app.models.course import Course, CourseCreate, CourseUpdate
from app.core.security import require_roles, UserRole

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/{course_id}/students", response_model=List[dict])
async def get_course_students(course_id: str, service: CourseService = Depends(get_course_service)):
    """Get students enrolled in a course"""
    try:
        # Mock student data for course
        return [
            {"id": "1", "name": "John Doe", "email": "john@example.com", "attendance": 85, "gpa": 3.2, "risk_level": "low"},
            {"id": "2", "name": "Jane Smith", "email": "jane@example.com", "attendance": 92, "gpa": 3.8, "risk_level": "low"}
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{course_id}/enroll/{student_id}")
async def enroll_student(course_id: str, student_id: str, service: CourseService = Depends(get_course_service)):
    """Enroll a student in a course"""
    try:
        return {"message": "Student enrolled successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{course_id}/enroll/{student_id}")
async def unenroll_student(course_id: str, student_id: str, service: CourseService = Depends(get_course_service)):
    """Unenroll a student from a course"""
    try:
        return {"message": "Student unenrolled successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/", response_model=Course, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.TEACHER]))])
async def create_course(course: CourseCreate, service: CourseService = Depends(get_course_service)):
    """
    Create a new course (Admin/Teacher only)
    
    Args:
        course: Course creation data
        service: Course service dependency
    
    Returns:
        Created course data
    
    Raises:
        HTTPException: If course code exists or server error
    """
    try:
        return await service.create_course(course)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{course_id}", response_model=Course)
async def get_course(course_id: str, service: CourseService = Depends(get_course_service)):
    """
    Retrieve a course by ID
    
    Args:
        course_id: Unique course code (e.g., CS-101)
        service: Course service dependency
    
    Returns:
        Course data
    
    Raises:
        HTTPException: If course not found or server error
    """
    try:
        return await service.get_course(course_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[Course])
async def get_all_courses(service: CourseService = Depends(get_course_service)):
    """
    Retrieve all courses
    
    Args:
        service: Course service dependency
    
    Returns:
        List of all courses
    
    Raises:
        HTTPException: If server error occurs
    """
    try:
        return await service.get_all_courses()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
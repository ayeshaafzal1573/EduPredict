from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.grade_service import GradeService, get_grade_service
from app.models.grade import Grade, GradeCreate, GradeUpdate, GradeStats
from app.core.security import require_roles, UserRole

router = APIRouter(prefix="/grades", tags=["Grades"])

@router.post("/", response_model=Grade, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.TEACHER]))])
async def create_grade(grade: GradeCreate, service: GradeService = Depends(get_grade_service)):
    """
    Create a new grade record (Admin/Teacher only)
    
    Args:
        grade: Grade creation data
        service: Grade service dependency
    
    Returns:
        Created grade record
    
    Raises:
        HTTPException: If server error occurs
    """
    try:
        return await service.create_grade(grade)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{student_id}/{course_id}/stats", response_model=GradeStats)
async def get_grade_stats(student_id: str, course_id: str, service: GradeService = Depends(get_grade_service)):
    """
    Retrieve grade statistics for a student in a course
    
    Args:
        student_id: Unique student ID (e.g., STU-1234)
        course_id: Unique course code (e.g., CS-101)
        service: Grade service dependency
    
    Returns:
        Grade statistics
    
    Raises:
        HTTPException: If no grades found or server error
    """
    try:
        return await service.generate_grade_stats(student_id, course_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
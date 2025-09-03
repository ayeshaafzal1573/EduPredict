"""
Student management endpoints for EduPredict
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.student import Student, StudentCreate, StudentUpdate, StudentPerformance
from app.models.user import TokenData
from app.core.security import get_current_user, require_teacher_or_admin
from app.core.database import get_database
from app.services.user_service import UserService
from app.services.student_service import StudentService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ---- Dependency Provider ----
def get_student_service(
    db=Depends(get_database),
    user_service: UserService = Depends(UserService)
):
    return StudentService(db, user_service)


@router.get("/", response_model=List[Student])
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    major: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    current_user: TokenData = Depends(require_teacher_or_admin),
    service: StudentService = Depends(get_student_service),
):
    """Get list of students with optional filtering"""
    try:
        students = await service.get_students(
            skip=skip,
            limit=limit,
            major=major,
            academic_year=academic_year,
        )
        return students
    except Exception as e:
        logger.error(f"Failed to retrieve students: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve students",
        )


@router.post("/", response_model=Student, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    current_user: TokenData = Depends(require_teacher_or_admin),
    service: StudentService = Depends(get_student_service),
):
    """Create a new student"""
    try:
        student = await service.create_student(
            student_data=student_data,
            created_by=current_user.id,
        )
        return student
    except Exception as e:
        logger.error(f"Failed to create student: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{student_id}", response_model=Student)
async def get_student(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
):
    """Get student by ID"""
    try:
        student = await service.get_student_by_id(student_id)
        return student
    except Exception as e:
        logger.error(f"Failed to get student {student_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )


@router.put("/{student_id}", response_model=Student)
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    current_user: TokenData = Depends(require_teacher_or_admin),
    service: StudentService = Depends(get_student_service),
):
    """Update an existing student"""
    try:
        student = await service.update_student(student_id, student_update)
        return student
    except Exception as e:
        logger.error(f"Failed to update student {student_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{student_id}", response_model=dict)
async def delete_student(
    student_id: str,
    current_user: TokenData = Depends(require_teacher_or_admin),
    service: StudentService = Depends(get_student_service),
):
    """Soft delete a student"""
    try:
        success = await service.delete_student(student_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )
        return {"message": "Student deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete student {student_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete student",
        )


@router.get("/{student_id}/performance", response_model=StudentPerformance)
async def get_student_performance(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
):
    """Get student performance metrics"""
    try:
        perf_summary = await service.get_student_performance_summary(student_id)
        return StudentPerformance(**perf_summary)
    except Exception as e:
        logger.error(f"Failed to get performance for student {student_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics",
        )


@router.get("/at-risk", response_model=List[dict])
async def get_at_risk_students(
    limit: int = Query(50, ge=1, le=200),
    current_user: TokenData = Depends(require_teacher_or_admin),
    service: StudentService = Depends(get_student_service),
):
    """Get list of at-risk students"""
    try:
        students = await service.get_at_risk_students(limit=limit)
        return students
    except Exception as e:
        logger.error(f"Failed to get at-risk students: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve at-risk students",
        )

"""
Grade management endpoints for EduPredict
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.user import TokenData
from app.models.grade import Grade, GradeCreate, GradeUpdate, GradeStats
from app.core.security import get_current_user
from app.services.grade_service import GradeService
from app.services.user_service import UserService
from app.services.course_service import CourseService
from app.core.database import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ✅ Dependency injector
def get_grade_service(
    db=Depends(get_database),
    user_service: UserService = Depends(lambda: UserService()),
    course_service: CourseService = Depends(lambda: CourseService())
):
    return GradeService(db, user_service, course_service)


@router.post("/", response_model=Grade)
async def create_grade(
    grade_data: GradeCreate,
    current_user: TokenData = Depends(get_current_user),
    grade_service: GradeService = Depends(get_grade_service)
) -> Grade:
    """Create a new grade record"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Teacher or Admin role required."
        )
    return await grade_service.create_grade(grade_data, current_user.sub)


@router.get("/", response_model=List[Grade])
async def get_grades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    student_id: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    grade_type: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user),
    grade_service: GradeService = Depends(get_grade_service)
) -> List[Grade]:
    """Get grade records with filtering"""
    student_filter = current_user.sub if current_user.role == "student" else student_id
    return await grade_service.get_grades(
        skip=skip,
        limit=limit,
        student_id=student_filter,
        course_id=course_id,
        grade_type=grade_type,
        user_role=current_user.role,
        user_id=current_user.sub
    )


@router.get("/student/{student_id}/stats", response_model=GradeStats)
async def get_student_grade_stats(
    student_id: str,
    course_id: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user),
    grade_service: GradeService = Depends(get_grade_service)
):
    """Get grade statistics for a student"""
    if current_user.role == "student" and current_user.sub != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return await grade_service.get_student_grade_stats(student_id=student_id, course_id=course_id)


@router.get("/course/{course_id}/gradebook")
async def get_course_gradebook(
    course_id: str,
    current_user: TokenData = Depends(get_current_user),
    grade_service: GradeService = Depends(get_grade_service)
):
    """Get complete gradebook for a course"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Teacher or Admin role required."
        )
    return await grade_service.get_course_gradebook(course_id)


@router.put("/{grade_id}", response_model=Grade)
async def update_grade(
    grade_id: str,
    grade_update: GradeUpdate,
    current_user: TokenData = Depends(get_current_user),
    grade_service: GradeService = Depends(get_grade_service)
) -> Grade:
    """Update a grade record"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Teacher or Admin role required."
        )
    return await grade_service.update_grade(grade_id, grade_update)


@router.delete("/{grade_id}")
async def delete_grade(
    grade_id: str,
    current_user: TokenData = Depends(get_current_user),
    grade_service: GradeService = Depends(get_grade_service)
):
    """Delete a grade record"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Teacher or Admin role required."
        )

    success = await grade_service.delete_grade(grade_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade record not found"
        )

    return {"message": "Grade deleted successfully"}

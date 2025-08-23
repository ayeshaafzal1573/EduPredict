"""
Grade management endpoints for EduPredict
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.user import TokenData
from app.models.grade import Grade, GradeCreate, GradeUpdate, GradeBulkCreate, GradeStats, CourseGradebook
from app.core.security import get_current_user
from app.services.grade_service import GradeService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

grade_service = GradeService()

@router.post("/", response_model=Grade)
async def create_grade(
    grade_data: GradeCreate,
    current_user: TokenData = Depends(get_current_user)
) -> Grade:
    """Create a new grade record"""
    try:
        # Only teachers and admins can create grades
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Teacher or Admin role required."
            )

        logger.info(f"Creating grade for student: {grade_data.student_id}")
        grade = await grade_service.create_grade(grade_data, current_user.sub)
        return grade
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create grade record"
        )

@router.get("/", response_model=List[Grade])
async def get_grades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    student_id: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    grade_type: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user)
) -> List[Grade]:
    """Get grade records with filtering"""
    try:
        logger.info(f"Getting grades for user: {current_user.sub}")

        # Students can only see their own grades
        if current_user.role == "student":
            student_filter = current_user.sub
        else:
            student_filter = student_id

        grades = await grade_service.get_grades(
            skip=skip,
            limit=limit,
            student_id=student_filter,
            course_id=course_id,
            grade_type=grade_type,
            user_role=current_user.role,
            user_id=current_user.sub
        )

        return grades
    except Exception as e:
        logger.error(f"Failed to get grades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve grade records"
        )

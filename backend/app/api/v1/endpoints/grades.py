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
        # Return empty list instead of raising error - service should handle mock data
        return []

@router.get("/student/{student_id}/stats")
async def get_student_grade_stats(
    student_id: str,
    course_id: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    """Get grade statistics for a student"""
    try:
        # Students can only see their own stats
        if current_user.role == "student" and current_user.sub != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        stats = await grade_service.get_student_grade_stats(
            student_id=student_id,
            course_id=course_id
        )

        return stats.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get grade stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve grade statistics"
        )

@router.get("/course/{course_id}/gradebook")
async def get_course_gradebook(
    course_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get complete gradebook for a course"""
    try:
        # Only teachers and admins can access gradebooks
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Teacher or Admin role required."
            )

        gradebook = await grade_service.get_course_gradebook(course_id)
        return gradebook
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get course gradebook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve course gradebook"
        )

@router.put("/{grade_id}", response_model=Grade)
async def update_grade(
    grade_id: str,
    grade_update: GradeUpdate,
    current_user: TokenData = Depends(get_current_user)
) -> Grade:
    """Update a grade record"""
    try:
        # Only teachers and admins can update grades
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Teacher or Admin role required."
            )

        updated_grade = await grade_service.update_grade(grade_id, grade_update)
        return updated_grade
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update grade record"
        )

@router.delete("/{grade_id}")
async def delete_grade(
    grade_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a grade record"""
    try:
        # Only teachers and admins can delete grades
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete grade record"
        )

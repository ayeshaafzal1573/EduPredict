"""
Course management endpoints for EduPredict
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional, Dict, Any
from app.models.user import TokenData
from app.models.course import Course, CourseCreate, CourseUpdate
from app.core.security import get_current_user
from app.services.course_service import CourseService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

course_service = CourseService()

@router.post("/", response_model=Course)
async def create_course(
    course_data: CourseCreate,
    current_user: TokenData = Depends(get_current_user)
) -> Course:
    """Create a new course"""
    try:
        # Only teachers and admins can create courses
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Teacher or Admin role required."
            )

        logger.info(f"Creating course: {course_data.name}")
        course = await course_service.create_course(course_data, current_user.sub)
        return course
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create course"
        )

@router.get("/", response_model=List[Course])
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    teacher_id: Optional[str] = None,
    semester: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
) -> List[Course]:
    """Get list of courses with filtering"""
    try:
        logger.info(f"Getting courses for user: {current_user.sub}")

        # Students can only see their enrolled courses
        if current_user.role == "student":
            courses = await course_service.get_student_courses(current_user.sub, skip, limit)
        # Teachers can see their own courses or all if admin
        elif current_user.role == "teacher":
            teacher_filter = teacher_id if teacher_id else current_user.sub
            courses = await course_service.get_courses(skip, limit, teacher_filter, semester)
        # Admins and analysts can see all courses
        else:
            courses = await course_service.get_courses(skip, limit, teacher_id, semester)

        return courses
    except Exception as e:
        logger.error(f"Failed to get courses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve courses"
        )

@router.get("/{course_id}", response_model=Course)
async def get_course(
    course_id: str,
    current_user: TokenData = Depends(get_current_user)
) -> Course:
    """Get a specific course by ID"""
    try:
        logger.info(f"Getting course: {course_id}")
        course = await course_service.get_course_by_id(course_id)

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Check access permissions
        if current_user.role == "student":
            if current_user.sub not in course.students:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You are not enrolled in this course."
                )
        elif current_user.role == "teacher":
            if course.teacher_id != current_user.sub and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You are not the instructor of this course."
                )

        return course
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get course: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve course"
        )

"""
Attendance management endpoints for EduPredict
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.user import TokenData
from app.models.attendance import Attendance, AttendanceCreate, AttendanceUpdate, AttendanceBulkCreate
from app.core.security import get_current_user
from app.services.attendance_service import AttendanceService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

attendance_service = AttendanceService()

@router.post("/", response_model=Attendance)
async def create_attendance_record(
    attendance_data: AttendanceCreate,
    current_user: TokenData = Depends(get_current_user)
) -> Attendance:
    """Create a new attendance record"""
    try:
        # Only teachers and admins can create attendance records
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Teacher or Admin role required."
            )

        logger.info(f"Creating attendance record for student: {attendance_data.student_id}")
        attendance = await attendance_service.create_attendance(attendance_data, current_user.sub)
        return attendance
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create attendance record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create attendance record"
        )

@router.get("/", response_model=List[Attendance])
async def get_attendance(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    student_id: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: TokenData = Depends(get_current_user)
) -> List[Attendance]:
    """Get attendance records with filtering"""
    try:
        logger.info(f"Getting attendance records for user: {current_user.sub}")

        # Students can only see their own attendance
        if current_user.role == "student":
            student_filter = current_user.sub
        else:
            student_filter = student_id

        attendance_records = await attendance_service.get_attendance_records(
            skip=skip,
            limit=limit,
            student_id=student_filter,
            course_id=course_id,
            date_from=date_from,
            date_to=date_to,
            user_role=current_user.role,
            user_id=current_user.sub
        )

        return attendance_records
    except Exception as e:
        logger.error(f"Failed to get attendance records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attendance records"
        )

@router.get("/stats/{student_id}", response_model=dict)
async def get_student_attendance_stats(
    student_id: str,
    course_id: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    """Get attendance statistics for a student"""
    try:
        # Students can only see their own stats
        if current_user.role == "student" and current_user.sub != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        stats = await attendance_service.get_student_attendance_stats(
            student_id=student_id,
            course_id=course_id,
            date_from=date_from,
            date_to=date_to
        )

        return stats.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get attendance stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attendance statistics"
        )

@router.get("/course/{course_id}/summary")
async def get_course_attendance_summary(
    course_id: str,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    """Get attendance summary for a course"""
    try:
        # Only teachers and admins can access course summaries
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Teacher or Admin role required."
            )

        summary = await attendance_service.get_course_attendance_summary(
            course_id=course_id,
            date_from=date_from,
            date_to=date_to
        )

        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get course attendance summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve course attendance summary"
        )

"""
Attendance management endpoints for EduPredict
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.user import TokenData
from app.models.attendance import Attendance, AttendanceCreate, AttendanceUpdate, AttendanceBulkCreate, AttendanceStats
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
):
    """Create a new attendance record"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Teacher or Admin role required.")
    return await attendance_service.create_attendance(attendance_data, current_user.sub)


@router.post("/bulk", response_model=List[Attendance])
async def create_bulk_attendance(
    bulk_data: AttendanceBulkCreate,
    current_user: TokenData = Depends(get_current_user)
):
    """Create multiple attendance records at once"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Teacher or Admin role required.")
    return await attendance_service.create_bulk_attendance(bulk_data, current_user.sub)


@router.get("/", response_model=List[Attendance])
async def get_attendance(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    student_id: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    """Get attendance records with filters"""
    student_filter = current_user.sub if current_user.role == "student" else student_id
    return await attendance_service.get_attendance_records(
        skip=skip,
        limit=limit,
        student_id=student_filter,
        course_id=course_id,
        date_from=date_from,
        date_to=date_to,
        user_role=current_user.role,
        user_id=current_user.sub
    )


@router.get("/stats/{student_id}", response_model=AttendanceStats)
async def get_student_attendance_stats(
    student_id: str,
    course_id: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    """Get attendance statistics for a student"""
    if current_user.role == "student" and current_user.sub != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return await attendance_service.get_student_attendance_stats(
        student_id=student_id,
        course_id=course_id,
        date_from=date_from,
        date_to=date_to
    )


@router.get("/course/{course_id}/summary")
async def get_course_attendance_summary(
    course_id: str,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    """Get attendance summary for a course"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Teacher or Admin role required.")
    return await attendance_service.get_course_attendance_summary(
        course_id=course_id,
        date_from=date_from,
        date_to=date_to
    )


@router.put("/{attendance_id}", response_model=Attendance)
async def update_attendance_record(
    attendance_id: str,
    update_data: AttendanceUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update an attendance record"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Teacher or Admin role required.")
    return await attendance_service.update_attendance(attendance_id, update_data)


@router.delete("/{attendance_id}", response_model=dict)
async def delete_attendance_record(
    attendance_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete an attendance record"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Teacher or Admin role required.")
    deleted = await attendance_service.delete_attendance(attendance_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return {"success": True, "deleted_id": attendance_id}

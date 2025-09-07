from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.attendance_service import AttendanceService, get_attendance_service
from app.models.attendance import Attendance, AttendanceCreate, AttendanceUpdate, AttendanceStats
from app.core.security import require_roles, UserRole

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/", response_model=Attendance, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.TEACHER]))])
async def create_attendance(attendance: AttendanceCreate, service: AttendanceService = Depends(get_attendance_service)):
    """
    Create a new attendance record (Admin/Teacher only)
    
    Args:
        attendance: Attendance creation data
        service: Attendance service dependency
    
    Returns:
        Created attendance record
    
    Raises:
        HTTPException: If server error occurs
    """
    try:
        return await service.create_attendance(attendance)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{student_id}/{course_id}/stats", response_model=AttendanceStats)
async def get_attendance_stats(student_id: str, course_id: str, service: AttendanceService = Depends(get_attendance_service)):
    """
    Retrieve attendance statistics for a student in a course
    
    Args:
        student_id: Unique student ID (e.g., STU-1234)
        course_id: Unique course code (e.g., CS-101)
        service: Attendance service dependency
    
    Returns:
        Attendance statistics
    
    Raises:
        HTTPException: If no records found or server error
    """
    try:
        return await service.generate_attendance_stats(student_id, course_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
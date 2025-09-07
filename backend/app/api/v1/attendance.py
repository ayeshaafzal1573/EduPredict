from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.attendance_service import AttendanceService, get_attendance_service
from app.models.attendance import Attendance, AttendanceCreate, AttendanceUpdate, AttendanceStats
from app.core.security import require_roles, UserRole, get_current_user, TokenData
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_attendance_collection, get_students_collection, get_courses_collection
from datetime import datetime, date
from loguru import logger

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("/")
async def get_attendance_records(
    student_id: str = None,
    course_id: str = None,
    date_from: str = None,
    date_to: str = None,
    limit: int = 100,
    current_user: TokenData = Depends(get_current_user),
    attendance_collection: AsyncIOMotorCollection = Depends(get_attendance_collection)
):
    """Get attendance records with filters"""
    try:
        query = {}
        
        if student_id:
            query["student_id"] = student_id
        if course_id:
            query["course_id"] = course_id
        if date_from:
            query["date"] = {"$gte": date_from}
        if date_to:
            if "date" in query:
                query["date"]["$lte"] = date_to
            else:
                query["date"] = {"$lte": date_to}
        
        records = await attendance_collection.find(query).limit(limit).to_list(length=limit)
        
        # Convert to proper format
        result = []
        for record in records:
            result.append({
                "id": str(record["_id"]),
                "student_id": record.get("student_id"),
                "course_id": record.get("course_id"),
                "date": record.get("date"),
                "status": record.get("status"),
                "marked_by": record.get("marked_by"),
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at")
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting attendance records: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/bulk", dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.TEACHER]))])
async def create_bulk_attendance(
    bulk_data: dict,
    current_user: TokenData = Depends(get_current_user),
    attendance_collection: AsyncIOMotorCollection = Depends(get_attendance_collection)
):
    """Create attendance records in bulk"""
    try:
        course_id = bulk_data.get("course_id")
        attendance_date = bulk_data.get("date")
        records = bulk_data.get("attendance_records", [])
        
        if not course_id or not attendance_date or not records:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields")
        
        # Parse date
        if isinstance(attendance_date, str):
            attendance_date = datetime.strptime(attendance_date, "%Y-%m-%d").date()
        
        # Prepare attendance records
        attendance_docs = []
        for record in records:
            doc = {
                "student_id": record.get("student_id"),
                "course_id": course_id,
                "date": attendance_date,
                "status": record.get("status", "present"),
                "notes": record.get("notes", ""),
                "marked_by": current_user.user_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            attendance_docs.append(doc)
        
        # Delete existing records for this date and course
        await attendance_collection.delete_many({
            "course_id": course_id,
            "date": attendance_date
        })
        
        # Insert new records
        if attendance_docs:
            await attendance_collection.insert_many(attendance_docs)
        
        return {"message": f"Bulk attendance created successfully for {len(attendance_docs)} students"}
    except Exception as e:
        logger.error(f"Error creating bulk attendance: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/", response_model=Attendance, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.TEACHER]))])
async def create_attendance(attendance: AttendanceCreate, service: AttendanceService = Depends(get_attendance_service)):
    """Create a new attendance record (Admin/Teacher only)"""
    try:
        return await service.create_attendance(attendance)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating attendance: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{student_id}/{course_id}/stats", response_model=AttendanceStats)
async def get_attendance_stats(student_id: str, course_id: str, service: AttendanceService = Depends(get_attendance_service)):
    """Retrieve attendance statistics for a student in a course"""
    try:
        return await service.generate_attendance_stats(student_id, course_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting attendance stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
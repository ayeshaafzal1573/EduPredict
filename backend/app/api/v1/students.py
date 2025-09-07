from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.student_service import StudentService, get_student_service
from app.models.student import Student, StudentCreate, StudentUpdate, StudentAnalytics
from app.core.security import require_roles, UserRole

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=Student, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.TEACHER]))])
async def create_student(student: StudentCreate, service: StudentService = Depends(get_student_service)):
    """
    Create a new student (Admin/Teacher only)
    
    Args:
        student: Student creation data
        service: Student service dependency
    
    Returns:
        Created student data
    
    Raises:
        HTTPException: If student ID exists or server error occurs
    """
    try:
        return await service.create_student(student)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{student_id}", response_model=Student)
async def get_student(student_id: str, service: StudentService = Depends(get_student_service)):
    """
    Retrieve a student by ID
    
    Args:
        student_id: Unique student ID (e.g., STU-1234)
        service: Student service dependency
    
    Returns:
        Student data
    
    Raises:
        HTTPException: If student not found or server error
    """
    try:
        return await service.get_student(student_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{student_id}", response_model=Student, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.TEACHER]))])
async def update_student(student_id: str, update_data: StudentUpdate, service: StudentService = Depends(get_student_service)):
    """
    Update a student's information (Admin/Teacher only)
    
    Args:
        student_id: Unique student ID
        update_data: Updated student data
        service: Student service dependency
    
    Returns:
        Updated student data
    
    Raises:
        HTTPException: If student not found or server error
    """
    try:
        return await service.update_student(student_id, update_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{student_id}/analytics", response_model=StudentAnalytics, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST]))])
async def get_student_analytics(student_id: str, service: StudentService = Depends(get_student_service)):
    """
    Retrieve analytics for a student (Admin/Analyst only)
    
    Args:
        student_id: Unique student ID
        service: Student service dependency
    
    Returns:
        Student analytics data
    
    Raises:
        HTTPException: If student not found or server error
    """
    try:
        return await service.generate_analytics(student_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.analytics_service import AnalyticsService, get_analytics_service
from app.models.student import StudentAnalytics
from app.core.security import require_roles, UserRole

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/{student_id}", response_model=StudentAnalytics, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST]))])
async def get_student_analytics(student_id: str, service: AnalyticsService = Depends(get_analytics_service)):
    """
    Retrieve comprehensive analytics for a student (Admin/Analyst only)
    
    Args:
        student_id: Unique student ID (e.g., STU-1234)
        service: Analytics service dependency
    
    Returns:
        Student analytics data
    
    Raises:
        HTTPException: If student not found or server error
    """
    try:
        return await service.generate_student_analytics(student_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
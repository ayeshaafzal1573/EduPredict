from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.notification_service import NotificationService, get_notification_service
from app.models.notification import Notification, NotificationCreate
from app.core.security import require_roles, UserRole

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=Notification, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.TEACHER]))])
async def create_notification(notification: NotificationCreate, service: NotificationService = Depends(get_notification_service)):
    """
    Create a new notification (Admin/Teacher only)
    
    Args:
        notification: Notification creation data
        service: Notification service dependency
    
    Returns:
        Created notification
    
    Raises:
        HTTPException: If server error occurs
    """
    try:
        return await service.create_notification(notification)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{user_id}", response_model=List[Notification])
async def get_user_notifications(user_id: str, service: NotificationService = Depends(get_notification_service)):
    """
    Retrieve notifications for a user
    
    Args:
        user_id: Unique user ID
        service: Notification service dependency
    
    Returns:
        List of notifications
    
    Raises:
        HTTPException: If server error occurs
    """
    try:
        return await service.get_user_notifications(user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
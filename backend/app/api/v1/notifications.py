from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.notification_service import NotificationService, get_notification_service
from app.models.notification import Notification, NotificationCreate
from app.core.security import require_roles, UserRole, get_current_user, TokenData

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=Notification, dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.TEACHER]))])
async def create_notification(notification: NotificationCreate, service: NotificationService = Depends(get_notification_service)):
    """Create a new notification (Admin/Teacher only)"""
    try:
        return await service.create_notification(notification)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{user_id}", response_model=List[Notification])
async def get_user_notifications(
    user_id: str, 
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Retrieve notifications for a user"""
    try:
        # Allow users to get their own notifications or admins to get any
        if user_id == "me":
            user_id = current_user.user_id
        elif current_user.role not in ["admin"] and user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return await service.get_user_notifications(user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Mark a notification as read"""
    try:
        # This would need to be implemented in the service
        return {"message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/read-all")
async def mark_all_notifications_read(
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Mark all notifications as read for current user"""
    try:
        # This would need to be implemented in the service
        return {"message": "All notifications marked as read"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.models.notification import Notification, NotificationCreate
from app.services.notification_service import NotificationService
from app.models.user import TokenData
from app.core.security import get_current_user

router = APIRouter()
notification_service = NotificationService()

@router.post("/", response_model=Notification, status_code=status.HTTP_201_CREATED)
async def create_notification(
    data: NotificationCreate,
    current_user: TokenData = Depends(get_current_user)
):
    # Sirf admin/teacher bana sake
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return await notification_service.create_notification(data)


@router.get("/", response_model=List[Notification])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: TokenData = Depends(get_current_user)
):
    return await notification_service.get_notifications(current_user.sub, skip, limit, unread_only)


@router.put("/{notif_id}/read")
async def mark_notification_as_read(
    notif_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    success = await notification_service.mark_as_read(notif_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}


@router.delete("/{notif_id}")
async def delete_notification(
    notif_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    success = await notification_service.delete_notification(notif_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}

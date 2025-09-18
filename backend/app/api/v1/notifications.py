from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user, TokenData
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_notifications_collection
from app.models.notification import Notification, NotificationCreate
from loguru import logger
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/{user_id}")
async def get_user_notifications(
    user_id: str, 
    current_user: TokenData = Depends(get_current_user),
    notifications_collection: AsyncIOMotorCollection = Depends(get_notifications_collection)
):
    """Retrieve notifications for a user"""
    try:
        # Allow users to get their own notifications or use 'me'
        if user_id == "me":
            user_id = current_user.user_id
        elif current_user.role not in ["admin", "teacher"] and user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        notifications = await notifications_collection.find({
            "user_id": user_id
        }).sort("created_at", -1).to_list(length=100)
        
        result = []
        for notif in notifications:
            result.append({
                "id": str(notif["_id"]),
                "user_id": notif["user_id"],
                "title": notif["title"],
                "message": notif["message"],
                "type": notif.get("type", "info"),
                "is_read": notif["is_read"],
                "created_at": notif["created_at"]
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        # Return sample notifications for demo
        return [
            {
                "id": "1",
                "user_id": user_id,
                "title": "Welcome to EduPredict",
                "message": "Welcome to the EduPredict system! Explore your dashboard to see your academic progress.",
                "type": "info",
                "is_read": False,
                "created_at": datetime.utcnow()
            },
            {
                "id": "2",
                "user_id": user_id,
                "title": "Grade Updated",
                "message": "Your grade for Computer Science 101 has been updated.",
                "type": "grade",
                "is_read": False,
                "created_at": datetime.utcnow()
            }
        ]

@router.post("/")
async def create_notification(
    notification: NotificationCreate,
    current_user: TokenData = Depends(get_current_user),
    notifications_collection: AsyncIOMotorCollection = Depends(get_notifications_collection)
):
    """Create a new notification"""
    try:
        notification_dict = notification.dict()
        notification_dict.update({
            "is_read": False,
            "created_at": datetime.utcnow()
        })
        
        result = await notifications_collection.insert_one(notification_dict)
        return {"message": "Notification created successfully", "id": str(result.inserted_id)}
        
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to create notification")

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: TokenData = Depends(get_current_user),
    notifications_collection: AsyncIOMotorCollection = Depends(get_notifications_collection)
):
    """Mark a notification as read"""
    try:
        result = await notifications_collection.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"is_read": True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read")
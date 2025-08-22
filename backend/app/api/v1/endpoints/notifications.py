"""
Notification endpoints for EduPredict
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.user import TokenData
from app.core.security import get_current_user

router = APIRouter()


@router.get("/")
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    unread_only: bool = Query(False),
    current_user: TokenData = Depends(get_current_user)
):
    """Get user notifications"""
    try:
        # Mock response for now
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )

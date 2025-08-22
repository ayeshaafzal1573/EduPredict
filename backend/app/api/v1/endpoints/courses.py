"""
Course management endpoints for EduPredict
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.user import TokenData
from app.core.security import get_current_user

router = APIRouter()


@router.get("/")
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    """Get list of courses"""
    try:
        # Mock response for now
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve courses"
        )

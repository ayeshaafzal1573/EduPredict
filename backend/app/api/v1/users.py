"""
User management endpoints for EduPredict (Production-ready)
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.models.user import User, UserCreate, UserUpdate, TokenData
from app.core.security import get_current_user, require_admin
from app.services.user_service import UserService
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_users_collection

router = APIRouter(tags=["Users"])

async def get_user_service() -> UserService:
    """Dependency for UserService"""
    return UserService()

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    current_user: TokenData = Depends(require_admin),
    user_service: UserService = Depends(get_user_service)
):
    """Get list of users (Admin only)"""
    try:
        users = await user_service.get_users(skip=skip, limit=limit, role=role)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    current_user: TokenData = Depends(require_admin),
    user_service: UserService = Depends(get_user_service)
):
    """Create a new user (Admin only)"""
    try:
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID"""
    if current_user.user_id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: TokenData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update user information"""
    if current_user.user_id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    updated_user = await user_service.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(require_admin),
    user_service: UserService = Depends(get_user_service)
):
    """Delete user (Admin only)"""
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}

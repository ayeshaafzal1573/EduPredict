"""
Authentication endpoints for EduPredict (simple version)
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status,Depends
from app.models.user import LoginRequest, Token, UserCreate, User, TokenData
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_user
)
from app.services.user_service import UserService
from app.core.config import settings
from app.core.database import db_manager

import logging
router = APIRouter()
user_service = UserService()
logger = logging.getLogger(__name__)


def generate_access_token(user) -> Token:
    """Generate only access token (no refresh logic)"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }
    access_token = create_access_token(token_data, access_token_expires)

    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        return await user_service.create_user(user_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Register failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    try:
        print("🔹 Login attempt for:", login_data.email)
        print("🔹 MongoDB DB instance:", db_manager.mongodb_db)

        # Try to list first few users to confirm DB connection
        try:
            users_collection = db_manager.get_collection("users")
            sample_users = await users_collection.find().to_list(5)
            print("🔹 Sample users in collection:", sample_users)
        except Exception as db_err:
            print("⚠️ Error accessing users collection:", db_err)

        # Fetch the user
        user = await user_service.get_user_by_email(login_data.email)
        print("🔹 Fetched user:", user)

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        await user_service.update_last_login(str(user.id))
        print("✅ Login successful for user:", user.email)
        return generate_access_token(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
@router.get("/me", response_model=User)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information"""
    try:
        user = await user_service.get_user_by_id(current_user.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return User(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user info failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

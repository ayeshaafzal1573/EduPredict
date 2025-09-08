from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password, get_password_hash, get_current_user, TokenData
from app.core.database import get_users_collection
from app.models.user import User, UserCreate, UserInDB, Token, LoginRequest
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(
    payload: LoginRequest, 
    collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """User login endpoint"""
    try:
        user = await collection.find_one({"email": payload.email})
        if not user or not verify_password(payload.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )

        # Update last login timestamp
        await collection.update_one(
            {"_id": user["_id"]}, 
            {"$set": {"last_login": datetime.utcnow()}}
        )

        access_token = create_access_token(
            data={
                "sub": str(user["_id"]), 
                "email": user["email"], 
                "role": user["role"]
            },
            expires_delta=timedelta(minutes=30)
        )
        
        return Token(
            access_token=access_token, 
            token_type="bearer", 
            expires_in=1800
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/register", response_model=User)
async def register_user(
    user: UserCreate, 
    collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Register a new user"""
    try:
        existing = await collection.find_one({"email": user.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Email already registered"
            )
        
        hashed_password = get_password_hash(user.password)
        user_dict = user.dict()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        user_dict["is_active"] = True
        
        result = await collection.insert_one(user_dict)
        user_in_db = await collection.find_one({"_id": result.inserted_id})
        
        return User(
            id=str(user_in_db["_id"]),
            email=user_in_db["email"],
            first_name=user_in_db["first_name"],
            last_name=user_in_db["last_name"],
            role=user_in_db["role"],
            is_active=user_in_db["is_active"],
            created_at=user_in_db["created_at"],
            updated_at=user_in_db["updated_at"],
            last_login=user_in_db.get("last_login")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user), 
    collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Get current user information"""
    try:
        user = await collection.find_one({"_id": ObjectId(current_user.user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        
        return User(
            id=str(user["_id"]),
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            role=user["role"],
            is_active=user.get("is_active", True),
            created_at=user["created_at"],
            updated_at=user["updated_at"],
            last_login=user.get("last_login")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )
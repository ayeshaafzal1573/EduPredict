from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password, get_password_hash, require_roles, UserRole
from app.core.database import get_users_collection
from app.models.user import User, UserCreate, UserInDB, Token, LoginRequest, PasswordReset, PasswordResetConfirm
from motor.motor_asyncio import AsyncIOMotorCollection
from loguru import logger
from datetime import datetime, timedelta
from app.core.security import get_current_user, require_admin, TokenData

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=User, dependencies=[Depends(require_roles([UserRole.ADMIN]))])
async def register_user(user: UserCreate, collection: AsyncIOMotorCollection = Depends(get_users_collection)):
    """
    Register a new user (Admin only)
    
    Args:
        user: User creation data
        collection: Users collection dependency
    
    Returns:
        Created user data
    
    Raises:
        HTTPException: If email exists or server error
    """
    try:
        existing = await collection.find_one({"email": user.email})
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        hashed_password = get_password_hash(user.password)
        user_dict = user.dict()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        result = await collection.insert_one(user_dict)
        user_in_db = await collection.find_one({"_id": result.inserted_id})
        user_response = User(
            id=str(user_in_db["_id"]),
            email=user_in_db["email"],
            first_name=user_in_db["first_name"],
            last_name=user_in_db["last_name"],
            role=user_in_db["role"],
            is_active=user_in_db.get("is_active", True),
            created_at=user_in_db["created_at"],
            updated_at=user_in_db["updated_at"],
            last_login=user_in_db.get("last_login")
        )
        return user_response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to register user {user.email}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, collection: AsyncIOMotorCollection = Depends(get_users_collection)):
    user = await collection.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update last login timestamp
    await collection.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.utcnow()}})

    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=60)
    )
    return Token(access_token=access_token, token_type="bearer", expires_in=3600)
@router.get("/me", response_model=User)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user), collection: AsyncIOMotorCollection = Depends(get_users_collection)):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        collection: Users collection dependency
    
    Returns:
        Current user data
    
    Raises:
        HTTPException: If user not found
    """
    try:
        from bson import ObjectId
        user = await collection.find_one({"_id": ObjectId(current_user.user_id)})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
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
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/password-reset", response_model=dict)
async def request_password_reset(reset: PasswordReset, collection: AsyncIOMotorCollection = Depends(get_users_collection)):
    """
    Request password reset (sends reset token via email)
    
    Args:
        reset: Email for password reset
        collection: Users collection dependency
    
    Returns:
        Confirmation message
    
    Raises:
        HTTPException: If user not found or server error
    """
    try:
        user = await collection.find_one({"email": reset.email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        # Placeholder: Generate and send reset token (e.g., via email service)
        reset_token = create_access_token(data={"sub": str(user["_id"]), "email": user["email"]}, expires_delta=timedelta(hours=1))
        logger.info(f"Password reset requested for {reset.email}, token: {reset_token}")
        return {"message": "Password reset token sent to email"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to request password reset for {reset.email}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/password-reset/confirm", response_model=dict)
async def confirm_password_reset(reset: PasswordResetConfirm, collection: AsyncIOMotorCollection = Depends(get_users_collection)):
    """
    Confirm password reset with token
    
    Args:
        reset: Reset token and new password
        collection: Users collection dependency
    
    Returns:
        Confirmation message
    
    Raises:
        HTTPException: If token invalid or server error
    """
    try:
        # Placeholder: Decode reset token (requires JWT validation)
        user_id = "decoded_user_id"  # Replace with actual token decoding
        hashed_password = get_password_hash(reset.new_password)
        result = await collection.update_one(
            {"_id": user_id},
            {"$set": {"hashed_password": hashed_password, "updated_at": datetime.utcnow()}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"message": "Password reset successful"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to confirm password reset: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
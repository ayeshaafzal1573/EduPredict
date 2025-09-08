from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.user import User, UserCreate, UserUpdate, TokenData
from app.core.security import get_current_user, get_password_hash
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_users_collection
from loguru import logger
from bson import ObjectId
from datetime import datetime

router = APIRouter(tags=["Users"])

@router.get("/", response_model=List[dict])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Get list of users"""
    try:
        query = {"is_active": True}
        if role:
            query["role"] = role
        
        users = await users_collection.find(query).skip(skip).limit(limit).to_list(length=limit)
        
        result = []
        for user in users:
            result.append({
                "id": str(user["_id"]),
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "role": user["role"],
                "is_active": user["is_active"],
                "created_at": user["created_at"],
                "updated_at": user["updated_at"],
                "last_login": user.get("last_login")
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return []

@router.post("/", response_model=dict)
async def create_user(
    user_data: UserCreate,
    current_user: TokenData = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Create a new user"""
    try:
        # Check if email already exists
        existing = await users_collection.find_one({"email": user_data.email})
        if existing:
            raise HTTPException(status_code=409, detail="Email already exists")
        
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.dict()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        user_dict["is_active"] = True
        
        result = await users_collection.insert_one(user_dict)
        return {"message": "User created successfully", "id": str(result.inserted_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Get user by ID"""
    try:
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "role": user["role"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
            "last_login": user.get("last_login")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: TokenData = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Update user information"""
    try:
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        update_data = user_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """Delete user (soft delete)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")
"""
User service for handling user-related operations
"""

from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.models.user import UserCreate, UserUpdate, UserInDB, User
from app.core.database import get_users_collection
from app.core.security import get_password_hash


class UserService:
    """Service class for user operations"""

    def __init__(self):
        self.collection = None

    def _get_collection(self):
        """Get users collection lazily"""
        if self.collection is None:
            self.collection = get_users_collection()
        return self.collection
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            collection = self._get_collection()
            # Hash password
            hashed_password = get_password_hash(user_data.password)

            # Create user document
            user_dict = user_data.model_dump(exclude={"password"})
            user_dict["hashed_password"] = hashed_password
            user_dict["created_at"] = datetime.utcnow()
            user_dict["updated_at"] = datetime.utcnow()

            # Insert user
            result = await collection.insert_one(user_dict)

            # Get created user
            created_user = await collection.find_one({"_id": result.inserted_id})
            return self._convert_to_user_model(created_user)
            
        except DuplicateKeyError:
            raise ValueError("Email already exists")
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        try:
            collection = self._get_collection()
            user_doc = await collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return UserInDB(**user_doc)
            return None
        except Exception:
            return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        try:
            collection = self._get_collection()
            user_doc = await collection.find_one({"email": email})
            if user_doc:
                return UserInDB(**user_doc)
            return None
        except Exception:
            return None
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        try:
            collection = self._get_collection()
            update_data = user_data.model_dump(exclude_unset=True)
            if update_data:
                update_data["updated_at"] = datetime.utcnow()

                result = await collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}
                )

                if result.modified_count:
                    updated_user = await collection.find_one({"_id": ObjectId(user_id)})
                    return self._convert_to_user_model(updated_user)

            return None
        except Exception as e:
            raise Exception(f"Failed to update user: {str(e)}")
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by setting is_active to False)"""
        try:
            collection = self._get_collection()
            result = await collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def get_users(self, skip: int = 0, limit: int = 100, role: Optional[str] = None) -> List[User]:
        """Get list of users with pagination and filtering"""
        try:
            collection = self._get_collection()
            query = {"is_active": True}
            if role:
                query["role"] = role

            cursor = collection.find(query).skip(skip).limit(limit)
            users = await cursor.to_list(length=limit)

            return [self._convert_to_user_model(user) for user in users]
        except Exception:
            return []
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            collection = self._get_collection()
            result = await collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def count_users(self, role: Optional[str] = None) -> int:
        """Count total users"""
        try:
            collection = self._get_collection()
            query = {"is_active": True}
            if role:
                query["role"] = role
            return await collection.count_documents(query)
        except Exception:
            return 0
    
    def _convert_to_user_model(self, user_doc: dict) -> User:
        """Convert database document to User model"""
        return User(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            first_name=user_doc["first_name"],
            last_name=user_doc["last_name"],
            role=user_doc["role"],
            is_active=user_doc["is_active"],
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"],
            last_login=user_doc.get("last_login")
        )

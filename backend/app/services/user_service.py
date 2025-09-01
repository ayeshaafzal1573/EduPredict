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
        # ❌ Ab yaha collection set nahi karenge (DB ready nahi hota)
        pass

    def _get_collection(self):
        """Always fetch collection dynamically"""
        return get_users_collection()

    async def get_by_email(self, email: str):
        return await self._get_collection().find_one({"email": email})

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        collection = self._get_collection()
        hashed_password = get_password_hash(user_data.password)

        user_dict = user_data.model_dump(exclude={"password"})
        user_dict.update({
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        })

        try:
            result = await collection.insert_one(user_dict)
            created_user = await collection.find_one({"_id": result.inserted_id})
            return self._convert_to_user_model(created_user)
        except DuplicateKeyError:
            raise ValueError("Email already exists")

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        user_doc = await self._get_collection().find_one({"_id": ObjectId(user_id)})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user_doc = await self._get_collection().find_one({"email": email})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            return None

        update_data["updated_at"] = datetime.utcnow()
        result = await self._get_collection().update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        if result.modified_count:
            updated_user = await self._get_collection().find_one({"_id": ObjectId(user_id)})
            return self._convert_to_user_model(updated_user)
        return None

    async def delete_user(self, user_id: str) -> bool:
        result = await self._get_collection().update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def get_users(self, skip: int = 0, limit: int = 100, role: Optional[str] = None) -> List[User]:
        query = {"is_active": True}
        if role:
            query["role"] = role

        cursor = self._get_collection().find(query).skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        return [self._convert_to_user_model(u) for u in users]

    async def update_last_login(self, user_id: str) -> bool:
        result = await self._get_collection().update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def count_users(self, role: Optional[str] = None) -> int:
        query = {"is_active": True}
        if role:
            query["role"] = role
        return await self._get_collection().count_documents(query)

    def _convert_to_user_model(self, user_doc: dict) -> User:
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

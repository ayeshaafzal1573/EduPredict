from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId
from app.models.base import PyObjectId, MongoBaseModel


class UserRole(str, Enum):
    """User roles in the system"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    ANALYST = "analyst"


class UserBase(MongoBaseModel):
    """Base user model"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    role: UserRole
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8, max_length=100)

    @validator("password")
    def validate_password(cls, v):
        """Ensure password meets complexity requirements"""
        if not any(c.isupper() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one uppercase letter and one digit")
        return v


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """User model as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class User(UserBase):
    """User response model"""
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    sub: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class PasswordReset(BaseModel):
    """Password reset model"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def validate_new_password(cls, v):
        """Ensure new password meets complexity requirements"""
        if not any(c.isupper() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("New password must contain at least one uppercase letter and one digit")
        return v
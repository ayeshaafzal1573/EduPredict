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

    @validator("email")
    def validate_email(cls, v):
        """Ensure email is valid"""
        if not v or "@" not in v:
            raise ValueError("Valid email address is required")
        return v.lower()

    @validator("first_name", "last_name")
    def validate_names(cls, v):
        """Ensure names are not empty and contain only valid characters"""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        if not v.replace(" ", "").replace("-", "").replace("'", "").isalpha():
            raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
        return v.strip()


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8, max_length=100)

    @validator("password")
    def validate_password(cls, v):
        """Ensure password meets complexity requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    @validator("email")
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Valid email address is required")
        return v.lower() if v else v

    @validator("first_name", "last_name")
    def validate_names(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Name cannot be empty")
            if not v.replace(" ", "").replace("-", "").replace("'", "").isalpha():
                raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
            return v.strip()
        return v


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

    @validator("email")
    def validate_email(cls, v):
        if not v or "@" not in v:
            raise ValueError("Valid email address is required")
        return v.lower()

    @validator("password")
    def validate_password(cls, v):
        if not v or len(v) < 1:
            raise ValueError("Password is required")
        return v


class PasswordReset(BaseModel):
    """Password reset model"""
    email: EmailStr

    @validator("email")
    def validate_email(cls, v):
        if not v or "@" not in v:
            raise ValueError("Valid email address is required")
        return v.lower()


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def validate_new_password(cls, v):
        """Ensure new password meets complexity requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
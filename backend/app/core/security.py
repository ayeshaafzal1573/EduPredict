
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.user import UserRole, TokenData
from loguru import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
    
    Returns:
        bool: True if passwords match
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate hashed password
    
    Args:
        password: Plain text password
    
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data
        expires_delta: Token expiration time
    
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Get current user from JWT token
    
    Args:
        token: JWT token
    
    Returns:
        TokenData: Decoded token data
    
    Raises:
        HTTPException: If token invalid or user not found
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        if not user_id or not email or not role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return TokenData(user_id=user_id, email=email, role=UserRole(role))
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_roles(roles: list[UserRole]):
    """
    Dependency to restrict access to specific roles
    
    Args:
        roles: List of allowed roles
    
    Returns:
        Callable: Dependency function
    """
    async def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return role_checker

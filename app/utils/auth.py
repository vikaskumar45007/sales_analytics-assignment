import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from app.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

# Sample users database 
USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@salesanalytics.com",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin",
        "is_active": True
    },
    "agent1": {
        "username": "agent1",
        "email": "agent1@salesanalytics.com",
        "hashed_password": pwd_context.hash("agent123"),
        "role": "agent",
        "is_active": True
    },
    "manager1": {
        "username": "manager1",
        "email": "manager1@salesanalytics.com",
        "hashed_password": pwd_context.hash("manager123"),
        "role": "manager",
        "is_active": True
    }
}


class AuthService:
    """Authentication service for JWT token management"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password"""
        user = USERS_DB.get(username)
        if not user:
            return None
        if not AuthService.verify_password(password, user["hashed_password"]):
            return None
        if not user["is_active"]:
            return None
        return user
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            username: str = payload.get("sub")
            if username is None:
                return None
            return payload
        except jwt.PyJWTError as e:
            logger.error(f"JWT verification failed: {e}")
            return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = USERS_DB.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current active user"""
    if not current_user["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_role: str):
    """Decorator to require specific user role"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)):
        if current_user["role"] != required_role and current_user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker


# Role-specific dependencies
require_admin = require_role("admin")
require_manager = require_role("manager")
require_agent = require_role("agent")

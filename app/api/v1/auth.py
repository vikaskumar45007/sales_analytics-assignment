import logging
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserLogin, UserRegister, Token, UserResponse, UserCreate
from app.utils.auth import AuthService, get_current_active_user, require_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user and return JWT token"""
    try:
        user = AuthService.authenticate_user(user_credentials.username, user_credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = AuthService.create_access_token(
            data={"sub": user["username"], "role": user["role"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds())
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, current_user: Dict[str, Any] = Depends(require_admin)):
    """Register a new user (admin only)"""
    try:
        if user_data.username in AuthService.USERS_DB:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        hashed_password = AuthService.get_password_hash(user_data.password)
        new_user = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "role": user_data.role,
            "is_active": True
        }
        
        AuthService.USERS_DB[user_data.username] = new_user
        
        return UserResponse(
            username=new_user["username"],
            email=new_user["email"],
            role=new_user["role"],
            is_active=new_user["is_active"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        username=current_user["username"],
        email=current_user["email"],
        role=current_user["role"],
        is_active=current_user["is_active"]
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Refresh JWT token"""
    try:
        access_token_expires = timedelta(minutes=30)
        access_token = AuthService.create_access_token(
            data={"sub": current_user["username"], "role": current_user["role"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds())
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

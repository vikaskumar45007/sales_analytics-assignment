from pydantic import BaseModel, EmailStr
from typing import Optional


class UserLogin(BaseModel):
    """User login request schema"""
    username: str
    password: str


class UserRegister(BaseModel):
    """User registration request schema"""
    username: str
    email: EmailStr
    password: str
    role: str = "agent"


class Token(BaseModel):
    """JWT token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema"""
    username: str
    email: str
    role: str
    is_active: bool


class UserCreate(BaseModel):
    """User creation schema"""
    username: str
    email: EmailStr
    password: str
    role: str = "agent"
    is_active: bool = True

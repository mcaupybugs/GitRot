from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base model for user"""
    email: EmailStr
    name: str
    image: Optional[str] = None

class UserCreate(UserBase):
    """Model for creating a new user"""
    provider: str = "google"
    provider_id: str

class UserUpdate(BaseModel):
    """Model for updating user information"""
    name: Optional[str] = None
    image: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Model for user response"""
    id: str
    is_active: bool
    provider: str
    provider_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserAuthRequest(BaseModel):
    """Model for OAuth authentication request"""
    email: EmailStr
    name: str
    image: Optional[str] = None
    provider: str = "google"
    provider_id: str

class UserAuthResponse(BaseModel):
    """Model for OAuth authentication response"""
    user_id: str
    is_new: bool
    email: str
    name: str
    image: Optional[str] = None
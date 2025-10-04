from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base model for user"""
    email: EmailStr
    name: str

class UserCreate(UserBase):
    """Model for creating a new user"""
    pass

class UserUpdate(BaseModel):
    """Model for updating user information"""
    name: Optional[str] = None
    is_active: Optional[str] = None
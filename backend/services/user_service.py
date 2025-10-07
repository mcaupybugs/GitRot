from sqlalchemy.orm import Session
from database.models import User
from models.user_model import UserCreate, UserUpdate, UserAuthRequest
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service for user-related operations"""

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str)-> Optional[User]:
        """Get user by id"""
        return db.query(User).filter(User.id == user_id).first()
    

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        db_user = User(
            email = user_data.email,
            name = user_data.name,
            image = user_data.image,
            provider = user_data.provider,
            provider_id = user_data.provider_id,
            is_active = True
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Created new user: {db_user.email} via {db_user.provider}")
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        logger.info(f"Updated user: {db_user.email}")
        return db_user
    
    @staticmethod
    def register_or_login(db: Session, auth_data: UserAuthRequest) -> tuple[User,bool]:
        existing_user = UserService.get_user_by_email(db, auth_data.email)

        if existing_user:
            # User exists - update profile info if changed
            needs_update = False
            if auth_data.name and existing_user.name != auth_data.name:
                existing_user.name = auth_data.name
                needs_update = True
            if auth_data.image and existing_user.image != auth_data.image:
                existing_user.image = auth_data.image
                needs_update = True
            
            # if the same user is with another provider ex github etc
            if auth_data.provider and auth_data.provider!= existing_user.provider:
                logger.warning(
                f"Account conflict: {auth_data.email} exists with {existing_user.provider}, "
                f"but trying to sign in with {auth_data.provider}"
                )
                raise ValueError(
                    f"An account with this email already exists using {existing_user.provider}. "
                    f"Please sign in with {existing_user.provider} instead."
                )            
            if needs_update:
                db.commit()
                db.refresh(existing_user)
                logger.info(f"Updated existing user profile: {existing_user.email}")
            
            return existing_user, False
            
        user_create = UserCreate(
            email=auth_data.email,
            name=auth_data.name,
            image=auth_data.image,
            provider=auth_data.provider,
            provider_id=auth_data.provider_id
        )

        new_user = UserService.create_user(db, user_create)
        return new_user, True
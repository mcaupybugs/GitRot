from sqlalchemy import Column, String, DateTime, Boolean, Integer, func, Index
from database.config import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    image = Column(String, nullable=True)
    provider = Column(String, nullable=False, default="google")
    provider_id = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"User id:{self.id}, email: {self.email}"
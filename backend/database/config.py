from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager
import os

class Base(DeclarativeBase):
    pass

def get_database_url():
    """Get the database URL based on environment"""
    return os.getenv("DATABASE_URL", "sqlite:///./gitrot_dev.db")

    
DATABASE_URL = get_database_url()
IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
    pool_size=None if IS_SQLITE else 10,
    max_overflow=None if IS_SQLITE else 20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

def create_tables():
    """create database tables"""
    from backend.database import models
    Base.metadata.create_all(bind=engine)

@contextmanager
def session_scope():
    db = SessionLocal()
    try: 
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
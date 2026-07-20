from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.database.session")

# Setup SQLAlchemy database engine
try:
    logger.info(f"Connecting to database: {settings.POSTGRES_DB} at {settings.POSTGRES_SERVER}")
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,  # Test connections before executing queries
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,   # Recycle connections after 1 hour
        pool_timeout=30      # Timeout waiting for pool connection
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding database session and closing it afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

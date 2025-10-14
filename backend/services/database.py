"""
Database Service
Handles database connections, sessions, and operations
"""

from sqlalchemy import create_engine  # For creating database connections
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession  # For async database operations
from sqlalchemy.orm import sessionmaker, Session  # For managing database sessions
from sqlalchemy.pool import NullPool  # Connection pooling strategy
import os  # For environment variables
from typing import AsyncGenerator  # Type hint for async generators
import logging  # For logging database events

from models.database import Base  # Base class for all database models

logger = logging.getLogger(__name__)

# ============= Singleton Pattern Implementation =============

class DatabaseService:
    """Singleton database service for managing connections"""
    _instance = None  # Stores the single instance
    _initialized = False  # Tracks if instance is initialized

    def __new__(cls):
        if cls._instance is None:  # First time creating instance?
            cls._instance = super(DatabaseService, cls).__new__(cls)  # Create new instance
        return cls._instance  # Return the single instance

    def __init__(self):
        if not self._initialized:  # Only initialize once
            self._initialize()  # Do actual initialization
            self.__class__._initialized = True  # Mark as initialized

    def _initialize(self):
        """Initialize database connections"""
        # Database configuration
        self.database_url = os.getenv(
            "DATABASE_URL",  # Get from environment variable
            "postgresql://postgres:password@localhost/finmentor"  # Default local database
        )

        # Convert to async URL if needed
        if self.database_url.startswith("postgresql://"):  # Standard PostgreSQL URL?
            self.async_database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")  # Make it async-compatible
        else:
            self.async_database_url = self.database_url  # Already async-compatible

        # Create async engine
        self.engine = create_async_engine(
            self.async_database_url,  # Async-compatible database URL
            echo=os.getenv("DEBUG", "False").lower() == "true",  # Log SQL queries if DEBUG=true
            poolclass=NullPool,  # No connection pooling (creates new connections each time)
        )

        # Create async session factory
        self.AsyncSessionLocal = sessionmaker(
            self.engine,  # Use async engine
            class_=AsyncSession,  # Create AsyncSession instances
            expire_on_commit=False  # Don't expire objects after commit (can still use them)
        )

        # Sync engine for migrations
        self.sync_engine = create_engine(
            self.database_url,  # Regular (non-async) database URL
            echo=os.getenv("DEBUG", "False").lower() == "true"  # Log SQL if debugging
        )

        # Sync session for scripts
        self.SessionLocal = sessionmaker(
            autocommit=False,  # Manual commit required (safer)
            autoflush=False,  # Manual flush required (more control)
            bind=self.sync_engine  # Connect to sync engine
        )

        logger.info("DatabaseService singleton initialized")

    async def get_session(self) -> AsyncSession:
        """Get an async database session"""
        async with self.AsyncSessionLocal() as session:  # Create new session
            return session  # Return for use

    def get_sync_session(self) -> Session:
        """Get a sync database session"""
        return self.SessionLocal()  # Create and return sync session

# Create singleton instance
db_service = DatabaseService()  # This creates the one and only instance

# Module-level references for backward compatibility
DATABASE_URL = db_service.database_url  # Expose database URL
ASYNC_DATABASE_URL = db_service.async_database_url  # Expose async URL
engine = db_service.engine  # Expose async engine
AsyncSessionLocal = db_service.AsyncSessionLocal  # Expose async session factory
sync_engine = db_service.sync_engine  # Expose sync engine
SessionLocal = db_service.SessionLocal  # Expose sync session factory

# ============= Database Initialization =============

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:  # Start database transaction
            # Create all tables defined in models
            await conn.run_sync(Base.metadata.create_all)  # Run synchronously in async context
            logger.info("Database tables created successfully")  # Log success
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")  # Log error
        raise  # Re-raise exception

async def drop_db():
    """Drop all database tables (use with caution!)"""
    try:
        async with engine.begin() as conn:  # Start transaction
            await conn.run_sync(Base.metadata.drop_all)  # Drop all tables
            logger.info("Database tables dropped")  # Log completion
    except Exception as e:
        logger.error(f"Failed to drop database: {e}")  # Log error
        raise  # Re-raise for caller to handle

# ============= Session Management =============

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session
    Use in FastAPI endpoints with Depends()
    """
    async with AsyncSessionLocal() as session:  # Create new session
        try:
            yield session  # Provide session to endpoint
            await session.commit()  # Commit changes if successful
        except Exception:
            await session.rollback()  # Rollback on error
            raise  # Re-raise exception
        finally:
            await session.close()  # Always close session

def get_sync_db() -> Session:
    """Get synchronous database session for scripts"""
    db = SessionLocal()  # Create sync session
    try:
        return db  # Return for use
    finally:
        db.close()  # Ensure session is closed

# ============= Connection Testing =============

async def test_connection():
    """Test database connection"""
    try:
        async with engine.connect() as conn:  # Try to connect
            result = await conn.execute("SELECT 1")  # Simple test query
            logger.info("Database connection successful")  # Log success
            return True  # Connection works
    except Exception as e:
        logger.error(f"Database connection failed: {e}")  # Log failure
        return False  # Connection failed
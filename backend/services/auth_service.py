"""
Authentication Service
Handles user authentication, registration, and JWT tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import logging

from models.database import User
from services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service for user authentication and management"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversation_service = ConversationService(db)

    # ============= Password Management =============

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    # ============= Token Management =============

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            if payload.get("type") != token_type:
                return None

            return payload

        except JWTError:
            return None

    # ============= User Management =============

    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        **profile_data
    ) -> Optional[User]:
        """Register a new user"""
        try:
            # Check if user already exists
            result = await self.db.execute(
                select(User).where(
                    (User.email == email) | (User.username == username)
                )
            )
            if result.scalar_one_or_none():
                logger.warning(f"User already exists: {email} or {username}")
                return None

            # Create new user
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=self.get_password_hash(password),
                age=profile_data.get("age"),
                user_type=profile_data.get("user_type", "beginner"),
                education_level=profile_data.get("education_level", "basic"),
                risk_tolerance=profile_data.get("risk_tolerance", "moderate"),
                financial_goals=profile_data.get("financial_goals", []),
                preferred_language=profile_data.get("preferred_language", "en"),
                preferred_output=profile_data.get("preferred_output", "text"),
                created_at=datetime.utcnow()
            )

            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            # Log registration activity
            await self.conversation_service.log_user_activity(
                user_id=user.id,
                activity_type="registration",
                activity_data={"username": username, "email": email}
            )

            logger.info(f"User registered: {username} ({email})")
            return user

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to register user: {e}")
            return None

    async def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
        """Authenticate a user with username/email and password"""
        try:
            # Find user by username or email
            result = await self.db.execute(
                select(User).where(
                    (User.username == username_or_email) |
                    (User.email == username_or_email)
                )
            )
            user = result.scalar_one_or_none()

            if not user:
                return None

            if not self.verify_password(password, user.hashed_password):
                return None

            # Update last login
            user.last_login = datetime.utcnow()
            await self.db.commit()

            # Log login activity
            await self.conversation_service.log_user_activity(
                user_id=user.id,
                activity_type="login",
                activity_data={"method": "password"}
            )

            return user

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None

    async def update_user_profile(
        self,
        user_id: str,
        **profile_data
    ) -> Optional[User]:
        """Update user profile"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return None

            # Update allowed fields
            allowed_fields = [
                "full_name", "age", "user_type", "education_level",
                "risk_tolerance", "financial_goals", "preferred_language",
                "preferred_output"
            ]

            for field, value in profile_data.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)

            user.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"Updated profile for user {user_id}")
            return user

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update user profile: {e}")
            return None

    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False

            if not self.verify_password(old_password, user.hashed_password):
                return False

            user.hashed_password = self.get_password_hash(new_password)
            user.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Password changed for user {user_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to change password: {e}")
            return False

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user account (soft delete by marking inactive)"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False

            # Soft delete - mark as inactive
            user.is_active = False
            user.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"User {user_id} marked as inactive")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete user: {e}")
            return False

    # ============= Token Validation =============

    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        return await self.get_user_by_id(user_id)

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token"""
        payload = self.verify_token(refresh_token, token_type="refresh")
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Verify user still exists and is active
        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            return None

        # Create new access token
        return self.create_access_token({"sub": user_id})

    # ============= User Statistics =============

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics and activity summary"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return {}

            # Get conversation stats from conversation service
            stats = await self.conversation_service.get_user_statistics(user_id)

            # Add user profile info
            stats.update({
                "username": user.username,
                "member_since": user.created_at.isoformat() if user.created_at else None,
                "user_type": user.user_type,
                "education_level": user.education_level,
                "is_premium": user.is_premium
            })

            return stats

        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {}
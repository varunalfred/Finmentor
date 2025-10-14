"""
Authentication Router
Handles user registration, login, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI components
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # OAuth2 authentication
from pydantic import BaseModel, EmailStr  # Data validation
from typing import Optional  # Type hints for optional fields
from datetime import datetime  # For timestamps

from services.auth_service import AuthService  # Authentication business logic
from services.database import get_db  # Database session dependency
from sqlalchemy.ext.asyncio import AsyncSession  # Async database sessions

router = APIRouter()  # Create router for auth endpoints

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")  # Defines where to get tokens

# Initialize auth service
auth_service = AuthService()  # Singleton service for auth operations

# ============= Request/Response Models =============

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr  # Valid email address required
    username: str  # Unique username
    password: str  # Password (will be hashed)
    full_name: Optional[str] = None  # Optional real name
    user_type: Optional[str] = "beginner"  # Experience level: beginner/intermediate/advanced
    education_level: Optional[str] = "basic"  # Financial knowledge level
    risk_tolerance: Optional[str] = "moderate"  # Investment risk preference

class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str

class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    user_type: str
    education_level: str
    risk_tolerance: str
    is_premium: bool
    created_at: datetime

# ============= Auth Endpoints =============

@router.post("/register", response_model=UserResponse)  # POST to /api/auth/register
async def register(
    user_data: UserRegister,  # Registration data from request body
    db: AsyncSession = Depends(get_db)  # Inject database session
):
    """Register a new user"""
    try:
        # Check if user exists
        existing = await auth_service.get_user_by_email(db, user_data.email)  # Query by email
        if existing:  # Email already taken?
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,  # 400 Bad Request
                detail="Email already registered"  # Error message
            )

        # Create new user
        user = await auth_service.create_user(
            db=db,  # Database session
            email=user_data.email,  # User's email
            username=user_data.username,  # Chosen username
            password=user_data.password,  # Password (will be hashed in service)
            full_name=user_data.full_name,  # Optional full name
            user_type=user_data.user_type,  # Experience level
            education_level=user_data.education_level,  # Knowledge level
            risk_tolerance=user_data.risk_tolerance  # Risk preference
        )

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            user_type=user.user_type,
            education_level=user.education_level,
            risk_tolerance=user.risk_tolerance,
            is_premium=user.is_premium,
            created_at=user.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)  # POST to /api/auth/login
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # Standard OAuth2 form (username/password)
    db: AsyncSession = Depends(get_db)  # Database session
):
    """Login and get access token"""
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(
            db=db,  # Database to check
            username=form_data.username,  # Provided username
            password=form_data.password  # Provided password (will be verified)
        )

        if not user:  # Authentication failed?
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,  # 401 Unauthorized
                detail="Invalid username or password",  # Error message
                headers={"WWW-Authenticate": "Bearer"}  # OAuth2 header
            )

        # Create access token
        token = auth_service.create_access_token(
            data={"sub": user.username, "user_id": user.id}  # Token payload (subject and ID)
        )

        return Token(
            access_token=token,  # The JWT token
            token_type="bearer",  # OAuth2 bearer token
            expires_in=auth_service.access_token_expire_minutes * 60  # Expiry in seconds
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/token", response_model=Token)  # OAuth2 standard endpoint
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),  # OAuth2 form data
    db: AsyncSession = Depends(get_db)  # Database session
):
    """OAuth2 compatible token endpoint"""
    return await login(form_data, db)  # Just calls login endpoint

@router.get("/me", response_model=UserResponse)  # GET /api/auth/me
async def get_current_user(
    token: str = Depends(oauth2_scheme),  # Extract token from Authorization header
    db: AsyncSession = Depends(get_db)  # Database session
):
    """Get current user information"""
    try:
        # Decode token
        payload = auth_service.decode_token(token)  # Decode JWT token
        if not payload:  # Invalid or expired token?
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,  # 401 error
                detail="Invalid token",  # Error message
                headers={"WWW-Authenticate": "Bearer"}  # OAuth2 header
            )

        # Get user
        username = payload.get("sub")  # Extract username from token payload
        user = await auth_service.get_user_by_username(db, username)  # Fetch user from DB

        if not user:  # User doesn't exist?
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,  # 404 Not Found
                detail="User not found"  # Error message
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            user_type=user.user_type,
            education_level=user.education_level,
            risk_tolerance=user.risk_tolerance,
            is_premium=user.is_premium,
            created_at=user.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_token: str = Depends(oauth2_scheme)
):
    """Refresh access token"""
    try:
        # Decode current token
        payload = auth_service.decode_token(current_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Create new token with same data
        new_token = auth_service.create_access_token(
            data={"sub": payload.get("sub"), "user_id": payload.get("user_id")}
        )

        return Token(
            access_token=new_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout")  # POST /api/auth/logout
async def logout(token: str = Depends(oauth2_scheme)):  # Require valid token
    """Logout user (client should discard token)"""
    # In a stateless JWT system, logout is handled client-side
    # If using Redis, we could blacklist the token here
    return {"message": "Logged out successfully"}  # Success message

# ============= Dependency for Protected Routes =============

async def get_current_active_user(
    token: str = Depends(oauth2_scheme),  # Extract token from header
    db: AsyncSession = Depends(get_db)  # Get database session
):
    """Dependency to get current active user for protected routes"""
    try:
        payload = auth_service.decode_token(token)  # Decode JWT
        if not payload:  # Invalid token?
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,  # 401 error
                detail="Invalid token",  # Error message
                headers={"WWW-Authenticate": "Bearer"}  # OAuth2 header
            )

        username = payload.get("sub")  # Get username from token
        user = await auth_service.get_user_by_username(db, username)  # Fetch from DB

        if not user:  # User not found?
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,  # 404 error
                detail="User not found"  # Error message
            )

        if not user.is_active:  # User account deactivated?
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,  # 400 error
                detail="Inactive user"  # Error message
            )

        return user  # Return user object for endpoint to use

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )
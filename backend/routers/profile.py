from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from models.database import User, Portfolio, Holding, UserActivity, Conversation
from services.database import get_db
from services.auth_service import AuthService
import shutil
import os
import uuid

router = APIRouter(prefix="/api", tags=["profile"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Helper function to get auth service with database session
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get AuthService instance with database session"""
    return AuthService(db)

# Dependency to get current authenticated user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user from JWT token"""
    try:
        # Verify and decode token
        payload = auth_service.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Get user
        username = payload.get("sub")
        user = await auth_service.get_user_by_username(username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Helper to log user activity
def log_user_activity(db: Session, user_id: str, activity_type: str, data: Dict = None):
    try:
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            activity_data=data or {}
        )
        db.add(activity)
        db.commit()
    except Exception as e:
        print(f"Failed to log activity: {e}")

# Pydantic models for requests
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    user_type: Optional[str] = None
    education_level: Optional[str] = None
    risk_tolerance: Optional[str] = None
    financial_goals: Optional[List[str]] = None
    preferred_language: Optional[str] = None
    preferred_output: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

# Get user profile
@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile information"""
    try:
        return {
            "success": True,
            "data": {
                "id": current_user.id,
                "email": current_user.email,
                "username": current_user.username,
                "full_name": current_user.full_name,
                "age": current_user.age,
                "user_type": current_user.user_type,
                "education_level": current_user.education_level,
                "risk_tolerance": current_user.risk_tolerance,
                "financial_goals": current_user.financial_goals or [],
                "preferred_language": current_user.preferred_language,
                "preferred_output": current_user.preferred_output,
                "is_premium": current_user.is_premium,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update user profile
@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    try:
        # Update fields if provided
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name
        if profile_data.age is not None:
            current_user.age = profile_data.age
        if profile_data.user_type is not None:
            current_user.user_type = profile_data.user_type
        if profile_data.education_level is not None:
            current_user.education_level = profile_data.education_level
        if profile_data.risk_tolerance is not None:
            current_user.risk_tolerance = profile_data.risk_tolerance
        if profile_data.financial_goals is not None:
            current_user.financial_goals = profile_data.financial_goals
        if profile_data.preferred_language is not None:
            current_user.preferred_language = profile_data.preferred_language
        if profile_data.preferred_output is not None:
            current_user.preferred_output = profile_data.preferred_output
            
        db.commit()
        db.refresh(current_user)
        
        # Log activity
        log_user_activity(db, current_user.id, "update_profile", {"updated_fields": profile_data.dict(exclude_unset=True)})
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": current_user.to_dict()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Upload profile picture
@router.post("/profile/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    try:
        # Create uploads directory if not exists
        UPLOAD_DIR = "static/uploads/avatars"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Generate unique filename
        file_ext = file.filename.split(".")[-1]
        filename = f"{current_user.id}_{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Update user profile
        # Note: In production, you'd upload to S3/Cloudinary and store the URL
        # For local, we'll store the relative path
        relative_path = f"/static/uploads/avatars/{filename}"
        current_user.profile_picture_url = relative_path
        
        db.commit()
        
        # Log activity
        log_user_activity(db, current_user.id, "update_avatar", {"filename": filename})
        
        return {
            "success": True,
            "url": relative_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# Get user's portfolio holdings (used as watchlist)
@router.get("/watchlist")
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's portfolio holdings (acting as watchlist)"""
    try:
        # Get user's portfolios
        portfolios = db.query(Portfolio).filter(
            Portfolio.user_id == current_user.id
        ).all()
        
        # Collect all holdings from all portfolios
        all_holdings = []
        for portfolio in portfolios:
            holdings = db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id
            ).all()
            
            for holding in holdings:
                all_holdings.append({
                    "symbol": holding.symbol,
                    "quantity": holding.quantity,
                    "average_cost": holding.average_cost,
                    "current_price": holding.current_price,
                    "current_value": holding.current_value,
                    "total_return": holding.total_return,
                    "percentage_return": holding.percentage_return,
                    "portfolio_name": portfolio.name
                })
        
        return {
            "success": True,
            "data": all_holdings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get watchlist/portfolio stats
@router.get("/watchlist/stats")
async def get_watchlist_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio/watchlist statistics"""
    try:
        # Get user's portfolios
        portfolios = db.query(Portfolio).filter(
            Portfolio.user_id == current_user.id
        ).all()
        
        total_stocks = 0
        total_value = 0.0
        gainers = 0
        losers = 0
        
        for portfolio in portfolios:
            holdings = db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id
            ).all()
            
            total_stocks += len(holdings)
            
            for holding in holdings:
                if holding.current_value:
                    total_value += holding.current_value
                
                if holding.percentage_return:
                    if holding.percentage_return > 0:
                        gainers += 1
                    elif holding.percentage_return < 0:
                        losers += 1
        
        return {
            "success": True,
            "data": {
                "total_stocks": total_stocks,
                "total_value": round(total_value, 2),
                "gainers": gainers,
                "losers": losers
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add stock to watchlist
@router.post("/watchlist")
async def add_to_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a stock to watchlist"""
    try:
        # Check if stock is already in watchlist
        # First find the user's watchlist portfolio
        watchlist_portfolio = db.query(Portfolio).filter(
            Portfolio.user_id == current_user.id,
            Portfolio.name == "Watchlist"
        ).first()
        
        # If not exists, create it
        if not watchlist_portfolio:
            watchlist_portfolio = Portfolio(
                user_id=current_user.id,
                name="Watchlist",
                is_virtual=True
            )
            db.add(watchlist_portfolio)
            db.commit()
            db.refresh(watchlist_portfolio)
            
        # Check if holding exists
        existing_holding = db.query(Holding).filter(
            Holding.portfolio_id == watchlist_portfolio.id,
            Holding.symbol == symbol
        ).first()
        
        if existing_holding:
            return {
                "success": True,
                "message": f"{symbol} is already in your watchlist"
            }
            
        # Add new holding
        # Note: In a real app, we'd fetch current price here
        new_holding = Holding(
            portfolio_id=watchlist_portfolio.id,
            symbol=symbol,
            quantity=1, # Default quantity
            average_cost=0,
            current_price=0
        )
        db.add(new_holding)
        db.commit()
        
        # Log activity
        log_user_activity(db, current_user.id, "add_watchlist", {"symbol": symbol})
        
        return {
            "success": True,
            "message": f"Added {symbol} to watchlist"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Remove stock from watchlist
@router.delete("/watchlist/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a stock from watchlist"""
    try:
        # Find watchlist portfolio
        watchlist_portfolio = db.query(Portfolio).filter(
            Portfolio.user_id == current_user.id,
            Portfolio.name == "Watchlist"
        ).first()
        
        if not watchlist_portfolio:
            return {
                "success": False,
                "message": "Watchlist not found"
            }
            
        # Find holding
        holding = db.query(Holding).filter(
            Holding.portfolio_id == watchlist_portfolio.id,
            Holding.symbol == symbol
        ).first()
        
        if holding:
            db.delete(holding)
            db.commit()
            
            # Log activity
            log_user_activity(db, current_user.id, "remove_watchlist", {"symbol": symbol})
            
            return {
                "success": True,
                "message": f"Removed {symbol} from watchlist"
            }
        else:
            return {
                "success": False,
                "message": "Stock not found in watchlist"
            }
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Get user activity/history
@router.get("/activity")
async def get_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get user's activity history including chats"""
    try:
        # Get system activities
        activities = db.query(UserActivity).filter(
            UserActivity.user_id == current_user.id
        ).order_by(
            desc(UserActivity.created_at)
        ).limit(limit).all()
        
        # Get recent conversations
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(
            desc(Conversation.created_at)
        ).limit(limit).all()
        
        activity_list = []
        
        # Add system activities
        for activity in activities:
            activity_list.append({
                "type": activity.activity_type,
                "data": activity.activity_data,
                "timestamp": activity.created_at.isoformat() if activity.created_at else None,
                "source": "system"
            })
            
        # Add conversations as activities
        for conv in conversations:
            activity_list.append({
                "type": "chat_session",
                "data": {"title": conv.title or "New Chat", "topic": conv.topic, "id": conv.id},
                "timestamp": conv.created_at.isoformat() if conv.created_at else None,
                "source": "chat"
            })
            
        # Sort combined list by timestamp desc
        activity_list.sort(key=lambda x: x["timestamp"] or "", reverse=True)
        
        return {
            "success": True,
            "data": activity_list[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Clear activity history
@router.delete("/activity")
async def clear_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear user's activity history"""
    try:
        # Delete all user activities
        db.query(UserActivity).filter(
            UserActivity.user_id == current_user.id
        ).delete()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Activity history cleared"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

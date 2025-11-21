from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any
from models.database import User, Portfolio, Holding, UserActivity
from services.database import get_db
from services.auth_service import AuthService

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
                "is_premium": current_user.is_premium,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None
            }
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
        # TODO: Implement actual watchlist addition to database
        return {
            "success": True,
            "message": f"Added {symbol} to watchlist"
        }
    except Exception as e:
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
        # TODO: Implement actual watchlist removal from database
        return {
            "success": True,
            "message": f"Removed {symbol} from watchlist"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get user activity/history
@router.get("/activity")
async def get_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get user's activity history"""
    try:
        activities = db.query(UserActivity).filter(
            UserActivity.user_id == current_user.id
        ).order_by(
            desc(UserActivity.created_at)
        ).limit(limit).all()
        
        activity_list = []
        for activity in activities:
            activity_list.append({
                "type": activity.activity_type,
                "data": activity.activity_data,
                "timestamp": activity.created_at.isoformat() if activity.created_at else None
            })
        
        return {
            "success": True,
            "data": activity_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

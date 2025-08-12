from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from models import User
from services.rate_limiter import RateLimiter
from config.database import get_db
from api.dependencies import get_current_user
import os

# Initialize rate limiter
rate_limiter = RateLimiter()

def rate_limit(
    max_requests: int = 100,
    window: int = 60,
    user: User = Depends(get_current_user),
    request: Request = None
):
    """
    Rate limiting dependency
    
    Args:
        max_requests: Maximum number of requests allowed in the window
        window: Time window in seconds
        user: Current user (from dependency)
        request: Current request (from dependency)
    """
    # Determine rate limit based on user role
    if hasattr(user, 'roles'):
        if 'admin' in user.roles:
            # Admins have higher limits or no limits
            return
        elif 'premium_user' in user.roles:
            # Premium users have higher limits
            max_requests = 100
        else:
            # Regular users
            max_requests = int(os.getenv("REGULAR_USER_RATE_LIMIT", 10))
    
    # Create rate limit key
    endpoint = request.url.path if request else "unknown"
    key = f"rate_limit:{user.id}:{endpoint}"
    
    # Check if request is allowed
    if not rate_limiter.is_allowed(key, max_requests, window):
        # Get rate limit headers
        headers = rate_limiter.get_rate_limit_headers(key, max_requests, window)
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers=headers
        )
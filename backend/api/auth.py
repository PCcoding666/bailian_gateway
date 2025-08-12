from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models import User
from services.auth_service import AuthService
from services.user_service import UserService
from config.database import get_db
from utils.jwt_utils import Token, verify_token

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    nickname: Optional[str] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class TokenRefresh(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    status: int
    created_at: str
    last_login_at: Optional[str] = None

class AuthResponse(BaseModel):
    code: int = 200
    message: str = "Success"
    data: Optional[dict] = None

# Router
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Security
security = HTTPBearer()

def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    token = credentials.credentials
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/register", response_model=AuthResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """User registration"""
    auth_service = AuthService(db)
    user = auth_service.register(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        nickname=user_data.nickname,
        phone=user_data.phone
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    return AuthResponse(
        code=200,
        message="Registration successful",
        data=user.to_dict()
    )

@router.post("/login", response_model=AuthResponse)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """User login"""
    auth_service = AuthService(db)
    tokens = auth_service.login(user_data.username, user_data.password)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    return AuthResponse(
        code=200,
        message="Login successful",
        data={
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_in": 3600,
            "user": auth_service.user_service.get_user_by_username(user_data.username).to_dict()
        }
    )

@router.post("/refresh", response_model=AuthResponse)
def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token"""
    auth_service = AuthService(db)
    tokens = auth_service.refresh_token(token_data.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return AuthResponse(
        code=200,
        message="Token refresh successful",
        data={
            "access_token": tokens.access_token,
            "expires_in": 3600
        }
    )

@router.get("/user", response_model=AuthResponse)
def get_current_user(current_user: User = Depends(get_current_user_from_token)):
    """Get current user information"""
    return AuthResponse(
        code=200,
        message="Retrieval successful",
        data=current_user.to_dict()
    )

@router.put("/user", response_model=AuthResponse)
def update_current_user(
    user_data: dict,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    user_service = UserService(db)
    user = user_service.update_user_profile(
        user_id=current_user.id,
        nickname=user_data.get("nickname"),
        phone=user_data.get("phone")
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user profile"
        )
    
    return AuthResponse(
        code=200,
        message="Update successful",
        data=user.to_dict()
    )
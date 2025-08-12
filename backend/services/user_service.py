from sqlalchemy.orm import Session
from models import User
from utils.jwt_utils import create_access_token, create_refresh_token, Token
from datetime import datetime
from typing import Optional
import re

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        # Check if username is email
        if "@" in username:
            user = self.get_user_by_email(username)
        else:
            user = self.get_user_by_username(username)
        
        if not user or not user.verify_password(password):
            return None
        return user

    def create_user(self, username: str, email: str, password: str, 
                   nickname: Optional[str] = None, phone: Optional[str] = None) -> Optional[User]:
        """Create a new user"""
        # Check if user already exists
        if self.get_user_by_username(username):
            return None
        
        if self.get_user_by_email(email):
            return None
        
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return None
        
        # Validate password strength (min 8 chars, at least one uppercase, one lowercase, one digit, one special char)
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
            return None
        
        # Create new user
        user = User(
            username=username,
            email=email,
            nickname=nickname,
            phone=phone
        )
        user.set_password(password)
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def update_user_last_login(self, user_id: int):
        """Update user's last login time"""
        user = self.get_user_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            self.db.commit()

    def generate_tokens(self, user: User) -> Token:
        """Generate access and refresh tokens for user"""
        # Create token data
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "roles": ["user"]  # Default role, can be extended
        }
        
        # Create tokens
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def update_user_profile(self, user_id: int, nickname: Optional[str] = None, 
                           phone: Optional[str] = None) -> Optional[User]:
        """Update user profile information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        if nickname is not None:
            user.nickname = nickname
        
        if phone is not None:
            user.phone = phone
            
        self.db.commit()
        self.db.refresh(user)
        
        return user
from sqlalchemy.orm import Session
from models import User
from services.user_service import UserService
from utils.jwt_utils import Token, verify_token
from typing import Optional

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def login(self, username: str, password: str) -> Optional[Token]:
        """Authenticate user and generate tokens"""
        user = self.user_service.authenticate_user(username, password)
        if not user:
            return None
        
        # Update last login time
        self.user_service.update_user_last_login(user.id)
        
        # Generate tokens
        tokens = self.user_service.generate_tokens(user)
        return tokens

    def register(self, username: str, email: str, password: str,
                nickname: Optional[str] = None, phone: Optional[str] = None) -> Optional[User]:
        """Register new user"""
        user = self.user_service.create_user(username, email, password, nickname, phone)
        return user

    def refresh_token(self, refresh_token: str) -> Optional[Token]:
        """Refresh access token using refresh token"""
        payload = verify_token(refresh_token)
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        username = payload.get("username")
        
        if not user_id or not username:
            return None
        
        # Create new access token
        token_data = {
            "user_id": user_id,
            "username": username,
            "roles": payload.get("roles", ["user"])
        }
        
        from utils.jwt_utils import create_access_token
        access_token = create_access_token(data=token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token"""
        payload = verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        return self.user_service.get_user_by_id(user_id)
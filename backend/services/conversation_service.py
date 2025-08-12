from sqlalchemy.orm import Session
from models import Conversation, Message
from typing import Optional, List

class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, user_id: int, model_name: str, title: Optional[str] = None) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            model_name=model_name,
            title=title or "New Conversation"
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation

    def get_conversation_by_id(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """Get conversation by ID for a specific user"""
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

    def get_user_conversations(self, user_id: int, skip: int = 0, limit: int = 10) -> List[Conversation]:
        """Get all conversations for a user"""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

    def update_conversation(self, conversation_id: int, user_id: int, title: str) -> Optional[Conversation]:
        """Update conversation title"""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None
        
        conversation.title = title
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete conversation"""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False
        
        self.db.delete(conversation)
        self.db.commit()
        return True